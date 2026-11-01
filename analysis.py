"""Reusable EDA and text-mining functions for the Task 2 analysis."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


ISSUE_RULES = {
    "Electrical issue": (
        "battery", "charger", "charging", "power", "voltage", "current",
        "electrical", "electric", "short circuit", "fuse", "wiring",
    ),
    "Software / firmware issue": (
        "software", "firmware", "crash", "freeze", "frozen", "reboot",
        "bug", "application", "app",
    ),
    "Thermal issue": (
        "overheat", "overheating", "overheated", "overheats", "hot", "heat",
        "temperature", "thermal",
    ),
    "Connectivity issue": (
        "wifi", "wi-fi", "bluetooth", "network", "connection", "connectivity",
        "pairing", "signal",
    ),
    "Component failure": (
        "motor", "sensor", "pump", "compressor", "valve", "bearing", "fan",
        "switch", "relay", "capacitor", "seal", "filter", "display", "screen",
        "connector", "circuit board", "pcb", "engine",
    ),
    "Physical damage": (
        "broken", "cracked", "damage", "damaged", "leak", "leaking",
        "corrosion", "rust",
    ),
    "Performance issue": (
        "slow", "performance", "intermittent", "not working", "fails",
        "failure", "failed", "stopped", "low output", "weak",
    ),
}

ENTITY_TERMS = {
    "battery", "charger", "motor", "sensor", "pump", "compressor", "valve",
    "bearing", "fan", "switch", "fuse", "relay", "capacitor", "seal",
    "filter", "display", "screen", "connector", "circuit board", "pcb",
    "engine", "cable", "wire", "wifi", "wi-fi", "bluetooth", "firmware",
    "software", "overheat", "overheating", "overheated", "overheats", "leak",
    "corrosion",
}

NULL_LIKE_VALUES = {"", "na", "n/a", "null", "none", "nan"}


def load_dataset(source, filename: str, sheet_name=0) -> pd.DataFrame:
    """Load CSV or Excel data without assuming a schema."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    if suffix in {".xlsx", ".xlsm"}:
        return pd.read_excel(source, sheet_name=sheet_name)
    raise ValueError("Unsupported file type. Upload a CSV or Excel workbook.")


