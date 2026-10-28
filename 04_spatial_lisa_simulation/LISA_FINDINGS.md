# Phase 4 Findings: Spatial Layer and Scenario Simulation (`LISA_scenario_simulation.ipynb`)

Run date: 2026-10-28. Notebook executed end to end against the local `data/` directory, no cell errors. All rates use `RESP_RFACT_F2`. Target `y` = 1 if functionally illiterate.

**Status: complete.** All sections ran, including spatial weights, global Moran's I, local clusters and maps. Boundaries: option B, city/municipality polygons (`data/geo/phl_adm3.gpkg`, exported from the `phl_admin3` layer of `data/phl_admin_boundaries.gdb`, OCHA COD-AB) dissolved to PRV units through `data/geo/prv_crosswalk.csv`. The crosswalk takes each PRV name from the PSA value set `PRV_VS1` in `flemms_2024_v1_metadata(dictionary).xlsx` and matches it to a boundary code by name. All 118 codes matched. The model and province sections reproduce the 2026-10-24 run exactly; the simulation changed because it now targets the LISA High-High units instead of the fallback rule.

## 1. Out-of-fold model

Each person needs an honest prediction to aggregate to province level, so the primary model (45 features from `02_xgboost_xai/selected_features_train_only.csv`, same hyperparameters as the ALE notebook) is refit in 5 folds grouped by household (`GroupKFold` on `HHID`). Every person is scored by the fold model that did not see their household.

| Item | Value |
|---|---|
| Rows, households, PRV codes | 468,643, 163,655, 118 |
| Weighted ROC-AUC, out of fold | 0.701 |
| Weighted PR-AUC, out of fold | 0.507 |
| Unweighted ROC-AUC, out of fold | 0.709 |
| Observed weighted prevalence | 0.292 |
| Weighted mean prediction after prior correction | 0.290 |
| Intercept shift applied | 0 (gap below 0.5 points) |

- Cross-validated discrimination matches the single held-out split of the ALE notebook (0.702), so the earlier figure was not a lucky split.
- **Calibration.** `scale_pos_weight` shifts the log-odds by log(spw). Subtracting that shift from the margin (prior correction) is enough. In every predicted-risk decile the weighted mean prediction is within 0.8 points of the observed rate (decile 1: 0.090 vs 0.098; decile 10: 0.614 vs 0.616). Province means of predicted probabilities can therefore be read as risk levels, not only as rankings. Table: `oof_calibration_deciles.csv`; figure: `lisa_figures/oof_calibration.png`.

## 2. Province aggregation

`province_rates_observed_predicted.csv` holds, per PRV code: n, number of household clusters, weighted population, observed rate and its linearised cluster SE, mean predicted rate and its SE, residual (observed minus predicted), and the CV of the observed rate.

- Observed rates match `00_eda/eda_province_rates.csv` exactly (max difference 1.1e-16), so the two notebooks use the same universe.
- Observed and predicted provincial rates correlate at 0.77. Individual composition on the model features explains most, but not all, of the provincial pattern.
- Residuals run from -17.8 to +17.4 points.
- The largest observed CV is 0.193 (PRV 814, n = 1,180, rate 5.5%). All other units are more precise, so no unit is too noisy to map.

Largest residuals:

| PRV | Name | n | Observed | Predicted | Residual |
|---|---|---|---|---|---|
| 70 | Tawi-Tawi | 4,693 | 66.4% | 49.0% | +17.4 |
| 67 | Surigao del Norte | 4,435 | 42.9% | 30.4% | +12.5 |
| 2 | Agusan del Norte | 4,590 | 44.3% | 32.2% | +12.0 |
| 73 | Zamboanga del Sur | 4,098 | 48.9% | 37.0% | +12.0 |
| 60 | Samar (Western) | 4,475 | 46.1% | 34.1% | +11.9 |
| 81 | Apayao | 2,164 | 13.2% | 30.9% | -17.8 |
| 11 | Benguet | 3,639 | 12.1% | 27.1% | -15.0 |
| 814 | San Juan | 1,180 | 5.5% | 20.2% | -14.8 |
| 66 | Sulu | 4,289 | 22.8% | 36.2% | -13.4 |
| 901 | Isabela City | 1,949 | 21.9% | 35.1% | -13.2 |

Positive residuals mark provinces worse than their population profile predicts; negative residuals mark provinces doing better.

## 3. Scenario simulation

Design (notebook section 9): in each target province, people in the internet question's universe who are not already at the target level are switched at random until the weighted share at the target state rises by 10 percentage points. Every person is re-scored by their own out-of-fold model. The effect is the change in the weighted mean predicted rate over all residents. 50 Monte Carlo draws of who takes up the change give the interval below; a cluster bootstrap interval per province is in `simulation_province_effects.csv`. Digital-skill items are switched as a block because they are highly correlated.

