import geemap.foliumap as geemap
import streamlit as st

# Initialize the Earth Engine module
from stages.connection import establish_connection
from stages.data_acquisition import (
    get_rootzone_soil_moisture,
    get_precipitation_data,
    get_elevation,
    get_slope,
    get_soil_organic_carbon,
    get_world_cover,
    get_afforestation_candidates,
)

establish_connection()

roi_coords = [
    [-17.5, 15.0],
    [-17.5, 20.0],
    [39.0, 20.0],
    [43.0, 10.5],
    [35.0, 8.0],
    [25.0, 10.0],
    [15.0, 8.0],
    [-5.0, 12.0],
    [-10.0, 13.0],
]

roi = {
    "roi_coords": roi_coords,
    "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
    "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
}

map_data = {
    "elevation": {
        "data": get_elevation(roi["roi_coords"]),
        "vis_params": {
            "min": 0,
            "max": 3000,
            "palette": ["0000FF", "00FFFF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Elevation",
        "legend": {
            "title": "Elevation (m)",
            "legend_dict": {
                "0-600 m": "0000FF",
                "600-1200 m": "00FFFF",
                "1200-1800 m": "00FF00",
                "1800-2400 m": "FFFF00",
                "2400-3000 m": "FF0000",
            },
        },
    },
    "slope": {
        "data": get_slope(roi["roi_coords"]),
        "vis_params": {
            "min": 0,
            "max": 60,
            "palette": ["00FFFF", "0000FF", "00FF00", "FFFF00", "FF0000"],
        },
        "name": "Slope",
        "legend": {
            "title": "Slope (degrees)",
            "legend_dict": {
                "0-12°": "0000FF",
                "12-24°": "00FFFF",
                "24-36°": "00FF00",
                "36-48°": "FFFF00",
                "48-60°": "FF0000",
            },
        },
    },
    "world_cover": {
        "data": get_world_cover(roi["roi_coords"]),
        "vis_params": {
            "bands": ["Map"],
            "min": 10,
            "max": 100,
            "palette": [
                "006400",
                "FFBB22",
                "FFFF4C",
                "F096FF",
                "FA0000",
                "B4B4B4",
                "F0F0F0",
                "0064C8",
                "0096A0",
                "00CF75",
                "FAE6A0",
            ],
        },
        "name": "World Cover",
        "legend": {
            "title": "World Cover",
            "legend_dict": {
                "Tree Cover": "006400",
                "Shrubland": "FFBB22",
                "Grassland": "FFFF4C",
                "Cropland": "F096FF",
                "Built-up": "FA0000",
                "Bare / Sparse Vegetation": "B4B4B4",
                "Snow and Ice": "F0F0F0",
                "Permanent Water Bodies": "0064C8",
                "Herbaceous Wetland": "0096A0",
                "Mangroves": "00CF75",
                "Moss and Lichen": "FAE6A0",
            },
        },
    },
    "soc_0_20cm": {
        "data": get_soil_organic_carbon(roi["roi_coords"]),
        "vis_params": {
            "min": 0,
            "max": 200,
            "palette": ["FFFFFF", "C0C0C0", "808080", "404040", "000000"],
        },
        "name": "Soil Organic Carbon 0-20cm",
        "legend": {
            "title": "Soil Organic Carbon (0-20 cm) g/kg",
            "legend_dict": {
                "0-40 g/kg": "FFFFFF",
                "40-80 g/kg": "C0C0C0",
                "80-120 g/kg": "808080",
                "120-160 g/kg": "404040",
                "160-200 g/kg": "000000",
            },
        },
    },
    "soil_moisture": {
        "data": get_rootzone_soil_moisture(
            roi["roi_coords"],
            roi["soil_moisture"]["start_date"],
            roi["soil_moisture"]["end_date"],
        ),
        "vis_params": {
            "min": 0.0,
            "max": 0.5,
            "palette": ["red", "yellow", "green", "blue"],
        },
        "name": "Root Zone Moisture %",
        "legend": {
            "title": "Root Zone Moisture %",
            "legend_dict": {
                "0.0-0.125": "FF0000",  # Red
                "0.125-0.25": "FFFF00",  # Yellow
                "0.25-0.375": "008000",  # Green
                "0.375-0.5": "0000FF",  # Blue
            },
        },
    },
    "precipitation": {
        "data": get_precipitation_data(
            roi["roi_coords"],
            roi["precipitation"]["start_date"],
            roi["precipitation"]["end_date"],
        ),
        "vis_params": {
            "min": 0,
            "max": 2000,
            "palette": [
                "FFFFFF",
                "C0C0C0",
                "808080",
                "404040",
                "000000",
                "0000FF",
                "00FFFF",
                "00FF00",
                "FFFF00",
                "FF0000",
            ],
        },
        "name": "Precipitation",
        "legend": {
            "title": "Precipitation",
            "legend_dict": {
                "0-200 mm": "FFFFFF",
                "200-400 mm": "C0C0C0",
                "400-600 mm": "808080",
                "600-800 mm": "404040",
                "800-1000 mm": "000000",
                "1000-1200 mm": "0000FF",
                "1200-1400 mm": "00FFFF",
                "1400-1600 mm": "00FF00",
                "1600-1800 mm": "FFFF00",
                "1800-2000 mm": "FF0000",
            },
        },
    },
    "afforestation_candidates": {
        "data": get_afforestation_candidates(
            roi["roi_coords"],
            roi["precipitation"]["start_date"],
            roi["precipitation"]["end_date"],
        ),
        "vis_params": {
            "min": 0,
            "max": 1,
            "palette": ["red", "green"],
        },
        "name": "Planting Zones",
        "legend": {
            "title": "Planting Zones",
            "legend_dict": {
                "Not Suitable": "FF0000",
                "Suitable": "00FF00",
            },
        },
    },
}


def add_layer_to_map(Map, layer):
    data = layer["data"]
    vis_params = layer["vis_params"]
    name = layer["name"]
    legend = layer.get("legend", None)

    Map.addLayer(data, vis_params, name)


def calculalte_center(roi_coords):

    # Calculate the centroid of the roi_coords to use as the center for the map
    lats = [coord[1] for coord in roi_coords]  # Extract all latitudes
    lngs = [coord[0] for coord in roi_coords]  # Extract all longitudes

    # Calculate the average of latitudes and longitudes
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    center = (center_lat, center_lng)

    return center


def generate_legend_html(map_data):
    """Generate HTML content for displaying legends based on map data."""
    # Enhanced layout: Include a bottom margin for each legend block
    html_content = "<div style='margin-top: 20px; display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: start;'>"
    for key, info in reversed(list(map_data.items())):
        # Adding 'margin-bottom: 10px;' to each legend block to create space between rows
        html_content += f"<div style='margin-right: 20px; margin-bottom: 30px;'><b>{info['legend']['title']}</b><br/>"
        legend = info.get("legend", {})
        if legend:
            for label, color in legend["legend_dict"].items():
                html_content += f"<div style='display: flex; align-items: center; margin-top: 5px;'><div style='width: 20px; height: 20px; background-color: #{color}; border: 1px solid grey;'></div><span style='margin-left: 5px;'>{label}</span></div>"
        html_content += "</div>"
    html_content += "</div>"
    return html_content


def display_map(map_data, roi_coords):

    center = calculalte_center(roi_coords)

    # Create the map centered at the calculated centroid
    Map = geemap.Map(center=center, zoom=3.0)

    # Add layers to the map
    for layer in map_data.values():
        add_layer_to_map(Map, layer)

    # Display the map in Streamlit
    Map.to_streamlit()

    legends_html = generate_legend_html(map_data)
    st.markdown(legends_html, unsafe_allow_html=True)


display_map(map_data, roi_coords)
