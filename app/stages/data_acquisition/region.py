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
    world_cover_esa_codes,
)
from utils import validate_are_keys_the_same


def get_rootzone_soil_moisture_region(roi_coords, start_date, end_date):
    """
    Retrieves the mean root zone soil moisture for a specified date range.

    Parameters:
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The mean root zone soil moisture image for the specified period.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_mean_soil_moisture_data((start_date, end_date), roi)


def get_precipitation_region(roi_coords, start_date, end_date):
    """
    Retrieves the total precipitation for a specified date range.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The total precipitation image for the specified period.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_total_precipitation_data((start_date, end_date), roi)


def get_elevation_region(roi_coords):
    """
    Retrieves the elevation data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The elevation image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_elevation_data(roi)


def get_slope_region(roi_coords):
    """
    Retrieves the slope data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The slope image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_slope_data(roi)


def get_soil_organic_carbon_region(roi_coords):
    """
    Retrieves the soil organic carbon data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The soil organic carbon image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_soil_organic_carbon_data(roi)


def get_world_cover_region(roi_coords):
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    return fetch_world_cover_data(roi)


def get_afforestation_candidates_region(roi_coords, periods):
    """
    Retrieves candidate regions for afforestation based on environmental criteria such as
    soil moisture, precipitation, slope, and world cover.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        start_date (str): Start date for analyzing precipitation data.
        end_date (str): End date for analyzing precipitation data.

    Returns:
        ee.Image: Image showing areas suitable for afforestation.
    """
    slope, precipitation_annual, soil_moisture_rainy_season, world_cover = (
        get_afforestation_candidates_data(roi_coords, periods)
    )

    # Combine all conditions
    candidate_regions = evaluate_afforestation_candidates(
        slope, precipitation_annual, soil_moisture_rainy_season, world_cover
    )

    return candidate_regions


def get_afforestation_candidates_data(roi_coords, periods):

    rainy_season = periods["soil_moisture"]
    year = periods["precipitation"]

    # Fetch environmental data for the specified region and date range
    slope = get_slope_region(roi_coords)
    precipitation_annual = get_precipitation_region(
        roi_coords, year["start_date"], year["end_date"]
    )
    soil_moisture_rainy_season = get_rootzone_soil_moisture_region(
        roi_coords, rainy_season["start_date"], rainy_season["end_date"]
    )
    world_cover = get_world_cover_region(roi_coords)
    return slope, precipitation_annual, soil_moisture_rainy_season, world_cover


def get_region_data(roi, map_data):
    """
    Enrich the map data dictionary with additional environmental data layers for the specified region of interest.

    Parameters:
        roi (dict): Dictionary containing the region of interest coordinates and periods for data fetching.
        map_data (dict): Dictionary containing the current map data layers to be enriched.

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

    # Validate that all layers have matching keys in their legend dicts
    for key, layer in map_data.items():
        if "legend" in layer and "legend_dict" in layer["legend"]:
            try:
                validate_are_keys_the_same(
                    world_cover_esa_codes, layer["legend"]["legend_dict"]
                )
            except ValueError as e:
                print(f"Validation error in {key} layer: {str(e)}")

    data["center"] = center
    data["maps"] = map_data

    return data


def calculate_center(roi_coords):

    # Calculate the centroid of the roi_coords to use as the center for the map
    lats = [coord[1] for coord in roi_coords]  # Extract all latitudes
    lngs = [coord[0] for coord in roi_coords]  # Extract all longitudes

    # Calculate the average of latitudes and longitudes
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    center = (center_lat, center_lng)

    return center
