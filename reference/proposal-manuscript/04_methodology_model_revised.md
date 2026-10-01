# 04. Methodology: Architecture, Modeling, & XAI (Revised)

> **Context / Changelog Note:**
> Revised in response to panel defense feedback (Comments 1, 2, 3, 4, 5 in `Comments_Proposal_Defense.md`) and the recent adviser alignment:
> 1. **Option C Implementation:** Clarifies PCA as an unsupervised exploratory/diagnostic tool for variance and redundancy, while establishing XGBoost Gain as the supervised feature selection mechanism.
> 2. **Deepened ALE Framework:** Contrasts ALE with classical econometrics "marginal effects, ceteris paribus".
> 3. **Friedman's H-statistic Contingency:** Outlines analytical pivot to 2D joint effect surfaces if $H \to 1$.
> 4. **Spatial Layer Precision:** Removes Geographically Weighted Regression (GWR); re-anchors simulation directly on XGBoost input perturbation.

---

### Phase 1: Exploratory Dimensionality Analysis (Diagnostic PCA)
- **High-Dimensional Feature Space:** Manages 752 one-hot encoded predictor features post-cleaning, excluding administrative identifiers, survey weights, and Form 2 target leakage variables.
- **Unsupervised Variance Characterization:** PCA is applied to evaluate structural collinearity and redundancy in the survey space. A 95% cumulative Explained Variance Ratio (EVR) threshold retains 539 principal components.
- **Diagnostic Role (Not Selection):** The top 10 principal components are inspected for loading patterns to document broader respondent profiles (e.g., educational backgrounds, household asset blocks). Crucially, PCA loadings are **not** used to filter the predictive model inputs because unsupervised variance does not imply target relevance.

### Phase 1B: Supervised Feature Selection (XGBoost Gain)
- **Target-Aligned Selection:** To prioritize features directly associated with functional illiteracy (`FLITERATE`), an initial `XGBClassifier` is trained across all 752 encoded features using survey design weights (`RESP_RFACT_F2`) and class weights (`scale_pos_weight`).
- **Ranking by Gain Importance:** The top 44 features exhibiting the highest training gain are extracted as the final predictor subset (`phase1b_selected_features.csv`).
- **Empirical Variance vs. Relevance Check:** Comparing the 44 PCA-highest-loading features against the 44 supervised gain features reveals an empirical overlap of only **8/44 (18%)**, empirically justifying the decision to decouple variance exploration (PCA) from risk prediction (XGBoost).

### Phase 2: Predictive Modeling (Early Warning System via XGBoost)
- **Supervised Classifier:** Predicts binary functional literacy ($0 = \text{Literate}$, $1 = \text{Illiterate}$) using the 44 selected original survey features. Keeping original features preserves direct policy interpretability.
- **Evaluation Design:** 80/20 stratified train-test split (`random_state=42`).
- **Survey & Imbalance Weighting:** Incorporates `scale_pos_weight` to counteract the class imbalance (~30% illiterate base) alongside sample weights (`RESP_RFACT_F2`) to reflect true national population representation.
- **Optimization:** Optimizes regularized log-loss objective via second-order Taylor expansion (gradients and Hessians), regularized by tree complexity penalty $\Omega(f) = \gamma T + \frac{1}{2}\lambda \sum w_j^2$. Primary evaluation metrics focus on weighted ROC-AUC and PR-AUC.

### Phase 3: Explainable AI (XAI) Stack
- **SHAP (Shapley Additive Explanations):** Computes tree-based local attributions to measure the magnitude and sign of each feature's contribution to predicted illiteracy risk.
- **Accumulated Local Effects (ALE):**
  - Evaluates main effect shapes over conditional feature distributions.
  - *Contrast with Linear Marginal Effects:* In a classical linear regression framework, a coefficient represents a constant marginal effect ($\frac{\partial Y}{\partial X_j}$), evaluated *ceteris paribus* (holding all other variables constant). In observational survey data with correlated features (e.g., age, school attendance, internet access), the *ceteris paribus* assumption creates unrealistic counterfactuals. ALE overcomes this by calculating local, non-parametric differences across conditional intervals, describing how risk shifts locally without extrapolating outside the joint data distribution.
- **Friedman’s H-Statistic & Second-Order Interactions:**
  - Measures the strength of pairwise non-linear feature interactions ($0 \le H \le 1$).
  - *Analytical Contingency ($H \to 1$):* If $H$ approaches 1 for a feature pair (e.g., school attendance $\times$ age), it signifies that the risk effect cannot be explained by single-feature SHAP or ALE curves alone. Under high-$H$ conditions, the analysis pivots to generating **two-dimensional joint ALE response heatmaps**, formulating policy recommendations around combined interventions rather than isolated levers.

### Phase 4: Spatial Diagnostic Layer & Policy Scenario Simulation
- **Provincial Aggregation:** Individual predicted illiteracy probabilities are aggregated to provincial and HUC levels using survey population expansion weights.
- **Spatial Autocorrelation (LISA):** Computes Local Moran's $I$ to identify statistically significant clusters: High-High (spatial poverty/illiteracy traps), Low-Low (literacy clusters), and spatial outliers (High-Low, Low-High).
- **Policy Intervention Simulation:** *GWR is removed.* Scenario simulations are instead executed directly through the trained XGBoost model by perturbing specific input variables across target populations (e.g., simulating a 10% increase in digital literacy or internet access in high-risk provinces) and measuring the resulting reduction in predicted illiteracy risk.
