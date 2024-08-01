import streamlit as st
import geemap.foliumap as geemap
import folium
from streamlit_folium import st_folium
import geocoder
from stages.server_connection import establish_connection

# Establish server connection
establish_connection()

# Function to get the current geo-localization position
def get_current_location():
    g = geocoder.ip("me")
    return g.latlng

# Initialize session state for latitude and longitude
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    default_latlng = get_current_location()
    st.session_state.latitude = default_latlng[0]
    st.session_state.longitude = default_latlng[1]

# Streamlit UI
st.title("Geo-localization Position Display")

# Input fields for latitude and longitude with default values
latitude = st.number_input("Latitude", value=st.session_state.latitude, on_change=lambda: update_map_location())
longitude = st.number_input("Longitude", value=st.session_state.longitude, on_change=lambda: update_map_location())

# Update session state when the input values change
def update_map_location():
    st.session_state.latitude = latitude
    st.session_state.longitude = longitude

# Button to update the latitude and longitude to current location
if st.button("Use My Current Location"):
    latlng = get_current_location()
    st.session_state.latitude = latlng[0]
    st.session_state.longitude = latlng[1]

# Create a map centered at the provided latitude and longitude
m = geemap.Map(center=[st.session_state.latitude, st.session_state.longitude], zoom=12)

# Add a marker for the provided latitude and longitude
folium.Marker([st.session_state.latitude, st.session_state.longitude], popup="Specified Location").add_to(m)

# Display the map in Streamlit
st_folium(m, width=725)
