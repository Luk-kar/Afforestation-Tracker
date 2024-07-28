# Third party
import requests
import ee

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


def find_key_by_value(dictionary, value, default):
    for key, val in dictionary.items():
        if val == value:
            return key
    return default


# Google Earth Engine Collections
# All of the data is open-source, Google provides the server side computation
gee_map_collections = {
    "rootzone_soil_moisture": "NASA/SMAP/SPL4SMGP/007",
    "precipitation": "UCSB-CHG/CHIRPS/DAILY",
    "elevation": "USGS/SRTMGL1_003",
    "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",
    "world_type_terrain_cover": "ESA/WorldCover/v100/2020",
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


def fetch_suitable_for_afforestation_data(
    slope, precipitation, soil_moisture, world_cover
):
    """
    Evaluates environmental criteria to determine suitability for afforestation using either Earth Engine objects or scalar values.

    Args:
    slope (float or ee.Image): Slope of the land.
    precipitation (float or ee.Image): Precipitation amount.
    soil_moisture (float or ee.Image): Soil moisture percentage.
    world_cover (str or ee.Image): World cover category.

    Returns:
    bool or ee.Image: Whether the area is suitable for afforestation.
    """

    conditions = {
        "slope": 15,
        "precipitation": 200,
        "moisture": 0.1,
        "vegetation_mask": [
            world_cover_esa_codes["Grassland"],
            world_cover_esa_codes["Bare / Sparse Vegetation"],
        ],
    }

    if (
        isinstance(slope, ee.Image)
        and isinstance(precipitation, ee.Image)
        and isinstance(soil_moisture, ee.Image)
        and isinstance(world_cover, ee.Image)
    ):
        # Earth Engine image logic
        suitable_slope = slope.lt(conditions["slope"])
        suitable_precipitation = precipitation.gte(conditions["precipitation"])
        suitable_soil_moisture = soil_moisture.gte(
            conditions["moisture"]
        )  # Adjusting to a decimal for consistency
        vegetation_mask = world_cover.eq(conditions["vegetation_mask"][0]).Or(
            world_cover.eq(conditions["vegetation_mask"][1])
        )

        return (
            suitable_slope.And(suitable_precipitation)
            .And(suitable_soil_moisture)
            .And(vegetation_mask)
        )

    elif (
        isinstance(slope, (int, float))
        and isinstance(precipitation, (int, float))
        and isinstance(soil_moisture, (int, float))
        and isinstance(world_cover, int)
    ):
        # Scalar logic
        valid_slope = slope <= conditions["slope"]
        hydration_criteria = (soil_moisture >= conditions["moisture"]) or (
            precipitation >= conditions["precipitation"]
        )
        valid_cover = world_cover in [
            world_cover_esa_codes["Grassland"],
            world_cover_esa_codes["Bare / Sparse Vegetation"],
        ]

        return valid_slope and hydration_criteria and valid_cover
    else:
        raise TypeError("Invalid input types for afforestation data evaluation.")


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

    # Combine all conditions
    candidate_regions = fetch_suitable_for_afforestation_data(
        slope, precipitation_annual, soil_moisture_rainy_season, world_cover
    )

    return candidate_regions


def get_rootzone_soil_moisture_point(lat, lon, start_date, end_date):
    """
    Retrieves the mean soil moisture value at a specific point for a specified date range.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        start_date (str): The start date for the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date for the period of interest in 'YYYY-MM-DD' format.

    Returns:
        float: Average soil moisture value at the given point for the specified date range, or 0 if no data is available.
    """
    point = ee.Geometry.Point([lon, lat])
    mean_soil_moisture_image = fetch_mean_soil_moisture_data(
        (start_date, end_date), point
    )

    soil_moisture_value = (
        mean_soil_moisture_image.reduceRegion(ee.Reducer.first(), point, scale=100)
        .get("mean_soil_moisture_root_zone")
        .getInfo()
    )
    return soil_moisture_value if soil_moisture_value is not None else 0


def get_precipitation_point(lat, lon, start_date, end_date):

    point = ee.Geometry.Point([lon, lat])
    total_precipitation_image = fetch_total_precipitation_data(
        (start_date, end_date), point
    )

    precipitation_value = (
        total_precipitation_image.reduceRegion(
            reducer=ee.Reducer.first(), geometry=point, scale=100
        )
        .get("total_precipitation")
        .getInfo()
    )

    return precipitation_value


def get_soil_organic_carbon_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])
    soil_organic_carbon = ee.Image(gee_map_collections["soil_organic_carbon"])

    carbon_value = (
        soil_organic_carbon.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=100,
        )
        .get("mean_0_20")
        .getInfo()
    )

    return carbon_value


def get_elevation_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])
    elevation_image = fetch_elevation_data(point)

    elevation_value = (
        elevation_image.reduceRegion(ee.Reducer.first(), point, scale=10)
        .get("elevation")
        .getInfo()
    )

    return elevation_value


def get_slope_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])

    slope = fetch_slope_data(point)

    slope_value = (
        slope.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=100,
        )
        .get("slope")
        .getInfo()
    )

    return slope_value


def get_world_cover_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    world_cover = fetch_world_cover_data(point)

    world_cover_value = (
        world_cover.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=100,
        )
        .get("world_cover")
        .getInfo()
    )

    return world_cover_value


def get_address_from_coordinates(lat, lon):
    """Fetch address from Nominatim Geocoding API using latitude and longitude."""
    base_url = "https://nominatim.openstreetmap.org/reverse"
    headers = {"User-Agent": "MyApp"}
    params = {"lat": lat, "lon": lon, "format": "json"}
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        json_result = response.json()
        address = json_result.get("display_name")
        if address:
            return address
        else:
            return "No address found."
    else:
        return "Error in Geocoding API call."
