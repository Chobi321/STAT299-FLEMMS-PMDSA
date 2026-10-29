# Handover: 2026-10-29

> This is a temporary session handover document. Read once at the start of the session to restore state, then DELETE or DISCARD `docs/handover.md`. Do not retain this file in future context windows.

## Current objective and state

- **Goal:** Close Phase 3 (XAI) items from `PROJECT_PLAN.md`: SHAP on the audited model, grouped SHAP, Friedman's H, 2D ALE heatmaps.
- **Status:** SHAP, grouped SHAP and H are done and written up. The 2D ALE redraw for supported pairs is coded in `02_xgboost_xai/ALE_leakage_audit.ipynb` section 11 but has **not completed a run**: Claude Code killed it for low system memory (three times today). Committed heatmap/`ale_2d_values.csv`/section 11 outputs are from the older unsupported-pair run.

## Key decisions (why)

- **TreeSHAP via XGBoost native `pred_contribs`/`pred_interactions`**: `shap` is not installed; same algorithm, no new dependency.
- **New `*_audited.csv` file names**: old `xgboost_*.csv` kept for the pre-audit comparison.
- **Same-variable dummy pairs excluded** from interactions (e.g. `HGC_LEVEL_1` x `HGC_LEVEL_2`): mutually exclusive, not an interaction.
- **2D ALE pairs need full joint support** (every cell >= 0.1% weighted rows): top three H² pairs (studying x age, `TVOCTRAIN_5` x `HGC_LEVEL_1/2`) sit on combinations absent from the data, so their H² and heatmaps are extrapolation.
- **Reporting rule for the paper**: grouped SHAP for magnitude, ALE for direction (per-dummy SHAP direction flips vs ALE for multi-level variables). Rank drivers by SHAP/ALE, not gain.

## Actions completed

- `PROJECT_PLAN.md`: Phase 4 marked DONE; Phase 3 results and remaining item recorded.
- Stale `docs/handover/HANDOVER_2026-10-22_2130.md` deleted; `~$*` in `.gitignore`.
- Notebook sections 9 to 11 added; outputs `shap_importance_audited.csv`, `shap_grouped_importance_audited.csv`, `shap_interactions_audited.csv`, `friedman_h_pairs.csv`.
- `02_xgboost_xai/ALE_LEAKAGE_FINDINGS.md` section 6 (SHAP, H, 2D ALE, `TVOCTRAIN` skip-logic evidence). AUC 0.702 reproduced.

## Next steps

- [ ] Run the notebook **in a terminal outside Claude Code** (or start Claude Code with `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`), close memory-heavy apps first:
  `cd 02_xgboost_xai && jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 ALE_leakage_audit.ipynb`
- [ ] Read section 11 output: which pairs pass support (`friedman_h_pairs.csv` `Supported` column), then replace the "Pending run" paragraph in `ALE_LEAKAGE_FINDINGS.md` 6.3 and Phase 3 open item 1 in `PROJECT_PLAN.md`; commit `ale_2d_support.csv`, `ale_2d_values.csv`, the PNG.
- [ ] Remaining list: Phase 2 hyperparameter tuning; Phase 1B write training-only list into `01b_supervised_selection/`; data-quality items 2 to 5 in `reference/Notebook_Verification_TODO.md`; check `paper/final_paper_draft.docx` against settled numbers.

## Constraints and blockers

- Full run reloads ~470k rows and refits several models; memory is the blocker, not the code (all code cells pass `ast.parse`).
- If few or no pairs pass the 0.1% support rule, the cell asserts `no candidate pair has full joint support`. Fallback to discuss: mask unsupported cells instead of excluding pairs.
- When running nbconvert, do not pipe through `tail`/`grep` without keeping the exit code; a SyntaxError was hidden that way once.
- Commits: no AI attribution (project rule).
