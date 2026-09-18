"""Generate the deterministic synthetic grant dataset used by the project."""
from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd

SEED = 42
BASE_DATE = datetime(2026, 6, 19)

AGENCIES = ["DBT", "DST", "BIRAC", "ICMR", "CSIR", "ANRF", "WHO", "NIH", "Gates Foundation"]
AREAS = ["Biotechnology", "Genomics", "Vaccines", "Drug Discovery", "Public Health", "Bioinformatics", "Cancer Research", "Immunology", "Agricultural Biotechnology", "Precision Medicine"]
TITLES = ["Innovative Research Grant", "Young Investigator Award", "Precision Medicine Initiative", "Translational Research Program", "Health Innovation Program", "Strategic Research Scheme", "Genomics Research Fund", "International Collaboration Grant"]
ELIGIBILITY = ["Faculty", "Universities", "Research Institutes", "Faculty + Scientists", "Startups"]
STATUS = ["Open", "Under Review", "Closed"]

def generate_grants(n=150):
    rng = random.Random(SEED)
    records = []
    for grant_id in range(1, n + 1):
        records.append({
            "Grant_ID": grant_id,
            "Agency": rng.choice(AGENCIES),
            "Grant_Name": rng.choice(TITLES),
            "Funding_Amount": rng.randint(10, 500) * 100000,
            "Research_Area": rng.choice(AREAS),
            "Deadline": BASE_DATE + timedelta(days=rng.randint(30, 365)),
            "Eligibility": rng.choice(ELIGIBILITY),
            "Duration_Months": rng.choice([12, 24, 36, 48, 60]),
            "Status": rng.choice(STATUS),
        })
    df = pd.DataFrame(records)
    df["Deadline"] = pd.to_datetime(df["Deadline"]).dt.strftime("%Y-%m-%d")
    return df

if __name__ == "__main__":
    out = Path("data/raw/grants.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    generate_grants().to_csv(out, index=False)
    print(f"Wrote {len(generate_grants())} grants to {out}")
