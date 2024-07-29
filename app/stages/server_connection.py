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

    if path_private_key is None or service_account is None:
        raise ValueError(
            f"Environment variables for the service account or access token are not set.\n"
            f"YOUR_ACCESS_TOKEN: {path_private_key}\nSERVICE_ACCOUNT: {service_account}"
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
    credentials = ee.ServiceAccountCredentials(service_account, private_key_path)
    ee.Initialize(credentials)


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
