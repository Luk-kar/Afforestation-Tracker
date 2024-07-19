# Third-party imports
import ee
from stages.connection import establish_connection

# Import necessary libraries
import streamlit as st
from streamlit_folium import folium_static
import folium
import ee

establish_connection()

roi_coords = {
    "roi_coords": [
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
    ],
    "start_date": "2020-01-01",
    "end_date": "2020-12-31",
}

collections = {
    "precipitation": "UCSB-CHG/CHIRPS/PENTAD",
}


def download_data():
    roi = ee.Geometry.Polygon(roi_coords["roi_coords"])
    start_date = roi_coords["start_date"]
    end_date = roi_coords["end_date"]

    return get_precipitation_data("UCSB-CHG/CHIRPS/PENTAD", roi, start_date, end_date)


def get_precipitation_data(collection, roi, start_date, end_date):
    return (
        ee.ImageCollection(collection)
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .map(lambda image: image.clip(roi))  # Clip each image to the ROI
        .sum()
        .rename("Precipitation")
    )


if establish_connection():
    print("Connection to Google Earth Engine is successful.")

precipitation_vis = {
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

# Create a folium map at a specified location
m = folium.Map(
    location=[17.5, 0.0], zoom_start=5
)  # Centered based on the ROI in data_acquisition.py

image = download_data()
layer_name = "precipitation"

try:
    url = image.getMapId(precipitation_vis)["tile_fetcher"].url_format
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
