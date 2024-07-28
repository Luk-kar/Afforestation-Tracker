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
