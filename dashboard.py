import streamlit as st
import duckdb
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="LinkedIn Revenue Intelligence",
    layout="wide"
)

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    con = duckdb.connect()
    con.execute("CREATE TABLE revenue AS SELECT * FROM read_csv_auto('data/linkedin_revenue.csv')")

    annual = con.execute("""
        SELECT year, SUM(total_revenue) AS annual_revenue
        FROM revenue
        GROUP BY year
        ORDER BY year
    """).df()

    growth = con.execute("""
        SELECT
            period,
            total_revenue,
            ROUND(
                (total_revenue - LAG(total_revenue) OVER (ORDER BY year, quarter)) * 100.0
                / LAG(total_revenue) OVER (ORDER BY year, quarter), 2
            ) AS qoq_growth_pct
        FROM revenue
        ORDER BY year, quarter
    """).df()

    segments = con.execute("""
        SELECT
            period,
            talent_solutions,
            marketing_solutions,
            premium_subscriptions,
            total_revenue
        FROM revenue
        ORDER BY year, quarter
    """).df()

    mix = con.execute("""
        SELECT
            period,
            ROUND(talent_solutions * 100.0 / total_revenue, 1) AS talent_pct,
            ROUND(marketing_solutions * 100.0 / total_revenue, 1) AS marketing_pct,
            ROUND(premium_subscriptions * 100.0 / total_revenue, 1) AS premium_pct
        FROM revenue
        ORDER BY year, quarter
    """).df()

    return annual, growth, segments, mix

annual, growth, segments, mix = load_data()

# ---- HEADER ----
st.title("LinkedIn Revenue Intelligence Dashboard")
st.markdown("An overview of LinkedIn revenue trends across segments and quarters.")
st.divider()

# ---- ANNUAL REVENUE ----
st.subheader("Annual Revenue by Year")
st.dataframe(annual, use_container_width=True)
st.divider()

# ---- QoQ GROWTH ----
st.subheader("Quarter-over-Quarter Growth Rate")
st.dataframe(growth, use_container_width=True)
st.divider()

# ---- SEGMENT BREAKDOWN ----
st.subheader("Revenue by Segment per Quarter")
st.dataframe(segments, use_container_width=True)
st.divider()

# ---- SEGMENT MIX ----
st.subheader("Segment Mix (% of Total Revenue)")
st.dataframe(mix, use_container_width=True)
st.divider()

# ---- KEY INSIGHTS ----
st.subheader("Key Insights")
st.markdown("""
- **Consistent growth:** Revenue grew from $19.9B in 2022 to $27.4B in 2024, an increase of 37% over two years.
- **Seasonal Q1 dip:** Every year, Q1 shows a revenue decline (Q1 2023: -4.26%, Q1 2024: -1.89%), likely tied to enterprise budget cycles resetting after Q4.
- **Q2 is the strongest quarter:** Q2 consistently delivers the highest growth each year (Q2 2023: +8.51%, Q2 2024: +7.22%).
- **Talent Solutions dominates:** It accounts for roughly 59-60% of total revenue every quarter.
- **Premium Subscriptions declining in mix:** Its share dropped from 18.5% in Q1 2022 to 17.2% in Q4 2024, worth monitoring.
""")

st.divider()
st.caption("Data sourced from Microsoft quarterly earnings reports (approximated). Built as part of LinkedIn Revenue Intern application.")