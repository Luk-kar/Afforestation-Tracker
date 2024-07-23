import streamlit as st
import folium
import ee
from streamlit_folium import st_folium
from folium.plugins import MousePosition

# Initialize the Earth Engine module.
from stages.connection import establish_connection

establish_connection()


# Define a function to get elevation data from Google Earth Engine
def get_elevation(lat, lon):
    point = ee.Geometry.Point(lon, lat)
    elevation = (
        ee.Image("USGS/SRTMGL1_003")
        .sample(point, 30)
        .first()
        .get("elevation")
        .getInfo()
    )
    return elevation


# Function to create a folium map
def create_map():
    start_coords = [34.05, -118.25]  # Default coordinates
    folium_map = folium.Map(location=start_coords, zoom_start=4, tiles="OpenStreetMap")

    # Add a mouse click event to folium map to display elevation
    folium_map.add_child(folium.LatLngPopup())  # Shows latitude and longitude on hover

    # Add a position mouse position tool to the map
    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=False,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(folium_map)

    return folium_map


# Streamlit layout
st.title("Interactive Elevation Map with Google Earth Engine and Folium")

# Map display
folium_map = create_map()
# Use Streamlit Folium component to render Folium map in Streamlit
map_result = st_folium(folium_map, width=725, height=500)

# Show elevation on click
if map_result["last_clicked"]:
    lat, lon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]
    elevation = get_elevation(lat, lon)
    st.success(f"Elevation at Latitude: {lat}, Longitude: {lon} is {elevation} meters.")
