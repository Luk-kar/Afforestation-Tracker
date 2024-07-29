"""
This module contains functions to validate the input data.
"""

# Python
from datetime import datetime

# Local
from _types import Roi_Coords

# Third party
import ee


def validate_are_keys_the_same(dict1: dict, dict2: dict):
    """
    Compares the keys of two dictionaries and raises an error if they do not match.

    Raises:
    ValueError: If the keys of the two dictionaries do not match, with details of missing keys.
    """

    if set(dict1.keys()) != set(dict2.keys()):
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())
        error_message = "Dictionaries have mismatched keys.\n"
        if missing_in_dict1:
            error_message += f"Missing in dict1: {missing_in_dict1}\n"
        if missing_in_dict2:
            error_message += f"Missing in dict2: {missing_in_dict2}\n"
        raise ValueError(error_message)


def validate_many_dates(start_date: str, end_date: str) -> bool:
    """
    Validate the start and end dates to be in 'YYYY-MM-DD' format.
    """
    return not all(validate_date(date) for date in [start_date, end_date])


def validate_date(date_str: str) -> bool:
    """Validate date format to be YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_roi_coords(roi_coords: Roi_Coords) -> bool:
    """Validate the ROI coordinates to be a list of lists with two numbers each."""

    if not isinstance(roi_coords, list):
        raise ValueError("ROI coordinates should be a list of lists.")

    for i in roi_coords:
        if not isinstance(i, list) or len(i) != 2:
            raise ValueError("Each coordinate should be a list of two elements.")

        if not isinstance(i[0], (int, float)) or not isinstance(i[1], (int, float)):
            return ValueError("Each coordinate should be a list of two numbers.")
        else:
            validate_coordinates(i[0], i[1])


def validate_coordinates(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError(
            "Latitude must be between -90 and 90 and longitude between -180 and 180."
        )


def handle_ee_operations(func):
    """Decorator to handle errors from Google Earth Engine operations"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ee.EEException as e:
            raise RuntimeError(f"Earth Engine operation failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in Earth Engine operation: {str(e)}")

    return wrapper
