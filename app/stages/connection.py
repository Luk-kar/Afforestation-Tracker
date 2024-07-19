import ee
import os


def get_environment_variables():
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


def initialize_earth_engine(service_account, private_key):
    """
    Initializes Google Earth Engine with specified credentials.

    Args:
        service_account: Google service account email.
        private_key: Path to the Google service account private key file.

    Raises:
        RuntimeError: If initialization fails.
    """
    credentials = ee.ServiceAccountCredentials(service_account, private_key)
    ee.Initialize(credentials)


def establish_connection():
    """Initializes Google Earth Engine with service account credentials."""

    try:
        service_account, private_key = get_environment_variables()
        initialize_earth_engine(service_account, private_key)
        print("Earth Engine initialized successfully")
        return True

    except ee.EEException as e:
        raise RuntimeError(
            f"Connection validation failed with Earth Engine API error: {e}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Connection validation failed with an unexpected error: {e}"
        )
