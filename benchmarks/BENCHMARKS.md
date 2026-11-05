# Run benchmarks (75-variable model, 2026-11-01)

Machine: Windows 11, 6 CPU threads, 17.1 GB RAM (7 to 10 GB free at the start of each run). Notebooks were executed in place with `run_notebook_benchmark.py` (wall time and per-cell time from nbconvert timestamps; memory is the summed resident set of nbconvert plus its kernel, sampled every 2 s). Raw numbers: `*_cells.csv` and `*_summary.json` in this folder.

## Totals

| Notebook | Model size | Wall time | Sum of cell time | Peak memory |
|---|---|---|---|---|
| `feature_count_sweep.ipynb` (5 folds x 14 values of k) | 5 to 703 dummies | not measured | 1,839 s (31 min) | not measured |
| `ALE_leakage_audit.ipynb` | 551 dummies (S4) | 269 s | 266 s | 3.24 GB |
| `LISA_scenario_simulation.ipynb` | 551 dummies | 578 s | 572 s | 9.16 GB |

The three runs together take about 50 minutes. The sweep is a one-off; the other two are the re-runs needed whenever the feature list changes.

## Where the time goes

| Notebook | Cell | What | Seconds | Peak GB |
|---|---|---|---|---|
| Sweep | 9 | 5-fold CV over all k (70 fits plus 5 rankings) | 1,723 | n/m |
| Sweep | 16 | final ranking and test fit | 96 | n/m |
| ALE | 11 | scenarios S0 to S3 (four selections on 750 columns plus fits) | 150 | 3.24 |
| ALE | 14 | S4 fit (551 dummies) and metrics | 41 | 2.69 |
| ALE | 21 | SHAP importance, grouped SHAP, interactions (1,000 rows) | 30 | 2.53 |
| ALE | 23 | Friedman's H (8 pairs, 3,000 rows) | 13 | 2.34 |
| ALE | 25 | support tables and 2D ALE (3 pairs) | 5 | 2.57 |
| Phase 4 | 7 | out-of-fold model, 5 grouped folds | 205 | 3.38 |
| Phase 4 | 12 | province aggregation | 47 | 3.01 |
| Phase 4 | 14 | boundary dissolve and spatial weights | 31 | **9.16** |
| Phase 4 | 17 | LISA with 9,999 permutations and maps | 218 | 4.16 |
| Phase 4 | 21 | scenario simulation (3 scenarios x 50 draws) | 41 | 4.03 |

## Against the 45-feature model

The old notebooks stored timings for only part of their cells (ALE 14 cells, Phase 4 14 cells), so these are partial and the old runs had no memory log.

| Step | 45 features | 551 dummies | Change |
|---|---|---|---|
| ALE, sum of timed cells | 220 s | 266 s | +21% |
| ALE, SHAP cell | 45 s (5,000 interaction rows) | 30 s (1,000 rows) | faster, fewer rows |
| Phase 4, sum of timed cells | 412 s | 572 s | +39% |
| Phase 4, out-of-fold model | 38 s | 205 s | 5.4x |
| Phase 4, simulation | under 20 s | 41 s | about 2x or more |

Training cost grows about 5x for 12x as many columns. Notebook totals grow far less, because most of their time is in steps that do not depend on the column count (S0 to S3 selection, LISA permutations).

## Memory notes

- The ALE notebook peaks at 3.2 GB, so the 2D ALE run no longer fails for memory on this machine. The earlier kills probably came from other processes using RAM at the same time. The one failure in this session was a code error (`Series.reset_index(names=...)` needs a newer pandas than the installed one), fixed in section 11.
- SHAP interaction values cost rows x columns^2 x 4 bytes: 1,000 x 552 x 552 is 1.2 GB, so they are scored in chunks of 100 rows (peak 2.5 GB). The old 5,000-row sample would have needed about 6 GB.
- The Phase 4 peak of 9.16 GB is in the spatial-weights cell (cell 14), not in the modelling cells (3.4 to 4.2 GB). It comes from the boundary file and does not depend on the feature count, but it is the cell closest to the 17 GB limit. Close other applications before running Phase 4.

## Reproduce

From the repo root:

```
python -I benchmarks/run_notebook_benchmark.py 02_xgboost_xai/ALE_leakage_audit.ipynb 04_spatial_lisa_simulation/LISA_scenario_simulation.ipynb
```

The ALE notebook must run first because it writes `selected_features_train_only.csv`, which Phase 4 reads. The sweep (`feature_count_sweep.ipynb`) resumes from `sweep_cv_results.csv`, so delete the `sweep_*.csv` files to time a cold run.
