import ee


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
    soc = get_soil_organic_carbon(roi_coords)
    suitableSOC = soc.gt(20)  # Example: suitable SOC greater than 20 g/kg
    suitableMoisture = soilMoistureRootZone.mean().gte(
        0.1
    )  # Suitable soil moisture greater than or equal to 10% VWC
    goodMoisture = suitableSOC.Or(suitableMoisture)

    candidateRegions = annualPrecipitation.gte(200).And(suitableSlope).And(goodMoisture)

    worldCover = get_world_cover(roi_coords)
    grassland = worldCover.eq(30)  # Grassland class in ESA WorldCover
    barrenland = worldCover.eq(60)  # Barrenland class in ESA WorldCover
    vegetationMask = grassland.Or(barrenland)

    # Apply the mask to the candidate regions
    afforestationCandidates = candidateRegions.And(vegetationMask)

    return afforestationCandidates
