# Python
import ee
import unittest
import os
import json
from typing import List, Literal, Dict, TypedDict, Tuple
import sys
import time
import random
import subprocess
import re

# Third party
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

# To avoid overloading the server
SERVER_PAUSE = random.uniform(0.5, 1.0)


def setup_import_paths():
    """Adjusts sys.path to include the 'app' directory for imports."""

    # Calculate the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # The 'app' directory is at the same level as the 'test' directory
    app_dir = os.path.join(current_dir, "..", "app")

    print(f"Adding '{app_dir}' to sys.path for imports")
    # Add the 'app' directory to make possible imports within the app directory
    sys.path.append(os.path.abspath(app_dir))


# Set up root for the app
setup_import_paths()

# Local
from app.stages.server_connection import (
    get_environment_variables,
    establish_connection,
)
from app.config import GEE_MAP_COLLECTIONS, ROI
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
    get_afforestation_candidates_region,
)
from app.stages.data_acquisition.region import calculate_center
from app.stages.data_categorization import (
    evaluate_afforestation_candidates,
)
from app.stages.data_acquisition.gee_server import WORLD_COVER_ESA_CODES
from app.stages.visualization import generate_legend_html
from app.config import MAP_DATA


def check_internet_connection():
    try:
        import requests

        # Change if google is blocked in your country
        requests.get("https://www.google.com")
    except requests.ConnectionError:
        print("No internet connection available. Aborting tests.")
        sys.exit()


check_internet_connection()


class TestConnectionToGoogleEarthEngine(unittest.TestCase):

    service_account: str
    private_key: str

    @classmethod
    def setUpClass(cls):
        """Sets up test environment and initial conditions before each test."""

        print("\nTesting connection to Google Earth Engine:")
        cls.service_account, cls.private_key = get_environment_variables()

    def test_get_environment_variables_success(self):
        """Test that the environment variables are retrieved successfully."""

        service_account, private_key = self.service_account, self.private_key

        self.assertIsNotNone(service_account)
        self.assertIsNotNone(private_key)

        self.assertIsInstance(service_account, str)
        self.assertIsInstance(private_key, str)

        self.assertNotEqual(service_account, "")
        self.assertNotEqual(private_key, "")

        self.assertTrue(service_account.endswith(".iam.gserviceaccount.com"))

        self.assertTrue(os.path.exists(private_key))
        self.assertTrue(private_key.endswith(".json"))

        with open(private_key, "r") as f:
            private_key_content = f.read()

        private_key_json = json.loads(private_key_content)

        self.assertIn("client_email", private_key_json)
        self.assertIn("private_key", private_key_json)

        # Validate the structure of the private key
        private_key_pem = private_key_json["private_key"]
        self.assertTrue(self._is_valid_rsa_private_key(private_key_pem))

    def test_establish_connection_success(self):
        """Test that the connection to Google Earth Engine is established successfully."""

        try:
            establish_connection()
        except RuntimeError as e:
            self.fail(
                f"Failed to establish connection to Google Earth Engine: {str(e)}"
            )

    def _is_valid_rsa_private_key(self, private_key_pem: str) -> bool:
        """
        Validates the structure of the RSA private key.
        Args:
            private_key_pem (str): The RSA private key in PEM format.
        Returns:
            bool: True if the key is valid, False otherwise.
        """
        try:
            # Load the private key to ensure it is well-formed
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(), password=None, backend=default_backend()
            )
            return True
        except ValueError:
            return False


class TestMapDataCollections(unittest.TestCase):

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


class Period(TypedDict):
    start_date: str
    end_date: str


PeriodsDict = Dict[Literal["soil_moisture", "precipitation"], Period]


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

        time.sleep(SERVER_PAUSE)

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

        time.sleep(SERVER_PAUSE)

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


