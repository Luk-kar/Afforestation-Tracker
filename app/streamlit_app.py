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
    display_map,
    display_map_point_info,
    display_map_legend,
    report_error,
)
from stages.data_acquisition.point import get_map_point_data, get_client_location
from stages.data_acquisition.region import get_region_data, calculate_center
from config import MAP_DATA, ROI


def streamlit_app():
    """Streamlit app logic."""

    st.markdown(
        "<h1 style='text-align: center;'>Afforestation Tracker 🗺️🌳</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center;'>Click on the map to view data for a specific point 👆</p>",
        unsafe_allow_html=True,
    )

    # Initialize Earth Engine and display data on the map
    if not initialize_earth_engine():
        return

    if "latitude" not in st.session_state or "longitude" not in st.session_state:
        # init the lat and lon session state
        sahel_centroid = calculate_center(ROI["roi_coords"])
        st.session_state.latitude, st.session_state.longitude = sahel_centroid

    regions_data, map_result = fetch_and_display_region_data()
    if not regions_data:
        return

    handle_map_clicks(map_result)

    display_coordinate_input_panel()

    display_legend(regions_data)


def display_coordinate_input_panel():
    """Display the coordinate input panel."""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.number_input(
            "Latitude",
            value=st.session_state.latitude,
            key="latitude",
            step=0.5,
            format="%.4f",
        )

    with col2:
        st.number_input(
            "Longitude",
            value=st.session_state.longitude,
            key="longitude",
            step=0.5,
            format="%.4f",
        )

    with col3:
        st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
        st.button(
            "Use My Current Location", on_click=update_coords_with_client_localization
        )


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


def handle_map_clicks(map_result: dict):
    """Handle map clicks and display point data."""

    try:

        if map_result and "last_clicked" in map_result and map_result["last_clicked"]:

            last_click_lat, last_click_lng = (
                map_result["last_clicked"]["lat"],
                map_result["last_clicked"]["lng"],
            )

            if last_click_lat != st.session_state.latitude:
                st.session_state.latitude = last_click_lat
            if last_click_lng != st.session_state.longitude:
                st.session_state.longitude = last_click_lng

        point_data = get_map_point_data(ROI)
        display_map_point_info(point_data)
    except RuntimeError as e:
        report_error("Failed to retrieve or display point data", e)


def display_legend(regions_data: dict):
    """Display the map legend."""
    try:
        display_map_legend(regions_data["maps"])
    except RuntimeError as e:
        report_error("Failed to display map legend", e)


def update_coords_with_client_localization():
    st.session_state.latitude, st.session_state.longitude = get_client_location()


if __name__ == "__main__":
    streamlit_app()
