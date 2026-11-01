# Advanced EDA and Text Mining Report

> This analysis uses public, consumer-submitted NHTSA complaints for selected 2019 vehicle models. Reports are not independently verified, and this selected sample is not representative of the vehicle fleet. Rule-based tags and clusters are exploratory signals, not verified root causes.

## Dataset overview
- Source rows: 2273
- Rows after duplicate removal: 2273
- Columns: 15
- Exact duplicate rows before normalization: 0
- Duplicate rows after trimming whitespace/null-like strings: 0
- Missing cells before imputation: 0
- Missing cells after supported imputation: 0

## Data quality and column profile

| column              | dtype   |   non_null |   missing |   unique_values |           mean |   median |         std |   min |   max |
|:--------------------|:--------|-----------:|----------:|----------------:|---------------:|---------:|------------:|------:|------:|
| Complaint_ID        | string  |       2273 |         0 |            2273 |  nan           |      nan | nan         |   nan |   nan |
| Reported_Date       | string  |       2273 |         0 |            1416 |  nan           |      nan | nan         |   nan |   nan |
| Incident_Date       | string  |       2273 |         0 |            1426 |  nan           |      nan | nan         |   nan |   nan |
| Product_Model       | string  |       2273 |         0 |               4 |  nan           |      nan | nan         |   nan |   nan |
| Model_Year          | int64   |       2273 |         0 |               1 | 2019           |     2019 |   0         |  2019 |  2019 |
| Manufacturer        | string  |       2273 |         0 |               3 |  nan           |      nan | nan         |   nan |   nan |
| Component           | string  |       2273 |         0 |             240 |  nan           |      nan | nan         |   nan |   nan |
| Crash               | bool    |       2273 |         0 |               2 |  nan           |      nan | nan         |   nan |   nan |
| Fire                | bool    |       2273 |         0 |               2 |  nan           |      nan | nan         |   nan |   nan |
| Number_Injuries     | int64   |       2273 |         0 |               4 |    0.0369556   |        0 |   0.230675  |     0 |     3 |
| Number_Deaths       | int64   |       2273 |         0 |               2 |    0.000439947 |        0 |   0.0209749 |     0 |     1 |
| Failure_Description | string  |       2273 |         0 |            2238 |  nan           |      nan | nan         |   nan |   nan |
| Data_Source         | string  |       2273 |         0 |               1 |  nan           |      nan | nan         |   nan |   nan |
| Source_URL          | string  |       2273 |         0 |               4 |  nan           |      nan | nan         |   nan |   nan |
| Retrieved_On        | string  |       2273 |         0 |               1 |  nan           |      nan | nan         |   nan |   nan |

Numeric summary statistics describe the cleaned data. Categorical missing values are labeled `Unknown`; numeric missing values use the column median where available. A wholly missing numeric column remains missing.

### Numeric highlights

- **Model_Year**: mean 2.02e+03, median 2.02e+03, range 2.02e+03-2.02e+03.
- **Number_Injuries**: mean 0.037, median 0, range 0-3.
- **Number_Deaths**: mean 0.00044, median 0, range 0-1.

## Text-mining findings

- **Safety system issue**: 1011 records.
- **Powertrain / fuel issue**: 867 records.
- **Electrical issue**: 85 records.
- **Other / needs review**: 69 records.
- **Visibility / lighting issue**: 67 records.
- **Vehicle structure issue**: 59 records.
- **Tire / wheel issue**: 41 records.
- **Performance issue**: 23 records.
- **Physical damage**: 17 records.
- **Component failure**: 17 records.
- **Software / firmware issue**: 10 records.
- **Thermal issue**: 5 records.
- **Connectivity issue**: 2 records.

The most frequent rule-based category is **Safety system issue** (1011 records). Validate its examples before treating it as a product-level failure signal.

### Cluster themes

- **Cluster 1**: car, vehicle, unknown, problem, honda
- **Cluster 2**: contact, failure, vehicle, contact stated, stated
- **Cluster 3**: steering, wheel, steering wheel, steering steering, sticky
- **Cluster 4**: contact, parts, air bags, bags, air
- **Cluster 5**: fuel, engine, car, propulsion, fuel propulsion
- **Cluster 6**: transmission, train, power train, power, gear
- **Cluster 7**: contact, fuel gasoline, gasoline, recall repair, repair
- **Cluster 8**: collision, forward, car, forward collision, avoidance

### Repeated components/entities to investigate

- **engine** appears in 571 tagged records.
- **collision avoidance** appears in 480 tagged records.
- **brake** appears in 362 tagged records.
- **steering** appears in 328 tagged records.
- **fuel system** appears in 235 tagged records.
- **power train** appears in 230 tagged records.
- **pump** appears in 201 tagged records.
- **transmission** appears in 175 tagged records.
- **wheel** appears in 155 tagged records.
- **battery** appears in 109 tagged records.
These are candidate contributors suggested by repeated text mentions, not confirmed root causes.

Clusters group text by TF-IDF similarity. They do not prove causal relationships or identify root cause without engineering validation.

- NHTSA records marked as involving a crash: 79.
- Injuries reported across these complaints: 84.
- Deaths reported across these complaints: 1.
These are values recorded in submitted complaints, not independently verified outcomes or estimates of risk.

## Complaint filing frequency over time