class TestCandidateForAfforestation(unittest.TestCase):

    sahel_region: List[str] = ROI["roi_coords"]

    periods: PeriodsDict = ROI["periods"]
    soil_moisture_period: Period = periods["soil_moisture"].values()
    precipitation_period: Period = periods["precipitation"].values()

    # The same like within the app
    CONDITIONS = {
        "slope": 15,
        "precipitation": 200,
        "moisture": 0.2,
        "vegetation_mask": {
            "grassland": WORLD_COVER_ESA_CODES["Grassland"],
            "barren_land": WORLD_COVER_ESA_CODES["Bare / Sparse Vegetation"],
        },
    }

    data = {
        "true": {
            "slope": CONDITIONS["slope"],
            "precipitation": CONDITIONS["precipitation"],
            "soil_moisture": CONDITIONS["moisture"],
            "world_cover": WORLD_COVER_ESA_CODES["Grassland"],
        },
        "false": {
            "slope": CONDITIONS["slope"] - 1,
            "precipitation": CONDITIONS["precipitation"] - 1,
            "soil_moisture": CONDITIONS["moisture"] - 0.1,
            "world_cover": WORLD_COVER_ESA_CODES["Tree Cover"],
        },
        "invalid": {
            "slope": None,
            "precipitation": None,
            "soil_moisture": None,
            "world_cover": 404,
        },
    }

    @classmethod
    def setUpClass(cls):
        """Establish connection to Google Earth Engine before each test."""

        print("\nTesting evaluating afforestation candidates for the point and region:")

    def setUp(self):
        """Await the connection to Google Earth Engine before each test to not overload the server."""

        time.sleep(SERVER_PAUSE)

    def test_evaluate_afforestation_candidates(self):
        """Test that the afforestation candidates are evaluated successfully for the region."""

        data = self.data

        try:
            result = evaluate_afforestation_candidates(**data["true"])
            self.assertTrue(result)

        except Exception as e:
            self.fail(f"Failed to evaluate afforestation candidates: {str(e)}")

    def test_evaluate_afforestation_candidates_false(self):
        """Test that the afforestation candidates are evaluated successfully for the region."""

        data = self.data

        try:
            result = evaluate_afforestation_candidates(**data["false"])
            self.assertFalse(result)

        except Exception as e:
            self.fail(f"Failed to evaluate afforestation candidates: {str(e)}")

    def test_get_afforestation_candidates_region(self):
        """Test that the afforestation candidates are fetched successfully for the region."""

        region = self.sahel_region
        periods = ROI["periods"]
        establish_connection()

        try:
            get_afforestation_candidates_region(region, periods)
        except Exception as e:
            self.fail(
                f"Failed to fetch afforestation candidates for the region: {str(e)}"
            )


COORDS_INPUT_XPATH = (
    "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput']"
)


