import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bird Species Observation Analysis",
    page_icon="🐦",
    layout="wide"
)

st.title("🐦 Bird Species Observation Analysis Dashboard")

st.markdown(
    "Analyze bird observations, species diversity, locations, "
    "environmental conditions and observation trends."
)

# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv("bird_species.csv")

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

# =========================================================
# DATA CLEANING
# =========================================================

# Convert Date
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

# Convert Year
if "Year" in df.columns:
    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce"
    )

# Convert bird count
if "Initial_Three_Min_Cnt" in df.columns:
    df["Initial_Three_Min_Cnt"] = pd.to_numeric(
        df["Initial_Three_Min_Cnt"],
        errors="coerce"
    ).fillna(0)

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

filtered_df = df.copy()

# ---------------------------------------------------------
# Species Filter
# ---------------------------------------------------------

if "Common_Name" in df.columns:

    species_list = sorted(
        df["Common_Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_species = st.sidebar.multiselect(
        "🐦 Select Bird Species",
        species_list,
        default=species_list
    )

    filtered_df = filtered_df[
        filtered_df["Common_Name"]
        .astype(str)
        .isin(selected_species)
    ]

# ---------------------------------------------------------
# Site Filter
# ---------------------------------------------------------

if "Site_Name" in df.columns:

    site_list = sorted(
        df["Site_Name"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_sites = st.sidebar.multiselect(
        "📍 Select Site",
        site_list,
        default=site_list
    )

    filtered_df = filtered_df[
        filtered_df["Site_Name"]
        .astype(str)
        .isin(selected_sites)
    ]

# ---------------------------------------------------------
# Year Filter
# ---------------------------------------------------------

if "Year" in df.columns:

    year_values = sorted(
        df["Year"]
        .dropna()
        .unique()
    )

    if len(year_values) > 0:

        selected_years = st.sidebar.multiselect(
            "📅 Select Year",
            year_values,
            default=year_values
        )

        filtered_df = filtered_df[
            filtered_df["Year"]
            .isin(selected_years)
        ]

# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📊 Key Performance Indicators")

# Total records
total_observations = len(filtered_df)

# Total bird count
if "Initial_Three_Min_Cnt" in filtered_df.columns:

    total_birds = int(
        filtered_df["Initial_Three_Min_Cnt"]
        .sum()
    )

else:
    total_birds = 0

# Total species
if "Common_Name" in filtered_df.columns:

    total_species = (
        filtered_df["Common_Name"]
        .nunique()
    )

else:
    total_species = 0

# Total sites
if "Site_Name" in filtered_df.columns:

    total_sites = (
        filtered_df["Site_Name"]
        .nunique()
    )

else:
    total_sites = 0


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Observation Records",
        f"{total_observations:,}"
    )

with col2:

    st.metric(
        "Total Birds Observed",
        f"{total_birds:,}"
    )

with col3:

    st.metric(
        "Bird Species",
        f"{total_species:,}"
    )

with col4:

    st.metric(
        "Observation Sites",
        f"{total_sites:,}"
    )

# =========================================================
# CHART 1 - TOP BIRD SPECIES
# =========================================================

st.subheader("🐦 Top Bird Species")

if (
    "Common_Name" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    species_counts = (
        filtered_df
        .groupby("Common_Name")["Initial_Three_Min_Cnt"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    species_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Top 10 Bird Species by Number Observed"
    )

    ax.set_xlabel("Bird Species")
    ax.set_ylabel("Bird Count")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# =========================================================
# CHART 2 - BIRDS BY SITE
# =========================================================

st.subheader("📍 Bird Observations by Site")

if (
    "Site_Name" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    site_counts = (
        filtered_df
        .groupby("Site_Name")["Initial_Three_Min_Cnt"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    site_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Top 10 Observation Sites"
    )

    ax.set_xlabel("Site")
    ax.set_ylabel("Bird Count")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# =========================================================
# CHART 3 - MONTHLY TREND
# =========================================================

st.subheader("📈 Monthly Bird Observation Trend")

if (
    "Date" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    trend_df = filtered_df.copy()

    trend_df = trend_df.dropna(
        subset=["Date"]
    )

    trend_df["Month"] = (
        trend_df["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_trend = (
        trend_df
        .groupby("Month")["Initial_Three_Min_Cnt"]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    monthly_trend.plot(
        kind="line",
        marker="o",
        ax=ax
    )

    ax.set_title(
        "Monthly Bird Observation Trend"
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Bird Count")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# =========================================================
# CHART 4 - LOCATION TYPE
# =========================================================

st.subheader("🌳 Birds by Location Type")

if (
    "Location_Type" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    habitat_counts = (
        filtered_df
        .groupby("Location_Type")[
            "Initial_Three_Min_Cnt"
        ]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    habitat_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Bird Observations by Location Type"
    )

    ax.set_xlabel("Location Type")
    ax.set_ylabel("Bird Count")

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# =========================================================
# CHART 5 - TOP SPECIES DISTRIBUTION
# =========================================================

st.subheader("🥧 Species Distribution")

if (
    "Common_Name" in filtered_df.columns
    and "Initial_Three_Min_Cnt" in filtered_df.columns
):

    distribution = (
        filtered_df
        .groupby("Common_Name")[
            "Initial_Three_Min_Cnt"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    fig, ax = plt.subplots(
        figsize=(7, 7)
    )

    distribution.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    ax.set_title(
        "Top 5 Species Distribution"
    )

    st.pyplot(fig)

# =========================================================
# BUSINESS / ANALYTICAL RECOMMENDATIONS
# =========================================================

st.subheader("💡 Business Recommendations")

if len(filtered_df) > 0:

    # -----------------------------------------------------
    # Top Species
    # -----------------------------------------------------

    if (
        "Common_Name" in filtered_df.columns
        and "Initial_Three_Min_Cnt" in filtered_df.columns
    ):

        species_summary = (
            filtered_df
            .groupby("Common_Name")[
                "Initial_Three_Min_Cnt"
            ]
            .sum()
            .sort_values(ascending=False)
        )

        if len(species_summary) > 0:

            top_species = species_summary.index[0]
            top_species_count = species_summary.iloc[0]

            st.write(
                f"🔹 **Prioritize monitoring of {top_species}**, "
                f"which has the highest recorded bird count "
                f"of **{int(top_species_count):,}**."
            )

    # -----------------------------------------------------
    # Top Site
    # -----------------------------------------------------

    if (
        "Site_Name" in filtered_df.columns
        and "Initial_Three_Min_Cnt" in filtered_df.columns
    ):

        site_summary = (
            filtered_df
            .groupby("Site_Name")[
                "Initial_Three_Min_Cnt"
            ]
            .sum()
            .sort_values(ascending=False)
        )

        if len(site_summary) > 0:

            top_site = site_summary.index[0]

            st.write(
                f"🔹 **Prioritize conservation activities "
                f"at {top_site}**, where bird observations "
                f"are highest."
            )

    # -----------------------------------------------------
    # Species Diversity
    # -----------------------------------------------------

    st.write(
        f"🔹 The selected data contains "
        f"**{total_species:,} different bird species**. "
        f"Areas with high species diversity should receive "
        f"greater conservation attention."
    )

    # -----------------------------------------------------
    # Monitoring
    # -----------------------------------------------------

    st.write(
        "🔹 Conduct additional surveys at sites with "
        "lower observation counts to understand whether "
        "the difference is caused by habitat conditions "
        "or monitoring frequency."
    )

    # -----------------------------------------------------
    # Seasonal Monitoring
    # -----------------------------------------------------

    st.write(
        "🔹 Use monthly observation trends to identify "
        "periods of higher bird activity and plan field "
        "monitoring accordingly."
    )

    # -----------------------------------------------------
    # Data Quality
    # -----------------------------------------------------

    st.write(
        "🔹 Maintain consistent records for species, "
        "site, date, weather conditions and bird counts "
        "to improve future biodiversity analysis."
    )

else:

    st.warning(
        "No data available for the selected filters."
    )

# =========================================================
# CONCLUSION
# =========================================================

st.subheader("📌 Conclusion")

st.write(
    """
    The Bird Species Observation Analysis Dashboard provides
    a comprehensive view of bird observations across different
    species, sites and location types. KPI cards summarize the
    total observation records, total birds observed, species
    diversity and observation sites.

    The charts help identify the most frequently observed
    species, important observation sites, monthly trends and
    location types with higher bird activity.

    These insights can support biodiversity monitoring,
    conservation planning, habitat management and efficient
    allocation of field-survey resources.
    """
)
