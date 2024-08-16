"""
The module tests the data acquisition stage of the app.
"""

#  Python
import unittest
import time
from typing import List, Tuple

# Test
from tests._types import PeriodsDict, Period
from tests._server import PAUSE
from tests._setup import BaseTestCase

# Third party
import ee

# App
from app.stages.server_connection import establish_connection
from app.config import GEE_MAP_COLLECTIONS
from app.stages.data_acquisition.point import (
    get_rootzone_soil_moisture_point,
    get_precipitation_point,
    get_soil_organic_carbon_point,
    get_elevation_point,
    get_slope_point,
    get_world_cover_point,
    get_address_from_point,
)
from app.stages.data_acquisition.region import (
    get_rootzone_soil_moisture_region,
    get_precipitation_region,
    get_soil_organic_carbon_region,
    get_elevation_region,
    get_slope_region,
    get_world_cover_region,
    get_satellite_imagery_region,
)
from app.stages.data_acquisition.region import calculate_center
from app.config import ROI


class TestMapDataCollections(BaseTestCase):

    collections = GEE_MAP_COLLECTIONS

    @classmethod
    def setUpClass(cls):
        """Establish connection to Google Earth Engine before each test."""

        print("\nTesting Data Map Collections on Google Earth Engine:")
        establish_connection()

    def test_collections_exist(self):
        """Test that the Google Earth Engine collections exist."""

        collections = self.collections

        self.assertIsNotNone(collections)
        self.assertIsInstance(collections, dict)
        self.assertTrue(len(collections) > 0)

        for collection_name, collection_id in collections.items():

            self.assertIsNotNone(collection_id)

            self.assertIsInstance(collection_name, str)
            self.assertIsInstance(collection_id, str)

            self.assertNotEqual(collection_name, "")
            self.assertNotEqual(collection_id, "")

    def test_collections_is_on_google_earth_engine(self):
        """Test that the Google Earth Engine collections are available."""

        collections = self.collections

        for collection_name, collection_id in collections.items():

            try:
                ee.ImageCollection(collection_id)

            except Exception as e:
                self.fail(
                    f"Collection '{collection_name}' with ID '{collection_id}' not found on Google Earth Engine: {str(e)}"
                )


class TestGetPointData(unittest.TestCase):

    sahel_region: List[str] = ROI["roi_coords"]

    periods: PeriodsDict = ROI["periods"]
    soil_moisture_period: Period = periods["soil_moisture"].values()
    precipitation_period: Period = periods["precipitation"].values()

    coords: Tuple[float, float] = calculate_center(sahel_region)

    @classmethod
    def setUpClass(cls):
        """Establish connection to Google Earth Engine before each test."""

        print(
            "\nTesting fetching point data from Google Earth Engine and OpenStreetMap:"
        )
        establish_connection()

    def setUp(self):
        """Await the connection to Google Earth Engine before each test to not overload the server."""

        time.sleep(PAUSE["short"])

    def test_get_rootzone_soil_moisture_point(self):
        """Test that the rootzone soil moisture data is fetched successfully."""

        coords = self.coords
        period = self.soil_moisture_period

        try:
            get_rootzone_soil_moisture_point(*coords, *period)
        except Exception as e:
            self.fail(f"Failed to fetch rootzone soil moisture data: {str(e)}")

    def test_get_precipitation_point(self):
        """Test that the precipitation data is fetched successfully."""

        coords = self.coords
        period = self.precipitation_period

        try:
            get_precipitation_point(*coords, *period)
        except Exception as e:
            self.fail(f"Failed to fetch precipitation data: {str(e)}")

    def test_get_soil_organic_carbon_point(self):
        """Test that the soil organic carbon data is fetched successfully."""

        coords = self.coords

        try:
            get_soil_organic_carbon_point(*coords)
        except Exception as e:
            self.fail(f"Failed to fetch soil organic carbon data: {str(e)}")

    def test_get_elevation_point(self):
        """Test that the elevation data is fetched successfully."""

        coords = self.coords

        try:
            get_elevation_point(*coords)
        except Exception as e:
            self.fail(f"Failed to fetch elevation data: {str(e)}")

    def test_get_slope_point(self):
        """Test that the slope data is fetched successfully."""

        coords = self.coords

        try:
            get_slope_point(*coords)
        except Exception as e:
            self.fail(f"Failed to fetch slope data: {str(e)}")

    def test_get_world_cover_point(self):
        """Test that the world cover data is fetched successfully."""

        coords = self.coords

        try:
            get_world_cover_point(*coords)
        except Exception as e:
            self.fail(f"Failed to fetch world cover data: {str(e)}")

    def test_get_address_from_point(self):
        """
        Test that the address is fetched successfully from the coordinates.

        Note: The API is OpenStreetMap Nominatim:
        https://nominatim.openstreetmap.org/ui/search.html
        """

        coords = self.coords

        try:
            get_address_from_point(*coords)
        except Exception as e:
            self.fail(f"Failed to fetch address from coordinates: {str(e)}")


