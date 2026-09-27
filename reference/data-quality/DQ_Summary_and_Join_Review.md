# DQ Issue Summary + Merge/Join Review

Companion to `Imputation_Crosscheck_Findings.md`. Two parts: (1) a flat list of every column with a data-quality issue and its disposition, (2) a review of `load_and_merge_flemms()`'s join logic.

## Part 1 — Column DQ issue summary

Legend: **Leakage** = must be excluded from modeling entirely. **Imputation-OK** = current `Not_Applicable` fill already matches verified skip logic, no code change needed. **Imputation-FIX** = current fill is present but wrong/inconsistent with skip logic or with the paper's own stated rule. **Unverified** = Form 3 source doc unavailable; treating as plausible-but-unconfirmed per your instruction. **Bug** = not an imputation question at all — a code defect.

| Column(s) | Issue type | Disposition |
|---|---|---|
| `BASIC_NUM` | **Bug (leakage)** | `identifiers` drop-list has `'NUMERACY'` (matches nothing) instead of `'BASIC_NUM'`. Fix the string so it's excluded like `BASIC_LIT` is. Didn't reach the final 44 features this run, but contaminated the PCA fit. |
| `READING`, `WRITING`, `COMPUTE`, `COMPRE`, `LLEVEL10OVER`, `LLEVEL5OVER`, `READING59`, `WRITING59`, `COMPUTE59`, `LLEVEL59`, `FLLEVEL`, `BLITERATE`, `BASIC_LIT`, `READ_IND_F2` | **Leakage — confirmed correct** | These are literally the Form 2A/2B/2C literacy-test output fields. Already dropped in `identifiers`. No further action. |
| `FLITERATE` | **Target, not a feature** | 28,127 missing = individuals with no Form 2 record at all (true unit nonresponse). Already handled correctly — Phase 2 drops rows via `.notna()` before training. No action needed. |
| `OF_PRESENT` | Imputation-OK | Gated by `OF`≠5. Current `Not_Applicable` fill correct. |
| `ATTEND_SCHOOL` | Imputation-OK | Gated to ages 3–30. Current fill correct (recommend a cross-tab sanity check against `AGE>30`). |
| `ATTEND_GRADE_LEVEL` | Imputation-OK | Gated on `ATTEND_SCHOOL` ∈ {1,2,3}. Current fill correct. |
| `MODETRVL1/2/3` | Imputation-OK (0 missing) | Codebook has a **native code 99=N/A** — PSA fills this itself, no pipeline action needed. |
| `NATT_REASON` | Imputation-OK (0 missing) | Gated on `ATTEND_SCHOOL`=4; already fully populated. |
| `DAYCARE` | Imputation-OK | Gated on `HGC_LEVEL` ≥ Kindergarten. Current fill correct. |
| `KINDER` | Imputation-OK | Gated on `HGC_LEVEL` ≥ Grade 1. Current fill correct. |
| `SHS` | Imputation-OK | Gated on age/grade eligibility for SHS. Current fill plausible. |
| `WORK` | Imputation-OK | Gated to ages 15+. Current fill correct (recommend cross-tab vs `AGE<15`). |
| `WORK_CLASS` | Imputation-OK | Gated on `WORK`=1. Codebook has no native N/A code here (per your own remark), so the constant fill is doing real work correctly. |
| `TOILET_LOC`, `TOILET_SHARE`, `TOILET_PUBLIC` | Imputation-OK | Cascading skip via `TOILET`(Q17)→`TOILET_SHARE`(Q19)→`TOILET_PUBLIC`(Q20). Current fill correct at every stage. |
| `ODL_SOFTWARE`, `ODL_TECHNOLOGY` | Imputation-OK | Gated on household-level ODL usage (Q22). Current fill correct. |
| `GUARDIAN` | Imputation-OK | Gated on `ADULTS`(Q3)=Yes. Current fill correct. |
| `CHILD_FACILITY` | Imputation-OK (0 missing) | Household-level, asked to all. No action. |
| `SHS_TRACK` | **Imputation — needs raw-data check** | Codebook has a **native code 4=N/A already baked in**. A *blank* cell is therefore a different phenomenon than routine skip (possibly the same unit-nonresponse pool below) — don't assume the blank↔skip equivalence holds here without checking `value_counts(dropna=False)`. |
| `ALS` | **Imputation — needs raw-data check** | Same issue as `SHS_TRACK`: native code 4=N/A exists. Contradicts your CSV remark ("blank means Not Applicable") — the two are likely different things. Verify before finalizing. |
| `NOWORK_REASON` | **Imputation — needs raw-data check** | Gated on `WORK`=2 (No), yet shows **0 missing**, which is suspicious if the gate is real — suggests PSA may already write a placeholder/sentinel code for workers, rather than leaving it blank. Check `value_counts(dropna=False)`. |
| `ADULTS` | **Imputation-FIX (recommendation)** | Your CSV remark proposes defaulting to code 2 ("No"). Recommend keeping `Not_Applicable` instead — collapsing a structural skip ("no children 0–4 exist") into a substantive answer ("no adult supervises them") asserts a fact you don't have. Also keeps consistency with the paper's single stated imputation rule (§3.2). |
| `HGC_LEVEL`, `ALS`, `BASIC_LIT`, `BASIC_NUM`, `DIFF_SEEING`, `DIFF_HEARING`, `DIFF_WALKING`, `DIFF_REMEMBERING`, `DIFF_SELFCARE`, `DIFF_COMMUNICATING` | **Imputation-FIX (mechanism mismatch)** | All share an identical 6,669 missing count with no age/eligibility gate that explains it in the 10–64 universe — most likely a single subgroup with no Form 1 individual-module record at all (unit nonresponse, e.g. unreachable OFWs), not skip logic. Recommend **not** defaulting `DIFF_*` to code 1 ("no difficulty") as your remark suggests — that fabricates a favorable value for people you know nothing about. Keep `Not_Applicable`/a distinct "Unknown" bucket, and flag the mechanism distinction in §3.2 rather than attributing all of it to skip logic. |
| `READ_IND_F3`, `INTERNET`, `SPORTS`, `MM_PNPAPER`…`MM_ECOMMERCE` (all mass-media items) | **Unverified** | Form 3 source doc unavailable. Plausible-but-unconfirmed: gated on literacy/reading ability. Proceeding with `Not_Applicable` as pragmatic default per your instruction. |
| `DSKILL_INFO1`…`DSKILL_PROB6` (all digital-skill items) | **Unverified** | Plausible-but-unconfirmed: gated on internet/ICT access (nested inside the above gate — higher missing count, 147,648). `Not_Applicable` as pragmatic default. |
| `TVOCGRAD`, `TVOCTRAIN`, `TVOCAT`, `TVOCCERT` | **Unverified** | Plausible TVET-module funnel gating (progressively stricter). `Not_Applicable` as pragmatic default. |
| `PATHWAY_COLLEGE`…`PATHWAY_OTHERS` | **Unverified** | Single shared gate (92,239 missing, identical across all 7). `Not_Applicable` as pragmatic default. |
| `MSPORT_FREQ`, `MSPORT_WHY`, `MSPORT_WHERE` | **Unverified** | Gated on `MSPORT` response. `Not_Applicable` as pragmatic default. |
| `HELPOTHERS`, `APPLYSKILLS` | **Unverified** | No clear internal pattern to infer gate from column names alone. `Not_Applicable` as pragmatic default, lowest confidence of the unverified group. |
| *(all categorical columns, cross-cutting)* | **Unconfirmed root-cause risk — worth a raw-data check** | Your original premise was that missing values are stored as literal empty strings (`''`) rather than `NaN`, which would silently bypass both `SimpleImputer` (Phase 1) and `.fillna()` (Phase 2) — `''` would survive as its own one-hot category instead of being folded into `'Not_Applicable'`. I can't confirm this without the raw CSVs. Recommend running, on any flagged column: `df['ALS'].apply(type).value_counts()` and `(df['ALS'] == '').sum()` vs `df['ALS'].isna().sum()` — if the empty-string count is nonzero, that confirms the bug and both imputers need `SimpleImputer(..., missing_values=np.nan)` widened to also treat `''` as missing (e.g. replace `''`→`np.nan` right after load, before the `astype('object')` step). |

