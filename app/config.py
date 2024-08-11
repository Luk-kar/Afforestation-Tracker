"""
Configuration file for the app

This file contains the configuration for the app. It is used to store the
configuration for the different stages of the app. This includes the
configuration for the data acquisition, data processing, and data visualization
stages.
"""

SIZE_SAMPLE_METERS = 100  # google earth engine sample size

ROI_COORDS = [
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

ROI = {
    "roi_coords": ROI_COORDS,
    "periods": {
        "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
        "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
    },
}

# Google Earth Engine Collections
# All of the data is open-source, Google provides the server side computation
GEE_MAP_COLLECTIONS = {
    "rootzone_soil_moisture": "NASA/SMAP/SPL4SMGP/007",  # https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_007
    "precipitation": "UCSB-CHG/CHIRPS/DAILY",  # https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
    "elevation": "USGS/SRTMGL1_003",  # https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003
    "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",  # https://developers.google.com/earth-engine/datasets/catalog/ISDASOIL_Africa_v1_carbon_total
    "world_type_terrain_cover": "ESA/WorldCover/v100/2020",  # https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100
    "satellite_imagery": "COPERNICUS/S2_HARMONIZED",  # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_HARMONIZED
}

MAP_DATA = {
    "satellite_imagery": {
        "vis_params": {
            "bands": ["B4", "B3", "B2"],  # Example bands for RGB true color
        },
        "name": "Satellite Imagery",
        "shown": False,
    },
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
        "shown": False,
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
        "shown": False,
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
        "shown": False,
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
        "shown": False,
    },
    "soil_moisture": {
        "vis_params": {
            "min": 0.0,
            "max": 0.5,
            "palette": ["red", "yellow", "green", "blue"],
        },
        "name": "Root Zone Moisture",
        "legend": {
            "title": "Root Zone Moisture",
            "legend_dict": {
                "0.0-12.5": "FF0000",  # Red
                "12.5-25.0": "FFFF00",  # Yellow
                "25.0.-37.5": "008000",  # Green
                "37.5-50.0": "0000FF",  # Blue
            },
        },
        "shown": True,
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
        "shown": True,
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
        "shown": True,
    },
}