Target provinces (LISA High-High on the observed rate, p < 0.05, section 5): 11 PRV codes (24, 26, 37, 48, 60, 67, 72, 73, 80, 83, 86), 45,909 rows, 7.8% of the weighted population. Code 999 is excluded.

| Scenario | Variables switched | Effect in target provinces (pp) | MC interval (pp) | National effect (pp) |
|---|---|---|---|---|
| Internet use | `INTERNET` | -0.33 | -0.34 to -0.32 | -0.03 |
| Digital skills | 7 `DSKILL_*` items | -0.93 | -0.94 to -0.91 | -0.07 |
| Internet plus skills | 8 variables | -1.11 | -1.14 to -1.09 | -0.09 |

The 2026-10-24 run used the fallback rule (top fifth of observed rates, 24 PRV codes, 20.1% of the weighted population) and gave -0.28, -0.91 and -1.08 pp in the target provinces and -0.06, -0.18 and -0.22 pp nationally. The per-province effects barely move; the national effects fall because the LISA target set covers fewer people.

Reading the table:

- Effects are small. A 10-point rise in uptake lowers the predicted rate in the target provinces by at most about 1 point, about 11 points per person switched in the combined scenario.
- The target set rests on High-High units that do not survive BH-FDR (section 5). Treat it as a working definition of high-risk areas, not a confirmed cluster.
- Digital skills move predictions about three times as much as internet use alone, and the two together add up to slightly less than their sum.
- The intervals are narrow because they cover only who is drawn for uptake, not refitting uncertainty. They show the result is stable, not that it is causal.
- This is consistent with the ALE results: schooling dominates, and each digital item lowers the odds by about 8 to 10%.
- These are model-based scenarios. They show how the model's predictions respond to a change in inputs, not the effect of a policy.

Figure: `lisa_figures/simulation_effects.png`.

## 4. Global Moran's I

Spatial units: 117 (code 999 has no polygon). Queen contiguity leaves 13 island units without neighbours (PRV 9, 12, 18, 20, 40, 41, 59, 61, 66, 70, 78, 79, 85); each is attached to its nearest neighbour, giving 9 connected components and 3.6 neighbours on average. KNN k = 6 gives one component. Permutations: 9,999.

| Variable | Queen I | p | KNN-6 I | p |
|---|---|---|---|---|
| Observed rate | 0.340 | 0.0001 | 0.375 | 0.0001 |
| Predicted rate | 0.649 | 0.0001 | 0.608 | 0.0001 |
| Residual | 0.114 | 0.063 | 0.125 | 0.006 |

- Observed functional illiteracy is spatially clustered under both weight schemes.
- Predicted rates cluster almost twice as strongly as observed rates. The spatial pattern is largely compositional: neighbouring provinces share the population profile the model features capture.
- Residual clustering is weak: not significant under queen weights, significant under KNN-6. Place-level factors outside the model add at most a modest spatial signal.

Table: `global_morans_i.csv`; weights: `spatial_weights_summary.csv`; figure: `lisa_figures/moran_scatter_obs.png`.

## 5. LISA clusters

Significance rule: permutation p < 0.05 (`cluster_p05`), queen weights. The BH-FDR column (`cluster_fdr`) is a sensitivity check.

| Variable | Rule | High-High | Low-Low | Low-High | High-Low | Not significant |
|---|---|---|---|---|---|---|
| Observed rate | p < 0.05 | 11 | 17 | 4 | 0 | 85 |
| Observed rate | BH-FDR | 0 | 8 | 1 | 0 | 108 |
| Predicted rate | p < 0.05 | 16 | 21 | 0 | 0 | 80 |
| Predicted rate | BH-FDR | 2 | 19 | 0 | 0 | 96 |
| Residual | p < 0.05 | 7 | 6 | 5 | 3 | 96 |
| Residual | BH-FDR | 0 | 0 | 0 | 0 | 117 |

**Robustness.** No observed-rate High-High unit and no residual cluster survives BH-FDR. The Metro Manila Low-Low cluster largely does (8 of 17 observed, 19 of 21 predicted). High-risk clusters should be reported as suggestive at the unadjusted level, with this caveat stated.

Cluster membership, observed rate (p < 0.05):

| Cluster | Units |
|---|---|
| High-High (11) | Eastern Samar, Northern Samar, Samar (Western), Leyte; Zamboanga del Norte, Zamboanga del Sur, Zamboanga Sibugay; Davao del Sur, Davao Occidental; Sarangani; Surigao del Norte |
| Low-Low (17) | Caloocan, Makati, Mandaluyong, Manila, Marikina, Muntinlupa, Parañaque, Pasay, Pasig, Quezon City, San Juan, Taguig, Pateros; Bulacan, Cavite, Rizal; Baguio City |
| Low-High (4) | Misamis Occidental, South Cotabato, Sulu, Isabela City |

