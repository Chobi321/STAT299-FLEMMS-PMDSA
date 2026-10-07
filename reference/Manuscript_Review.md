# Manuscript Review: `proposal-manuscript/proposal-manuscript-full.md`

Review of the full proposal manuscript against `Comments_Proposal_Defense.md`, `Action_Plan_Proposal_Edits.md`, and the current notebook. Edits already applied to the manuscript are listed first. Items marked OPEN need a decision or a source from the authors.

## 1. Edits applied

| Section | Change | Defense comment |
|---|---|---|
| 1 Intro | Fixed unbalanced quote and missing space after "(PSA, 2024)"; fixed "shifts. Linguistic diversity, or" run-on; removed "auxiliary socio-economic indicators" (contradicts 1.3, FLEMMS only) | n/a |
| 1.1 Objectives | Objective 1 recast as LISA descriptive precursor; Objective 2 "drive" changed to "are associated with"; Objective 3 leads with predictive EWS and policy simulation | 1 |
| 1.3 Limitations | Added cross-sectional and non-causal caveat | n/a |
| 2.4 | Removed claim that LISA shows how determinants vary by location (a GWR claim); non-stationarity noted as a limitation | 1 |
| 2.5 | SHAP cost sentence corrected (exponential for exact Shapley, TreeSHAP for trees); "inflation" replaced by "internet access"; added ALE vs marginal effects paragraph; added H-statistic "what if H approaches 1" paragraph | 2, 4 |
| 2.6 | PCA recast as unsupervised diagnostic; supervised selection named; text matches the Compressed manuscript | 3, 5ii |
| 3 intro, 3.3 | Phase 1 retitled "Diagnostic PCA and Supervised Feature Selection"; loadings list marked diagnostic only; gain-based selection of 44 features added (8 of 44 overlap with the PCA list) | 3, 5ii |
| 3.2 | Imputation split into a categorical rule and a numeric rule; stray "Alternatively" removed; high-cardinality and leakage drops stated | 5i |
| 3.4, 3.4.1 | Input set now the gain-selected 44; "attrition" corrected; "Randomized Grid Search" corrected; software line flagged | n/a |
| 3.5 | ALE and H bullets expanded and cross-referenced to 2.5 | 2, 4 |
| 3.6 | GWR paragraph and formulas removed; heading renamed; LISA clusters now defined on predicted risk (was literacy); simulation reworded to re-score the XGBoost model | 1 |

## 2. OPEN items for the authors

**Citations (no source invented; `[CITATION NEEDED]` markers added in text)**
- 1 Intro: source or derivation of "19 million" and of San Juan City 94.5%.
- 2.3: DICT 2024-2025 reports, "recent longitudinal studies", World Bank 2025 updates. None are in the reference list.
- Cited but absent from References: Lundberg 2018, Owada et al. 2019.
- Check reference details against the papers: Anselin (1995) is listed as Geographical Analysis 7(2) and appears to be 27(2); Brunsdon et al. (1996) and Filmer and Pritchett (2001) have no journal named.
- The action plan said to drop the Brunsdon citation with GWR. It is kept because 2.4 still uses it to define spatial non-stationarity. Remove it only if that sentence is also cut.

**Not implemented in the notebook yet**
- Friedman's H-statistic, ALE curves, hyperparameter search, early stopping. The manuscript states these as planned ("will"). The notebook computes SHAP importance and SHAP interactions only.
- `iml` is an R package, but the stack is Python. The software line is marked `[TO BE CONFIRMED]`.
- The H-statistic paragraph in 2.5 carries `[DATA MISSING]` for the empirical values.

**Design decisions to raise with the adviser**
- Calibration: `scale_pos_weight` combined with survey weights distorts predicted probabilities. 3.4.1 says risk scores "reflect the actual scale of the Philippine population". Decide whether scores are used only for ranking, and say so.
- "Early warning": a single cross-section predicts current status, not future emergence. The intro still says hotspots are identified "before they manifest". Consider softening.
- Validation: random 80/20 splits can leak across provinces. Add a province-held-out check or list it as a limitation.
- LISA on model predictions vs observed weighted provincial rates: one sentence of justification is needed, and provincial sample sizes should be reported.
- Tense alternates between "was" and "will be" across 3.4 and 3.4.1. Choose one once the analysis is final.
- Objective 2 and 1.2 still say "income dynamics", while 1.3 says FLEMMS has no income measure. Left unchanged per the action plan (Decision Point 2).

## 3. Repo hygiene
- `proposal-manuscript-full.md` was untracked and is now added as the working full manuscript.
- `STAT 299_ PROPOSAL_Compressed.md` still contains GWR in 3.6 and the unrebalanced objectives. It needs the same edits, or should be retired.
- `01_` to `04_` chapter files and the `_revised` files overlap. `04_methodology_model.md` still describes GWR.
- `CHANGELOG_POST_DEFENSE_REVISIONS.md` is empty.
- Equations in the full manuscript are blank in this Markdown export (images dropped). Check the source document before submission.
