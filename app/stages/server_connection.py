"""
Module for establishing connection with the Google Earth Engine API.
"""

# Python
import os

# Third party
import ee


def get_environment_variables() -> tuple[str, str]:
    """
    Retrieves environment variables for authentication.

    Returns:
        Tuple containing service account email and path to the private key.

    Raises:
        ValueError: If the environment variables are not set.
    """
    path_private_key = os.getenv("YOUR_ACCESS_TOKEN")
    service_account = os.getenv("SERVICE_ACCOUNT")

    missing_vars = [
        var
        for var, value in [
            ("SERVICE_ACCOUNT", service_account),
            ("YOUR_ACCESS_TOKEN", path_private_key),
        ]
        if not value
    ]
    if missing_vars:
        raise ValueError(
            f"Required environment variables are not set or are empty: {', '.join(missing_vars)}"
        )

    return service_account, path_private_key


def initialize_earth_engine(service_account: str, private_key_path: str):
    """
    Initializes Google Earth Engine with specified credentials.

    Args:
        service_account: Google service account email.
        private_key_path: Path to the Google service account private key file.

    Raises:
        RuntimeError: If initialization fails.
    """
    try:
        credentials = ee.ServiceAccountCredentials(service_account, private_key_path)
        ee.Initialize(credentials)
    except ee.EEException as e:
        raise RuntimeError(f"Failed to initialize Google Earth Engine: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(
            f"An error occurred during Google Earth Engine initialization: {str(e)}"
        ) from e


def establish_connection():
    """Initializes Google Earth Engine with service account credentials."""

    try:
        service_account, private_key = get_environment_variables()
        initialize_earth_engine(service_account, private_key)
        return True

    except ee.EEException as e:
        raise RuntimeError(
            f"Connection validation failed with Earth Engine API error: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Connection validation failed with an unexpected error: {e}"
        ) from e
