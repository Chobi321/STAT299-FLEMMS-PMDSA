# Consultation, 6 November 2026

Notebooks for this meeting: `1_model_and_drivers.ipynb` and `2_geography_and_scenarios.ipynb`. Both read saved results and run in seconds.

## Where we are

| Objective | Status |
|---|---|
| 1. Spatial precursor (LISA) | Done |
| 2. Predictive model | Done except hyperparameter tuning |
| 3. Drivers and scenario simulation | Done except interpreting the 2D interaction plots |

## Four results

1. **The model ranks people moderately well.** Weighted ROC-AUC is 0.71 on households it never saw (PR-AUC 0.52). It is well calibrated: mean prediction 0.288 against 0.292 observed. We treat it as an area-level tool, not a screening tool for individuals.
2. **Schooling is the main driver, digital skills second.** Grouped SHAP is 0.224 for schooling and 0.174 for the digital-skill block. The model is close to additive: no supported interaction has H² above 0.054.
3. **Illiteracy is spatially clustered, and mostly because of who lives where.** Moran's I is 0.34 (observed) against 0.65 (predicted). What the model leaves unexplained clusters only weakly (0.10).
4. **More digital uptake changes predictions by about one point.** Raising uptake by 10 points in the 11 hotspot provinces lowers predicted illiteracy by 0.3 (internet), 0.9 (skills) or 1.0 (both) percentage points there, and under 0.1 nationally. This is how the model responds, not a policy effect.

## What changed since the defense

- Features are chosen on training households only. Choosing on all rows made no difference to AUC.
- We dropped `READ_IND_F3`, which restates the outcome.
- The train and test split is grouped by household.
- The feature count now comes from a cross-validated sweep (44 became 75 variables, AUC 0.702 to 0.711).
- PCA is a diagnostic, not a selector.

## Caveats

- The 11 hotspot provinces (Samar and Leyte, Zamboanga, southern Davao, Sarangani, Surigao del Norte) hold at p < 0.05 but none survives BH-FDR. We call them suggestive.
- The Form 3 questionnaire is not in our files, so skip logic is unverified. `TVOCTRAIN_5` looks partly like an education indicator.
- Single-dummy schooling odds ratios are smaller in the 75-variable model (elementary 0.91, was 0.52). We quote grouped SHAP for the size of the schooling effect.
- The model is untuned (300 trees, depth 6).
- On PCA: a model on 533 components scored 0.713 against 0.702 for 44 selected features (older split). PCA does not lose accuracy. The case for supervised selection is a short, readable feature list.

## Questions for the adviser

1. **Feature count.** The strict one-standard-error rule gives k = 100 (AUC 0.7088). We used k = 75 (0.7071), which is on the flat part of the curve and has the most stable selection across folds. Is that acceptable?
2. **Wording.** With AUC 0.71 and good calibration, should we describe the model as an area-level early warning tool, not an individual-level one?
3. **Reporting level.** Report the 75 selected variables, with dummy levels only in the SHAP and ALE tables?

## Next steps

1. Hyperparameter tuning.
2. Interpret the 2D ALE heatmaps.
3. Recompute the PCA overlap against the 75-variable list. The old 9 of 44 is stale.
4. Replace the placeholder numbers in the manuscript.
