"""Interactive Streamlit dashboard for Research Funding Opportunity Intelligence."""
from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st
from src.analytics import deadline_risk, funding_by_agency, funding_by_research_area, load_grants, match_researcher

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "raw" / "grants.csv"

st.set_page_config(page_title="Research Funding Intelligence", page_icon="🔬", layout="wide")

@st.cache_data
def get_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Demo dataset not found. Run python src/generate_data.py first.")
    return load_grants(DATA_PATH)

try:
    df = get_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

st.title("🔬 Research Funding Opportunity Intelligence")
st.caption("Interactive analytics dashboard for portfolio, deadline, and researcher-to-grant analysis.")
st.warning("Demo only: all records are synthetic. Funding amounts and deadlines are not live opportunities.")

with st.sidebar:
    st.header("Filters")
    agencies = st.multiselect("Agency", sorted(df["Agency"].unique()), default=sorted(df["Agency"].unique()))
    areas = st.multiselect("Research area", sorted(df["Research_Area"].unique()), default=sorted(df["Research_Area"].unique()))
    statuses = st.multiselect("Status", sorted(df["Status"].unique()), default=sorted(df["Status"].unique()))
    as_of = st.date_input("Analysis date", value=date.today())

filtered = df[df["Agency"].isin(agencies) & df["Research_Area"].isin(areas) & df["Status"].isin(statuses)].copy()
risk = deadline_risk(filtered, pd.Timestamp(as_of))
open_count = int(filtered["Status"].eq("Open").sum())
critical_count = int(risk["Deadline_Risk"].eq("Critical").sum())
modeled_funding = float(filtered["Funding_Amount"].sum())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Opportunities", f"{len(filtered):,}")
m2.metric("Open opportunities", f"{open_count:,}")
m3.metric("Modeled funding", f"₹{modeled_funding/1e7:.2f} Cr")
m4.metric("Critical deadlines", f"{critical_count:,}")

left, right = st.columns(2)
with left:
    st.subheader("Funding by agency")
    agency = funding_by_agency(filtered)
    if not agency.empty:
        st.bar_chart(agency.set_index("Agency")["Total_Funding"], height=320)
    else:
        st.info("No data matches the current filters.")
with right:
    st.subheader("Funding by research area")
    area = funding_by_research_area(filtered)
    if not area.empty:
        st.bar_chart(area.set_index("Research_Area")["Total_Funding"], height=320)
    else:
        st.info("No data matches the current filters.")

st.divider()
tab1, tab2, tab3 = st.tabs(["Deadline intelligence", "Researcher matching", "Opportunity explorer"])

with tab1:
    st.subheader("Deadline risk")
    risk_filter = st.multiselect("Show risk categories", ["Critical", "Watch", "Low", "Expired", "Not Open"], default=["Critical", "Watch"])
    view = risk[risk["Deadline_Risk"].isin(risk_filter)].copy()
    view["Funding_Amount"] = view["Funding_Amount"].map(lambda x: f"₹{x/1e5:.1f} L")
    st.dataframe(view[["Grant_ID","Agency","Grant_Name","Research_Area","Funding_Amount","Deadline","Days_To_Deadline","Deadline_Risk"]], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Researcher-to-grant matching")
    match_areas = st.multiselect("Research areas", sorted(df["Research_Area"].unique()), default=[])
    eligibility = st.selectbox("Eligibility", ["Any"] + sorted(df["Eligibility"].unique()))
    if match_areas:
        matches = match_researcher(df, match_areas, None if eligibility == "Any" else eligibility)
        st.metric("Matching open opportunities", len(matches))
        display = matches.copy()
        display["Funding_Amount"] = display["Funding_Amount"].map(lambda x: f"₹{x/1e5:.1f} L")
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one research area.")

with tab3:
    st.subheader("Opportunity explorer")
    search = st.text_input("Search grant name, agency, or research area")
    explorer = filtered.copy()
    if search.strip():
        needle = search.strip().casefold()
        mask = (explorer["Grant_Name"].str.casefold().str.contains(needle, na=False) |
                explorer["Agency"].str.casefold().str.contains(needle, na=False) |
                explorer["Research_Area"].str.casefold().str.contains(needle, na=False))
        explorer = explorer[mask]
    explorer["Funding_Amount"] = explorer["Funding_Amount"].map(lambda x: f"₹{x/1e5:.1f} L")
    st.dataframe(explorer, use_container_width=True, hide_index=True)

st.caption("Use official funding portals for real-world opportunity decisions.")
