"""
The server module provides functionality for managing server operations and configurations.
"""

# Python
import random

# To avoid overloading the server
PAUSE = {
    "short": random.uniform(0.5, 1.0),
    "long": 3,
}
