"""
The server module test the user elements interface of the app.
"""

# Python
import os
import re
import subprocess
import time
from typing import Dict

# Test
from tests._server import PAUSE
from tests._setup import BaseTestCase

# Third party
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

# App
from app.stages.visualization import generate_legend_html
from app.config import MAP_DATA


COORDS_INPUT_XPATH = (
    "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput']"
)


# Test UI components
class TestUIComponents(BaseTestCase):

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
        wait_server = PAUSE["long"]
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
