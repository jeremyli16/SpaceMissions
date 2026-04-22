import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, callback

import functions as fn

app = Dash(__name__)

_df = fn.df


def _summary_stats():
    if fn.DATA_LOADED and not _df.empty:
        total = len(_df)
        success_rate = round((_df["MissionStatus"] == "Success").sum() / total * 100, 2)
        date_min = _df["Date"].min().strftime("%Y-%m-%d")
        date_max = _df["Date"].max().strftime("%Y-%m-%d")
        date_min_picker = _df["Date"].min().date()
        date_max_picker = _df["Date"].max().date()
    else:
        total, success_rate = 0, 0.0
        date_min = date_max = "N/A"
        date_min_picker = date_max_picker = None
    return total, success_rate, date_min, date_max, date_min_picker, date_max_picker


total_missions, overall_success_rate, date_min, date_max, date_min_picker, date_max_picker = _summary_stats()

_company_options = (
    [{"label": c, "value": c} for c in sorted(_df["Company"].dropna().unique())]
    if not _df.empty else []
)
_status_options = [
    {"label": s, "value": s}
    for s in ["Success", "Failure", "Partial Failure", "Prelaunch Failure"]
]

_card_style = {
    "background": "#1e2a3a",
    "border": "1px solid #2d3f55",
    "borderRadius": "8px",
    "padding": "20px 24px",
    "flex": "1",
    "minWidth": "180px",
}
_label_style = {"color": "#8a9bb0", "fontSize": "12px", "textTransform": "uppercase", "letterSpacing": "1px", "margin": "0 0 6px 0"}
_value_style = {"color": "#e8f0fe", "fontSize": "28px", "fontWeight": "700", "margin": "0"}

_warning_banner = (
    html.Div(
        "⚠ space_missions.csv not found. Place the file in the project directory and restart.",
        style={"background": "#7a5500", "color": "#ffe58f", "padding": "10px 20px", "borderRadius": "6px", "marginBottom": "16px"},
    )
    if not fn.DATA_LOADED else None
)

