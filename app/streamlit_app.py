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


# Define region of interest coordinates
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

# Define visualization parameters for different layers
vis_params = {
    "moisture": {
        "min": 0.0,
        "max": 0.5,
        "palette": ["red", "yellow", "green", "blue"],
    },
    "precipitation": {
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
    },
    "elevation": {
        "min": 0,
        "max": 3000,
        "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
    },
    "slope": {
        "min": 0,
        "max": 60,
        "palette": ["00FFFF", "0000FF", "00FF00", "FFFF00", "FF0000"],
    },
    "soc": {
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
    },
    "regions": {
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
    },
    "candidate": {
        "min": 0,
        "max": 1,
        "palette": ["red", "green"],
    },
}

# Define input data for the maps
roi = {
    "roi_coords": roi_coords,
    "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
    "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
}

# Create a map centered on the specified location and zoom level
Map = geemap.Map(center=(20, 0), zoom=2)

# Get the mean root zone soil moisture image for the specified date range
mean_soil_moisture_rootzone = get_rootzone_soil_moisture(
    roi["roi_coords"],
    roi["soil_moisture"]["start_date"],
    roi["soil_moisture"]["end_date"],
)

# Get other data layers for the specified date range
precipitation_map = get_precipitation_data(
    roi["roi_coords"],
    roi["precipitation"]["start_date"],
    roi["precipitation"]["end_date"],
)
elevation_clipped = get_elevation(roi["roi_coords"])
slope = get_slope(roi["roi_coords"])
soc_0_20cm_clipped = get_soil_organic_carbon(roi["roi_coords"])
worldCover_clipped = get_world_cover(roi["roi_coords"])
afforestation_candidates = get_afforestation_candidates(
    roi["roi_coords"],
    roi["precipitation"]["start_date"],
    roi["precipitation"]["end_date"],
)

# Add layers to the map
add_layer_to_map(
    Map, mean_soil_moisture_rootzone, vis_params["moisture"], "Root Zone Soil Moisture"
)
add_layer_to_map(Map, elevation_clipped, vis_params["elevation"], "Elevation")
add_layer_to_map(Map, slope, vis_params["slope"], "Slope")
add_layer_to_map(
    Map, soc_0_20cm_clipped, vis_params["soc"], "Soil Organic Carbon 0-20cm"
)
add_layer_to_map(Map, worldCover_clipped, vis_params["regions"], "ESA WorldCover 2020")
add_layer_to_map(Map, precipitation_map, vis_params["precipitation"], "Precipitation")
add_layer_to_map(
    Map,
    afforestation_candidates,
    vis_params["candidate"],
    "Candidate Regions for Afforestation",
)

# Display the map in Streamlit
Map.to_streamlit(height=600)
