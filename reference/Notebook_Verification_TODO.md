# Notebook Verification TODO

Things to actually run against the real data (in `data/`, not available in this checkout) before finalizing the imputation/leakage fixes from `Imputation_Crosscheck_Findings.md` and `DQ_Summary_and_Join_Review.md`. Nothing here has been executed yet — these are checks to run, not confirmed conclusions.

## 1. Join/merge fan-out check (`load_and_merge_flemms()`)

The merge chain (`df_member` → `+RTF1` on `HHID` → `+RTF2` on `HHID,LNO` → `+RTF3` on `HHID,LNO`) is only safe if each right-hand table has a unique key. The notebook currently only prints the final post-filter shape, so a fan-out at any intermediate step would be invisible. Run before merging:

```python
assert not df_rtf1['HHID'].duplicated().any(), "RTF1 has duplicate HHID rows — merge will fan out"
assert not df_rtf2.duplicated(subset=['HHID', 'LNO']).any(), "RTF2 has duplicate (HHID, LNO) rows — merge will fan out"
assert not df_rtf3.duplicated(subset=['HHID', 'LNO']).any(), "RTF3 has duplicate (HHID, LNO) rows — merge will fan out"
```

And compare row counts across the chain (should stay flat until the age filter):
```python
print(len(df_member))                              # baseline
df_merged = df_member.merge(df_rtf1, on='HHID', how='left')
print(len(df_merged))                               # should equal df_member
df_merged = df_merged.merge(df_rtf2, on=['HHID','LNO'], how='left')
print(len(df_merged))                               # should still equal df_member
df_merged = df_merged.merge(df_rtf3, on=['HHID','LNO'], how='left')
print(len(df_merged))                               # should still equal df_member
```

Also sanity-check merge-key dtypes match across files before joining (a silent dtype mismatch, e.g. `int64` vs `object`/leading-zero strings, drops matches without erroring):
```python
df_member['HHID'].dtype, df_rtf1['HHID'].dtype, df_rtf2['HHID'].dtype, df_rtf3['HHID'].dtype
df_member['LNO'].dtype, df_rtf2['LNO'].dtype, df_rtf3['LNO'].dtype
```

## 2. Blank-vs-NaN encoding check (root cause of the original imputation concern)

Confirm whether "missing" categorical values are real `NaN` (correctly caught by `SimpleImputer`/`.fillna()`) or literal empty strings / whitespace tokens (which silently survive as their own one-hot category instead of folding into `'Not_Applicable'`). Run on a few flagged columns, e.g. `ALS`, `DIFF_SEEING`, `SHS_TRACK`:
```python
df['ALS'].apply(type).value_counts()
(df['ALS'] == '').sum(), df['ALS'].isna().sum()
```
If the empty-string count is nonzero, both imputers need missing values normalized to `np.nan` right after load (before the `astype('object')` step), e.g. `df.replace('', np.nan, inplace=True)` (or per-column, if only some columns use blanks vs. other sentinel tokens).

## 3. Native N/A codes vs. genuine skip — columns needing `value_counts(dropna=False)`

`SHS_TRACK` and `ALS` both have a codebook-native "N/A" code already (`4`). Confirm whether that code actually appears in the raw data alongside real `NaN`s — if so, blank cells are a *different* phenomenon than routine skip logic (see the "6669 pattern" in `Imputation_Crosscheck_Findings.md`) and shouldn't be assumed equivalent to it:
```python
df['SHS_TRACK'].value_counts(dropna=False)
df['ALS'].value_counts(dropna=False)
df['NOWORK_REASON'].value_counts(dropna=False)   # 0 missing despite being gated on WORK=2 — check for a placeholder code
```

## 4. The "6669 pattern" subgroup

Confirm whether the ~6,669 rows missing `BASIC_LIT`/`BASIC_NUM`/`HGC_LEVEL`/`ALS`/all six `DIFF_*` columns are the same rows across all of them (supporting the "single unit-nonresponse subgroup" theory), and whether that subgroup correlates with OF/absentee status:
```python
mask = df['ALS'].isna()
df.loc[mask, ['OF', 'OF_PRESENT']].value_counts(dropna=False)
# also confirm it's the same ~6669 rows across columns, not coincidentally-equal but different sets:
(df['BASIC_LIT'].isna() & df['DIFF_SEEING'].isna()).sum()   # compare to 6669
```

## 5. Sanity cross-tabs for the "already-correct" imputation columns

Cheap confirmations that the skip-logic reasoning in `Imputation_Crosscheck_Findings.md` actually matches row counts:
```python
df[df['AGE'] > 30]['ATTEND_SCHOOL'].isna().mean()   # expect ~1.0
df[df['AGE'] < 15]['WORK'].isna().mean()             # expect ~1.0
```

## 6. Phase 1 / Phase 2 independence — decide and fix

Confirmed by reading the notebook: the *working* Phase 2 cell (`1c2667ee`, the one that actually produced the checked-in `xgboost_*.csv` outputs) reuses Phase 1's in-memory `df` directly, rather than re-merging from raw CSVs. An earlier Phase 2 attempt in the notebook (`dc1b08dd`) does re-merge independently but has a Python `IndentationError` and never executed.

This contradicts `CLAUDE.md`'s current description: *"Phase 2 reloads and re-derives everything Phase 1 computed rather than reusing in-memory objects — treat them as independently runnable."* As currently written, Phase 2 is **not** independently runnable — it requires Phase 1's `df` to already be in memory.

**Decision needed (not yet made):** pick one —
- (a) Fix `CLAUDE.md`'s description to match reality (Phase 2 depends on Phase 1's `df`), or
- (b) Fix the notebook — repair the broken re-merge cell (`dc1b08dd`'s indentation error) so Phase 2 is genuinely standalone, matching what `CLAUDE.md` currently claims, then delete/retire the dead `df`-reusing cell (`1c2667ee`) once the standalone version is verified to produce the same results.

Leaning toward (b) for reproducibility (a thesis notebook's phases should be re-runnable from a fresh kernel independently, per `CLAUDE.md`'s own stated design intent) — but this changes which code path generates the reported results, so re-verify the `xgboost_*.csv` outputs are unchanged after the fix before treating it as a pure cleanup.
