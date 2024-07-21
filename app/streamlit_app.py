import streamlit as st
import geemap.foliumap as geemap
import ee

# Initialize the Earth Engine module
from stages.connection import establish_connection

establish_connection()


def get_rootzone_soil_moisture(roi_coords, start_date, end_date):
    """
    Retrieves the mean root zone soil moisture for a specified date range.

    Parameters:
        start_date (str): The start date of the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date of the period of interest in 'YYYY-MM-DD' format.

    Returns:
        ee.Image: The mean root zone soil moisture image for the specified period.
    """

    # Load the ImageCollection for SMAP Level 4 Global Daily 9 km EASE-Grid Soil Moisture
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


def add_layer_to_map(Map, image, vis_params, layer_name):
    Map.addLayer(image, vis_params, layer_name)


roi_coords = [
    [-17.5, 15.0],
    [-17.5, 20.0],
    [39.0, 20.0],
    [43.0, 10.5],
    [35.0, 8.0],
    [25.0, 10.0],
    [15.0, 8.0],
    [-5.0, 12.0],
    [-10.0, 13.0],
]
start_date = "2020-01-01"
end_date = "2020-01-10"

# Set visualization parameters for the soil moisture
moisture_vis_params = {
    "min": 0.0,
    "max": 0.5,
    "palette": ["red", "yellow", "green", "blue"],
}

# Adjusted visualization parameters for precipitation
precipitation_vis = {
    "min": 0,
    "max": 2000,
    "palette": [
        "FFFFFF",
        "C0C0C0",
        "808080",
        "404040",
        "000000",
        "0000FF",
        "00FFFF",
        "00FF00",
        "FFFF00",
        "FF0000",
    ],
}

# Additional datasets
elevation = ee.Image("USGS/SRTMGL1_003")
soilGrids = ee.Image("ISDASOIL/Africa/v1/carbon_total")
soc_0_20cm = soilGrids.select("mean_0_20")
worldCover = ee.Image("ESA/WorldCover/v100/2020")

# Visualization parameters for additional layers
elevation_vis = {
    "min": 0,
    "max": 3000,
    "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
}

slope_vis = {
    "min": 0,
    "max": 60,
    "palette": ["00FFFF", "0000FF", "00FF00", "FFFF00", "FF0000"],
}

soc_vis = {
    "min": 0,
    "max": 200,
    "palette": [
        "FFFFFF",
        "C0C0C0",
        "808080",
        "404040",
        "000000",
        "00FF00",
        "008000",
        "FFFF00",
        "FFA500",
        "FF0000",
    ],
}

regions_vis = {
    "bands": ["Map"],
    "min": 10,
    "max": 100,
    "palette": [
        "006400",  # Tree cover - Dark Green
        "FFBB22",  # Shrubland - Light Orange
        "FFFF4C",  # Grassland - Yellow
        "F096FF",  # Cropland - Light Pink
        "FA0000",  # Built-up - Bright Red
        "B4B4B4",  # Bare / Sparse vegetation - Grey
        "F0F0F0",  # Snow and ice - White
        "0064C8",  # Permanent water bodies - Blue
        "0096A0",  # Herbaceous wetland - Cyan
        "00CF75",  # Mangroves - Green
        "FAE6A0",  # Moss and lichen - Light Yellow
    ],
}

# Create a map centered on the specified location and zoom level
Map = geemap.Map(center=(20, 0), zoom=2)

# Get the mean root zone soil moisture image for the specified date range
mean_soil_moisture_rootzone = get_rootzone_soil_moisture(
    roi_coords, start_date, end_date
)
start_date = "2023-01-01"
end_date = "2023-12-31"

precipitation_map = get_precipitation_data(roi_coords, start_date, end_date)

# Add the root zone soil moisture layer to the map
# add_layer_to_map(
#     Map, mean_soil_moisture_rootzone, moisture_vis_params, "Root Zone Soil Moisture"
# )

# Add additional layers to the map
roi = ee.Geometry.Polygon(roi_coords)
elevation_clipped = elevation.clip(roi)
slope = ee.Terrain.slope(elevation_clipped)
soc_0_20cm_clipped = soc_0_20cm.clip(roi)
worldCover_clipped = worldCover.clip(roi)

# add_layer_to_map(Map, elevation_clipped, elevation_vis, "Elevation")
# add_layer_to_map(Map, slope, slope_vis, "Slope")
# add_layer_to_map(Map, soc_0_20cm_clipped, soc_vis, "Soil Organic Carbon 0-20cm")
# add_layer_to_map(Map, worldCover_clipped, regions_vis, "ESA WorldCover 2020")
add_layer_to_map(Map, precipitation_map, precipitation_vis, "Precipitation")

# Define the time range for one year (e.g., 2023)
startDate = "2023-01-01"
endDate = "2023-12-31"

# Filter the CHIRPS data to the specified date range and region
chirpsYear = (
    ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
    .filterDate(startDate, endDate)
    .filterBounds(roi)
)

# Sum the daily precipitation to get the annual precipitation
annualPrecipitation = chirpsYear.sum()

# Calculate the slope in degrees
slope = ee.Terrain.slope(elevation_clipped)

# Define the time period of interest for moisture (modify dates as needed)
filteredMoistureDataset = (
    ee.ImageCollection("NASA/SMAP/SPL4SMGP/007")
    .filterDate("2020-01-01", "2020-01-10")
    .filterBounds(roi)
)

# Select the 'sm_surface' and 'sm_rootzone' bands
soilMoistureSurface = filteredMoistureDataset.select("sm_surface")
soilMoistureRootZone = filteredMoistureDataset.select("sm_rootzone")

# Identify regions with minimal slope
suitableSlope = slope.lt(15)

# Identify regions with minimal soil organic carbon or sufficient moisture
suitableSOC = soc_0_20cm_clipped.gt(20)  # Example: suitable SOC greater than 20 g/kg
suitableMoisture = soilMoistureSurface.mean().gte(
    0.1
)  # Suitable soil moisture greater than or equal to 10% VWC
goodMoisture = suitableSOC.Or(suitableMoisture)

# Combine criteria to identify candidate regions
candidateRegions = annualPrecipitation.gte(200).And(suitableSlope).And(goodMoisture)

# Mask out areas that are not Grass or Shrubland or Barrenland
grassland = worldCover_clipped.eq(30)  # Grassland class in ESA WorldCover
barrenland = worldCover_clipped.eq(60)  # Barrenland class in ESA WorldCover
vegetationMask = grassland.Or(barrenland)

# Apply the mask to the candidate regions
afforestationCandidates = candidateRegions.And(vegetationMask)

# Visualization parameters for candidate regions
candidateVis = {
    "min": 0,
    "max": 1,
    "palette": ["red", "green"],
}

# Add the afforestation candidates layer to the map
add_layer_to_map(
    Map, afforestationCandidates, candidateVis, "Candidate Regions for Afforestation"
)


# Display the map in Streamlit
Map.to_streamlit(height=600)
