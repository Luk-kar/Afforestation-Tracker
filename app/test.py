import streamlit as st
import folium
from streamlit_folium import st_folium
import geocoder
from stages.server_connection import establish_connection

# Establish a server connection
establish_connection()


# Function to get the current geolocation using the user's IP
def get_current_location():
    g = geocoder.ip("me")
    return g.latlng


# Set the latitude and longitude in session state based on the current location
def set_lat_lon():
    default_latlng = get_current_location()
    return default_latlng[0], default_latlng[1]


# Update coordinates based on map click events
def update_coords_on_click(map_data):
    if map_data and map_data["last_clicked"]:
        last_click_lat, last_click_lng = (
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"],
        )
        st.session_state.latitude = last_click_lat
        st.session_state.longitude = last_click_lng


# Initialize latitude and longitude in session state if not already set
if "latitude" not in st.session_state or "longitude" not in st.session_state:
    st.session_state.latitude, st.session_state.longitude = set_lat_lon()

# Button to use the current location, updating map and inputs
if st.button("Use My Current Location"):
    st.session_state.latitude, st.session_state.longitude = set_lat_lon()

# Main Streamlit app layout
st.title("Geo-localization Position Display")

# Create the Folium map centered on the current location
map = folium.Map(
    location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12
)
folium.Marker(
    [st.session_state.latitude, st.session_state.longitude], popup="Specified Location"
).add_to(map)
folium.LatLngPopup().add_to(map)

# Embed the Folium map in the Streamlit app
map_data = st_folium(map, width=725, height=500)

# Update coordinates if a location on the map is clicked
update_coords_on_click(map_data)

# Widget for manually updating latitude
latitude = st.number_input(
    "Latitude", value=st.session_state.latitude, key="latitude", on_change=set_lat_lon
)
longitude = st.number_input(
    "Longitude",
    value=st.session_state.longitude,
    key="longitude",
    on_change=set_lat_lon,
)

if longitude != st.session_state.longitude:
    st.session_state.longitude = longitude
elif latitude != st.session_state.latitude:
    st.session_state.latitude = latitude