Predicted-rate High-High (16): Agusan del Sur, Basilan, Davao del Sur, Lanao del Norte, Lanao del Sur, North Cotabato, Sultan Kudarat, Sulu, Zamboanga del Norte, Zamboanga del Sur, Sarangani, Zamboanga Sibugay, Davao Occidental, Maguindanao del Norte, Iligan City, Isabela City. Predicted-rate Low-Low (21): all 17 Metro Manila units plus Bulacan, Cavite, Laguna and Rizal. Baguio City is Low-Low on the observed rate only.

Residual clusters (p < 0.05):

| Cluster | Units | Reading |
|---|---|---|
| High-High (7) | Eastern Samar, Northern Samar, Samar (Western), Surigao del Norte, Biliran, Zamboanga Sibugay, Dinagat Islands | Worse than the population profile predicts, among similar neighbours |
| Low-Low (6) | Baguio City, Makati, Mandaluyong, Pasig, Taguig, Pateros | Better than predicted, among similar neighbours |
| High-Low (3) | Basilan, Tawi-Tawi, Quezon City | Worse than predicted, isolated |
| Low-High (5) | Leyte, Misamis Occidental, South Cotabato, Sulu, Mandaue City | Better than predicted, isolated |

Answers to the questions set before the run:

1. **Are high observed rates clustered?** Yes, at p < 0.05: Eastern Visayas (Samar island and Leyte), the Zamboanga Peninsula and southern Davao. None survives FDR.
2. **Do predicted rates cluster in the same places?** Partly. The predicted High-High cluster shifts south and west into BARMM and central Mindanao (Lanao, Maguindanao, Basilan, Sulu, Cotabato), where composition predicts high risk. Zamboanga and southern Davao are in both.
3. **Do residuals cluster?** Weakly. The Samar island group (Eastern, Northern, Western Samar, with Biliran) is High-High on both observed rate and residual, which makes it the strongest candidate for a place-level factor outside the model features. Of the five largest positive residuals named before the run, Surigao del Norte and Samar (Western) fall in the residual High-High cluster and Tawi-Tawi is High-Low; Zamboanga del Sur and Agusan del Norte are not significant.
4. **Simulation re-targeted.** Section 3 now uses the 11 observed High-High units.

Table: `lisa_clusters.csv` (local I, p, quadrant, both cluster rules, per unit and variable); figures: `lisa_figures/lisa_cluster_maps.png`, `lisa_figures/choropleth_rates.png`.

## 6. Limits and open points

1. **Cotabato City** has no PRV code in the data (value-set code 98 is unused). Its polygon sits inside Maguindanao del Norte in the boundary file and is dissolved into PRV 87. Where its respondents are coded is unverified.
2. **Code 999** (n = 589, rate 51.3%) is labelled `BARMM63` in the PSA value set, which matches the 63 barangays of the BARMM Special Geographic Area (boundary code `PH19099`). It stays out of the weights and targets, and the 8 Special Geographic Area polygons are left off the map. Mapping 999 to `PH19099` is possible but would add a unit with n = 589.
3. **Multiple testing.** The headline High-High clusters rest on unadjusted permutation p-values (section 5).
4. **Simulation universe.** The universe for `INTERNET` and `DSKILL_*` is inferred from the data. The Form 3 questionnaire is not in the repo, so it is unverified.
5. **Untuned model.** Hyperparameters are the ALE notebook's defaults (300 trees, depth 6, learning rate 0.05).
6. **Interval coverage.** Neither interval includes model refitting uncertainty.

## 7. Files

| File | Content |
|---|---|
| `LISA_scenario_simulation.ipynb` | Full run with outputs |
| `oof_model_metrics.csv` | Out-of-fold metrics and calibration shift |
| `oof_calibration_deciles.csv` | Calibration by predicted-risk decile |
| `province_rates_observed_predicted.csv` | Province table (input to LISA) |
| `simulation_summary.csv` | Scenario effects, target and national |
| `simulation_province_effects.csv` | Scenario effects per target province with MC and bootstrap intervals |
| `global_morans_i.csv` | Global Moran's I, three variables by two weight schemes |
| `lisa_clusters.csv` | Local I, p-values and cluster labels per unit and variable |
| `spatial_weights_summary.csv` | Queen and KNN-6 weight diagnostics |
| `prv_crosswalk_template.csv` | Blank template; the filled crosswalk is `data/geo/prv_crosswalk.csv` (gitignored) |
| `lisa_figures/` | Calibration, simulation, choropleth, Moran scatter and LISA cluster maps |
