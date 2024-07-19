# Third-party imports
import ee

roi_coords = {
    "roi_coords": [
        [
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
    ],
    "start_date": "2021-01-01",
    "end_date": "2021-12-31",
}

collections = {
    "sentinel2": "COPERNICUS/S2_HARMONIZED",
    "surface_soil_moisture": "NASA/SMAP/SPL4SMGP/007",
    "sm_rootzone": "NASA/SMAP/SPL4SMGP/007",
    "srtm": "USGS/SRTMGL1_003",
    "precipitation": "UCSB-CHG/CHIRPS/PENTAD",
    "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",
    "world_cover": "ESA/WorldCover/v100/2020",
}


def get_data():
    data = download_data(roi_coords, collections)
    return data


def download_data(roi_dict, collections):
    roi = ee.Geometry.Polygon(roi_dict["roi_coords"])
    start_date = roi_dict["start_date"]
    end_date = roi_dict["end_date"]

    data = {}

    # Sentinel-2 data for NDVI and SAVI
    if "sentinel2" in collections:
        data["sentinel2"] = get_sentinel2(collections, roi, start_date, end_date)

    # Surface Soil Moisture data
    if "surface_soil_moisture" in collections:
        smap_collection = ee.ImageCollection(collections["surface_soil_moisture"])
        sm_surface_moisture = smap_collection.filterDate(
            start_date, end_date
        ).filterBounds(roi)
        data["surface_soil_moisture"] = sm_surface_moisture.mean().select("sm_surface")

    # Rootzone Soil Moisture data
    if "sm_rootzone" in collections:
        smap_collection = ee.ImageCollection(collections["sm_rootzone"])
        sm_rootzone_moisture = smap_collection.filterDate(
            start_date, end_date
        ).filterBounds(roi)
        data["sm_rootzone"] = sm_rootzone_moisture.mean().select("sm_rootzone")

    # Elevation data (SRTM) for slope and aspect calculations
    if "srtm" in collections:
        srtm = get_srtm_data(collections["srtm"], roi)
        data["srtm"] = srtm
        data["aspect"] = get_aspect_data(srtm)
        data["slope"] = get_slope_data(srtm)

    # Precipitation data (CHIRPS)
    if "precipitation" in collections:
        data["precipitation"] = get_precipitation_data(
            collections["precipitation"], roi, start_date, end_date
        )

    # Soil Organic Carbon data
    if "soil_organic_carbon" in collections:
        data["soil_organic_carbon"] = get_soil_organic_carbon_data(
            collections["soil_organic_carbon"], roi
        )

    # ESA WorldCover Data
    if "world_cover" in collections:
        data["world_cover"] = get_world_cover_data(collections["world_cover"], roi)

    return data


def get_soil_organic_carbon_data(collection, roi):
    return (
        ee.Image(collection).clip(roi).select("mean_0_20").rename("Soil_Organic_Carbon")
    )


def get_precipitation_data(collection, roi, start_date, end_date):
    return (
        ee.ImageCollection(collection)
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .sum()
        .rename("Precipitation")
    )


def get_aspect_data(srtm):
    return ee.Terrain.aspect(srtm).rename("Aspect")


def get_slope_data(srtm):
    return ee.Terrain.slope(srtm).rename("Slope")


def get_srtm_data(collection, roi):
    return ee.Image(collection).clip(roi)


def get_soil_moisture(collection, roi, start_date, end_date):
    return (
        ee.ImageCollection(collection)
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .mean()
        .select("sm_surface")
        .rename("Soil_Moisture")
    )


def get_sentinel2(collections, roi, start_date, end_date):
    return (
        ee.ImageCollection(collections["sentinel2"])
        .filterDate(start_date, end_date)
        .filterBounds(roi)
        .median()
    )


def get_world_cover_data(collection, roi):
    return ee.Image(collection).clip(roi)


# Data structure: data["sentinel2"], data["surface_soil_moisture"], data["sm_rootzone"], data["srtm"], data["aspect"], data["slope"], data["precipitation"], data["soil_organic_carbon"], data["world_cover"]