app.layout = html.Div(
    style={"fontFamily": "Inter, system-ui, sans-serif", "background": "#0f1923", "minHeight": "100vh", "padding": "24px 32px", "color": "#e8f0fe"},
    children=[
        _warning_banner,

        # Header
        html.H1("Space Missions Dashboard", style={"color": "#e8f0fe", "fontSize": "24px", "fontWeight": "700", "margin": "0 0 24px 0", "textAlign": "center"}),

        # Summary stats
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap"},
            children=[
                html.Div([html.P("Total Missions", style=_label_style), html.P(id="stat-total", style=_value_style)], style=_card_style),
                html.Div([html.P("Overall Success Rate", style=_label_style), html.P(id="stat-success-rate", style=_value_style)], style=_card_style),
                html.Div([html.P("Date Range", style=_label_style), html.P(id="stat-date-range", style={**_value_style, "fontSize": "16px"})], style=_card_style),
            ],
        ),

        # Filters
        html.Div(
            style={"display": "flex", "gap": "16px", "marginBottom": "24px", "flexWrap": "wrap", "alignItems": "flex-end"},
            children=[
                html.Div([
                    html.Label("Date Range", style=_label_style),
                    dcc.DatePickerRange(
                        id="date-filter",
                        min_date_allowed=date_min_picker,
                        max_date_allowed=date_max_picker,
                        start_date=date_min_picker,
                        end_date=date_max_picker,
                        display_format="YYYY-MM-DD",
                        style={"background": "#1e2a3a"},
                    ),
                ]),
                html.Div([
                    html.Label("Company", style=_label_style),
                    dcc.Dropdown(
                        id="company-filter",
                        options=_company_options,
                        placeholder="All companies",
                        clearable=True,
                        multi=True,
                        style={"width": "300px", "background": "#1e2a3a", "color": "#0f1923"},
                    ),
                ]),
                html.Div([
                    html.Label("Mission Status", style=_label_style),
                    dcc.Dropdown(
                        id="status-filter",
                        options=_status_options,
                        placeholder="All statuses",
                        multi=True,
                        style={"width": "300px", "background": "#1e2a3a", "color": "#0f1923"},
                    ),
                ]),
                html.Div([
                    html.Label(" ", style=_label_style),
                    html.Button(
                        "Reset Filters",
                        id="reset-btn",
                        n_clicks=0,
                        style={
                            "background": "#2d3f55",
                            "color": "#e8f0fe",
                            "border": "1px solid #4a9eff",
                            "borderRadius": "6px",
                            "padding": "8px 16px",
                            "cursor": "pointer",
                            "fontSize": "13px",
                            "fontWeight": "600",
                        },
                    ),
                ]),
            ],
        ),

        # Charts 2x2 grid
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "24px"},
            children=[
                dcc.Graph(id="year-chart"),
                dcc.Graph(id="company-chart"),
                dcc.Graph(id="status-chart"),
                dcc.Graph(id="success-rate-chart"),
            ],
        ),

        # Data table
        html.Div([
            html.H2("Mission Data", style={"fontSize": "16px", "fontWeight": "600", "color": "#8a9bb0", "margin": "0 0 12px 0"}),
            dash_table.DataTable(
                id="mission-table",
                columns=[
                    {"name": "Mission", "id": "Mission"},
                    {"name": "Company", "id": "Company"},
                    {"name": "Date", "id": "Date"},
                    {"name": "Rocket", "id": "Rocket"},
                    {"name": "Status", "id": "MissionStatus"},
                    {"name": "Price (M$)", "id": "Price"},
                ],
                sort_action="native",
                filter_action="native",
                page_action="native",
                page_size=20,
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#1e2a3a", "color": "#8a9bb0", "fontWeight": "600", "border": "1px solid #2d3f55"},
                style_cell={"backgroundColor": "#131f2e", "color": "#c8d8ea", "border": "1px solid #1e2a3a", "padding": "8px 12px", "fontSize": "13px"},
                style_data_conditional=[
                    {"if": {"filter_query": '{MissionStatus} = "Success"'}, "color": "#52c41a"},
                    {"if": {"filter_query": '{MissionStatus} = "Failure"'}, "color": "#ff4d4f"},
                    {"if": {"filter_query": '{MissionStatus} = "Partial Failure"'}, "color": "#faad14"},
                    {"if": {"filter_query": '{MissionStatus} = "Prelaunch Failure"'}, "color": "#ff7a45"},
                ],
            ),
        ]),
    ],
)

_CHART_TEMPLATE = "plotly_dark"
_CHART_BG = "#131f2e"
_PAPER_BG = "#1e2a3a"


def _fix_hover(fig):
    fig.for_each_trace(lambda t: t.update(
        hovertemplate=t.hovertemplate.replace("=", ": ") if t.hovertemplate else t.hovertemplate
    ))
    return fig

_DEFAULT_START = date_min_picker
_DEFAULT_END = date_max_picker


