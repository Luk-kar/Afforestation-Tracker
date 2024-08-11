"""This module contains the error logging configuration for the Streamlit app."""

# Python
import logging
import os


def set_logging_level():
    """Set the logging level for the Streamlit app."""

    logs_dir_path = "logs"
    if not os.path.exists(logs_dir_path):
        os.makedirs(logs_dir_path)

    errors_path = os.path.join("logs", "errors.log")
    logging.basicConfig(
        level=logging.ERROR,
        filename=errors_path,
        filemode="a",
        format="%(asctime)s - %(message)s",
    )
