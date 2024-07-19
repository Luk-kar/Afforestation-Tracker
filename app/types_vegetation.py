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


def get_elevation_data(roi):
    return ee.Image("USGS/SRTMGL1_003").clip(roi).rename("elevation")


def get_precipitation(roi, start_date, end_date):
    # dataset = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
    # filtered_dataset = dataset.filterDate(start_date, end_date).filterBounds(roi)
    # precipitation = filtered_dataset.sum().clip(roi)
    # return precipitation
    return (
        ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .map(lambda image: image.clip(roi))  # Clip each image to the ROI
        .sum()
        .rename("Precipitation")
    )


# Get soil moisture data
surface_soil_moisture = get_surface_soil_moisture(roi, start_date, end_date)
rootzone_soil_moisture = get_rootzone_soil_moisture(roi, start_date, end_date)
elevation = get_elevation_data(roi)

# Visualization parameters for moisture data
moisture_vis_params = {
    "min": 0.0,
    "max": 0.5,
    "palette": ["red", "yellow", "green", "blue"],
}

elevation_vis = {
    "min": 0,
    "max": 3000,
    "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
}

precipitation_vis_params = {
    "min": 0,
    "max": 3000,
    "palette": [
        "FFFFFF",
        "C0C0C0",
        "808080",
        "404040",
        "000000",
        "0000FF",
        "00FFFF",
        "00FF00",
        "FFFF00",
        "FF0000",
    ],
}


# Generalized function to add layer to folium map
def add_layer_to_map(map_obj, image, vis_params, layer_name):
    try:
        layer_url = image.getMapId(vis_params)["tile_fetcher"].url_format
        folium.TileLayer(
            tiles=layer_url,
            attr="Google Earth Engine",
            overlay=True,
            name=layer_name,
        ).add_to(map_obj)
        print(f"{layer_name} layer added successfully.")
    except Exception as e:
        st.error(f"Failed to add {layer_name} layer: {str(e)}")


# Get data for each layer
surface_soil_moisture = get_surface_soil_moisture(roi, start_date, end_date)
rootzone_soil_moisture = get_rootzone_soil_moisture(roi, start_date, end_date)
elevation = get_elevation_data(roi)
precipitation = get_precipitation(roi, start_date, end_date)

# Visualization parameters for each layer
moisture_vis_params = {
    "min": 0.0,
    "max": 0.5,
    "palette": ["red", "yellow", "green", "blue"],
}

elevation_vis_params = {
    "min": 0,
    "max": 3000,
    "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
}

# Create a folium map
m = folium.Map(location=[17.5, 0.0], zoom_start=5)

# Add layers to the map using the generalized function
add_layer_to_map(m, surface_soil_moisture, moisture_vis_params, "Surface Soil Moisture")
add_layer_to_map(
    m, rootzone_soil_moisture, moisture_vis_params, "Rootzone Soil Moisture"
)
add_layer_to_map(m, elevation, elevation_vis_params, "Elevation")
add_layer_to_map(m, precipitation, precipitation_vis_params, "Precipitation")

# Add layer control to the map
folium.LayerControl().add_to(m)

# Use streamlit_folium to display the map in Streamlit
st.title("Soil Moisture Visualization")
folium_static(m)
