# Phase 4 Findings: Spatial Layer and Scenario Simulation

Notebook: `LISA_scenario_simulation.ipynb`, re-run 2026-11-01 on the 75-variable model (551 dummies from `02_xgboost_xai/selected_features_train_only.csv`). Earlier 45-feature results are in `archive_45feature/`. All rates use `RESP_RFACT_F2`. Target `y` = 1 if functionally illiterate.

Boundaries: OCHA COD-AB city/municipality polygons (`data/geo/phl_adm3.gpkg`) dissolved to PRV units through `prv_crosswalk.csv` (names from PSA value set `PRV_VS1`, all 118 codes matched). Code 999 (`BARMM63`, n = 589) has no polygon and stays out of the weights and targets, leaving 117 spatial units.

## 1. Out-of-fold model

The model is refit in 5 folds grouped by household, so every person is scored by a model that never saw their household.

| Item | 75-variable model | 45-feature model |
|---|---|---|
| Weighted ROC-AUC, out of fold | 0.709 | 0.701 |
| Weighted PR-AUC, out of fold | 0.517 | 0.507 |
| Unweighted ROC-AUC, out of fold | 0.716 | 0.709 |
| Observed weighted prevalence | 0.292 | 0.292 |
| Mean prediction after prior correction | 0.288 | 0.290 |

- No intercept shift was applied (gap 0.4 points, below the 0.5 threshold).
- **Calibration.** Subtracting log `scale_pos_weight` from the margin (prior correction) is enough. Deciles 1 to 9 are within 0.9 points of the observed rate. Decile 10 under-predicts: 0.603 against 0.630 observed (2.7 points). The old model's worst decile was off by 0.8 points. Province means can still be read as risk levels, with the top decile slightly low. Files: `oof_calibration_deciles.csv`, `lisa_figures/oof_calibration.png`.

## 2. Province aggregation

`province_rates_observed_predicted.csv` has, per PRV code: n, household clusters, weighted population, observed and predicted rate with SEs, residual (observed minus predicted) and CV.

- Observed rates match `00_eda/eda_province_rates.csv`, so both notebooks use the same universe.
- Observed and predicted provincial rates correlate at 0.79 (0.77 before). The model features explain most of the provincial pattern.
- Residuals run from -17.7 to +17.8 points. The largest CV is 0.193 (PRV 814, n = 1,180), so no unit is too noisy to map.

Largest residuals (positive means worse than the population profile predicts):

| PRV | Name | n | Observed | Predicted | Residual |
|---|---|---|---|---|---|
| 70 | Tawi-Tawi | 4,693 | 66.4% | 48.6% | +17.8 |
| 67 | Surigao del Norte | 4,435 | 42.9% | 30.4% | +12.5 |
| 2 | Agusan del Norte | 4,590 | 44.3% | 31.9% | +12.4 |
| 73 | Zamboanga del Sur | 4,098 | 48.9% | 37.0% | +12.0 |
| 60 | Samar (Western) | 4,475 | 46.1% | 35.2% | +10.9 |
| 81 | Apayao | 2,164 | 13.2% | 30.8% | -17.7 |
| 814 | San Juan | 1,180 | 5.5% | 19.5% | -14.1 |
| 11 | Benguet | 3,639 | 12.1% | 25.5% | -13.3 |
| 66 | Sulu | 4,289 | 22.8% | 36.1% | -13.3 |
| 59 | Romblon | 4,057 | 18.1% | 31.3% | -13.2 |

## 3. Global Moran's I

13 island units have no queen neighbour and are attached to their nearest unit (3.6 neighbours on average, 9 components). KNN-6 gives one component. 9,999 permutations.

| Variable | Queen I | p | KNN-6 I | p |
|---|---|---|---|---|
| Observed rate | 0.340 | 0.0001 | 0.375 | 0.0001 |
| Predicted rate | 0.649 | 0.0001 | 0.611 | 0.0001 |
| Residual | 0.098 | 0.093 | 0.111 | 0.011 |

- Observed illiteracy is spatially clustered under both schemes.
- Predicted rates cluster almost twice as strongly, so the pattern is largely compositional.
- Residual clustering is weak: not significant under queen weights, significant under KNN-6.

Files: `global_morans_i.csv`, `spatial_weights_summary.csv`.

## 4. LISA clusters

Rule: permutation p < 0.05 (`cluster_p05`), queen weights. BH-FDR (`cluster_fdr`) is a sensitivity column. BH-FDR controls the expected share of false positives among the clusters declared, which matters here because 117 units are tested at once.

| Variable | Rule | High-High | Low-Low | Low-High | High-Low | Not sig. |
|---|---|---|---|---|---|---|
| Observed | p < 0.05 | 11 | 17 | 4 | 0 | 85 |
| Observed | BH-FDR | 0 | 8 | 1 | 0 | 108 |
| Predicted | p < 0.05 | 14 | 21 | 1 | 0 | 81 |
| Predicted | BH-FDR | 1 | 15 | 0 | 0 | 101 |
| Residual | p < 0.05 | 7 | 6 | 5 | 3 | 96 |
| Residual | BH-FDR | 0 | 0 | 0 | 0 | 117 |

**Robustness.** No observed High-High unit and no residual cluster survives BH-FDR. Only Sulu survives as a predicted High-High unit. Metro Manila Low-Low largely survives (8 of 17 observed). Report high-risk clusters as suggestive at the unadjusted level, with this caveat.

Observed-rate clusters (p < 0.05):

