from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

RANDOM_STATE = 42
rng = np.random.default_rng(RANDOM_STATE)

OUTPUT_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2026-01-01"
NUMBER_OF_DAYS = 30
NUMBER_OF_OPERATORS = 30

SHIFT_CONFIG = {
    "Shift 1": 8,
    "Shift 2": 8,
    "Shift 3": 8,
}

EQUIPMENT_CONFIG = {
    "Quay Crane": {"prefix": "QC", "count": 8, "baseline": 28, "unit": "box"},
    "RTGC": {"prefix": "RTG", "count": 12, "baseline": 20, "unit": "box"},
    "Reach Stacker": {"prefix": "RS", "count": 5, "baseline": 14, "unit": "box"},
    "Forklift": {"prefix": "FL", "count": 6, "baseline": 10, "unit": "box"},
    "Head Truck": {"prefix": "HT", "count": 18, "baseline": 10, "unit": "move"},
}

CONDITION_FACTORS = {
    "Normal": 1.00,
    "Kepadatan sedang": 0.90,
    "Kepadatan tinggi": 0.80,
    "Pembatasan alat": 0.75,
    "Penghentian resmi": 0.00,
}
CONDITION_PROBABILITIES = [0.62, 0.20, 0.10, 0.06, 0.02]

DOWNTIME_REASONS = [
    "Equipment breakdown",
    "Waiting job",
    "Yard congestion",
    "System interruption",
    "Weather",
    "Operator change",
]


def create_operator_master() -> pd.DataFrame:
    records = []
    for number in range(1, NUMBER_OF_OPERATORS + 1):
        records.append({
            "operator_id": f"OPR-{number:03d}",
            "operator_name": f"Operator {number:03d}",
            "worker_status": rng.choice(["Tetap", "Outsourcing"], p=[0.25, 0.75]),
            "vendor": rng.choice(["Vendor A", "Vendor B", "Vendor C"]),
        })
    return pd.DataFrame(records)


def create_equipment_master() -> pd.DataFrame:
    records = []
    for equipment_type, cfg in EQUIPMENT_CONFIG.items():
        for number in range(1, cfg["count"] + 1):
            records.append({
                "equipment_type": equipment_type,
                "equipment_id": f"{cfg['prefix']}-{number:02d}",
                "baseline_per_hour": cfg["baseline"],
                "production_unit": cfg["unit"],
            })
    return pd.DataFrame(records)


def determine_validation(
    achievement: float,
    utilization: float,
    nonstop_hours: float,
    downtime_minutes: float,
    downtime_reason: str,
) -> tuple[str, str, str]:
    flags = []
    if achievement < 90:
        flags.append("produksi_bawah_target")
    if achievement > 110:
        flags.append("produksi_di_atas_batas")
    if utilization < 80:
        flags.append("utilisasi_rendah")
    if nonstop_hours > 4:
        flags.append("nonstop_lebih_4_jam")
    if downtime_minutes > 30 and downtime_reason == "Tidak ada":
        flags.append("downtime_tanpa_alasan")

    validation_status = "REVIEW" if flags else "PASS"
    safety_alert = "HARD ALERT" if nonstop_hours > 4 else "SAFE"
    data_quality_flag = "|".join(flags) if flags else "OK"
    return validation_status, safety_alert, data_quality_flag


def determine_approval(validation_status: str) -> tuple[str, str, str]:
    if validation_status == "PASS":
        foreman = rng.choice(["Approved", "Pending", "Returned"], p=[0.90, 0.07, 0.03])
    else:
        foreman = rng.choice(["Approved", "Pending", "Returned"], p=[0.55, 0.30, 0.15])

    if foreman == "Approved":
        supervisor = rng.choice(["Approved", "Pending", "Returned"], p=[0.88, 0.08, 0.04])
    else:
        supervisor = "Waiting Foreman"

    final_status = (
        "FINAL"
        if validation_status == "PASS" and foreman == "Approved" and supervisor == "Approved"
        else "PENDING"
    )
    return foreman, supervisor, final_status


