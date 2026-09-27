# Action Plan: Post-Defense Edits to `STAT 299_ PROPOSAL_Compressed.md`

Source: panel feedback in `Comments_Proposal_Defense.md`. Line numbers below refer to the current `STAT 299_ PROPOSAL_Compressed.md`.

## Decision points

1. **RESOLVED — GWR: cut entirely.** Confirmed. LISA stays as the descriptive spatial layer; GWR (paragraph, formulas, and its orphaned Brunsdon et al. 1996 citation) is removed. See §3.6 in the edit map.
2. **RESOLVED — FIES: not present, disregard.** Confirmed FIES doesn't appear in this manuscript version (it was in an earlier draft), so there is nothing to cut here. The "income dynamics" / "regional economic shifts" phrasing in §1.1/Intro is **not** being treated as a FIES remnant — leave that wording alone unless a future pass finds an actual reason to touch it.
3. **OPEN — What is PCA *for*?** See the dedicated comparison below. This is the one still needing Sarah's/the adviser's call before §2.6, §3.3, §3.4 get edited.
4. **CONFIRMED — draft Comment 4 methodologically, don't cite a number yet.** `PCA_FLEMMS_streamlined.ipynb` doesn't compute an actual Friedman's H value (only SHAP importance + SHAP pairwise interactions are exported). Action item: add H-statistic computation to Phase 2 as a follow-up notebook task (tracked in "Suggested pass order" step 6); the manuscript's §2.5/§3.5 discussion of *what happens if H → 1* can and should be written now at the methodological level, marking the empirical value as pending rather than invented.

## Decision point 3 — PCA's role: three options compared

The current pipeline does something non-standard: PCA is fit on the 752-feature matrix, but **the final XGBoost model is never trained on the principal components themselves**. Component loadings are used only to rank and select 44 *original* named features, which then go into XGBoost untransformed. Below are the three ways to frame (or change) this, since Comments 3 and 5(ii) both hinge on picking one.

**Option A — Keep current mechanics, frame PCA purely as a feature-selection filter.**
- What changes: no notebook changes. Only the prose in §2.6/§3.3 changes, to state plainly that PCA's loadings are an unsupervised heuristic for narrowing 752 → 44 features, and that the components themselves are never modeled, explained, or presented as policy objects — only the named original features are.
- Upside: zero engineering cost; keeps full interpretability — every SHAP/ALE output stays in terms of a real, named survey variable ("Internet Access", not "PC7"), which matches the paper's own policy-facing pitch to DepEd/DOLE; consistent with why ALE was chosen over PDP in the first place (real, named axes with real units).
- Downside — the one the panel is actually probing: PCA loadings rank features by how much *variance* they explain in the feature space, not by how *predictive* they are of functional literacy. High-variance isn't guaranteed to mean high-relevance-to-target. The paper would need to explicitly own this as a limitation (it partially already does, in §1.3) rather than let it go unaddressed, since an unsupervised method is being used to pre-select inputs for a supervised task.

**Option B — Make PCA an actual data-transformation step (train XGBoost on the PC scores themselves).**
- What changes: Phase 2 would train on `X_pca` (already computed in Phase 1) instead of the one-hot 44-feature subset; SHAP/interaction exports would need to be reported per-component instead of per-named-feature.
- Upside: textbook-correct PCA usage — genuinely achieves dimensionality reduction and orthogonality/decorrelation, the classic justification for pre-processing with PCA. Statistically the cleanest story to defend on paper.
- Downside — this actively undercuts the paper's core premise. A SHAP value on "PC7" is meaningless to a policymaker without a second translation layer back through loadings, and that same translation burden reappears for ALE curves (an axis in unitless component-score space instead of "0–100% internet access") and for the H-statistic/interaction narrative (§2.4's "intersection of poor infrastructure and non-schooling" language assumes concrete, named features are what interacts — an abstract component-pair interaction is much harder to narrate the same way). Also the largest engineering lift of the three, and the riskiest to attempt this close to a defense-driven revision.

