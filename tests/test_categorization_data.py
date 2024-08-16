"""
This module contains test cases for evaluating 
and fetching afforestation candidates for a specific region.
"""

# Python
from contextlib import contextmanager
import time
from typing import List

# Test
from tests._types import PeriodsDict, Period
from tests._server import PAUSE
from tests._setup import BaseTestCase

# App
from app.stages.server_connection import (
    establish_connection,
)
from app.config import ROI
from app.stages.data_acquisition.region import get_afforestation_candidates_region
from app.stages.data_categorization import evaluate_afforestation_candidates
from app.stages.data_acquisition.gee_server import WORLD_COVER_ESA_CODES

# Third-party
import ee


class TestCandidateForAfforestation(BaseTestCase):
    """
    Test cases for evaluating and fetching afforestation candidates
    for a specific region or point
    """

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
        """
        Await the connection to Google Earth Engine
        before each test to not overload the server.
        """

        time.sleep(PAUSE["short"])

    @contextmanager
    def _handle_specific_exceptions(self, action_description):
        try:
            yield
        except ee.EEException as e:
            self.fail(f"Earth Engine error while {action_description}: {str(e)}")
        except ValueError as e:
            self.fail(f"Value error in test data or inputs: {str(e)}")
        except TypeError as e:
            self.fail(f"Type error in inputs: {str(e)}")
        except RuntimeError as e:
            self.fail(f"Runtime error during {action_description}: {str(e)}")

    def test_evaluate_afforestation_candidates(self):
        """Test that the afforestation candidates are evaluated successfully for the region."""

        data = self.data

        with self._handle_specific_exceptions("evaluating afforestation candidates"):

            result = evaluate_afforestation_candidates(**data["true"])
            self.assertTrue(result)

    def test_evaluate_afforestation_candidates_false(self):
        """Test that the afforestation candidates are evaluated successfully for the region."""

        data = self.data

        with self._handle_specific_exceptions("evaluating afforestation candidates"):

            result = evaluate_afforestation_candidates(**data["false"])
            self.assertFalse(result)

    def test_get_afforestation_candidates_region(self):
        """Test that the afforestation candidates are fetched successfully for the region."""

        region = self.sahel_region
        periods = ROI["periods"]
        establish_connection()

        try:
            get_afforestation_candidates_region(region, periods)

        except ee.EEException as e:
            self.fail(f"Earth Engine error while fetching candidates: {str(e)}")
        except ValueError as e:
            self.fail(f"Invalid ROI coordinates: {str(e)}")
        except RuntimeError as e:
            self.fail(f"Runtime error during fetching candidates: {str(e)}")