## Part 2 — Join/merge review (`load_and_merge_flemms()`)

**Structure:**
```
df_member (person-level, base population)
  .merge(df_rtf1, on='HHID', how='left')            # household-level → broadcast to members
  .merge(df_rtf2, on=['HHID','LNO'], how='left')     # person-level literacy/target
  .merge(df_rtf3, on=['HHID','LNO'], how='left')     # person-level ICT
```

**What's correct:**
- Using `df_member` as the left-most/base table is the right call — it's the person-level roster, so every household member is preserved regardless of whether they have a Form 2/3 record (appropriately becomes `NaN` → later dropped via `FLITERATE.notna()` in Phase 2, not silently lost here).
- `RTF1` merging on `HHID` alone (not `HHID`+`LNO`) is correct *if* RTF1 is genuinely one row per household — it's a household-level questionnaire, so every member of that household should receive the same broadcast values. This is the right join grain **conceptually**, but its correctness depends on an assumption I can't verify without the data: that `HHID` is unique in `df_rtf1`.
- `RTF2`/`RTF3` merging on `HHID`+`LNO` is the right grain for person-level files, and renaming `LNO_F2`/`LNO_F3` → `LNO` before joining is a reasonable way to align Form 2/3's own line-number field with MEMBER's `LNO`, assuming PSA uses the same line-numbering convention across forms for the same household (standard practice, but also unverifiable from here).
- `remove_overlaps()` dropping `REG/PRV/MUN/BGY/URBANITY/REG2` before each merge avoids `_x`/`_y` suffix collisions — correct, and necessary since pandas would otherwise silently rename these to `REG_x`/`REG_y` etc. rather than error, which is a much harder bug to notice after the fact. One inconsistency worth a quick check: `overlap_cols` includes `MUN` and `BGY`, but neither name appeared in your earlier printed column list for the merged dataframe (`STRINGS`/`INTEGERS`/`FLOATS` dump) — suggesting the household PUF may not actually carry city/municipality or barangay identifiers (plausible, for anonymization). Harmless as written (`remove_overlaps` only drops columns `if c in df.columns`), just dead list entries, not a bug.
- Age filter (`10 ≤ AGE ≤ 64`) is applied once, after all merges complete — correct placement; filtering earlier on any individual source table would risk losing legitimate rows before the full join.

