# Third party
import folium
import geemap.foliumap as geemap
import streamlit as st
from folium.plugins import MousePosition
from streamlit_folium import st_folium

import streamlit.components.v1 as components

# Initialize the Earth Engine module
from stages.connection import establish_connection
from stages.data_acquisition.gee_server import (
    fetch_suitable_for_afforestation_data,
    world_cover_esa_codes,
)
from stages.data_acquisition.region import (
    get_rootzone_soil_moisture_region,
    get_precipitation_region,
    get_elevation_region,
    get_slope_region,
    get_soil_organic_carbon_region,
    get_world_cover_region,
    get_afforestation_candidates_region,
)
from stages.data_acquisition.point import (
    get_rootzone_soil_moisture_point,
    get_precipitation_point,
    get_soil_organic_carbon_point,
    get_elevation_point,
    get_slope_point,
    get_world_cover_point,
    get_address_from_point,
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
]  # Sahel geo-polygon

roi = {
    "roi_coords": roi_coords,
    "periods": {
        "soil_moisture": {"start_date": "2020-06-01", "end_date": "2020-10-01"},
        "precipitation": {"start_date": "2023-01-01", "end_date": "2023-12-31"},
    },
}

map_data = {
    "elevation": {
        "data": get_elevation_region(roi["roi_coords"]),
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
        "data": get_slope_region(roi["roi_coords"]),
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
        "data": get_world_cover_region(roi["roi_coords"]),
        "vis_params": {
            "bands": ["world_cover"],
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
        "data": get_soil_organic_carbon_region(roi["roi_coords"]),
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
        "data": get_rootzone_soil_moisture_region(
            roi["roi_coords"],
            roi["periods"]["soil_moisture"]["start_date"],
            roi["periods"]["soil_moisture"]["end_date"],
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
        "data": get_precipitation_region(
            roi["roi_coords"],
            roi["periods"]["precipitation"]["start_date"],
            roi["periods"]["precipitation"]["end_date"],
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
        "data": get_afforestation_candidates_region(
            roi["roi_coords"],
            roi["periods"],
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


def validate_are_keys_the_same(dict1, dict2):
    if set(dict1.keys()) != set(dict2.keys()):
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())
        error_message = "Dictionaries have mismatched keys.\n"
        if missing_in_dict1:
            error_message += f"Missing in dict1: {missing_in_dict1}\n"
        if missing_in_dict2:
            error_message += f"Missing in dict2: {missing_in_dict2}\n"
        raise ValueError(error_message)


validate_are_keys_the_same(
    world_cover_esa_codes, map_data["world_cover"]["legend"]["legend_dict"]
)


def add_layer_to_map(Map, layer):
    data = layer["data"]
    vis_params = layer["vis_params"]
    name = layer["name"]

    # Update the vis_params to set the opacity (if the API supports it directly)
    # For Google Earth Engine's folium map, you can include 'opacity' as a key in vis_params.
    updated_vis_params = vis_params.copy()  # Make a copy to avoid mutating the original
    updated_vis_params["opacity"] = 0.6  # Set opacity to 60%

    Map.addLayer(data, updated_vis_params, name)


def calculate_center(roi_coords):

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
    html_content = """
    <style>
        .scrollable-box {
            height: 315px; /* Adjust height as needed */
            overflow-x: scroll;
            overflow-y: hidden;
            white-space: nowrap;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: #f9f9f9;
            display: flex;
            align-items: flex-start;
        }
        .draggable {
            display: inline-block;
            cursor: move;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: max-content;
            margin-right: 10px;
        }
        .legend-title {
            font-weight: bold;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-top: 5px;
        }
        .legend-color-box {
            width: 20px;
            height: 20px;
            border: 1px solid grey;
            margin-right: 5px;
        }
    </style>
    <div class='scrollable-box'>
    """

    for key, info in reversed(list(map_data.items())):
        html_content += f"""
        <div class='draggable' id='{key}_legend'>
            <div class='legend-title'>{info['legend']['title']}</div>
            <div class='legend-items'>
        """
        legend = info.get("legend", {})
        if legend:
            for label, color in legend["legend_dict"].items():
                html_content += f"""
                <div class='legend-item'>
                    <div class='legend-color-box' style='background-color: #{color};'></div>
                    <span>{label}</span>
                </div>
                """
        html_content += "</div></div>"

    html_content += "</div>"

    html_content += """
    <script>
        document.querySelectorAll('.draggable').forEach(el => {
            el.addEventListener('mousedown', function(e) {
                let shiftX = e.clientX - el.getBoundingClientRect().left;
                let shiftY = e.clientY - el.getBoundingClientRect().top;

                function moveAt(pageX, pageY) {
                    el.style.left = pageX - shiftX + 'px';
                    el.style.top = pageY - shiftY + 'px';
                }

                function onMouseMove(e) {
                    moveAt(e.pageX, e.pageY);
                }

                document.addEventListener('mousemove', onMouseMove);

                el.onmouseup = function() {
                    document.removeEventListener('mousemove', onMouseMove);
                    el.onmouseup = null;
                };

                el.ondragstart = function() {
                    return false;
                };
            });
        });
    </script>
    """

    return html_content


def display_map(map_data, roi_coords):

    center = calculate_center(roi_coords)

    # Create the map centered at the calculated centroid
    Map = geemap.Map(center=center, zoom=3.0)

    Map.add_child(folium.LatLngPopup())

    for layer in map_data.values():
        add_layer_to_map(Map, layer)

    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=False,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(Map)

    folium.LayerControl().add_to(Map)

    return Map


def display_map_point_info(map_result, roi):

    # Data for point
    lat, lon = map_result["last_clicked"]["lat"], map_result["last_clicked"]["lng"]

    # Fetch data for each attribute
    elevation = get_elevation_point(lat, lon)
    slope = get_slope_point(lat, lon)
    soil_moisture = get_rootzone_soil_moisture_point(
        lat,
        lon,
        roi["periods"]["soil_moisture"]["start_date"],
        roi["periods"]["soil_moisture"]["end_date"],
    )
    precipitation = get_precipitation_point(
        lat,
        lon,
        roi["periods"]["precipitation"]["start_date"],
        roi["periods"]["precipitation"]["end_date"],
    )

    soil_organic_carbon = get_soil_organic_carbon_point(lat, lon)
    world_cover = get_world_cover_point(lat, lon)
    address = get_address_from_point(lat, lon)

    afforestation_validation = fetch_suitable_for_afforestation_data(
        slope, precipitation, soil_moisture, world_cover
    )

    # Text formatting
    lat_rounded, lon_rounded = (round(lat, 4), round(lon, 4))
    afforestation_yes_no = "Yes" if afforestation_validation else "No"
    slope_rounded = round(slope, 1)
    precipitation_rounded = round(precipitation, 2)
    soil_moisture_rounded = round(soil_moisture * 100, 2)

    # Text display
    result = f"""
    Latitude: {lat_rounded} | Longitude: {lon_rounded}\n
    Address: {address}\n
    Afforestation Candidate: **{afforestation_yes_no}**\n
    Elevation: {elevation} meters,
    Slope: {slope_rounded}°,
    Root Zone Soil Moisture: {soil_moisture_rounded} %,
    Precipitation: {precipitation_rounded} mm,
    Soil Organic Carbon: {soil_organic_carbon} g/kg,
    World Cover: {world_cover}
    """

    if afforestation_validation:
        st.success(result)
    else:
        st.error(result)  # no success


folium_map = display_map(map_data, roi_coords)

map_result = st_folium(folium_map)

# Show elevation on click
if map_result["last_clicked"]:
    display_map_point_info(map_result, roi)

legends_html = generate_legend_html(map_data)
# st.markdown(legends_html, unsafe_allow_html=True)

components.html(legends_html, height=400, scrolling=True)
