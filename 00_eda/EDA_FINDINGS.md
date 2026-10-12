# EDA Findings: FLEMMS 2024 (`EDA_FLEMMS.ipynb`)

Run date: 2026-10-12. Notebook executed end to end against the local `data/` directory (no cell errors). Figures were regenerated in `eda_figures/` and `eda_province_rates.csv` was rewritten. All rates are survey-weighted with `RESP_RFACT_F2` unless labelled unweighted. Target `y` = 1 if functionally illiterate (`FLITERATE == 2`).

## 1. Data audit

| Item | Value |
|---|---|
| MEMBER rows (all ages) | 650,424 |
| Merged frame, ages 10-64 | 496,770 rows x 196 columns (0.78 GB) |
| Duplicate (HHID, LNO) keys | 0 |
| Households | 166,090 |
| Rows with Form 2 record (valid `FLITERATE`) | 94.3% |
| Rows with Form 3 record (`INTERNET`) | 94.4% |
| Rows with `RESP_RFACT_F2` | 100.0% |
| Dictionary entries parsed | 3,766 |

- Constant columns (no information): `READING59`, `WRITING59`, `COMPUTE59`, `LLEVEL59`, `PATHWAY_OTHERS`.
- 18 columns have more than 50 unique values and are dropped from PCA (for example `PRV`, `HHID`, `AGE`, `ETHNICITY`, `HGC_GRADE`, `TVOCCOURSE`, the PSU and weight columns).
- Rows without a Form 2 record (28,127) are older than analysis rows (mean age 36.3 vs 32.8) and slightly less female (45.6% vs 49.3%). They cannot enter weighted rates or the model, so the analysis universe is 468,643 rows. This is a small selection difference worth stating in the limitations.

## 2. Missingness

Column missingness distribution: 80 columns at 0%, 17 at 0-5%, 38 at 5-25%, 22 at 25-50%, 15 at 50-75%, 19 at 75-99%, 6 at 100%. Most missingness is structural skip logic (NaN means "not applicable"), which supports the constant `Not_Applicable` imputation used in the pipeline.

## 3. Target and weights

| Quantity | Value |
|---|---|
| Raw `FLITERATE` counts | 1 (literate): 325,368; 2 (illiterate): 143,275; missing: 28,127 |
| Illiteracy prevalence, unweighted | 30.6% |
| Illiteracy prevalence, weighted | 29.2% |
| Population represented (sum of weights) | 85,001,944 |
| Weight CV | 0.97 |
| Kish effective sample size | 242,573 of 468,643 |
| Design effect from weights | about 1.93 |

The weights lower the headline rate by 1.4 points and roughly halve the effective sample size. Any reported uncertainty that ignores the design effect will be too narrow.

## 4. Univariate profile

Cardinality of columns: 91 with at most 2 levels, 44 with 3-5, 21 with 6-10, 18 with 11-50, 18 with more than 50.

## 5. Bivariate: age

| Age band | n | Unweighted | Weighted | Population share |
|---|---|---|---|---|
| 10-14 | 65,259 | 37.5% | 36.2% | 12.8% |
| 15-19 | 60,544 | 24.3% | 23.4% | 12.1% |
| 20-24 | 50,450 | 21.7% | 21.7% | 11.6% |
| 25-34 | 87,396 | 25.7% | 25.4% | 22.1% |
| 35-44 | 80,195 | 29.7% | 28.5% | 17.4% |
| 45-54 | 69,120 | 34.8% | 33.2% | 13.7% |
| 55-64 | 55,679 | 41.0% | 39.8% | 10.2% |

The age profile is U-shaped: highest at 10-14 and at 55-64, lowest at 20-24. The 10-14 rate partly reflects children who have not yet completed the schooling that confers functional literacy, so age band should be read together with schooling and attendance. The two-way age by schooling and age by internet views are in `06_two_way_age.png`.

## 6. Association ranking (Cramer's V against the target)

Top predictors, weighted V (unweighted in brackets):

| Rank | Feature | V weighted | V unweighted |
|---|---|---|---|
| 1 | `HGC_LEVEL` (highest grade completed) | 0.272 | 0.292 |
| 2 | `DSKILL_CONT3` | 0.206 | 0.221 |
| 3 | `DSKILL_CONT1` | 0.206 | 0.223 |
| 4 | `DSKILL_PROB6` | 0.206 | 0.223 |
| 5 | `DSKILL_INFO2` | 0.205 | 0.220 |
| 18 | `MM_WORK` (mass media for work or e-mail) | 0.192 | 0.209 |
| 21 | `SHS` | 0.187 | 0.195 |
| 23 | `TVOCGRAD` | 0.186 | 0.195 |
| 27 | `MM_SOCMED` | 0.184 | 0.205 |
| 29 | `INTERNET` | 0.179 | 0.197 |

