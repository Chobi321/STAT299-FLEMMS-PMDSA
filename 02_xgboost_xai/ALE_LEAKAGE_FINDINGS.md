# Model, Leakage Audit and XAI: Findings

Notebooks: `ALE_leakage_audit.ipynb` (audit, primary model, ALE, SHAP, H, 2D ALE) and `feature_count_sweep.ipynb` (feature count). Both re-run 2026-11-01 on the 75-variable model. The 45-feature results are archived in `archive_45feature/`.

Data: 468,643 individuals aged 10-64 with a valid target and weight, 163,655 households. Weighted illiteracy prevalence 29.2%. All averages use `RESP_RFACT_F2`. Effects are on the log-odds scale of predicted illiteracy.

## 1. Design and checks

1. **Household leakage.** The split is grouped by `HHID` (80/20, `random_state=42`): 374,921 train rows, 93,722 test rows, no household on both sides.
2. **Selection leakage.** Features are ranked on training rows only.
3. **Proxy features.** `READ_IND_F3` is excluded (below). `READ_IND_F2` and Form 2 derived columns were already excluded.

## 2. Proxy check

Weighted illiteracy rate by level of each reading indicator:

| Variable | Level | Share of rows | Illiteracy rate |
|---|---|---|---|
| `READ_IND_F2` | 1 | 97.5% | 27.9% |
| `READ_IND_F2` | 2 or 3 | 2.5% | 100% |
| `READ_IND_F3` | 1 | 96.1% | 27.9% |
| `READ_IND_F3` | 2 | 1.8% | 93.9% |
| `READ_IND_F3` | 3 | 0.5% | 87.0% |
| `READ_IND_F3` | missing | 1.5% | 38.9% |

`READ_IND_F3` was among the top three features in an unrestricted selection and works as a proxy for the outcome, so it is excluded. `RESULT_CODE_F2` and `RESP_AGREE_F2` are constant. The Form 3 questionnaire is not in the repo, so the exclusion rests on the empirical relation, not on skip logic.

## 3. Audit scenarios (45-feature models)

Held-out households, weighted.

| Scenario | Features | ROC-AUC | PR-AUC |
|---|---|---|---|
| S0 Phase 1B list (selected on all rows) | 43 | 0.7005 | 0.5155 |
| S1 selected on training rows only | 44 | 0.6996 | 0.5160 |
| S2 S1 without `READ_IND_F3` | 44 | 0.7010 | 0.5042 |
| S2b S2 plus `AGE` forced in | 45 | 0.7019 | 0.5051 |
| S3 S2 without `TVOC*` | 44 | 0.7004 | 0.5038 |

- Selecting on all rows and ignoring households did not inflate performance. AUC is about 0.70 throughout.
- Removing `READ_IND_F3` costs no ROC-AUC and 0.012 PR-AUC. Removing `TVOC*` costs almost nothing, so it stays in the model but is flagged.
- About 8 of 44 features rotate between selections, so the lower half of a 44-feature ranking is not stable.

## 4. Feature count and primary model

The 44 came from the PCA recipe, not a performance criterion, so `feature_count_sweep.ipynb` sweeps the number of original variables k. Method: 5-fold `GroupKFold` by household on training rows, selection redone inside each fold, `AGE` forced in, `READ_IND_F3` excluded, one-standard-error rule on weighted ROC-AUC.

| k (variables) | Dummies | CV ROC-AUC | CV PR-AUC | Mean pairwise Jaccard |
|---|---|---|---|---|
| 10 | 120 | 0.6887 | 0.492 | 0.858 |
| 25 | 294 | 0.6993 | 0.507 | 0.861 |
| 50 | 437 | 0.7044 | 0.513 | 0.803 |
| **75** | **565** | **0.7071** | **0.516** | **0.909** |
| 100 | 624 | 0.7088 | 0.518 | 0.868 |
| 148 (all) | 703 | 0.7097 | 0.519 | 1.000 |

- The curve flattens after about 50 variables. From 75 to all 148 variables adds 0.003 AUC.
- The strict one-SE rule picks k = 100 (test ROC-AUC 0.7114). **We use k = 75** (551 dummies after the final fit), the elbow with the most stable selection. This is a judgement call, not the rule's output, and should be stated as such.
- Primary model, test households: weighted ROC-AUC **0.711**, PR-AUC **0.516**, unweighted ROC-AUC 0.716. The 45-feature model scored 0.702 and 0.505. Recall and precision at 0.5 have not been recomputed for this model.
- Many slots go to multi-level variables (`WORK_TYPE_MAJOR` 44 dummies, `ATTEND_GRADE` 41). Report features at variable level (`sweep_selected_variables.csv`) and use dummies only in the ALE and SHAP tables.

