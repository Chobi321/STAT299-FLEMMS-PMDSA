# Phase 4 Findings: Spatial Layer and Scenario Simulation (`LISA_scenario_simulation.ipynb`)

Run date: 2026-10-24. Notebook executed end to end against the local `data/` directory, no cell errors. All rates use `RESP_RFACT_F2`. Target `y` = 1 if functionally illiterate.

**Status: partial.** The model, province aggregation and simulation sections ran. The LISA sections (spatial weights, global Moran's I, local clusters, maps) were skipped because no boundary file is in `data/geo/`. Sections 4 and 5 below are placeholders until that run.

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

| PRV | n | Observed | Predicted | Residual |
|---|---|---|---|---|
| 70 | 4,693 | 66.4% | 49.0% | +17.4 |
| 67 | 4,435 | 42.9% | 30.4% | +12.5 |
| 2 | 4,590 | 44.3% | 32.2% | +12.0 |
| 73 | 4,098 | 48.9% | 37.0% | +12.0 |
| 60 | 4,475 | 46.1% | 34.1% | +11.9 |
| 81 | 2,164 | 13.2% | 30.9% | -17.8 |
| 11 | 3,639 | 12.1% | 27.1% | -15.0 |
| 814 | 1,180 | 5.5% | 20.2% | -14.8 |
| 66 | 4,289 | 22.8% | 36.2% | -13.4 |
| 901 | 1,949 | 21.9% | 35.1% | -13.2 |

Positive residuals mark provinces worse than their population profile predicts; negative residuals mark provinces doing better. Province names are `[DATA MISSING]` until the PRV crosswalk is filled.

## 3. Scenario simulation

Design (notebook section 9): in each target province, people in the internet question's universe who are not already at the target level are switched at random until the weighted share at the target state rises by 10 percentage points. Every person is re-scored by their own out-of-fold model. The effect is the change in the weighted mean predicted rate over all residents. 50 Monte Carlo draws of who takes up the change give the interval below; a cluster bootstrap interval per province is in `simulation_province_effects.csv`. Digital-skill items are switched as a block because they are highly correlated.

Target provinces (fallback rule, because LISA did not run): the top fifth of observed rates, 24 PRV codes, 102,256 rows, 20.1% of the weighted population. Code 999 is excluded.

| Scenario | Variables switched | Effect in target provinces (pp) | MC interval (pp) | National effect (pp) |
|---|---|---|---|---|
| Internet use | `INTERNET` | -0.28 | -0.29 to -0.28 | -0.06 |
| Digital skills | 7 `DSKILL_*` items | -0.91 | -0.92 to -0.89 | -0.18 |
| Internet plus skills | 8 variables | -1.08 | -1.09 to -1.05 | -0.22 |

Reading the table:

- Effects are small. A 10-point rise in uptake lowers the predicted rate in the target provinces by at most about 1 point, about 11 points per person switched in the combined scenario.
- Digital skills move predictions about three times as much as internet use alone, and the two together add up to slightly less than their sum.
- The intervals are narrow because they cover only who is drawn for uptake, not refitting uncertainty. They show the result is stable, not that it is causal.
- This is consistent with the ALE results: schooling dominates, and each digital item lowers the odds by about 8 to 10%.
- These are model-based scenarios. They show how the model's predictions respond to a change in inputs, not the effect of a policy.

Figure: `lisa_figures/simulation_effects.png`.

## 4. Global Moran's I `[DATA MISSING: needs boundaries]`

To be filled from `global_morans_i.csv`: Moran's I for observed rate, predicted rate and residual, under queen contiguity (islands attached to their nearest neighbour) and KNN k = 6, 9,999 permutations.

## 5. LISA clusters `[DATA MISSING: needs boundaries]`

To be filled from `lisa_clusters.csv`. Significance rule: permutation p < 0.05 (`cluster_p05`). The BH-FDR column (`cluster_fdr`) is reported as a sensitivity check only.

Questions the run should answer:

1. Are high observed rates clustered (High-High units), and where?
2. Do the predicted rates cluster in the same places? If yes, composition explains the clustering.
3. Do residuals cluster? A residual High-High cluster means a place-level factor outside the model features. PRV 70, 67, 2, 73 and 60 are the candidates to check.
4. Once the High-High units exist, the simulation re-targets them, and section 3 is re-run.

## 6. Limits and open points

1. **Boundaries and crosswalk.** Need `data/geo/flemms_units.gpkg`, or `data/geo/phl_adm3.gpkg` plus `data/geo/prv_crosswalk.csv` (start from `prv_crosswalk_template.csv`). Fill names from the PSA codebook, not by code order.
2. **Code 999** (n = 589, rate 51.3%) is unresolved. It is kept in the tables and left out of the weights and targets.
3. **Simulation universe.** The universe for `INTERNET` and `DSKILL_*` is inferred from the data. The Form 3 questionnaire is not in the repo, so it is unverified.
4. **Untuned model.** Hyperparameters are the ALE notebook's defaults (300 trees, depth 6, learning rate 0.05).
5. **Interval coverage.** Neither interval includes model refitting uncertainty.

## 7. Files

| File | Content |
|---|---|
| `LISA_scenario_simulation.ipynb` | Full run with outputs |
| `oof_model_metrics.csv` | Out-of-fold metrics and calibration shift |
| `oof_calibration_deciles.csv` | Calibration by predicted-risk decile |
| `province_rates_observed_predicted.csv` | Province table (input to LISA) |
| `simulation_summary.csv` | Scenario effects, target and national |
| `simulation_province_effects.csv` | Scenario effects per target province with MC and bootstrap intervals |
| `prv_crosswalk_template.csv` | PRV codes to be named |
| `lisa_figures/` | Calibration and simulation figures; LISA maps after the boundary run |
