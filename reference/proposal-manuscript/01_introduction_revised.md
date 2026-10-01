# 01. Introduction, Objectives, & Scope (Revised)

> **Context / Changelog Note:**
> Revised in response to panel defense feedback (Comment 1 in `Comments_Proposal_Defense.md`).
> Rebalanced objectives: Objective 1 (spatial analysis) is reframed as a *descriptive precursor* using LISA, placing Objective 3 (Predictive Early Warning System & Policy Simulation) at the methodological and rhetorical center.

- **Title:** A Spatial and Machine Learning Approach to Identifying High-Risk Functional Literacy Areas in the Philippines
- **Problem Statement:** Broad national metrics mask localized literacy vulnerabilities. 2024 FLEMMS reveals a significant divergence: while basic literacy exceeds ~90%, functional literacy (requiring comprehension, writing, and numeracy) stands at only 70.8%, creating an estimated 19-million citizen "labor force lag". This vulnerability is driven by an intertwined socio-technical ecosystem: digital divide disparities (e.g., San Juan City at 94.5% vs. remote provinces) and intergenerational education barriers.
- **Objectives:**
  1. *Descriptive Spatial Precursor:* Establish where functional literacy disparities are geographically concentrated across Philippine provinces and Highly Urbanized Cities (HUCs) using Local Indicators of Spatial Association (LISA).
  2. *Predictive Early Warning System (Primary Objective):* Develop an Extreme Gradient Boosting (XGBoost) classifier parameterized with official survey weights to accurately predict individual and localized functional illiteracy risk among the working-age population.
  3. *Driver Quantification & Scenario Simulation:* Quantify key individual, household, and digital infrastructure drivers using an Explainable AI (XAI) stack (SHAP, ALE, and Friedman's H-statistic), and simulate policy interventions directly through the trained predictive model.
- **Scope & Limitations:**
  - **Population Universe:** Individuals aged 10 to 64 years old, aligned with PSA FLEMMS Form 2 (Literacy) and Form 3 (Individual ICT).
  - **Sample Size:** Microdata covering approximately 496,770 observations, weighted using official survey replicate/design weights (`RESP_RFACT_F2`) for national population representation.
  - **Proxy Constraints:** FLEMMS does not contain direct household income values. Asset ownership, utility access, and housing construction materials serve as socioeconomic proxies.
