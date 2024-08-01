import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import geocoder
from stages.server_connection import establish_connection

# Establish server connection
establish_connection()


# Function to get the current geo-localization position
def get_current_location():
    g = geocoder.ip("me")
    return g.latlng


def set_lat_lon(get_current_location):

    default_latlng = get_current_location()
    st.session_state.latitude = default_latlng[0]
    st.session_state.longitude = default_latlng[1]


def update_coords_on_click(map_data):

    last_click_lat, last_click_lng = (
        map_data["last_clicked"]["lat"],
        map_data["last_clicked"]["lng"],
    )
    st.session_state.latitude = last_click_lat
    st.session_state.longitude = last_click_lng


if "latitude" not in st.session_state or "longitude" not in st.session_state:
    set_lat_lon(get_current_location)

st.title("Geo-localization Position Display")

map = folium.Map(
    location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12
)

folium.Marker(
    [st.session_state.latitude, st.session_state.longitude], popup="Specified Location"
).add_to(map)

folium.LatLngPopup().add_to(map)

map_data = st_folium(map, width=725, height=500)


if map_data["last_clicked"]:
    update_coords_on_click(map_data)

latitude = st.number_input("Latitude", value=st.session_state.latitude)
longitude = st.number_input("Longitude", value=st.session_state.longitude)

# Button to update the latitude and longitude to current location
if st.button("Use My Current Location"):
    latlng = get_current_location()
    st.session_state.latitude = latlng[0]
    st.session_state.longitude = latlng[1]

# This button is used to refresh the map based on input coordinates
if st.button("Update Map"):
    st.session_state.update_map = True
else:
    st.session_state.update_map = False
