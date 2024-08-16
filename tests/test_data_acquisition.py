"""
The module tests the data acquisition stage of the app.
"""

#  Python
from contextlib import contextmanager
import unittest
import time
from typing import List, Tuple

# Test
from tests._types import PeriodsDict, Period
from tests._server import PAUSE
from tests._setup import BaseTestCase

# Third party
import ee
import requests

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
    """Test the map data collections on Google Earth Engine."""

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

            except ee.EEException as e:  # Specific to Earth Engine errors
                self.fail(
                    f"Collection '{collection_name}' with ID '{collection_id}' not found on Google Earth Engine: {str(e)}"
                )
            except ConnectionError as e:  # Handles possible connection issues
                self.fail(
                    f"Connection error while accessing collection '{collection_name}' with ID '{collection_id}': {str(e)}"
                )
            except TimeoutError as e:  # Handles possible timeout issues
                self.fail(
                    f"Timeout occurred while accessing collection '{collection_name}' with ID '{collection_id}': {str(e)}"
                )


class TestGetPointData(unittest.TestCase):
    """Test the fetching of point data from Google Earth Engine."""

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
        """Await connection to Google Earth Engine before each test to not overload the server."""

        time.sleep(PAUSE["short"])

    @contextmanager
    def _handle_specific_exceptions(self, action_description):
        """Handle specific exceptions that may occur during the test."""

        try:
            yield
        except ee.EEException as e:
            self.fail(f"Earth Engine error when {action_description}: {str(e)}")
        except (ConnectionError, TimeoutError) as e:
            self.fail(f"Network error when {action_description}: {str(e)}")
        except Exception as e:
            self.fail(f"Unexpected error when {action_description}: {str(e)}")

    def test_get_rootzone_soil_moisture_point(self):
        """Test that the rootzone soil moisture data is fetched successfully."""

        coords = self.coords
        period = self.soil_moisture_period

        with self._handle_specific_exceptions("fetching rootzone soil moisture data"):
            soil_moisture_value = get_rootzone_soil_moisture_point(*coords, *period)
            self.assertIsNotNone(soil_moisture_value)
            self.assertIsInstance(soil_moisture_value, (float, int))

    def test_get_precipitation_point(self):
        """Test that the precipitation data is fetched successfully."""

        coords = self.coords
        period = self.precipitation_period

        with self._handle_specific_exceptions("fetching precipitation data"):
            precipitation_value = get_precipitation_point(*coords, *period)
            self.assertIsNotNone(precipitation_value)
            self.assertIsInstance(precipitation_value, (float, int))

    def test_get_soil_organic_carbon_point(self):
        """Test that the soil organic carbon data is fetched successfully."""

        coords = self.coords

        with self._handle_specific_exceptions("fetching soil organic carbon data"):
            soil_organic_carbon_value = get_soil_organic_carbon_point(*coords)
            self.assertIsNotNone(soil_organic_carbon_value)
            self.assertIsInstance(soil_organic_carbon_value, (float, int))

    def test_get_elevation_point(self):
        """Test that the elevation data is fetched successfully."""

        coords = self.coords

        with self._handle_specific_exceptions("fetching elevation data"):
            elevation_value = get_elevation_point(*coords)
            self.assertIsNotNone(elevation_value)
            self.assertIsInstance(elevation_value, (float, int))

    def test_get_slope_point(self):
        """Test that the slope data is fetched successfully."""

        coords = self.coords

        with self._handle_specific_exceptions("fetching slope data"):
            slope_value = get_slope_point(*coords)
            self.assertIsNotNone(slope_value)
            self.assertIsInstance(slope_value, (float, int))

    def test_get_world_cover_point(self):
        """Test that the world cover data is fetched successfully."""

        coords = self.coords

        with self._handle_specific_exceptions("fetching world cover data"):
            world_cover = get_world_cover_point(*coords)
            self.assertIsNotNone(world_cover)
            self.assertIsInstance(world_cover, (str, int))

    def test_get_address_from_point(self):
        """
        Test that the address is fetched successfully from the coordinates.

        Note: The API is OpenStreetMap Nominatim:
        https://nominatim.openstreetmap.org/ui/search.html
        """

        coords = self.coords

        try:
            address = get_address_from_point(*coords)
            self.assertNotEqual(
                address, "No address found.", "No address was returned."
            )
            self.assertIsInstance(address, str, "The returned address is not a string.")

        except requests.exceptions.HTTPError as e:
            self.fail(f"HTTP error occurred while fetching address: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            self.fail(f"Connection error occurred while fetching address: {str(e)}")
        except requests.exceptions.Timeout as e:
            self.fail(f"Timeout occurred while fetching address: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request exception occurred: {str(e)}")
        except Exception as e:
            self.fail(f"An unexpected error occurred: {str(e)}")


class TestRegionData(unittest.TestCase):
    """Test the region data acquisition from Google Earth Engine."""

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
        """Await connection to Google Earth Engine before each test to not overload the server."""

        time.sleep(PAUSE["short"])

    @contextmanager
    def _handle_specific_exceptions(self, action_description):
        """Handle specific exceptions that may occur during the test."""

        try:
            yield
        except ee.EEException as e:
            self.fail(f"Earth Engine error when {action_description}: {str(e)}")
        except (ConnectionError, TimeoutError) as e:
            self.fail(f"Network error when {action_description}: {str(e)}")
        except Exception as e:
            self.fail(f"Unexpected error when {action_description}: {str(e)}")

    def test_get_rootzone_soil_moisture_region(self):
        """Test that the rootzone soil moisture data is fetched successfully for the region."""

        region = self.sahel_region
        period = self.soil_moisture_period

        with self._handle_specific_exceptions("fetching rootzone soil moisture data"):
            image = get_rootzone_soil_moisture_region(region, *period)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_precipitation_region(self):
        """Test that the precipitation data is fetched successfully for the region."""

        region = self.sahel_region
        period = self.precipitation_period

        with self._handle_specific_exceptions("fetching precipitation data"):
            image = get_precipitation_region(region, *period)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_soil_organic_carbon_region(self):
        """Test that the soil organic carbon data is fetched successfully for the region."""

        region = self.sahel_region

        with self._handle_specific_exceptions("fetching precipitation data"):
            image = get_soil_organic_carbon_region(region)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_elevation_region(self):
        """Test that the elevation data is fetched successfully for the region."""

        region = self.sahel_region

        with self._handle_specific_exceptions("fetching elevation data"):
            image = get_elevation_region(region)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_slope_region(self):
        """Test that the slope data is fetched successfully for the region."""

        region = self.sahel_region

        with self._handle_specific_exceptions("fetching precipitation data"):
            image = get_slope_region(region)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_world_cover_region(self):
        """Test that the world cover data is fetched successfully for the region."""

        region = self.sahel_region

        with self._handle_specific_exceptions("fetching precipitation data"):
            image = get_world_cover_region(region)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)

    def test_get_satellite_imagery_region(self):
        """Test that the satellite imagery data is fetched successfully for the region."""

        region = self.sahel_region

        with self._handle_specific_exceptions("fetching precipitation data"):
            image = get_satellite_imagery_region(region)
            self.assertIsNotNone(image)
            self.assertIsInstance(image, ee.image.Image)
