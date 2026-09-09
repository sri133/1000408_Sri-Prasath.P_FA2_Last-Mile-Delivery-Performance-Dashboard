import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_FILE = "Last_mile_Delivery_Data.csv"

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Delivery Analytics | LogiSight",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# NEON DARK THEME — CSS + ANIMATIONS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root{
    --neon-cyan:#00f6ff;
    --neon-pink:#ff2bd6;
    --neon-purple:#a742ff;
    --neon-green:#39ff88;
    --bg-dark:#070912;
    --card-dark:#0f1526;
}

.stApp{
    background: radial-gradient(circle at 15% 10%, #12172b 0%, #070912 55%, #030308 100%);
    color:#e8ecff;
    font-family:'Rajdhani', sans-serif;
}
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0b0e1c 0%, #05060d 100%);
    border-right:1px solid rgba(0,246,255,0.25);
}
h1,h2,h3{
    font-family:'Orbitron', sans-serif !important;
}

/* Glowing animated title */
.neon-title{
    font-family:'Orbitron', sans-serif;
    font-size:2.3rem;
    font-weight:900;
    text-align:center;
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple), var(--neon-pink), var(--neon-cyan));
    background-size:300% auto;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation: shine 6s linear infinite, glow-pulse 3s ease-in-out infinite;
    padding:8px 0 2px 0;
}
@keyframes shine{
    to{ background-position:300% center; }
}
@keyframes glow-pulse{
    0%,100%{ filter: drop-shadow(0 0 6px rgba(0,246,255,0.35)); }
    50%{ filter: drop-shadow(0 0 18px rgba(255,43,214,0.55)); }
}
.neon-subtitle{
    text-align:center;
    color:#9fb0d9;
    font-size:1rem;
    letter-spacing:1px;
    margin-bottom:1.4rem;
    animation: fadeIn 1.6s ease-in;
}
@keyframes fadeIn{
    from{ opacity:0; transform:translateY(-6px);}
    to{ opacity:1; transform:translateY(0);}
}

/* Metric cards */
div[data-testid="stMetric"]{
    background: linear-gradient(145deg, var(--card-dark), #0a0e1c);
    border:1px solid rgba(0,246,255,0.25);
    border-radius:14px;
    padding:14px 10px 8px 10px;
    box-shadow: 0 0 12px rgba(0,246,255,0.08), inset 0 0 20px rgba(167,66,255,0.05);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    animation: fadeIn 0.8s ease;
}
div[data-testid="stMetric"]:hover{
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 0 22px rgba(255,43,214,0.35), 0 0 10px rgba(0,246,255,0.25);
    border-color: rgba(255,43,214,0.6);
}
div[data-testid="stMetricValue"]{
    color: var(--neon-cyan) !important;
    text-shadow: 0 0 10px rgba(0,246,255,0.6);
}
div[data-testid="stMetricLabel"]{
    color:#b7c3ea !important;
}

/* Section header pill */
.section-pill{
    display:inline-block;
    padding:6px 18px;
    margin: 22px 0 4px 0;
    border-radius:999px;
    background: linear-gradient(90deg, rgba(0,246,255,0.12), rgba(167,66,255,0.12));
    border:1px solid rgba(0,246,255,0.35);
    font-family:'Orbitron', sans-serif;
    font-size:0.95rem;
    color:#e8ecff;
    box-shadow: 0 0 14px rgba(0,246,255,0.12);
    animation: fadeIn 0.7s ease;
}
.section-caption{
    color:#8ea0cf;
    font-size:0.88rem;
    margin-bottom:10px;
}

/* Buttons */
.stButton>button{
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink));
    color:white;
    border:none;
    border-radius:10px;
    font-weight:600;
    letter-spacing:0.5px;
    box-shadow: 0 0 12px rgba(255,43,214,0.4);
    transition: all 0.25s ease;
}
.stButton>button:hover{
    box-shadow: 0 0 22px rgba(0,246,255,0.6);
    transform: scale(1.03);
}

/* Tabs */
button[data-baseweb="tab"]{
    font-family:'Orbitron', sans-serif;
    font-size:0.8rem;
    color:#9fb0d9 !important;
}
button[data-baseweb="tab"][aria-selected="true"]{
    color: var(--neon-cyan) !important;
    border-bottom: 2px solid var(--neon-cyan) !important;
}

