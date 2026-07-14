
from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="JICT Dashboard Monitoring Produksi",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "produksi_dummy.csv"

NAVY = "#082746"
NAVY_LIGHT = "#123E68"
BLUE = "#1479B8"
CYAN = "#12A5A5"
ORANGE = "#F47C20"
GREEN = "#168C63"
RED = "#D64045"
YELLOW = "#E2A72E"
PAGE_BG = "#F4F7FB"
CARD_BORDER = "#DDE6EF"
MUTED = "#677587"


# ============================================================
# STYLING
# ============================================================

st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at 85% 5%, rgba(20,121,184,0.08), transparent 25%),
                linear-gradient(180deg, #F7FAFD 0%, {PAGE_BG} 100%);
        }}

        .block-container {{
            max-width: 1720px;
            padding-top: 1rem;
            padding-bottom: 2.5rem;
            padding-left: 1.6rem;
            padding-right: 1.6rem;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            background: linear-gradient(110deg, #061B31 0%, {NAVY} 55%, {NAVY_LIGHT} 100%);
            border-radius: 18px;
            padding: 22px 26px;
            color: white;
            box-shadow: 0 16px 38px rgba(5, 31, 57, 0.20);
            margin-bottom: 16px;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 50%;
            right: -90px;
            top: -145px;
        }}

        .brand-row {{
            display: flex;
            align-items: center;
            gap: 20px;
            position: relative;
            z-index: 1;
        }}

        .brand-mark {{
            font-size: 2rem;
            font-weight: 950;
            font-style: italic;
            letter-spacing: -0.08em;
            white-space: nowrap;
        }}

        .brand-divider {{
            width: 1px;
            height: 43px;
            background: rgba(255,255,255,0.28);
        }}

        .hero-title {{
            font-size: clamp(1.25rem, 2.1vw, 2rem);
            font-weight: 850;
            line-height: 1.15;
            letter-spacing: -0.025em;
        }}

        .hero-subtitle {{
            margin-top: 6px;
            font-size: 0.82rem;
            color: #C9D7E5;
        }}

        .prototype-badge {{
            z-index: 1;
            padding: 9px 13px;
            border-radius: 9px;
            border: 1px solid {ORANGE};
            color: #FFAA61;
            background: rgba(244,124,32,0.08);
            font-size: 0.75rem;
            font-weight: 850;
            white-space: nowrap;
            letter-spacing: 0.02em;
        }}

        .filter-card {{
            background: rgba(255,255,255,0.94);
            border: 1px solid {CARD_BORDER};
            border-radius: 15px;
            padding: 15px 18px 5px 18px;
            box-shadow: 0 8px 22px rgba(8,39,70,0.06);
            margin-bottom: 14px;
        }}

        .filter-heading {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: {NAVY};
            font-size: 0.9rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 3px;
        }}

        .filter-note {{
            color: {MUTED};
            font-size: 0.74rem;
            text-transform: none;
            letter-spacing: 0;
            font-weight: 500;
        }}

        div[data-testid="stDateInput"] input,
        div[data-baseweb="select"] > div {{
            background: #F3F6FA;
            border-color: #E1E7EF;
            min-height: 43px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 13px;
            margin: 7px 0 16px 0;
        }}

        .kpi-card {{
            position: relative;
            overflow: hidden;
            background: white;
            border: 1px solid {CARD_BORDER};
            border-radius: 15px;
            padding: 15px 17px;
            min-height: 119px;
            box-shadow: 0 8px 22px rgba(8,39,70,0.065);
        }}

        .kpi-card::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            background: var(--accent);
        }}

        .kpi-icon {{
            position: absolute;
            right: 14px;
            top: 13px;
            width: 31px;
            height: 31px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 9px;
            background: color-mix(in srgb, var(--accent) 12%, white);
            color: var(--accent);
            font-size: 1rem;
        }}

        .kpi-label {{
            color: {MUTED};
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.055em;
            margin-bottom: 8px;
            padding-right: 35px;
        }}

        .kpi-value {{
            color: {NAVY};
            font-size: 1.72rem;
            font-weight: 900;
            line-height: 1.05;
        }}

        .kpi-sub {{
            color: {MUTED};
            font-size: 0.70rem;
            margin-top: 7px;
        }}

        .section-card {{
            background: white;
            border: 1px solid {CARD_BORDER};
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 22px rgba(8,39,70,0.055);
            margin-bottom: 14px;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(90deg, {NAVY}, {NAVY_LIGHT});
            color: white;
            padding: 10px 14px;
            font-size: 0.85rem;
            font-weight: 850;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }}

        .section-header small {{
            color: #C8D7E7;
            font-size: 0.69rem;
            text-transform: none;
            font-weight: 500;
            letter-spacing: 0;
        }}

        .table-scroll {{
            width: 100%;
            max-height: 405px;
            overflow: auto;
        }}

        table.pretty-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
        }}

        table.pretty-table th {{
            position: sticky;
            top: 0;
            z-index: 2;
            background: #EAF2F9;
            color: {NAVY};
            border-bottom: 1px solid #C9D8E6;
            padding: 10px 9px;
            text-align: left;
            font-weight: 850;
            white-space: nowrap;
        }}

        table.pretty-table td {{
            padding: 9px;
            color: #2B3D50;
            border-bottom: 1px solid #E8EEF4;
            white-space: nowrap;
        }}

        table.pretty-table tbody tr:nth-child(even) {{
            background: #FAFCFE;
        }}

        table.pretty-table tbody tr:hover {{
            background: #F0F6FB;
        }}

        .num {{
            text-align: right !important;
            font-variant-numeric: tabular-nums;
        }}

        .achievement-pill,
        .status-pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 62px;
            padding: 4px 8px;
            border-radius: 999px;
            font-weight: 850;
            font-size: 0.70rem;
        }}

        .ach-good {{
            color: #0C7650;
            background: #DDF4E9;
        }}

        .ach-review {{
            color: #9A6412;
            background: #FFF0CE;
        }}

        .ach-bad {{
            color: #B23237;
            background: #FBE1E3;
        }}

        .status-final {{
            color: #0C7650;
            background: #DDF4E9;
        }}

        .status-pending {{
            color: #9A6412;
            background: #FFF0CE;
        }}

        .validation-approved {{
            color: #0C7650;
            background: #DDF4E9;
        }}

        .validation-pending {{
            color: #9A6412;
            background: #FFF0CE;
        }}

        .validation-returned {{
            color: #B23237;
            background: #FBE1E3;
        }}

        .info-box {{
            background: linear-gradient(135deg, #EAF4FB, #F5FAFE);
            border: 1px solid #CFE1EF;
            border-left: 5px solid {BLUE};
            border-radius: 13px;
            padding: 15px 16px;
            min-height: 180px;
            box-shadow: 0 7px 18px rgba(8,39,70,0.045);
            color: #2D4257;
            font-size: 0.80rem;
            line-height: 1.58;
        }}

        .info-title {{
            color: {NAVY};
            font-size: 0.84rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.045em;
            margin-bottom: 7px;
        }}

        .validation-card {{
            background: white;
            border: 1px solid {CARD_BORDER};
            border-radius: 13px;
            overflow: hidden;
            min-height: 180px;
            box-shadow: 0 7px 18px rgba(8,39,70,0.045);
        }}

        .validation-head {{
            background: #EAF2F9;
            color: {NAVY};
            padding: 9px 12px;
            font-size: 0.82rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .validation-row {{
            display: grid;
            grid-template-columns: 1.35fr 0.55fr 2.2fr;
            gap: 8px;
            align-items: center;
            padding: 9px 12px;
            border-top: 1px solid #E7EDF3;
            color: #33485D;
            font-size: 0.76rem;
        }}

        .validation-count {{
            color: {NAVY};
            font-weight: 900;
            text-align: center;
            font-variant-numeric: tabular-nums;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: white;
            border: 1px solid {CARD_BORDER};
            border-radius: 15px;
            padding: 5px;
            box-shadow: 0 8px 22px rgba(8,39,70,0.055);
        }}

        .footer-note {{
            text-align: center;
            color: {MUTED};
            font-size: 0.72rem;
            margin-top: 17px;
        }}

        .stDownloadButton button {{
            border-radius: 9px;
            border: 1px solid #C9D7E5;
            color: {NAVY};
            background: white;
            font-weight: 750;
        }}

        @media (max-width: 1100px) {{
            .kpi-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}

        @media (max-width: 720px) {{
            .hero {{
                align-items: flex-start;
                flex-direction: column;
            }}

            .brand-divider {{
                display: none;
            }}

            .brand-row {{
                align-items: flex-start;
                flex-direction: column;
                gap: 6px;
            }}

            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .filter-note {{
                display: none;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH, parse_dates=["date"])

    required_columns = {
        "date",
        "shift",
        "operator_name",
        "equipment_type",
        "actual_boxes",
        "target_boxes",
        "productive_hours",
        "shift_hours",
        "longest_nonstop_hours",
        "validation_status",
        "supervisor_status",
        "final_status",
        "safety_alert",
    }

    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(f"Kolom dataset belum lengkap: {sorted(missing)}")

    numeric_columns = [
        "actual_boxes",
        "target_boxes",
        "productive_hours",
        "shift_hours",
        "longest_nonstop_hours",
        "utilization_percentage",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0)

    return data


try:
    df = load_data()
except Exception as error:
    st.error(f"Gagal membaca data: {error}")
    st.stop()


# ============================================================
# HELPER
# ============================================================

def dominant_value(series: pd.Series) -> str:
    mode = series.mode()
    if mode.empty:
        return "-"
    return str(mode.iloc[0])


def aggregate_supervisor_validation(series: pd.Series) -> str:
    """Meringkas validasi atasan untuk setiap operator."""
    statuses = set(
        series.dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    # Jika ada satu saja data dikembalikan, operator ditandai RETURNED.
    if "Returned" in statuses:
        return "RETURNED"

    # Jika masih ada proses yang belum selesai, statusnya PENDING.
    if (
        "Pending" in statuses
        or "Waiting Foreman" in statuses
    ):
        return "PENDING"

    # APPROVED hanya jika seluruh data telah disetujui supervisor.
    if statuses and statuses == {"Approved"}:
        return "APPROVED"

    return "PENDING"


def operator_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby("operator_name", as_index=False)
        .agg(
            equipment_type=("equipment_type", dominant_value),
            boxes_actual=("actual_boxes", "sum"),
            target_boxes=("target_boxes", "sum"),
            productive_hours=("productive_hours", "sum"),
            shift_hours=("shift_hours", "sum"),
            supervisor_validation=(
                "supervisor_status",
                aggregate_supervisor_validation,
            ),
            final_count=("final_status", lambda x: (x == "FINAL").sum()),
            total_records=("record_id", "count"),
        )
    )

    summary["achievement"] = np.where(
        summary["target_boxes"] > 0,
        summary["boxes_actual"] / summary["target_boxes"] * 100,
        0,
    )

    summary["utilization"] = np.where(
        summary["shift_hours"] > 0,
        summary["productive_hours"] / summary["shift_hours"] * 100,
        0,
    )

    summary["final_status"] = np.where(
        summary["final_count"] == summary["total_records"],
        "FINAL",
        "PENDING",
    )

    return summary.sort_values(
        "boxes_actual",
        ascending=False,
    ).reset_index(drop=True)


def equipment_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby("equipment_type", as_index=False)
        .agg(
            boxes=("actual_boxes", "sum"),
            target=("target_boxes", "sum"),
            productive_hours=("productive_hours", "sum"),
        )
    )

    summary["achievement"] = np.where(
        summary["target"] > 0,
        summary["boxes"] / summary["target"] * 100,
        0,
    )

    summary["average_productivity"] = np.where(
        summary["productive_hours"] > 0,
        summary["boxes"] / summary["productive_hours"],
        0,
    )

    return summary.sort_values(
        "boxes",
        ascending=False,
    ).reset_index(drop=True)


def weighted_utilization(data: pd.DataFrame) -> float:
    total_shift = data["shift_hours"].sum()
    if total_shift <= 0:
        return 0.0
    return data["productive_hours"].sum() / total_shift * 100


def status_badge(status: str) -> str:
    css_class = (
        "status-final"
        if status == "FINAL"
        else "status-pending"
    )
    return (
        f'<span class="status-pill {css_class}">'
        f'{escape(str(status))}</span>'
    )


def achievement_badge(value: float) -> str:
    if 90 <= value <= 110:
        css_class = "ach-good"
    elif 80 <= value < 90 or 110 < value <= 120:
        css_class = "ach-review"
    else:
        css_class = "ach-bad"

    return (
        f'<span class="achievement-pill {css_class}">'
        f'{value:.1f}%</span>'
    )


def supervisor_validation_badge(status: str) -> str:
    css_map = {
        "APPROVED": "validation-approved",
        "PENDING": "validation-pending",
        "RETURNED": "validation-returned",
    }

    css_class = css_map.get(
        status,
        "validation-pending",
    )

    return (
        f'<span class="status-pill {css_class}">'
        f'{escape(str(status))}</span>'
    )


def render_operator_table(data: pd.DataFrame) -> None:
    rows = []

    for _, row in data.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(row['operator_name']))}</td>"
            f"<td>{escape(str(row['equipment_type']))}</td>"
            f"<td class='num'>{row['boxes_actual']:,.0f}</td>"
            f"<td class='num'>{row['target_boxes']:,.1f}</td>"
            f"<td class='num'>{achievement_badge(row['achievement'])}</td>"
            f"<td class='num'>{row['productive_hours']:,.1f}</td>"
            f"<td class='num'>{row['utilization']:,.1f}%</td>"
            f"<td>{supervisor_validation_badge(row['supervisor_validation'])}</td>"
            f"<td>{status_badge(row['final_status'])}</td>"
            "</tr>"
        )

    html = f"""
    <div class="section-card">
        <div class="section-header">
            <span>Ringkasan per Operator</span>
            <small>Top {len(data)} berdasarkan produksi aktual</small>
        </div>
        <div class="table-scroll">
            <table class="pretty-table">
                <thead>
                    <tr>
                        <th>Operator</th>
                        <th>Alat Dominan</th>
                        <th class="num">Boxes Aktual</th>
                        <th class="num">Target Boxes</th>
                        <th class="num">Pencapaian</th>
                        <th class="num">Jam Produktif</th>
                        <th class="num">Utilisasi</th>
                        <th>Validasi Atasan</th>
                        <th>Status Final</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_equipment_table(data: pd.DataFrame) -> None:
    rows = []

    for _, row in data.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(row['equipment_type']))}</td>"
            f"<td class='num'>{row['boxes']:,.0f}</td>"
            f"<td class='num'>{row['target']:,.1f}</td>"
            f"<td class='num'>{achievement_badge(row['achievement'])}</td>"
            f"<td class='num'>{row['average_productivity']:,.1f}</td>"
            "</tr>"
        )

    html = f"""
    <div class="section-card">
        <div class="section-header">
            <span>Ringkasan per Jenis Alat</span>
            <small>Produksi agregat periode terpilih</small>
        </div>
        <div class="table-scroll">
            <table class="pretty-table">
                <thead>
                    <tr>
                        <th>Jenis Alat</th>
                        <th class="num">Boxes / Move</th>
                        <th class="num">Target</th>
                        <th class="num">Pencapaian</th>
                        <th class="num">Produktivitas / Jam</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def kpi_card(
    label: str,
    value: str,
    subtitle: str,
    icon: str,
    accent: str,
) -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent};">'
        f'<div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{subtitle}</div>'
        f'</div>'
    )


def chart_layout(
    figure: go.Figure,
    title: str,
    height: int = 390,
) -> go.Figure:
    figure.update_layout(
        title=dict(
            text=title,
            x=0.03,
            font=dict(
                size=16,
                color=NAVY,
            ),
        ),
        height=height,
        margin=dict(
            l=28,
            r=18,
            t=62,
            b=35,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            color="#34495E",
            size=11,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
    )

    figure.update_xaxes(
        showgrid=False,
        linecolor="#D9E2EB",
        tickfont=dict(size=10),
    )

    figure.update_yaxes(
        gridcolor="#E9EEF4",
        zeroline=False,
        tickfont=dict(size=10),
    )

    return figure


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="brand-row">
            <div class="brand-mark">JICT ⚓</div>
            <div class="brand-divider"></div>
            <div>
                <div class="hero-title">
                    Dashboard Monitoring Produksi Boxes &amp; Jam Kerja Non-Stop
                </div>
                <div class="hero-subtitle">
                    Operations Administration Management · Production, utilization,
                    validation, and safety monitoring
                </div>
            </div>
        </div>
        <div class="prototype-badge">
            PROTOTYPE — SYNTHETIC / DUMMY DATA
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILTER
# ============================================================

st.markdown(
    """
    <div class="filter-card">
        <div class="filter-heading">
            <span>⚙ Filter Data</span>
            <span class="filter-note">
                Seluruh KPI, tabel, dan grafik akan mengikuti pilihan filter
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

date_min = df["date"].min().date()
date_max = df["date"].max().date()

row_1 = st.columns([1, 1, 1, 1])

with row_1[0]:
    start_date = st.date_input(
        "Tanggal Mulai",
        value=date_min,
        min_value=date_min,
        max_value=date_max,
    )

with row_1[1]:
    end_date = st.date_input(
        "Tanggal Akhir",
        value=date_max,
        min_value=date_min,
        max_value=date_max,
    )

with row_1[2]:
    selected_shift = st.selectbox(
        "Shift",
        ["Semua", *sorted(df["shift"].dropna().unique())],
    )

with row_1[3]:
    selected_equipment = st.selectbox(
        "Jenis Alat",
        ["Semua", *sorted(df["equipment_type"].dropna().unique())],
    )

row_2 = st.columns([1, 1, 1, 0.72])

with row_2[0]:
    selected_final = st.selectbox(
        "Status Final",
        ["Semua", *sorted(df["final_status"].dropna().unique())],
    )

with row_2[1]:
    selected_validation = st.selectbox(
        "Status Validasi",
        ["Semua", *sorted(df["validation_status"].dropna().unique())],
    )

with row_2[2]:
    selected_alert = st.selectbox(
        "Safety Alert",
        ["Semua", *sorted(df["safety_alert"].dropna().unique())],
    )


# ============================================================
# APPLY FILTER
# ============================================================

if start_date > end_date:
    st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    st.stop()

filtered_df = df[
    df["date"].dt.date.between(start_date, end_date)
].copy()

if selected_shift != "Semua":
    filtered_df = filtered_df[
        filtered_df["shift"] == selected_shift
    ]

if selected_equipment != "Semua":
    filtered_df = filtered_df[
        filtered_df["equipment_type"] == selected_equipment
    ]

if selected_final != "Semua":
    filtered_df = filtered_df[
        filtered_df["final_status"] == selected_final
    ]

if selected_validation != "Semua":
    filtered_df = filtered_df[
        filtered_df["validation_status"] == selected_validation
    ]

if selected_alert != "Semua":
    filtered_df = filtered_df[
        filtered_df["safety_alert"] == selected_alert
    ]

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter.")
    st.stop()

with row_2[3]:
    st.download_button(
        "⬇ Unduh Data",
        data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="jict_filtered_production.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# KPI
# ============================================================

total_actual = filtered_df["actual_boxes"].sum()
total_target = filtered_df["target_boxes"].sum()

achievement = (
    total_actual / total_target * 100
    if total_target > 0
    else 0
)

utilization = weighted_utilization(filtered_df)

alert_count = (
    filtered_df["safety_alert"]
    .eq("HARD ALERT")
    .sum()
)

kpi_html = (
    '<div class="kpi-grid">'
    + kpi_card(
        label="Total Boxes / Move",
        value=f"{total_actual:,.0f}",
        subtitle=f"{len(filtered_df):,} transaksi terfilter",
        icon="▣",
        accent=BLUE,
    )
    + kpi_card(
        label="Target Boxes / Move",
        value=f"{total_target:,.0f}",
        subtitle="Target terkoreksi kondisi operasi",
        icon="◎",
        accent=ORANGE,
    )
    + kpi_card(
        label="Pencapaian",
        value=f"{achievement:.1f}%",
        subtitle="Rentang review awal: 90–110%",
        icon="↗",
        accent=(
            GREEN
            if 90 <= achievement <= 110
            else RED
        ),
    )
    + kpi_card(
        label="Utilisasi",
        value=f"{utilization:.1f}%",
        subtitle="Jam produktif ÷ total jam shift",
        icon="◷",
        accent=(
            CYAN
            if utilization >= 80
            else YELLOW
        ),
    )
    + kpi_card(
        label="Safety Alert",
        value=f"{alert_count:,}",
        subtitle="Segmen kerja terus-menerus > 4 jam",
        icon="⚠",
        accent=RED,
    )
    + '</div>'
)

st.markdown(
    f'<div class="kpi-grid">{kpi_html}</div>',
    unsafe_allow_html=True,
)


# ============================================================
# TABLES
# ============================================================

operator_df = operator_summary(filtered_df)
equipment_df = equipment_summary(filtered_df)

top_operator_count = min(12, len(operator_df))
operator_display = operator_df.head(top_operator_count)

table_left, table_right = st.columns([1.38, 1])

with table_left:
    render_operator_table(operator_display)

with table_right:
    render_equipment_table(equipment_df)


# ============================================================
# PRINCIPLE & VALIDATION
# ============================================================

data_final = filtered_df["final_status"].eq("FINAL").sum()

pending_supervisor = filtered_df["supervisor_status"].isin(
    ["Pending", "Waiting Foreman", "Returned"]
).sum()

system_review = filtered_df["validation_status"].eq("REVIEW").sum()

segment_over_4 = filtered_df["longest_nonstop_hours"].gt(4).sum()

info_left, info_right = st.columns([1.38, 1])

with info_left:
    st.markdown(
        """
        <div class="info-box">
            <div class="info-title">Prinsip Target dan Validasi</div>
            <b>Target produksi</b> dihitung dari baseline box/jam × jam produktif
            × faktor kondisi operasi. Jam produktif merupakan jam shift setelah
            dikurangi waktu istirahat dan downtime tercatat.<br><br>
            Sistem memberi status <b>REVIEW</b> apabila pencapaian berada di luar
            rentang 90–110%, utilisasi di bawah parameter awal, data tidak lengkap,
            downtime tidak memiliki reason code, atau segmen kerja terus-menerus
            melampaui empat jam.<br><br>
            Status <b>FINAL</b> hanya digunakan setelah pemeriksaan sistem,
            persetujuan foreman, persetujuan supervisor, dan rekonsiliasi
            Operations Administration.
        </div>
        """,
        unsafe_allow_html=True,
    )

with info_right:
    st.markdown(
        f"""
        <div class="validation-card">
            <div class="validation-head">Status Validasi &amp; Keselamatan</div>
            <div class="validation-row">
                <span>Data Final</span>
                <span class="validation-count">{data_final:,}</span>
                <span>Siap digunakan untuk laporan prototype</span>
            </div>
            <div class="validation-row">
                <span>Pending Supervisor</span>
                <span class="validation-count">{pending_supervisor:,}</span>
                <span>Masih memerlukan keputusan atau klarifikasi</span>
            </div>
            <div class="validation-row">
                <span>System Review</span>
                <span class="validation-count">{system_review:,}</span>
                <span>Ditemukan penyimpangan berdasarkan rule engine</span>
            </div>
            <div class="validation-row">
                <span>Segmen &gt; 4 Jam</span>
                <span class="validation-count">{segment_over_4:,}</span>
                <span>Wajib diperiksa terhadap break dan fatigue control</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CHARTS
# ============================================================

chart_operator = operator_df.head(10).sort_values(
    "boxes_actual",
    ascending=True,
)

operator_fig = go.Figure()

operator_fig.add_trace(
    go.Bar(
        x=chart_operator["boxes_actual"],
        y=chart_operator["operator_name"],
        name="Boxes Aktual",
        orientation="h",
        marker_color=BLUE,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Aktual: %{x:,.0f}<extra></extra>"
        ),
    )
)

operator_fig.add_trace(
    go.Bar(
        x=chart_operator["target_boxes"],
        y=chart_operator["operator_name"],
        name="Target Boxes",
        orientation="h",
        marker_color=ORANGE,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Target: %{x:,.1f}<extra></extra>"
        ),
    )
)

operator_fig.update_layout(
    barmode="group",
    xaxis_title="Boxes / Move",
    yaxis_title="",
)

chart_layout(
    operator_fig,
    "Boxes Aktual vs Target — Top 10 Operator",
    430,
)

equipment_chart_df = equipment_df.sort_values(
    "boxes",
    ascending=True,
)

equipment_fig = go.Figure()

equipment_fig.add_trace(
    go.Bar(
        x=equipment_chart_df["boxes"],
        y=equipment_chart_df["equipment_type"],
        name="Boxes Aktual",
        orientation="h",
        marker_color=BLUE,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Aktual: %{x:,.0f}<extra></extra>"
        ),
    )
)

equipment_fig.add_trace(
    go.Bar(
        x=equipment_chart_df["target"],
        y=equipment_chart_df["equipment_type"],
        name="Target Boxes",
        orientation="h",
        marker_color=ORANGE,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Target: %{x:,.1f}<extra></extra>"
        ),
    )
)

equipment_fig.update_layout(
    barmode="group",
    xaxis_title="Boxes / Move",
    yaxis_title="",
)

chart_layout(
    equipment_fig,
    "Boxes Aktual vs Target — Jenis Alat",
    430,
)

chart_left, chart_right = st.columns([1.38, 1])

with chart_left:
    st.plotly_chart(
        operator_fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

with chart_right:
    st.plotly_chart(
        equipment_fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-note">
        ⚓ Prototype menggunakan data sintetis/dummy.
        Angka dan hasil analisis tidak merepresentasikan data operasional aktual JICT.
    </div>
    """,
    unsafe_allow_html=True,
)
