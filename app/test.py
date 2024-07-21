import geemap.foliumap as geemap
import streamlit as st
import ee
from stages.connection import establish_connection

establish_connection()


def create_map(layer_visibilities):
    Map = geemap.Map(center=(0, 0), zoom=2, add_google_map=False)

    # Access and visualize the Global Surface Water data
    water = ee.Image("JRC/GSW1_3/GlobalSurfaceWater")
    occurrence = water.select("occurrence")
    water_vis_params = {"min": 0, "max": 100, "palette": ["cccccc", "0000ff"]}

    # Add the water occurrence layer based on checkbox state
    if layer_visibilities.get("Water Occurrence", False):
        Map.addLayer(occurrence, water_vis_params, "Water Occurrence")
        # Only add the legend if the layer is visible
        legend_dict = {"No Water": "cccccc", "Water Present": "0000ff"}
        Map.add_legend(title="Water Occurrence (%)", legend_dict=legend_dict)

    return Map


def app():
    st.title("Dynamic Legend Control for Layer Visibility")

    # Dictionary to store the visibility state of layers
    layer_visibilities = {}

    # Checkbox to control the visibility of the water occurrence layer
    layer_visibilities["Water Occurrence"] = st.sidebar.checkbox(
        "Show Water Occurrence", True
    )

    # Create and display the map based on the current state of layer visibility
    Map = create_map(layer_visibilities)
    Map.to_streamlit(height=600)


if __name__ == "__main__":
    app()
