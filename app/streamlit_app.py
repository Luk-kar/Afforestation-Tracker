# Third party
from streamlit_folium import st_folium

# Local
from stages.server_connection import establish_connection
from stages.visualization import (
    display_map,
    display_map_point_info,
    display_map_legend,
)
from config import map_data_regions, roi_coords, roi

# Initialize the Earth Engine module
establish_connection()

folium_map = display_map(map_data_regions, roi_coords)

map_result = st_folium(folium_map)

# Show elevation on click
if map_result["last_clicked"]:
    display_map_point_info(map_result, roi)

display_map_legend(map_data_regions)
