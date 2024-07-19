# Import necessary libraries
import streamlit as st
from streamlit_folium import folium_static
import folium
import ee

from stages.connection import establish_connection
from stages.data_acquisition import get_data

# Initialize the Earth Engine module
establish_connection()

# Obtain data from data_acquisition.py
data = (
    get_data()
)  # Assuming this function returns a dictionary of ee.Image objects with keys as layer names


def get_vis_params(layer_name):
    """Return appropriate visualization parameters based on the layer type."""
    vis_params = {
        "default": {"min": 0, "max": 3000, "palette": ["blue", "green", "red"]},
        "precipitation": {"min": 0, "max": 300, "palette": ["white", "blue"]},
        "soil_moisture": {"min": 0, "max": 0.5, "palette": ["white", "green"]},
        "surface_soil_moisture": {
            "min": 0.0,
            "max": 0.5,
            "palette": [
                "ffffe5",
                "f7fcb9",
                "d9f0a3",
                "addd8e",
                "78c679",
                "41ab5d",
                "238443",
                "006837",
                "004529",
            ],
        },
        "sm_rootzone": {
            "min": 0.0,
            "max": 0.5,
            "palette": [
                "fff7fb",
                "ece2f0",
                "d0d1e6",
                "a6bddb",
                "67a9cf",
                "3690c0",
                "02818a",
                "016c59",
                "014636",
            ],
        },
        "sentinel2": {"bands": ["B4", "B3", "B2"], "min": 0, "max": 0.3},
        # Add other specific layers with their visualization parameters
    }
    return vis_params.get(layer_name, vis_params["default"])


# Create a folium map at a specified location
m = folium.Map(
    location=[17.5, 0.0], zoom_start=5
)  # Centered based on the ROI in data_acquisition.py

# Add Earth Engine layers to the folium map
for layer_name, image in data.items():
    vis_params = get_vis_params(layer_name)  # Dynamically get visualization parameters
    try:
        url = image.getMapId(vis_params)["tile_fetcher"].url_format
        folium.TileLayer(
            tiles=url, attr="Google Earth Engine", overlay=True, name=layer_name
        ).add_to(m)
    except Exception as e:
        st.error(f"Failed to add layer {layer_name}: {str(e)}")

# Add layer control to switch between different data layers
folium.LayerControl().add_to(m)

# Use streamlit_folium to display the map in Streamlit
st.title("Visualizing Earth Engine Data on Folium Map")
folium_static(m)
