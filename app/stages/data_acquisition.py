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


def fetch_mean_soil_moisture(date_range, geometry):
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


def fetch_total_precipitation(date_range, geometry):
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


def fetch_elevation(geometry):
    """
    Fetches and computes the elevation data over a given date range and geographical area.

    Parameters:
        geometry (ee.Geometry): The geographic area for the elevation calculation.

    Returns:
        ee.Image: An image representing the elevation over the specified area.
    """

    elevation = ee.Image(gee_map_collections["elevation"]).clip(geometry)

    return elevation.rename("Elevation")


def fetch_soil_organic_carbon(geometry):
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

    return soil_organic_carbon.rename("Soil Organic Carbon")


def fetch_world_cover(geometry):
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        geometry (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    world_cover = ee.Image(gee_map_collections["world_type_terrain_cover"])
    world_cover = world_cover.clip(geometry)

    return world_cover


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
    mean_soil_moisture_image = fetch_mean_soil_moisture((start_date, end_date), roi)
    return mean_soil_moisture_image


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
    return fetch_total_precipitation((start_date, end_date), roi)


def get_elevation_region(roi_coords):
    """
    Retrieves the elevation data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The elevation image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    elevation_image = fetch_elevation(roi)
    return elevation_image


def get_slope_region(roi_coords):
    """
    Retrieves the slope data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The slope image for the specified region.
    """
    elevation = get_elevation_region(roi_coords)
    slope = ee.Terrain.slope(elevation)
    return slope


def get_soil_organic_carbon(roi_coords):
    """
    Retrieves the soil organic carbon data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The soil organic carbon image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)
    soc_0_20cm = fetch_soil_organic_carbon(roi)
    return soc_0_20cm


def get_world_cover(roi_coords):
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    roi = ee.Geometry.Polygon(roi_coords)

    worldCover_clipped = fetch_world_cover(roi)
    return worldCover_clipped


def get_afforestation_candidates(roi_coords, start_date, end_date):
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

    chirpsYear = (
        ee.ImageCollection(gee_map_collections["precipitation"])
        .filterDate(start_date, end_date)
        .filterBounds(roi)
    )
    annualPrecipitation = chirpsYear.sum()
    elevation = get_elevation_region(roi_coords)
    slope = ee.Terrain.slope(elevation)

    filteredMoistureDataset = (
        ee.ImageCollection(gee_map_collections["rootzone_soil_moisture"])
        .filterDate("2020-01-01", "2020-01-10")
        .filterBounds(roi)
    )

    soilMoistureRootZone = filteredMoistureDataset.select("sm_rootzone")
    suitableSlope = slope.lt(15)

    suitableMoisture = soilMoistureRootZone.mean().gte(0.1)

    candidateRegions = (
        annualPrecipitation.gte(200).Or(suitableMoisture).And(suitableSlope)
    )

    worldCover = get_world_cover(roi_coords)
    grassland = worldCover.eq(30)  # Grassland class in ESA WorldCover
    barrenland = worldCover.eq(60)  # Barrenland class in ESA WorldCover
    vegetationMask = grassland.Or(barrenland)

    # Apply the mask to the candidate regions
    afforestationCandidates = candidateRegions.And(vegetationMask)

    return afforestationCandidates


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
    mean_soil_moisture_image = fetch_mean_soil_moisture((start_date, end_date), point)
    # Retrieve the mean soil moisture value at the point
    soil_moisture_value = (
        mean_soil_moisture_image.reduceRegion(ee.Reducer.first(), point, scale=1000)
        .get("mean_soil_moisture_root_zone")
        .getInfo()
    )
    return soil_moisture_value if soil_moisture_value is not None else 0


def get_precipitation_point(lat, lon, start_date, end_date):
    point = ee.Geometry.Point([lon, lat])
    total_precipitation_image = fetch_total_precipitation((start_date, end_date), point)

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
    # Load the specific image which represents soil organic carbon
    soil_organic_carbon = ee.Image(gee_map_collections["soil_organic_carbon"])

    # Use reduceRegion instead of sample to extract the value from the image
    carbon_value = (
        soil_organic_carbon.reduceRegion(
            reducer=ee.Reducer.first(),  # Using first() reducer to get the value
            geometry=point,
            scale=30,  # The scale should match the resolution at which the data is meaningful
        )
        .get("mean_0_20")
        .getInfo()
    )  # Ensure the correct band name is used

    return carbon_value


def get_elevation_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])
    elevation_image = fetch_elevation(point)

    elevation_value = (
        elevation_image.reduceRegion(ee.Reducer.first(), point, scale=10)
        .get("Elevation")
        .getInfo()
    )

    return elevation_value


def get_slope_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])

    elevation = ee.Image(gee_map_collections["elevation"])
    slope = ee.Terrain.slope(elevation)

    slope_value = slope.sample(point, 30).first().get("slope").getInfo()

    return slope_value


def get_world_cover_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    world_cover = fetch_world_cover(point)

    world_cover_value = (
        world_cover.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=10,
        )
        .get("Map")
        .getInfo()
    )  # 'Map' is the band name

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

    # Load necessary datasets
    elevation = ee.Image(gee_map_collections["elevation"])
    slope = ee.Terrain.slope(elevation)
    chirps = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate(start_date, end_date)
        .sum()
    )
    soil_moisture = (
        ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
        .filterDate("2020-01-01", "2020-01-10")  # Adjust dates as needed
        .select("sm_rootzone")
        .mean()
    )
    worldCover = ee.Image("ESA/WorldCover/v100/2020")

    # Calculate conditions using reduceRegion
    is_suitable_slope = (
        slope.lt(15).reduceRegion(ee.Reducer.first(), point, 30).get("slope").getInfo()
        is not None
    )
    is_good_precip = (
        chirps.gte(200)
        .reduceRegion(ee.Reducer.first(), point, 30)
        .get("precipitation")
        .getInfo()
        >= 200
    )
    is_suitable_moisture = (
        soil_moisture.gte(0.1)
        .reduceRegion(ee.Reducer.first(), point, 30)
        .get("sm_rootzone")
        .getInfo()
        >= 0.1
    )
    world_cover_value = (
        worldCover.reduceRegion(ee.Reducer.first(), point, 30).get("Map").getInfo()
    )

    # Check land cover
    is_grassland = world_cover_value == 30
    is_barrenland = world_cover_value == 60
    is_suitable_land = is_grassland or is_barrenland

    # Final check for afforestation candidate
    if (
        is_suitable_slope
        and is_good_precip
        and is_suitable_moisture
        and is_suitable_land
    ):
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
