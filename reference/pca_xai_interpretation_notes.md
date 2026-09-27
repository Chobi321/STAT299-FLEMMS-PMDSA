# PCA, Supervised Selection, and XAI Interpretation Notes

## Purpose

This note records the current methodological interpretation of PCA, supervised XGBoost feature selection, and XAI for the FLEMMS functional-literacy study. It separates observed pipeline results from analyses that remain to be run.

## Observed Phase 1 and Phase 1B results

- The Phase 1 preprocessing produced 752 encoded predictor features after excluding identifiers, survey weights, and specified target-leakage variables.
- PCA fitted to a 95% variance threshold retained 539 principal components.
- The diagnostic Phase 1 shortlist consisted of 43 unique original features drawn from the largest loadings of the first ten PCA components. This shortlist does not itself retain 95% of the variance. The 539 PCA components do.
- Phase 1B selected 44 original features using XGBoost gain importance against `FLITERATE`.
- The PCA-derived and supervised lists shared 8 features. The reported overlap is 8/44, or 18%.

## Interpretation of the limited overlap

The limited overlap indicates that the variables contributing most strongly to broad variation in the survey data are not, in general, the same variables that best distinguish functional-literacy outcomes. This does not make PCA incorrect. PCA and supervised XGBoost answer different questions:

- PCA asks how the predictor space is structured and where variables carry overlapping information.
- Supervised XGBoost selection asks which predictors are useful for identifying functional-illiteracy risk.

The final predictive XGBoost plus SHAP and ALE pipeline should therefore use the supervised original-feature list. PCA remains an exploratory and diagnostic analysis rather than the final feature-selection gate.

## Practical contribution of PCA

PCA can contribute to the study in four ways:

1. It documents redundancy and correlation in the large FLEMMS predictor space.
2. It identifies whether many questionnaire indicators vary together as broader respondent or household patterns.
3. It provides a compact PCA-component representation for a predictive-signal comparison against the supervised original-feature model.
4. It provides context for interpreting correlated SHAP-important predictors as related conditions rather than fully independent policy levers.

PCA should not be presented as identifying causes of functional illiteracy, nor should a high-loading PCA feature automatically be described as an important risk factor.

## Clean PCA-component comparison

`PCA_component_XGBoost_comparison.ipynb` implements a held-out comparison between:

1. XGBoost trained on PCA component scores retaining 95% of training-set variance.
2. XGBoost trained on 44 original features selected by XGBoost gain using training rows only.

The notebook uses one stratified 80/20 split with `random_state=42`. It fits PCA and the supervised selector on the training partition only, applies the models to the held-out partition, and compares weighted ROC-AUC, PR-AUC, balanced accuracy, recall, precision, and F1.

Interpretation rule used in the notebook: an absolute ROC-AUC difference no larger than 0.02 is treated as practically comparable for this descriptive robustness check. This threshold is a reporting convention, not a formal equivalence test.

### Observed comparison result

The completed run retained 533 PCA components, representing 95.05% of training-set variance. On the weighted held-out test partition, the PCA-component model achieved ROC-AUC 0.7132 and the supervised 44-original-feature model achieved ROC-AUC 0.7020. The supervised-minus-PCA ROC-AUC gap was -0.0112, which is within the predeclared plus or minus 0.02 practical-comparability threshold.

This result suggests that the 95%-variance PCA representation retained comparable predictive signal in this split. It does not make PCA components the preferred policy-facing explanation: the supervised original-feature model remains substantially easier to explain with SHAP and ALE.

For future runs, a materially lower PCA-component performance would instead suggest that variance-preserving compression does not retain all variation relevant to functional-literacy classification. That outcome would support retaining supervised original features for the policy-facing model.

## Proposed PCA-supported XAI interpretation

The primary XAI results should remain feature-level SHAP values, ALE curves, and SHAP interaction values because they can be expressed in the original survey variables. PCA can add a secondary domain-level interpretation:

1. Identify the high-SHAP original features.
2. Examine each feature's absolute loadings on the early, substantively interpretable PCA components.
3. Where several high-SHAP features load strongly on the same component, describe them as a broader empirical domain, subject to the cautions below.
4. Use that domain to contextualize the individual SHAP and ALE findings. Do not replace the individual findings with a component label.

Example reporting logic: if multiple SHAP-important education variables load strongly on a component characterized by education-related indicators, the results may be discussed as a coherent education-related risk profile. The component describes co-occurring variation; the SHAP and ALE results describe model associations with predicted risk.

## Assumptions and cautions

### PCA interpretation

- PCA is unsupervised. Components capture variance, not functional-literacy relevance, causality, or policy priority.
- A principal component is a weighted combination of encoded variables. It is not an observed real-world construct unless its loading pattern is coherent and substantively defensible.
- The sign of a PCA component is arbitrary. Interpret the variables with large positive and negative loadings together, not the component sign alone.
- A feature may load meaningfully on multiple components. Do not force every SHAP-important feature into one domain.
- Only early components with clear, stable loading patterns should receive substantive labels. The 539 components retained for 95% variance should not all be named or interpreted as latent profiles.
- The 43-feature diagnostic shortlist from the first ten components is a loading heuristic. It must not be described as the set that preserves 95% of variance.

### Predictive-model and XAI interpretation

- SHAP values explain the fitted model's predictions. They do not establish causal effects, interventions, or independent real-world mechanisms.
- Correlated features can share or shift SHAP attribution. A lower SHAP rank does not prove that a correlated variable is unimportant in substantive terms.
- ALE is preferred to partial dependence plots for main effect shapes because correlated survey features can make partial-dependence scenarios unrealistic. ALE still describes model behavior, not causality.
- SHAP interaction values should be interpreted as model-detected joint predictive patterns, not evidence of causal interaction.
- The decision threshold, class weighting, and survey weights affect classification metrics and must be reported with the results.

### Evaluation design

- The existing Phase 1B feature list was produced using all valid rows. It is suitable for the current Phase 2 workflow, but using that full-data list before evaluating on the same held-out test set can make performance estimates optimistic.
- For the PCA-component comparison, PCA fitting and supervised feature selection occur within training data only. This avoids test-set information influencing the comparison.
- The preprocessing already used in Phase 1 is retained for consistency with the existing pipeline. A fully nested validation design would also fit imputation, encoding, and scaling within the training partition; this can be considered for a later robustness extension.
- Survey weights are used for model fitting and held-out metric calculation in the comparison notebook. This supports population-representative weighting, but it does not by itself implement a full complex-survey variance analysis.

## Recommended manuscript framing

Use PCA as an exploratory description of the predictor space and as a robustness comparison, not as the study's main policy-facing explanatory method. The applied chain is:

> PCA characterizes correlated and redundant predictor structure. Supervised XGBoost identifies outcome-relevant predictors. SHAP identifies influential model features, ALE describes fitted effect shapes, and SHAP interactions identify joint predictive patterns.

Avoid claiming that PCA discovers definitive latent profiles or that SHAP identifies causes of functional illiteracy.
