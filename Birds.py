import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bird Species Observation Analysis",
    page_icon="🐦",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    forest_df = pd.read_csv(
        "Bird_Monitoring_Data_Forest.csv"
    )

    grassland_df = pd.read_csv(
        "Bird_Monitoring_Data_GRASSLAND.csv"
    )

    # Add habitat
    forest_df["Habitat"] = "Forest"
    grassland_df["Habitat"] = "Grassland"

    # Combine datasets
    df = pd.concat(
        [forest_df, grassland_df],
        ignore_index=True
    )

    # Remove unwanted columns
    df = df.loc[
        :,
        ~df.columns.str.contains("^Unnamed")
    ]

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Year
    if "Year" not in df.columns:
        df["Year"] = df["Date"].dt.year

    # Month
    df["Month"] = df["Date"].dt.month_name()

    # Season
    df["Season"] = df["Date"].dt.month.map({
        12: "Winter",
        1: "Winter",
        2: "Winter",
        3: "Spring",
        4: "Spring",
        5: "Spring",
        6: "Summer",
        7: "Summer",
        8: "Summer",
        9: "Autumn",
        10: "Autumn",
        11: "Autumn"
    })

    return df


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title(
    "🐦 Bird Species Observation Analysis Dashboard"
)

st.markdown(
    """
    **Forest & Grassland Bird Monitoring**

    Analyze bird observations, species diversity, habitat patterns,
    environmental conditions and conservation priorities.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")


# Habitat
habitat_options = sorted(
    df["Habitat"].dropna().unique()
)

selected_habitat = st.sidebar.multiselect(
    "🌳 Habitat",
    habitat_options,
    default=habitat_options
)


# Year
year_options = sorted(
    df["Year"].dropna().unique()
)

selected_year = st.sidebar.multiselect(
    "📅 Year",
    year_options,
    default=year_options
)


# Species
species_options = sorted(
    df["Common_Name"].dropna().unique()
)

selected_species = st.sidebar.multiselect(
    "🐦 Species",
    species_options
)


# Location
location_options = sorted(
    df["Location_Type"].dropna().unique()
)

selected_location = st.sidebar.multiselect(
    "📍 Location Type",
    location_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if selected_habitat:
    filtered_df = filtered_df[
        filtered_df["Habitat"].isin(selected_habitat)
    ]


if selected_year:
    filtered_df = filtered_df[
        filtered_df["Year"].isin(selected_year)
    ]


if selected_species:
    filtered_df = filtered_df[
        filtered_df["Common_Name"].isin(selected_species)
    ]


if selected_location:
    filtered_df = filtered_df[
        filtered_df["Location_Type"].isin(selected_location)
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_observations = len(filtered_df)

unique_species = filtered_df[
    "Scientific_Name"
].nunique()

forest_species = filtered_df[
    filtered_df["Habitat"] == "Forest"
]["Scientific_Name"].nunique()

grassland_species = filtered_df[
    filtered_df["Habitat"] == "Grassland"
]["Scientific_Name"].nunique()


# Conservation species
conservation_df = filtered_df[
    (
        filtered_df["PIF_Watchlist_Status"]
        .astype(str)
        .str.upper()
        .isin(["TRUE", "YES"])
    )
    |
    (
        filtered_df["Regional_Stewardship_Status"]
        .astype(str)
        .str.upper()
        .isin(["TRUE", "YES"])
    )
]

conservation_species = conservation_df[
    "Scientific_Name"
].nunique()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "🐦 Total Observations",
    f"{total_observations:,}"
)

col2.metric(
    "🦜 Unique Species",
    f"{unique_species:,}"
)

col3.metric(
    "🌲 Forest Species",
    f"{forest_species:,}"
)

col4.metric(
    "🌾 Grassland Species",
    f"{grassland_species:,}"
)

col5.metric(
    "⚠️ Conservation Species",
    f"{conservation_species:,}"
)


st.divider()


# ============================================================
# CHART 1 - HABITAT
# ============================================================

st.subheader("🌳 Bird Observations by Habitat")

habitat_data = (
    filtered_df
    .groupby("Habitat")
    .size()
    .reset_index(name="Observations")
)

fig1 = px.bar(
    habitat_data,
    x="Habitat",
    y="Observations",
    text="Observations",
    title="Forest vs Grassland Observations"
)

fig1.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ============================================================
# CHART 2 - TOP SPECIES
# ============================================================

st.subheader("🐦 Top 10 Most Observed Species")

species_data = (
    filtered_df["Common_Name"]
    .value_counts()
    .head(10)
    .reset_index()
)

species_data.columns = [
    "Species",
    "Observations"
]

fig2 = px.bar(
    species_data.sort_values("Observations"),
    x="Observations",
    y="Species",
    orientation="h",
    text="Observations",
    title="Top 10 Bird Species"
)

fig2.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ============================================================
# CHART 3 - SPECIES DIVERSITY
# ============================================================

st.subheader("🌿 Species Diversity by Habitat")

diversity_data = (
    filtered_df
    .groupby("Habitat")["Scientific_Name"]
    .nunique()
    .reset_index()
)

diversity_data.columns = [
    "Habitat",
    "Unique Species"
]

fig3 = px.bar(
    diversity_data,
    x="Habitat",
    y="Unique Species",
    text="Unique Species",
    title="Unique Bird Species by Habitat"
)

fig3.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ============================================================
# CHART 4 - YEARLY TREND
# ============================================================

st.subheader("📈 Year-wise Bird Observation Trend")

year_data = (
    filtered_df
    .groupby("Year")
    .size()
    .reset_index(name="Observations")
    .sort_values("Year")
)

fig4 = px.line(
    year_data,
    x="Year",
    y="Observations",
    markers=True,
    title="Bird Observations by Year"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ============================================================
# CHART 5 - SEASON
# ============================================================

st.subheader("🌤️ Seasonal Bird Activity")

season_order = [
    "Spring",
    "Summer",
    "Autumn",
    "Winter"
]

season_data = (
    filtered_df
    .groupby("Season")
    .size()
    .reindex(season_order)
    .reset_index(name="Observations")
)

fig5 = px.bar(
    season_data,
    x="Season",
    y="Observations",
    text="Observations",
    title="Bird Observations by Season"
)

fig5.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# ============================================================
# CHART 6 - TEMPERATURE
# ============================================================

st.subheader("🌡️ Temperature vs Bird Activity")

temperature_data = (
    filtered_df
    .groupby("Temperature")
    .size()
    .reset_index(name="Observations")
)

fig6 = px.scatter(
    temperature_data,
    x="Temperature",
    y="Observations",
    title="Bird Activity vs Temperature"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)


# ============================================================
# CHART 7 - HUMIDITY
# ============================================================

st.subheader("💧 Humidity vs Bird Activity")

humidity_data = (
    filtered_df
    .groupby("Humidity")
    .size()
    .reset_index(name="Observations")
)

fig7 = px.scatter(
    humidity_data,
    x="Humidity",
    y="Observations",
    title="Bird Activity vs Humidity"
)

st.plotly_chart(
    fig7,
    use_container_width=True
)


# ============================================================
# CHART 8 - IDENTIFICATION METHOD
# ============================================================

st.subheader("🔍 Bird Identification Methods")

id_data = (
    filtered_df["ID_Method"]
    .value_counts()
    .reset_index()
)

id_data.columns = [
    "ID Method",
    "Observations"
]

fig8 = px.pie(
    id_data,
    names="ID Method",
    values="Observations",
    title="Identification Method Distribution"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)


# ============================================================
# CHART 9 - DISTANCE
# ============================================================

st.subheader("📏 Observation Distance")

distance_data = (
    filtered_df["Distance"]
    .value_counts()
    .reset_index()
)

distance_data.columns = [
    "Distance",
    "Observations"
]

fig9 = px.bar(
    distance_data,
    x="Distance",
    y="Observations",
    text="Observations",
    title="Bird Observations by Distance"
)

fig9.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig9,
    use_container_width=True
)


# ============================================================
# CHART 10 - FLYOVER
# ============================================================

st.subheader("🪽 Flyover Observations")

flyover_data = (
    filtered_df["Flyover_Observed"]
    .value_counts()
    .reset_index()
)

flyover_data.columns = [
    "Flyover",
    "Observations"
]

fig10 = px.pie(
    flyover_data,
    names="Flyover",
    values="Observations",
    title="Flyover Observation Distribution"
)

st.plotly_chart(
    fig10,
    use_container_width=True
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.divider()

st.header("💡 Business Insights & Recommendations")


# -------- Insight 1 --------

if len(habitat_data) > 0:

    top_habitat = habitat_data.loc[
        habitat_data["Observations"].idxmax(),
        "Habitat"
    ]

    top_habitat_count = habitat_data[
        habitat_data["Habitat"] == top_habitat
    ]["Observations"].iloc[0]

    st.success(
        f"🌳 **Habitat Insight:** "
        f"{top_habitat} has the highest number of recorded observations "
        f"with {top_habitat_count:,} observations."
    )


# -------- Insight 2 --------

if len(species_data) > 0:

    top_species = species_data.iloc[0]["Species"]

    top_species_count = species_data.iloc[0]["Observations"]

    st.info(
        f"🐦 **Species Insight:** "
        f"{top_species} is among the most frequently observed species "
        f"with {top_species_count:,} observations."
    )


# -------- Insight 3 --------

if len(diversity_data) > 0:

    diverse_habitat = diversity_data.loc[
        diversity_data["Unique Species"].idxmax(),
        "Habitat"
    ]

    diverse_count = diversity_data[
        diversity_data["Habitat"] == diverse_habitat
    ]["Unique Species"].iloc[0]

    st.warning(
        f"🌿 **Biodiversity Insight:** "
        f"{diverse_habitat} shows the highest observed species diversity "
        f"with {diverse_count:,} unique species."
    )


# -------- Insight 4 --------

if len(season_data.dropna()) > 0:

    season_clean = season_data.dropna(
        subset=["Observations"]
    )

    if len(season_clean) > 0:

        active_season = season_clean.loc[
            season_clean["Observations"].idxmax(),
            "Season"
        ]

        active_count = season_clean[
            season_clean["Season"] == active_season
        ]["Observations"].iloc[0]

        st.success(
            f"📅 **Seasonal Insight:** "
            f"{active_season} has the highest observation activity "
            f"with {active_count:,} observations."
        )


# -------- Insight 5 --------

if conservation_species > 0:

    st.error(
        f"⚠️ **Conservation Insight:** "
        f"{conservation_species:,} species in the filtered dataset "
        f"are identified as conservation-priority species."
    )

else:

    st.info(
        "ℹ️ **Conservation Insight:** "
        "No conservation-priority species were identified "
        "under the current filters."
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("🎯 Business Recommendations")

recommendations = [
    "Prioritize habitat protection in areas showing high bird diversity.",
    "Increase monitoring of frequently observed and conservation-priority species.",
    "Conduct additional observations during seasons with higher bird activity.",
    "Use environmental conditions such as temperature and humidity when planning monitoring activities.",
    "Continue repeated observations to identify long-term biodiversity trends.",
    "Support habitat restoration and land-management decisions using observation patterns."
]

for recommendation in recommendations:

    st.write(
        "✅ " + recommendation
    )


# ============================================================
# CONSERVATION TABLE
# ============================================================

st.divider()

st.subheader("⚠️ Conservation Priority Species")

if len(conservation_df) > 0:

    conservation_table = (
        conservation_df[
            [
                "Common_Name",
                "Scientific_Name",
                "PIF_Watchlist_Status",
                "Regional_Stewardship_Status"
            ]
        ]
        .drop_duplicates()
        .sort_values("Common_Name")
    )

    st.dataframe(
        conservation_table,
        use_container_width=True
    )

else:

    st.info(
        "No conservation-priority species found "
        "for the selected filters."
    )


# ============================================================
# FILTERED DATA
# ============================================================

st.divider()

st.subheader("📋 Filtered Observation Data")

st.write(
    f"Showing **{len(filtered_df):,}** observations"
)

st.dataframe(
    filtered_df,
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🐦 Bird Species Observation Analysis | "
    "Forest & Grassland Monitoring"
)