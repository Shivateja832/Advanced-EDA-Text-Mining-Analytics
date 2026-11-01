"""Generate deterministic, clearly labeled product-service events for demonstration."""

from __future__ import annotations

from pathlib import Path
import random

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SEED = 20261030

ISSUE_TEMPLATES = {
    "Motor / bearing": [
        "Motor bearing makes a loud rattling noise during the spin cycle.",
        "Drive motor vibrates heavily and the bearing feels rough.",
        "Motor assembly stops under load; technician found bearing wear.",
        "Customer reports grinding near the drive motor after regular use.",
        "Bearing noise increases at high speed and the motor trips offline.",
    ],
    "Battery / charging": [
        "Battery does not hold charge and charging indicator flashes.",
        "Unit will not charge with the supplied charger; battery drains quickly.",
        "Battery temperature rises during charging and charge stops early.",
        "Charging port is intermittent and battery status drops unexpectedly.",
    ],
    "Water leak / pump seal": [
        "Water leaks from the pump seal during the drain cycle.",
        "Customer reports a leak below the inlet valve after each wash.",
        "Pump housing is wet and the water seal appears damaged.",
        "Drain pump runs but a small leak forms around the hose connector.",
    ],
    "Firmware / control": [
        "Control display freezes after firmware update and needs a reboot.",
        "Unit restarts during the cycle after the latest software update.",
        "Firmware update fails and the control application shows an error.",
        "Controller becomes unresponsive until the device is power cycled.",
    ],
    "Connectivity": [
        "Bluetooth pairing drops repeatedly when the mobile application opens.",
        "Wi-Fi connection is intermittent and remote status is unavailable.",
        "Network signal is lost after the device reconnects from sleep.",
        "Customer cannot pair the unit with the application over Bluetooth.",
    ],
    "Thermal / fan": [
        "Cooling fan stops and the enclosure becomes unusually hot.",
        "Temperature warning appears after the cooling fan slows down.",
        "Unit overheats during extended operation; ventilation fan is noisy.",
        "Fan motor is weak and warm air is not being exhausted.",
    ],
}

BASE_ISSUE_WEIGHTS = {
    "Motor / bearing": 0.25,
    "Battery / charging": 0.19,
    "Water leak / pump seal": 0.17,
    "Firmware / control": 0.15,
    "Connectivity": 0.13,
    "Thermal / fan": 0.11,
}

MODEL_BY_ISSUE = {
    "Motor / bearing": ["AeroWash X4", "AeroWash X4", "AeroWash X4", "AeroWash X2", "AeroDry D1"],
    "Battery / charging": ["VoltGo S2", "VoltGo S2", "VoltGo S2", "VoltGo S1", "AeroDry D1"],
    "Water leak / pump seal": ["AeroWash X2", "AeroWash X4", "AquaClean P3", "AquaClean P3"],
    "Firmware / control": ["VoltGo S2", "AeroWash X4", "AquaClean P3", "AeroDry D1"],
    "Connectivity": ["VoltGo S2", "AeroWash X4", "AquaClean P3", "AeroDry D1"],
    "Thermal / fan": ["AeroDry D1", "AeroDry D1", "VoltGo S2", "AeroWash X4"],
}

MODEL_ACTIVE_UNITS = {
    "AeroWash X4": 18500,
    "AeroWash X2": 14200,
    "AeroDry D1": 11900,
    "VoltGo S2": 9800,
    "VoltGo S1": 7200,
    "AquaClean P3": 8600,
}


def _monthly_issue_weights(month: pd.Period) -> dict[str, float]:
    """Create a planted but plausible increase in one synthetic failure mode."""
    weights = BASE_ISSUE_WEIGHTS.copy()
    if month >= pd.Period("2025-04", freq="M"):
        weights["Motor / bearing"] += 0.19
        weights["Connectivity"] -= 0.035
        weights["Firmware / control"] -= 0.045
        weights["Battery / charging"] -= 0.04
        weights["Thermal / fan"] -= 0.035
        weights["Water leak / pump seal"] -= 0.035
    return weights


