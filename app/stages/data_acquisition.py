import ee

import requests


def get_rootzone_soil_moisture(roi_coords, start_date, end_date):
    """
    Retrieves the mean root zone soil moisture for a specified date range.

    Parameters:
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The mean root zone soil moisture image for the specified period.
    """
    dataset = ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
    roi = ee.Geometry.Polygon(roi_coords)
    filtered_dataset = dataset.filterDate(start_date, end_date).filterBounds(roi)
    soil_moisture_rootzone = filtered_dataset.select("sm_rootzone")
    mean_soil_moisture_rootzone = soil_moisture_rootzone.mean().clip(roi)
    return mean_soil_moisture_rootzone


def get_precipitation_data(roi_coords, start_date, end_date):
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
    return (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .select("precipitation")
        .map(lambda image: image.clip(roi))  # Clip each image to the ROI
        .sum()
        .rename("Precipitation")
    )


def get_elevation(roi_coords):
    """
    Retrieves the elevation data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The elevation image for the specified region.
    """
    elevation = ee.Image("USGS/SRTMGL1_003")
    roi = ee.Geometry.Polygon(roi_coords)
    elevation_clipped = elevation.clip(roi)
    return elevation_clipped


def get_slope(roi_coords):
    """
    Retrieves the slope data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The slope image for the specified region.
    """
    elevation = get_elevation(roi_coords)
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
    soilGrids = ee.Image("ISDASOIL/Africa/v1/carbon_total")
    soc_0_20cm = soilGrids.select("mean_0_20")
    roi = ee.Geometry.Polygon(roi_coords)
    soc_0_20cm_clipped = soc_0_20cm.clip(roi)
    return soc_0_20cm_clipped


def get_world_cover(roi_coords):
    """
    Retrieves the world cover data for the specified region of interest.

    Parameters:
        roi_coords (list): List of coordinates defining the region of interest.

    Returns:
        ee.Image: The world cover image for the specified region.
    """
    worldCover = ee.Image("ESA/WorldCover/v100/2020")
    roi = ee.Geometry.Polygon(roi_coords)
    worldCover_clipped = worldCover.clip(roi)
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
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate(start_date, end_date)
        .filterBounds(roi)
    )
    annualPrecipitation = chirpsYear.sum()
    elevation = get_elevation(roi_coords)
    slope = ee.Terrain.slope(elevation)

    filteredMoistureDataset = (
        ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
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


def get_rootzone_soil_moisture_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    soil_moisture = ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")

    # Filter the collection to a specific period if necessary and reduce it to get a single image
    # Here we're assuming to take the first available image for simplicity
    latest_soil_moisture_image = (
        soil_moisture.first()
    )  # Assuming you want the latest available data

    # Now using the 'sm_rootzone' band
    soil_moisture_value = (
        latest_soil_moisture_image.reduceRegion(
            ee.Reducer.first(),  # Use the appropriate reducer
            point,
            scale=1000,  # Set an appropriate scale based on dataset resolution
        )
        .get("sm_rootzone")
        .getInfo()
    )

    if soil_moisture_value is None:
        soil_moisture_value = 0

    return soil_moisture_value


def get_precipitation_point(lat, lon, start_date, end_date):
    point = ee.Geometry.Point([lon, lat])
    # Get the precipitation data image collection
    precipitation = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")

    # Filter the collection based on the specified date range
    total_precipitation = precipitation.filterDate(start_date, end_date).sum()

    # Use reduceRegion to get a single value
    precipitation_value = (
        total_precipitation.reduceRegion(
            reducer=ee.Reducer.first(),  # Using first() reducer to get the value at the point
            geometry=point,
            scale=30,  # Scale parameter should be set appropriately for the data resolution
        )
        .get("precipitation")
        .getInfo()
    )  # Make sure 'precipitation' is the correct band name

    return precipitation_value


def get_soil_organic_carbon_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    # Load the specific image which represents soil organic carbon
    soil_organic_carbon = ee.Image("ISDASOIL/Africa/v1/carbon_total")

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
    point = ee.Geometry.Point(lon, lat)
    elevation = (
        ee.Image("USGS/SRTMGL1_003")
        .sample(point, 30)
        .first()
        .get("elevation")
        .getInfo()
    )
    return elevation


def get_slope_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])

    elevation = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(elevation)

    slope_value = slope.sample(point, 30).first().get("slope").getInfo()

    return slope_value


def get_world_cover_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    world_cover = ee.Image("ESA/WorldCover/v100/2020")

    # Use reduceRegion instead of sample to get the value directly
    world_cover_value = (
        world_cover.reduceRegion(
            reducer=ee.Reducer.first(),  # Getting the first value that matches the point
            geometry=point,
            scale=10,  # Adjust scale according to the resolution of the WorldCover data
        )
        .get("Map")
        .getInfo()
    )  # 'Map' is the band name

    # Mapping from WorldCover class IDs to names
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

    # Return the corresponding class name for the world cover value
    return class_names.get(
        world_cover_value, "Unknown Cover"
    )  # Default to "Unknown Class" if not found


def get_afforestation_candidates_point(lat, lon, start_date, end_date):
    point = ee.Geometry.Point([lon, lat])

    # Load necessary datasets
    elevation = ee.Image("USGS/SRTMGL1_003")
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
