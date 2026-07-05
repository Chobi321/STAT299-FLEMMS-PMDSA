# 04. Methodology: Architecture, Modeling, & XAI

- **Phase 1: Dimensionality Reduction (PCA):**
  - Manages initial 752 features post-encoding. A 95% variance threshold initially isolated 539 components.
  - To maintain policy interpretability, the top 10 principal components are isolated, extracting the top 5 highest loading features per component to achieve a refined subset of 44 key features.
- **Phase 2: Predictive Modeling (XGBoost):**
  - Supervised binary classifier: Target variable binarized (0 = Literate, 1 = Illiterate).
  - Evaluated on an 80/20 stratified train-test split. Uses second-order Taylor expansion to optimize log-loss objective function with added tree complexity regularizations ($\Omega$).
  - Addresses minority class imbalance (~30% illiterate base) via the `scale_pos_weight` hyperparameter.
- **Phase 3: Explainable AI (XAI) Stack:**
  - *SHAP:* Captures local feature attribution magnitude and direction.
  - *Accumulated Local Effects (ALE):* Isolates marginal effects over conditional distributions, replacing biased Partial Dependence Plots (PDP) that fail due to highly correlated variables (e.g., Urbanization vs Internet Access).
  - *Friedman’s H-statistic:* Quantifies multi-dimensional variable interactions (e.g., cross-sections of poor infrastructure and non-schooling factors).
- **Phase 4: Spatial Diagnostic Layer:**
  - Aggregates individual risk probabilities into provincial levels to run Local Indicators of Spatial Association (LISA) to detect High-High and Low-Low clusters. Uses Geographically Weighted Regression (GWR) to capture localized parameter variations and simulate target interventions (e.g., "What-if" 10% internet access shifts).