def create_production_data(operators: pd.DataFrame, equipment: pd.DataFrame) -> pd.DataFrame:
    dates = pd.date_range(START_DATE, periods=NUMBER_OF_DAYS, freq="D")
    records = []
    record_number = 1

    for date in dates:
        weekend_factor = 0.90 if date.dayofweek >= 5 else 1.00

        for shift_name, shift_hours in SHIFT_CONFIG.items():
            active_count = int(rng.integers(10, 19))

            selected_operators = operators.sample(
                n=active_count,
                replace=False,
                random_state=int(rng.integers(0, 1_000_000)),
            ).reset_index(drop=True)

            selected_equipment = equipment.sample(
                n=active_count,
                replace=False,
                random_state=int(rng.integers(0, 1_000_000)),
            ).reset_index(drop=True)

            for idx in range(active_count):
                operator = selected_operators.iloc[idx]
                unit = selected_equipment.iloc[idx]

                condition = rng.choice(list(CONDITION_FACTORS), p=CONDITION_PROBABILITIES)
                condition_factor = CONDITION_FACTORS[condition]

                break_hours = float(np.clip(rng.normal(0.75, 0.15), 0.25, 1.25))
                downtime_minutes = float(np.clip(rng.gamma(1.7, 15), 0, 180))
                if condition == "Penghentian resmi":
                    downtime_minutes = float(rng.uniform(240, 420))

                productive_hours = max(0.0, shift_hours - break_hours - downtime_minutes / 60)
                baseline = float(unit["baseline_per_hour"])
                target = baseline * productive_hours * condition_factor * weekend_factor

                probability = rng.random()
                if probability < 0.05:
                    production_factor = float(rng.uniform(0.60, 0.85))
                elif probability < 0.08:
                    production_factor = float(rng.uniform(1.15, 1.30))
                else:
                    production_factor = float(np.clip(rng.normal(1.00, 0.07), 0.85, 1.15))

                actual = max(0, int(round(target * production_factor)))
                achievement = actual / target * 100 if target > 0 else 0.0
                utilization = productive_hours / shift_hours * 100 if shift_hours > 0 else 0.0

                nonstop_hours = (
                    float(rng.uniform(4.1, 5.6))
                    if rng.random() < 0.04
                    else float(np.clip(rng.normal(3.0, 0.55), 1.2, 4.0))
                )

                downtime_reason = "Tidak ada" if downtime_minutes < 10 else str(rng.choice(DOWNTIME_REASONS))
                validation, safety, quality_flag = determine_validation(
                    achievement,
                    utilization,
                    nonstop_hours,
                    downtime_minutes,
                    downtime_reason,
                )
                foreman, supervisor, final_status = determine_approval(validation)

                records.append({
                    "record_id": f"TRX-{record_number:07d}",
                    "date": date.strftime("%Y-%m-%d"),
                    "shift": shift_name,
                    "operator_id": operator["operator_id"],
                    "operator_name": operator["operator_name"],
                    "worker_status": operator["worker_status"],
                    "vendor": operator["vendor"],
                    "equipment_type": unit["equipment_type"],
                    "equipment_id": unit["equipment_id"],
                    "production_unit": unit["production_unit"],
                    "job_type": rng.choice(["Loading", "Discharge"]),
                    "condition": condition,
                    "condition_factor": round(condition_factor, 2),
                    "shift_hours": shift_hours,
                    "break_hours": round(break_hours, 2),
                    "downtime_minutes": round(downtime_minutes, 1),
                    "downtime_reason": downtime_reason,
                    "productive_hours": round(productive_hours, 2),
                    "longest_nonstop_hours": round(nonstop_hours, 2),
                    "baseline_per_hour": baseline,
                    "target_production": round(target, 1),
                    "actual_production": actual,
                    "target_boxes": round(target, 1),
                    "actual_boxes": actual,
                    "achievement_percentage": round(achievement, 1),
                    "utilization_percentage": round(utilization, 1),
                    "validation_status": validation,
                    "foreman_status": foreman,
                    "supervisor_status": supervisor,
                    "final_status": final_status,
                    "safety_alert": safety,
                    "data_quality_flag": quality_flag,
                })
                record_number += 1

    return pd.DataFrame(records)


