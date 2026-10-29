# Project Plan and Status

Plan for working through the analysis phases in the post-defense proposal (`reference/proposal-manuscript/04_methodology_model_revised.md`, `01_introduction_revised.md`). Status as of 2026-10-29.

Status key: DONE, PARTIAL (runs, but a proposal commitment is missing), TODO, BLOCKED.

Detailed findings live next to the work:

- `00_eda/EDA_FINDINGS.md` for the EDA and PCA diagnostics.
- `02_xgboost_xai/ALE_LEAKAGE_FINDINGS.md` for the leakage audit and ALE.
- `04_spatial_lisa_simulation/LISA_FINDINGS.md` for the out-of-fold model, province aggregation and scenario simulation.

## 1. Objectives and where they are served

| Proposal objective | Served by | Status |
|---|---|---|
| 1. Descriptive spatial precursor (LISA on provinces and HUCs) | Phase 4 | DONE (LISA ran 2026-10-28; High-High clusters do not survive BH-FDR) |
| 2. Predictive early warning system (weighted XGBoost) | Phases 1B and 2 | PARTIAL (grouped CV and calibration done; tuning not) |
| 3. Driver quantification and scenario simulation | Phases 3 and 4 | PARTIAL (ALE and simulation done; H-statistic, 2D ALE and audited SHAP not) |

## 2. Phase map

| Proposal phase | Folder | Notebook | Status |
|---|---|---|---|
| EDA (supports Chapter 3) | `00_eda/` | `EDA_FLEMMS.ipynb`, `data_exploration.ipynb` | DONE |
| Phase 1: diagnostic PCA | `01_pca_diagnostic/` | `notebooks/PCA_FLEMMS_streamlined.ipynb`, `PCA_component_XGBoost_comparison.ipynb` | DONE |
| Phase 1B: supervised selection | `01b_supervised_selection/` | `notebooks/PCA_FLEMMS_streamlined.ipynb`, `02_xgboost_xai/ALE_leakage_audit.ipynb` | PARTIAL |
| Phase 2: predictive model | `02_xgboost_xai/` | `ALE_leakage_audit.ipynb` | PARTIAL |
| Phase 3: XAI stack | `02_xgboost_xai/` | `ALE_leakage_audit.ipynb` | PARTIAL |
| Phase 4: LISA and simulation | `04_spatial_lisa_simulation/` | `LISA_scenario_simulation.ipynb` | DONE |

The spatial folder was renamed from `03_spatial_lisa_gwr/` to `04_spatial_lisa_simulation/` on 2026-10-25, since GWR is out.

## 3. Phase by phase

### EDA (DONE)

Full results: `00_eda/EDA_FINDINGS.md`.

