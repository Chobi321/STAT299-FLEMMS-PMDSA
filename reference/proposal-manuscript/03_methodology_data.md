# 03. Methodology: Data Source & Processing

- **Data Source:** 2024 Functional Literacy, Education, and Mass Media Survey (FLEMMS) by the PSA. Consolidated from RTF1, RTF2, RTF3, and MEMBER volumes.
- **Sampling Design:** 2023 Geo-Enabled Master Sample (GeoMS) framework. Stratified two-stage cluster sampling:
  - *First Stage:* Primary Sampling Units (PSUs / barangays) selected with probability proportional to size (PPS).
  - *Second Stage:* Secondary Sampling Units (SSUs / households) systematically chosen.
- **Data Cleansing & Weighting:**
  - Missing data imputed as 'Not Applicable' based on survey skip-logic paths.
  - Survey sampling weights (`RESP_RFACT_F2`) must be embedded into the model loss functions to represent the true scale of the national population.