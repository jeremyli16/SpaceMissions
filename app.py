from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
_rocket_status_options = (
    [{"label": s, "value": s} for s in sorted(_df["RocketStatus"].dropna().unique())]
    if not _df.empty else []
)
_location_options = (
    [{"label": loc, "value": loc} for loc in sorted(_df["Location"].dropna().unique())]
    if not _df.empty else []
)
_decades = list(range(1950, 2030, 10))
_decade_options = [{"label": "All", "value": "all"}] + [
    {"label": f"{d}s", "value": str(d)} for d in _decades
]
if not _df.empty and _df["Price"].notna().any():
    _price_min = float(_df["Price"].min())
    _price_max = float(_df["Price"].max())
else:
    _price_min, _price_max = 0.0, 1000.0
_price_range = _price_max - _price_min
_mark_unit = 1000 if _price_range >= 1000 else 100 if _price_range >= 100 else 10 if _price_range >= 10 else 1
_price_marks = {v: str(v) for v in range(0, int(_price_max) + _mark_unit, _mark_unit) if v <= _price_max}

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

        # All filter rows in an inline-flex column so all rows share the same width
        html.Div(
            style={"display": "inline-flex", "flexDirection": "column", "gap": "12px", "marginBottom": "24px"},
            children=[

                # Row 1: date + decade + reset
                html.Div(
                    style={"display": "flex", "gap": "16px", "alignItems": "flex-end"},
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
                            html.Label("Decade", style=_label_style),
                            dcc.RadioItems(
                                id="decade-filter",
                                options=_decade_options,
                                value="all",
                                inline=True,
                                inputStyle={"display": "none"},
                                labelStyle={
                                    "padding": "5px 10px",
                                    "marginRight": "4px",
                                    "background": "#2d3f55",
                                    "borderRadius": "4px",
                                    "cursor": "pointer",
                                    "fontSize": "13px",
                                    "color": "#e8f0fe",
                                },
                            ),
                        ]),
                        html.Div([
                            html.Label(" ", style=_label_style),
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

                # Row 2: company + status + rocket status + location
                html.Div(
                    style={"display": "flex", "gap": "16px", "alignItems": "flex-end"},
                    children=[
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
                                style={"width": "280px", "background": "#1e2a3a", "color": "#0f1923"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Rocket Status", style=_label_style),
                            dcc.Dropdown(
                                id="rocket-status-filter",
                                options=_rocket_status_options,
                                placeholder="All rockets",
                                clearable=True,
                                multi=True,
                                style={"width": "200px", "background": "#1e2a3a", "color": "#0f1923"},
                            ),
                        ]),
                        html.Div([
                            html.Label("Location", style=_label_style),
                            dcc.Dropdown(
                                id="location-filter",
                                options=_location_options,
                                placeholder="All locations",
                                clearable=True,
                                multi=True,
                                style={"width": "220px", "background": "#1e2a3a", "color": "#0f1923"},
                            ),
                        ]),
                    ],
                ),

                # Row 3: price range — slider fills width determined by rows above
                html.Div(
                    style={"display": "flex", "gap": "16px", "alignItems": "center"},
                    children=[
                        html.Label("Price Range (M$)", style={**_label_style, "margin": 0, "whiteSpace": "nowrap"}),
                        html.Div(
                            dcc.RangeSlider(
                                id="price-filter",
                                min=_price_min,
                                max=_price_max,
                                value=[_price_min, _price_max],
                                marks=_price_marks,
                                tooltip={"placement": "bottom", "always_visible": False},
                                updatemode="mouseup",
                            ),
                            style={"flex": "1", "minWidth": "0"},
                        ),
                    ],
                ),
            ],
        ),

        # Charts 3x2 grid
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "24px"},
            children=[
                dcc.Graph(id="year-chart"),
                dcc.Graph(id="company-chart"),
                dcc.Graph(id="country-chart"),
                dcc.Graph(id="success-rate-chart"),
                dcc.Graph(id="heatmap-chart"),
                dcc.Graph(id="cost-chart"),
            ],
        ),

        # Data table
        html.Div([
            html.Div(
                style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "marginBottom": "12px"},
                children=[
                    html.H2("Mission Data", style={"fontSize": "16px", "fontWeight": "600", "color": "#8a9bb0", "margin": "0"}),
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "8px"},
                        children=[
                            html.Label("Rows per page:", style={**_label_style, "margin": 0}),
                            dcc.Dropdown(
                                id="page-size-select",
                                options=[{"label": str(n), "value": n} for n in [10, 20, 50, 100]],
                                value=20,
                                clearable=False,
                                style={"width": "80px", "color": "#0f1923"},
                            ),
                        ],
                    ),
                ],
            ),
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
    Output("rocket-status-filter", "value"),
    Output("location-filter", "value"),
    Output("decade-filter", "value"),
    Output("price-filter", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return _DEFAULT_START, _DEFAULT_END, None, None, None, None, "all", [_price_min, _price_max]


@callback(
    Output("date-filter", "start_date", allow_duplicate=True),
    Output("date-filter", "end_date", allow_duplicate=True),
    Input("decade-filter", "value"),
    prevent_initial_call=True,
)
def sync_date_to_decade(decade):
    if not decade or decade == "all":
        return _DEFAULT_START, _DEFAULT_END
    decade_int = int(decade)
    start = date(decade_int, 1, 1)
    end = date(min(decade_int + 9, date_max_picker.year), 12, 31)
    if date_min_picker and start < date_min_picker:
        start = date_min_picker
    if date_max_picker and end > date_max_picker:
        end = date_max_picker
    return start, end


@callback(
    Output("mission-table", "page_size"),
    Input("page-size-select", "value"),
)
def update_page_size(value):
    return value if value else 20


@callback(
    Output("stat-total", "children"),
    Output("stat-success-rate", "children"),
    Output("stat-date-range", "children"),
    Output("year-chart", "figure"),
    Output("company-chart", "figure"),
    Output("country-chart", "figure"),
    Output("success-rate-chart", "figure"),
    Output("heatmap-chart", "figure"),
    Output("cost-chart", "figure"),
    Output("mission-table", "data"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
    Input("company-filter", "value"),
    Input("status-filter", "value"),
    Input("rocket-status-filter", "value"),
    Input("location-filter", "value"),
    Input("decade-filter", "value"),
    Input("price-filter", "value"),
)
def update_all(start_date, end_date, company, statuses, rocket_statuses, locations, decade, price_range):
    filtered = _df.copy()

    if decade and decade != "all":
        decade_start = int(decade)
        filtered = filtered[
            (filtered["Date"].dt.year >= decade_start) &
            (filtered["Date"].dt.year < decade_start + 10)
        ]
    if start_date:
        filtered = filtered[filtered["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["Date"] <= pd.to_datetime(end_date)]
    if company:
        filtered = filtered[filtered["Company"].isin(company)]
    if statuses:
        filtered = filtered[filtered["MissionStatus"].isin(statuses)]
    if rocket_statuses:
        filtered = filtered[filtered["RocketStatus"].isin(rocket_statuses)]
    if locations:
        filtered = filtered[filtered["Location"].isin(locations)]
    if price_range:
        lo, hi = price_range
        price_mask = filtered["Price"].isna() | ((filtered["Price"] >= lo) & (filtered["Price"] <= hi))
        filtered = filtered[price_mask]

    # Chart 1: Missions per year + success rate (dual-axis line)
    if not filtered.empty:
        by_year = filtered.groupby(filtered["Date"].dt.year).agg(
            Missions=("Mission", "count"),
            Successes=("MissionStatus", lambda x: (x == "Success").sum()),
        ).reset_index()
        by_year.columns = ["Year", "Missions", "Successes"]
        by_year["SuccessRate"] = (by_year["Successes"] / by_year["Missions"] * 100).round(2)
    else:
        by_year = pd.DataFrame({"Year": [], "Missions": [], "SuccessRate": []})
    fig_year = make_subplots(specs=[[{"secondary_y": True}]])
    fig_year.add_trace(
        go.Scatter(x=by_year["Year"], y=by_year["Missions"], name="Missions",
                   line=dict(color="#4a9eff"), mode="lines+markers"),
        secondary_y=False,
    )
    fig_year.add_trace(
        go.Scatter(x=by_year["Year"], y=by_year["SuccessRate"], name="Success Rate (%)",
                   line=dict(color="#52c41a", dash="dash"), mode="lines+markers"),
        secondary_y=True,
    )
    fig_year.update_layout(
        title_text="Missions per Year & Success Rate",
        template=_CHART_TEMPLATE,
        plot_bgcolor=_CHART_BG,
        paper_bgcolor=_PAPER_BG,
        margin=dict(t=40, b=20, l=20, r=60),
        title_x=0.5,
        title_font_weight="bold",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig_year.update_yaxes(title_text="Missions", secondary_y=False, title_font_color="#4a9eff")
    fig_year.update_yaxes(title_text="Success Rate (%)", secondary_y=True, range=[0, 100], title_font_color="#52c41a")

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

    # Chart 3: Launches by location (horizontal bar)
    if not filtered.empty:
        location_counts = filtered["Location"].value_counts().reset_index()
        location_counts.columns = ["Location", "Missions"]
        location_counts = location_counts.head(15)
    else:
        location_counts = pd.DataFrame({"Location": [], "Missions": []})
    fig_country = px.bar(
        location_counts, x="Missions", y="Location",
        orientation="h",
        title="Launches by Location (Top 15)",
        template=_CHART_TEMPLATE,
        color="Missions",
        color_continuous_scale="Blues",
    )
    fig_country.update_layout(plot_bgcolor=_CHART_BG, paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), yaxis={"categoryorder": "total ascending", "ticklabelstandoff": 8}, coloraxis_showscale=False, title_x=0.5, title_font_weight="bold")

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

    # Chart 5: Launch activity heatmap (year × month)
    _month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if not filtered.empty:
        heat_df = filtered.dropna(subset=["Date"]).copy()
        heat_df["Year"] = heat_df["Date"].dt.year
        heat_df["Month"] = heat_df["Date"].dt.month
        heat_pivot = heat_df.groupby(["Year", "Month"]).size().unstack(fill_value=0)
        for m in range(1, 13):
            if m not in heat_pivot.columns:
                heat_pivot[m] = 0
        heat_pivot = heat_pivot[sorted(heat_pivot.columns)]
        z_vals = heat_pivot.values.tolist()
        y_vals = heat_pivot.index.tolist()
    else:
        z_vals, y_vals = [], []
    fig_heatmap = go.Figure(go.Heatmap(
        z=z_vals, x=_month_names, y=y_vals,
        colorscale="Blues",
        hovertemplate="Year: %{y}<br>Month: %{x}<br>Launches: %{z}<extra></extra>",
    ))
    fig_heatmap.update_layout(title="Launch Activity by Month & Year", template=_CHART_TEMPLATE, paper_bgcolor=_PAPER_BG, plot_bgcolor=_CHART_BG, margin=dict(t=40, b=20, l=20, r=20), title_x=0.5, title_font_weight="bold")

    # Chart 6: Mission cost distribution (histogram)
    price_data = filtered.dropna(subset=["Price"])
    if not price_data.empty:
        fig_cost = px.histogram(
            price_data, x="Price",
            title="Mission Cost Distribution (M$)",
            template=_CHART_TEMPLATE,
            color_discrete_sequence=["#4a9eff"],
            nbins=30,
        )
    else:
        fig_cost = px.histogram(
            pd.DataFrame({"Price": pd.Series([], dtype=float)}), x="Price",
            title="Mission Cost Distribution (M$)",
            template=_CHART_TEMPLATE,
            color_discrete_sequence=["#4a9eff"],
        )
    fig_cost.update_layout(plot_bgcolor=_CHART_BG, paper_bgcolor=_PAPER_BG, margin=dict(t=40, b=20, l=20, r=20), title_x=0.5, title_font_weight="bold", xaxis_title="Cost (M$)", yaxis_title="Missions")

    # Table data
    table_df = filtered[["Mission", "Company", "Date", "Rocket", "MissionStatus", "Price"]].copy()
    table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")
    table_df["Price"] = table_df["Price"].astype(str).replace({"<NA>": "", "nan": ""})
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
    _fix_hover(fig_country)
    _fix_hover(fig_success)
    _fix_hover(fig_cost)

    return f"{total:,}", f"{success_rate}%", date_range_str, fig_year, fig_company, fig_country, fig_success, fig_heatmap, fig_cost, table_data