class TestRegionData(unittest.TestCase):

    sahel_region: List[str] = ROI["roi_coords"]

    periods: PeriodsDict = ROI["periods"]
    soil_moisture_period: Period = periods["soil_moisture"].values()
    precipitation_period: Period = periods["precipitation"].values()

    @classmethod
    def setUpClass(cls):
        """Establish connection to Google Earth Engine before each test."""

        print("\nTesting fetching region data from Google Earth Engine:")
        establish_connection()

    def setUp(self):
        """Await the connection to Google Earth Engine before each test to not overload the server."""

        time.sleep(PAUSE["short"])

    def test_get_rootzone_soil_moisture_region(self):
        """Test that the rootzone soil moisture data is fetched successfully for the region."""

        region = self.sahel_region
        period = self.soil_moisture_period

        try:
            get_rootzone_soil_moisture_region(region, *period)
        except Exception as e:
            self.fail(
                f"Failed to fetch rootzone soil moisture data for the region: {str(e)}"
            )

    def test_get_precipitation_region(self):
        """Test that the precipitation data is fetched successfully for the region."""

        region = self.sahel_region
        period = self.precipitation_period

        try:
            get_precipitation_region(region, *period)
        except Exception as e:
            self.fail(f"Failed to fetch precipitation data for the region: {str(e)}")

    def test_get_soil_organic_carbon_region(self):
        """Test that the soil organic carbon data is fetched successfully for the region."""

        region = self.sahel_region

        try:
            get_soil_organic_carbon_region(region)
        except Exception as e:
            self.fail(
                f"Failed to fetch soil organic carbon data for the region: {str(e)}"
            )

    def test_get_elevation_region(self):
        """Test that the elevation data is fetched successfully for the region."""

        region = self.sahel_region

        try:
            get_elevation_region(region)
        except Exception as e:
            self.fail(f"Failed to fetch elevation data for the region: {str(e)}")

    def test_get_slope_region(self):
        """Test that the slope data is fetched successfully for the region."""

        region = self.sahel_region

        try:
            get_slope_region(region)
        except Exception as e:
            self.fail(f"Failed to fetch slope data for the region: {str(e)}")

    def test_get_world_cover_region(self):
        """Test that the world cover data is fetched successfully for the region."""

        region = self.sahel_region

        try:
            get_world_cover_region(region)
        except Exception as e:
            self.fail(f"Failed to fetch world cover data for the region: {str(e)}")

    def test_get_satellite_imagery_region(self):
        """Test that the satellite imagery data is fetched successfully for the region."""

        region = self.sahel_region

        try:
            get_satellite_imagery_region(region)
        except Exception as e:
            self.fail(
                f"Failed to fetch satellite imagery data for the region: {str(e)}"
            )
