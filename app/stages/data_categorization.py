"""
This module contains the logic to evaluate environmental criteria 
to determine suitability for afforestation.
"""

# Python
from typing import Union

# Third party
import ee

# Local
from stages.data_acquisition.gee_server import world_cover_esa_codes


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

    conditions: dict[str, Union[int, float, dict[str, int]]] = {
        "slope": 15,
        "precipitation": 200,
        "moisture": 0.2,
        "vegetation_mask": {
            "grassland": world_cover_esa_codes["Grassland"],
            "barren_land": world_cover_esa_codes["Bare / Sparse Vegetation"],
        },
    }

    is_google_earth_engine_types: bool = (
        isinstance(slope, ee.Image)
        and isinstance(precipitation, ee.Image)
        and isinstance(soil_moisture, ee.Image)
        and isinstance(world_cover, ee.Image)
    )

    is_primitive_values_types: bool = (
        (isinstance(slope, (int, float)) or slope is None)
        and isinstance(precipitation, (int, float))
        and isinstance(soil_moisture, (int, float))
        and isinstance(world_cover, int)
    )

    if is_google_earth_engine_types:
        # Earth Engine image logic
        suitable_slope: ee.Image = slope.lt(conditions["slope"])
        suitable_precipitation: ee.Image = precipitation.gte(
            conditions["precipitation"]
        )
        suitable_soil_moisture: ee.Image = soil_moisture.gte(conditions["moisture"])
        vegetation_mask: ee.Image = world_cover.eq(
            conditions["vegetation_mask"]["grassland"]
        ).Or(world_cover.eq(conditions["vegetation_mask"]["barren_land"]))

        return (
            suitable_slope.And(suitable_precipitation)
            .And(suitable_soil_moisture)
            .And(vegetation_mask)
        )

    elif is_primitive_values_types:
        # Scalar logic: Validate local, pre-fetched data
        # to determine afforestation suitability without additional queries

        valid_slope: bool = slope <= conditions["slope"]
        hydration_criteria: bool = (soil_moisture >= conditions["moisture"]) or (
            precipitation >= conditions["precipitation"]
        )
        valid_cover: bool = world_cover in [
            conditions["vegetation_mask"]["grassland"],
            conditions["vegetation_mask"]["barren_land"],
        ]

        return valid_slope and hydration_criteria and valid_cover

    else:
        raise TypeError(
            "Invalid input types for afforestation data evaluation:\n"
            f"slope: {slope} {isinstance(slope, (int, float))} \n"
            f"precipitation: {precipitation} {isinstance(precipitation, (int, float))}\n"
            f"soil_moisture: {soil_moisture} {isinstance(soil_moisture, (int, float))}\n"
            f"world_covers: {world_cover} {isinstance(world_cover, int)}\n"
        )
