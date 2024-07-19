import streamlit as st
import folium
from streamlit_folium import folium_static
import ee


from stages.connection import establish_connection

establish_connection()


def main():
    st.title("Landcover Upscaling using Earth Engine")

    # Define the geometry for the area of interest.
    geometry = ee.Geometry.Polygon(
        [
            [
                [29.972731783841393, 31.609824974226175],
                [29.972731783841393, 30.110383818311096],
                [32.56550522134139, 30.110383818311096],
                [32.56550522134139, 31.609824974226175],
                [29.972731783841393, 31.609824974226175],
            ]
        ]  # Ensure the polygon is closed by repeating the first point.
    )

    # Load the MODIS land cover data.
    modis_landcover = (
        ee.ImageCollection("MODIS/006/MCD12Q1")
        .filterDate("2001-01-01", "2001-12-31")
        .first()
        .select("LC_Type1")
        .subtract(1)
    )  # Adjust labels to start at zero

    # Visualization parameters for MODIS landcover.
    landcover_palette = (
        "05450a,086a10,54a708,78d203,009900,c6b044,dcd159,"
        "dade48,fbff13,b6ff05,27ff87,c24f44,a5a5a5,ff6d4c,69fff8,f9ffa4,1c0dff"
    )
    vis_params = {"palette": landcover_palette, "min": 0, "max": 16}

    # Load and filter Landsat data.
    landsat = (
        ee.ImageCollection("LANDSAT/LE07/C02/T1")
        .filterBounds(geometry)
        .filterDate("2000-01-01", "2001-01-01")
    )

    landsat_composite = ee.Algorithms.Landsat.simpleComposite(
        collection=landsat, asFloat=True
    )

    # Create a training dataset by sampling the stacked images.
    training = modis_landcover.addBands(landsat_composite).sample(
        region=geometry, scale=30, numPixels=1000  # Explicitly define the region here.
    )

    # Train a classifier.
    classifier = ee.Classifier.smileCart().train(
        features=training,  # This should be an ee.FeatureCollection
        classProperty="LC_Type1",  # Ensure this is the correct name of the label property
    )

    # Apply the classifier.
    upsampled = landsat_composite.classify(classifier)

    # Create a Folium map for visualization.
    folium_map = folium.Map(location=[30.86, 31.27], zoom_start=8)
    folium_map.add_ee_layer(modis_landcover, vis_params, "MODIS Landcover")
    folium_map.add_ee_layer(upsampled, vis_params, "Upsampled Landcover")

    # Display the map.
    folium_static(folium_map)


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict["tile_fetcher"].url_format,
        attr="Map Data &copy; Google Earth Engine",
        name=name,
        overlay=True,
        control=True,
    ).add_to(self)


folium.Map.add_ee_layer = add_ee_layer

if __name__ == "__main__":
    main()
