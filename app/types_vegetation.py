import ee
import folium
import streamlit as st
from streamlit_folium import folium_static
from stages.connection import establish_connection

# Initialize the Earth Engine module
try:
    establish_connection()
except ee.EEException as e:
    st.error("Error initializing Earth Engine: {}".format(e))

# Define the region of interest (ROI)
roi_coords = [
    [
        [-17.5, 15.0],
        [-17.5, 20.0],
        [39.0, 20.0],
        [43.0, 10.5],
        [35.0, 8.0],
        [25.0, 10.0],
        [15.0, 8.0],
        [-5.0, 12.0],
        [-10.0, 13.0],
    ]
]
roi = ee.Geometry.Polygon(roi_coords)

# Define the date range
start_date = "2020-01-01"
end_date = "2020-01-10"


# Retrieve Surface Soil Moisture Data
def get_surface_soil_moisture(roi, start_date, end_date):
    dataset = ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
    filtered_dataset = dataset.filterDate(start_date, end_date).filterBounds(roi)
    soil_moisture_surface = filtered_dataset.select("sm_surface").mean().clip(roi)
    return soil_moisture_surface


# Retrieve Root Zone Soil Moisture Data
def get_rootzone_soil_moisture(roi, start_date, end_date):
    dataset = ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
    filtered_dataset = dataset.filterDate(start_date, end_date).filterBounds(roi)
    soil_moisture_rootzone = filtered_dataset.select("sm_rootzone").mean().clip(roi)
    return soil_moisture_rootzone


# Get soil moisture data
surface_soil_moisture = get_surface_soil_moisture(roi, start_date, end_date)
rootzone_soil_moisture = get_rootzone_soil_moisture(roi, start_date, end_date)

# Visualization parameters for moisture data
moisture_vis_params = {
    "min": 0.0,
    "max": 0.5,
    "palette": ["red", "yellow", "green", "blue"],
}

# Create a folium map
m = folium.Map(location=[17.5, 0.0], zoom_start=5)

# Add surface soil moisture layer to the map
try:
    surface_soil_moisture_url = surface_soil_moisture.getMapId(moisture_vis_params)[
        "tile_fetcher"
    ].url_format
    folium.TileLayer(
        tiles=surface_soil_moisture_url,
        attr="Google Earth Engine",
        overlay=True,
        name="Surface Soil Moisture",
    ).add_to(m)
    print("Surface Soil Moisture layer added successfully.")
except Exception as e:
    st.error("Failed to add Surface Soil Moisture layer: {}".format(e))

# Add rootzone soil moisture layer to the map
try:
    rootzone_soil_moisture_url = rootzone_soil_moisture.getMapId(moisture_vis_params)[
        "tile_fetcher"
    ].url_format
    folium.TileLayer(
        tiles=rootzone_soil_moisture_url,
        attr="Google Earth Engine",
        overlay=True,
        name="Rootzone Soil Moisture",
    ).add_to(m)
    print("Rootzone Soil Moisture layer added successfully.")
except Exception as e:
    st.error("Failed to add Rootzone Soil Moisture layer: {}".format(e))

# Add layer control to the map
folium.LayerControl().add_to(m)

# Use streamlit_folium to display the map in Streamlit
st.title("Soil Moisture Visualization")
folium_static(m)
