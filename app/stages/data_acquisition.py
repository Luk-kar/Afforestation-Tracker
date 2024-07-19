# Third-party imports
import ee

roi_coords = {
    "roi_coords": [[[-10.0, 15.0], [-10.0, 20.0], [10.0, 20.0], [10.0, 15.0]]],
    "start_date": "2021-01-01",
    "end_date": "2021-12-31",
}

collections = {
    "sentinel2": "COPERNICUS/S2_HARMONIZED",
    "surface_soil_moisture": "NASA/SMAP/SPL4SMGP/007",
    "sm_rootzone": "NASA/SMAP/SPL4SMGP/007",
    "srtm": "USGS/SRTMGL1_003",
    "aspect": "",
    "precipitation": "UCSB-CHG/CHIRPS/PENTAD",
    "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",
    "ESA_WorldCover_Data": "",
}


def get_data():

    print("Connection to Google Earth Engine is successful.")

    data = download_data(roi_coords, collections)

    print("data is downloaded")

    return data


def mask_clouds(image):
    qa = image.select("QA60")
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask).divide(10000)


def download_data(roi_dict, collections):

    roi = ee.Geometry.Polygon(roi_dict["roi_coords"])
    start_date = roi_dict["start_date"]
    end_date = roi_dict["end_date"]

    data = {}

    # Sentinel-2 data for NDVI and SAVI
    if "sentinel2" in collections:

        data["sentinel2"] = get_sentinel2(collections, roi, start_date, end_date)

    if "surface_soil_moisture" in collections:
        smap_collection = ee.ImageCollection(collections["surface_soil_moisture"])
        sm_surface_moisture = smap_collection.filterDate(
            start_date, end_date
        ).filterBounds(roi)
        data["surface_soil_moisture"] = sm_surface_moisture.mean().select(
            "sm_surface"
        )  # Assuming 'sm_surface' is the band name

    if "sm_rootzone" in collections:
        smap_collection = ee.ImageCollection(collections["sm_rootzone"])
        sm_rootzone_moisture = smap_collection.filterDate(
            start_date, end_date
        ).filterBounds(roi)
        data["sm_rootzone"] = sm_rootzone_moisture.mean().select(
            "sm_rootzone"
        )  # Assuming 'sm_rootzone' is the band name

    # Elevation data (SRTM) for slope and aspect calculations
    if "srtm" in collections:

        srtm = get_srtm_data(collections["srtm"], roi)

        if srtm and "aspect" in collections:

            data["aspect"] = get_aspect_data(srtm)

    # Precipitation data (CHIRPS)
    if "precipitation" in collections:

        data["precipitation"] = get_precipitation_data(
            collections["precipitation"], roi, start_date, end_date
        )

    # Soil Organic Carbon data
    if "soil_organic_carbon" in collections:

        data["soil_organic_carbon"] = get_soil_organic_carbon_data(
            collections["soil_organic_carbon"]
        )

    return data


def get_soil_organic_carbon_data(collection):
    return ee.Image(collection).select("mean_20_50").rename("Soil_Organic_Carbon")


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
        .map(mask_clouds)
        .median()
    )
