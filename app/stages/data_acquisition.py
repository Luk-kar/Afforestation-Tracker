# Third-party imports
import ee
import geemap

# Local imports
from stages.connection import establish_connection


def get_data():

    roi_coords = {
        "roi_coords": [[[-10.0, 15.0], [-10.0, 20.0], [10.0, 20.0], [10.0, 15.0]]],
        "start_date": "2021-01-01",
        "end_date": "2021-12-31",
    }

    collection_types_args = {
        "sentinel2": "COPERNICUS/S2_HARMONIZED",
        "soil_moisture": "NASA/SMAP/SPL4SMGP/007",
        "srtm": "USGS/SRTMGL1_003",
        "slope": "",
        "aspect": "",
        "precipitation": "UCSB-CHG/CHIRPS/PENTAD",
        "soil_organic_carbon": "ISDASOIL/Africa/v1/carbon_total",
    }

    establish_connection()

    print("Connection to Google Earth Engine is successful.")

    data = download_data(roi_coords, collection_types_args)

    print("data is downloaded")

    # Display the acquired data (for verification)

    Map = geemap.Map(center=[17.5, 0.0], zoom=5)
    for key, layer in data.items():
        Map.addLayer(layer, {"min": 0, "max": 1}, key.capitalize())

    map_path = "output_map.html"
    Map.save(map_path)
    print(f"Map has been saved to {map_path}")


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

    # Soil Moisture data
    if "soil_moisture" in collections:

        data["soil_moisture"] = get_soil_moisture(
            collections["soil_moisture"], roi, start_date, end_date
        )

    # Elevation data (SRTM) for slope and aspect calculations
    if "srtm" in collections:

        srtm = get_srtm_data(collections["srtm"], roi)

        if srtm:
            if "slope" in collections:
                data["slope"] = get_slope_data(srtm)

            if "aspect" in collections:
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
        .map(mask_clouds)
        .median()
    )
