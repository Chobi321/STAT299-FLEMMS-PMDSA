# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A STAT299 thesis research project: *"A Spatial and Machine Learning Approach to Identifying High-Risk Functional Literacy Areas in the Philippines."* It has two halves that should not be conflated:

1. **The proposal/manuscript** — a set of Markdown chapter files (academic prose).
2. **The analysis** — a single Jupyter notebook implementing a PCA → XGBoost → SHAP/ALE pipeline over PSA FLEMMS 2024 survey data, plus its CSV outputs.

There is no build, lint, or test tooling — this is not a software package. "Running the project" means executing notebook cells against the (gitignored, locally-supplied) `data/` directory.

## Working with the proposal text (`01_*.md`–`04_*.md`)

Read `context_map.md` first — it indexes which chapter file covers which topic (introduction/scope, lit review, data methodology, model methodology) specifically so you can **read only the relevant chapter file instead of all of them**, to conserve context.

`readme.md` contains the binding "Research Writing Protocol" for any writing/editing in this repo. Key rules from it:
- Academic, precise, dense tone. Never use "delve", "testament", "tapestry", "revolutionize", "beacon", "it's worth noting", "in conclusion".
- Never invent citations, DOIs, data points, or author names. If something is missing/uncertain, write `[CITATION NEEDED]` or `[DATA MISSING]` — do not fill it in.
- Prefer user-provided PDFs/reference libraries/`.bib` files over general knowledge for factual claims.
- Surgical edits only — don't rewrite a whole section to fix one paragraph.
- IMRaD structure by default. Abstracts ≤250 words, sequenced Background → Objective → Method → Results → Conclusion.
- Active voice ("We measure...") over passive.
- Flag claims lacking empirical support or logical continuity rather than smoothing over them.
- If a prompt's premise is unclear or contradictory, stop and ask rather than guessing.

## The analysis pipeline (`PCA_FLEMMS_streamlined.ipynb`)

Two phases, each a self-contained block of cells (Phase 2 reloads and re-derives everything Phase 1 computed rather than reusing in-memory objects — treat them as independently runnable):

**Phase 1 — Dimensionality reduction (diagnostic only, as of the Option C revision below):**
1. `load_and_merge_flemms()` merges four raw PSA CSVs (`MEMBER`, `RTF1` household, `RTF2` literacy/target, `RTF3` ICT) on `HHID`/`LNO`, dropping PSA's duplicated geographic columns before merging. Filters to the 10–64 working-age universe.
2. `preprocess_for_pca_memory_safe()` drops identifiers/survey weights/target-leakage columns (see the `identifiers` list — anything derived from Form 2 literacy results is leakage and must stay excluded, including `BASIC_NUM`), forces remaining columns to categorical, drops high-cardinality columns (>50 uniques) to save RAM, imputes (median for numeric, constant `'Not_Applicable'` for categorical), one-hot encodes, and standard-scales.
3. `run_pca_optimized()` fits PCA to a 95% variance threshold (752 → 539 components).
4. `extract_top_features()` takes the top 10 components and the top 5 highest-loading features each, producing 44 unique features (`phase_1_features`) — reported only as a diagnostic list, not fed to the model (see Phase 1B).
5. `build_dynamic_dictionary_from_excel()` / `clean_psa_labels()` turn PSA's raw value-set Excel dictionaries (`flemms_2024_v*_metadata(dictionary).xlsx`) into human-readable feature labels; manual overrides exist for continuous variables (`FATHER`, `MOTHER`, `AGE`) and for digital-skill dummy columns that PSA labels identically (see `digital_skill_translations` in Phase 2 — if you rename/add modeling features, this mapping needs to stay in sync).
6. Output: `phase1_selected_features.csv` (Feature_Name, Descriptive_Name) — PCA's variance-based picks, kept for the overlap comparison, no longer the model's input list.

**Phase 1B — Supervised feature selection (Option C: PCA is a diagnostic, not a selector):**
Addresses the defense panel's "variance ≠ relevance" critique directly instead of just asserting it as a limitation. Reuses Phase 1's `X_scaled`/`feature_names` (all 752 encoded features), trains an `XGBClassifier` against the real target (same `scale_pos_weight`/`sample_weight=RESP_RFACT_F2` treatment as Phase 2) to rank features by gain, and takes the top 44 by that ranking instead of by PCA loading. Reports the overlap between the PCA-selected and supervised-selected lists (`phase1b_pca_vs_supervised_overlap.csv`) and writes the supervised list — with the same descriptive-name treatment as Phase 1 — to `phase1b_selected_features.csv`, which Phase 2 now reads instead of `phase1_selected_features.csv`.

**Phase 2 — Predictive modeling (XGBoost + XAI):**
1. Re-merges raw data, re-encodes, then filters columns down to exactly the 44 (or so) features from `phase1b_selected_features.csv`, plus target `FLITERATE` and weight `RESP_RFACT_F2`.
2. Target normalization: PSA encodes `FLITERATE` as 1=Literate/2=Illiterate; this is remapped to 0=Literate/1=Illiterate throughout.
3. `XGBClassifier` trained with `scale_pos_weight` (class imbalance) and `sample_weight=RESP_RFACT_F2` (survey design weight) — **both are required for results to represent the true national population**, not just the sample.
4. 80/20 stratified split, `random_state=42` used consistently across PCA/split/model for reproducibility.
5. Exports three CSVs, each carrying both the raw `Feature` name and its `Descriptive_Name`:
   - `xgboost_basic_importance.csv` — gain-based feature importance.
   - `xgboost_shap_ale_impact.csv` — mean |SHAP| impact magnitude + correlation-derived effect direction ("Increases Risk"/"Decreases Risk").
   - `xgboost_shap_interactions.csv` — top pairwise SHAP interaction strengths (computed on a subsample of the test set — 1000–2000 rows — because full interaction values are O(n·features²) and RAM-prohibitive at the full ~93k-row test set).

Both phases are written to be RAM-conscious on the full ~496,770-row × 752-encoded-feature dataset: expect `gc.collect()` calls, subsampling for interaction values, and dropping high-cardinality columns. Preserve that pattern when extending the notebook rather than materializing full dense arrays.

Planned/unresolved spatial layer (LISA, GWR — described in `04_methodology_model.md`) is not yet implemented in the notebook.

## Git workflow

- Never add AI attribution to commit messages or pull request descriptions (no "Co-Authored-By: Claude", no "Generated with Claude Code" footer, no mention of Claude or Anthropic anywhere in the message).

## Data dependencies

Raw PSA FLEMMS 2024 CSVs and metadata dictionaries are expected under `data/PHL-PSA-FLEMMS-2024-V1-PUF/` and `data/PHL-PSA-FLEMMS-2024-V2-PUF/` (paths hardcoded at the top of each phase's first cell). `data/` is gitignored and not present in this checkout — it must be supplied locally to actually execute the notebook. The four CSV outputs in the repo root (`phase1_selected_features.csv`, `xgboost_*.csv`) are the checked-in *results* of a prior run, not regenerated automatically.
