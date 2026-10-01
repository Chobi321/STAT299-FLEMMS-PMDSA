# STAT 299: A Spatial and Machine Learning Approach to Identifying High-Risk Functional Literacy Areas in the Philippines

This repository is the central workspace for a Master's thesis / capstone research project under the PMDSA (Professional Master in Data Science and Analytics) program. The study utilizes the Philippine Statistics Authority's **2024 FLEMMS** survey to build an Early Warning System (EWS) for functional illiteracy, combined with Explainable AI (XAI) for policy interpretation.

## Repository Structure

The project has two distinct halves:

1. **The Machine Learning & Data Pipeline**
2. **The Research Proposal & Manuscript**

---

## 1. The Machine Learning & Data Pipeline
The analysis is primarily driven by Jupyter notebooks. The pipeline recently transitioned to **Option C** (Supervised Feature Selection) based on panel defense feedback ("variance ≠ relevance").

* **`PCA_FLEMMS_streamlined.ipynb`**: The main end-to-end pipeline. 
  * **Phase 1**: Ingests, cleans, and encodes the raw survey data (752 features). Uses PCA as an exploratory diagnostic (95% variance) to check redundancy.
  * **Phase 1B**: Fits an XGBoost model on the 752 features to rank and select the top 44 features by predictive gain. 
  * **Phase 2**: Trains the predictive EWS XGBoost model using the 44 supervised features and outputs SHAP/ALE metrics.
* **`PCA_component_XGBoost_comparison.ipynb`**: A benchmark comparing XGBoost on PCA components versus original supervised features (proving they have equivalent predictive power, ROC-AUC gap is only -0.0112).
* **`data/`**: Expected to contain the raw FLEMMS 2024 PUF CSVs. *(Gitignored)*
* **Generated Artifacts**:
  * `phase1b_selected_features.csv` (Features used in the model)
  * `xgboost_shap_ale_impact.csv` (Policy impact directions)
  * `xgboost_shap_interactions.csv` (Pairwise feature effects)

---

## 2. The Research Proposal & Manuscript
The manuscript drafts, defense feedback, and revision plans are maintained under the `reference/` directory. 

* **`reference/proposal-manuscript/`**: The core proposal document is split into modular chapters to conserve context when editing:
  * `01_introduction.md`
  * `02_lit_review.md`
  * `03_methodology_data.md`
  * `04_methodology_model.md`
  * `context_map.md` (Index of topics across chapters)

### What is expected of us to edit?
Based on the faculty defense panel's feedback and our `reference/Action_Plan_Proposal_Edits.md`, the following structural edits are expected in the proposal documents:

1. **De-emphasize GWR (Geographically Weighted Regression):** GWR has been removed. The manuscript should re-balance its spatial objectives to focus purely on spatial inequality via LISA as a descriptive precursor, placing the primary focus on the predictive XGBoost model and policy analysis. *(Affects `01_introduction.md` and `04_methodology_model.md`)*
2. **Methodology Updates (Option C integration):** The methodology sections must be updated to clearly define **PCA's role** as an exploratory/diagnostic tool for variance and redundancy, while **XGBoost Gain** is the method used for feature selection. We need to explain why this was done (to prioritize relevance to the target over sheer variance). *(Affects `04_methodology_model.md`)*
3. **ALE vs. Marginal Effects:** Expand the explanation of Accumulated Local Effects (ALE) to contrast it explicitly with the "marginal effect, ceteris paribus" concept used in linear regression, as requested by the panel. *(Affects `04_methodology_model.md`)*
4. **Friedman's H-statistic Interpretation:** Add a theoretical discussion on what happens if the H-statistic approaches 1, indicating strong interaction effects (e.g., pivoting to joint 2D effect plots). *(Affects `04_methodology_model.md`)*
5. **Imputation Clarification:** Explicitly state the two different imputation rules being used (Median for numeric/age, Constant "Not Applicable" for categorical skip-logic). *(Affects `03_methodology_data.md`)*

## Research Writing Protocol
*(As previously defined in CLAUDE.md)*
- Maintain an academic, precise, and dense tone. 
- Never invent citations, DOIs, or data points. Use `[CITATION NEEDED]` or `[DATA MISSING]` if uncertain.
- Keep edits surgical—do not rewrite entire sections to fix one paragraph.
- Ensure the IMRaD structure is maintained, using the active voice.
