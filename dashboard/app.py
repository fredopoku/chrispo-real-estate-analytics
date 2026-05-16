"""
============================================================
  Chrispo E.P.O LTD — Interactive Analytics Dashboard
  Author  : Frederick Opoku Afriyie
  Stack   : Python · Plotly Dash · Pandas
  Run     : python app.py  →  open http://127.0.0.1:8050
============================================================
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import os

# ── Brand colours ──────────────────────────────────────────
BLUE   = "#1A3A6B"
GOLD   = "#C9A84C"
GREEN  = "#1e7e4a"
RED    = "#C0392B"
LIGHT  = "#F0F4FF"
WHITE  = "#FFFFFF"
GREY   = "#7F8C8D"

PHASE_COLORS = {
    "Phase 1 – Launch (Overpriced)":        RED,
    "Phase 2 – First Adjustment":           GOLD,
    "Phase 2 – Market Research Adjustment": GOLD,
    "Phase 3 – Optimised Pricing":          GREEN,
    "Phase 3 – Optimised":                  GREEN,
    "Phase 4 – Stable Growth":              BLUE,
}

STATUS_COLORS = {
    "Available":   BLUE,
    "Sold":        GREEN,
    "Rented":      GOLD,
    "Under Offer": "#7F5BB5",
}

# ── Load data ──────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")

df_b = pd.read_csv(os.path.join(DATA, "chrispo_bookings_data.csv"))
df_p = pd.read_csv(os.path.join(DATA, "chrispo_pricing_journey.csv"))
df_l = pd.read_csv(os.path.join(DATA, "chrispo_listings_data.csv"))

# ── App ────────────────────────────────────────────────────
app = Dash(__name__, title="Chrispo E.P.O LTD Analytics",
           suppress_callback_exceptions=True,
           meta_tags=[{"name": "viewport",
                        "content": "width=device-width, initial-scale=1"}])
server = app.server  # for deployment

# ── Layout helpers ─────────────────────────────────────────
def kpi_card(label, value, colour=BLUE, sub=None):
    return html.Div([
        html.P(label, style={"fontSize": "11px", "color": GREY,
                              "margin": "0 0 4px", "textTransform": "uppercase",
                              "letterSpacing": "0.05em"}),
        html.P(value, className="kpi-card-value",
               style={"fontSize": "22px", "fontWeight": "700",
                      "color": colour, "margin": "0",
                      "whiteSpace": "nowrap"}),
        html.P(sub, style={"fontSize": "11px", "color": GREY, "margin": "4px 0 0"})
        if sub else html.Div(),
    ], className="kpi-card", style={
        "background": WHITE,
        "borderRadius": "10px",
        "padding": "16px 20px",
        "boxShadow": "0 2px 12px rgba(26,58,107,0.08)",
        "borderLeft": f"4px solid {colour}",
        "flex": "1",
        "minWidth": "0",
    })

def section_header(title):
    return html.H3(title, style={
        "color": BLUE, "fontSize": "14px", "fontWeight": "600",
        "margin": "0 0 12px", "letterSpacing": "0.03em",
        "textTransform": "uppercase",
    })

def chart_card(children, style=None):
    base = {
        "background": WHITE,
        "borderRadius": "12px",
        "padding": "20px",
        "boxShadow": "0 2px 12px rgba(26,58,107,0.08)",
        "marginBottom": "16px",
        "minWidth": "0",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base)

# ── Figures ────────────────────────────────────────────────
def fig_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=BLUE, family="Georgia"),
                   x=0, xanchor="left", pad=dict(l=0)),
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        font=dict(family="Georgia, serif", color="#333"),
        margin=dict(l=48, r=24, t=44, b=88),
        legend=dict(orientation="h", yanchor="top", y=-0.22,
                    xanchor="center", x=0.5, font=dict(size=11)),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0", tickfont=dict(size=10),
                     automargin=True)
    fig.update_yaxes(gridcolor="#F0F0F0", linecolor="#E0E0E0", tickfont=dict(size=10))
    return fig

def make_occupancy_fig(property_filter="Both"):
    df = df_p.copy()
    if property_filter != "Both":
        df = df[df["Property"] == property_filter]
    fig = go.Figure()
    for prop in df["Property"].unique():
        sub = df[df["Property"] == prop]
        phase_labels = sub["Phase"].str.extract(r"^(Phase \d+)")[0]
        fig.add_trace(go.Bar(
            x=phase_labels,
            y=sub["Occupancy_Rate_Pct"],
            name=prop,
            marker_color=[PHASE_COLORS.get(p, GREY) for p in sub["Phase"]],
            text=sub["Occupancy_Rate_Pct"].map(lambda x: f"{x:.0f}%"),
            textposition="outside",
            hovertemplate="<b>%{fullData.name}</b> %{x}<br>Occupancy: %{y:.0f}%<extra></extra>",
        ))
    fig = fig_layout(fig, "Occupancy rate by pricing phase")
    fig.update_layout(barmode="group", showlegend=True,
                      yaxis=dict(title="Occupancy (%)", range=[0, 95]))
    return fig

def make_rate_fig():
    fig = go.Figure()
    for prop, color, dash in [("Barekese", BLUE, "solid"), ("Buokrom", GREEN, "dash")]:
        sub = df_p[df_p["Property"] == prop]
        ph_labels = [p.split("–")[0].strip() for p in sub["Phase"]]
        fig.add_trace(go.Scatter(
            x=ph_labels, y=sub["Weekday_Rate_GHS"],
            name=f"{prop} weekday", mode="lines+markers",
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=9, color=color),
            hovertemplate="<b>%{x}</b><br>Weekday: ₵%{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ph_labels, y=sub["Weekend_Rate_GHS"],
            name=f"{prop} weekend", mode="lines+markers",
            line=dict(color=color, width=2, dash="dot"),
            marker=dict(size=7, color=color, symbol="square"),
            hovertemplate="<b>%{x}</b><br>Weekend: ₵%{y:,.0f}<extra></extra>",
        ))
    fig = fig_layout(fig, "Nightly rate journey — weekday vs weekend (GHS)")
    fig.update_layout(
        yaxis=dict(title="Rate (GHS)"),
        margin=dict(l=48, r=24, t=44, b=88),
    )
    fig.add_annotation(
        x="Phase 1", y=2000, text="Overpriced → low bookings",
        showarrow=True, arrowhead=2, arrowcolor=RED,
        font=dict(size=10, color=RED), ax=60, ay=-50,
        bgcolor="rgba(255,255,255,0.8)", borderpad=4,
    )
    return fig

def make_revenue_impact_fig():
    fig = go.Figure()
    max_rev = 0
    for prop, color in [("Barekese", BLUE), ("Buokrom", GREEN)]:
        sub = df_p[df_p["Property"] == prop]
        ph_labels = [p.split("–")[0].strip() for p in sub["Phase"]]
        max_rev = max(max_rev, sub["Est_Monthly_Revenue_GHS"].max())
        fig.add_trace(go.Bar(
            x=ph_labels, y=sub["Est_Monthly_Revenue_GHS"],
            name=prop, marker_color=color, opacity=0.85,
            text=sub["Est_Monthly_Revenue_GHS"].map(lambda x: f"₵{x/1000:.0f}K"),
            textposition="outside",
            hovertemplate="<b>%{fullData.name}</b> %{x}<br>Est. Revenue: ₵%{y:,.0f}<extra></extra>",
        ))
    fig = fig_layout(fig, "Estimated monthly revenue by phase (GHS)")
    fig.update_layout(
        barmode="group",
        yaxis=dict(title="Revenue (GHS)", range=[0, max_rev * 1.2]),
        margin=dict(l=48, r=24, t=44, b=88),
    )
    return fig

def make_quarterly_revenue_fig(property_filter="Both"):
    df = df_b[df_b["Booking_Type"] == "Nightly Stay"].copy()
    if property_filter != "Both":
        df = df[df["Property"] == property_filter]
    rev = df.groupby(["Year_Quarter", "Property"])["Revenue_GHS"].sum().reset_index()
    rev = rev.sort_values("Year_Quarter")
    fig = go.Figure()
    for prop, color in [("Barekese", BLUE), ("Buokrom", GREEN)]:
        sub = rev[rev["Property"] == prop]
        fig.add_trace(go.Scatter(
            x=sub["Year_Quarter"], y=sub["Revenue_GHS"],
            name=prop, mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=7, color=color),
            fill="tozeroy", fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.08])}",
            hovertemplate="<b>%{x}</b><br>Revenue: ₵%{y:,.0f}<extra></extra>",
        ))
    fig = fig_layout(fig, "Quarterly booking revenue trend (GHS)")
    fig.update_layout(
        xaxis=dict(title="Quarter", tickangle=45),
        yaxis=dict(title="Revenue (GHS)"),
        margin=dict(l=48, r=24, t=44, b=110),
    )
    return fig

def make_booking_type_fig():
    rev = df_b[df_b["Property"] == "Barekese"].groupby("Booking_Type")["Revenue_GHS"].sum()
    fig = go.Figure(go.Pie(
        labels=rev.index, values=rev.values,
        hole=0.5,
        marker=dict(colors=[BLUE, GOLD], line=dict(color=WHITE, width=2)),
        textinfo="label+percent",
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        automargin=True,
        hovertemplate="<b>%{label}</b><br>Revenue: ₵%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig = fig_layout(fig, "Barekese — stays vs event revenue")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=60, r=60, t=56, b=40),
    )
    return fig

def make_weekday_weekend_fig():
    rev = df_b[df_b["Booking_Type"] == "Nightly Stay"].groupby("Is_Weekend")["Revenue_GHS"].sum()
    labels = ["Weekday", "Weekend"]
    values = [rev.get(False, 0), rev.get(True, 0)]
    max_val = max(values)
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=[BLUE, GOLD],
        text=[f"₵{v/1000:.0f}K" for v in values],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Revenue: ₵%{y:,.0f}<extra></extra>",
    ))
    fig = fig_layout(fig, "Weekday vs weekend revenue")
    fig.update_layout(
        yaxis=dict(title="Revenue (GHS)", range=[0, max_val * 1.2]),
        showlegend=False,
    )
    return fig

def make_portfolio_status_fig():
    counts = df_l.groupby(["Location", "Status"]).size().reset_index(name="Count")
    fig = go.Figure()
    for status, color in STATUS_COLORS.items():
        sub = counts[counts["Status"] == status]
        fig.add_trace(go.Bar(
            x=sub["Location"], y=sub["Count"],
            name=status, marker_color=color,
            text=sub["Count"], textposition="inside",
            hovertemplate=f"<b>{status}</b><br>Count: %{{y}}<extra></extra>",
        ))
    fig = fig_layout(fig, "Listings by status — Offinso vs Amrahia")
    fig.update_layout(
        barmode="stack",
        yaxis=dict(title="Number of listings"),
        xaxis=dict(title=""),
        uniformtext=dict(minsize=9, mode="hide"),
        legend=dict(
            orientation="v", x=1.02, xanchor="left",
            y=0.5, yanchor="middle", font=dict(size=11),
        ),
        margin=dict(l=48, r=110, t=56, b=48),
    )
    return fig

def make_type_mix_fig():
    counts = df_l.groupby(["Property_Type", "Location"]).size().reset_index(name="Count")
    max_count = counts["Count"].max()
    fig = go.Figure()
    for loc, color in [("Offinso", BLUE), ("Amrahia", GOLD)]:
        sub = counts[counts["Location"] == loc]
        fig.add_trace(go.Bar(
            x=sub["Property_Type"], y=sub["Count"],
            name=loc, marker_color=color, opacity=0.9,
            text=sub["Count"], textposition="outside",
            hovertemplate=f"<b>{loc}</b><br>%{{x}}: %{{y}}<extra></extra>",
        ))
    fig = fig_layout(fig, "Property type mix — Offinso vs Amrahia")
    fig.update_layout(barmode="group",
                      yaxis=dict(title="Count", range=[0, max_count * 1.25]),
                      xaxis=dict(title=""))
    return fig

# ── KPI values ─────────────────────────────────────────────
total_rev    = df_b["Revenue_GHS"].sum()
bar_rev      = df_b[df_b["Property"] == "Barekese"]["Revenue_GHS"].sum()
buo_rev      = df_b[df_b["Property"] == "Buokrom"]["Revenue_GHS"].sum()
total_book   = len(df_b)
port_val     = df_l["Price_GHS"].sum()
total_list   = len(df_l)
units_sold   = (df_l["Status"] == "Sold").sum()

# ── Layout ─────────────────────────────────────────────────
NAV_STYLE = {
    "display": "flex", "gap": "8px", "padding": "0 32px",
    "borderBottom": f"2px solid {LIGHT}",
}

TAB_STYLE = {
    "padding": "14px 24px", "cursor": "pointer",
    "fontSize": "13px", "fontWeight": "600",
    "color": GREY, "border": "none", "background": "none",
    "borderBottom": "3px solid transparent",
    "fontFamily": "Georgia, serif",
}

app.layout = html.Div([

    # ── Header ──────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1("Chrispo E.P.O LTD", style={
                "color": BLUE, "fontSize": "22px", "fontWeight": "700",
                "margin": "0", "fontFamily": "Georgia, serif",
            }),
            html.P("Real Estate & Short-Stay Analytics · Ashanti & Greater Accra Regions",
                   style={"color": GREY, "fontSize": "12px", "margin": "2px 0 0"}),
        ]),
        html.Div([
            html.Span("2022 – 2024", style={
                "background": LIGHT, "color": BLUE,
                "padding": "4px 12px", "borderRadius": "20px",
                "fontSize": "12px", "fontWeight": "600",
            }),
        ]),
    ], className="app-header", style={
        "display": "flex", "justifyContent": "space-between",
        "alignItems": "center", "padding": "20px 32px 16px",
        "background": WHITE,
        "boxShadow": "0 2px 8px rgba(26,58,107,0.06)",
    }),

    # ── Tabs ────────────────────────────────────────────
    html.Div([
        html.Button("Pricing Journey", id="tab-pricing", n_clicks=0,
                    style={**TAB_STYLE, "borderBottomColor": BLUE, "color": BLUE}),
        html.Button("Booking Performance", id="tab-booking", n_clicks=0,
                    style=TAB_STYLE),
        html.Button("Property Portfolio", id="tab-portfolio", n_clicks=0,
                    style=TAB_STYLE),
    ], className="app-nav", style=NAV_STYLE),

    # ── Content ─────────────────────────────────────────
    html.Div(id="page-content", className="page-content", style={
        "padding": "24px 32px",
        "background": LIGHT,
        "minHeight": "calc(100vh - 120px)",
    }),

], style={"fontFamily": "Georgia, serif", "background": LIGHT})

# ── Pages ──────────────────────────────────────────────────
def pricing_page():
    return html.Div([
        # KPI row
        html.Div([
            kpi_card("Barekese Phase 1 Occupancy", "18%", RED, "Overpriced launch"),
            kpi_card("Barekese Phase 3 Occupancy", "58%", GREEN, "After repricing"),
            kpi_card("Revenue uplift", "+290%", GREEN, "Phase 1 → Phase 3"),
            kpi_card("Buokrom Phase 1 → Phase 3", "15% → 61%", BLUE, "3 pricing phases"),
        ], className="kpi-grid", style={"display": "grid",
                  "gridTemplateColumns": "repeat(4, 1fr)",
                  "gap": "12px", "marginBottom": "20px"}),

        # Filter
        html.Div([
            html.Label("Filter by property:", style={"fontSize": "12px",
                        "color": GREY, "marginRight": "10px", "fontWeight": "600"}),
            dcc.Dropdown(
                id="property-filter",
                options=[
                    {"label": "Both", "value": "Both"},
                    {"label": "Barekese", "value": "Barekese"},
                    {"label": "Buokrom", "value": "Buokrom"},
                ],
                value="Both", clearable=False,
                style={"width": "200px", "fontSize": "13px"},
            ),
        ], style={"display": "flex", "alignItems": "center",
                  "marginBottom": "16px"}),

        # Charts row 1
        html.Div([
            chart_card([
                section_header("Occupancy by phase"),
                dcc.Graph(id="occ-chart", config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={"flex": "1"}),
            chart_card([
                section_header("Nightly rate journey (GHS)"),
                dcc.Graph(figure=make_rate_fig(), config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={"flex": "1"}),
        ], className="chart-row", style={"display": "flex", "gap": "16px"}),

        # Chart row 2
        chart_card([
            section_header("Estimated monthly revenue by phase"),
            dcc.Graph(figure=make_revenue_impact_fig(),
                      config={"displayModeBar": False},
                      style={"height": "280px"}),
        ]),
    ])

def booking_page():
    return html.Div([
        # KPI row
        html.Div([
            kpi_card("Total revenue", f"₵{total_rev:,.0f}", BLUE),
            kpi_card("Barekese revenue", f"₵{bar_rev:,.0f}", BLUE, "All phases"),
            kpi_card("Buokrom revenue", f"₵{buo_rev:,.0f}", GREEN, "All phases"),
            kpi_card("Total bookings", f"{total_book:,}", GOLD),
        ], className="kpi-grid", style={"display": "grid",
                  "gridTemplateColumns": "repeat(4, 1fr)",
                  "gap": "12px", "marginBottom": "20px"}),

        # Filter
        html.Div([
            html.Label("Filter by property:", style={"fontSize": "12px",
                        "color": GREY, "marginRight": "10px", "fontWeight": "600"}),
            dcc.Dropdown(
                id="booking-filter",
                options=[
                    {"label": "Both", "value": "Both"},
                    {"label": "Barekese", "value": "Barekese"},
                    {"label": "Buokrom", "value": "Buokrom"},
                ],
                value="Both", clearable=False,
                style={"width": "200px", "fontSize": "13px"},
            ),
        ], style={"display": "flex", "alignItems": "center",
                  "marginBottom": "16px"}),

        # Revenue trend
        chart_card([
            section_header("Quarterly revenue trend"),
            dcc.Graph(id="rev-trend-chart", config={"displayModeBar": False},
                      style={"height": "300px"}),
        ]),

        # Bottom row
        html.Div([
            chart_card([
                section_header("Barekese — stays vs events"),
                dcc.Graph(figure=make_booking_type_fig(),
                          config={"displayModeBar": False},
                          style={"height": "260px"}),
            ], style={"flex": "1"}),
            chart_card([
                section_header("Weekday vs weekend revenue"),
                dcc.Graph(figure=make_weekday_weekend_fig(),
                          config={"displayModeBar": False},
                          style={"height": "260px"}),
            ], style={"flex": "1"}),
        ], className="chart-row", style={"display": "flex", "gap": "16px"}),
    ])

def portfolio_page():
    off = df_l[df_l["Location"] == "Offinso"]
    amr = df_l[df_l["Location"] == "Amrahia"]
    return html.Div([
        # KPI row
        html.Div([
            kpi_card("Total listings", str(total_list), BLUE),
            kpi_card("Combined portfolio value", f"₵{port_val/1e6:.1f}M", BLUE),
            kpi_card("Units sold", str(units_sold), GREEN, "Combined"),
            kpi_card("Offinso value", f"₵{off['Price_GHS'].sum()/1e6:.1f}M", GOLD),
            kpi_card("Amrahia value", f"₵{amr['Price_GHS'].sum()/1e6:.1f}M", BLUE),
        ], className="kpi-grid", style={"display": "grid",
                  "gridTemplateColumns": "repeat(5, 1fr)",
                  "gap": "12px", "marginBottom": "20px"}),

        # Charts
        html.Div([
            chart_card([
                section_header("Listings by status"),
                dcc.Graph(figure=make_portfolio_status_fig(),
                          config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={"flex": "1"}),
            chart_card([
                section_header("Property type mix"),
                dcc.Graph(figure=make_type_mix_fig(),
                          config={"displayModeBar": False},
                          style={"height": "300px"}),
            ], style={"flex": "1"}),
        ], className="chart-row", style={"display": "flex", "gap": "16px"}),

        # Listings table
        chart_card([
            section_header("All listings — Offinso & Amrahia"),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([
                        html.Th(col, style={
                            "padding": "8px 12px", "textAlign": "left",
                            "fontSize": "11px", "color": WHITE,
                            "background": BLUE, "fontWeight": "600",
                            "textTransform": "uppercase", "letterSpacing": "0.05em",
                        }) for col in ["ID", "Location", "Type", "Beds",
                                       "Price (GHS)", "Status"]
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(row["Listing_ID"], style={"padding": "7px 12px",
                                    "fontSize": "12px", "color": GREY}),
                            html.Td(row["Location"], style={"padding": "7px 12px",
                                    "fontSize": "12px", "fontWeight": "600",
                                    "color": BLUE}),
                            html.Td(row["Property_Type"], style={"padding": "7px 12px",
                                    "fontSize": "12px"}),
                            html.Td(str(int(row["Bedrooms"])) if pd.notna(row["Bedrooms"])
                                    else "—", style={"padding": "7px 12px",
                                    "fontSize": "12px", "textAlign": "center"}),
                            html.Td(f"₵{row['Price_GHS']:,.0f}",
                                    style={"padding": "7px 12px", "fontSize": "12px",
                                           "fontWeight": "600"}),
                            html.Td(style={
                                "padding": "4px 12px",
                            }, children=html.Span(row["Status"], style={
                                "background": STATUS_COLORS.get(row["Status"], GREY) + "20",
                                "color": STATUS_COLORS.get(row["Status"], GREY),
                                "padding": "3px 10px", "borderRadius": "12px",
                                "fontSize": "11px", "fontWeight": "600",
                            })),
                        ], style={
                            "borderBottom": f"1px solid {LIGHT}",
                            "background": WHITE if i % 2 == 0 else "#FAFBFF",
                        }) for i, (_, row) in enumerate(df_l.iterrows())
                    ]),
                ], style={"width": "100%", "borderCollapse": "collapse"}),
            ], style={"overflowX": "auto"}),
        ]),
    ])

# ── Callbacks ──────────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Output("tab-pricing", "style"),
    Output("tab-booking", "style"),
    Output("tab-portfolio", "style"),
    Input("tab-pricing", "n_clicks"),
    Input("tab-booking", "n_clicks"),
    Input("tab-portfolio", "n_clicks"),
    prevent_initial_call=False,
)
def render_page(n1, n2, n3):
    from dash import ctx
    trigger = ctx.triggered_id
    active = {**TAB_STYLE, "borderBottomColor": BLUE, "color": BLUE}
    inactive = TAB_STYLE
    if trigger == "tab-booking":
        return booking_page(), inactive, active, inactive
    elif trigger == "tab-portfolio":
        return portfolio_page(), inactive, inactive, active
    return pricing_page(), active, inactive, inactive

@callback(
    Output("occ-chart", "figure"),
    Input("property-filter", "value"),
    prevent_initial_call=False,
)
def update_occ(prop):
    return make_occupancy_fig(prop)

@callback(
    Output("rev-trend-chart", "figure"),
    Input("booking-filter", "value"),
    prevent_initial_call=False,
)
def update_rev(prop):
    return make_quarterly_revenue_fig(prop)

# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
