"""Download and normalize public NHTSA vehicle complaints for the analysis."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "data" / "nhtsa_public_vehicle_complaints.csv"
API_ROOT = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
VEHICLES = (
    ("HONDA", "ACCORD", 2019),
    ("TOYOTA", "CAMRY", 2019),
    ("FORD", "F-150", 2019),
    ("HONDA", "CR-V", 2019),
)


def _redact_contact_details(text: str) -> str:
    """Avoid retaining obvious contact identifiers from free-text reports."""
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[redacted email]", text)
    text = re.sub(
        r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)",
        "[redacted phone]",
        text,
    )
    text = re.sub(r"\b[A-HJ-NPR-Z0-9]{17}\b", "[redacted VIN]", text, flags=re.I)
    return text


def _get_complaints(make: str, model: str, model_year: int) -> tuple[str, list[dict]]:
    query = urlencode({"make": make, "model": model, "modelYear": model_year})
    source_url = f"{API_ROOT}?{query}"
    request = Request(source_url, headers={"User-Agent": "EDA-Text-Mining-Student-Project/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Unable to retrieve NHTSA records for {make} {model} {model_year}: {error}") from error

    complaints = payload.get("results")
    if not isinstance(complaints, list):
        raise ValueError(f"NHTSA returned an unexpected response for {make} {model} {model_year}.")
    return source_url, complaints


def build_dataset() -> pd.DataFrame:
    rows = []
    for make, model, model_year in VEHICLES:
        source_url, complaints = _get_complaints(make, model, model_year)
        print(f"{make} {model} {model_year}: {len(complaints):,} complaints")
        for complaint in complaints:
            products = complaint.get("products") or []
            product = next(
                (item for item in products if item.get("type") == "Vehicle"),
                products[0] if products else {},
            )
            description = str(complaint.get("summary") or "").strip()
            rows.append(
                {
                    "Complaint_ID": f"ODI-{complaint.get('odiNumber') or ''}",
                    "Reported_Date": complaint.get("dateComplaintFiled"),
                    "Incident_Date": complaint.get("dateOfIncident"),
                    "Product_Model": " ".join(
                        str(value).strip()
                        for value in (
                            product.get("productYear") or model_year,
                            product.get("productMake") or make,
                            product.get("productModel") or model,
                        )
                    ),
                    "Model_Year": product.get("productYear") or model_year,
                    "Manufacturer": complaint.get("manufacturer") or make,
                    "Component": complaint.get("components") or "Unknown",
                    "Crash": complaint.get("crash"),
                    "Fire": complaint.get("fire"),
                    "Number_Injuries": complaint.get("numberOfInjuries"),
                    "Number_Deaths": complaint.get("numberOfDeaths"),
                    "Failure_Description": _redact_contact_details(description),
                    "Data_Source": "NHTSA public complaints API",
                    "Source_URL": source_url,
                    "Retrieved_On": date.today().isoformat(),
                }
            )

    data = pd.DataFrame(rows)
    if data.empty:
        raise ValueError("NHTSA returned no complaints for the selected vehicle models.")
    data = data.drop_duplicates(subset=["Complaint_ID"], keep="first")
    data["Reported_Date"] = pd.to_datetime(
        data["Reported_Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    data["Incident_Date"] = pd.to_datetime(
        data["Incident_Date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    return data


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_dataset()
    dataset.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Saved {len(dataset):,} unique public complaints to {OUTPUT_PATH}")
