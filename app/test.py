# import streamlit as st
# import geemap.foliumap as geemap
# import folium
# from streamlit_folium import st_folium
# import geocoder
# from stages.server_connection import establish_connection

# establish_connection()
# # Get geo-localization position
# g = geocoder.ip("me")

# latitude = g.latlng[0]
# longitude = g.latlng[1]

# # Create a map centered at the geo-localization position
# m = geemap.Map(center=[latitude, longitude], zoom=12)

# # Add a marker for the geo-localization position
# folium.Marker([latitude, longitude], popup="Your Location").add_to(m)

# # Display the map in Streamlit
# st.title("Geo-localization Position Display")
# st_folium(m, width=725)

# if __name__ == "__main__":
#     st.run()

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


# Get the default geo-localization position
default_latlng = get_current_location()

# Streamlit UI
st.title("Geo-localization Position Display")

# Input fields for latitude and longitude with default values
latitude = st.number_input("Latitude", value=default_latlng[0])
longitude = st.number_input("Longitude", value=default_latlng[1])

# Button to update the latitude and longitude to current location
if st.button("Use My Current Location"):
    latlng = get_current_location()
    latitude = latlng[0]
    longitude = latlng[1]
    st.experimental_rerun()  # Re-run the script to update the input fields with the current location

# Create a map centered at the provided latitude and longitude
m = geemap.Map(center=[latitude, longitude], zoom=12)

# Add a marker for the provided latitude and longitude
folium.Marker([latitude, longitude], popup="Specified Location").add_to(m)

# Display the map in Streamlit
st_folium(m, width=725)
