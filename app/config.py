# Local
from stages.data_acquisition.region import (
    get_rootzone_soil_moisture_region,
    get_precipitation_region,
    get_elevation_region,
    get_slope_region,
    get_soil_organic_carbon_region,
    get_world_cover_region,
    get_afforestation_candidates_region,
)
from stages.data_acquisition.gee_server import (
    world_cover_esa_codes,
)

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
]  # Sahel geo-polygon

roi = {
    "roi_coords": roi_coords,
    "periods": {
        "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
        "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
    },
}

map_data = {
    "elevation": {
        "vis_params": {
            "min": 0,
            "max": 3000,
            "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Elevation",
        "legend": {
            "title": "Elevation (m)",
            "legend_dict": {
                "0-600 m": "0000FF",
                "600-1200 m": "00FFFF",
                "1200-1800 m": "00FF00",
                "1800-2400 m": "FFFF00",
                "2400-3000 m": "FF0000",
            },
        },
    },
    "slope": {
        "vis_params": {
            "min": 0,
            "max": 60,
            "palette": ["00FFFF", "0000FF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Slope",
        "legend": {
            "title": "Slope (degrees)",
            "legend_dict": {
                "0-12°": "0000FF",
                "12-24°": "00FFFF",
                "24-36°": "00FF00",
                "36-48°": "FFFF00",
                "48-60°": "FF0000",
            },
        },
    },
    "world_cover": {
        "vis_params": {
            "bands": ["world_cover"],
            "min": 10,
            "max": 100,
            "palette": [
                "006400",
                "FFBB22",
                "FFFF4C",
                "F096FF",
                "FA0000",
                "B4B4B4",
                "F0F0F0",
                "0064C8",
                "0096A0",
                "00CF75",
                "FAE6A0",
            ],
        },
        "name": "World Cover",
        "legend": {
            "title": "World Cover",
            "legend_dict": {
                "Tree Cover": "006400",
                "Shrubland": "FFBB22",
                "Grassland": "FFFF4C",
                "Cropland": "F096FF",
                "Built-up": "FA0000",
                "Bare / Sparse Vegetation": "B4B4B4",
                "Snow and Ice": "F0F0F0",
                "Permanent Water Bodies": "0064C8",
                "Herbaceous Wetland": "0096A0",
                "Mangroves": "00CF75",
                "Moss and Lichen": "FAE6A0",
            },
        },
    },
    "soc_0_20cm": {
        "vis_params": {
            "min": 0,
            "max": 200,
            "palette": ["FFFFFF", "C0C0C0", "808080", "404040", "000000"],
        },
        "name": "Soil Organic Carbon 0-20cm",
        "legend": {
            "title": "Soil Organic Carbon (0-20 cm) g/kg",
            "legend_dict": {
                "0-40 g/kg": "FFFFFF",
                "40-80 g/kg": "C0C0C0",
                "80-120 g/kg": "808080",
                "120-160 g/kg": "404040",
                "160-200 g/kg": "000000",
            },
        },
    },
    "soil_moisture": {
        "vis_params": {
            "min": 0.0,
            "max": 0.5,
            "palette": ["red", "yellow", "green", "blue"],
        },
        "name": "Root Zone Moisture %",
        "legend": {
            "title": "Root Zone Moisture %",
            "legend_dict": {
                "0.0-12.5": "FF0000",  # Red
                "12.5-25.0.": "FFFF00",  # Yellow
                "25.0.-37.5": "008000",  # Green
                "37.5-50.0": "0000FF",  # Blue
            },
        },
    },
    "precipitation": {
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
                "0-200 mm": "FFFFFF",
                "200-400 mm": "C0C0C0",
                "400-600 mm": "808080",
                "600-800 mm": "404040",
                "800-1000 mm": "000000",
                "1000-1200 mm": "0000FF",
                "1200-1400 mm": "00FFFF",
                "1400-1600 mm": "00FF00",
                "1600-1800 mm": "FFFF00",
                "1800-2000 mm": "FF0000",
            },
        },
    },
    "afforestation_candidates": {
        "vis_params": {
            "min": 0,
            "max": 1,
            "palette": ["red", "green"],
        },
        "name": "Planting Zones",
        "legend": {
            "title": "Planting Zones",
            "legend_dict": {
                "Not Suitable": "FF0000",
                "Suitable": "00FF00",
            },
        },
    },
}


def validate_are_keys_the_same(dict1, dict2):
    if set(dict1.keys()) != set(dict2.keys()):
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())
        error_message = "Dictionaries have mismatched keys.\n"
        if missing_in_dict1:
            error_message += f"Missing in dict1: {missing_in_dict1}\n"
        if missing_in_dict2:
            error_message += f"Missing in dict2: {missing_in_dict2}\n"
        raise ValueError(error_message)


validate_are_keys_the_same(
    world_cover_esa_codes, map_data["world_cover"]["legend"]["legend_dict"]
)


def get_map_region_data(roi, map_data):
    """
    Enrich the map data dictionary with additional environmental data layers for the specified region of interest.

    Parameters:
        roi (dict): Dictionary containing the region of interest coordinates and periods for data fetching.
        map_data (dict): Dictionary containing the current map data layers to be enriched.

    """
    # Fetch and update each environmental layer in the map_data dictionary

    # Elevation
    map_data["elevation"]["data"] = get_elevation_region(roi["roi_coords"])

    # Slope
    map_data["slope"]["data"] = get_slope_region(roi["roi_coords"])

    # World Cover
    map_data["world_cover"]["data"] = get_world_cover_region(roi["roi_coords"])

    # Soil Organic Carbon
    map_data["soc_0_20cm"]["data"] = get_soil_organic_carbon_region(roi["roi_coords"])

    # Soil Moisture
    map_data["soil_moisture"]["data"] = get_rootzone_soil_moisture_region(
        roi["roi_coords"],
        roi["periods"]["soil_moisture"]["start_date"],
        roi["periods"]["soil_moisture"]["end_date"],
    )

    # Precipitation
    map_data["precipitation"]["data"] = get_precipitation_region(
        roi["roi_coords"],
        roi["periods"]["precipitation"]["start_date"],
        roi["periods"]["precipitation"]["end_date"],
    )

    # Afforestation Candidates
    map_data["afforestation_candidates"]["data"] = get_afforestation_candidates_region(
        roi["roi_coords"], roi["periods"]
    )

    # Validate that all layers have matching keys in their legend dicts
    for key, layer in map_data.items():
        if "legend" in layer and "legend_dict" in layer["legend"]:
            try:
                validate_are_keys_the_same(
                    world_cover_esa_codes, layer["legend"]["legend_dict"]
                )
            except ValueError as e:
                print(f"Validation error in {key} layer: {str(e)}")

    return map_data


# Call the function with existing roi and map_data
map_data_regions = get_map_region_data(roi, map_data)
