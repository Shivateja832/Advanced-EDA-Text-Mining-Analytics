# Advanced EDA and Text Mining

This local application supports the Task 2 EDA, text mining, clustering, and
stakeholder-report requirements. A deterministic synthetic product-service
dataset is included so the notebook and app can be exercised immediately. It
contains planted patterns and data-quality edge cases for demonstration only;
it is not real customer, company, or product data and its findings must not be
used to make operational decisions.

This implementation includes data cleaning, exploratory visualizations,
rule-based NLP tags, TF-IDF/K-Means complaint grouping, failure trends, and
CSV/Markdown analysis outputs.

## Included runnable data

- `data/synthetic_product_service_events.csv`: several thousand synthetic event
  records with dates, product models, components, lots, severity, exposure,
  costs, and complaint descriptions. A small number of duplicates and missing
  or whitespace-inconsistent values are intentionally present for EDA/cleaning
  validation.
- `data/synthetic_entity_examples.xlsx`: example entity vocabulary workbook
  used to enrich extracted component and issue tags.
- `generate_synthetic_dataset.py`: deterministic generator (fixed random seed)
  to recreate both files.

Regenerate the sample input with:

```powershell
python generate_synthetic_dataset.py
```

## Run locally

From this folder, create and activate a Python 3.10+ environment, then run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The app accepts CSV, XLSX, and XLSM files,
lets you select an Excel sheet and free-text/date columns, and optionally accepts
the example-entities Excel workbook. Downloads include a cleaned CSV, a text-tag
CSV, and a stakeholder Markdown report.

Numeric histogram bins are converted to display labels before charting because
Streamlit/Altair chart axes do not support pandas `Interval` objects directly.

## Streamlit Community Cloud deployment

The project is prepared for Streamlit Community Cloud:

- Repository root contains `app.py` and `requirements.txt`.
- The app and its clearly labeled synthetic demo inputs are in the repository.
- `.streamlit/config.toml` sets the server to headless mode and disables usage stats.
- `.gitignore` excludes local environments, caches, and secret files.

To publish it, sign in to [Streamlit Community Cloud](https://share.streamlit.io),
choose **Create app**, select the public GitHub repository
`Shivateja832/Advanced-EDA-Text-Mining-Analytics`, branch `main`, and set the
app file to `app.py`. Streamlit Cloud will provide the final public app URL after
the first successful build. Do not place credentials or private customer data in
this public repository.

## Notebook workflow

Open `Task2_Advanced_EDA_Text_Mining.ipynb` and run the cells in order; it is
pre-configured to use the included synthetic CSV and entity workbook. The
notebook uses the same functions as the app and saves cleaned data, extracted
tags, cluster themes, charts, monthly counts, and a stakeholder report in
`outputs/`. Replace the input paths with real approved data for real findings.

## Analysis behavior and limits

- String fields are trimmed, common null-like strings become missing, duplicate
  rows are removed, categorical missing values become `Unknown`, and numeric
  missing values are filled with the column median where available.
- Numeric summaries, missing-value counts, categorical distributions, and
  candidate free-text/date fields are profiled from the uploaded data.
- Rule-based entity/issue tags are generic starting points. Workbook terms can
  supplement entity extraction; issue categories are based on editable rules in
  `analysis.py`.
- TF-IDF keywords and KMeans clusters are exploratory groupings, not proof of
  root cause. Validate the output with subject-matter experts.
- Raw event counts do not account for product exposure, reporting rate, or
  installed base; calculate rates when suitable denominators are available.
- The generated sample plants a motor/bearing increase in one model/lot cohort
  and includes an active-unit denominator so the analysis can demonstrate
  segmentation and exposure-adjusted rates. These are test signals, not real
  manufacturing discoveries.

The app is locally runnable. A live cloud deployment is complete only after the
repository is updated and Streamlit Community Cloud reports a successful build;
the final Cloud URL must be verified after deployment.
