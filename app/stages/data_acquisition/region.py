"""
This module contains functions for fetching environmental data layers 
for a specified region of interest.
"""

# Third party
import ee

# Local
from stages.data_acquisition.gee_server import (
    fetch_total_precipitation_data,
    fetch_mean_soil_moisture_data,
    fetch_elevation_data,
    fetch_soil_organic_carbon_data,
    fetch_slope_data,
    fetch_world_cover_data,
)
from stages.data_categorization import evaluate_afforestation_candidates
from stages.data_acquisition.gee_server import (
    WORLD_COVER_ESA_CODES,
)
from validation import (
    validate_are_keys_the_same,
    validate_many_dates,
    is_valid_roi_coords,
    handle_ee_operations,
)
from _types import Roi_Coords


@handle_ee_operations
def get_rootzone_soil_moisture_region(
    roi_coords: Roi_Coords, start_date: str, end_date: str
) -> ee.Image:
    """
    Retrieves the mean root zone soil moisture for a specified date range.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The mean root zone soil moisture image for the specified period.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    if validate_many_dates(start_date, end_date):
        raise ValueError("Invalid date format. Dates should be in 'YYYY-MM-DD' format.")

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_mean_soil_moisture_data((start_date, end_date), roi)


@handle_ee_operations
def get_precipitation_region(
    roi_coords: Roi_Coords, start_date: str, end_date: str
) -> ee.Image:
    """
    Retrieves the total precipitation for a specified date range.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The total precipitation image for the specified period.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    if validate_many_dates(start_date, end_date):
        raise ValueError("Invalid date format. Dates should be in 'YYYY-MM-DD' format.")

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_total_precipitation_data((start_date, end_date), roi)


@handle_ee_operations
def get_elevation_region(roi_coords: Roi_Coords) -> ee.Image:
    """
    Retrieves the elevation data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The elevation image for the specified region.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_elevation_data(roi)


@handle_ee_operations
def get_slope_region(roi_coords: Roi_Coords) -> ee.Image:
    """
    Retrieves the slope data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The slope image for the specified region.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_slope_data(roi)


