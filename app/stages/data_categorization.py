"""
This module contains the logic to evaluate environmental criteria 
to determine suitability for afforestation.
"""

# Python
from typing import Union

# Third party
import ee

# Local
from stages.data_acquisition.gee_server import WORLD_COVER_ESA_CODES


def evaluate_afforestation_candidates(
    slope: Union[ee.Image, int, float],
    precipitation: Union[ee.Image, int, float],
    soil_moisture: Union[ee.Image, int, float],
    world_cover: Union[str, ee.Image],
) -> Union[bool, ee.Image]:
    """
    Evaluates environmental criteria to determine suitability for
    afforestation using either Earth Engine objects or scalar values.

    Returns:
    bool or ee.Image: Is the area suitable for afforestation.
    """
    # Centralized handling of conditions to uniformly assess
    # suitability across both point and regional data

    # NOTE:
    # DO NOT MOVE THIS CONSTANT OUTSIDE TO THE GLOBAL SCOPE!!!
    # For unknown reasons, the app fails render UI elements silently
    # when the constant is defined outside the function scope.
    CONDITIONS = {
        "slope": 15,
        "precipitation": 200,
        "moisture": 0.2,
        "vegetation_mask": {
            "grassland": WORLD_COVER_ESA_CODES["Grassland"],
            "barren_land": WORLD_COVER_ESA_CODES["Bare / Sparse Vegetation"],
        },
    }

    try:
        if (
            isinstance(world_cover, int)
            and world_cover not in WORLD_COVER_ESA_CODES.values()
        ):

            raise ValueError(
                "Provided world_cover code is not valid."
                + f"world_cover: {world_cover}, {type(world_cover)}"
            )

        if all(
            isinstance(item, ee.Image)
            for item in [slope, precipitation, soil_moisture, world_cover]
        ):

            return evaluate_with_ee_images(
                slope, precipitation, soil_moisture, world_cover, CONDITIONS
            )

        elif all(
            isinstance(item, (int, float)) or item is None
            for item in [slope, precipitation, soil_moisture]
        ) and isinstance(world_cover, int):

            return evaluate_with_scalars(
                slope, precipitation, soil_moisture, world_cover, CONDITIONS
            )

        else:
            raise TypeError(
                "Input types must either all be Earth Engine Images or all be scalar values."
                + f"world_cover: {world_cover} {type(world_cover)},"
                + f"slope: {slope} {type(slope)},"
                + f"precipitation: {precipitation} {type(precipitation)},"
                + f"soil_moisture: {soil_moisture} {type(soil_moisture)}"
            )

    except ee.EEException as e:
        raise RuntimeError(f"Failed to process Earth Engine data: {e}") from e
    except Exception as e:
        raise RuntimeError(f"An error occurred during evaluation: {e}") from e


def evaluate_with_ee_images(
    slope: ee.Image,
    precipitation: ee.Image,
    soil_moisture: ee.Image,
    world_cover: ee.Image,
    conditions: dict,
) -> ee.Image:
    """
    Evaluate the suitability of an area for afforestation using Earth Engine images.

    Returns: ee.Image: A mask image indicating the suitability of the area.
    """
    suitable_slope = slope.lt(conditions["slope"])
    suitable_precipitation = precipitation.gte(conditions["precipitation"])
    suitable_soil_moisture = soil_moisture.gte(conditions["moisture"])
    vegetation_mask = world_cover.eq(conditions["vegetation_mask"]["grassland"]).Or(
        world_cover.eq(conditions["vegetation_mask"]["barren_land"])
    )
    return (
        suitable_slope.And(suitable_precipitation)
        .And(suitable_soil_moisture)
        .And(vegetation_mask)
    )


def evaluate_with_scalars(
    slope: Union[int, float],
    precipitation: Union[int, float],
    soil_moisture: Union[int, float],
    world_cover: int,
    conditions: dict,
) -> bool:
    """
    Evaluate the suitability of an area for afforestation using scalar values.

    Returns: bool: Is the area suitable for afforestation.
    """

    valid_slope = slope <= conditions["slope"]
    hydration_criteria = (soil_moisture >= conditions["moisture"]) or (
        precipitation >= conditions["precipitation"]
    )
    valid_cover = world_cover in conditions["vegetation_mask"].values()
    return valid_slope and hydration_criteria and valid_cover