def clean_dataset(data: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Trim string inconsistencies, remove duplicate rows, and impute missing values."""
    if data.empty and len(data.columns) == 0:
        raise ValueError("The uploaded dataset has no columns.")

    original_rows = len(data)
    exact_duplicates = int(data.duplicated().sum())
    cleaned = data.copy()
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        values = cleaned[column].astype("string").str.strip()
        cleaned[column] = values.mask(values.str.casefold().isin(NULL_LIKE_VALUES))

    normalized_duplicates = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates().copy()
    missing_before = cleaned.isna().sum()

    for column in cleaned.columns:
        if pd.api.types.is_numeric_dtype(cleaned[column]):
            median = cleaned[column].median()
            if pd.notna(median):
                cleaned[column] = cleaned[column].fillna(median)
        elif cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna("Unknown")

    audit = {
        "original_rows": original_rows,
        "rows_after_deduplication": len(cleaned),
        "exact_duplicate_rows": exact_duplicates,
        "duplicates_after_whitespace_normalization": normalized_duplicates,
        "missing_before_imputation": missing_before,
        "missing_after_imputation": cleaned.isna().sum(),
    }
    return cleaned, audit


def profile_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize dtype, non-null/missing counts, cardinality, and numeric statistics."""
    rows = []
    for column in data.columns:
        series = data[column]
        row = {
            "column": str(column),
            "dtype": str(series.dtype),
            "non_null": int(series.notna().sum()),
            "missing": int(series.isna().sum()),
            "unique_values": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            row.update(
                {
                    "mean": series.mean(),
                    "median": series.median(),
                    "std": series.std(),
                    "min": series.min(),
                    "max": series.max(),
                }
            )
        else:
            row.update(
                {
                    "mean": np.nan,
                    "median": np.nan,
                    "std": np.nan,
                    "min": np.nan,
                    "max": np.nan,
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def detect_text_columns(data: pd.DataFrame) -> list[str]:
    """Suggest likely free-text columns using type, average length, and cardinality."""
    candidates = []
    for column in data.select_dtypes(include=["object", "string"]).columns:
        if re.search(r"(^|[_\s])(id|key|code|serial|sku|notice)([_\s]|$)", str(column), re.I):
            continue
        if re.search(r"date|time|created|reported|occurred", str(column), re.I):
            continue
        values = data[column].dropna().astype(str)
        if values.empty:
            continue
        average_length = values.str.len().mean()
        unique_ratio = values.nunique() / max(len(values), 1)
        if values.nunique() < min(5, len(values)):
            continue
        if average_length >= 20 and unique_ratio >= 0.001:
            candidates.append(str(column))
        elif average_length >= 8 and unique_ratio >= 0.3:
            candidates.append(str(column))
    return candidates


def detect_date_columns(data: pd.DataFrame) -> list[str]:
    """Suggest date columns based on names or successful parsing of sample values."""
    candidates = []
    for column in data.columns:
        if re.search(r"date|time|created|reported|occurred", str(column), re.I):
            candidates.append(str(column))
            continue
        if not pd.api.types.is_numeric_dtype(data[column]):
            values = data[column].dropna().astype(str).head(30)
            if len(values) and pd.to_datetime(
                values, errors="coerce", format="mixed"
            ).notna().mean() >= 0.8:
                candidates.append(str(column))
    return candidates


def _contains_term(text: str, term: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None


def classify_issue(text: str) -> str:
    """Assign the first matching issue category; unmatched records remain explicit."""
    normalized = text.casefold()
    for category, terms in ISSUE_RULES.items():
        if any(_contains_term(normalized, term) for term in terms):
            return category
    return "Other / needs review"


def _row_keywords(texts: list[str], limit: int = 5) -> list[list[str]]:
    """Return each record's highest TF-IDF unigram/bigram terms."""
    if not texts:
        return []
    keywords = [[] for _ in texts]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=3000,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b",
    )
    analyzer = vectorizer.build_analyzer()
    usable = [bool(analyzer(text)) for text in texts]
    if not any(usable):
        return keywords
    matrix = vectorizer.fit_transform([text for text, keep in zip(texts, usable) if keep])
    terms = vectorizer.get_feature_names_out()
    row_index = 0
    for index, keep in enumerate(usable):
        if not keep:
            continue
        row = matrix.getrow(row_index)
        ranked = sorted(zip(row.indices, row.data), key=lambda item: item[1], reverse=True)
        keywords[index] = [str(terms[column]) for column, _ in ranked[:limit]]
        row_index += 1
    return keywords


def _cluster_texts(texts: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    """Group non-empty issue text and return human-readable representative terms."""
    labels = [
        "Unclustered - empty text" if not text.strip() else "Unclustered - no useful terms"
        for text in texts
    ]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=3000,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b",
    )
    analyzer = vectorizer.build_analyzer()
    nonempty_indices = [i for i, text in enumerate(texts) if analyzer(text)]
    unique_texts = list(dict.fromkeys(texts[i] for i in nonempty_indices))
    if len(unique_texts) < 2:
        for index in nonempty_indices:
            labels[index] = "Cluster 1"
        return labels, {"Cluster 1": []} if unique_texts else {}

    matrix = vectorizer.fit_transform(unique_texts)
    terms = vectorizer.get_feature_names_out()
    signatures = []
    for row_index in range(matrix.shape[0]):
        row = matrix.getrow(row_index)
        signatures.append(
            tuple(
                (int(feature), round(float(weight), 12))
                for feature, weight in zip(row.indices, row.data)
            )
        )

    unique_positions = {}
    for position, signature in enumerate(signatures):
        unique_positions.setdefault(signature, position)
    if len(unique_positions) < 2:
        for index in nonempty_indices:
            labels[index] = "Cluster 1"
        return labels, {"Cluster 1": []}

    distinct_signatures = list(unique_positions)
    distinct_matrix = matrix[list(unique_positions.values())]
    cluster_count = min(8, max(2, round(np.sqrt(len(distinct_signatures) / 2))))
    cluster_count = min(cluster_count, len(distinct_signatures))
    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    unique_labels = model.fit_predict(distinct_matrix)
    label_by_signature = {
        signature: f"Cluster {int(cluster) + 1}"
        for signature, cluster in zip(distinct_signatures, unique_labels)
    }
    signature_by_text = dict(zip(unique_texts, signatures))
    for index in nonempty_indices:
        labels[index] = label_by_signature[signature_by_text[texts[index]]]

    representatives = {}
    for cluster_index, center in enumerate(model.cluster_centers_):
        top_indices = center.argsort()[::-1][:5]
        representatives[f"Cluster {cluster_index + 1}"] = [
            str(terms[index]) for index in top_indices if center[index] > 0
        ]
    return labels, representatives


def mine_text(
    data: pd.DataFrame,
    text_columns: Iterable[str],
    extra_entity_terms: Iterable[str] = (),
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Extract issue categories, lexicon entities, TF-IDF keywords, and text clusters."""
    columns = list(text_columns)
    if not columns:
        raise ValueError("Select at least one free-text column.")
    missing_columns = [column for column in columns if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Selected text columns are missing: {missing_columns}")

    texts = (
        data[columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .tolist()
    )
    keywords = _row_keywords(texts)
    clusters, representatives = _cluster_texts(texts)
    terms = ENTITY_TERMS | {
        str(term).strip().casefold()
        for term in extra_entity_terms
        if str(term).strip()
    }
    sorted_terms = sorted(terms, key=lambda value: (-len(value), value))

    result = data.copy()
    result["Record_ID"] = [str(index) for index in data.index]
    result["Mined_Text"] = texts
    result["Issue_Type"] = [classify_issue(text) for text in texts]
    result["Entity_Tags"] = [
        "; ".join(term for term in sorted_terms if _contains_term(text.casefold(), term))
        for text in texts
    ]
    result["Keyword_Tags"] = ["; ".join(values) for values in keywords]
    result["Text_Cluster"] = clusters
    result["Cluster_Top_Terms"] = [
        "; ".join(representatives.get(label, [])) for label in clusters
    ]
    return result, representatives


def monthly_trend(data: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """Count records by month, retaining invalid/missing dates outside the trend."""
    parsed = pd.to_datetime(data[date_column], errors="coerce")
    valid = parsed.dropna()
    if valid.empty:
        return pd.DataFrame(columns=["Month", "Record_Count"])
    counts = valid.dt.to_period("M").value_counts().sort_index()
    return pd.DataFrame(
        {"Month": counts.index.astype(str), "Record_Count": counts.to_numpy()}
    )


def generate_report(
    data: pd.DataFrame,
    cleaned_data: pd.DataFrame,
    audit: dict,
    mined_data: pd.DataFrame | None = None,
    representatives: dict[str, list[str]] | None = None,
    date_column: str | None = None,
) -> str:
    """Build a data-derived Markdown summary with explicit limits on interpretation."""
    profile = profile_columns(cleaned_data)
    numeric = profile.loc[profile["mean"].notna()].sort_values(
        "mean", ascending=False
    )
    category_counts = (
        mined_data["Issue_Type"].value_counts()
        if mined_data is not None and "Issue_Type" in mined_data
        else pd.Series(dtype=int)
    )
    is_synthetic = (
        "Synthetic_Data_Notice" in cleaned_data.columns
        and cleaned_data["Synthetic_Data_Notice"]
        .astype("string")
        .str.contains("synthetic", case=False, na=False)
        .any()
    )
    provenance_notice = (
        "This analysis uses a generated synthetic dataset for demonstration; "
        "its counts, patterns, and conclusions are not real customer or product evidence."
        if is_synthetic
        else "This report is generated from the uploaded records."
    )
    lines = [
        "# Advanced EDA and Text Mining Report",
        "",
        f"> {provenance_notice} Rule-based tags and clusters are exploratory "
        "signals, not verified root causes.",
        "",
        "## Dataset overview",
        f"- Source rows: {audit['original_rows']}",
        f"- Rows after duplicate removal: {audit['rows_after_deduplication']}",
        f"- Columns: {data.shape[1]}",
        f"- Exact duplicate rows before normalization: {audit['exact_duplicate_rows']}",
        "- Duplicate rows after trimming whitespace/null-like strings: "
        f"{audit['duplicates_after_whitespace_normalization']}",
        f"- Missing cells before imputation: {int(audit['missing_before_imputation'].sum())}",
        f"- Missing cells after supported imputation: {int(audit['missing_after_imputation'].sum())}",
        "",
        "## Data quality and column profile",
        "",
        profile.to_markdown(index=False),
        "",
        "Numeric summary statistics describe the cleaned data. Categorical missing "
        "values are labeled `Unknown`; numeric missing values use the column median "
        "where available. A wholly missing numeric column remains missing.",
        "",
    ]
    if numeric.empty:
        lines += ["No numeric columns were available for numeric summary statistics.", ""]
    else:
        lines += ["### Numeric highlights", ""]
        lines.extend(
            f"- **{row['column']}**: mean {row['mean']:.3g}, median "
            f"{row['median']:.3g}, range {row['min']:.3g}-{row['max']:.3g}."
            for _, row in numeric.head(5).iterrows()
        )
        lines.append("")

    if mined_data is not None:
        lines += ["## Text-mining findings", ""]
        if category_counts.empty:
            lines.append("No issue categories were generated.")
        else:
            for category, count in category_counts.items():
                record_word = "record" if int(count) == 1 else "records"
                lines.append(f"- **{category}**: {int(count)} {record_word}.")
            top_category = str(category_counts.index[0])
            record_word = "record" if int(category_counts.iloc[0]) == 1 else "records"
            lines += [
                "",
                f"The most frequent rule-based category is **{top_category}** "
                f"({int(category_counts.iloc[0])} {record_word}). Validate its examples "
                "before treating it as a product-level failure signal.",
            ]
        lines += ["", "### Cluster themes", ""]
        for cluster, terms in (representatives or {}).items():
            lines.append(f"- **{cluster}**: {', '.join(terms) if terms else 'No representative terms'}")
        entity_counts = (
            mined_data["Entity_Tags"]
            .dropna()
            .str.split("; ")
            .explode()
        )
        entity_counts = entity_counts[entity_counts.ne("")].value_counts()
        if not entity_counts.empty:
            lines += [
                "",
                "### Repeated components/entities to investigate",
                "",
            ]
            lines.extend(
                f"- **{entity}** appears in {int(count)} tagged records."
                for entity, count in entity_counts.head(10).items()
            )
            lines.append(
                "These are candidate contributors suggested by repeated text mentions, "
                "not confirmed root causes."
            )
        lines += [
            "",
            "Clusters group text by TF-IDF similarity. They do not prove causal "
            "relationships or identify root cause without engineering validation.",
            "",
        ]

    if date_column:
        trend = monthly_trend(cleaned_data, date_column)
        lines += ["## Event frequency over time", ""]
        if trend.empty:
            lines.append(f"No parseable dates were found in `{date_column}`.")
        else:
            lines.extend(
                f"- {row.Month}: {int(row.Record_Count)} records"
                for row in trend.itertuples(index=False)
            )
            if len(trend) >= 12:
                previous = int(trend.iloc[:6]["Record_Count"].sum())
                recent = int(trend.iloc[-6:]["Record_Count"].sum())
                if previous:
                    change = (recent - previous) / previous * 100
                    lines += [
                        "",
                        f"Last six-month volume changed by **{change:+.1f}%** "
                        f"versus the first six months ({recent} vs {previous} records).",
                    ]
        lines.append("")

    if mined_data is not None:
        if date_column and not category_counts.empty:
            dates = pd.to_datetime(mined_data[date_column], errors="coerce")
            trend_rows = mined_data.assign(
                _Month=dates.dt.to_period("M").astype("string")
            ).dropna(subset=["_Month"])
            top_issue = str(category_counts.index[0])
            issue_monthly = (
                trend_rows.loc[trend_rows["Issue_Type"].eq(top_issue)]
                .groupby("_Month")
                .size()
                .sort_index()
            )
            if len(issue_monthly) >= 12:
                previous_issue_count = int(issue_monthly.iloc[:6].sum())
                recent_issue_count = int(issue_monthly.iloc[-6:].sum())
                issue_change = (
                    (recent_issue_count - previous_issue_count)
                    / previous_issue_count
                    * 100
                    if previous_issue_count
                    else None
                )
                lines += [
                    "## Failure-mode trend",
                    "",
                    f"**{top_issue}** occurred {recent_issue_count} times in the most "
                    f"recent six months versus {previous_issue_count} times in the "
                    "first six months"
                    + (
                        f" ({issue_change:+.1f}%)."
                        if issue_change is not None
                        else "."
                    ),
                    "Review the month-by-month chart and validate whether the change "
                    "tracks product volume, reporting changes, or a genuine reliability signal.",
                    "",
                ]

        model_column = next(
            (column for column in ["Product_Model", "Model", "Product"] if column in mined_data),
            None,
        )
        if model_column and not category_counts.empty:
            top_issue = str(category_counts.index[0])
            issue_rows = mined_data.loc[mined_data["Issue_Type"].eq(top_issue)]
            model_counts = issue_rows[model_column].value_counts()
            if not model_counts.empty:
                model_name = str(model_counts.index[0])
                share = model_counts.iloc[0] / max(len(issue_rows), 1) * 100
                lines += [
                    "## Segment patterns and root-cause hypotheses",
                    "",
                    f"- **Model concentration:** {model_name} accounts for "
                    f"{int(model_counts.iloc[0])} of {len(issue_rows)} "
                    f"**{top_issue}** records ({share:.1f}%). Check its production "
                    "lots, supplier changes, service conditions, and exposure before "
                    "attributing causality.",
                ]
                lot_column = next(
                    (column for column in ["Manufacturing_Lot", "Lot", "Batch"] if column in issue_rows),
                    None,
                )
                if lot_column:
                    lot_counts = issue_rows[lot_column].value_counts()
                    if not lot_counts.empty:
                        lot_name = str(lot_counts.index[0])
                        lot_share = lot_counts.iloc[0] / max(len(issue_rows), 1) * 100
                        lines.append(
                            f"- **Lot concentration:** {lot_name} appears in "
                            f"{int(lot_counts.iloc[0])} top-category records "
                            f"({lot_share:.1f}%). Treat this as a testable manufacturing "
                            "hypothesis, not a confirmed defect."
                        )

        severity_column = next(
            (column for column in ["Severity", "Priority", "Impact"] if column in mined_data),
            None,
        )
        if severity_column:
            high_mask = mined_data[severity_column].astype(str).str.casefold().isin(
                {"critical", "high", "urgent", "p1", "sev1"}
            )
            high_count = int(high_mask.sum())
            high_share = high_count / max(len(mined_data), 1) * 100
            lines.append(
                f"- **High-priority exposure:** {high_count} records "
                f"({high_share:.1f}%) are marked high/critical; prioritize their "
                "safety, downtime, and repeat-repair review."
            )
        if "Active_Units" in mined_data and model_column and date_column:
            dated = pd.to_datetime(mined_data[date_column], errors="coerce")
            rate_frame = mined_data.assign(_Month=dated.dt.to_period("M").astype("string"))
            if "Issue_Type" in rate_frame:
                rate_frame = rate_frame.loc[rate_frame["Issue_Type"].eq(str(category_counts.index[0]))]
            grouped = rate_frame.groupby([model_column, "_Month"], dropna=True).agg(
                events=("Record_ID", "count"),
                exposure=("Active_Units", "first"),
            )
            eligible = grouped.loc[grouped["events"].ge(5) & grouped["exposure"].gt(0)].copy()
            if not eligible.empty:
                eligible["events_per_1000_active_units"] = (
                    eligible["events"] / eligible["exposure"] * 1000
                )
                top_cell = eligible["events_per_1000_active_units"].idxmax()
                lines.append(
                    f"- **Exposure-adjusted signal:** the highest model-month rate "
                    f"for the most common mined category is {eligible.loc[top_cell, 'events_per_1000_active_units']:.2f} "
                    f"reports per 1,000 active units ({top_cell[0]}, {top_cell[1]}), "
                    "among model-month groups with at least five reports. Confirm "
                    "that exposure definitions and reporting coverage are comparable."
                )
        lines += [
            "",
            "### Root-cause validation plan",
            "",
            "1. Pull representative records from the top issue/model/lot combinations "
            "and confirm the failure mode with service and engineering teams.",
            "2. Compare part revisions, suppliers, manufacturing dates, firmware, "
            "usage, and warranty returns for the concentrated cohorts.",
            "3. Reproduce the failure in controlled testing and verify corrective "
            "actions against a holdout period before calling a cause confirmed.",
            "",
        ]
        if not category_counts.empty:
            top_issue = str(category_counts.index[0])
            lines += [
                "### Prioritized stakeholder actions",
                "",
                f"1. Prioritize a cross-functional review of **{top_issue}** "
                f"({int(category_counts.iloc[0])} tagged records); sample cases "
                "across models, lots, severity, and reporting dates to verify the pattern.",
            ]
            if model_column and not category_counts.empty:
                issue_rows = mined_data.loc[mined_data["Issue_Type"].eq(top_issue)]
                model_counts = issue_rows[model_column].value_counts()
                if not model_counts.empty:
                    lines.append(
                        f"2. Compare the highest-count model, **{model_counts.index[0]}**, "
                        "with other models on an exposure-adjusted basis before initiating "
                        "a targeted supplier or design change."
                    )
            lines.append(
                "3. Use a staged containment/test plan with clear confirmation criteria; "
                "track repeat repairs, severity, cost, and rate after any corrective action."
            )
            lines.append("")

    lines += [
        "## Actionable stakeholder recommendations",
        "",
        "1. Review the highest-frequency issue category and inspect representative "
        "source records before prioritizing corrective work.",
        "2. Compare issue categories and cluster themes against product model, "
        "component, lot, region, and release fields when those fields exist.",
        "3. Validate text labels with subject-matter experts; refine the issue "
        "lexicon and entity terms using the provided examples workbook when available.",
        "4. If event dates exist, monitor monthly rates alongside units shipped or "
        "installed; raw event counts alone are not failure rates.",
        "5. Confirm suspected root causes with engineering tests, service records, "
        "and controlled failure analysis before changing product design.",
        "",
        "## Limits and further improvements",
        "",
        (
            "- This report is based on generated synthetic records; use real, "
            "quality-controlled product data before making operational decisions."
            if is_synthetic
            else "- Findings depend on the source dataset and chosen text/date columns."
        ),
        "- The built-in rules are generic and should be adapted to product terminology.",
        "- Date trends do not adjust for exposure, sales volume, reporting delays, or "
        "changes in customer base.",
        "- Clustering is unsupervised and can change with corpus size and wording.",
        "- Future improvement: validate labels against a human-reviewed sample and "
        "measure precision/recall before operational use.",
        "",
    ]
    return "\n".join(lines)


def top_value_counts(data: pd.DataFrame, column: str, limit: int = 15) -> pd.Series:
    """Return the most common non-null values for a selected categorical column."""
    return data[column].value_counts(dropna=False).head(limit)