@callback(
    Output("date-filter", "start_date"),
    Output("date-filter", "end_date"),
    Output("company-filter", "value"),
    Output("status-filter", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return _DEFAULT_START, _DEFAULT_END, None, None


@callback(
    Output("stat-total", "children"),
    Output("stat-success-rate", "children"),
    Output("stat-date-range", "children"),
    Output("year-chart", "figure"),
    Output("company-chart", "figure"),
    Output("status-chart", "figure"),
    Output("success-rate-chart", "figure"),
    Output("mission-table", "data"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
    Input("company-filter", "value"),
    Input("status-filter", "value"),
)
def update_all(start_date, end_date, company, statuses):
    filtered = _df.copy()

    if start_date:
        filtered = filtered[filtered["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["Date"] <= pd.to_datetime(end_date)]
    if company:
        filtered = filtered[filtered["Company"].isin(company)]
    if statuses:
        filtered = filtered[filtered["MissionStatus"].isin(statuses)]

    # Chart 1: Missions per year (line)
    if not filtered.empty:
        by_year = filtered.groupby(filtered["Date"].dt.year).size().reset_index(name="Missions")
        by_year.columns = ["Year", "Missions"]
    else:
        by_year = pd.DataFrame({"Year": [], "Missions": []})
    fig_year = px.line(
        by_year, x="Year", y="Missions",
        title="Missions per Year",
        template=_CHART_TEMPLATE,
        markers=True,
        color_discrete_sequence=["#4a9eff"],
    )
    fig_year.update_layout(plot_bgcolor=_CHART_BG, paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), title_x=0.5, title_font_weight="bold")

    # Chart 2: Top 15 companies by mission count (bar)
    if not filtered.empty:
        top_companies = (
            filtered.groupby("Company").size().reset_index(name="Missions")
            .sort_values("Missions", ascending=False).head(15)
        )
    else:
        top_companies = pd.DataFrame({"Company": [], "Missions": []})
    fig_company = px.bar(
        top_companies, x="Missions", y="Company",
        orientation="h",
        title="Top Companies by Mission Count",
        template=_CHART_TEMPLATE,
        color="Missions",
        color_continuous_scale="Blues",
    )
    fig_company.update_layout(plot_bgcolor=_CHART_BG, paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), yaxis={"categoryorder": "total ascending", "ticklabelstandoff": 8}, coloraxis_showscale=False, title_x=0.5, title_font_weight="bold")

    # Chart 3: Mission status breakdown (donut)
    if not filtered.empty:
        status_counts = filtered["MissionStatus"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
    else:
        status_counts = pd.DataFrame({"Status": [], "Count": []})
    fig_status = px.pie(
        status_counts, names="Status", values="Count",
        title="Mission Status Breakdown",
        template=_CHART_TEMPLATE,
        hole=0.45,
        color_discrete_map={
            "Success": "#52c41a",
            "Failure": "#ff4d4f",
            "Partial Failure": "#faad14",
            "Prelaunch Failure": "#ff7a45",
        },
    )
    fig_status.update_layout(paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), title_x=0.5, title_font_weight="bold")

    # Chart 4: Success rate by company — top 10 by mission count (horizontal bar)
    if not filtered.empty:
        grp = filtered.groupby("Company").agg(
            total=("MissionStatus", "count"),
            successes=("MissionStatus", lambda x: (x == "Success").sum()),
        ).reset_index()
        grp = grp[grp["total"] >= 5]
        grp["SuccessRate"] = (grp["successes"] / grp["total"] * 100).round(2)
        grp = grp.sort_values("total", ascending=False).head(10)
    else:
        grp = pd.DataFrame({"Company": [], "SuccessRate": []})
    fig_success = px.bar(
        grp, x="SuccessRate", y="Company",
        orientation="h",
        title="Success Rate by Company (top 10 by volume, min 5 missions)",
        template=_CHART_TEMPLATE,
        color="SuccessRate",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
    )
    fig_success.update_layout(plot_bgcolor=_CHART_BG, paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), yaxis={"categoryorder": "total ascending", "ticklabelstandoff": 8}, coloraxis_showscale=False, title_x=0.5, title_font_weight="bold")

    # Table data
    table_df = filtered[["Mission", "Company", "Date", "Rocket", "MissionStatus", "Price"]].copy()
    table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")
    table_df["Price"] = table_df["Price"].astype(str).replace("<NA>", "")
    table_data = table_df.to_dict("records")

    # Summary stats
    total = len(filtered)
    success_rate = round((filtered["MissionStatus"] == "Success").sum() / total * 100, 2) if total else 0.0
    if not filtered.empty and filtered["Date"].notna().any():
        d_min = filtered["Date"].min().strftime("%Y-%m-%d")
        d_max = filtered["Date"].max().strftime("%Y-%m-%d")
        date_range_str = f"{d_min} → {d_max}"
    else:
        date_range_str = "N/A"

    _fix_hover(fig_year)
    _fix_hover(fig_company)
    _fix_hover(fig_status)
    _fix_hover(fig_success)

    return f"{total:,}", f"{success_rate}%", date_range_str, fig_year, fig_company, fig_status, fig_success, table_data