**Option C — Two-stage / hybrid: use PCA only for structural diagnostics, pick the modeling features some other way.**
- What changes: PCA is retained as an *exploratory* diagnostic (reporting redundancy/latent structure — this is actually where the current "Information Agency"-style language in §2.6 line 110 naturally belongs, as description, not as the selection mechanism), while the 44 modeling features are chosen via a method actually aligned with the target — e.g. a preliminary supervised importance pass (XGBoost gain/SHAP on the full 752, or mutual information with `FLITERATE`), possibly cross-validated against the PCA-loading list to report the overlap.
- Upside: most theoretically sound — separates "understand redundancy" (PCA's actual strength) from "predict the target" (a supervised method's strength) and directly answers the panel's "variance ≠ relevance" gap with evidence instead of an acknowledged limitation.
- Downside: real engineering cost (Phase 1→Phase 2 handoff needs rearchitecting) and schedule risk this late in the process. A cheaper partial version exists: keep Option A's mechanics as-is, but add a small validation step reporting the % overlap between the PCA-selected 44 and a supervised-importance ranking — this buys most of Option C's credibility without a full pipeline rewrite.

**Recommendation for the tradeoff, not a decision on your behalf:** Option A is the lowest-risk, lowest-effort path and is the only one of the three that doesn't fight the paper's own interpretability premise — but it should be paired with an explicit, honest limitation sentence (or the cheap cross-check from Option C) rather than silently leaving the variance-vs-relevance gap unaddressed, since that's precisely what two reviewers independently flagged.

## Edit map by comment

### Comment 1 — Cut GWR/FIES, rebalance objectives toward prediction/policy

- **Abstract (lines 7, 9):** LISA is already the only spatial method named here — no GWR/FIES mention, no change needed. Optionally soften "spatial analysis and interpretable machine learning" (line 7) to lead with the predictive framing first.
- **§1.1 Objectives (lines 27–29):** Objective 1 (spatial inequality) currently reads as co-equal with Objective 3 (EWS). Reframe Objective 1 as a *descriptive precursor* ("first establish where disparities are geographically concentrated using LISA") rather than a standalone spatial-econometrics contribution, and move Objective 3 (EWS/prediction/policy simulation) to the rhetorical center. "Income dynamics" (line 28) is left as-is per Decision Point 2 — not a FIES remnant, no action needed.
- **§1.2 Significance (lines 31–35):** No GWR/FIES here. No change needed.
- **§2.2 Spatial Econometrics (lines 60–64):** Keep — this is the LISA literature grounding, not GWR. No change.
- **§3.6 Spatial Aggregation and Simulation (lines 220–241):** This is the main surgical cut.
  - Delete the GWR paragraph and formulas (lines 227–239) entirely.
  - Rewrite the **Simulation** bullet (line 241) so "what-if" scenarios are run by perturbing input feature values and re-scoring the *XGBoost model directly* (consistent with an EWS/policy-simulation framing), not by varying GWR coefficients. This directly serves the "emphasize predictive and policy analysis" instruction.
  - Rename the section heading away from implying GWR is still "(Proposed)" — e.g., "3.6 Spatial Diagnostics and Scenario Simulation."
- **References (line 249):** Remove the Brunsdon, Fotheringham & Charlton (1996) GWR citation once the GWR paragraph is cut — it becomes orphaned.

### Comment 2 — Deepen the ALE explanation, contrast with marginal effects

- **§2.5 (lines 90–96):** Currently explains ALE vs. PDP correctly but never bridges to the econometrics reader's mental model. Add one paragraph after line 96 explicitly contrasting ALE with the "marginal effect, ceteris paribus" concept from linear regression: a linear model's coefficient *is* a constant marginal effect by construction; ALE instead estimates a *local, non-parametric* marginal effect that is allowed to vary across a feature's range and is computed only over realistic (conditional) data regions rather than assuming independence. This is the panel's specific ask — make the analogy and the departure from it explicit, not just the ALE-vs-PDP contrast already there.
- **§3.5 (line 218):** Currently a one-line bullet naming ALE with no explanation. Either point back to §2.5's expanded discussion or add a one-sentence restatement of what ALE outputs mean for a policymaker reading a curve (e.g., "shows how predicted illiteracy risk shifts as internet access moves from none to full, holding the local data distribution fixed").

### Comment 3 / 5(ii) — Pin down PCA's role

Depends on Decision Point 3 above (still open — Option A/B/C). Edits below assume Option A since it requires no notebook rework; revise this sub-section once a final choice is made:

- **§2.6 (lines 106–110):** Line 110 currently claims PCA extracts "latent dimensions... that represent broader concepts like 'Information Agency'" — this is the language that muddies PCA's role by implying the components themselves carry policy meaning. Reword to state PCA's loadings are used solely to *rank and select original features* for the supervised model; the components themselves are not carried forward as modeling inputs or policy objects.
- **§3.3 (lines 139–148):** Already technically correct (extracts top-5 loading features per top-10 component → 44 features) but never states *why* this design was chosen over just using the 539 components as model inputs. Add one sentence: features are kept in their original, named form (rather than as opaque PC scores) specifically so that Phase 2's SHAP/ALE outputs remain interpretable to policymakers — PCA is therefore a feature-selection filter, not a dimensionality-reduction step in the final model's input space.
- **§3.4 (line 150–152):** Line 150 already says "the refined feature set... serves as the input" — good, keep, just make sure it doesn't contradict the reworded §2.6/§3.3.

### Comment 4 — Friedman's H-statistic: what changes if H → 1

- **§2.5 (lines 98–104):** Definition is present and correct. Add 2–3 sentences after line 104 addressing the panel's actual question: if H-statistic values approach 1 for a given feature pair, single-feature SHAP/ALE rankings are no longer sufficient to explain risk — the paper should state it will pivot to reporting **joint/2D effect plots** for high-H pairs (e.g., a heatmap of predicted risk across the internet-access × schooling-status grid) and frame policy recommendations around the *combination* rather than either variable alone. If H stays low across pairs, state the paper will report that additive, single-feature interpretation is adequate and simpler policy narratives hold.
- **§3.5 (line 218):** Same one-line-bullet issue as ALE — expand slightly or point to §2.5.
- Note the results-dependency from Decision Point 4: this section can be drafted now as a conditional methodology; the *actual* H values and which pairs trigger the "joint effect" path can't be filled in until the notebook computes them.

### Comment 5(i) — Clean up the imputation methodology

- **§3.2 (lines 131–132):** The prose states only one rule ("missing values are imputed as 'Not Applicable'") plus a generic imputation formula placeholder, but the notebook (`preprocess_for_pca_memory_safe`, confirmed in `PCA_FLEMMS_streamlined.ipynb`) actually runs **two different imputers**: `SimpleImputer(strategy='median')` for numeric columns and `SimpleImputer(strategy='constant', fill_value='Not_Applicable')` for categorical columns. The manuscript needs to say both, not generalize the categorical case as if it covers everything.
- Fix: split line 131–132 into two explicit rules — (a) categorical/skip-logic missingness → constant 'Not Applicable' fill, justified by survey skip-logic as already argued; (b) numeric missingness (in practice just `AGE`, since nearly everything else is forced categorical per the notebook's `astype('object')` step) → median imputation, with a one-line justification (robust to outliers, minimal numeric columns affected). Replace or caption the single formula image so it isn't presented as if one equation covers both cases.
- Cross-check against `03_methodology_data.md` in this same `reference/` folder — it currently states only the categorical rule too, so it needs the identical fix to stay consistent with the main manuscript.

## Suggested pass order

1. **Settle Decision Point 3** (PCA framing — Option A/B/C) with Sarah/adviser input; the other three decisions are already resolved above.
2. **Structural cut pass:** remove GWR (§3.6, refs), rebalance Objective 1 vs. 3 emphasis (§1.1) — no FIES-specific rewording needed per Decision Point 2.
3. **Methods-precision pass:** fix imputation (§3.2, and mirror in `03_methodology_data.md`), fix PCA role language (§2.6, §3.3) once Decision Point 3 is settled.
4. **Theoretical-depth pass:** add the ALE-vs-marginal-effects paragraph (§2.5), add the H-statistic contingency discussion (§2.5), tighten the one-line bullets in §3.5 for both.
5. **Consistency read-through:** re-read Abstract → Objectives → Significance → Literature Review → Methodology in one pass to confirm no orphaned GWR/FIES/PCA-as-policy-object language remains, and that `context_map.md` / `01`–`04` chapter files (which still describe LISA **and** GWR as co-equal, per `04_methodology_model.md`) get the same GWR cut so the short-form chapter files don't contradict the full manuscript.
6. **Notebook follow-up (separate from this doc):** add Friedman's H-statistic computation to Phase 2 so Comment 4's discussion can eventually cite real values instead of a conditional-only treatment.

## Housekeeping noticed in passing

- `reference/New folder` is an empty directory (looks like a stray Windows Explorer artifact from the reorg) — flag for deletion, not removing without confirming it's not a placeholder for something you intended to add.
- The `01_introduction.md`–`04_methodology_model.md` chapter files were written *before* this feedback and still describe the pre-edit framing (equal-weight spatial objectives, GWR as an implemented layer). They'll need the same edits as the main manuscript once the decision points above are settled — treat them as a second, shorter application of this same plan, not a separate one.