- Analysis universe is 468,643 of 496,770 rows. The 28,127 dropped rows (no Form 2 record) are older, mean age 36.3 against 32.8.
- Illiteracy is 29.2% weighted and 30.6% unweighted. The weights represent 85.0M people. Effective sample size is 242,573 (design effect about 1.93).
- The age profile is U-shaped: 36.2% at ages 10-14, 21.7% at 20-24, 39.8% at 55-64.
- The strongest raw association is highest grade completed (Cramer's V 0.27), then the digital-skill items (about 0.20).
- Provincial weighted rates run from 5.5% to 66.4% across 118 areas, smallest sample 589.

### Phase 1: diagnostic PCA (DONE)

- PC1 explains 5.8% of variance and the first 10 components 19.1%. The best single component reaches AUC 0.614.
- Variance order and target relevance have a rank correlation of 0.65, so PCA ranking is a weak selector.
- PCA needs 504 components for 95% of variance on 750 encoded columns, so it compresses little here. This EDA count is the one the manuscript quotes (decided 2026-10-25).

Open:
1. **Component count: resolved.** The manuscript quotes the EDA run (504 components, 750 columns). The main notebook's older run (539, 752) and the comparison notebook's training-split figure (533) are not quoted.
2. `PATHWAY_OTHERS` is constant but appears in the PCA list as `PATHWAY_OTHERS_2`. The ALE notebook drops constants before encoding. Port that rule to the main notebook.
3. Run the data-quality checks in `reference/Notebook_Verification_TODO.md`. The ALE notebook now asserts merge-key uniqueness and no row fan-out (item 1 passes). Items 2 to 5 (blank vs NaN, native N/A codes, the 6,669 subgroup, skip-logic cross-tabs) are still not run.

### Phase 1B: supervised feature selection (PARTIAL)

Done, with the audit in `02_xgboost_xai/ALE_LEAKAGE_FINDINGS.md`:

- Selection on all rows did not inflate results. Selecting on training rows only changes weighted ROC-AUC from 0.7005 to 0.6996. Eight of the 44 features change, so the lower half of the ranking is not stable.
- The original overlap figure (8 of 44, 18% against the PCA list) comes from the all-rows selection. It should be recomputed against the training-only list before it goes in the manuscript.
- The PCA-component benchmark gap (-0.011 AUC) was measured on the older split. It is consistent with the grouped-split result (about 0.70 for 44 features).

Open:
1. PCA overlap recomputed against `02_xgboost_xai/selected_features_train_only.csv` (2026-10-25): 9 of the 44 training-only features (20%) are in the 43-feature PCA list. The manuscript quotes this figure, not the older 8 of 44.
2. Decide whether the manuscript reports the 44 features by gain (dummy level) or by original variable. Several dummies of the same variable occupy slots (`HGC_LEVEL_1`, `_2`, `_3`, `_6`).
3. Write the training-only selection back into `01b_supervised_selection/` so Phase 1B has one source of truth. Today `phase1b_selected_features.csv` still holds the all-rows list.

### Leakage audit (DONE, new)

- `READ_IND_F3` is a proxy for the outcome. Respondents coded 2 are 93.9% illiterate and coded 3 are 87.0%, against 27.9% for code 1. It was in the top three features before exclusion. Removing it cost 0 ROC-AUC and 0.012 PR-AUC.
- `READ_IND_F2` was already excluded. Codes 2 and 3 are 100% illiterate.
- Splitting by household did not change performance. AUC stays near 0.70.
- `TVOC*` variables stay in the model. Removing them costs no AUC, but their skip logic is unverified.
- Form 3 skip logic cannot be checked because the Form 3 questionnaire is not in the repo.

### Phase 2: predictive model (PARTIAL)

Primary model (45 features: 44 by training gain without `READ_IND_F3`, plus `AGE`), household-grouped test set, weighted:

| Metric | Value |
|---|---|
| ROC-AUC | 0.702 |
| PR-AUC | 0.505 |
| Recall, illiterate class (threshold 0.5) | 0.59 |
| Precision, illiterate class | 0.44 |

Discrimination is moderate. A model that gets 0.70 AUC on this feature set will rank people only somewhat better than chance, which matters for how the manuscript words "early warning".

Open:
1. Add hyperparameter tuning. The 300-tree, depth-6 settings have not been tuned. Grouped 5-fold cross-validation of the untuned model is done in the Phase 4 notebook: weighted out-of-fold ROC-AUC 0.701, PR-AUC 0.507.
2. Calibration: done in the Phase 4 notebook. After the prior correction (subtract log `scale_pos_weight` from the margin) the weighted mean prediction is 0.290 against 0.292 observed, and every decile is within 0.8 points of its observed rate.
3. Make `notebooks/PCA_FLEMMS_streamlined.ipynb` Phase 2 standalone or retire it in favour of the ALE notebook (`reference/Notebook_Verification_TODO.md` item 6). The ALE notebook is already standalone.
4. The three `xgboost_*.csv` files predate the audit. Treat them as superseded until regenerated from the audited model.

### Phase 3: XAI stack (PARTIAL)

Done (`ALE_LEAKAGE_FINDINGS.md`, section 4):

- Weighted ALE on the log-odds scale for the 12 highest-gain features plus age. Half-sample differences are at most 0.011.
- Completing elementary or lower secondary roughly halves the odds of functional illiteracy (odds ratios 0.52 and 0.50). Digital skill and internet use lower the odds by about 8 to 10% each. Never using media for work or e-mail raises them by about 17%.
- Age effect is low from 20 to 40 and rises after 40, reaching about +0.2 log-odds at 60.
- Under the audited model, schooling dominates. The older SHAP exports showed digital skill dominating. This difference should be addressed explicitly in the discussion.

Open:
1. **Friedman's H is not computed.** Compute it for the top candidate pairs on a subsample. The old SHAP interaction file points to age with school attendance and digital skill with internet use.
2. Two-dimensional ALE heatmaps for the pairs with the largest H, as the proposal promises.
3. Re-run SHAP (importance, direction, interactions) on the audited model so SHAP and ALE describe the same model.
4. Report the digital-skill block as a group (grouped SHAP), since the items are highly correlated.

### Phase 4: spatial layer and simulation (DONE)

Notebook: `04_spatial_lisa_simulation/LISA_scenario_simulation.ipynb`, first executed 2026-10-24, full run with boundaries 2026-10-28. Results: `04_spatial_lisa_simulation/LISA_FINDINGS.md`. All steps ran. LISA significance rule: permutation p < 0.05 (decided 2026-10-25), with BH-FDR as a sensitivity column.

Steps:
1. Boundaries: OCHA COD-AB city/municipality polygons dissolved to PRV units through `prv_crosswalk.csv` (names from PSA value set `PRV_VS1`; all 118 codes matched). Code 999 (`BARMM63`, n = 589) stays out of the weights and targets.
2. Aggregate predicted probabilities to province level with `RESP_RFACT_F2`, next to the observed weighted rate.
3. Build spatial weights (queen contiguity plus a nearest-neighbour rule for islands), then global Moran's I and LISA with permutation inference.
4. Scenario simulation: change selected inputs (for example internet use or digital skill) in high-risk provinces, re-score with the audited model, and report the change in predicted risk with uncertainty.
5. Describe results as model-based scenarios, not causal effects.

## 4. Order of work

1. Reconcile component counts and port the constant-column drop (Phase 1).
2. Run the remaining data-quality checks (Phase 1).
3. Recompute the PCA overlap and update `01b_supervised_selection/` from the training-only list (Phase 1B).
4. Tune and cross-validate the model, add calibration (Phase 2).
5. Compute Friedman's H, 2D ALE, and re-run SHAP on the audited model (Phase 3).
6. ~~Build the spatial layer and simulation (Phase 4).~~ Done 2026-10-28.
7. Replace placeholder values in the manuscript with the numbers above.

## 5. Manuscript edits already supported by results

These can be written now with real numbers:

- Chapter 3 data: analysis universe, weights, design effect, missingness structure (`EDA_FINDINGS.md`).
- Chapter 4 PCA role: variance versus relevance evidence (rank correlation 0.65, best component AUC 0.614).
- Chapter 4 validation: household-grouped split, training-only selection, proxy exclusion (`ALE_LEAKAGE_FINDINGS.md`).
- Chapter 4 ALE: the contrast with ceteris paribus marginal effects can now cite actual curves.

- Spatial results: global Moran's I, LISA clusters, residual clusters and re-targeted simulation (`LISA_FINDINGS.md`).

Wait on: H-statistic text, tuned performance figures.

## 6. Decisions for the adviser or Sarah

1. Report selected features at dummy level or original-variable level.
2. Keep or drop Form 3 variables with unverified skip logic if the questionnaire cannot be found.
3. Whether moderate discrimination (AUC about 0.70) changes how strongly the manuscript describes the model as an early warning system.

Decided 2026-10-25: PCA count from the EDA run (504), LISA rule p < 0.05, spatial folder renamed to `04_spatial_lisa_simulation/`. Resolved 2026-10-28: boundaries (OCHA COD-AB) and PRV crosswalk (PSA `PRV_VS1`).
