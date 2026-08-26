import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

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
    df = pd.read_csv("Bird_Monitoring_Cleaned.csv")

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Bird_Monitoring_Cleaned.csv"

    if not file_path.exists():
        st.error(f"CSV file not found: {file_path}")
        st.stop()

    df = pd.read_csv(file_path)

    # Convert numeric columns
    numeric_columns = [
        "Year",
        "Temperature",
        "Humidity",
        "Initial_Three_Min_Cnt"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Convert date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        df["Month"] = df["Date"].dt.month
        df["Month_Name"] = df["Date"].dt.month_name()

    # Create season
    if "Month" in df.columns:

       def get_season(month):
            if month in [12, 1, 2]:
                return "Winter"
            elif month in [3, 4, 5]:
                return "Spring"
            elif month in [6, 7, 8]:
                return "Summer"
            else:
                return "Autumn"

        df["Season"] = df["Month"].apply(get_season)

    return df
df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🐦 Bird Species Observation Analysis")

st.markdown(
    "### Explore bird observations, species diversity, habitats, "
    "environmental conditions and conservation status."
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")


# Year filter
if "Year" in df.columns:

    years = sorted(
        df["Year"].dropna().unique()
    )

    selected_years = st.sidebar.multiselect(
        "Select Year",
        options=years,
        default=years
    )

else:
    selected_years = []


# Habitat filter
if "Location_Type" in df.columns:

    habitats = sorted(
        df["Location_Type"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_habitats = st.sidebar.multiselect(
        "Select Habitat",
        options=habitats,
        default=habitats
    )

else:
    selected_habitats = []


# Species filter
if "Common_Name" in df.columns:

    species = sorted(
        df["Common_Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_species = st.sidebar.multiselect(
        "Select Species",
        options=species
    )

else:
    selected_species = []


# Season filter
if "Season" in df.columns:

    seasons = [
        "Spring",
        "Summer",
        "Autumn",
        "Winter"
    ]

    selected_seasons = st.sidebar.multiselect(
        "Select Season",
        options=seasons,
        default=seasons
    )

else:
    selected_seasons = []


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if "Year" in filtered_df.columns and selected_years:
    filtered_df = filtered_df[
        filtered_df["Year"].isin(selected_years)
    ]


if "Location_Type" in filtered_df.columns and selected_habitats:
    filtered_df = filtered_df[
        filtered_df["Location_Type"].isin(selected_habitats)
    ]


if "Common_Name" in filtered_df.columns and selected_species:
    filtered_df = filtered_df[
        filtered_df["Common_Name"].isin(selected_species)
    ]


if "Season" in filtered_df.columns and selected_seasons:
    filtered_df = filtered_df[
        filtered_df["Season"].isin(selected_seasons)
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_observations = len(filtered_df)

if "Scientific_Name" in filtered_df.columns:
    unique_species = filtered_df["Scientific_Name"].nunique()
else:
    unique_species = 0


if "Site_Name" in filtered_df.columns:
    observation_sites = filtered_df["Site_Name"].nunique()
else:
    observation_sites = 0


if "Admin_Unit_Code" in filtered_df.columns:
    admin_units = filtered_df["Admin_Unit_Code"].nunique()
else:
    admin_units = 0


# Watchlist species
watchlist_species = 0

if "PIF_Watchlist_Status" in filtered_df.columns:

    watchlist = filtered_df[
        filtered_df["PIF_Watchlist_Status"]
        .astype(str)
        .str.upper()
        .isin(["TRUE", "YES", "1"])
    ]

    if "Scientific_Name" in watchlist.columns:
        watchlist_species = watchlist[
            "Scientific_Name"
        ].nunique()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Observations",
        f"{total_observations:,}"
    )

with col2:
    st.metric(
        "Unique Species",
        f"{unique_species:,}"
    )

with col3:
    st.metric(
        "Observation Sites",
        f"{observation_sites:,}"
    )

with col4:
    st.metric(
        "Administrative Units",
        f"{admin_units:,}"
    )

with col5:
    st.metric(
        "Watchlist Species",
        f"{watchlist_species:,}"
    )


st.divider()


# ============================================================
# CHART 1 - OBSERVATIONS BY YEAR
# ============================================================

st.subheader("📅 Bird Observations by Year")

if "Year" in filtered_df.columns:

    yearly_data = (
        filtered_df
        .groupby("Year")
        .size()
        .reset_index(name="Observations")
        .sort_values("Year")
    )

    fig_year = px.line(
        yearly_data,
        x="Year",
        y="Observations",
        markers=True,
        title="Observation Trend by Year"
    )

    fig_year.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Observations"
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )


# ============================================================
# CHART 2 - HABITAT
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🌳 Species by Habitat")

    if (
        "Location_Type" in filtered_df.columns
        and "Scientific_Name" in filtered_df.columns
    ):

        habitat_data = (
            filtered_df
            .groupby("Location_Type")["Scientific_Name"]
            .nunique()
            .reset_index(name="Species")
            .sort_values("Species", ascending=False)
        )

        fig_habitat = px.bar(
            habitat_data,
            x="Location_Type",
            y="Species",
            title="Unique Species by Habitat"
        )

        st.plotly_chart(
            fig_habitat,
            use_container_width=True
        )


# ============================================================
# CHART 3 - TOP SPECIES
# ============================================================

with col2:

    st.subheader("🐦 Top 10 Bird Species")

    if "Common_Name" in filtered_df.columns:

        top_species = (
            filtered_df["Common_Name"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_species.columns = [
            "Common_Name",
            "Observations"
        ]

        fig_species = px.bar(
            top_species,
            x="Observations",
            y="Common_Name",
            orientation="h",
            title="Top 10 Most Observed Species"
        )

        fig_species.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            )
        )

        st.plotly_chart(
            fig_species,
            use_container_width=True
        )


# ============================================================
# CHART 4 - SEASON
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🌦️ Observations by Season")

    if "Season" in filtered_df.columns:

        season_data = (
            filtered_df["Season"]
            .value_counts()
            .reindex(
                [
                    "Spring",
                    "Summer",
                    "Autumn",
                    "Winter"
                ],
                fill_value=0
            )
            .reset_index()
        )

        season_data.columns = [
            "Season",
            "Observations"
        ]

        fig_season = px.bar(
            season_data,
            x="Season",
            y="Observations",
            title="Bird Activity by Season"
        )

        st.plotly_chart(
            fig_season,
            use_container_width=True
        )


# ============================================================
# CHART 5 - IDENTIFICATION METHOD
# ============================================================

with col2:

    st.subheader("🔊 Identification Method")

    if "ID_Method" in filtered_df.columns:

        method_data = (
            filtered_df["ID_Method"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        method_data.columns = [
            "ID_Method",
            "Observations"
        ]

        fig_method = px.pie(
            method_data,
            names="ID_Method",
            values="Observations",
            title="Bird Identification Methods"
        )

        st.plotly_chart(
            fig_method,
            use_container_width=True
        )


# ============================================================
# CHART 6 - TEMPERATURE VS BIRD COUNT
# ============================================================

st.subheader("🌡️ Temperature vs Bird Activity")

if (
    "Temperature" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    temperature_df = filtered_df[
        [
            "Temperature",
            "Initial_Three_Min_Cnt"
        ]
    ].dropna()

    fig_temp = px.scatter(
        temperature_df,
        x="Temperature",
        y="Initial_Three_Min_Cnt",
        title="Temperature vs Initial Three-Minute Bird Count",
        opacity=0.6
    )

    fig_temp.update_layout(
        xaxis_title="Temperature",
        yaxis_title="Bird Count"
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )


# ============================================================
# CONSERVATION SECTION
# ============================================================

st.divider()

st.subheader("🛡️ Conservation Insights")

col1, col2 = st.columns(2)


with col1:

    if "PIF_Watchlist_Status" in filtered_df.columns:

        watchlist_counts = (
            filtered_df["PIF_Watchlist_Status"]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        watchlist_counts.columns = [
            "Status",
            "Observations"
        ]

        fig_watchlist = px.pie(
            watchlist_counts,
            names="Status",
            values="Observations",
            title="PIF Watchlist Status"
        )

        st.plotly_chart(
            fig_watchlist,
            use_container_width=True
        )


with col2:

    if "Regional_Stewardship_Status" in filtered_df.columns:

        stewardship_counts = (
            filtered_df[
                "Regional_Stewardship_Status"
            ]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        stewardship_counts.columns = [
            "Status",
            "Observations"
        ]

        fig_stewardship = px.pie(
            stewardship_counts,
            names="Status",
            values="Observations",
            title="Regional Stewardship Status"
        )

        st.plotly_chart(
            fig_stewardship,
            use_container_width=True
        )


# ============================================================
# DATA PREVIEW
# ============================================================

st.divider()

st.subheader("📋 Filtered Dataset")

st.write(
    f"Showing {len(filtered_df):,} observations"
)

st.dataframe(
    filtered_df,
    use_container_width=True
)