- 2018-11: 1 records
- 2018-12: 3 records
- 2019-01: 6 records
- 2019-02: 7 records
- 2019-03: 17 records
- 2019-04: 8 records
- 2019-05: 14 records
- 2019-06: 15 records
- 2019-07: 44 records
- 2019-08: 43 records
- 2019-09: 35 records
- 2019-10: 27 records
- 2019-11: 16 records
- 2019-12: 16 records
- 2020-01: 26 records
- 2020-02: 25 records
- 2020-03: 15 records
- 2020-04: 10 records
- 2020-05: 13 records
- 2020-06: 20 records
- 2020-07: 19 records
- 2020-08: 15 records
- 2020-09: 16 records
- 2020-10: 12 records
- 2020-11: 15 records
- 2020-12: 18 records
- 2021-01: 18 records
- 2021-02: 31 records
- 2021-03: 19 records
- 2021-04: 17 records
- 2021-05: 10 records
- 2021-06: 9 records
- 2021-07: 13 records
- 2021-08: 13 records
- 2021-09: 6 records
- 2021-10: 12 records
- 2021-11: 7 records
- 2021-12: 6 records
- 2022-01: 10 records
- 2022-02: 58 records
- 2022-03: 34 records
- 2022-04: 21 records
- 2022-05: 16 records
- 2022-06: 33 records
- 2022-07: 21 records
- 2022-08: 25 records
- 2022-09: 23 records
- 2022-10: 14 records
- 2022-11: 15 records
- 2022-12: 15 records
- 2023-01: 10 records
- 2023-02: 18 records
- 2023-03: 22 records
- 2023-04: 14 records
- 2023-05: 21 records
- 2023-06: 22 records
- 2023-07: 21 records
- 2023-08: 21 records
- 2023-09: 22 records
- 2023-10: 19 records
- 2023-11: 20 records
- 2023-12: 20 records
- 2024-01: 25 records
- 2024-02: 37 records
- 2024-03: 31 records
- 2024-04: 33 records
- 2024-05: 44 records
- 2024-06: 39 records
- 2024-07: 31 records
- 2024-08: 42 records
- 2024-09: 33 records
- 2024-10: 31 records
- 2024-11: 31 records
- 2024-12: 40 records
- 2025-01: 29 records
- 2025-02: 24 records
- 2025-03: 30 records
- 2025-04: 25 records
- 2025-05: 37 records
- 2025-06: 25 records
- 2025-07: 35 records
- 2025-08: 26 records
- 2025-09: 27 records
- 2025-10: 22 records
- 2025-11: 26 records
- 2025-12: 29 records
- 2026-01: 22 records
- 2026-02: 29 records
- 2026-03: 26 records
- 2026-04: 37 records
- 2026-05: 38 records
- 2026-06: 47 records
- 2026-07: 43 records
- 2026-08: 60 records
- 2026-09: 53 records
- 2026-10: 34 records

Last six-month filing volume changed by **+554.8%** versus the first six months (275 vs 42 records).

## Complaint category trend

Complaints tagged **Safety system issue** were filed 96 times in the most recent six months versus 40 times in the first six months (+140.0%).
Review the month-by-month chart and determine whether the change reflects complaint/reporting behavior; filings do not by themselves establish a change in failure incidence.

## Segment patterns and root-cause hypotheses

- **Model concentration:** 2019 HONDA CR-V accounts for 592 of 1011 **Safety system issue** records (58.6%). Check its production lots, supplier changes, service conditions, and exposure before attributing causality.

### Root-cause validation plan

1. Pull representative records from the top issue/model/lot combinations and confirm the failure mode with service and engineering teams.
2. Compare part revisions, suppliers, manufacturing dates, firmware, usage, and warranty returns for the concentrated cohorts.
3. Reproduce the failure in controlled testing and verify corrective actions against a holdout period before calling a cause confirmed.

### Prioritized stakeholder actions

1. Prioritize a cross-functional review of **Safety system issue** (1011 tagged records); sample cases across models, lots, severity, and reporting dates to verify the pattern.
2. Compare the highest-count model, **2019 HONDA CR-V**, with other models on an exposure-adjusted basis before initiating a targeted supplier or design change.
3. Use a staged containment/test plan with clear confirmation criteria; track repeat repairs, severity, cost, and rate after any corrective action.

## Actionable stakeholder recommendations

1. Review the highest-frequency issue category and inspect representative source records before prioritizing corrective work.
2. Compare issue categories and cluster themes against product model, component, lot, region, and release fields when those fields exist.
3. Validate text labels with subject-matter experts; refine the issue lexicon and entity terms using the provided examples workbook when available.
4. If event dates exist, monitor monthly rates alongside units shipped or installed; raw event counts alone are not failure rates.
5. Confirm suspected root causes with engineering tests, service records, and controlled failure analysis before changing product design.

## Limits and further improvements

- NHTSA complaints are consumer-submitted reports, not verified defects; selected vehicle models do not represent the fleet. Raw complaint counts are not failure rates because vehicle exposure and reporting propensity are unavailable.
- The built-in rules are generic and should be adapted to product terminology.
- Date trends do not adjust for exposure, sales volume, reporting delays, or changes in customer base.
- Clustering is unsupervised and can change with corpus size and wording.
- Future improvement: validate labels against a human-reviewed sample and measure precision/recall before operational use.
