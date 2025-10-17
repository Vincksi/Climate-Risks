import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Column Names for reference 
COL_PLANT_NAME = 'Plant name (English)_x'
COL_OWNER = 'Owner'
COL_COUNTRY = 'Country/Area_x'
COL_CAPACITY_TTPA = 'Nominal crude steel capacity (ttpa)'
COL_COORDINATES = 'Coordinates'

# Derived Column Names 
COL_CAPACITY_MTPA = 'Capacity_Mtpa'
COL_LATITUDE = 'lat'
COL_LONGITUDE = 'Longitude'

#Page setup
st.set_page_config(
    page_title="Global Steel Plants Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data loading & cleaning
DATA_FILE = 'steel_plants.csv'

@st.cache_data
def load_and_clean_data(file_path):
    """Loads the original steel plants data and performs necessary cleaning."""
    df = pd.read_csv(file_path)

    # Convert capacity to numeric, coercing errors (like 'unknown') to NaN
    df[COL_CAPACITY_MTPA] = pd.to_numeric(df[COL_CAPACITY_TTPA], errors='coerce') / 1000

    # Split 'Coordinates' (e.g., "36.7539610, 6.2444200")
    df[[COL_LATITUDE, COL_LONGITUDE]] = df[COL_COORDINATES].str.split(', ', expand=True)

    # Convert to numeric
    df[COL_LATITUDE] = pd.to_numeric(df[COL_LATITUDE], errors='coerce')
    df[COL_LONGITUDE] = pd.to_numeric(df[COL_LONGITUDE], errors='coerce')

    # Drop rows where coordinates are NaN (cannot be plotted)
    df = df.dropna(subset=[COL_LATITUDE, COL_LONGITUDE])

    return df

try:
    df = load_and_clean_data(DATA_FILE)
except FileNotFoundError:
    st.error(f"Error: The data file '{DATA_FILE}' was not found. Please ensure it is uploaded.")
    st.stop()

# Page title and description
st.title("🏭 Global Steel Production Portfolio")
st.markdown("""
An interactive dashboard displaying global steel plant assets, focusing on capacity, location, and ownership.
Data columns used are the **original names** from the dataset.
""")
st.markdown("---")

# Filters
st.sidebar.header("⚙️ Data Filters")

# Company filter
all_companies = sorted(df[COL_OWNER].unique())
selected_companies = st.sidebar.multiselect(
    f"Select Company ({COL_OWNER})",
    options=all_companies,
    default=all_companies[:10] # Default to top 10 for better initial view
)

# Region/Country filter 
all_countries = sorted(df[COL_COUNTRY].unique())
selected_countries = st.sidebar.multiselect(
    f"Select Country ({COL_COUNTRY})",
    options=all_countries,
    default=all_countries
)

# Capacity Range Slider
capacity_values = df[COL_CAPACITY_MTPA].dropna()
if not capacity_values.empty:
    min_capacity = capacity_values.min().round(2)
    max_capacity = capacity_values.max().round(2)
    capacity_range = st.sidebar.slider(
        f"Crude Steel Capacity Range (Mtpa)",
        min_value=float(min_capacity),
        max_value=float(max_capacity),
        value=(float(min_capacity), float(max_capacity)),
        step=0.1
    )
else:
    st.sidebar.warning("No valid capacity data available.")
    capacity_range = (0, 0)

#apply filters
df_filtered = df.copy()

if selected_companies:
    df_filtered = df_filtered[df_filtered[COL_OWNER].isin(selected_companies)]

if selected_countries:
    df_filtered = df_filtered[df_filtered[COL_COUNTRY].isin(selected_countries)]

df_filtered = df_filtered[
    (df_filtered[COL_CAPACITY_MTPA].isnull()) |
    ((df_filtered[COL_CAPACITY_MTPA] >= capacity_range[0]) &
     (df_filtered[COL_CAPACITY_MTPA] <= capacity_range[1]))
]


# Message if filtered dataframe is empty
if df_filtered.empty:
    st.error("No steel plants match the selected filters. Please adjust your selections.")
    st.stop()

# Main content

## KPI Metrics
st.header("📊 Key Performance Indicators (KPIs)")

# Calculate KPIs
total_plants = len(df_filtered)
total_capacity = df_filtered[COL_CAPACITY_MTPA].sum().round(2)
avg_capacity = df_filtered[COL_CAPACITY_MTPA].mean().round(2) if total_plants > 0 else 0
unique_countries = df_filtered[COL_COUNTRY].nunique()

# Create columns for metric display
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Plants (Filtered)", value=f"{total_plants:,}")
with col2:
    st.metric(label="Total Capacity (Mtpa)", value=f"{total_capacity:,.2f}")
with col3:
    st.metric(label="Avg. Plant Capacity (Mtpa)", value=f"{avg_capacity:,.2f}")
with col4:
    st.metric(label=f"Countries ({COL_COUNTRY})", value=f"{unique_countries}")

st.markdown("---")

## Interactive Map
st.header("📍 Plant Locations Map")
st.markdown("The map visualizes the geographic distribution of the filtered plants. Larger circles indicate higher steel capacity (Mtpa). Colors indicate the region of each factory.")

map_data = df_filtered.rename(columns={COL_LATITUDE: 'lat', COL_LONGITUDE: 'lon'}).copy()
map_data = map_data.dropna(subset=['lat', 'lon', COL_CAPACITY_MTPA])

if not map_data.empty:

    #Scale circle size
    map_data['radius'] = map_data[COL_CAPACITY_MTPA].mul(20000).clip(lower=5000, upper=80000)

    # Color per region
    # Define simple region-color mapping (R,G,B,A)
    region_colors = {
        "Asia Pacific": [250, 0, 0, 160],         
        "Europe": [0, 128, 255, 160],     
        "Africa": [0, 200, 0, 160],       
        "North America": [255, 165, 0, 160], 
        "Middle East": [255, 220, 0, 160], 
        "Central & South America ": [160, 32, 240, 160],  
        "Eurasia": [255, 105, 180, 160],
    }

    # Apply mapping
    map_data["color"] = map_data.get("Region", "Unknown").map(region_colors).apply(
        lambda x: x if isinstance(x, list) else [128, 128, 128, 160] #in case some regions are missing
    )


    # Build map 
    POSITRON = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_radius='radius',
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": (
            f"<b>Plant:</b> {{{COL_PLANT_NAME}}}<br>"
            f"<b>Owner:</b> {{{COL_OWNER}}}<br>"
            f"<b>Region:</b> {{Region}}<br>"
            f"<b>Country:</b> {{{COL_COUNTRY}}}<br>"
            f"<b>Capacity (Mtpa):</b> {{{COL_CAPACITY_MTPA}}}"
        ),
        "style": {"backgroundColor": "white", "color": "black"}
    }

    view_state = pdk.ViewState(latitude=float(map_data['lat'].mean()) if map_data['lat'].notna().any() else 0.0, 
                               longitude=float(map_data['lon'].mean()) if map_data['lon'].notna().any() else 0.0, 
                               zoom=2, pitch=0)

    st.pydeck_chart(pdk.Deck(
        map_style=POSITRON,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))

else:
    st.warning("No plants with valid capacity and coordinates to display on the map.")

st.markdown("---")



## Data Table
st.header("📋 Detailed Data Table")

# Select and display all relevant original columns plus the derived capacity
table_cols = [
    COL_PLANT_NAME,
    COL_OWNER,
    COL_COUNTRY,
    'Region',
    'Status',
    COL_CAPACITY_TTPA, 
    COL_CAPACITY_MTPA, 
    'Start date_x',
    'Main production equipment',
    COL_COORDINATES 
]

table_df = df_filtered[table_cols]

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Footer 
st.sidebar.markdown("---")
st.sidebar.caption("💡 **Notes:**")
st.sidebar.markdown(
    """
    * *Data Source: Global Steel Plants Dataset (`steel_plants.csv`).*
    * *Filtering uses the original column names (e.g., 'Owner' and 'Country/Area_x').*
    * *Capacity metrics are calculated using a derived column **Capacity_Mtpa** (Nominal crude steel capacity in Mtpa) for consistency, but the original **Nominal crude steel capacity (ttpa)** column is shown in the table.*
    """
)