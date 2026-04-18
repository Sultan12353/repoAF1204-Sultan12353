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
    return mo, pd


@app.cell
def _(pd):
    # 1: Setup & Data Prep
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)

    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100
    return (df_final,)


@app.cell
def _(df_final, mo):
    # 2: Define the UI Controls

    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3],
        label="Filter by Sector",
    )

    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9

    cap_slider = mo.ui.slider(
        start=0,
        stop=200,
        step=10,
        value=0,
        label="Min Market Cap ($ Billions)"
    )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    # 3: Reactive Filter Logic

    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
    ]

    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
def _(count, filtered_portfolio, mo, pd):
    # 4: Visualizations
    import plotly.express as px

    # Plot 1: Scatter
    fig_portfolio = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Name',
        title=f"Cost of Debt vs. Z-Score ({count} observations)",
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation',
        width=900,
        height=600
    )

    fig_portfolio.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation_text="Distress Threshold (Z-Score = 1.81)",
        annotation_font_color="red",
        annotation_position="top"
    )

    fig_portfolio.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation_text="Safe Threshold (Z-Score = 2.99)",
        annotation_font_color="green",
        annotation_position="top"
    )

    # Plot 2: Travel Map
    travel_data = pd.DataFrame({
        'City': ['London', 'New York', 'Tokyo', 'Sydney', 'Paris'],
        'Lat': [51.5, 40.7, 35.6, -33.8, 48.8],
        'Lon': [-0.1, -74.0, 139.6, 151.2, 2.3],
        'Visit_Year_str': ['2022', '2023', '2024', '2021', '2023']
    })

    years = sorted(travel_data['Visit_Year_str'].unique(), key=int)

    fig_travel = px.scatter_geo(
        travel_data,
        lat='Lat', lon='Lon',
        hover_name='City',
        color='Visit_Year_str',
        category_orders={'Visit_Year_str': years},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth",
        title="My Travel Footprint",
        labels={'Visit_Year_str': 'Visit Year'}
    )

    fig_travel.update_traces(marker=dict(size=12))
    fig_travel.update_layout(width=800, height=500)
    
    return fig_portfolio, fig_travel


@app.cell
def _(cap_slider, fig_portfolio, fig_travel, mo, sector_dropdown):
    # 5: Layout

    tab_cv = mo.md(
        """
    **Summary:**

    Strong interest in:

    - Investment management
    - Financial markets
    - Financial analysis

    Experienced in market research, financial summaries, Excel-based data handling, and supporting investment decisions through practical exposure in a family investment business.

    Analytical, detail-oriented, and eager to apply financial and research skills to real-world business and investment challenges.

    **Education:**

    BSc Accounting and Finance, Bayes Business School, City, University of London (2025 – 2028)

    Relevant Modules:
    - Introductory Financial Accounting
    - Introduction to Finance
    - Business Research Methods

    **Skills:**

    - 📊 Financial Analysis
    - 📈 Market Research
    - 💻 Microsoft Excel
    - 📑 Financial Statement Analysis
    - 📊 Data Visualisation
    - 🐍 Python Programming
    - 🧮 Financial Modelling
    - 📂 Data Cleaning
    - 🤝 Communication and Teamwork
    """
    )

    tab_data_content = mo.vstack([
        mo.md("## 📊 Interactive Credit Risk Analyzer"),
        mo.callout(mo.md("Use the filters below to explore the relationship between Borrowing Costs and Credit Risk."), kind="info"),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        mo.plotly(fig_portfolio)  # Changed: display the figure directly, not as a UI element
    ])

    tab_personal = mo.vstack([
        mo.md("## 🌍 My Hobbies: Travel & Photography"),
        mo.md("When I'm not analyzing company financials, I love exploring the world."),
        mo.plotly(fig_travel)  # Changed: display the figure directly
    ])
    return tab_cv, tab_data_content, tab_personal


@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal):
    # 6: Final assembly

    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Passion Projects": tab_data_content,
        "✈️ Personal Interests": tab_personal
    })

    mo.md(
        f"""
# **Sultan Almahmoud**

{app_tabs}
"""
    )