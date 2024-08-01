"""
This module contains functions to display the map and map point information on the Streamlit app.
"""

# Third party
import ee
import folium
from folium.plugins import MousePosition
import geemap.foliumap as geemap
import streamlit as st
import streamlit.components.v1 as components

# Local
from stages.data_acquisition.gee_server import WORLD_COVER_ESA_CODES
from stages.data_acquisition.point import get_client_location


def add_layer_to_map(gee_map: geemap.Map, layer: dict):
    """Add a layer to the map with the specified vis_params and name."""
    try:
        data: ee.Image = layer["data"]
        vis_params: dict = layer["vis_params"]
        name: str = layer["name"]

        # Validate data types
        if not isinstance(data, ee.Image):
            raise TypeError("Data must be an Earth Engine Image.")
        if not isinstance(vis_params, dict):
            raise TypeError("Visualization parameters must be a dictionary.")
        if not isinstance(name, str):
            raise TypeError("Layer name must be a string.")

        updated_vis_params = vis_params.copy()
        updated_vis_params["opacity"] = 0.6  # Set opacity to 60%
        gee_map.addLayer(data, updated_vis_params, name)
    except Exception as e:
        raise RuntimeError(f"Failed to add layer to map: {e}") from e


def generate_legend(map_legends: dict) -> str:
    """
    Generate HTML for the map legend using the provided legend data.

    Returns:
        str: HTML string for the map legend
    """
    style_section = """
    <style>
        .scrollable-legend {
            height: 315px;
            overflow-x: scroll;
            overflow-y: hidden;
            white-space: nowrap;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: #f9f9f9;
            display: flex;
            align-items: flex-start;
        }
        .legend-entry {
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
        .legend-detail {
            display: flex;
            align-items: center;
            margin-top: 5px;
        }
        .color-indicator {
            width: 20px;
            height: 20px;
            border: 1px solid grey;
            margin-right: 5px;
        }
    </style>
    """

    legend_html = "<div class='scrollable-legend'>"
    for key, info in reversed(list(map_legends.items())):
        legend_html += f"""
            <div class='legend-entry' id='{key}_legend'>
                <div class='legend-title'>{info['legend']['title']}</div>
                <div class='legend-details'>
        """
        for label, color in info.get("legend", {}).get("legend_dict", {}).items():
            legend_html += f"""
                    <div class='legend-detail'>
                        <div class='color-indicator' style='background-color: #{color};'></div>
                        <span>{label}</span>
                    </div>
            """
        legend_html += "</div></div>"

    legend_html += "</div>"

    dragging_script = """
    <script>
        document.querySelectorAll('.legend-entry').forEach(el => {
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
                el.ondragstart = function() { return false; };
            });
        });
    </script>
    """

    return style_section + legend_html + dragging_script


def display_map(data: dict) -> geemap.Map:
    """
    Display the map with the specified data layers and center.
    """

    try:
        maps = data["maps"]
        center = data["center"]

        # Create the map centered at the calculated centroid
        gee_map = geemap.Map(center=center, zoom=3.0)

        gee_map.add_child(folium.LatLngPopup())

        if "latitude" in st.session_state and "longitude" in st.session_state:
            folium.Marker(
                [st.session_state.latitude, st.session_state.longitude],
                popup="Current Location",
            ).add_to(gee_map)

        for layer in maps.values():
            add_layer_to_map(gee_map, layer)

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
        ).add_to(gee_map)

        folium.LayerControl().add_to(gee_map)

        return gee_map

    except Exception as e:
        raise RuntimeError(f"Failed to display map: {e}") from e


def display_map_point_info(data: dict):
    """
    Display the information for the clicked point on the map as a separate success or error message.
    """
    try:
        # Text formatting
        (
            lat_rounded,
            lon_rounded,
            afforestation_yes_no,
            slope_rounded,
            precipitation_rounded,
            soil_moisture_rounded,
            world_cover,
        ) = map_point_text_format(data)

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
        World Cover: {world_cover}
        """

        if data["afforestation_validation"]:
            st.success(result)
        else:
            st.error(result)

    except Exception as e:
        raise RuntimeError(f"Failed to display map point information: {e}") from e


def map_point_text_format(data: dict) -> tuple:
    """
    Format the map point information for display.

    Returns:
        Tuple containing the formatted text for the map point
    """

    lat_rounded, lon_rounded = (round(data["lat"], 4), round(data["lon"], 4))
    afforestation_yes_no = "Yes" if data["afforestation_validation"] else "No"
    slope_rounded = round(data["slope"], 1)
    precipitation_rounded = round(data["precipitation"], 2)
    soil_moisture_rounded = round(data["soil_moisture"] * 100, 2)

    world_cover_code = data["world_cover"]
    world_cover = next(
        (
            name
            for name, code in WORLD_COVER_ESA_CODES.items()
            if code == world_cover_code
        ),
        "Unknown cover",
    )

    return (
        lat_rounded,
        lon_rounded,
        afforestation_yes_no,
        slope_rounded,
        precipitation_rounded,
        soil_moisture_rounded,
        world_cover,
    )


def display_coordinate_input_panel():
    """Display the coordinate input panel."""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.number_input(
            "Latitude",
            value=st.session_state.latitude,
            key="latitude",
            step=0.5,
            format="%.4f",
        )

    with col2:
        st.number_input(
            "Longitude",
            value=st.session_state.longitude,
            key="longitude",
            step=0.5,
            format="%.4f",
        )

    with col3:
        st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
        st.button(
            "Use My Current Location", on_click=update_coords_with_client_localization
        )


def update_coords_with_client_localization():
    st.session_state.latitude, st.session_state.longitude = get_client_location()


def display_map_legend(map_data: dict):
    """
    Display the map legend for the specified map data.
    """
    legends_html = generate_legend(map_data)
    components.html(legends_html, height=400, scrolling=True)


def display_text(text: str):
    st.markdown(
        f"<p style='text-align: center;'>{text}</p>",
        unsafe_allow_html=True,
    )


def display_title(text: str):
    st.markdown(
        f"<h1 style='text-align: center;'>{text}</h1>",
        unsafe_allow_html=True,
    )


def report_error(message: str, exception: RuntimeError):
    """Report an error and stop the app."""
    st.error(f"{message}: {exception}")
    st.stop()
