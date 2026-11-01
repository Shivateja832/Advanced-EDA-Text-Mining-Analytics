# Advanced EDA and Text Mining Report

> This analysis uses a generated synthetic dataset for demonstration; its counts, patterns, and conclusions are not real customer or product evidence. Rule-based tags and clusters are exploratory signals, not verified root causes.

## Dataset overview
- Source rows: 3587
- Rows after duplicate removal: 3582
- Columns: 16
- Exact duplicate rows before normalization: 5
- Duplicate rows after trimming whitespace/null-like strings: 5
- Missing cells before imputation: 5
- Missing cells after supported imputation: 0

## Data quality and column profile

| column                    | dtype   |   non_null |   missing |   unique_values |      mean |   median |      std |   min |      max |
|:--------------------------|:--------|-----------:|----------:|----------------:|----------:|---------:|---------:|------:|---------:|
| Event_ID                  | string  |       3582 |         0 |            3582 |   nan     |      nan |  nan     |   nan |   nan    |
| Reported_Date             | string  |       3582 |         0 |             900 |   nan     |      nan |  nan     |   nan |   nan    |
| Product_Model             | string  |       3582 |         0 |               7 |   nan     |      nan |  nan     |   nan |   nan    |
| Product_Family            | string  |       3582 |         0 |               3 |   nan     |      nan |  nan     |   nan |   nan    |
| Component                 | string  |       3582 |         0 |              19 |   nan     |      nan |  nan     |   nan |   nan    |
| Manufacturing_Lot         | string  |       3582 |         0 |               5 |   nan     |      nan |  nan     |   nan |   nan    |
| Firmware_Version          | string  |       3582 |         0 |               5 |   nan     |      nan |  nan     |   nan |   nan    |
| Region                    | string  |       3582 |         0 |               6 |   nan     |      nan |  nan     |   nan |   nan    |
| Sales_Channel             | string  |       3582 |         0 |               5 |   nan     |      nan |  nan     |   nan |   nan    |
| Severity                  | string  |       3582 |         0 |               4 |   nan     |      nan |  nan     |   nan |   nan    |
| Days_In_Service           | int64   |       3582 |         0 |            1348 |   755.969 |      762 |  435.078 |     1 |  1499    |
| Warranty_Status           | string  |       3582 |         0 |               2 |   nan     |      nan |  nan     |   nan |   nan    |
| Active_Units              | int64   |       3582 |         0 |             195 | 14696.2   |    13399 | 4767.87  |  7200 | 23456    |
| Estimated_Repair_Cost_USD | float64 |       3582 |         0 |            3144 |   105.56  |      102 |   41.02  |    25 |   233.23 |
| Failure_Description       | string  |       3582 |         0 |              30 |   nan     |      nan |  nan     |   nan |   nan    |
| Synthetic_Data_Notice     | string  |       3582 |         0 |               1 |   nan     |      nan |  nan     |   nan |   nan    |

Numeric summary statistics describe the cleaned data. Categorical missing values are labeled `Unknown`; numeric missing values use the column median where available. A wholly missing numeric column remains missing.

### Numeric highlights

- **Active_Units**: mean 1.47e+04, median 1.34e+04, range 7.2e+03-2.35e+04.
- **Days_In_Service**: mean 756, median 762, range 1-1.5e+03.
- **Estimated_Repair_Cost_USD**: mean 106, median 102, range 25-233.

## Text-mining findings

- **Component failure**: 1775 records.
- **Electrical issue**: 718 records.
- **Software / firmware issue**: 565 records.
- **Thermal issue**: 335 records.
- **Connectivity issue**: 189 records.

The most frequent rule-based category is **Component failure** (1775 records). Validate its examples before treating it as a product-level failure signal.

### Cluster themes

- **Cluster 1**: motor, bearing, wear, noise, bearing wear
- **Cluster 2**: pairing, network-condition checks, pairing network-condition, network-condition, request pairing
- **Cluster 3**: seal, controller, inspection, request leak-path, seal inspection
- **Cluster 4**: battery, temperature, charger, airflow, temperature checks

### Repeated components/entities to investigate

