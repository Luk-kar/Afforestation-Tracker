# Third party
import requests
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
        buffer_distance = 30
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


def fetch_and_evaluate_conditions_data(geometry, start_date, end_date):
    """
    Fetches and evaluates environmental conditions for afforestation suitability.

    Parameters:
        geometry (ee.Geometry): Geometry object representing a point or region.
        start_date (str): The start date for precipitation data.
        end_date (str): The end date for precipitation data.

    Returns:
        dict: Dictionary containing the evaluations of slope, precipitation, soil moisture, and land cover.
    """
    # TODO make much harsher conditions

    slope = fetch_slope_data(geometry)
    precipitation = fetch_total_precipitation_data((start_date, end_date), geometry)
    soil_moisture = fetch_mean_soil_moisture_data(
        ("2020-06-01", "2020-10-01"), geometry
    )
    world_cover = fetch_world_cover_data(geometry)

    results = {
        "is_suitable_slope": slope.lt(15),
        "suitable_precipitation": precipitation.gte(200),
        "suitable_moisture": soil_moisture.select("mean_soil_moisture_root_zone").gte(
            0.2
        ),
        "grassland": world_cover.eq(30),
        "barrenland": world_cover.eq(60),
    }
    return results


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


def get_afforestation_candidates_region(roi_coords, start_date, end_date):
    """
    Identifies candidate regions for afforestation based on multiple criteria.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The candidate regions for afforestation.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    conditions = fetch_and_evaluate_conditions_data(roi, start_date, end_date)

    vegetation_mask = conditions["grassland"].Or(conditions["barrenland"])

    hydration_criteria = conditions["suitable_precipitation"].Or(
        conditions["suitable_moisture"]
    )

    is_not_steep = conditions["is_suitable_slope"]

    candidate_regions = hydration_criteria.And(is_not_steep).And(vegetation_mask)

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
        mean_soil_moisture_image.reduceRegion(ee.Reducer.first(), point, scale=1000)
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
            scale=30,
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
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=30,
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
            scale=10,
        )
        .get("world_cover")
        .getInfo()
    )

    # TODO export logic to the display
    class_names = {
        10: "Tree Cover",
        20: "Shrubland",
        30: "Grassland",
        40: "Cropland",
        50: "Built-up",
        60: "Bare / Sparse Vegetation",
        70: "Snow and Ice",
        80: "Permanent Water Bodies",
        90: "Herbaceous Wetland",
        95: "Mangroves",
        100: "Moss and Lichen",
    }

    return class_names.get(world_cover_value, "Unknown Cover")


def get_afforestation_candidates_point(lat, lon, start_date, end_date):

    point = ee.Geometry.Point([lon, lat])
    conditions = fetch_and_evaluate_conditions_data(point, start_date, end_date)
    scale = 30

    is_suitable_land_cover = (
        conditions["grassland"]
        .Or(conditions["barrenland"])
        .reduceRegion(ee.Reducer.first(), point, scale)
        .getInfo()
    )

    is_hydration_criteria = (
        conditions["suitable_precipitation"]
        .Or(conditions["suitable_moisture"])
        .reduceRegion(ee.Reducer.first(), point, scale)
        .getInfo()
    )

    is_suitable_slope = (
        conditions["is_suitable_slope"]
        .reduceRegion(ee.Reducer.first(), point, scale)
        .getInfo()
    )
    if is_suitable_land_cover and is_hydration_criteria and is_suitable_slope:
        return "Suitable for Afforestation"
    else:
        return "Not Suitable for Afforestation"


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
