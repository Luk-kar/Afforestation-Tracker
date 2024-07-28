# Third party
import requests
import ee

# Local
from stages.data_acquisition.gee_server import (
    fetch_total_precipitation_data,
    fetch_mean_soil_moisture_data,
    fetch_elevation_data,
    fetch_soil_organic_carbon_data,
    fetch_slope_data,
    fetch_world_cover_data,
)
from stages.data_categorization import evaluate_afforestation_candidates


def get_rootzone_soil_moisture_point(lat, lon, start_date, end_date):
    """
    Retrieves the mean soil moisture value at a specific point for a specified date range.

    Parameters:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.
        start_date (str): The start date for the period of interest in 'YYYY-MM-DD' format.
        end_date (str): The end date for the period of interest in 'YYYY-MM-DD' format.

    Returns:
        float: Average soil moisture value at the given point for the specified date range, or 0 if no data is available.
    """
    point = ee.Geometry.Point([lon, lat])
    mean_soil_moisture_image = fetch_mean_soil_moisture_data(
        (start_date, end_date), point
    )

    soil_moisture_value = (
        mean_soil_moisture_image.reduceRegion(ee.Reducer.first(), point, scale=100)
        .get("mean_soil_moisture_root_zone")
        .getInfo()
    )
    return soil_moisture_value if soil_moisture_value is not None else 0


def get_precipitation_point(lat, lon, start_date, end_date):

    point = ee.Geometry.Point([lon, lat])
    total_precipitation_image = fetch_total_precipitation_data(
        (start_date, end_date), point
    )

    precipitation_value = (
        total_precipitation_image.reduceRegion(
            reducer=ee.Reducer.first(), geometry=point, scale=100
        )
        .get("total_precipitation")
        .getInfo()
    )

    return precipitation_value


def get_soil_organic_carbon_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])
    soil_organic_carbon = fetch_soil_organic_carbon_data(point)

    carbon_value = (
        soil_organic_carbon.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=100,
        )
        .get("soil_organic_carbon")
        .getInfo()
    )

    return carbon_value


def get_elevation_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])
    elevation_image = fetch_elevation_data(point)

    elevation_value = (
        elevation_image.reduceRegion(ee.Reducer.first(), point, scale=10)
        .get("elevation")
        .getInfo()
    )

    return elevation_value


def get_slope_point(lat, lon):

    point = ee.Geometry.Point([lon, lat])

    slope = fetch_slope_data(point)

    slope_value = (
        slope.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=100,
        )
        .get("slope")
        .getInfo()
    )

    # Assign a default value of 0
    # if no elevation variation is detected in the area,
    # which results in a 'None' slope value.
    if slope_value is None:
        slope_value = 0

    return slope_value


def get_world_cover_point(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    world_cover = fetch_world_cover_data(point)

    world_cover_value = (
        world_cover.reduceRegion(
            reducer=ee.Reducer.first(),
            geometry=point,
            scale=100,
        )
        .get("world_cover")
        .getInfo()
    )

    return world_cover_value


def get_address_from_point(lat, lon):
    """Fetch address from Nominatim Geocoding API using latitude and longitude."""
    base_url = "https://nominatim.openstreetmap.org/reverse"
    headers = {"User-Agent": "MyApp"}
    params = {"lat": lat, "lon": lon, "format": "json"}
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        json_result = response.json()
        address = json_result.get("display_name")
        if address:
            return address
        else:
            return "No address found."
    else:
        return "Error in Geocoding API call."


def get_map_point_data(roi, lat, lon):

    data = {
        "elevation": get_elevation_point(lat, lon),
        "slope": get_slope_point(lat, lon),
        "soil_moisture": get_rootzone_soil_moisture_point(
            lat,
            lon,
            roi["periods"]["soil_moisture"]["start_date"],
            roi["periods"]["soil_moisture"]["end_date"],
        ),
        "precipitation": get_precipitation_point(
            lat,
            lon,
            roi["periods"]["precipitation"]["start_date"],
            roi["periods"]["precipitation"]["end_date"],
        ),
        "soil_organic_carbon": get_soil_organic_carbon_point(lat, lon),
        "world_cover": get_world_cover_point(lat, lon),
        "address": get_address_from_point(lat, lon),
        "lat": lat,
        "lon": lon,
    }

    data["afforestation_validation"] = evaluate_afforestation_candidates(
        data["slope"],
        data["precipitation"],
        data["soil_moisture"],
        data["world_cover"],
    )
    return data
