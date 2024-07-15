# Import necessary libraries
import streamlit as st
import geemap
import ee

from stages.connection import establish_connection

# Initialize the Earth Engine module
establish_connection()


def create_map():
    Map = geemap.Map(center=[17.5, 0.0], zoom=5)
    # Test with a simple public dataset
    dem = ee.Image("USGS/SRTMGL1_003")
    Map.addLayer(dem, {"min": 0, "max": 3000}, "DEM")
    return Map


# Streamlit webpage layout
def app():
    st.title("Earth Engine Data Visualization")

    # Create the map
    Map = create_map()

    # Display the map using Streamlit's components
    Map.to_streamlit(height=700)


# Run the app
if __name__ == "__main__":
    app()