def inject_anomalies(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()

    no_reason_idx = result.sample(frac=0.02, random_state=101).index
    result.loc[no_reason_idx, "downtime_minutes"] = rng.uniform(45, 150, len(no_reason_idx)).round(1)
    result.loc[no_reason_idx, "downtime_reason"] = "Tidak ada"
    result.loc[no_reason_idx, "validation_status"] = "REVIEW"
    result.loc[no_reason_idx, "final_status"] = "PENDING"
    result.loc[no_reason_idx, "data_quality_flag"] = "downtime_tanpa_alasan"

    nonstop_idx = result.sample(frac=0.02, random_state=102).index
    result.loc[nonstop_idx, "longest_nonstop_hours"] = rng.uniform(4.1, 5.8, len(nonstop_idx)).round(2)
    result.loc[nonstop_idx, "safety_alert"] = "HARD ALERT"
    result.loc[nonstop_idx, "validation_status"] = "REVIEW"
    result.loc[nonstop_idx, "final_status"] = "PENDING"
    result.loc[nonstop_idx, "data_quality_flag"] = "nonstop_lebih_4_jam"

    duplicate_count = max(1, int(len(result) * 0.01))
    duplicates = result.sample(n=duplicate_count, random_state=103).copy()
    duplicates["record_id"] = [f"DUP-{n:07d}" for n in range(1, duplicate_count + 1)]
    duplicates["data_quality_flag"] = "duplicate_transaction"
    duplicates["validation_status"] = "REVIEW"
    duplicates["final_status"] = "PENDING"

    return pd.concat([result, duplicates], ignore_index=True)


def create_audit_trail(production_data: pd.DataFrame) -> pd.DataFrame:
    sample_size = min(120, len(production_data))
    sample = production_data.sample(n=sample_size, random_state=104).reset_index(drop=True)
    changed_at = pd.to_datetime(sample["date"]) + pd.to_timedelta(rng.integers(8, 23, sample_size), unit="h")

    return pd.DataFrame({
        "audit_id": [f"AUD-{n:05d}" for n in range(1, sample_size + 1)],
        "record_id": sample["record_id"],
        "changed_at": changed_at,
        "field_changed": rng.choice(
            ["actual_production", "downtime_minutes", "downtime_reason", "break_hours"],
            size=sample_size,
        ),
        "old_value": rng.integers(0, 100, size=sample_size),
        "new_value": rng.integers(0, 100, size=sample_size),
        "changed_by": rng.choice(
            ["Foreman 01", "Foreman 02", "Supervisor 01", "Operations Admin"],
            size=sample_size,
        ),
        "change_reason": rng.choice(
            ["Koreksi input", "Rekonsiliasi log alat", "Validasi kondisi lapangan", "Perbaikan reason code"],
            size=sample_size,
        ),
        "approval_status": rng.choice(["Approved", "Pending", "Returned"], p=[0.82, 0.12, 0.06], size=sample_size),
    })


def validate_data(data: pd.DataFrame) -> None:
    required = {
        "record_id", "date", "shift", "operator_id", "equipment_id",
        "actual_boxes", "target_boxes", "achievement_percentage",
        "utilization_percentage", "validation_status", "safety_alert", "final_status",
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Kolom wajib hilang: {sorted(missing)}")
    if data["record_id"].duplicated().any():
        raise ValueError("record_id harus unik")
    if (data["actual_boxes"] < 0).any() or (data["target_boxes"] < 0).any():
        raise ValueError("Nilai produksi tidak boleh negatif")
    if (~data["utilization_percentage"].between(0, 100)).any():
        raise ValueError("Utilisasi harus 0–100")


def main() -> None:
    operators = create_operator_master()
    equipment = create_equipment_master()
    production = inject_anomalies(create_production_data(operators, equipment))
    audit = create_audit_trail(production)
    validate_data(production)

    production.to_csv(OUTPUT_DIR / "produksi_dummy.csv", index=False, encoding="utf-8-sig")
    operators.to_csv(OUTPUT_DIR / "operator_master_dummy.csv", index=False, encoding="utf-8-sig")
    equipment.to_csv(OUTPUT_DIR / "equipment_master_dummy.csv", index=False, encoding="utf-8-sig")
    audit.to_csv(OUTPUT_DIR / "audit_trail_dummy.csv", index=False, encoding="utf-8-sig")

    total_actual = production["actual_boxes"].sum()
    total_target = production["target_boxes"].sum()
    summary = pd.DataFrame({
        "KPI": [
            "Jumlah transaksi", "Jumlah operator", "Jumlah equipment",
            "Total produksi aktual", "Total target", "Pencapaian total (%)",
            "Utilisasi rata-rata (%)", "System review", "Hard alert",
            "Data final", "Data pending",
        ],
        "Nilai": [
            len(production),
            production["operator_id"].nunique(),
            production["equipment_id"].nunique(),
            total_actual,
            round(total_target, 1),
            round(total_actual / total_target * 100 if total_target else 0, 1),
            round(production["utilization_percentage"].mean(), 1),
            int(production["validation_status"].eq("REVIEW").sum()),
            int(production["safety_alert"].eq("HARD ALERT").sum()),
            int(production["final_status"].eq("FINAL").sum()),
            int(production["final_status"].eq("PENDING").sum()),
        ],
    })
    summary.to_csv(OUTPUT_DIR / "summary_dummy.csv", index=False, encoding="utf-8-sig")

    print("DATA DUMMY BERHASIL DIBUAT")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
