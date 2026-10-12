# ALE and Leakage Audit: Findings

Notebook: `ALE_leakage_audit.ipynb` (run 2026-10-12, executed in place, no errors).
Data: 468,643 individuals aged 10-64 with a valid target and weight, 163,655 households. Weighted illiteracy prevalence 29.2%.
All averages use `RESP_RFACT_F2`. Effects are on the log-odds scale of predicted illiteracy.

## 1. What was checked

1. **Household leakage.** Members of the same household share many features. The train/test split is now grouped by `HHID` (80/20, `random_state=42`), so no household appears on both sides. Train has 374,921 rows and test has 93,722.
2. **Selection leakage.** Phase 1B ranked features by gain on all rows before splitting. Here the split comes first and the top 44 features are chosen from training rows only.
3. **Proxy features.** Variables that restate the literacy outcome were checked against the target and removed where they did.

## 2. Proxy check

Weighted illiteracy rate by level of each reading indicator:

| Variable | Level | Share of rows | Illiteracy rate |
|---|---|---|---|
| `READ_IND_F2` | 1 | 97.5% | 27.9% |
| `READ_IND_F2` | 2 | 2.0% | 100% |
| `READ_IND_F2` | 3 | 0.5% | 100% |
| `READ_IND_F3` | 1 | 96.1% | 27.9% |
| `READ_IND_F3` | 2 | 1.8% | 93.9% |
| `READ_IND_F3` | 3 | 0.5% | 87.0% |
| `READ_IND_F3` | 9 | under 0.1% | 80.3% |
| `READ_IND_F3` | missing | 1.5% | 38.9% |

- `READ_IND_F2` fully determines the target for levels 2 and 3. It was already excluded from every model.
- `READ_IND_F3` behaves almost the same way. Anyone flagged 2 or 3 is very likely illiterate. In the unrestricted training-only selection it was among the top three features. It is treated as a proxy for the outcome and excluded from the primary model.
- `RESULT_CODE_F2` and `RESP_AGREE_F2` are constant (all 1) in the analysis rows, so they carry no information.
- Form 3 skip logic remains unverified because the Form 3 questionnaire is not in the repo. The exclusion rests on the empirical relation above, not on the questionnaire.

## 3. Scenario comparison

Held-out households, weighted metrics.

| Scenario | Features | ROC-AUC | PR-AUC |
|---|---|---|---|
| S0: original Phase 1B list (selected on all rows) | 43 | 0.7005 | 0.5155 |
| S1: selected on training rows only | 44 | 0.6996 | 0.5160 |
| S2: S1 without `READ_IND_F3` | 44 | 0.7010 | 0.5042 |
| S2b: S2 plus `AGE` forced in (model used for ALE) | 45 | 0.7019 | 0.5051 |
| S3: S2 without the `TVOC*` family | 44 | 0.7004 | 0.5038 |

(S0 has 43 features because one Phase 1B feature does not exist in the new encoding.)

Reading the table:

- Selecting on all rows did not inflate performance. S0 and S1 differ by 0.001 AUC.
- Grouping by household did not reduce performance either. AUC is about 0.70 throughout.
- Removing `READ_IND_F3` costs nothing in ROC-AUC and about 0.012 in PR-AUC (0.516 to 0.504). The proxy was easy for the model to use but not needed.
- Removing the `TVOC*` family also costs almost nothing, so those variables stay in the model but remain flagged.
- Feature overlap: S1 shares 36 of 44 features with the original Phase 1B list, S2 shares 32 of 44 with S1, and S3 shares 33 of 44 with S2. About 8 features rotate between runs, which means the lower half of the ranking is not stable.
- `AGE` was not chosen by gain once schooling and the other predictors were present. It was added deliberately as a demographic control so that a continuous age curve could be drawn. It is not a leakage risk.

Primary model (S2b) on the test set: weighted ROC-AUC 0.702, weighted PR-AUC 0.505, unweighted ROC-AUC 0.708. At a 0.5 threshold, weighted recall for the illiterate class is 0.59 and precision 0.44 (accuracy 0.67).

## 4. ALE results

Primary model, test set, 20 quantile bins for age. For dummy features the effect is the change in log-odds when the dummy goes from 0 to 1, evaluated on rows where it equals 1.