| Cluster | Units |
|---|---|
| High-High (11) | Eastern Samar, Northern Samar, Samar (Western), Leyte; Zamboanga del Norte, Zamboanga del Sur, Zamboanga Sibugay; Davao del Sur, Davao Occidental; Sarangani; Surigao del Norte |
| Low-Low (17) | Caloocan, Makati, Mandaluyong, Manila, Marikina, Muntinlupa, Paranaque, Pasay, Pasig, Quezon City, San Juan, Taguig, Pateros; Bulacan, Cavite, Rizal; Baguio City |
| Low-High (4) | Misamis Occidental, South Cotabato, Sulu, Isabela City |

Predicted-rate High-High (14): Agusan del Sur, Davao del Sur, Eastern Samar, Lanao del Norte, North Cotabato, Sultan Kudarat, Sulu, Zamboanga del Norte, Zamboanga del Sur, Sarangani, Zamboanga Sibugay, Davao Occidental, Maguindanao del Norte, Isabela City.

Residual clusters (p < 0.05): High-High (7) Eastern Samar, Northern Samar, Samar (Western), Surigao del Norte, Biliran, Zamboanga Sibugay, Dinagat Islands. Low-Low (6) Baguio City, Makati, Mandaluyong, Pasig, Taguig, Pateros. High-Low (3) Basilan, Tawi-Tawi, Quezon City. Low-High (5) Leyte, Misamis Occidental, South Cotabato, Sulu, Mandaue City.

Answers to the questions set before the run:

1. **Are high observed rates clustered?** Yes at p < 0.05: Eastern Visayas (Samar island and Leyte), the Zamboanga Peninsula and southern Davao. None survives FDR.
2. **Do predicted rates cluster in the same places?** Partly. Zamboanga and southern Davao appear in both. The predicted cluster extends into central Mindanao (Lanao, Cotabato, Sultan Kudarat, Maguindanao).
3. **Do residuals cluster?** Weakly. The Samar island group is High-High on both observed rate and residual, the strongest candidate for a place-level factor outside the model.

Files: `lisa_clusters.csv`, `lisa_figures/lisa_cluster_maps.png`, `lisa_figures/choropleth_rates.png`. The cluster lists above use the same 11 observed High-High units as the 45-feature run.

## 5. Scenario simulation

In each target province, people in the question's universe who are not at the target level are switched at random until the weighted share at the target state rises by 10 points. Each person is re-scored by their own out-of-fold model, and the effect is the change in the weighted mean predicted rate over all residents. 50 Monte Carlo draws give the interval; cluster-bootstrap intervals per province are in `simulation_province_effects.csv`.

Targets: the 11 observed High-High PRV codes (24, 26, 37, 48, 60, 67, 72, 73, 80, 83, 86), 7.8% of the weighted population.

| Scenario | Variables switched | Target provinces (pp) | MC interval (pp) | National (pp) |
|---|---|---|---|---|
| Internet use | `INTERNET` | -0.31 | -0.31 to -0.30 | -0.02 |
| Digital skills | 10 `DSKILL_*` items | -0.89 | -0.91 to -0.87 | -0.07 |
| Internet plus skills | 11 variables | -1.04 | -1.08 to -1.03 | -0.08 |

The 45-feature run gave -0.33, -0.93 and -1.11 pp (national -0.03, -0.07, -0.09).

- Effects are small: a 10-point rise in uptake lowers the predicted rate in the target provinces by about 1 point at most.
- Digital skills move predictions about three times as much as internet use alone, and the two together add up to less than their sum.
- The target set rests on High-High units that do not survive BH-FDR, so treat it as a working definition of high-risk areas.
- The intervals cover only who is drawn for uptake, not refitting uncertainty. These are model-based scenarios, not causal effects of a policy.
- The small effects fit the ALE and SHAP results: schooling dominates and each digital item lowers the odds by about 6 to 9%.

Figure: `lisa_figures/simulation_effects.png`.

## 6. Limits

1. **Cotabato City** has no PRV code in the data (code 98 unused). Its polygon is dissolved into PRV 87, and where its respondents are coded is unverified.
2. **Code 999** (n = 589, rate 51.3%) matches the BARMM Special Geographic Area (`PH19099`). Mapping it would add a unit with n = 589.
3. **Multiple testing.** High-High clusters rest on unadjusted p-values (section 4).
4. **Simulation universe.** The universe for `INTERNET` and `DSKILL_*` is inferred, since the Form 3 questionnaire is not in the repo.
5. **Untuned model.** 300 trees, depth 6, learning rate 0.05.
6. **Interval coverage.** Neither interval includes model refitting uncertainty.
7. **Memory.** The spatial-weights cell peaks at 9.2 GB (`benchmarks/BENCHMARKS.md`). Close other applications before running.

## 7. Files

| File | Content |
|---|---|
| `LISA_scenario_simulation.ipynb` | Full run with outputs |
| `oof_model_metrics.csv`, `oof_calibration_deciles.csv` | Out-of-fold metrics and calibration |
| `province_rates_observed_predicted.csv` | Province table (input to LISA) |
| `simulation_summary.csv`, `simulation_province_effects.csv` | Scenario effects |
| `global_morans_i.csv`, `lisa_clusters.csv`, `spatial_weights_summary.csv` | Spatial results |
| `prv_crosswalk.csv`, `prv_crosswalk_template.csv` | PRV to boundary code |
| `lisa_figures/` | Calibration, simulation, choropleth, Moran and LISA maps |
| `archive_45feature/` | Previous 45-feature outputs |
