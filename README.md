# Advanced EDA and Text Mining

This application supports the Task 2 EDA, text mining, clustering, and
stakeholder-report requirements. Its default dataset is a snapshot of public
consumer vehicle complaints retrieved from the U.S. National Highway Traffic
Safety Administration (NHTSA) complaints API. Complaint narratives are
consumer-submitted and not independently verified; this selected set is not
representative of the vehicle fleet and cannot establish failure rates or causes.

This implementation includes data cleaning, exploratory visualizations,
rule-based NLP tags, TF-IDF/K-Means complaint grouping, failure trends, and
CSV/Markdown analysis outputs.

## Included public data

- `data/nhtsa_public_vehicle_complaints.csv`: 2,273 complaint records for four
  selected 2019 vehicle models (Honda Accord, Toyota Camry, Ford F-150, and
  Honda CR-V). Complaint IDs are retained for traceability; full VINs are not
  collected, and obvious email, phone, and VIN patterns in narrative text are
  redacted.
- `fetch_nhtsa_complaints.py`: reproducible downloader/normalizer for the
  official public API. The snapshot contains the retrieval date and source URL
  on each record.
- `data/synthetic_product_service_events.csv` and
  `generate_synthetic_dataset.py`: optional synthetic fixtures retained for
  repeatable cleaning and workflow tests. Do not treat their planted patterns
  as real evidence.
- `data/synthetic_entity_examples.xlsx`: optional entity-term workbook for
  testing vocabulary enrichment.

Refresh the public dataset with network access:

```powershell
python fetch_nhtsa_complaints.py
```

## Run locally

From this folder, create and activate a Python 3.10+ environment, then run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The app loads the included NHTSA dataset by default and accepts CSV, XLSX, and XLSM files,
lets you select an Excel sheet and free-text/date columns, and optionally accepts
the example-entities Excel workbook. Downloads include a cleaned CSV, a text-tag
CSV, and a stakeholder Markdown report.

Numeric histogram bins are converted to display labels before charting because
Streamlit/Altair chart axes do not support pandas `Interval` objects directly.

## Streamlit Community Cloud deployment

The app is deployed on Streamlit Community Cloud and was verified against the
published page:

- **Live app:** https://advanced-eda-text-mining-analytics-hs3rusxkyzch9msng8dmvm.streamlit.app/
- **Source:** `Shivateja832/Advanced-EDA-Text-Mining-Analytics`, branch `main`, file `app.py`

The project is prepared for Streamlit Community Cloud:

- Repository root contains `app.py` and `requirements.txt`.
- The app and its public complaint data snapshot are in the repository.
- `.streamlit/config.toml` sets the server to headless mode and disables usage stats.
- `.gitignore` excludes local environments, caches, and secret files.

To recreate the deployment, sign in to [Streamlit Community Cloud](https://share.streamlit.io),
choose **Create app**, select the public GitHub repository
`Shivateja832/Advanced-EDA-Text-Mining-Analytics`, branch `main`, and set the
app file to `app.py`. Streamlit Cloud will provide the final public app URL after
the first successful build. Do not place credentials or private customer data in
this public repository.

## Notebook workflow

Open `Advanced_EDA_Text_Mining.ipynb` and run the cells in order; it is
pre-configured to use the included public NHTSA CSV. The notebook uses the same functions as the app and saves cleaned data, extracted
tags, cluster themes, charts, monthly counts, and a stakeholder report in
`outputs/`. Replace the input paths with real approved data for real findings.

## Analysis behavior and limits

- String fields are trimmed, common null-like strings become missing, duplicate
  rows are removed, categorical missing values become `Unknown`, and numeric
  missing values are filled with the column median where available. The included
  NHTSA snapshot has no intentional missing cells or
  duplicate rows; the cleaning workflow is still applied and reports the observed
  quality results instead of manufacturing defects in the evidence.
- Numeric summaries, missing-value counts, categorical distributions, and
  candidate free-text/date fields are profiled from the uploaded data.
- Rule-based entity/issue tags are generic starting points. Workbook terms can
  supplement entity extraction; issue categories are based on editable rules in
  `analysis.py`.
- TF-IDF keywords and KMeans clusters are exploratory groupings, not proof of
  root cause. Validate the output with subject-matter experts.
- Raw event counts do not account for product exposure, reporting rate, or
  installed base; calculate rates when suitable denominators are available.
- The default NHTSA dataset has no fleet-size denominator; complaint counts
  cannot be interpreted as model failure rates. Complaint dates show filing
  frequency, not necessarily when a failure occurred.
- The selected 2019 model sample is chosen for workflow coverage, not statistical
  representativeness. Verify any pattern against complete, exposure-adjusted
  manufacturer/service data before product decisions.

The deployment log showed dependencies installed and the Uvicorn server started.
The public page rendered the analysis sections and download controls. The
included complaint narratives are public reports, but are not independently
verified product evidence.