## 5. ALE results

Primary model, test set. For a dummy, the effect is the log-odds change when it goes from 0 to 1, evaluated on rows where it equals 1. Shown are the 12 highest-gain dummies plus age.

| Feature | Meaning | Share of rows | Effect | Odds ratio |
|---|---|---|---|---|
| `TVOCTRAIN_5` | Not attending TechVoc training | 29.5% | -0.30 | 0.74 |
| `HGC_LEVEL_2` | Lower secondary completed | 37.9% | -0.35 | 0.70 |
| `HGC_LEVEL_6` | Bachelor level completed | 26.0% | -0.11 | 0.90 |
| `HGC_LEVEL_1` | Elementary completed | 22.4% | -0.09 | 0.91 |
| `DSKILL_INFO2_1` | Skill: information and data | 50.4% | -0.09 | 0.91 |
| `DSKILL_CONT3_1` | Skill: content creation | 21.4% | -0.09 | 0.91 |
| `DSKILL_PROB6_1` | Skill: problem solving | 41.8% | -0.08 | 0.92 |
| `NOWORK_REASON_1` | Not working, still studying | 16.0% | -0.08 | 0.92 |
| `TVOCGRAD_5` | Not a TechVoc graduate | 28.3% | -0.07 | 0.94 |
| `DSKILL_CONT1_1` | Skill: content creation | 26.0% | -0.06 | 0.94 |
| `INTERNET_1` | Used internet, past 3 months | 76.5% | -0.03 | 0.97 |
| `MM_WORK_1` | Never uses media for work or e-mail | 43.3% | +0.11 | 1.11 |

Age (log-odds, relative to the weighted mean): about -0.05 from ages 11 to 31, near -0.03 at 39, then rising to +0.02 at 42, +0.11 at 52, +0.15 at 56 and +0.20 at 60 to 64. Ages 10 to 11 move by 0.09 and should not be read as a trend.

- **The schooling effects shrank against the 45-feature run.** Elementary completion went from odds ratio 0.52 to 0.91 and lower secondary from 0.50 to 0.70. The likely cause is that schooling is now spread over 8 `HGC_LEVEL` dummies and the 41 `ATTEND_GRADE` dummies, so a single dummy carries less. This is not verified. Quote the grouped SHAP for the size of the schooling effect and do not reuse the old "halves the odds" statement.
- Digital-skill items each lower the odds by about 6 to 9%. They are correlated, so report them as a block.
- The age curve is low through the 30s and climbs after 40, as in the raw U-shape, with no rise at 10 to 14 once schooling is controlled.
- Stability: two random halves of the test households differ by at most 0.004 (`HGC_LEVEL_2`).

## 6. SHAP (audited model)

TreeSHAP from XGBoost `pred_contribs` and `pred_interactions`, log-odds scale, weighted. Importance uses the full test set. Interactions use 1,000 rows scored in chunks of 100.

| Group | Columns | Mean \|SHAP\| |
|---|---|---|
| `HGC_LEVEL` (schooling completed) | 8 | 0.224 |
| `DSKILL` block (10 items) | 20 | 0.174 |
| `TVOCTRAIN` | 5 | 0.132 |
| `SEX` | 1 | 0.091 |
| `MM_WORK` | 5 | 0.071 |
| `HH_WASHING` | 1 | 0.067 |
| `AGE` | 1 | 0.064 |
| `HH_PC` | 1 | 0.055 |
| `INTERNET` | 2 | 0.043 |

- Schooling leads, the digital block is second. The digital-skill dominance in the old `xgboost_shap_ale_impact.csv` was a pre-audit artifact.
- Gain and SHAP disagree. `AGE` is 238th by gain and 7th by SHAP, `SEX_2` is 23rd by gain and 3rd by SHAP. Rank drivers by SHAP or ALE, not gain.
- Per-dummy SHAP direction can differ from ALE for multi-level variables (SHAP marks `HGC_LEVEL_1` as "Increases Risk", ALE gives 0.91), because SHAP compares with the average person and ALE with the omitted level. Report grouped SHAP for magnitude and ALE for direction.

## 7. Friedman's H and 2D ALE

