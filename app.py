import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title="GIS Disaster Dashboard", layout="wide")

DATA_PATH = "D:/GIS DASHBOARD/Data/Processed/final_tehsil_risk_map.geojson"

@st.cache_data
def load_data():
    gdf = gpd.read_file(DATA_PATH)
    return gdf

gdf = load_data()

# Fix column names after GeoJSON merge
gdf = gdf.rename(columns={
    "province_x": "province",
    "district_x": "district"
})

# Drop duplicate columns if they exist
gdf = gdf.drop(columns=["province_y", "district_y"], errors="ignore")



st.title("GIS-Based Disaster Decision Support Dashboard")
st.caption("Rule-based multi-hazard risk dashboard using rainfall, temperature, and earthquake data")

# Sidebar
st.sidebar.header("Filters")

risk_filter = st.sidebar.multiselect(
    "Select Risk Level",
    options=gdf["overall_risk_level"].dropna().unique(),
    default=list(gdf["overall_risk_level"].dropna().unique())
)

province_filter = st.sidebar.multiselect(
    "Select Province",
    options=gdf["province"].dropna().unique(),
    default=list(gdf["province"].dropna().unique())
)

filtered = gdf[
    (gdf["overall_risk_level"].isin(risk_filter)) &
    (gdf["province"].isin(province_filter))
]

# Risk colors
def get_color(level):
    if level == "Critical":
        return "red"
    elif level == "High":
        return "orange"
    elif level == "Medium":
        return "yellow"
    elif level == "Low":
        return "green"
    else:
        return "gray"

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tehsils", len(filtered))
col2.metric("Critical Risk", len(filtered[filtered["overall_risk_level"] == "Critical"]))
col3.metric("High Risk", len(filtered[filtered["overall_risk_level"] == "High"]))
col4.metric("No Data", len(filtered[filtered["overall_risk_level"] == "No Data"]))

# Map
st.subheader("Interactive Risk Map")

m = folium.Map(location=[30, 70], zoom_start=5, tiles="cartodbpositron")

folium.GeoJson(
    filtered,
    style_function=lambda feature: {
        "fillColor": get_color(feature["properties"].get("overall_risk_level")),
        "color": "black",
        "weight": 0.4,
        "fillOpacity": 0.65,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "province",
            "district",
            "tehsil",
            "overall_risk_level",
            "overall_risk_score",
            "flood_score",
            "heatwave_score",
            "earthquake_score",
            "recommendation",
        ],
        aliases=[
            "Province:",
            "District:",
            "Tehsil:",
            "Risk Level:",
            "Overall Score:",
            "Flood Score:",
            "Heatwave Score:",
            "Earthquake Score:",
            "Recommendation:",
        ],
        localize=True,
    ),
).add_to(m)

st_folium(m, width=1300, height=600)

# Charts
st.subheader("Risk Analysis")

c1, c2 = st.columns(2)

with c1:
    risk_count = filtered["overall_risk_level"].value_counts().reset_index()
    risk_count.columns = ["Risk Level", "Count"]

    fig1 = px.bar(
        risk_count,
        x="Risk Level",
        y="Count",
        title="Tehsils by Risk Level"
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    top_risk = filtered.sort_values("overall_risk_score", ascending=False).head(10)

    fig2 = px.bar(
        top_risk,
        x="tehsil",
        y="overall_risk_score",
        color="overall_risk_level",
        title="Top 10 High-Risk Tehsils"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Tehsil profile
st.subheader("Tehsil Risk Profile")

selected_tehsil = st.selectbox(
    "Select Tehsil",
    options=filtered["tehsil"].dropna().unique()
)

profile = filtered[filtered["tehsil"] == selected_tehsil].iloc[0]

p1, p2, p3 = st.columns(3)

p1.metric("Flood Score", round(profile["flood_score"], 2))
p2.metric("Heatwave Score", round(profile["heatwave_score"], 2))
p3.metric("Earthquake Score", round(profile["earthquake_score"], 2))

st.write("### Recommendation")
st.info(profile["recommendation"])

st.write("### Raw Indicators")
st.dataframe(
    filtered[
        [
            "province",
            "district",
            "tehsil",
            "avg_rainfall",
            "max_rainfall",
            "avg_temperature",
            "max_temperature",
            "max_magnitude",
            "earthquake_count",
            "overall_risk_score",
            "overall_risk_level",
        ]
    ],
    use_container_width=True
)