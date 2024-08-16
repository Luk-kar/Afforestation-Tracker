"""
The module contains the tests for the connection to Google Earth Engine.
"""

# Python
import json
import os

# Third party
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Test
from tests._setup import BaseTestCase

# App:
from app.stages.server_connection import (
    get_environment_variables,
    establish_connection,
)


class TestConnectionToGoogleEarthEngine(BaseTestCase):
    """
    Test the connection to Google Earth Engine.
    """

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

        with open(private_key, "r", encoding="utf-8") as f:
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
