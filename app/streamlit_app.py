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

roi = {
    "roi_coords": roi_coords,
    "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
    "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
}

map_data = {
    "soil_moisture": {
        "data": get_rootzone_soil_moisture(
            roi["roi_coords"],
            roi["soil_moisture"]["start_date"],
            roi["soil_moisture"]["end_date"],
        ),
        "vis_params": {
            "min": 0.0,
            "max": 0.5,
            "palette": ["red", "yellow", "green", "blue"],
        },
        "name": "Root Zone Soil Moisture",
        "legend": {
            "title": "Root Zone Soil Moisture",
            "legend_dict": {
                "Low": "red",
                "Moderate": "yellow",
                "High": "green",
                "Very High": "blue",
            },
        },
    },
    "precipitation": {
        "data": get_precipitation_data(
            roi["roi_coords"],
            roi["precipitation"]["start_date"],
            roi["precipitation"]["end_date"],
        ),
        "vis_params": {
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
        "name": "Precipitation",
        "legend": {
            "title": "Precipitation",
            "legend_dict": {
                "Very Low": "FFFFFF",
                "Low": "C0C0C0",
                "Moderate Low": "808080",
                "Moderate": "404040",
                "Moderate High": "000000",
                "High": "0000FF",
                "Very High": "00FFFF",
            },
        },
    },
    "elevation": {
        "data": get_elevation(roi["roi_coords"]),
        "vis_params": {
            "min": 0,
            "max": 3000,
            "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Elevation",
    },
    "slope": {
        "data": get_slope(roi["roi_coords"]),
        "vis_params": {
            "min": 0,
            "max": 60,
            "palette": ["00FFFF", "0000FF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Slope",
    },
    "soc_0_20cm": {
        "data": get_soil_organic_carbon(roi["roi_coords"]),
        "vis_params": {
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
        "name": "Soil Organic Carbon 0-20cm",
    },
    "world_cover": {
        "data": get_world_cover(roi["roi_coords"]),
        "vis_params": {
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
        "name": "ESA WorldCover 2020",
    },
    "afforestation_candidates": {
        "data": get_afforestation_candidates(
            roi["roi_coords"],
            roi["precipitation"]["start_date"],
            roi["precipitation"]["end_date"],
        ),
        "vis_params": {
            "min": 0,
            "max": 1,
            "palette": ["red", "green"],
        },
        "name": "Candidate Regions for Afforestation",
    },
}


def add_layer_to_map(Map, layer):
    data = layer["data"]
    vis_params = layer["vis_params"]
    name = layer["name"]
    legend = layer.get("legend", None)

    Map.addLayer(data, vis_params, name)
    if legend:
        print("legend:", legend)
        Map.add_legend(title=legend["title"], legend_dict=legend["legend_dict"])


def display_map(map_data):
    Map = geemap.Map(center=(20, 0), zoom=2)

    # Add layers to the map
    for layer in map_data.values():
        add_layer_to_map(Map, layer)

    # Display the map in Streamlit
    Map.to_streamlit()


display_map(map_data)
