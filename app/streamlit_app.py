"""
This script contains the Streamlit app logic and is the entry point for the Streamlit app. 
It initializes the Earth Engine module, retrieves the region data, and displays the map.
"""

# Third party
import streamlit as st
from streamlit_folium import st_folium

# Local
from stages.server_connection import establish_connection
from stages.visualization import (
    display_text,
    display_title,
    display_map,
    display_coordinate_input_panel,
    display_map_point_info,
    display_map_legend,
    report_error,
)
from stages.data_acquisition.point import get_map_point_data
from stages.data_acquisition.region import get_region_data, calculate_center
from config import MAP_DATA, ROI


def streamlit_app():
    """Main Streamlit app function."""

    display_title("Afforestation Tracker 🗺️🌴")
    display_text("Click on the map to view data for a specific point 👆")

    if not initialize_earth_engine():
        return  # Exit app

    elif "latitude" not in st.session_state or "longitude" not in st.session_state:
        setup_latitude_longitude_session()

    regions_data, map_result = fetch_and_display_region_data()
    if not regions_data:
        return  # Exit app

    is_map_clicked = (
        map_result and "last_clicked" in map_result and map_result["last_clicked"]
    )
    if is_map_clicked:
        update_latitude_longitude_session(map_result)

    point_data = get_map_point_data(ROI)
    display_map_point_info(point_data)

    # Ensure display_coordinate_input_panel() is called here
    # to prevent StreamlitAPIException by avoiding updates
    # to session state after widget instantiation.
    display_coordinate_input_panel()

    display_legend(regions_data)


def setup_latitude_longitude_session():
    """Setup the latitude and longitude session state in streamlit class"""

    sahel_centroid = calculate_center(ROI["roi_coords"])
    st.session_state["latitude"], st.session_state["longitude"] = sahel_centroid


def initialize_earth_engine() -> bool:
    """Initialize the Earth Engine and handle errors."""
    try:
        establish_connection()
        return True
    except RuntimeError as e:
        report_error("Failed to initialize Earth Engine module", e)
        return False


def fetch_and_display_region_data():
    """Fetch region data and display the map."""
    try:
        regions_data = get_region_data(ROI, MAP_DATA)
        folium_map = display_map(regions_data)
        map_result = st_folium(folium_map, key="map", width=725, height=500)
        return regions_data, map_result
    except RuntimeError as e:
        report_error("Failed to retrieve or display region data", e)
        return None


def update_latitude_longitude_session(map_result: dict):
    """Update the latitude and longitude session state in streamlit class"""

    last_click_lat, last_click_lng = (
        map_result["last_clicked"]["lat"],
        map_result["last_clicked"]["lng"],
    )

    if last_click_lat != st.session_state["latitude"]:
        st.session_state["latitude"] = last_click_lat
    if last_click_lng != st.session_state["longitude"]:
        st.session_state["longitude"] = last_click_lng


def display_legend(regions_data: dict):
    """Display the map legend."""
    try:
        display_map_legend(regions_data["maps"])
    except RuntimeError as e:
        report_error("Failed to display map legend", e)


if __name__ == "__main__":
    streamlit_app()
