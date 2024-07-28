# Third party
from streamlit_folium import st_folium

# Local
from stages.server_connection import establish_connection
from stages.visualization import (
    display_map,
    display_map_point_info,
    display_map_legend,
)
from stages.data_acquisition.point import get_map_point_data

from config import map_data_regions, roi_coords, roi

# Initialize the Earth Engine module
establish_connection()

folium_map = display_map(map_data_regions, roi_coords)
map_result = st_folium(folium_map)

# Show on click
if map_result["last_clicked"]:

    lat, lon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]
    point_data = get_map_point_data(roi, lat, lon)
    display_map_point_info(point_data)

display_map_legend(map_data_regions)
