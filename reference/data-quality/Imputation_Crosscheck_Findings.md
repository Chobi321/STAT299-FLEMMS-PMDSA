# Imputation Cross-Check: FLEMMS Missing-Value Columns vs. Survey Skip Logic

Source: `STAT299_FLEMMS_MISSING_COLUMNS_ONEHOT_ENCODED.csv` (user's flagged columns + remarks), cross-checked against `reference/flemms-survey-questions/2024 FLEMMS FORM 1_Household Questionnaire.pdf` and Forms 2A/2B/2C.

## Before the column-by-column list: two things that aren't imputation issues but were found while cross-checking

### Finding 1 — Forms 2A/2B/2C are NOT the socioeconomic questionnaire

Each of Forms 2A (5–9yo), 2B (65+), 2C (10–64yo) is a **3-page literacy test instrument only** — Q1 "Reading Indicator" gate, then the actual reading/numeracy/functional-literacy test items. This is where `READING`, `WRITING`, `COMPUTE`, `COMPRE`, `LLEVEL*`, `FLLEVEL`, `BLITERATE`, `FLITERATE`, `READ_IND_F2` come from — confirming the user's "leakage" tags on these are correct; they are literally the test whose outcome is the target.

The demographic/education/work/disability/ICT/housing questions (everything else on the missing-columns list) live in **Form 1 (Household Questionnaire)**, which is what the skip-logic citations below are drawn from.

**Gap: there is no "Form 3" PDF in `reference/flemms-survey-questions/`.** Per `CLAUDE.md`, `RTF3` is the "ICT/Digital" file, but Form 1 only covers ICT at the *household* level (assets/subscriptions, §8–9) and ODL (§11). It does **not** contain `DSKILL_*`, `MM_*`, `INTERNET`, `READ_IND_F3`, `TVOC*`, `PATHWAY_*`, `SPORTS`/`MSPORT*`, `HELPOTHERS`, `APPLYSKILLS`. These ~45 columns belong to a separate individual-level ICT/Mass-Media/TVET/Sports questionnaire that isn't in this repo. I cannot verify their skip logic from source — see the "Unverified" section below rather than treat my inferences there as confirmed.

### Finding 2 — `BASIC_NUM` is not actually excluded as leakage (typo bug)

In `preprocess_for_pca_memory_safe`'s `identifiers` drop list (`PCA_FLEMMS_streamlined.ipynb`, cell `71dd0a43`):

```python
'NUMERACY', 'BASIC_LIT', 'BLITERATE', 'BLITERATE_1', 'BLITERATE_2',
```

The real column is `BASIC_NUM`, not `NUMERACY` — `NUMERACY` matches nothing in the merged dataframe, so `BASIC_NUM` (the household proxy-reported "can perform basic math" item, Form 1 Col. 18) survives into the 752-feature PCA space untouched, while its sibling `BASIC_LIT` (Col. 17) is correctly dropped. I checked `phase1_selected_features.csv` and all three `xgboost_*.csv` outputs — `BASIC_NUM` did not get selected into the final 44 or appear in any importance ranking in this run, so it hasn't visibly corrupted the reported results. It did, however, feed the PCA fit (all 752 one-hot columns → the 539 components), which can shift *which other* features get pulled into the top-5-per-component. Recommend fixing `'NUMERACY'` → `'BASIC_NUM'` regardless, for correctness independent of whether it happened to matter this run.

---

## Part A — Verified against Form 1 (confident recommendations)

| Column | Form 1 location | Skip logic (verbatim/paraphrased) | Recommended imputation | Notes |
|---|---|---|---|---|
| `OF_PRESENT` | §2, Col. 10A | Asked only if `OF` (Col. 10) ∈ {1,2,3,4} (some OF status); if `OF`=5 (No, resident) → "GO TO COL 12", skipping this item entirely | **`Not_Applicable`** (current pipeline is already correct) | Missing count (489,189) ≈ non-OF share of sample; consistent. |
| `ATTEND_SCHOOL` | §2–3, Col. 12 | Only asked to ages 3–30 (or OF present at time of visit); outside that age band it's never asked | **`Not_Applicable`** (already correct) | Recommend a sanity check: cross-tab missingness against `AGE>30` to confirm the count lines up. |
| `ATTEND_GRADE_LEVEL` | Col. 13 | Only asked if `ATTEND_SCHOOL` ∈ {1,2,3}; if `ATTEND_SCHOOL`=4 (No) → "GO TO COL 16" | **`Not_Applicable`** (already correct — matches user's own remark) | |
| `NATT_REASON` | Col. 16 | Asked only if `ATTEND_SCHOOL`=4 (No) | 0 missing in your file — no action needed | |
| `HGC_LEVEL` | Col. 20 | Shares the same Level 0–8 code table as Col. 13 ("Codes for Columns 13 & 20"); asked to all 5+ | See "the 6669 pattern" below — **do not treat as simple skip** | |
| `DAYCARE` | Col. 21 | Header: "For those who attended at least Kindergarten" — i.e., gated on `HGC_LEVEL` ≥ Kindergarten | **`Not_Applicable`** (already correct) if `HGC_LEVEL` < Kindergarten | |
| `KINDER` | Col. 22 | Header: "For those who attended at least Grade 1" — gated on `HGC_LEVEL` ≥ Grade 1 | **`Not_Applicable`** (already correct) | |
| `SHS` | Col. 23 | "Did ___ complete Senior High School?" 1–3=Yes variants, 4="NO, GO TO COL 26" | **`Not_Applicable`** for those who never reached SHS eligibility (age/grade-gated) — plausible as-is | |
| `SHS_TRACK` | Col. 24/25 | Codes list explicitly includes **native code 4 = "N/A"** in the codebook itself (not blank) | ⚠️ See "native N/A codes" note below — blank ≠ skip here, it may mean something else (raw-data verification needed) | |
| `ALS` | — | Codes are **1-Yes,Public / 2-Yes,Private / 3-No / 4-N/A** — again a **native N/A code already exists** | ⚠️ Do not assume blank = "this means Not Applicable" (contradicts the CSV's remarks2). If PSA already writes `4` for genuine non-applicability, a *blank* cell is a different phenomenon — likely the same subgroup as the "6669 pattern" below (unit nonresponse), not skip logic. Recommend verifying via `df['ALS'].value_counts(dropna=False)` — if `4` appears as a real value alongside NaN, that confirms it. | |
| `WORK` | Col. 28 | Employment module gated to "15 YEARS OLD & OVER" | **`Not_Applicable`** for ages 10–14 (already correct) | Recommend cross-tab against `AGE<15` to confirm 73,819 lines up. |
| `WORK_CLASS` | Col. 30 | Asked only if `WORK`=1 (Yes) | **`Not_Applicable`** (already correct — codebook has no native N/A code here, per user's own remark, so blank-fill genuinely represents the skip) | |
| `NOWORK_REASON` | Col. 31 | Asked only if `WORK`=2 (No) | 0 missing in your file is suspicious — if gated correctly, most workers (WORK=1) should show blank here. Recommend checking whether PSA already encodes a sentinel/placeholder value for this column in the raw CSV rather than true missingness. | |
| `MODETRVL1/2/3` | Col. 14 | Only relevant if attending school; **codebook has a native code `99 = N/A`** | 0 missing in your file — consistent with PSA using its own native `99` code rather than blank for non-applicability, so no imputation action needed | |
| `ADULTS` | §6, Q3 | Asked only if Q2 (`CHILDREN_04`, are there children 0–4) = Yes; if No → "Go to Q5" | **Recommend `Not_Applicable`, not the CSV's suggested "Default to 2/No."** The question presupposes children 0–4 exist; collapsing a structural skip into a substantive "No" answer conflates "no children to supervise" with "children exist but nobody supervises them," which are different facts. Keeping `Not_Applicable` is also consistent with the paper's single stated imputation rule (§3.2). | |
| `GUARDIAN` | §6, Q4 | Asked only if Q3 (`ADULTS`)=Yes | **`Not_Applicable`** (already correct) | |
| `CHILD_FACILITY` | §6, Q5 | Asked to all households (barangay-level, not gated) | 0 missing — no action needed | |
| `TOILET_LOC` | §10, Q18 | Skipped ("Go to Q21") if Q17 (`TOILET`) = 71 (public) or 95 (no facility) | **`Not_Applicable`** (already correct) | |
| `TOILET_SHARE` | §10, Q19 | Same skip condition as Q18 | **`Not_Applicable`** (already correct) | |
| `TOILET_PUBLIC` | §10, Q20 | Asked only if Q19 (`TOILET_SHARE`)=Yes | **`Not_Applicable`** (already correct) | |
| `ODL_SOFTWARE` | §11, Q23 | Asked only if Q22 (`ODL_FAM`... actually Q22 is a household-level ODL-usage Yes/No) = Yes; if No → "End interview for FLEMMS Form 1" | **`Not_Applicable`** (already correct) | |
| `ODL_TECHNOLOGY` | §11, Q24 | Same gate as Q23 | **`Not_Applicable`** (already correct) | |

## The "6669 pattern" — a distinct missingness mechanism, not skip logic

`BASIC_LIT`, `BASIC_NUM`, `HGC_LEVEL`, `ALS`, `DIFF_SEEING`, `DIFF_HEARING`, `DIFF_WALKING`, `DIFF_REMEMBERING`, `DIFF_SELFCARE`, `DIFF_COMMUNICATING` all show **exactly 6,669 missing** — too precise a coincidence to be six independent skip patterns. All of these questions are asked to "5 years old and over" with **no age/eligibility gate that would exclude anyone in your 10–64 universe**, and (per the note above) some of them — `ALS`, and by the codebook's own SHS_TRACK precedent — already have **native N/A codes**, meaning routine skip logic shouldn't produce blank cells here at all.

The most likely explanation: 6,669 is the count of MEMBER-roster individuals aged 10–64 who have **no corresponding Form 1 individual-module record at all** — e.g., someone listed as a household member but never actually reached for the detailed interview (common for OFWs abroad, or partial-completion households). This is **genuine item/unit nonresponse**, not "the question didn't apply to them."

This matters for the manuscript, not just the code: §3.2 currently justifies the blanket `'Not_Applicable'` fill on **survey skip-logic** grounds. That justification is correct for most columns in Part A, but doesn't hold for this subgroup — there the honest description is "missing data of unknown mechanism," not "structurally inapplicable." Two options:
1. Keep the single `'Not_Applicable'` constant-fill for simplicity, but add a limitation sentence acknowledging that a subset of missingness (the ~6,669-row group) is item nonresponse rather than skip logic, and that both are pooled into one placeholder category.
2. Recommend against the CSV's own remark ("Default to 1 — Maybe respondents have no difficulty whatsoever?") for the `DIFF_*` columns specifically: imputing "no difficulty" (a substantive, favorable value) onto a subgroup that's disproportionately likely to be OFWs or hard-to-reach households risks quietly biasing the disability-related features toward "no difficulty," which could matter if any `DIFF_*` column reaches the final 44. Recommend leaving these as `Not_Applicable`/a distinct "Unknown" category rather than defaulting to code 1.

**Actionable next step you can run against the real data** (not possible here — `data/` is gitignored/local-only): `df[df['ALS'].isna()][['OF','OF_PRESENT','RESULT_CODE_F1' if present]]` or similar, to confirm whether the 6,669-row group correlates with OF/absentee status.

## Part B — Cannot verify (Form 3 questionnaire not in repo)

These columns share a missing-count of either **27,784** or **147,648** — internally consistent with each other (suggesting two nested eligibility gates within Form 3: a base eligibility filter, then a stricter "digital skills" sub-gate), but I cannot cite exact question wording/skip arrows without the source PDF:

- `READ_IND_F3`, `MM_PNPAPER` … `MM_ECOMMERCE` (all mass-media items), `INTERNET` — 27,784 missing
- `DSKILL_INFO1` … `DSKILL_PROB6` (all digital-skill items) — 147,648 missing
- `TVOCGRAD`, `TVOCTRAIN` (362,978), `TVOCAT` (490,225), `TVOCCERT` (491,479)
- `PATHWAY_COLLEGE` … `PATHWAY_OTHERS` (92,239, all identical — one shared gate)
- `SPORTS` (27,784 — same base group as mass media), `MSPORT_FREQ/WHY/WHERE` (406,868)
- `HELPOTHERS` (269,607), `APPLYSKILLS` (440,694)

The CSV's own remarks2 reasoning ("these respondents cannot read at all... may not apply to them" for the mass-media block; "these people do not have the opportunity to exercise digital skills" for `DSKILL_*`) is plausible and matches how FLEMMS is typically structured (mass-media/ICT modules gated on literacy/internet-use), but **I'm not willing to confirm imputation values against a document I haven't read**. Recommend either:
- Supplying the actual "Form 3" ICT/Digital Skills/Mass Media/TVET questionnaire PDF (if you have it) so I can do the same verbatim skip-logic citation as Part A, or
- Explicitly marking these ~45 columns' imputation as "plausible, unverified" in the manuscript/methodology write-up (per the project's own rule of flagging rather than inventing), and using `Not_Applicable` as a pragmatic default consistent with the rest of the pipeline.

## Summary of code changes implied (not yet made)

1. Fix `'NUMERACY'` → `'BASIC_NUM'` in the `identifiers` list (`preprocess_for_pca_memory_safe`) so it's actually excluded as leakage, matching `BASIC_LIT`'s treatment.
2. No change needed for the majority of Part A columns — the existing single `'Not_Applicable'` constant-fill happens to already match the skip logic for most of them.
3. Consider *not* changing `ADULTS`/`DIFF_*` per the CSV's tentative remarks (default-to-substantive-code) — recommend keeping `Not_Applicable`, for the reasons above.
4. §3.2 / `03_methodology_data.md` prose (per `Action_Plan_Proposal_Edits.md` Comment 5(i)) should distinguish "skip-logic non-applicability" from "the 6,669-row unit-nonresponse pattern" rather than attribute all missingness to skip logic.
