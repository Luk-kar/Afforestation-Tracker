# Third party
import folium
import geemap.foliumap as geemap
import streamlit as st
from folium.plugins import MousePosition
import streamlit.components.v1 as components

# Local
from stages.data_categorization import evaluate_afforestation_candidates
from stages.data_acquisition.point import (
    get_rootzone_soil_moisture_point,
    get_precipitation_point,
    get_soil_organic_carbon_point,
    get_elevation_point,
    get_slope_point,
    get_world_cover_point,
    get_address_from_point,
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


def generate_map_legend_html(map_data):
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


def display_map(data):

    maps = data["maps"]
    center = data["center"]

    # Create the map centered at the calculated centroid
    Map = geemap.Map(center=center, zoom=3.0)

    Map.add_child(folium.LatLngPopup())

    for layer in maps.values():
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


def display_map_point_info(data):

    # Text formatting
    lat_rounded, lon_rounded = (round(data["lat"], 4), round(data["lon"], 4))
    afforestation_yes_no = "Yes" if data["afforestation_validation"] else "No"
    slope_rounded = round(data["slope"], 1)
    precipitation_rounded = round(data["precipitation"], 2)
    soil_moisture_rounded = round(data["soil_moisture"] * 100, 2)

    # Text display
    result = f"""
    Latitude: {lat_rounded} | Longitude: {lon_rounded}\n
    Address: {data['address']}\n
    Afforestation Candidate: **{afforestation_yes_no}**\n
    Elevation: {data['elevation']} meters,
    Slope: {slope_rounded}°,
    Rainy Season Root Zone Soil Moisture: {soil_moisture_rounded} %,
    Yearly Precipitation: {precipitation_rounded} mm,
    Soil Organic Carbon: {data['soil_organic_carbon']} g/kg,
    World Cover: {data['world_cover']}
    """

    if data["afforestation_validation"]:
        st.success(result)
    else:
        st.error(result)


def display_map_legend(map_data):
    legends_html = generate_map_legend_html(map_data)
    components.html(legends_html, height=400, scrolling=True)
