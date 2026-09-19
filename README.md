# Research Funding Opportunity Intelligence

[![CI](https://github.com/Rollins1989/Research-Funding-Opportunity-Intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/Rollins1989/Research-Funding-Opportunity-Intelligence/actions/workflows/ci.yml)
[![Dashboard Smoke Test](https://github.com/Rollins1989/Research-Funding-Opportunity-Intelligence/actions/workflows/dashboard.yml/badge.svg)](https://github.com/Rollins1989/Research-Funding-Opportunity-Intelligence/actions/workflows/dashboard.yml)


An end-to-end **research-funding analytics portfolio project** that turns structured grant-opportunity data into agency portfolio analysis, research-area intelligence, deadline-risk monitoring, researcher-to-grant matching, SQL analytics, and executive reporting.

> **Data disclaimer:** This repository uses synthetic/demo grant records for analytics practice. Funding amounts, deadlines, agencies, and opportunity names are not live funding announcements.

## Why this project exists

Research development teams need more than a list of grants. They need to answer:

- Which agencies represent the largest modeled funding portfolios?
- Which research areas receive the most modeled funding?
- Which open opportunities have deadlines requiring attention?
- Which opportunities match a researcher's research area and eligibility?
- How can the same analysis be reproduced in SQL and Python?

This project demonstrates that workflow with a clean separation between **data generation**, **reusable analytics**, **testing**, **SQL**, the notebook/reporting layer, and an interactive Streamlit dashboard.

## Project architecture

```text
Research-Funding-Opportunity-Intelligence/
├── data/
│   └── raw/                         # source/demo data
├── src/
│   ├── generate_data.py             # deterministic synthetic data generator
│   └── analytics.py                 # reusable analytics functions
├── tests/
│   └── test_analytics.py            # automated validation
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions test pipeline
├── Research Funding Opportunity Intelligence.ipynb
├── Funding_Intelligence_Report.xlsx
├── Director_Report.txt
├── Agency_Funding.png
├── Grant Project 1.png
├── Grant Project 2.png
├── grants.db
├── Research_Funding_Dataset (1).xls
├── requirements.txt
└── README.md
```

## Live demo / deployment

The dashboard is deployment-ready for Streamlit Community Cloud. In Streamlit Cloud, select this repository, branch `main`, and entrypoint `app.py`. The app regenerates its deterministic demo dataset when needed and does not require secrets or external APIs.

> This is a demonstration deployment pattern, not a live grant feed. The repository intentionally keeps synthetic data clearly labeled.

## Core analytics

The reusable module in `src/analytics.py` provides:

| Function | Purpose |
|---|---|
| `load_grants()` | Load and normalize grant data |
| `validate_schema()` | Validate required fields |
| `funding_by_agency()` | Agency-level portfolio analysis |
| `funding_by_research_area()` | Research-domain funding analysis |
| `deadline_risk()` | Explicit-date deadline risk classification |
| `match_researcher()` | Open-grant matching by research area/eligibility |
| `load_to_sqlite()` | Persist the dataframe to SQLite |
| `sql_agency_summary()` | Reproduce agency analysis through SQL |

## Dataset

The demo dataset contains 150 modeled opportunities across 9 agencies, 10 research areas, 5 eligibility categories, and 3 statuses.

Core fields:

`Grant_ID`, `Agency`, `Grant_Name`, `Funding_Amount`, `Research_Area`, `Deadline`, `Eligibility`, `Duration_Months`, `Status`.

The generator uses a fixed random seed so the dataset is reproducible.

## Tech stack

- **Python:** Pandas, NumPy, Matplotlib
- **Database:** SQLite
- **Testing:** pytest
- **Reporting:** Excel + Jupyter
- **CI:** GitHub Actions

## Run locally

```bash
git clone https://github.com/Rollins1989/Research-Funding-Opportunity-Intelligence.git
cd Research-Funding-Opportunity-Intelligence

python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
pytest -q
python src/generate_data.py
```

Then open the notebook:

```text
Research Funding Opportunity Intelligence.ipynb
```

## Reproducibility and testing

The analysis is intentionally separated from the notebook so the core logic can be tested and reused by a future API, scheduled pipeline, or dashboard.

The CI workflow runs the test suite on pushes and pull requests to `main`.

## Portfolio interpretation

This project is best presented as an **analytics and decision-support prototype**, not as a live grant-discovery product. A production implementation would require authoritative source URLs, source-system identifiers, ingestion timestamps, change detection, eligibility validation, deduplication, authentication where required, and scheduled ingestion from official funding portals.

## Current limitations

- Synthetic data rather than live opportunities.
- Deadline risk is deterministic and depends on an explicit analysis date.
- Researcher matching currently uses exact research-area and optional eligibility matching; it is not semantic/LLM matching.
- No live API ingestion or alerting is included.

These limitations are deliberate: the repository demonstrates the analytics foundation without pretending that demo records are real funding intelligence.

## Author

**Rollins1989**
