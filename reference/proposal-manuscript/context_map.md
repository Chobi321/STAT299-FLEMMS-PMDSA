# Reference Proposal Context Map

Use this index to target specific sections of the research proposal to conserve context tokens. Do not read other sections unless explicitly requested.

- **01_introduction.md**: Use when drafting introduction segments, refining the research scope (10–64 working-age population), or validating objectives (Spatial inequality, Driver quantification, EWS simulation).
- **02_lit_review.md**: Use for historical contextualization, theoretical background on the post-2024 functional literacy definition change (reading + writing + computing + comprehension), and spatial non-stationarity literature.
- **03_methodology_data.md**: Use for specifics on the 2024 FLEMMS survey datasets, sampling design (GeoMS, stratified two-stage cluster sampling), and missing data logic.
- **04_methodology_model.md**: Use for the predictive system formulas: PCA diagnostics (original draft selected 44 features by PCA loading; see the `_revised` file for XGBoost gain selection), XGBoost objective functions, Explainable AI framework constraints (SHAP, ALE, Friedman's H-statistic), and post-predictive spatial diagnostics (LISA/GWR).
- **01_introduction_revised.md**: Post-defense revised introduction rebalancing objectives to emphasize predictive EWS and LISA descriptive precursor.
- **04_methodology_model_revised.md**: Post-defense revised methodology incorporating Option C (PCA as diagnostic + XGBoost Gain feature selection), deep ALE vs. marginal effects contrast, Friedman's H contingency, and GWR removal.
- **CHANGELOG_POST_DEFENSE_REVISIONS.md**: Side-by-side comparison between original and revised chapters.