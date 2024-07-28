# Third party
import folium
import geemap.foliumap as geemap
import streamlit as st
from folium.plugins import MousePosition

# Initialize the Earth Engine module
from stages.data_acquisition.gee_server import (
    fetch_suitable_for_afforestation_data,
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
