import pandas as pd
import pytest

from src.analytics import (
    deadline_risk,
    funding_by_agency,
    load_grants,
    match_researcher,
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
    df = sample_df().drop(columns=["Agency"])
    with pytest.raises(ValueError):
        validate_schema(df)

def test_funding_by_agency_sorts_by_total_funding():
    result = funding_by_agency(sample_df())
    assert result.iloc[0]["Agency"] == "NIH"
    assert result.iloc[1]["Total_Funding"] == 1_500_000

def test_deadline_risk_uses_explicit_as_of_date():
    result = deadline_risk(sample_df(), "2026-06-01")
    risks = dict(zip(result["Grant_ID"], result["Deadline_Risk"]))
    assert risks[1] == "Watch"
    assert risks[2] == "Low"
    assert risks[3] == "Not Open"

def test_match_researcher_returns_only_open_matching_area():
    result = match_researcher(sample_df(), ["Genomics"])
    assert result["Grant_ID"].tolist() == [2]

def test_load_grants_normalizes_types(tmp_path):
    path = tmp_path / "grants.csv"
    sample_df().to_csv(path, index=False)
    result = load_grants(path)
    assert pd.api.types.is_datetime64_any_dtype(result["Deadline"])
    assert pd.api.types.is_numeric_dtype(result["Funding_Amount"])
