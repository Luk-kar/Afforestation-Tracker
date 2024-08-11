import unittest
from unittest.mock import patch


class TestAfforestation(unittest.TestCase):

    @patch("afforestation.ee.ImageCollection")
    def test_data_acquisition(self, mock_image_collection):
        # Mock the return value to simulate data acquisition
        mock_image_collection.return_value = "Mocked Data"
        data = afforestation.acquire_data("COPERNICUS/S2", "2021-01-01", "2021-12-31")
        self.assertEqual(data, "Mocked Data")