/* Scrollbar */
::-webkit-scrollbar{ width:8px; }
::-webkit-scrollbar-thumb{ background: linear-gradient(var(--neon-cyan), var(--neon-purple)); border-radius:8px; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_dark"
NEON_SEQUENCE = ["#00f6ff", "#ff2bd6", "#a742ff", "#39ff88", "#ffd93d", "#ff6b6b", "#4dd0e1"]


def style_fig(fig, title=None):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani, sans-serif", color="#e8ecff", size=13),
        title=dict(text=title, font=dict(family="Orbitron, sans-serif", size=15, color="#00f6ff")) if title else None,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=55, l=10, r=10, b=10),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    return fig


def section(title, caption):
    st.markdown(f'<div class="section-pill">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)


# =========================================================
# DATA LOADING — cache tied to the actual file's content,
# so any dataset update is picked up automatically.
# =========================================================
def _file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


@st.cache_data(show_spinner="Loading and cleaning delivery data...")
def load_data(file_hash: str, path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    text_cols = ["Weather", "Traffic", "Vehicle", "Area", "Category"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    df["Traffic"] = df["Traffic"].replace("NaN", pd.NA)

    df = df.dropna(subset=["Weather", "Traffic", "Agent_Rating", "Delivery_Time"])

    df["Delivery_Time"] = pd.to_numeric(df["Delivery_Time"], errors="coerce")
    df["Agent_Age"] = pd.to_numeric(df["Agent_Age"], errors="coerce")
    df["Agent_Rating"] = pd.to_numeric(df["Agent_Rating"], errors="coerce")
    df = df.dropna(subset=["Delivery_Time", "Agent_Age", "Agent_Rating"])

    # Dates / times
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Order_Time_parsed"] = pd.to_datetime(df["Order_Time"], errors="coerce", format="%H:%M:%S")
    df["Pickup_Time_parsed"] = pd.to_datetime(df["Pickup_Time"], errors="coerce", format="%H:%M:%S")
    df["Pickup_Lag_Min"] = (df["Pickup_Time_parsed"] - df["Order_Time_parsed"]).dt.total_seconds() / 60
    df.loc[df["Pickup_Lag_Min"] < 0, "Pickup_Lag_Min"] += 24 * 60  # midnight wraparound
    df["Order_Hour"] = df["Order_Time_parsed"].dt.hour
    df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)

    # --- MATH: mean/std based delay flag (z-score style threshold,
    # not an arbitrary cutoff): delayed if delivery time is above the mean.
    mean_time = df["Delivery_Time"].mean()
    std_time = df["Delivery_Time"].std()
    df["Z_Score"] = (df["Delivery_Time"] - mean_time) / std_time
    df["Is_Delayed"] = df["Delivery_Time"] > mean_time
    df["Is_Outlier"] = df["Z_Score"].abs() > 3  # >3 std devs = statistical outlier

    df["Rating_Band"] = pd.cut(
        df["Agent_Rating"],
        bins=[0, 3.5, 4.0, 4.5, 5.0, 10],
        labels=["<3.5", "3.5-4.0", "4.0-4.5", "4.5-5.0", "5.0+"]
    )

    return df


df = load_data(_file_hash(DATA_FILE), DATA_FILE)

# =========================================================
# SIDEBAR FILTERS  (with a reset button that actually works)
# =========================================================
FILTER_COLS = {
    "weather": "Weather",
    "traffic": "Traffic",
    "vehicle": "Vehicle",
    "area": "Area",
    "category": "Category",
}
FILTER_OPTIONS = {key: sorted(df[col].unique()) for key, col in FILTER_COLS.items()}

for key, opts in FILTER_OPTIONS.items():
    state_key = f"filter_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = opts


def reset_filters():
    for key, opts in FILTER_OPTIONS.items():
        st.session_state[f"filter_{key}"] = opts


st.sidebar.markdown("### 🔍 FILTER CONSOLE")
st.sidebar.multiselect("Weather", FILTER_OPTIONS["weather"], key="filter_weather")
st.sidebar.multiselect("Traffic", FILTER_OPTIONS["traffic"], key="filter_traffic")
st.sidebar.multiselect("Vehicle Type", FILTER_OPTIONS["vehicle"], key="filter_vehicle")
st.sidebar.multiselect("Area", FILTER_OPTIONS["area"], key="filter_area")
st.sidebar.multiselect("Product Category", FILTER_OPTIONS["category"], key="filter_category")
st.sidebar.button("🔄 Reset Filters", on_click=reset_filters, width='stretch')

filtered = df[
    df["Weather"].isin(st.session_state["filter_weather"])
    & df["Traffic"].isin(st.session_state["filter_traffic"])
    & df["Vehicle"].isin(st.session_state["filter_vehicle"])
    & df["Area"].isin(st.session_state["filter_area"])
    & df["Category"].isin(st.session_state["filter_category"])
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Matching records:** `{len(filtered):,} / {len(df):,}`")
st.sidebar.download_button(
    "⬇️ Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_delivery_data.csv",
    mime="text/csv",
    width='stretch',
)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="neon-title">🚚 LAST-MILE DELIVERY ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<div class="neon-subtitle">LOGISIGHT ANALYTICS — LIVE DATA-DRIVEN PERFORMANCE COMMAND CENTER</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No data matches the current filter selection. Please broaden your filters.")
    st.stop()

# =========================================================
# KPI ROW  (all computed live from filtered data)
# =========================================================
mean_dt = filtered["Delivery_Time"].mean()
median_dt = filtered["Delivery_Time"].median()
std_dt = filtered["Delivery_Time"].std()
pct_delayed = filtered["Is_Delayed"].mean() * 100
outlier_ct = int(filtered["Is_Outlier"].sum())

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg Delivery Time", f"{mean_dt:.1f} min")
k2.metric("Median Delivery Time", f"{median_dt:.1f} min")
k3.metric("Std. Deviation (σ)", f"{std_dt:.1f} min")
k4.metric("% Delayed (> mean)", f"{pct_delayed:.1f}%")
k5.metric("Statistical Outliers", f"{outlier_ct} (|z|>3)")

# =========================================================
# TABS
# =========================================================
tab_overview, tab_delay, tab_agents, tab_regional, tab_trends, tab_stats, tab_map = st.tabs(
    ["📊 Overview", "🌦️ Delay Analyzer", "🏍️ Vehicle & Agents",
     "🗺️ Regional & Category", "📈 Trends & Distribution",
     "🧮 Statistics", "🌍 Live Map"]
)

# ---------------------------------------------------------
# TAB: OVERVIEW  (the 4 newly requested visuals)
# ---------------------------------------------------------
with tab_overview:
    section("① MONTHLY TRENDS", "Average delivery time per month, with a 3-month moving average to smooth out noise (a rolling-mean calculation, not a static value).")
    monthly = filtered.dropna(subset=["Order_Month"]).groupby("Order_Month", as_index=False)["Delivery_Time"].mean().sort_values("Order_Month")
    monthly["Rolling_Avg"] = monthly["Delivery_Time"].rolling(window=3, min_periods=1).mean()
    fig_month = go.Figure()
    fig_month.add_trace(go.Scatter(x=monthly["Order_Month"], y=monthly["Delivery_Time"],
                                    mode="lines+markers", name="Monthly Avg",
                                    line=dict(color="#00f6ff", width=3), marker=dict(size=7)))
    fig_month.add_trace(go.Scatter(x=monthly["Order_Month"], y=monthly["Rolling_Avg"],
                                    mode="lines", name="3-Month Moving Avg",
                                    line=dict(color="#ff2bd6", width=2, dash="dash")))
    st.plotly_chart(style_fig(fig_month, "Monthly Delivery Time Trend"), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        section("② DELIVERY TIME DISTRIBUTION", "Histogram of delivery times with a fitted normal (Gaussian) curve — computed from the sample mean μ and std dev σ.")
        x_vals = np.linspace(filtered["Delivery_Time"].min(), filtered["Delivery_Time"].max(), 200)
        pdf = (1 / (std_dt * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_vals - mean_dt) / std_dt) ** 2)
        bin_width = (filtered["Delivery_Time"].max() - filtered["Delivery_Time"].min()) / 40
        pdf_scaled = pdf * len(filtered) * bin_width

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=filtered["Delivery_Time"], nbinsx=40, name="Deliveries",
                                         marker_color="#a742ff", opacity=0.75))
        fig_hist.add_trace(go.Scatter(x=x_vals, y=pdf_scaled, mode="lines", name="Normal Fit (μ,σ)",
                                       line=dict(color="#39ff88", width=3)))
        fig_hist.add_vline(x=mean_dt, line_dash="dot", line_color="#00f6ff",
                            annotation_text=f"μ={mean_dt:.0f}", annotation_font_color="#00f6ff")
        fig_hist.add_vline(x=median_dt, line_dash="dot", line_color="#ffd93d",
                            annotation_text=f"median={median_dt:.0f}", annotation_font_color="#ffd93d")
        st.plotly_chart(style_fig(fig_hist, "Delivery Time Distribution"), width='stretch')

    with c2:
        section("③ % LATE DELIVERIES", "Percentage of deliveries above the mean delivery time, grouped by traffic and weather.")
        late_traffic = filtered.groupby("Traffic", as_index=False)["Is_Delayed"].mean()
        late_traffic["pct"] = late_traffic["Is_Delayed"] * 100
        late_traffic["Group"] = "Traffic: " + late_traffic["Traffic"]

        late_weather = filtered.groupby("Weather", as_index=False)["Is_Delayed"].mean()
        late_weather["pct"] = late_weather["Is_Delayed"] * 100
        late_weather["Group"] = "Weather: " + late_weather["Weather"]

        late_combo = pd.concat([
            late_traffic[["Group", "pct"]].rename(columns={"Group": "Condition"}),
            late_weather[["Group", "pct"]].rename(columns={"Group": "Condition"}),
        ]).sort_values("pct", ascending=True)

        fig_late = px.bar(late_combo, x="pct", y="Condition", orientation="h",
                           color="pct", color_continuous_scale=["#39ff88", "#ffd93d", "#ff2bd6"],
                           labels={"pct": "% Delayed"})
        st.plotly_chart(style_fig(fig_late, "% Late Deliveries by Condition"), width='stretch')

    section("④ AGENT WORKLOAD PER AREA", "Delivery volume handled in each area — a proxy for agent workload since the dataset has no unique agent ID, only per-delivery age/rating.")
    area_ct = filtered.groupby("Area", as_index=False).size().rename(columns={"size": "Deliveries"})
    fig_area_donut = px.pie(area_ct, names="Area", values="Deliveries", hole=0.55,
                             color_discrete_sequence=NEON_SEQUENCE)
    fig_area_donut.update_traces(textinfo="percent+label", pull=[0.03] * len(area_ct))
    st.plotly_chart(style_fig(fig_area_donut, "Delivery Volume Share by Area"), width='stretch')

# ---------------------------------------------------------
# TAB: DELAY ANALYZER
# ---------------------------------------------------------
with tab_delay:
    section("DELAY ANALYZER", "Compares average delivery time and its variability across weather and traffic conditions.")
    c1, c2 = st.columns(2)
    with c1:
        w_stats = filtered.groupby("Weather", as_index=False)["Delivery_Time"].agg(["mean", "std"]).reset_index()
        fig = px.bar(w_stats, x="Weather", y="mean", error_y="std",
                     color="mean", color_continuous_scale="Plasma",
                     labels={"mean": "Avg Delivery Time (min)"})
        st.plotly_chart(style_fig(fig, "Avg Delivery Time ± σ by Weather"), width='stretch')
    with c2:
        fig = px.violin(filtered, x="Traffic", y="Delivery_Time", color="Traffic",
                         box=True, points=False, color_discrete_sequence=NEON_SEQUENCE)
        st.plotly_chart(style_fig(fig, "Delivery Time Spread by Traffic (Violin Plot)"), width='stretch')

    section("WEATHER × TRAFFIC HEATMAP", "Average delivery time for every weather/traffic combination — reveals the true 'worst-case' pairing.")
    pivot = filtered.pivot_table(index="Weather", columns="Traffic", values="Delivery_Time", aggfunc="mean")
    fig_heat = px.imshow(pivot, text_auto=".0f", color_continuous_scale="Inferno",
                          labels=dict(color="Avg Min"))
    st.plotly_chart(style_fig(fig_heat, "Avg Delivery Time: Weather × Traffic"), width='stretch')

# ---------------------------------------------------------
# TAB: VEHICLE & AGENTS
# ---------------------------------------------------------
with tab_agents:
    section("VEHICLE COMPARISON", "Speed comparison across vehicle types to guide fleet allocation.")
    veh_stats = filtered.groupby("Vehicle", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time")
    fig = px.bar(veh_stats, x="Vehicle", y="Delivery_Time", color="Vehicle",
                 color_discrete_sequence=NEON_SEQUENCE)
    st.plotly_chart(style_fig(fig, "Avg Delivery Time by Vehicle"), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        section("AGENT RATING vs SPEED", "Average delivery time by rating band.")
        rband = filtered.groupby("Rating_Band", observed=True, as_index=False)["Delivery_Time"].mean()
        fig = px.bar(rband, x="Rating_Band", y="Delivery_Time", color="Delivery_Time",
                     color_continuous_scale="Turbo")
        st.plotly_chart(style_fig(fig, "Avg Delivery Time by Rating Band"), width='stretch')
    with c2:
        section("AGE vs DELIVERY TIME + TREND LINE", "Linear regression fit (least-squares) shows whether age predicts delivery speed.")
        x = filtered["Agent_Age"].values
        y = filtered["Delivery_Time"].values
        slope, intercept = np.polyfit(x, y, 1)
        corr = np.corrcoef(x, y)[0, 1]
        r_squared = corr ** 2
        x_line = np.linspace(x.min(), x.max(), 50)
        y_line = slope * x_line + intercept

        fig = go.Figure()
        fig.add_trace(go.Scattergl(x=x, y=y, mode="markers", name="Deliveries",
                                    marker=dict(color=filtered["Agent_Rating"], colorscale="Viridis",
                                                size=5, opacity=0.5, showscale=True,
                                                colorbar=dict(title="Rating"))))
        fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name="Trend Line",
                                  line=dict(color="#ff2bd6", width=3)))
        st.plotly_chart(style_fig(fig, f"Age vs Delivery Time  (R²={r_squared:.3f}, slope={slope:.2f})"), width='stretch')
        st.caption(f"Regression equation: Delivery_Time ≈ {slope:.2f} × Age + {intercept:.1f}  |  Pearson r = {corr:.3f}")

# ---------------------------------------------------------
# TAB: REGIONAL & CATEGORY
# ---------------------------------------------------------
with tab_regional:
    section("REGIONAL BOTTLENECK FINDER", "Average delivery time and delay rate by area.")
    area_stats = filtered.groupby("Area", as_index=False).agg(
        Avg_Delivery_Time=("Delivery_Time", "mean"),
        Delay_Pct=("Is_Delayed", lambda x: x.mean() * 100),
        Orders=("Delivery_Time", "count"),
    ).sort_values("Avg_Delivery_Time", ascending=False)
    fig = px.bar(area_stats, x="Area", y="Avg_Delivery_Time", color="Delay_Pct",
                 color_continuous_scale="Sunsetdark", labels={"Delay_Pct": "% Delayed"},
                 hover_data=["Orders"])
    st.plotly_chart(style_fig(fig, "Avg Delivery Time & Delay % by Area"), width='stretch')

    section("CATEGORY VISUALIZER", "Which product categories face repeat delays, broken down by area (treemap).")
    cat_area = filtered.groupby(["Area", "Category"], as_index=False)["Delivery_Time"].mean()
    fig = px.treemap(cat_area, path=["Area", "Category"], values="Delivery_Time",
                      color="Delivery_Time", color_continuous_scale="Magma")
    st.plotly_chart(style_fig(fig, "Avg Delivery Time by Area → Category"), width='stretch')

# ---------------------------------------------------------
# TAB: TRENDS & DISTRIBUTION (extra depth)
# ---------------------------------------------------------
with tab_trends:
    section("ORDER HOUR vs DELAY RISK", "Does the hour an order is placed affect delay risk more than weather does?")
    hour_stats = filtered.dropna(subset=["Order_Hour"]).groupby("Order_Hour", as_index=False)["Is_Delayed"].mean()
    hour_stats["pct"] = hour_stats["Is_Delayed"] * 100
    fig = px.area(hour_stats, x="Order_Hour", y="pct", markers=True,
                   color_discrete_sequence=["#00f6ff"])
    fig.update_traces(line_color="#00f6ff", fillcolor="rgba(0,246,255,0.15)")
    st.plotly_chart(style_fig(fig, "% Delayed by Order Hour"), width='stretch')

    section("PICKUP LAG vs TRAVEL TIME", "How much of total delivery time is pickup lag versus the actual trip.")
    lag_df = filtered.dropna(subset=["Pickup_Lag_Min"])
    lag_df = lag_df[(lag_df["Pickup_Lag_Min"] >= 0) & (lag_df["Pickup_Lag_Min"] < 120)]
    fig = px.scatter(lag_df, x="Pickup_Lag_Min", y="Delivery_Time", color="Vehicle",
                      opacity=0.5, color_discrete_sequence=NEON_SEQUENCE)
    st.plotly_chart(style_fig(fig, "Pickup Lag vs Total Delivery Time"), width='stretch')

# ---------------------------------------------------------
# TAB: STATISTICS  (course = Mathematics for AI → show the math)
# ---------------------------------------------------------
with tab_stats:
    section("DESCRIPTIVE STATISTICS", "Full statistical summary of delivery time for the current filter selection.")
    desc = filtered["Delivery_Time"].describe().to_frame("Delivery_Time")
    desc.loc["variance"] = filtered["Delivery_Time"].var()
    desc.loc["skewness"] = filtered["Delivery_Time"].skew()
    desc.loc["kurtosis"] = filtered["Delivery_Time"].kurt()
    st.dataframe(desc.style.format("{:.2f}"), width='stretch')

    section("CORRELATION MATRIX", "Pearson correlation coefficients between numeric variables — shows which factors move together.")
    corr_matrix = filtered[["Agent_Age", "Agent_Rating", "Delivery_Time", "Pickup_Lag_Min"]].corr()
    fig = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    st.plotly_chart(style_fig(fig, "Correlation Heatmap"), width='stretch')

    section("OUTLIER DETECTION (Z-SCORE)", "Deliveries flagged as statistical outliers when |z-score| > 3, i.e. more than 3 standard deviations from the mean.")
    outliers_df = filtered[filtered["Is_Outlier"]][
        ["Order_ID", "Area", "Vehicle", "Weather", "Traffic", "Delivery_Time", "Z_Score"]
    ].sort_values("Z_Score", ascending=False)

    if outliers_df.empty:
        max_abs_z = filtered["Z_Score"].abs().max()
        st.success(
            f"No statistical outliers found — every delivery in the current selection falls within "
            f"±3 standard deviations of the mean (largest observed |z-score| = {max_abs_z:.2f}). "
            f"This means delivery times are consistently distributed with no extreme spikes."
        )
        st.caption("Showing the 10 most extreme deliveries anyway, for reference:")
        st.dataframe(
            filtered[["Order_ID", "Area", "Vehicle", "Weather", "Traffic", "Delivery_Time", "Z_Score"]]
            .reindex(filtered["Z_Score"].abs().sort_values(ascending=False).index).head(10),
            width='stretch'
        )
    else:
        st.dataframe(outliers_df.head(20), width='stretch')

# ---------------------------------------------------------
# TAB: LIVE MAP
# ---------------------------------------------------------
with tab_map:
    section("DELIVERY ROUTE MAP", "Store pickup points vs drop-off points for a sample of filtered deliveries.")
    sample = filtered.sample(min(1500, len(filtered)), random_state=42)
    fig_map = go.Figure()

    # Newer Plotly versions (7.x) replaced the Mapbox-based "Scattermapbox"
    # trace with the MapLibre-based "Scattermap" trace. This still works on
    # older Plotly versions too (added in 5.24+), so it's the safe choice.
    if hasattr(go, "Scattermap"):
        ScatterMapTrace = go.Scattermap
        map_layout_key = "map"
    else:
        ScatterMapTrace = go.Scattermapbox
        map_layout_key = "mapbox"

    fig_map.add_trace(ScatterMapTrace(
        lat=sample["Store_Latitude"], lon=sample["Store_Longitude"],
        mode="markers", marker=dict(size=6, color="#00f6ff"), name="Store"
    ))
    fig_map.add_trace(ScatterMapTrace(
        lat=sample["Drop_Latitude"], lon=sample["Drop_Longitude"],
        mode="markers", marker=dict(size=6, color="#ff2bd6"), name="Drop-off"
    ))
    fig_map.update_layout(
        **{map_layout_key: dict(
            style="carto-darkmatter",
            center=dict(lat=sample["Store_Latitude"].mean(), lon=sample["Store_Longitude"].mean()),
            zoom=3.2,
        )},
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, l=0, r=0, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0.4)")
    )
    st.plotly_chart(fig_map, width='stretch')

st.markdown("---")
st.caption("Built with Streamlit • Live-computed from Last_mile_Delivery_Data.csv • LogiSight Analytics")