- **motor** appears in 1300 tagged records.
- **bearing** appears in 1064 tagged records.
- **charger** appears in 603 tagged records.
- **battery** appears in 603 tagged records.
- **leak** appears in 552 tagged records.
- **seal** appears in 552 tagged records.
- **software** appears in 467 tagged records.
- **pump** appears in 413 tagged records.
- **fan** appears in 335 tagged records.
- **firmware** appears in 232 tagged records.
These are candidate contributors suggested by repeated text mentions, not confirmed root causes.

Clusters group text by TF-IDF similarity. They do not prove causal relationships or identify root cause without engineering validation.

## Event frequency over time

- 2024-01: 136 records
- 2024-02: 131 records
- 2024-03: 110 records
- 2024-04: 142 records
- 2024-05: 107 records
- 2024-06: 108 records
- 2024-07: 127 records
- 2024-08: 142 records
- 2024-09: 132 records
- 2024-10: 143 records
- 2024-11: 114 records
- 2024-12: 120 records
- 2025-01: 114 records
- 2025-02: 108 records
- 2025-03: 114 records
- 2025-04: 105 records
- 2025-05: 132 records
- 2025-06: 108 records
- 2025-07: 138 records
- 2025-08: 111 records
- 2025-09: 118 records
- 2025-10: 105 records
- 2025-11: 114 records
- 2025-12: 105 records
- 2026-01: 110 records
- 2026-02: 133 records
- 2026-03: 125 records
- 2026-04: 109 records
- 2026-05: 110 records
- 2026-06: 111 records

Last six-month volume changed by **-4.9%** versus the first six months (698 vs 734 records).

## Failure-mode trend

**Component failure** occurred 402 times in the most recent six months versus 300 times in the first six months (+34.0%).
Review the month-by-month chart and validate whether the change tracks product volume, reporting changes, or a genuine reliability signal.

## Segment patterns and root-cause hypotheses

- **Model concentration:** AeroWash X4 accounts for 876 of 1775 **Component failure** records (49.4%). Check its production lots, supplier changes, service conditions, and exposure before attributing causality.
- **Lot concentration:** L25-A appears in 482 top-category records (27.2%). Treat this as a testable manufacturing hypothesis, not a confirmed defect.
- **High-priority exposure:** 1353 records (37.8%) are marked high/critical; prioritize their safety, downtime, and repeat-repair review.
- **Exposure-adjusted signal:** the highest model-month rate for the most common mined category is 1.83 reports per 1,000 active units (AeroWash X4, 2025-05), among model-month groups with at least five reports. Confirm that exposure definitions and reporting coverage are comparable.

### Root-cause validation plan

1. Pull representative records from the top issue/model/lot combinations and confirm the failure mode with service and engineering teams.
2. Compare part revisions, suppliers, manufacturing dates, firmware, usage, and warranty returns for the concentrated cohorts.
3. Reproduce the failure in controlled testing and verify corrective actions against a holdout period before calling a cause confirmed.

### Prioritized stakeholder actions

1. Prioritize a cross-functional review of **Component failure** (1775 tagged records); sample cases across models, lots, severity, and reporting dates to verify the pattern.
2. Compare the highest-count model, **AeroWash X4**, with other models on an exposure-adjusted basis before initiating a targeted supplier or design change.
3. Use a staged containment/test plan with clear confirmation criteria; track repeat repairs, severity, cost, and rate after any corrective action.

## Actionable stakeholder recommendations

1. Review the highest-frequency issue category and inspect representative source records before prioritizing corrective work.
2. Compare issue categories and cluster themes against product model, component, lot, region, and release fields when those fields exist.
3. Validate text labels with subject-matter experts; refine the issue lexicon and entity terms using the provided examples workbook when available.
4. If event dates exist, monitor monthly rates alongside units shipped or installed; raw event counts alone are not failure rates.
5. Confirm suspected root causes with engineering tests, service records, and controlled failure analysis before changing product design.

## Limits and further improvements

- This report is based on generated synthetic records; use real, quality-controlled product data before making operational decisions.
- The built-in rules are generic and should be adapted to product terminology.
- Date trends do not adjust for exposure, sales volume, reporting delays, or changes in customer base.
- Clustering is unsupervised and can change with corpus size and wording.
- Future improvement: validate labels against a human-reviewed sample and measure precision/recall before operational use.
