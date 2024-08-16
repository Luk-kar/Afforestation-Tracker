"""
This module defines the types used in the test.
"""

# Python
from typing import Dict, Literal, TypedDict


class Period(TypedDict):
    start_date: str
    end_date: str


PeriodsDict = Dict[Literal["soil_moisture", "precipitation"], Period]
