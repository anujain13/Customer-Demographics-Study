import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Demographics Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (dark purple theme matching reference) ────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0e0b1f; color: #e0d9f7; }
    [data-testid="stSidebar"] { background-color: #1a1330; }
    [data-testid="stSidebar"] * { color: #e0d9f7 !important; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1540 0%, #2a1f55 100%);
        border: 1px solid #4a3d80;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #a78bfa;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #9ca3af;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Section headers */
    .section-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #c4b5fd;
        letter-spacing: 0.06em;
        border-bottom: 1px solid #3b2d6e;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }

    /* Dashboard title */
    .dash-title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #f3f0ff;
        background: linear-gradient(90deg, #7c3aed, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly { background: transparent !important; }

    /* Hide default streamlit header */
    header[data-testid="stHeader"] { background: #0e0b1f; }

    /* Divider */
    hr { border-color: #2d2260; }

    /* Selectbox / filter labels */
    label { color: #c4b5fd !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
import os

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

# Try same folder as script first, then let user upload
script_dir = os.path.dirname(os.path.abspath(__file__))
default_csv = os.path.join(script_dir, "shopping_trends_updated.csv")

if os.path.exists(default_csv):
    df = load_data(default_csv)
else:
    st.markdown("### 📂 Upload your dataset")
    uploaded = st.file_uploader("Upload `shopping_trends_updated.csv`", type="csv")
    if uploaded is None:
        st.info("Please upload the CSV file to continue.")
        st.stop()
    df = pd.read_csv(uploaded)

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Filter Customers By")

gender_options = ["All"] + sorted(df["Gender"].unique().tolist())
sel_gender = st.sidebar.selectbox("Gender", gender_options)

category_options = ["All"] + sorted(df["Category"].unique().tolist())
sel_category = st.sidebar.selectbox("Category", category_options)

season_options = ["All"] + sorted(df["Season"].unique().tolist())
sel_season = st.sidebar.selectbox("Season", season_options)

sub_options = ["All"] + sorted(df["Subscription Status"].unique().tolist())
sel_sub = st.sidebar.selectbox("Subscription Status", sub_options)

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

st.sidebar.markdown("---")
st.sidebar.markdown("**Promo Code Used**")
promo_options = st.sidebar.multiselect("", df["Promo Code Used"].unique().tolist(),
                                        default=df["Promo Code Used"].unique().tolist())

# ── Apply filters ────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_gender != "All":       fdf = fdf[fdf["Gender"] == sel_gender]
if sel_category != "All":     fdf = fdf[fdf["Category"] == sel_category]
if sel_season != "All":       fdf = fdf[fdf["Season"] == sel_season]
if sel_sub != "All":          fdf = fdf[fdf["Subscription Status"] == sel_sub]
fdf = fdf[(fdf["Age"] >= age_range[0]) & (fdf["Age"] <= age_range[1])]
if promo_options:             fdf = fdf[fdf["Promo Code Used"].isin(promo_options)]

# ── Color palette ────────────────────────────────────────────────────────────
COLORS  = ["#7c3aed", "#a78bfa", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]
BG      = "rgba(0,0,0,0)"
PAPER   = "rgba(0,0,0,0)"
FONT    = "#e0d9f7"
GRID    = "rgba(75,60,130,0.3)"

def base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(size=12, color="#c4b5fd"), x=0, xanchor="left"),
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color=FONT, size=11),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )

def axis_style():
    return dict(gridcolor=GRID, zerolinecolor=GRID,
                tickfont=dict(color="#9ca3af", size=10), showline=False)

# ── Top metrics ──────────────────────────────────────────────────────────────
total_customers  = len(fdf)
avg_purchase     = fdf["Purchase Amount (USD)"].mean()
avg_age          = fdf["Age"].mean()
avg_rating       = fdf["Review Rating"].mean()
sub_rate         = (fdf["Subscription Status"] == "Yes").mean() * 100
avg_prev         = fdf["Previous Purchases"].mean()

st.markdown('<p class="dash-title">🛍️ CUSTOMER DEMOGRAPHICS STUDY</p>', unsafe_allow_html=True)
st.markdown("---")

m1, m2, m3, m4, m5, m6 = st.columns(6)
for col, val, lbl in zip(
    [m1, m2, m3, m4, m5, m6],
    [f"{total_customers:,}", f"${avg_purchase:.2f}", f"{avg_age:.1f}",
     f"{avg_rating:.2f}", f"{sub_rate:.1f}%", f"{avg_prev:.1f}"],
    ["Total Customers", "Avg Purchase (USD)", "Avg Age",
     "Avg Review Rating", "Subscription Rate", "Avg Prev. Purchases"]
):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Category bar | Gender donut | Age-Purchase scatter ────────────────
r1c1, r1c2, r1c3 = st.columns([1.6, 1, 1.4])

with r1c1:
    st.markdown('<p class="section-title">Category-Wise Purchase Volume</p>', unsafe_allow_html=True)
    cat_data = fdf.groupby("Category").agg(
        Count=("Customer ID", "count"),
        Revenue=("Purchase Amount (USD)", "sum")
    ).reset_index().sort_values("Revenue", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=cat_data["Category"], x=cat_data["Count"],
        name="Count", orientation="h",
        marker_color=COLORS[0], text=cat_data["Count"],
        textposition="outside", textfont=dict(color=FONT, size=10)
    ))
    fig.add_trace(go.Bar(
        y=cat_data["Category"], x=cat_data["Revenue"],
        name="Revenue ($)", orientation="h",
        marker_color=COLORS[2], text=cat_data["Revenue"].apply(lambda x: f"${x:,.0f}"),
        textposition="outside", textfont=dict(color=FONT, size=10),
        visible=False
    ))
    fig.update_layout(**base_layout(),
        barmode="group", height=250,
        xaxis=axis_style(), yaxis=dict(tickfont=dict(color="#9ca3af", size=10)),
        updatemenus=[dict(
            type="buttons", direction="right", x=0.7, y=1.12,
            buttons=[
                dict(label="Count",   method="update", args=[{"visible": [True, False]}]),
                dict(label="Revenue", method="update", args=[{"visible": [False, True]}]),
            ],
            font=dict(size=9, color=FONT),
            bgcolor="#2a1f55", bordercolor="#4a3d80"
        )]
    )
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.markdown('<p class="section-title">Gender Distribution</p>', unsafe_allow_html=True)
    gender_data = fdf["Gender"].value_counts().reset_index()
    fig2 = px.pie(gender_data, names="Gender", values="count",
                  color_discrete_sequence=[COLORS[0], COLORS[4], COLORS[2]])
    fig2.update_traces(hole=0.55, textinfo="percent+label",
                       textfont=dict(size=10, color=FONT))
    fig2.update_layout(**base_layout(), height=250,
                       showlegend=True,
                       legend=dict(orientation="h", y=-0.05, font=dict(size=9)))
    st.plotly_chart(fig2, use_container_width=True)

with r1c3:
    st.markdown('<p class="section-title">Age vs Purchase Amount</p>', unsafe_allow_html=True)
    fig3 = px.scatter(fdf, x="Age", y="Purchase Amount (USD)",
                      color="Category", size="Review Rating",
                      color_discrete_sequence=COLORS, opacity=0.65)
    fig3.update_layout(**base_layout(), height=250,
                       xaxis=axis_style(), yaxis=axis_style(),
                       showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ── Row 2: Season trend | Payment methods | Subscription impact ──────────────
r2c1, r2c2, r2c3 = st.columns([1.3, 1, 1.2])

with r2c1:
    st.markdown('<p class="section-title">Seasonal Purchase Trend by Category</p>', unsafe_allow_html=True)
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    season_cat = fdf.groupby(["Season", "Category"])["Purchase Amount (USD)"].sum().reset_index()
    season_cat["Season"] = pd.Categorical(season_cat["Season"], categories=season_order, ordered=True)
    season_cat = season_cat.sort_values("Season")

    fig4 = px.line(season_cat, x="Season", y="Purchase Amount (USD)", color="Category",
                   color_discrete_sequence=COLORS, markers=True)
    fig4.update_traces(line_width=2, marker_size=6)
    fig4.update_layout(**base_layout(), height=240,
                       xaxis=axis_style(), yaxis=axis_style(),
                       legend=dict(font=dict(size=8), orientation="h", y=-0.25))
    st.plotly_chart(fig4, use_container_width=True)

with r2c2:
    st.markdown('<p class="section-title">Payment Method Breakdown</p>', unsafe_allow_html=True)
    pay_data = fdf["Payment Method"].value_counts().reset_index()
    fig5 = px.bar(pay_data, y="Payment Method", x="count", orientation="h",
                  color="count", color_continuous_scale=["#4a3d80", "#a78bfa"])
    fig5.update_layout(**base_layout(), height=240,
                       xaxis=axis_style(), yaxis=dict(tickfont=dict(color="#9ca3af", size=9)),
                       coloraxis_showscale=False)
    fig5.update_traces(text=pay_data["count"], textposition="outside",
                       textfont=dict(size=9, color=FONT))
    st.plotly_chart(fig5, use_container_width=True)

with r2c3:
    st.markdown('<p class="section-title">Subscription vs Non-Subscription Spend</p>', unsafe_allow_html=True)
    sub_grp = fdf.groupby("Subscription Status").agg(
        Avg_Purchase=("Purchase Amount (USD)", "mean"),
        Avg_Rating=("Review Rating", "mean"),
        Count=("Customer ID", "count")
    ).reset_index()

    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        x=sub_grp["Subscription Status"], y=sub_grp["Avg_Purchase"],
        name="Avg Purchase ($)", marker_color=COLORS[0],
        text=sub_grp["Avg_Purchase"].round(1), textposition="outside",
        textfont=dict(size=10, color=FONT)
    ))
    fig6.add_trace(go.Bar(
        x=sub_grp["Subscription Status"], y=sub_grp["Avg_Rating"] * 15,
        name="Avg Rating (×15)", marker_color=COLORS[2],
        text=sub_grp["Avg_Rating"].round(2), textposition="outside",
        textfont=dict(size=10, color=FONT)
    ))
    fig6.update_layout(**base_layout(), height=240, barmode="group",
                       xaxis=axis_style(), yaxis=axis_style())
    st.plotly_chart(fig6, use_container_width=True)

# ── Row 3: Frequency heatmap | Discount impact | Top locations ──────────────
r3c1, r3c2, r3c3 = st.columns([1.4, 1.1, 1])

with r3c1:
    st.markdown('<p class="section-title">Purchase Frequency by Category & Season</p>', unsafe_allow_html=True)
    freq_heat = fdf.groupby(["Category", "Season"])["Customer ID"].count().reset_index()
    freq_pivot = freq_heat.pivot(index="Category", columns="Season", values="Customer ID").fillna(0)
    season_cols = [c for c in ["Spring", "Summer", "Fall", "Winter"] if c in freq_pivot.columns]
    freq_pivot = freq_pivot[season_cols]

    fig7 = go.Figure(go.Heatmap(
        z=freq_pivot.values, x=freq_pivot.columns.tolist(), y=freq_pivot.index.tolist(),
        colorscale=[[0, "#1e1540"], [0.5, "#7c3aed"], [1, "#c4b5fd"]],
        text=freq_pivot.values.astype(int),
        texttemplate="%{text}", textfont=dict(size=10),
        showscale=True,
        colorbar=dict(tickfont=dict(color=FONT, size=9), len=0.9)
    ))
    fig7.update_layout(**base_layout(), height=240,
                       xaxis=dict(tickfont=dict(color="#9ca3af", size=10)),
                       yaxis=dict(tickfont=dict(color="#9ca3af", size=10)))
    st.plotly_chart(fig7, use_container_width=True)

with r3c2:
    st.markdown('<p class="section-title">Impact of Discount & Promo on Avg Purchase</p>', unsafe_allow_html=True)
    disc_promo = fdf.groupby(["Discount Applied", "Promo Code Used"])["Purchase Amount (USD)"].mean().reset_index()
    disc_promo["Group"] = disc_promo["Discount Applied"] + " / " + disc_promo["Promo Code Used"]
    fig8 = px.bar(disc_promo, x="Group", y="Purchase Amount (USD)",
                  color="Group", color_discrete_sequence=COLORS,
                  text=disc_promo["Purchase Amount (USD)"].round(1))
    fig8.update_traces(textposition="outside", textfont=dict(size=9, color=FONT))
    fig8.update_layout(**base_layout("Discount Applied / Promo Code"), height=240,
                       xaxis=dict(tickfont=dict(color="#9ca3af", size=9), tickangle=-20),
                       yaxis=axis_style(), showlegend=False)
    st.plotly_chart(fig8, use_container_width=True)

with r3c3:
    st.markdown('<p class="section-title">Top 10 Locations by Revenue</p>', unsafe_allow_html=True)
    loc_data = fdf.groupby("Location")["Purchase Amount (USD)"].sum().nlargest(10).reset_index()
    fig9 = px.bar(loc_data, y="Location", x="Purchase Amount (USD)", orientation="h",
                  color="Purchase Amount (USD)",
                  color_continuous_scale=["#4a3d80", "#06b6d4"])
    fig9.update_layout(**base_layout(), height=240,
                       xaxis=axis_style(),
                       yaxis=dict(tickfont=dict(color="#9ca3af", size=9)),
                       coloraxis_showscale=False)
    st.plotly_chart(fig9, use_container_width=True)

# ── Row 4: Review rating dist | Shipping type | Freq of purchases ────────────
r4c1, r4c2, r4c3 = st.columns([1, 1, 1.1])

with r4c1:
    st.markdown('<p class="section-title">Review Rating Distribution</p>', unsafe_allow_html=True)
    fig10 = px.histogram(fdf, x="Review Rating", nbins=20,
                         color_discrete_sequence=[COLORS[0]])
    fig10.update_traces(marker_line_color="#a78bfa", marker_line_width=1)
    fig10.update_layout(**base_layout(), height=220,
                        xaxis=axis_style(), yaxis=axis_style(),
                        bargap=0.05)
    st.plotly_chart(fig10, use_container_width=True)

with r4c2:
    st.markdown('<p class="section-title">Shipping Type Preference</p>', unsafe_allow_html=True)
    ship_data = fdf["Shipping Type"].value_counts().reset_index()
    fig11 = px.pie(ship_data, names="Shipping Type", values="count",
                   color_discrete_sequence=COLORS, hole=0.45)
    fig11.update_traces(textinfo="percent+label", textfont=dict(size=9, color=FONT))
    fig11.update_layout(**base_layout(), height=220,
                        legend=dict(font=dict(size=8), orientation="h", y=-0.1))
    st.plotly_chart(fig11, use_container_width=True)

with r4c3:
    st.markdown('<p class="section-title">Purchase Frequency vs Avg Spend</p>', unsafe_allow_html=True)
    freq_spend = fdf.groupby("Frequency of Purchases").agg(
        Avg_Spend=("Purchase Amount (USD)", "mean"),
        Count=("Customer ID", "count")
    ).reset_index().sort_values("Avg_Spend", ascending=False)
    fig12 = go.Figure()
    fig12.add_trace(go.Bar(
        x=freq_spend["Frequency of Purchases"], y=freq_spend["Avg_Spend"],
        marker_color=COLORS[1],
        text=freq_spend["Avg_Spend"].round(1), textposition="outside",
        textfont=dict(size=9, color=FONT), name="Avg Spend"
    ))
    fig12.add_trace(go.Scatter(
        x=freq_spend["Frequency of Purchases"], y=freq_spend["Count"],
        mode="lines+markers", name="Count", yaxis="y2",
        line=dict(color=COLORS[2], width=2), marker=dict(size=6)
    ))
    fig12.update_layout(**base_layout(), height=220,
                        xaxis=dict(tickfont=dict(color="#9ca3af", size=9), tickangle=-25),
                        yaxis=axis_style(),
                        yaxis2=dict(overlaying="y", side="right",
                                    tickfont=dict(color=COLORS[2], size=9),
                                    gridcolor="rgba(0,0,0,0)"),
                        legend=dict(font=dict(size=9), orientation="h", y=1.15))
    st.plotly_chart(fig12, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='color:#6b7280;font-size:0.72rem;text-align:center;'>"
    f"Showing <b style='color:#a78bfa'>{len(fdf):,}</b> of "
    f"<b style='color:#a78bfa'>{len(df):,}</b> customers · "
    f"Customer Demographics Study · Codtech IT Solutions Pvt. Ltd.</p>",
    unsafe_allow_html=True
)
