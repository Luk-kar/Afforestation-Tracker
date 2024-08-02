"""
This module contains functions to retrieve data for a specific point on the map.
"""

# Third party
import requests
import ee
import streamlit as st

# Local
import geocoder
from config import SIZE_SAMPLE_METERS
from stages.data_acquisition.gee_server import (
    fetch_total_precipitation_data,
    fetch_mean_soil_moisture_data,
    fetch_elevation_data,
    fetch_soil_organic_carbon_data,
    fetch_slope_data,
    fetch_world_cover_data,
)
from stages.data_categorization import evaluate_afforestation_candidates
from validation import handle_ee_operations, validate_coordinates


@handle_ee_operations
def get_rootzone_soil_moisture_point(
    lat: float, lon: float, start_date: str, end_date: str
) -> float:
    """
    Retrieves the mean soil moisture value at a specific point for a specified date range.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        start_date (str): The start date for the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date for the period of interest in 'YYYY-MM-DD' format.

    Returns:
        float: Average soil moisture value at the given point for the specified date range,
        or -1 if no data is available.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])

    mean_soil_moisture_image = fetch_mean_soil_moisture_data(
        (start_date, end_date), point
    )

    soil_moisture_value = (
        mean_soil_moisture_image.reduceRegion(
            ee.Reducer.first(), point, scale=SIZE_SAMPLE_METERS
        )
        .get("mean_soil_moisture_root_zone")
        .getInfo()
    )

    if soil_moisture_value is None:
        soil_moisture_value = -1

    return soil_moisture_value


@handle_ee_operations
def get_precipitation_point(
    lat: float, lon: float, start_date: str, end_date: str
) -> float:
    """
    Retrieves the total precipitation value at a specific point for a specified date range.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        start_date (str): The start date for the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date for the period of interest in 'YYYY-MM-DD'

    Returns:
        float: Total precipitation value at the given point for the specified date range,
        or 0 if no data is available.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])

    total_precipitation_image = fetch_total_precipitation_data(
        (start_date, end_date), point
    )

    precipitation_value = (
        total_precipitation_image.reduceRegion(
            reducer=ee.Reducer.first(), geometry=point, scale=SIZE_SAMPLE_METERS
        )
        .get("total_precipitation")
        .getInfo()
    )

    if precipitation_value is None:
        precipitation_value = -1

    return precipitation_value


@handle_ee_operations
def get_soil_organic_carbon_point(lat: float, lon: float) -> float:
    """
    Retrieves the soil organic carbon value at a specific point.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        float: Soil organic carbon value at the given point, or -1 if no data is available.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])
    soil_organic_carbon = fetch_soil_organic_carbon_data(point)

    carbon_value = (
        soil_organic_carbon.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=SIZE_SAMPLE_METERS,
        )
        .get("soil_organic_carbon")
        .getInfo()
    )

    if carbon_value is None:
        carbon_value = -1

    return carbon_value


@handle_ee_operations
def get_elevation_point(lat: float, lon: float) -> float:
    """
    Retrieves the elevation value at a specific point.

    Parameters:

        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        float: Elevation value at the given point, or -1 if no data is available.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])
    elevation_image = fetch_elevation_data(point)

    elevation_value = (
        elevation_image.reduceRegion(
            ee.Reducer.first(), point, scale=10
        )  # Exception for scale for precision
        .get("elevation")
        .getInfo()
    )

    if elevation_value is None:
        elevation_value = -1

    return elevation_value


@handle_ee_operations
def get_slope_point(lat: float, lon: float) -> float:
    """
    Retrieves the slope value at a specific point.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        float: Slope value at the given point, or 0 if no data is available.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])

    slope = fetch_slope_data(point)

    slope_value = (
        slope.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=SIZE_SAMPLE_METERS,
        )
        .get("slope")
        .getInfo()
    )

    # Assign a default value of 0
    # if no elevation variation is detected in the area,
    # which results in a 'None' slope value.
    if slope_value is None:
        slope_value = 0

    return slope_value


@handle_ee_operations
def get_world_cover_point(lat: float, lon: float) -> str:
    """
    Retrieves the world cover value at a specific point.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        str: World cover value at the given point, or `-1` if no data.
    """
    validate_coordinates(lat, lon)
    point = ee.Geometry.Point([lon, lat])
    world_cover = fetch_world_cover_data(point)

    world_cover_value = (
        world_cover.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=SIZE_SAMPLE_METERS,
        )
        .get("world_cover")
        .getInfo()
    )

    if world_cover_value is None:
        world_cover_value = -1

    return world_cover_value


def get_address_from_point(lat: float, lon: float) -> str:
    """
    Fetch address from Nominatim Geocoding API using latitude and longitude.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        str: Address of the given point, or 'No address found.' if no address is available.
    """
    validate_coordinates(lat, lon)

    base_url = "https://nominatim.openstreetmap.org/reverse"
    headers = {"User-Agent": "MyApp"}
    params = {"lat": lat, "lon": lon, "format": "json"}

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        IS_SUCCESS = response.status_code == 200

        if IS_SUCCESS:
            json_result = response.json()
            address = json_result.get("display_name")
            return address or "No address found."
        else:
            return f"Error in Geocoding API call. Status Code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Network error during geocoding: {str(e)}"


@handle_ee_operations
def get_map_point_data(roi: dict) -> dict:
    """
    Retrieves the data for a specific point on the map.

    Parameters:
        roi (dict): The region of interest containing the periods of interest.

    Returns:
        dict: The data for the specified point.
    """
    lat, lon = st.session_state["latitude"], st.session_state["longitude"]

    data = {
        "elevation": get_elevation_point(lat, lon),
        "slope": get_slope_point(lat, lon),
        "soil_moisture": get_rootzone_soil_moisture_point(
            lat,
            lon,
            roi["periods"]["soil_moisture"]["start_date"],
            roi["periods"]["soil_moisture"]["end_date"],
        ),
        "precipitation": get_precipitation_point(
            lat,
            lon,
            roi["periods"]["precipitation"]["start_date"],
            roi["periods"]["precipitation"]["end_date"],
        ),
        "soil_organic_carbon": get_soil_organic_carbon_point(lat, lon),
        "world_cover": get_world_cover_point(lat, lon),
        "address": get_address_from_point(lat, lon),
        "lat": lat,
        "lon": lon,
    }

    data["afforestation_validation"] = evaluate_afforestation_candidates(
        data["slope"],
        data["precipitation"],
        data["soil_moisture"],
        data["world_cover"],
    )
    return data


def get_client_location():
    """
    Get the latitude and longitude of the users's location.

    Returns:
        tuple: A tuple containing the latitude and longitude of the users's location.
    """
    current_location = geocoder.ip("me")
    latitude = current_location.latlng[0]
    longitude = current_location.latlng[1]
    return latitude, longitude
