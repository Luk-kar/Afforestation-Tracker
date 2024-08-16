"""
This module contains the setup functions for the tests.
"""

# Python
import os
import sys
import unittest

# Third-party
import requests


def check_internet_connection():
    try:
        # Change if google is blocked in your country
        requests.get("https://www.google.com")
    except requests.ConnectionError:
        print("No internet connection available. Aborting tests.")
        sys.exit()


def setup_import_paths():
    """Adjusts sys.path to include the 'app' directory for imports."""

    # Calculate the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # The 'app' directory is at the same level as the 'test' directory
    app_dir = os.path.join(current_dir, "..", "app")

    print(f"Adding '{app_dir}' to sys.path for imports")
    # Add the 'app' directory to make possible imports within the app directory
    sys.path.append(os.path.abspath(app_dir))


class BaseTestCase(unittest.TestCase):
    """Base test case for all tests."""

    @classmethod
    def setUpClass(cls):
        # Check internet connection once before any tests in this module run
        check_internet_connection()
