import sqlite3

import pandas as pd
import pytest

from src.analytics import (
    deadline_risk,
    funding_by_agency,
    funding_by_research_area,
    load_grants,
    load_to_sqlite,
    match_researcher,
    sql_agency_summary,
    validate_schema,
)

def sample_df():
    return pd.DataFrame(
        [
            [1, "DBT", "Grant A", 1000000, "Biotechnology", "2026-07-01", "Faculty", 24, "Open"],
            [2, "NIH", "Grant B", 2000000, "Genomics", "2026-12-01", "Universities", 36, "Open"],
            [3, "DBT", "Grant C", 500000, "Genomics", "2026-05-01", "Faculty", 12, "Closed"],
        ],
        columns=[
            "Grant_ID", "Agency", "Grant_Name", "Funding_Amount",
            "Research_Area", "Deadline", "Eligibility", "Duration_Months", "Status",
        ],
    ).assign(Deadline=lambda x: pd.to_datetime(x["Deadline"]))

def test_validate_schema_rejects_missing_column():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_schema(sample_df().drop(columns=["Agency"]))

def test_funding_by_agency_sorts_by_total_funding():
    result = funding_by_agency(sample_df())
    assert result.iloc[0]["Agency"] == "NIH"
    assert result.iloc[1]["Total_Funding"] == 1_500_000

def test_funding_by_research_area():
    result = funding_by_research_area(sample_df())
    assert result.iloc[0]["Research_Area"] == "Genomics"
    assert result.iloc[0]["Total_Funding"] == 2_500_000

def test_deadline_risk_uses_explicit_as_of_date():
    result = deadline_risk(sample_df(), "2026-06-01")
    risks = dict(zip(result["Grant_ID"], result["Deadline_Risk"]))
    assert risks[1] == "Critical"
    assert risks[2] == "Low"
    assert risks[3] == "Not Open"

def test_match_researcher_returns_only_open_matching_area():
    result = match_researcher(sample_df(), ["Genomics"])
    assert result["Grant_ID"].tolist() == [2]

def test_match_researcher_honors_eligibility_case_insensitively():
    result = match_researcher(sample_df(), ["genomics"], "universities")
    assert result["Grant_ID"].tolist() == [2]

def test_load_grants_normalizes_types_and_rejects_duplicates(tmp_path):
    path = tmp_path / "grants.csv"
    sample_df().to_csv(path, index=False)
    result = load_grants(path)
    assert pd.api.types.is_datetime64_any_dtype(result["Deadline"])
    assert pd.api.types.is_numeric_dtype(result["Funding_Amount"])

    duplicate = sample_df().copy()
    duplicate.loc[1, "Grant_ID"] = 1
    duplicate.to_csv(path, index=False)
    with pytest.raises(ValueError, match="Grant_ID"):
        load_grants(path)

def test_sqlite_round_trip(tmp_path):
    db = tmp_path / "grants.db"
    load_to_sqlite(sample_df(), db)
    result = sql_agency_summary(db)
    assert result.iloc[0]["Agency"] == "NIH"
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM Grants").fetchone()[0] == 3