**What isn't verifiable without the data, and is exactly the kind of bug this join pattern is prone to — recommend adding a check:**

The code never asserts that row count is preserved after each left join. A left join with `how='left'` only preserves the left table's row count if the join key is **unique on the right-hand side**. If `RTF1` has more than one row per `HHID` (e.g., a duplicate/revisit record), or `RTF2`/`RTF3` have more than one row per `(HHID, LNO)`, the merge will silently fan out — every member in that household gets duplicated once per extra matching row, quietly inflating `df_merged` beyond `len(df_member)`. The notebook only prints the *final* shape after all three merges and the age filter, so a fan-out at any intermediate step would be invisible in the current output.

Recommend adding, right after loading and before merging:
```python
assert not df_rtf1['HHID'].duplicated().any(), "RTF1 has duplicate HHID rows — merge will fan out"
assert not df_rtf2.duplicated(subset=['HHID', 'LNO']).any(), "RTF2 has duplicate (HHID, LNO) rows — merge will fan out"
assert not df_rtf3.duplicated(subset=['HHID', 'LNO']).any(), "RTF3 has duplicate (HHID, LNO) rows — merge will fan out"
```
and/or printing `len(df_member)` immediately before the merge chain and comparing it to `len(df_merged)` immediately after (before the age filter) — they should be equal. This is a cheap, one-time check against the real data that would either confirm the joins are sound or catch a fan-out that's currently undetectable from the notebook's own output.

**Also worth a quick manual check (not a code change):** confirm merge-key dtypes match across the four CSVs (e.g. `HHID`/`LNO` all read as the same dtype — `int64` vs `object` mismatches, or inconsistent leading zeros, are a common way these joins silently drop matches without erroring). `df_member['HHID'].dtype == df_rtf1['HHID'].dtype` etc.

## Note on `CLAUDE.md`'s Phase 1/Phase 2 independence claim

While reviewing this I noticed the notebook's actual executed Phase 2 cell (`1c2667ee`) reuses Phase 1's in-memory `df` directly (`df_subset = df[base_cols_needed].copy()`) rather than re-merging from raw CSVs. There's an earlier Phase 2 attempt in the notebook (`dc1b08dd`) that *does* re-merge from raw CSVs independently, but it has a Python `IndentationError` and never executed — the `xgboost_*.csv` outputs you have were produced by the working `df`-reusing cell, not the independent-re-merge one. This contradicts `CLAUDE.md`'s current description ("Phase 2 reloads and re-derives everything Phase 1 computed... treat them as independently runnable"). Flagging in case you rely on running Phase 2 standalone in a fresh kernel — as currently written, it can't be; it needs Phase 1's `df` in memory first. Happy to fix `CLAUDE.md`'s description, or fix the notebook to make Phase 2 truly standalone (matching the broken cell's original intent) — your call on which one should change.