@handle_ee_operations
def get_soil_organic_carbon_region(roi_coords: Roi_Coords) -> ee.Image:
    """
    Retrieves the soil organic carbon data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The soil organic carbon image for the specified region.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_soil_organic_carbon_data(roi)


@handle_ee_operations
def get_world_cover_region(roi_coords: Roi_Coords) -> ee.Image:
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_world_cover_data(roi)


@handle_ee_operations
def get_afforestation_candidates_region(
    roi_coords: Roi_Coords, periods: dict[str, dict[str, str]]
) -> ee.Image:
    """
    Retrieves candidate regions for afforestation based on environmental criteria such as
    soil moisture, precipitation, slope, and world cover.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        periods (dict): Dictionary containing the periods for data fetching.

    Returns:
        ee.Image: Image showing areas suitable for afforestation.
    """
    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    slope, precipitation_annual, soil_moisture_rainy_season, world_cover = (
        get_afforestation_candidates_data(roi_coords, periods)
    )

    # Combine all conditions
    candidate_regions = evaluate_afforestation_candidates(
        slope, precipitation_annual, soil_moisture_rainy_season, world_cover
    )

    return candidate_regions


@handle_ee_operations
def get_afforestation_candidates_data(
    roi_coords: Roi_Coords, periods: dict[str, dict[str, str]]
) -> tuple[ee.Image, ee.Image, ee.Image, ee.Image]:
    """
    Fetches the environmental data layers for the specified region and date range.

    Parameters:

        roi_coords (list): List of coordinates defining the region of interest.
        periods (dict): Dictionary containing the periods for data fetching.

    Returns:

        tuple: A tuple containing the slope, precipitation, soil moisture,
        and world cover data layers.
    """

    try:
        is_valid_roi_coords(roi_coords)
    except ValueError as e:
        raise ValueError(f"Invalid ROI coordinates: {str(e)}") from e

    if validate_many_dates(
        periods["soil_moisture"]["start_date"], periods["soil_moisture"]["end_date"]
    ) or validate_many_dates(
        periods["precipitation"]["start_date"], periods["precipitation"]["end_date"]
    ):
        raise ValueError("Invalid date format. Dates should be in 'YYYY-MM-DD' format.")

    rainy_season = periods["soil_moisture"]
    year = periods["precipitation"]

    slope = get_slope_region(roi_coords)
    precipitation_annual = get_precipitation_region(
        roi_coords, year["start_date"], year["end_date"]
    )
    soil_moisture_rainy_season = get_rootzone_soil_moisture_region(
        roi_coords, rainy_season["start_date"], rainy_season["end_date"]
    )
    world_cover = get_world_cover_region(roi_coords)

    return slope, precipitation_annual, soil_moisture_rainy_season, world_cover


@handle_ee_operations
def get_region_data(roi: dict, map_data: dict) -> dict:
    """
    Enrich the map data dictionary with additional environmental data layers
    for the specified region of interest.

    Parameters:
        roi (dict): Dictionary containing the region of interest coordinates
                    and periods for data fetching.

        map_data (dict): Dictionary containing the current map data layers to be enriched.

    Returns:
        dict: Dictionary containing the center coordinates and enriched map data
    """
    # Fetch and update each environmental layer in the map_data dictionary

    data = {}

    center = calculate_center(roi["roi_coords"])

    # Elevation
    map_data["elevation"]["data"] = get_elevation_region(roi["roi_coords"])

    # Slope
    map_data["slope"]["data"] = get_slope_region(roi["roi_coords"])

    # World Cover
    map_data["world_cover"]["data"] = get_world_cover_region(roi["roi_coords"])

    # Soil Organic Carbon
    map_data["soc_0_20cm"]["data"] = get_soil_organic_carbon_region(roi["roi_coords"])

    # Soil Moisture
    map_data["soil_moisture"]["data"] = get_rootzone_soil_moisture_region(
        roi["roi_coords"],
        roi["periods"]["soil_moisture"]["start_date"],
        roi["periods"]["soil_moisture"]["end_date"],
    )

    # Precipitation
    map_data["precipitation"]["data"] = get_precipitation_region(
        roi["roi_coords"],
        roi["periods"]["precipitation"]["start_date"],
        roi["periods"]["precipitation"]["end_date"],
    )

    # Afforestation Candidates
    map_data["afforestation_candidates"]["data"] = get_afforestation_candidates_region(
        roi["roi_coords"], roi["periods"]
    )

    # Validate that all layers are ee.Image objects
    for key, layer in map_data.items():
        if "data" in layer:
            if not isinstance(layer["data"], ee.Image):
                raise ValueError(
                    f"Error fetching {key} data: {layer['data']} is not an ee.Image."
                )

    # Validate that all layers have matching keys in their legend dicts
    for key, layer in map_data.items():
        if (
            "legend" in layer
            and "legend_dict" in layer["legend"]
            and layer == "world_cover"
        ):
            try:
                validate_are_keys_the_same(
                    WORLD_COVER_ESA_CODES, layer["legend"]["legend_dict"]
                )
            except ValueError as e:
                raise ValueError(f"Validation error in {key} layer: {str(e)}") from e

    data["center"] = center
    data["maps"] = map_data

    return data


def calculate_center(roi_coords: Roi_Coords) -> tuple[float, float]:
    """
    Calculate the centroid of the region of interest coordinates.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        tuple: A tuple containing the latitude and longitude of the centroid.
    """

    # Calculate the centroid of the roi_coords to use as the center for the map
    lats = [coord[1] for coord in roi_coords]  # Extract all latitudes
    lngs = [coord[0] for coord in roi_coords]  # Extract all longitudes

    # Calculate the average of latitudes and longitudes
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    center = (center_lat, center_lng)

    return center