| Feature | Meaning | Share of rows | Effect (log-odds) | Odds ratio |
|---|---|---|---|---|
| `HGC_LEVEL_2` | Lower secondary completed | 37.8% | -0.69 | 0.50 |
| `HGC_LEVEL_1` | Elementary completed | 22.4% | -0.65 | 0.52 |
| `HGC_LEVEL_3` | Next level up (label missing in the dictionary) | 8.7% | -0.53 | 0.59 |
| `HGC_LEVEL_6` | Bachelor level completed | 25.9% | -0.10 | 0.91 |
| `TVOCGRAD_5` | Not a TechVoc graduate | 28.2% | -0.14 | 0.87 |
| `TVOCTRAIN_5` | Not attending TechVoc training | 29.4% | -0.13 | 0.88 |
| `INTERNET_1` | Used the internet in the past 3 months | 76.5% | -0.11 | 0.90 |
| `DSKILL_INFO2_1` | Digital skill: information and data literacy | 50.4% | -0.09 | 0.91 |
| `DSKILL_PROB6_1` | Digital skill: problem solving | 41.8% | -0.09 | 0.92 |
| `DSKILL_CONT1_1` | Digital skill: content creation | 26.0% | -0.07 | 0.94 |
| `NOWORK_REASON_1` | Not working because still studying | 16.0% | -0.05 | 0.95 |
| `MM_WORK_1` | Never uses media for work or e-mail | 43.3% | +0.16 | 1.17 |

Age (log-odds relative to the weighted mean): roughly -0.05 to -0.10 between ages 20 and 40, then rising to about +0.12 at 56 and +0.22 at 60, and +0.15 at 64. Values below age 18 move between -0.03 and +0.10 and should not be read as a trend.

What this says:

- Schooling carries the largest effects. Having completed elementary or lower secondary roughly halves the odds of functional illiteracy relative to the omitted reference level.
- Digital skill and internet use matter but are small individually, about 8 to 10% lower odds each. They are correlated with each other, so single-item effects understate the combined effect of the digital block.
- The age effect is low in the 20s and 30s and climbs after 40, consistent with the U-shape in the raw EDA rates. The ALE age curve shows no strong rise at 10-14 once schooling is controlled for, which suggests the high raw rate in that group is mostly explained by incomplete schooling.
- Effects for the high-gain `TVOC*` features are small in log-odds even though gain is high (`TVOCTRAIN_5` has the second-highest gain). Gain ranks how often a variable is used to split, not how large its effect is.

## 5. Stability

ALE effects recomputed on two random halves of the test households. The largest absolute difference is 0.011 (`HGC_LEVEL_2`), and most are below 0.005. The curves are stable for the features listed.

## 6. Limits and open points

1. **Superseded outputs.** `xgboost_basic_importance.csv`, `xgboost_shap_ale_impact.csv` and `xgboost_shap_interactions.csv` come from the older pipeline (selection on all rows, `READ_IND_F3` allowed, no household grouping). They still show digital skill as dominant. Under the audited model, schooling dominates. Do not quote the old SHAP rankings without re-running them on the audited model.
2. **Reference levels.** Dummies are compared to the dropped reference level. For `HGC_LEVEL`, the all-zero state is the omitted level, so the effects read as "versus the reference level", not versus each other.
3. **Correlated features.** ALE avoids unrealistic combinations but cannot separate effects of highly correlated variables. Digital skill items should be reported as a group.
4. **Binary effects are local.** The 0-to-1 effect is evaluated on rows where the dummy is 1. It is not the effect of changing the dummy for everyone.
5. **Calibration.** `scale_pos_weight` shifts predicted probabilities upward. Log-odds effects keep their shape, but predicted probabilities should not be read as calibrated risks.
6. **Rare categories.** `NOWORK_REASON_6` showed a large effect (+0.95) in the first run, but it covers 0.5% of rows and is not in the final model. Effects for categories under 1% of rows are not reliable.
7. **Not yet done.** Friedman's H and two-dimensional ALE for the top interacting pairs, grouped SHAP on the audited model, and hyperparameter tuning with grouped cross-validation.
8. **Label mismatch.** One scenario label in `leakage_audit_scenarios.csv` still reads "(primary)" for S2. The primary model is S2b.

## 7. Files

| File | Content |
|---|---|
| `ALE_leakage_audit.ipynb` | Full run with outputs |
| `leakage_audit_scenarios.csv` | Scenario metrics |
| `primary_model_metrics.csv` | Metrics for S2b |
| `selected_features_train_only.csv` | Features chosen on training rows (S2), with `AGE` marked as forced in |
| `ale_values.csv` | ALE curve points |
| `ale_effect_summary.csv` | Effect size, odds ratio, share of rows per feature |
| `ale_stability_halves.csv` | Half-sample check |
| `ale_figures/ale_primary_model.png` | ALE chart |