def build_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return generated event rows and an entity reference table."""
    rng = np.random.default_rng(SEED)
    random.seed(SEED)
    records = []
    start = pd.Period("2024-01", freq="M")
    months = pd.period_range(start=start, end="2026-06", freq="M")
    issue_names = list(BASE_ISSUE_WEIGHTS)

    for month in months:
        weights = _monthly_issue_weights(month)
        probabilities = np.array([weights[name] for name in issue_names], dtype=float)
        probabilities /= probabilities.sum()
        monthly_volume = int(rng.integers(105, 146))
        month_start = month.start_time
        month_end = month.end_time.normalize()

        for _ in range(monthly_volume):
            issue = str(rng.choice(issue_names, p=probabilities))
            model = str(rng.choice(MODEL_BY_ISSUE[issue]))
            event_date = month_start + pd.Timedelta(
                days=int(rng.integers(0, (month_end - month_start).days + 1))
            )
            severity = str(
                rng.choice(
                    ["Critical", "High", "Medium", "Low"],
                    p=(
                        [0.12, 0.39, 0.36, 0.13]
                        if issue == "Motor / bearing" and month >= pd.Period("2025-04", freq="M")
                        else [0.06, 0.29, 0.43, 0.22]
                    ),
                )
            )

            if issue == "Motor / bearing":
                cohort = month >= pd.Period("2025-04", freq="M") and model == "AeroWash X4"
                lot_choices = ["L24-C", "L25-A", "L25-B", "L25-C", "L26-A"]
                if cohort:
                    lot = str(rng.choice(lot_choices, p=[0.06, 0.58, 0.20, 0.10, 0.06]))
                else:
                    lot = str(rng.choice(lot_choices, p=[0.38, 0.12, 0.16, 0.18, 0.16]))
            else:
                lot = str(rng.choice(["L24-C", "L25-A", "L25-B", "L25-C", "L26-A"]))

            model_units = MODEL_ACTIVE_UNITS[model]
            active_units = int(model_units * (1 + 0.006 * (month.ordinal - start.ordinal)))
            if issue == "Motor / bearing" and month >= pd.Period("2025-04", freq="M") and model == "AeroWash X4":
                active_units = int(active_units * 1.08)

            if issue == "Motor / bearing":
                component = str(rng.choice(["Drive motor", "Motor bearing", "Motor assembly"]))
                root_context = (
                    "Service notes mention repeat bearing wear in the affected build cohort."
                    if month >= pd.Period("2025-04", freq="M") and model == "AeroWash X4"
                    else "Service notes describe an isolated motor noise or wear concern."
                )
            elif issue == "Battery / charging":
                component = str(rng.choice(["Battery pack", "Charging port", "Power adapter"]))
                root_context = "Service notes request battery and charger diagnostics."
            elif issue == "Water leak / pump seal":
                component = str(rng.choice(["Drain pump", "Inlet valve", "Pump seal", "Hose connector"]))
                root_context = "Service notes request leak-path and seal inspection."
            elif issue == "Firmware / control":
                component = str(rng.choice(["Control board", "Firmware", "Display"]))
                root_context = "Service notes request controller and software-version review."
            elif issue == "Connectivity":
                component = str(rng.choice(["Wireless module", "Bluetooth module", "Antenna"]))
                root_context = "Service notes request pairing and network-condition checks."
            else:
                component = str(rng.choice(["Cooling fan", "Fan motor", "Thermal sensor"]))
                root_context = "Service notes request airflow and temperature checks."

            record = {
                "Event_ID": f"EVT-{len(records) + 1:06d}",
                "Reported_Date": event_date.date().isoformat(),
                "Product_Model": model,
                "Product_Family": (
                    "Home Care" if model.startswith("Aero")
                    else "Portable Power" if model.startswith("Volt")
                    else "Water Care"
                ),
                "Component": component,
                "Manufacturing_Lot": lot,
                "Firmware_Version": str(
                    rng.choice(["1.3.8", "1.4.0", "1.4.2", "1.5.0", "1.5.3"])
                ),
                "Region": str(rng.choice(["North", "South", "East", "West", "Central"])),
                "Sales_Channel": str(rng.choice(["Retail", "Direct", "Distributor", "Service Partner"])),
                "Severity": severity,
                "Days_In_Service": int(rng.integers(1, 1500)),
                "Warranty_Status": str(rng.choice(["In Warranty", "Out of Warranty"], p=[0.76, 0.24])),
                "Active_Units": active_units,
                "Estimated_Repair_Cost_USD": round(
                    float(np.clip(rng.normal(145 if severity in {"Critical", "High"} else 82, 28), 25, 390)), 2
                ),
                "Failure_Description": (
                    f"{random.choice(ISSUE_TEMPLATES[issue])} {root_context}"
                ),
                "Synthetic_Data_Notice": "Synthetic - generated for demonstration; not real customer data",
            }
            records.append(record)

    data = pd.DataFrame(records)
    # Add a small number of deliberate quality issues for cleaning validation.
    data.loc[11, "Region"] = None
    data.loc[55, "Estimated_Repair_Cost_USD"] = np.nan
    data.loc[107, "Firmware_Version"] = " 1.4.2 "
    data.loc[203, "Sales_Channel"] = " "
    data.loc[317, "Product_Model"] = None
    data.loc[601, "Region"] = " n/a "
    data = pd.concat([data, data.iloc[[40, 120, 400, 900, 1400]].copy()], ignore_index=True)

    entity_rows = [
        ("Component", "Motor", "Drive motor, motor assembly"),
        ("Component", "Bearing", "Motor bearing, bearing wear"),
        ("Component", "Battery", "Battery pack, battery drain"),
        ("Component", "Charger", "Power adapter, charging port"),
        ("Component", "Pump", "Drain pump, pump seal"),
        ("Component", "Valve", "Inlet valve"),
        ("Component", "Fan", "Cooling fan, fan motor"),
        ("Component", "Sensor", "Thermal sensor"),
        ("Component", "Control board", "Controller, circuit board"),
        ("Connectivity", "Wi-Fi", "Wireless module, network"),
        ("Connectivity", "Bluetooth", "Pairing, antenna"),
        ("Failure signal", "Leak", "Water leakage, seal damage"),
        ("Failure signal", "Overheating", "High temperature, thermal warning"),
        ("Failure signal", "Firmware", "Software update, reboot, frozen display"),
    ]
    entities = pd.DataFrame(
        entity_rows, columns=["Entity_Group", "Example_Entity", "Related_Terms"]
    )
    return data, entities


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data, entities = build_dataset()
    data_path = DATA_DIR / "synthetic_product_service_events.csv"
    entities_path = DATA_DIR / "synthetic_entity_examples.xlsx"
    data.to_csv(data_path, index=False, encoding="utf-8-sig")
    entities.to_excel(entities_path, index=False)
    print(f"Generated {len(data):,} synthetic records: {data_path}")
    print(f"Generated {len(entities):,} entity examples: {entities_path}")
    print("All records are synthetic and are not real customer/product reports.")


if __name__ == "__main__":
    main()
