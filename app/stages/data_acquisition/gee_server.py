# Third party
import ee

# Google Earth Engine Collections
# All of the data is open-source, Google provides the server side computation
gee_map_collections = {
    "rootzone_soil_moisture": "NASA/SMAP/SPL4SMGP/007",
    "precipitation": "UCSB-CHG/CHIRPS/DAILY",
    "elevation": "USGS/SRTMGL1_003",
    "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",
    "world_type_terrain_cover": "ESA/WorldCover/v100/2020",
}

world_cover_esa_codes = {
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


def fetch_mean_soil_moisture_data(date_range, geometry):
    """
    Fetches and computes the mean soil moisture over a given date range and geographical area.

    Parameters:
        date_range (tuple): A tuple of (start_date, end_date) in 'YYYY-MM-DD' format.
        geometry (ee.Geometry): The geographic area for the soil moisture calculation.

    Returns:
        ee.Image: An image representing the mean soil moisture over the specified period and area.
    """

    soil_moisture = ee.ImageCollection(
        gee_map_collections["rootzone_soil_moisture"],
    )
    mean_soil_moisture = (
        soil_moisture.filterDate(*date_range)
        .filterBounds(geometry)
        .select("sm_rootzone")
        .mean()
        .clip(geometry)
    )

    return mean_soil_moisture.rename("mean_soil_moisture_root_zone")


def fetch_total_precipitation_data(date_range, geometry):
    """
    Fetches and computes the total precipitation over a given date range and geographical area.

    Parameters:
        image_collection_name (str): Name of the image collection in the Google Earth Engine collections.
        date_range (tuple): A tuple of (start_date, end_date) in 'YYYY-MM-DD' format.
        geometry (ee.Geometry): The geographic area for the precipitation calculation.

    Returns:
        ee.Image: An image representing the total precipitation over the specified period and area.
    """

    precipitation = ee.ImageCollection(gee_map_collections["precipitation"])
    total_precipitation = (
        precipitation.filterDate(*date_range)
        .filterBounds(geometry)
        .select("precipitation")
        .sum()
        .clip(geometry)
    )

    return total_precipitation.rename("total_precipitation")


def fetch_elevation_data(geometry):
    """
    Fetches and computes the elevation data over a given date range and geographical area.

    Parameters:
        geometry (ee.Geometry): The geographic area for the elevation calculation.

    Returns:
        ee.Image: An image representing the elevation over the specified area.
    """

    elevation = ee.Image(gee_map_collections["elevation"]).clip(geometry)

    return elevation.rename("elevation")


def fetch_slope_data(geometry):
    """
    Fetches and computes the slope data over a given date range and geographical area.

    Parameters:
        geometry (ee.Geometry): The geographic area for the slope calculation.

    Returns:
        ee.Image: An image representing the slope over the specified area.
    """
    elevation = ee.Image(gee_map_collections["elevation"])

    # Check if geometry is a point and handle accordingly
    # Expand the region slightly around the point for reliable slope calculation
    if geometry.type().getInfo() == "Point":
        buffer_distance = 100
        geometry = geometry.buffer(buffer_distance)

    slope = ee.Terrain.slope(elevation.clip(geometry))
    return slope.rename("slope")


def fetch_soil_organic_carbon_data(geometry):
    """
    Fetches and processes the soil organic carbon data for a given geometry, which can be a point or a region.

    Parameters:
        geometry (ee.Geometry): The geometry (Point for specific locations or Polygon for regions).

    Returns:
        ee.Image or float: Soil organic carbon data clipped to the region or a specific value at a point.
    """

    soil_organic_carbon = (
        ee.Image(gee_map_collections["soil_organic_carbon"])
        .select("mean_0_20")
        .clip(geometry)
    )

    return soil_organic_carbon.rename("soil_organic_carbon")


def fetch_world_cover_data(geometry):
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        geometry (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    world_cover = ee.Image(gee_map_collections["world_type_terrain_cover"]).clip(
        geometry
    )

    return world_cover.rename("world_cover")
