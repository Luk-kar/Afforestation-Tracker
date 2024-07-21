import geemap.foliumap as geemap

# Initialize the Earth Engine module
from stages.connection import establish_connection
from stages.data_acquisition import (
    get_rootzone_soil_moisture,
    get_precipitation_data,
    get_elevation,
    get_slope,
    get_soil_organic_carbon,
    get_world_cover,
    get_afforestation_candidates,
)

establish_connection()


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
start_date = "2020-06-01"
end_date = "2020-10-01"

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

candidate_vis = {
    "min": 0,
    "max": 1,
    "palette": ["red", "green"],
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
elevation_clipped = get_elevation(roi_coords)
slope = get_slope(roi_coords)
soc_0_20cm_clipped = get_soil_organic_carbon(roi_coords)
worldCover_clipped = get_world_cover(roi_coords)
afforestation_candidates = get_afforestation_candidates(
    roi_coords, start_date, end_date
)


add_layer_to_map(
    Map, mean_soil_moisture_rootzone, moisture_vis_params, "Root Zone Soil Moisture"
)
add_layer_to_map(Map, elevation_clipped, elevation_vis, "Elevation")
add_layer_to_map(Map, slope, slope_vis, "Slope")
add_layer_to_map(Map, soc_0_20cm_clipped, soc_vis, "Soil Organic Carbon 0-20cm")
add_layer_to_map(Map, worldCover_clipped, regions_vis, "ESA WorldCover 2020")
add_layer_to_map(Map, precipitation_map, precipitation_vis, "Precipitation")
add_layer_to_map(
    Map, afforestation_candidates, candidate_vis, "Candidate Regions for Afforestation"
)

# Display the map in Streamlit
Map.to_streamlit(height=600)