H² on 3,000 test rows for 8 candidate pairs. A pair is supported if every cell of its joint 2D grid holds at least 0.1% of weighted rows. Unsupported pairs describe extrapolation and are not reported as interactions.

| Pair | H² | Min cell share | Supported |
|---|---|---|---|
| `HGC_LEVEL_1` x `INTERNET_1` | 0.054 | 10.1% | Yes |
| `HGC_LEVEL_1` x `TVOCTRAIN_5` | 0.050 | 0 | No |
| `HGC_LEVEL_2` x `TVOCTRAIN_5` | 0.042 | 0 | No |
| `AGE` x `HGC_LEVEL_1` | 0.029 | 0.4% | Yes |
| `DSKILL_PROB6_1` x `TVOCTRAIN_5` | 0.015 | 10.5% | Yes |
| `DSKILL_CONT1_1` x `TVOCTRAIN_5` | 0.014 | 12.8% | Yes |
| `AGE` x `ATTEND_SCHOOL_1` | 0.002 | 0 | No |
| `DSKILL_INFO2_1` x `INTERNET_1` | 0.001 | 0 | No |

- Supported interactions are small (H² at most 0.054). The model is close to additive in its main drivers. Digital skill and internet use do not interact, which supports adding them in the simulation.
- 2D ALE heatmaps are drawn for the three supported pairs with the largest H² (`HGC_LEVEL_1` x `INTERNET_1`, `AGE` x `HGC_LEVEL_1`, `DSKILL_PROB6_1` x `TVOCTRAIN_5`). Values are in `ale_2d_values.csv` and the figure in `ale_figures/ale_2d_top_pairs.png`. **The heatmaps have not been interpreted yet.**
- `TVOCTRAIN_5` = 1 never co-occurs with `HGC_LEVEL_1` = 1 or `HGC_LEVEL_2` = 1, so the "No" answer is recorded only for people with schooling beyond lower secondary. `TVOCTRAIN_5` then partly acts as an education indicator, which fits its top gain rank and modest ALE effect. This is indirect evidence on the unverified Form 3 skip logic.

## 8. Limits

1. **Superseded outputs.** `xgboost_basic_importance.csv`, `xgboost_shap_ale_impact.csv` and `xgboost_shap_interactions.csv` predate the audit. Quote the `*_audited.csv` files.
2. **Reference levels.** Dummy effects are versus the omitted level.
3. **Correlated features.** ALE cannot separate highly correlated variables. Report digital skills as a group.
4. **Binary effects are local** to rows where the dummy is 1.
5. **Calibration.** Raw predictions are shifted by `scale_pos_weight`. The prior-corrected model is calibrated (see `04_spatial_lisa_simulation/LISA_FINDINGS.md`).
6. **Rare categories.** Effects for categories under 1% of rows are unreliable.
7. **Not done.** Hyperparameter tuning (300 trees, depth 6, learning rate 0.05 throughout).
8. **Label mismatch.** `leakage_audit_scenarios.csv` marks both S2 and S4 as "(primary)". S4 is the primary model.
9. **`sweep_with_LNO/`** holds an earlier sweep (k* = 125). Its purpose is undocumented. Delete or label it before archiving.

## 9. Files

| File | Content |
|---|---|
| `ALE_leakage_audit.ipynb` | Audit, primary model, ALE, SHAP, H, 2D ALE |
| `feature_count_sweep.ipynb` | Cross-validated feature-count sweep |
| `leakage_audit_scenarios.csv`, `primary_model_metrics.csv` | Scenario and primary-model metrics |
| `selected_features_train_only.csv` | The 551 dummies of the primary model, with their `Variable` |
| `sweep_cv_summary.csv`, `sweep_cv_results.csv`, `sweep_stability_by_k.csv`, `sweep_final_metrics.csv` | Sweep results |
| `sweep_selected_variables.csv`, `sweep_selected_dummies.csv`, `sweep_top75_dummies.csv` | Ranking at k* and the top 75 |
| `ale_values.csv`, `ale_effect_summary.csv`, `ale_stability_halves.csv` | ALE curves, effect sizes, half-sample check |
| `shap_importance_audited.csv`, `shap_grouped_importance_audited.csv`, `shap_interactions_audited.csv` | SHAP |
| `friedman_h_pairs.csv`, `ale_2d_support.csv`, `ale_2d_values.csv` | H², joint support, 2D ALE |
| `ale_figures/` | ALE, 2D ALE and sweep curve figures |
| `archive_45feature/` | Previous 45-feature outputs |
