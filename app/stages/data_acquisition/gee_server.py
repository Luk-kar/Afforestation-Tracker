"""
This module contains functions to fetch data from Google Earth Engine (GEE) server.
"""

# Third party
import ee

# App
from _types import Date_Range
from validation import handle_ee_operations
from config import SIZE_SAMPLE_METERS, GEE_MAP_COLLECTIONS

WORLD_COVER_ESA_CODES = {
    "No data / Ocean": -1,
    "Tree Cover": 10,
    "Shrubland": 20,
    "Grassland": 30,
    "Cropland": 40,
    "Built-up": 50,
    "Bare / Sparse Vegetation": 60,
    "Snow and Ice": 70,
    "Permanent Water Bodies": 80,
    "Herbaceous Wetland": 90,
    "Mangroves": 95,
    "Moss and Lichen": 100,
}


@handle_ee_operations
def fetch_satellite_imagery_data(geometry: ee.Geometry) -> ee.Image:
    """
    Fetches the satellite imagery data for a given date range and geographical area.

    Parameters:
        date_range (tuple): A tuple of (start_date, end_date) in 'YYYY-MM-DD' format.
        geometry (ee.Geometry): The geographic area for the satellite imagery.

    Returns:
        ee.Image: An image representing the satellite imagery over the specified period and area.
    """

    satellite_imagery = ee.ImageCollection(GEE_MAP_COLLECTIONS["satellite_imagery"])
    satellite_image = (
        satellite_imagery.filterBounds(geometry)
        .first()
        .clip(geometry)
        .select(["B4", "B3", "B2"])
    )

    return satellite_image


@handle_ee_operations
def fetch_mean_soil_moisture_data(
    date_range: Date_Range, geometry: ee.Geometry
) -> ee.Image:
    """
    Fetches and computes the mean soil moisture over a given date range and geographical area.

    Parameters:
        date_range (tuple): A tuple of (start_date, end_date) in 'YYYY-MM-DD' format.
        geometry (ee.Geometry): The geographic area for the soil moisture calculation.

    Returns:
        ee.Image: An image representing the mean soil moisture over the specified period and area.
    """

    soil_moisture = ee.ImageCollection(
        GEE_MAP_COLLECTIONS["rootzone_soil_moisture"],
    )
    mean_soil_moisture = (
        soil_moisture.filterDate(*date_range)
        .filterBounds(geometry)
        .select("sm_rootzone")
        .mean()
        .clip(geometry)
    )

    return mean_soil_moisture.rename("mean_soil_moisture_root_zone")


@handle_ee_operations
def fetch_total_precipitation_data(
    date_range: Date_Range, geometry: ee.Geometry
) -> ee.Image:
    """
    Fetches and computes the total precipitation over a given date range and geographical area.

    Parameters:
        date_range (tuple): A tuple of (start_date, end_date) in 'YYYY-MM-DD' format.
        geometry (ee.Geometry): The geographic area for the precipitation calculation.

    Returns:
        ee.Image: An image representing the total precipitation over the specified period and area.
    """

    precipitation = ee.ImageCollection(GEE_MAP_COLLECTIONS["precipitation"])
    total_precipitation = (
        precipitation.filterDate(*date_range)
        .filterBounds(geometry)
        .select("precipitation")
        .sum()
        .clip(geometry)
    )

    return total_precipitation.rename("total_precipitation")


@handle_ee_operations
def fetch_elevation_data(geometry: ee.Geometry) -> ee.Image:
    """
    Fetches and computes the elevation data over a given date range and geographical area.

    Parameters:
        geometry (ee.Geometry): The geographic area for the elevation calculation.

    Returns:
        ee.Image: An image representing the elevation over the specified area.
    """

    elevation = ee.Image(GEE_MAP_COLLECTIONS["elevation"]).clip(geometry)

    return elevation.rename("elevation")


@handle_ee_operations
def fetch_slope_data(geometry: ee.Geometry) -> ee.Image:
    """
    Fetches and computes the slope data over a given date range and geographical area.

    Parameters:
        geometry (ee.Geometry): The geographic area for the slope calculation.

    Returns:
        ee.Image: An image representing the slope over the specified area.
    """
    elevation = ee.Image(GEE_MAP_COLLECTIONS["elevation"])

    # Check if geometry is a point and handle accordingly
    # Expand the region slightly around the point for reliable slope calculation
    if geometry.type().getInfo() == "Point":
        buffer_distance = SIZE_SAMPLE_METERS
        geometry = geometry.buffer(buffer_distance)

    slope = ee.Terrain.slope(elevation.clip(geometry))
    return slope.rename("slope")


@handle_ee_operations
def fetch_soil_organic_carbon_data(geometry: ee.Geometry) -> ee.Image:
    """
    Fetches and processes the soil organic carbon data for a given geometry,
    which can be a point or a region.

    Parameters:
        geometry (ee.Geometry): The geometry (Point for specific locations or Polygon for regions).

    Returns:
        ee.Image or float: Soil organic carbon data clipped to the region
        or a specific value at a point.
    """

    soil_organic_carbon = (
        ee.Image(GEE_MAP_COLLECTIONS["soil_organic_carbon"])
        .select("mean_0_20")
        .clip(geometry)
    )

    return soil_organic_carbon.rename("soil_organic_carbon")


@handle_ee_operations
def fetch_world_cover_data(geometry: ee.Geometry) -> ee.Image:
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        geometry (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    world_cover = ee.Image(GEE_MAP_COLLECTIONS["world_type_terrain_cover"]).clip(
        geometry
    )

    return world_cover.rename("world_cover")
