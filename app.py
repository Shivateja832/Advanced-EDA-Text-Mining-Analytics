"""Local Streamlit interface for upload-based EDA and text mining."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import zipfile

import pandas as pd
import streamlit as st

from analysis import (
    clean_dataset,
    detect_date_columns,
    detect_text_columns,
    generate_report,
    load_dataset,
    mine_text,
    monthly_trend,
    profile_columns,
    top_value_counts,
)


st.set_page_config(page_title="Advanced EDA and Text Mining", layout="wide")
st.title("Advanced EDA and Text Mining")
st.caption(
    "Upload a CSV, XLSX, or XLSM file to profile data quality, explore distributions, "
    "extract text tags, group issue reports, and download analysis outputs."
)
st.info(
    "Synthetic sample findings are illustrative only. Upload real approved data "
    "for operational analysis; rule-based tags and clusters are not confirmed causes."
)

uploaded_file = st.file_uploader(
    "Upload a dataset (or use the included synthetic demonstration data)",
    type=["csv", "xlsx", "xlsm"],
)
reference_file = st.file_uploader(
    "Optional: upload an entity-examples workbook (terms in cells are used as extra tags)",
    type=["xlsx", "xlsm"],
)

using_sample = uploaded_file is None
if using_sample:
    sample_path = Path(__file__).resolve().parent / "data" / "synthetic_product_service_events.csv"
    st.caption("Using the included synthetic sample; it is not real customer data.")
    try:
        data = load_dataset(sample_path, sample_path.name)
    except (ValueError, OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"Could not read the included sample dataset: {error}")
        st.stop()
else:
    try:
        source_bytes = uploaded_file.getvalue()
        if uploaded_file.name.lower().endswith((".xlsx", ".xlsm")):
            excel_file = pd.ExcelFile(BytesIO(source_bytes))
            sheet = st.selectbox("Excel sheet", excel_file.sheet_names)
            data = load_dataset(BytesIO(source_bytes), uploaded_file.name, sheet_name=sheet)
        else:
            data = load_dataset(BytesIO(source_bytes), uploaded_file.name)
    except (
        ValueError,
        OSError,
        UnicodeDecodeError,
        zipfile.BadZipFile,
        pd.errors.ParserError,
        ImportError,
    ) as error:
        st.error(f"Could not read the uploaded file: {error}")
        st.stop()

if len(data.columns) == 0:
    st.error("The uploaded file contains no columns.")
    st.stop()

cleaned, audit = clean_dataset(data)
st.subheader("Data quality")
metric_columns = st.columns(4)
metric_columns[0].metric("Source rows", f"{audit['original_rows']:,}")
metric_columns[1].metric("Rows after deduplication", f"{len(cleaned):,}")
metric_columns[2].metric("Duplicate rows", f"{audit['exact_duplicate_rows']:,}")
metric_columns[3].metric(
    "Missing cells before cleaning",
    f"{int(audit['missing_before_imputation'].sum()):,}",
)

left, right = st.columns(2)
with left:
    st.markdown("**Missing values by column (before imputation)**")
    missing_table = audit["missing_before_imputation"]
    st.dataframe(
        missing_table.rename("Missing").to_frame().sort_values("Missing", ascending=False),
        width="stretch",
    )
with right:
    st.markdown("**Column profile**")
    st.dataframe(profile_columns(cleaned), width="stretch")

st.subheader("Distributions")
numeric_columns = list(cleaned.select_dtypes(include="number").columns)
categorical_columns = [
    str(column)
    for column in cleaned.columns
    if column not in numeric_columns and cleaned[column].nunique(dropna=True) <= 100
]
plot_left, plot_right = st.columns(2)
with plot_left:
    if numeric_columns:
        numeric_column = st.selectbox("Numeric column", numeric_columns)
        numeric_values = cleaned[numeric_column].dropna()
        if numeric_values.empty:
            st.caption("No numeric values available to plot.")
        else:
            bin_count = min(20, max(1, int(numeric_values.nunique())))
            histogram = pd.cut(
                numeric_values, bins=bin_count, duplicates="drop"
            ).value_counts(sort=False)
            histogram_data = histogram.rename_axis("Bin").reset_index(name="Count")
            histogram_data["Bin"] = histogram_data["Bin"].astype(str)
            st.bar_chart(histogram_data, x="Bin", y="Count")
        st.dataframe(cleaned[numeric_columns].describe().T, width="stretch")
    else:
        st.caption("No numeric columns available.")
with plot_right:
    if categorical_columns:
        category_column = st.selectbox("Categorical column", categorical_columns)
        st.bar_chart(top_value_counts(cleaned, category_column))
    else:
        st.caption("No categorical columns with at most 100 unique values available.")

text_suggestions = detect_text_columns(cleaned)
text_columns = st.multiselect(
    "Free-text columns to analyze",
    options=[str(column) for column in cleaned.columns],
    default=text_suggestions,
    help="Suggestions use string type, typical text length, and value diversity. Adjust as needed.",
)

date_suggestions = detect_date_columns(cleaned)
date_options = ["None"] + [str(column) for column in cleaned.columns]
default_date = date_suggestions[0] if date_suggestions else "None"
date_column = st.selectbox(
    "Optional event date column for monthly trends",
    date_options,
    index=date_options.index(default_date),
)

extra_terms = []
if reference_file is not None:
    try:
        entity_data = pd.read_excel(reference_file, sheet_name=None, header=None)
        for sheet_data in entity_data.values():
            extra_terms.extend(
                str(value).strip()
                for value in sheet_data.to_numpy().ravel()
                if pd.notna(value) and str(value).strip()
            )
        extra_terms = list(dict.fromkeys(extra_terms))
        st.success(f"Loaded {len(extra_terms)} distinct terms from the reference workbook.")
    except (ValueError, OSError, zipfile.BadZipFile, ImportError) as error:
        st.error(f"Could not read the entity-examples workbook: {error}")
        st.stop()
elif using_sample:
    examples_path = Path(__file__).resolve().parent / "data" / "synthetic_entity_examples.xlsx"
    if not examples_path.is_file():
        st.error(f"The included entity-examples workbook is missing: {examples_path}")
        st.stop()
    entity_data = pd.read_excel(examples_path, sheet_name=None, header=None)
    for sheet_data in entity_data.values():
        extra_terms.extend(
            str(value).strip()
            for value in sheet_data.to_numpy().ravel()
            if pd.notna(value) and str(value).strip()
        )
    extra_terms = list(dict.fromkeys(extra_terms))

if text_columns:
    mined, representatives = mine_text(cleaned, text_columns, extra_terms)
    st.subheader("Text mining")
    issue_counts = mined["Issue_Type"].value_counts().rename("Record_Count")
    st.markdown("**Most frequently assigned issue categories**")
    st.bar_chart(issue_counts)
    st.dataframe(issue_counts.to_frame(), width="stretch")

    cluster_rows = [
        {
            "Text_Cluster": cluster,
            "Representative_Terms": "; ".join(terms),
        }
        for cluster, terms in representatives.items()
    ]
    st.markdown("**Cluster themes (similarity groups, not confirmed causes)**")
    st.dataframe(pd.DataFrame(cluster_rows), width="stretch")
    st.markdown("**Extracted tags preview**")
    st.dataframe(
        mined[
            [
                "Record_ID",
                "Issue_Type",
                "Entity_Tags",
                "Keyword_Tags",
                "Text_Cluster",
                "Cluster_Top_Terms",
            ]
        ].head(100),
        width="stretch",
    )
else:
    mined, representatives = None, {}
    st.warning("Select at least one text column to generate text tags and issue categories.")

if date_column != "None":
    trend = monthly_trend(cleaned, date_column)
    st.subheader("Monthly event frequency")
    if trend.empty:
        st.warning(f"No usable dates found in '{date_column}'.")
    else:
        st.line_chart(trend.set_index("Month")["Record_Count"])
        st.dataframe(trend, width="stretch")

report = generate_report(
    data,
    cleaned,
    audit,
    mined_data=mined,
    representatives=representatives,
    date_column=date_column if date_column != "None" else None,
)
st.subheader("Downloads")
st.download_button(
    "Download cleaned dataset (CSV)",
    data=cleaned.to_csv(index=False).encode("utf-8-sig"),
    file_name="cleaned_dataset.csv",
    mime="text/csv",
)
if mined is not None:
    st.download_button(
        "Download extracted text tags (CSV)",
        data=mined.to_csv(index=False).encode("utf-8-sig"),
        file_name="extracted_text_tags.csv",
        mime="text/csv",
    )
st.download_button(
    "Download stakeholder report (Markdown)",
    data=report.encode("utf-8"),
    file_name="stakeholder_report.md",
    mime="text/markdown",
)
