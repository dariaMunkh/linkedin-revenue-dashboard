import duckdb
import pandas as pd

# Connect to DuckDB and load the CSV
con = duckdb.connect()
con.execute("CREATE TABLE revenue AS SELECT * FROM read_csv_auto('data/linkedin_revenue.csv')")

# ---- QUERY 1: Total revenue by year ----
print("=== Total Revenue by Year ===")
q1 = con.execute("""
    SELECT 
        year,
        SUM(total_revenue) AS annual_revenue
    FROM revenue
    GROUP BY year
    ORDER BY year
""").df()
print(q1)

# ---- QUERY 2: Quarter-over-quarter growth ----
print("\n=== QoQ Growth Rate ===")
q2 = con.execute("""
    SELECT
        period,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY year, quarter) AS prev_quarter,
        ROUND(
            (total_revenue - LAG(total_revenue) OVER (ORDER BY year, quarter)) * 100.0
            / LAG(total_revenue) OVER (ORDER BY year, quarter), 2
        ) AS qoq_growth_pct
    FROM revenue
    ORDER BY year, quarter
""").df()
print(q2)

# ---- QUERY 3: Revenue segment mix (what % each segment contributes) ----
print("\n=== Segment Mix by Quarter ===")
q3 = con.execute("""
    SELECT
        period,
        ROUND(talent_solutions * 100.0 / total_revenue, 1) AS talent_pct,
        ROUND(marketing_solutions * 100.0 / total_revenue, 1) AS marketing_pct,
        ROUND(premium_subscriptions * 100.0 / total_revenue, 1) AS premium_pct
    FROM revenue
    ORDER BY year, quarter
""").df()
print(q3)

# ---- QUERY 4: Best and worst performing quarters ----
print("\n=== Top 3 Growth Quarters ===")
q4 = con.execute("""
    WITH growth AS (
        SELECT
            period,
            total_revenue,
            LAG(total_revenue) OVER (ORDER BY year, quarter) AS prev_quarter,
            ROUND(
                (total_revenue - LAG(total_revenue) OVER (ORDER BY year, quarter)) * 100.0
                / LAG(total_revenue) OVER (ORDER BY year, quarter), 2
            ) AS qoq_growth_pct
        FROM revenue
    )
    SELECT period, total_revenue, qoq_growth_pct
    FROM growth
    WHERE qoq_growth_pct IS NOT NULL
    ORDER BY qoq_growth_pct DESC
    LIMIT 3
""").df()
print(q4)

# ---- Save all results to Excel for Day 2 ----
with pd.ExcelWriter('data/linkedin_analysis.xlsx') as writer:
    q1.to_excel(writer, sheet_name='Annual Revenue', index=False)
    q2.to_excel(writer, sheet_name='QoQ Growth', index=False)
    q3.to_excel(writer, sheet_name='Segment Mix', index=False)
    q4.to_excel(writer, sheet_name='Top Growth Quarters', index=False)

print("\n All queries saved to data/linkedin_analysis.xlsx")