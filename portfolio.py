# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip
    return mo, pd, micropip


@app.cell
def _(pd):
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)
    df_final = df_final.dropna(subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key", "Market_Cap"])
    df_final = df_final[df_final["AvgCost_of_Debt"] < 5]
    df_final["Debt_Cost_Percent"] = df_final["AvgCost_of_Debt"] * 100
    df_final["Market_Cap_B"] = df_final["Market_Cap"] / 1e9

    return (df_final,)


@app.cell
def _(df_final, mo):
    metric_options = {
        "Average Cost of Debt (%)": "Debt_Cost_Percent",
        "Average Z-Score": "Z_Score_lag",
        "Average Market Cap ($ Billions)": "Market_Cap_B",
        "Number of Companies": "Company_Count",
    }

    metric_dropdown = mo.ui.dropdown(
        options=list(metric_options.keys()),
        value="Average Cost of Debt (%)",
        label="Choose metric",
    )

    top_n_slider = mo.ui.slider(
        start=3,
        stop=11,
        step=1,
        value=8,
        label="Number of sectors to show",
    )

    return metric_dropdown, metric_options, top_n_slider


@app.cell
def _(df_final, metric_dropdown, metric_options, top_n_slider):
    sector_summary = (
        df_final.groupby("Sector_Key", as_index=False)
        .agg(
            Debt_Cost_Percent=("Debt_Cost_Percent", "mean"),
            Z_Score_lag=("Z_Score_lag", "mean"),
            Market_Cap_B=("Market_Cap_B", "mean"),
            Company_Count=("Name", "count"),
        )
    )

    selected_col = metric_options[metric_dropdown.value]
    sector_summary = sector_summary.sort_values(
        by=selected_col,
        ascending=False,
    ).head(top_n_slider.value)

    return sector_summary, selected_col


@app.cell
async def _(micropip):
    await micropip.install("plotly")
    import plotly.express as px
    return (px,)


@app.cell
def _(mo, pd, px, sector_summary, metric_dropdown, selected_col):
    fig_sector = px.bar(
        sector_summary,
        x="Sector_Key",
        y=selected_col,
        color="Sector_Key",
        title=f"Sectors Ranked by {metric_dropdown.value}",
        labels={
            "Sector_Key": "Sector",
            selected_col: metric_dropdown.value,
        },
        template="presentation",
        width=900,
        height=600,
    )

    fig_sector.update_layout(showlegend=False)
    chart_element = mo.ui.plotly(fig_sector)

    travel_data = pd.DataFrame({
        "City": ["London", "New York", "Tokyo", "Sydney", "Paris"],
        "Lat": [51.5, 40.7, 35.6, -33.8, 48.8],
        "Lon": [-0.1, -74.0, 139.6, 151.2, 2.3],
        "Visit_Year_str": ["2022", "2023", "2024", "2021", "2023"],
    })

    years = sorted(travel_data["Visit_Year_str"].unique(), key=int)

    fig_travel = px.scatter_geo(
        travel_data,
        lat="Lat",
        lon="Lon",
        hover_name="City",
        color="Visit_Year_str",
        category_orders={"Visit_Year_str": years},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth",
        title="My Travel Footprint",
        labels={"Visit_Year_str": "Visit Year"},
    )

    fig_travel.update_traces(marker=dict(size=12))

    return chart_element, fig_travel


@app.cell
def _(chart_element, fig_travel, metric_dropdown, mo, top_n_slider):
    tab_cv = mo.md(
        """
        **Summary:**
        Strong interest in finance, markets, and financial analysis.

        **Education:**
        BSc Accounting and Finance, Bayes Business School,
        City, University of London (2025 - 2028)

        **Skills:**
        - Financial Analysis
        - Market Research
        - Microsoft Excel
        - Python Programming
        - Data Visualisation
        """
    )

    tab_data_content = mo.vstack([
        mo.md("## Sector Comparison"),
        mo.callout(
            mo.md("Use the controls below to compare sectors with a simple ranked bar chart."),
            kind="info",
        ),
        mo.hstack([metric_dropdown, top_n_slider], justify="center", gap=2),
        chart_element,
    ])

    tab_personal = mo.vstack([
        mo.md("## My Hobbies: Travel & Photography"),
        mo.md("When I'm not analyzing company financials, I love exploring the world."),
        mo.ui.plotly(fig_travel),
    ])

    return tab_cv, tab_data_content, tab_personal


@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal):
    app_tabs = mo.ui.tabs({
        "About Me": tab_cv,
        "Passion Projects": tab_data_content,
        "Personal Interests": tab_personal,
    })

    mo.md(
        f"""
# **Sultan Almahmoud**

{app_tabs}
"""
    )
    return


if __name__ == "__main__":
    app.run()