- Educational attainment is the single strongest univariate signal, followed by a large block of near-identical digital-skill items (V of about 0.18 to 0.21).
- Weighted V is consistently 0.01 to 0.02 below unweighted V, so the weighting does not change the ranking, only the magnitude.
- `WORK_TYPE_MAJOR` (45 levels) sits at V = 0.177, so its place in the ranking is partly a cardinality effect.
- Digital-skill items are near-duplicates of each other, which motivates the redundancy check in the next section and the PCA below. These items are also asked only of internet users, so part of their association with the target is a skip-logic artifact (non-users coded `Not_Applicable`).

## 7. Geography

- 118 provinces and HUCs; none has fewer than 200 analysis rows (minimum n = 589), so none was dropped.
- Unweighted mean of provincial weighted rates: 29.5%; median 28.3%.
- Lowest weighted rates: code 814 (5.5%, n = 1,180), 303 (10.2%), 812 (10.9%), 817 (11.9%), 11 (12.1%).
- Highest weighted rates: code 70 (66.4%, n = 4,693), 86 (53.4%), 999 (51.3%, n = 589), 73 (48.9%), 48 (48.2%).
- The spread from about 5% to 66% is large, which supports a spatial (LISA, GWR) layer. Province labels are PSA numeric codes; name mapping is `[DATA MISSING]` in the dictionary files used. Code 999 is the smallest cell and may be a residual or unspecified category, to be confirmed against the PSA codebook before it enters any spatial weights matrix.

## 8. PCA diagnostics

| Item | Value |
|---|---|
| Encoded and scaled matrix | 496,770 x 750 |
| Components for 95% variance | 504 (full-data fit) |
| PC1 variance | 5.8% |
| Top 10 components, cumulative | 19.1% |
| Top components by AUC against `y` | PC2 0.614, PC5 0.605, PC1 0.601, PC4 0.600, PC3 0.579 |
| Rank correlation, variance order vs target relevance | 0.653 |
| Overlap, PCA list vs supervised (gain) list | 8 features, 18% of the supervised list (PCA list 43, supervised list 44) |

Interpretation:

- Variance is spread thinly: it takes 504 components to reach 95%, and the first ten carry under a fifth of the variance. PCA offers little compression here, which is consistent with the one-hot encoding of many categorical columns.
- The most target-relevant components are PC1 to PC5, and the best single-component AUC is only 0.614. No individual component separates the classes well on its own.
- Variance order and target relevance are moderately aligned (rank correlation 0.653), so PCA is not useless as a ranking, but it is far from a reliable selector. Together with the 18% overlap between PCA-chosen and supervised-chosen features, this supports the Option C framing that PCA is a diagnostic and not the feature selector.
- Overlapping features include `DSKILL_INFO1_1`, `DSKILL_INFO2_1`, `INTERNET_1`, `MM_PNPAPER_2`, `NOWORK_REASON_ 1`, `PATHWAY_COLLEGE_2`, `PATHWAY_OTHERS_2`, `PATHWAY_STUDYABROAD_2`.

## 9. Discrepancies to resolve

1. **Component count.** This run gives 504 components at 95% variance on 750 encoded columns. `CLAUDE.md` and the main notebook report 539 components on 752 columns. Two columns fewer entered the encoding here, which is likely a difference in the dropped-column list or the constant columns. The notebook's own docstring expects the two to match, so this should be reconciled before the manuscript quotes either number.
2. **`PATHWAY_OTHERS` is constant** yet appears in the PCA-selected overlap list as `PATHWAY_OTHERS_2`. A constant column carries no information, so its presence in a selected list needs checking.
3. **Leakage check.** `HGC_LEVEL` and the school-attendance variables are strong predictors but are legitimately upstream of literacy. `BASIC_NUM` and other Form 2 derived columns must stay excluded, as in the main pipeline.

## 10. Outputs

- Figures: `eda_figures/` (18 PNG files, sections 2 to 10). All were regenerated by this run, so git shows them as modified.
- Table: `eda_province_rates.csv` (weighted and unweighted rate and n per `PRV`), input for the LISA step.
- The executed notebook copy was not saved into the repo; `EDA_FLEMMS.ipynb` is unchanged (it still has no stored outputs).
