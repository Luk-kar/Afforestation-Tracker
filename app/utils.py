"""
Small, various utility functions used throughout the program
"""


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
