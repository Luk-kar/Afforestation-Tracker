"""
This script contains the Streamlit app logic and is the entry point for the Streamlit app. 
It initializes the Earth Engine module, retrieves the region data, and displays the map.
"""

# Third party
from streamlit_folium import st_folium

# Local
from stages.server_connection import establish_connection
from stages.visualization import (
    display_map,
    display_map_point_info,
    display_map_legend,
    report_error,
)
from stages.data_acquisition.point import get_map_point_data
from stages.data_acquisition.region import get_region_data
from config import MAP_DATA, ROI


def streamlit_app():
    """Streamlit app logic."""

    # Initialize Earth Engine and display data on the map
    if not initialize_earth_engine():
        return

    regions_data, map_result = fetch_and_display_region_data()
    if not regions_data:
        return

    if map_result and "last_clicked" in map_result and map_result["last_clicked"]:
        handle_map_clicks(map_result)

    display_legend(regions_data)


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
        lat, lon = (
            map_result["last_clicked"]["lat"],
            map_result["last_clicked"]["lng"],
        )
        point_data = get_map_point_data(ROI, lat, lon)
        display_map_point_info(point_data)
    except RuntimeError as e:
        report_error("Failed to retrieve or display point data", e)


def display_legend(regions_data: dict):
    """Display the map legend."""
    try:
        display_map_legend(regions_data["maps"])
    except RuntimeError as e:
        report_error("Failed to display map legend", e)


if __name__ == "__main__":
    streamlit_app()
