"""Reusable analytics for research-funding opportunity intelligence."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

REQUIRED_COLUMNS = {
    "Grant_ID",
    "Agency",
    "Grant_Name",
    "Funding_Amount",
    "Research_Area",
    "Deadline",
    "Eligibility",
    "Duration_Months",
    "Status",
}

def validate_schema(df: pd.DataFrame) -> None:
    """Raise ValueError when required grant fields are missing."""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

def load_grants(path: str | Path) -> pd.DataFrame:
    """Load and normalize a grant CSV."""
    df = pd.read_csv(path)
    validate_schema(df)
    df = df.copy()
    df["Deadline"] = pd.to_datetime(df["Deadline"], errors="coerce")
    df["Funding_Amount"] = pd.to_numeric(df["Funding_Amount"], errors="coerce")
    df["Duration_Months"] = pd.to_numeric(df["Duration_Months"], errors="coerce")
    if df["Grant_ID"].duplicated().any():
        raise ValueError("Grant_ID values must be unique")
    return df

def funding_by_agency(df: pd.DataFrame) -> pd.DataFrame:
    """Return opportunity count and total modeled funding by agency."""
    validate_schema(df)
    return (
        df.groupby("Agency", as_index=False)
        .agg(Opportunities=("Grant_ID", "count"), Total_Funding=("Funding_Amount", "sum"))
        .sort_values("Total_Funding", ascending=False)
        .reset_index(drop=True)
    )

def funding_by_research_area(df: pd.DataFrame) -> pd.DataFrame:
    """Return opportunity count and total modeled funding by research area."""
    validate_schema(df)
    return (
        df.groupby("Research_Area", as_index=False)
        .agg(Opportunities=("Grant_ID", "count"), Total_Funding=("Funding_Amount", "sum"))
        .sort_values("Total_Funding", ascending=False)
        .reset_index(drop=True)
    )

def deadline_risk(df: pd.DataFrame, as_of: str | pd.Timestamp) -> pd.DataFrame:
    """Flag open grants by deadline urgency using an explicit analysis date."""
    validate_schema(df)
    as_of = pd.Timestamp(as_of)
    out = df.copy()
    out["Days_To_Deadline"] = (out["Deadline"] - as_of).dt.days
    out["Deadline_Risk"] = "Not Open"
    open_mask = out["Status"].eq("Open")
    out.loc[open_mask & (out["Days_To_Deadline"] < 0), "Deadline_Risk"] = "Expired"
    out.loc[open_mask & out["Days_To_Deadline"].between(0, 30), "Deadline_Risk"] = "Critical"
    out.loc[open_mask & out["Days_To_Deadline"].between(31, 60), "Deadline_Risk"] = "Watch"
    out.loc[open_mask & (out["Days_To_Deadline"] > 60), "Deadline_Risk"] = "Low"
    return out.sort_values(["Deadline_Risk", "Days_To_Deadline"]).reset_index(drop=True)

def match_researcher(
    df: pd.DataFrame,
    research_areas: Iterable[str],
    eligibility: str | None = None,
) -> pd.DataFrame:
    """Return open opportunities matching a researcher's areas and eligibility."""
    validate_schema(df)
    areas = {str(x).strip().casefold() for x in research_areas}
    out = df[
        df["Status"].eq("Open")
        & df["Research_Area"].astype(str).str.casefold().isin(areas)
    ].copy()
    if eligibility:
        out = out[
            out["Eligibility"].astype(str).str.casefold().eq(eligibility.strip().casefold())
        ]
    return out.sort_values(["Funding_Amount", "Deadline"], ascending=[False, True]).reset_index(drop=True)

def load_to_sqlite(df: pd.DataFrame, db_path: str | Path, table: str = "Grants") -> None:
    """Replace a SQLite table with the supplied normalized dataframe."""
    validate_schema(df)
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)

def sql_agency_summary(db_path: str | Path, table: str = "Grants") -> pd.DataFrame:
    """Query the agency portfolio summary directly from SQLite."""
    query = f'''
        SELECT Agency,
               COUNT(*) AS Opportunities,
               SUM(Funding_Amount) AS Total_Funding
        FROM "{table}"
        GROUP BY Agency
        ORDER BY Total_Funding DESC
    '''
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)
