import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Last-Mile Delivery Performance Dashboard",
    page_icon="🚚",
    layout="wide"
)

# -----------------------------
# Data loading & cleaning
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Last_mile_Delivery_Data.csv")

    # Strip whitespace from all text columns (dataset has trailing spaces
    # like "Urban ", "High ", "motorcycle ")
    text_cols = ["Weather", "Traffic", "Vehicle", "Area", "Category"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Some rows store missing Traffic as the literal string "NaN"
    df["Traffic"] = df["Traffic"].replace("NaN", pd.NA)

    # Drop rows with missing values in key analysis columns
    df = df.dropna(subset=["Weather", "Traffic", "Agent_Rating", "Delivery_Time"])

    # Convert types
    df["Delivery_Time"] = pd.to_numeric(df["Delivery_Time"], errors="coerce")
    df["Agent_Age"] = pd.to_numeric(df["Agent_Age"], errors="coerce")
    df["Agent_Rating"] = pd.to_numeric(df["Agent_Rating"], errors="coerce")
    df = df.dropna(subset=["Delivery_Time", "Agent_Age", "Agent_Rating"])

    # Flag "delayed" deliveries: above the overall average delivery time
    avg_time = df["Delivery_Time"].mean()
    df["Is_Delayed"] = df["Delivery_Time"] > avg_time

    # Bucket agent rating into bands for easier comparison
    df["Rating_Band"] = pd.cut(
        df["Agent_Rating"],
        bins=[0, 3.5, 4.0, 4.5, 5.0, 10],
        labels=["<3.5", "3.5-4.0", "4.0-4.5", "4.5-5.0", "5.0+"]
    )

    return df


df = load_data()
overall_avg_time = df["Delivery_Time"].mean()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("🔍 Filters")

weather_options = sorted(df["Weather"].unique())
traffic_options = sorted(df["Traffic"].unique())
vehicle_options = sorted(df["Vehicle"].unique())
area_options = sorted(df["Area"].unique())
category_options = sorted(df["Category"].unique())

sel_weather = st.sidebar.multiselect("Weather", weather_options, default=weather_options)
sel_traffic = st.sidebar.multiselect("Traffic", traffic_options, default=traffic_options)
sel_vehicle = st.sidebar.multiselect("Vehicle Type", vehicle_options, default=vehicle_options)
sel_area = st.sidebar.multiselect("Area", area_options, default=area_options)
sel_category = st.sidebar.multiselect("Product Category", category_options, default=category_options)

if st.sidebar.button("Reset Filters"):
    st.rerun()

# Apply filters
filtered = df[
    df["Weather"].isin(sel_weather)
    & df["Traffic"].isin(sel_traffic)
    & df["Vehicle"].isin(sel_vehicle)
    & df["Area"].isin(sel_area)
    & df["Category"].isin(sel_category)
]

st.sidebar.markdown(f"**Records matching filters:** {len(filtered):,} / {len(df):,}")

# -----------------------------
# Header & KPI row
# -----------------------------
st.title("🚚 Last-Mile Delivery Performance Dashboard")
st.caption("Interactive analytics for delivery time, traffic, weather, vehicles, agents, areas, and product categories.")

if filtered.empty:
    st.warning("No data matches the current filter selection. Please broaden your filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Delivery Time", f"{filtered['Delivery_Time'].mean():.1f} min")
col2.metric("% Delayed Deliveries", f"{filtered['Is_Delayed'].mean() * 100:.1f}%")
col3.metric("Avg Agent Rating", f"{filtered['Agent_Rating'].mean():.2f}")
col4.metric("Total Orders", f"{len(filtered):,}")

st.divider()

# -----------------------------
# 1. Delay Analyzer
# -----------------------------
st.subheader("1️⃣ Delay Analyzer — Weather & Traffic Impact")
st.caption("Compares average delivery time across weather and traffic conditions to reveal where delays are concentrated.")

c1, c2 = st.columns(2)
with c1:
    weather_avg = filtered.groupby("Weather", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time", ascending=False)
    fig1 = px.bar(weather_avg, x="Weather", y="Delivery_Time",
                  title="Avg Delivery Time by Weather", color="Delivery_Time",
                  color_continuous_scale="Reds")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    traffic_avg = filtered.groupby("Traffic", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time", ascending=False)
    fig2 = px.bar(traffic_avg, x="Traffic", y="Delivery_Time",
                  title="Avg Delivery Time by Traffic", color="Delivery_Time",
                  color_continuous_scale="Oranges")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -----------------------------
# 2. Vehicle Comparison
# -----------------------------
st.subheader("2️⃣ Vehicle Comparison")
st.caption("Shows delivery speed differences by vehicle type to help optimise fleet allocation.")

vehicle_avg = filtered.groupby("Vehicle", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time")
fig3 = px.bar(vehicle_avg, x="Vehicle", y="Delivery_Time",
              title="Avg Delivery Time by Vehicle Type", color="Vehicle")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------------
# 3. Agent Performance Insights
# -----------------------------
st.subheader("3️⃣ Agent Performance Insights")
st.caption("Analyses agent ratings and age against delivery time to spot performance trends useful for training or staffing.")

c3, c4 = st.columns(2)
with c3:
    rating_avg = filtered.groupby("Rating_Band", observed=True, as_index=False)["Delivery_Time"].mean()
    fig4 = px.bar(rating_avg, x="Rating_Band", y="Delivery_Time",
                  title="Avg Delivery Time by Agent Rating Band")
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    fig5 = px.scatter(filtered, x="Agent_Age", y="Delivery_Time", color="Agent_Rating",
                       title="Agent Age vs Delivery Time", opacity=0.5,
                       color_continuous_scale="Viridis")
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# -----------------------------
# 4. Regional Bottleneck Finder
# -----------------------------
st.subheader("4️⃣ Regional Bottleneck Finder")
st.caption("Maps average delivery time and delay rate by area to highlight regions needing operational attention.")

area_stats = filtered.groupby("Area", as_index=False).agg(
    Avg_Delivery_Time=("Delivery_Time", "mean"),
    Delay_Pct=("Is_Delayed", lambda x: x.mean() * 100)
).sort_values("Avg_Delivery_Time", ascending=False)

fig6 = px.bar(area_stats, x="Area", y="Avg_Delivery_Time",
              title="Avg Delivery Time by Area", color="Delay_Pct",
              color_continuous_scale="Reds",
              labels={"Delay_Pct": "% Delayed"})
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# -----------------------------
# 5. Category Visualizer
# -----------------------------
st.subheader("5️⃣ Category Visualizer")
st.caption("Checks which product categories repeatedly face delays, helping prioritise packaging or handling fixes.")

cat_stats = filtered.groupby("Category", as_index=False)["Delivery_Time"].mean().sort_values("Delivery_Time", ascending=False)
fig7 = px.bar(cat_stats, x="Category", y="Delivery_Time",
              title="Avg Delivery Time by Product Category", color="Delivery_Time",
              color_continuous_scale="Blues")
st.plotly_chart(fig7, use_container_width=True)

st.divider()
st.caption("Built with Streamlit • Data source: Last-mile delivery dataset")