# Test UI components
class TestUIComponents(unittest.TestCase):

    selectors = {
        "title": "//div[contains(@class, 'stMarkdown') and contains(., 'Afforestation Tracker 🗺️🌴')]",
        "subtitle": "//div[contains(@class, 'stMarkdown') and contains(., 'Click on the map to view data for a specific point 👆')]",
        "map": "//iframe[contains(@src, 'streamlit_folium') and @title='streamlit_folium.st_folium']",
        "coords_input_panel": {
            "latitude": f"{COORDS_INPUT_XPATH}[contains(., 'Latitude')]",
            "longitude": f"{COORDS_INPUT_XPATH}[contains(., 'Longitude')]",
        },
        "map_legend": generate_legend_html(MAP_DATA),
    }

    @classmethod
    def setUpClass(cls):

        print("\nTesting the Streamlit app UI components:")

        # Start the Streamlit app
        app_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "streamlit_app.py"
        )
        port = "8501"
        cls.streamlit_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                app_path,
                "--server.headless",
                "true",
                "--server.port",
                port,
            ]
        )

        # Allow some time for the app to start
        print("Waiting for the Streamlit app to start...")
        wait_server = 3
        print(wait_server)
        for i in range(wait_server).__reversed__():
            time.sleep(1)
            print(i)
        print("Starting the test")

        # Set up the Selenium WebDriver (assuming you have Chrome installed)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        cls.driver = webdriver.Chrome(options=options)

        cls.driver.get(f"http://localhost:{port}")

        # wait until "map" is loaded
        time.sleep(30)

        cls.driver.refresh()

        time.sleep(45)

        print("Page refreshed")

    @classmethod
    def tearDownClass(cls):
        # Close the browser and terminate the Streamlit app process
        cls.driver.quit()
        cls.streamlit_process.terminate()

    def await_element(self, element: str, timeout=10) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, element))
        )

    def test_title_exists(self):
        """Test if the title element exists."""

        title = self.selectors["title"]

        try:
            self.assertTrue(self.driver.find_element(By.XPATH, title))
        except NoSuchElementException:
            self.fail("Title element does not exist.")

    def test_subtitles_exists(self):
        """Test if the subtitle element exists."""

        subtitle = self.selectors["subtitle"]

        try:
            self.assertTrue(self.driver.find_element(By.XPATH, subtitle))
        except NoSuchElementException:
            self.fail("Subtitle element does not exist.")

    def test_map_exists(self):
        """Test if the map element exists."""

        _map = self.selectors["map"]

        try:
            self.assertTrue(self.await_element(_map))
        except NoSuchElementException:
            self.fail("Map element does not exist.")

    def test_map_point_info_exists(self):
        """Test if the map point information is displayed."""

        page_content = self.driver.page_source

        missing_details = self._find_missing_map_point_details(page_content)

        self.assertEqual(
            missing_details, {}, f"Map point information is missing:\n{missing_details}"
        )

    def _find_missing_map_point_details(self, output_text: str):
        """Find missing map point details from the output text."""

        # Regex patterns to extract information
        extracted_data = self._extract_map_point_details(output_text)

        # Find missing data
        missing_data = {}

        for key, data in extracted_data.items():
            if data is None:
                missing_data[key] = data

        return missing_data

    def _extract_map_point_details(self, output_text: str) -> Dict[str, str]:
        """Extracts the map point details from the output text."""

        # Regex patterns to extract information
        patterns = {
            "latitude": r"Latitude: ([\d.]+)",
            "longitude": r"Longitude: ([\d.]+)",
            "address": r"Address: (.+)",
            "afforestation_candidate": r"Afforestation Candidate: .*(Yes|No)",
            "elevation": r"Elevation: ([\d.]+) meters",
            "slope": r"Slope: ([\d.]+)°",
            "soil_moisture": r"Rainy Season Root Zone Soil Moisture: ([\d.]+) %",
            "yearly_precipitation": r"Yearly Precipitation: ([\d.]+) mm",
            "soil_organic_carbon": r"Soil Organic Carbon: ([\d.]+) g/kg",
            "world_cover": r"World Cover: <strong>(.+)</strong>",
        }

        # Extract data from the output text
        extracted_data = {}

        for key, pattern in patterns.items():
            match = re.search(pattern, output_text, re.MULTILINE)
            if match:
                extracted_data[key] = match.group(1)
            else:
                extracted_data[key] = (
                    None  # or 'Not found', based on your error handling preference
                )

        return extracted_data

    def test_coords_input_pane_exists(self):
        """Test if the coordinate input panel is displayed."""

        coords_input_panel = self.selectors["coords_input_panel"]

        try:
            self.assertTrue(self.await_element(coords_input_panel["latitude"], 15))
            self.assertTrue(self.await_element(coords_input_panel["longitude"], 15))

        except NoSuchElementException:
            self.fail("Coordinate input panel does not exist.")

    def test_map_legend_exists(self):
        """Test if the map legend is displayed."""

        map_legend = self.selectors["map_legend"]

        page_content = self.driver.page_source

        try:
            self.assertTrue(map_legend in page_content)

        except NoSuchElementException:

            self.fail("Map legend does not exist.")


if __name__ == "__main__":
    unittest.main()
