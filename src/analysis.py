"""Reusable grant analytics functions."""
import sqlite3
from pathlib import Path
import pandas as pd

def load_grants(path):
    df = pd.read_csv(path, parse_dates=["Deadline"])
    df["Days_Left"] = (df["Deadline"] - pd.Timestamp("2026-06-19")).dt.days
    return df

def agency_summary(df):
    return df.groupby("Agency", as_index=False).agg(
        Grants=("Grant_ID", "count"),
        Total_Funding=("Funding_Amount", "sum"),
        Average_Funding=("Funding_Amount", "mean"),
    ).sort_values("Total_Funding", ascending=False)

def area_summary(df):
    return df.groupby("Research_Area", as_index=False).agg(
        Grants=("Grant_ID", "count"),
        Total_Funding=("Funding_Amount", "sum"),
    ).sort_values("Total_Funding", ascending=False)

def deadline_risk(df, window=30):
    return df[(df["Status"] != "Closed") & (df["Days_Left"].between(0, window))].sort_values("Days_Left")

def researcher_matches(df, research_area):
    return df[(df["Research_Area"] == research_area) & (df["Status"] != "Closed")].sort_values(["Days_Left", "Funding_Amount"], ascending=[True, False])

def write_sqlite(df, db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("Grants", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_grants_agency ON Grants(Agency)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_grants_deadline ON Grants(Deadline)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_grants_area ON Grants(Research_Area)")
