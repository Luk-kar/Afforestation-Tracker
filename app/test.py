import streamlit as st
import folium
from streamlit_folium import st_folium
import geocoder
from stages.server_connection import establish_connection

# Establish a server connection
establish_connection()


def get_current_location():
    g = geocoder.ip("me")
    return g.latlng


def set_lat_lon():
    default_latlng = get_current_location()
    return default_latlng[0], default_latlng[1]


def update_coords_on_click_map(map_data):
    if map_data and map_data["last_clicked"]:
        last_click_lat, last_click_lng = (
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"],
        )
        st.session_state.latitude = last_click_lat
        st.session_state.longitude = last_click_lng


def update_coords_on_click_btn():
    st.session_state.latitude, st.session_state.longitude = set_lat_lon()


if "latitude" not in st.session_state or "longitude" not in st.session_state:
    st.session_state.latitude, st.session_state.longitude = set_lat_lon()


st.title("Geo-localization Position Display")

map = folium.Map(zoom_start=6)
folium.Marker(
    [st.session_state.latitude, st.session_state.longitude], popup="You are here!"
).add_to(map)
folium.LatLngPopup().add_to(map)


map_data = st_folium(map, width=725, height=500)
update_coords_on_click_map(map_data)

col1, col2 = st.columns(2)  # Create two columns

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


st.button("Use My Current Location", on_click=update_coords_on_click_btn)
