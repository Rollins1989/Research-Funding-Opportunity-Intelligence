import pandas as pd
from src.analysis import agency_summary, area_summary, deadline_risk, researcher_matches

def sample():
    return pd.DataFrame({
        "Grant_ID": [1, 2, 3],
        "Agency": ["A", "A", "B"],
        "Funding_Amount": [100, 200, 300],
        "Research_Area": ["Bio", "Cancer", "Bio"],
        "Deadline": pd.to_datetime(["2026-06-25", "2026-07-30", "2026-06-20"]),
        "Status": ["Open", "Closed", "Under Review"],
        "Days_Left": [6, 41, 1],
    })

def test_agency_summary():
    out = agency_summary(sample())
    assert out.iloc[0]["Agency"] == "A"
    assert out.iloc[0]["Total_Funding"] == 300

def test_area_summary():
    out = area_summary(sample())
    assert out.iloc[0]["Research_Area"] == "Bio"

def test_deadline_risk_excludes_closed():
    out = deadline_risk(sample(), window=30)
    assert set(out["Grant_ID"]) == {1, 3}

def test_researcher_matches_excludes_closed():
    out = researcher_matches(sample(), "Bio")
    assert list(out["Grant_ID"]) == [3, 1]
