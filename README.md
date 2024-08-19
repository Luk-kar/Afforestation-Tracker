# 🗺️🌴 Afforestation Tracker
## 📋 Overview

![Sahara region](doc/images/sahara-region.jpeg)

This project is inspired by the UN's [**Great Green Wall**](https://en.wikipedia.org/wiki/Great_Green_Wall_(Africa)) initiative in Africa.

The **Afforestation Tracker** is an online tool that tracks and studies areas in the Sahel region for planting trees. It uses geographic data from different sources to assess the environment and find the best locations for planting.

The system features an interactive map that allows users to explore different layers like:
1. Areas good for planting trees
1. Ground wetness
1. Rainfall levels
1. Soil carbon content
1. Vegetation types
1. Ground slope
1. Height above sea level
1. Satellite photos

Each type of data comes with a guide to help users understand it. By clicking on a map point, users can see detailed info about that place's tree-planting potential.

The system gathers data from `Google Earth Engine` for environmental info and `Nominatim` for place names. It uses `Streamlit` for the web interface, with `folium` and `geemap` for maps, making it easy to use online.

This tool is useful for researchers and decision-makers involved in tree planting in the Sahel to help with managing land sustainably.

## 📊 Data Visualization

![dashboard](doc/images/dashboard_preview.png)

## Data used

- **Rootzone Soil Moisture:**

  Sourced from NASA's SMAP Mission, specifically the SPL4SMGP dataset, which offers high-resolution soil moisture data essential for assessing suitable planting sites, when precipitation is low, but there are floods. [Details](https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_007)

- **Precipitation:**

  Daily precipitation data is provided by the UCSB Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS), which helps in understanding rainfall patterns critical for vegetation. [Details](https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY)

- **Elevation:** 

  Elevation data is obtained from the USGS SRTMGL1 dataset, aiding in the evaluation of plant species requirements and terrain accessibility. [Details](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003)

- **Soil Organic Carbon:** 

  The ISDASOIL database provides data on soil organic carbon content across Africa, crucial for assessing soil health and fertility. [Details](https://developers.google.com/earth-engine/datasets/catalog/ISDASOIL_Africa_v1_carbon_total)

- **World Type Terrain Cover:** 

  Utilizes the ESA WorldCover dataset to map different types of terrain cover, which supports the selection of appropriate vegetation types for different areas. [Details](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100)

- **Satellite Imagery:**
 
  High-resolution imagery from the Copernicus Sentinel-2 mission is employed to obtain current and accurate visualizations of the landscapes, enhancing the precision of assessments. [Details](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_HARMONIZED)

- **Place Names:**

  The Nominatim API is utilized to retrieve accurate place names, improving the mapping interface's usability by enabling easy search and location identification for specific areas. [Details](https://nominatim.org/)

## 🗂️ Project Structure

![data_pipeline](doc/images/data_pipeline.png)

### 📚 Key Libraries

**Data Acquisition:**

- [**`ee:`**](https://developers.google.com/earth-engine/guides/python_install)

  _Tools for working with geographic data API on Google Earth Engine._

**Data Visualization:**

- [**`Streamlit:`**](https://docs.streamlit.io/)
  
  _A tool for building web apps easily, transforming data scripts into interactive apps with little coding._

- [**`folium:`**](https://python-visualization.github.io/folium/latest/)

  _Allows interactive maps in Python, using Leaflet.js for visualizing geographic data._

- [**`streamlit-folium:`**](https://folium.streamlit.app/)

  _Enhances Streamlit apps with real-time map interactions_

- [**`geemap:`**](https://geemap.org/)

  _Adds more map controls and manages map layers efficiently in Google Earth Engine._

## 📦 Requirements

See the [`Pipfile`](Pipfile) for needed packages.

## ⚙️ Installation

Before you launch the app, prepare the `.env` file with these  [settings](https://developers.google.com/earth-engine/guides/app_key):

```plaintext
 YOUR_ACCESS_TOKEN: The full path to your GEE service account JSON key file.
 SERVICE_ACCOUNT: The email address of your GEE service account.

 ```

To prepare the environment:

```bash
pip install pipenv
pipenv install
pipenv shell
```

## 🔧 Configuration

Adjust settings in the [app/config.py](app/config.py) file, which controls configurations and outlines data processing steps.

Details include:

  - UI settings
  - Data sample size for Google Earth Engine
  - Target region and data collection settings
  - Sources and visualization settings for different data types

---

### 🌴 Afforestation Category Logic

Details in: [`app/stages/data_categorization.py`](app/stages/data_categorization.py).


## 🔨 Usage

Run the app with:

```bash
streamlit run app/streamlit_app.py
```
**🚨 Note**:
Depends on external data, so loading times may vary. Keep your `GEE` private key updated.


## ✅ Testing

To test, activate the environment and run tests:

```bash
pipenv shell
python -m unittest discover
```
---

## 💡 Notes

Insights include:

1. **State management and caching**

    in [`Streamlit v1.37.1`](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) is often unstable, making it hard to update UI elements consistently, especially with the external server's API calls. Bugs can occur silently, especially when UI or dynamic JavaScript elements don't show up. It's best to use these features sparingly.

2. **Backend Engine Alternatives:**
    For apps needing heavy API use and detailed state management, try using Dash or Flask over Streamlit. [`Dash`](https://dash.plotly.com/) and [`Flask`](https://flask.palletsprojects.com/en/3.0.x/) handle complex tasks better. See the differences [here](https://www.datarevenue.com/en-blog/data-dashboarding-streamlit-vs-dash-vs-shiny-vs-voila).

3. **Test Data Transformations Directly on Cloud Services:**
    To streamline development, test data transformations directly on [`Google Earth Engine`](https://code.earthengine.google.com/).

4. **Use Data Sources Independent of Cloud Providers:**
    Use independent data sources like [`NASA`](https://worldview.earthdata.nasa.gov/), [`UCSB`](https://www.library.ucsb.edu/geospatial/maps), [`iSDA`](https://www.isda-africa.com/isdasoil/), and [`ESA`](https://esa.maps.eox.at/), available freely or by subscription. This lessens reliance on the Google Cloud Platform (`GCP`) and keeps data accessible if it goes down. Some data can be also found on `AWS`.

## 🧩 Ideas for Further Growth

1. Show the user's current location.

2. Map plant species to their optimal planting regions
    <details>
    <summary>Click me</summary>

      ### Trees:
      - **[Acacia senegal](https://en.wikipedia.org/wiki/Acacia_senegal)** _(Gum Arabic Tree)_
      - **[Faidherbia albida](https://en.wikipedia.org/wiki/Faidherbia_albida)** _(Apple-ring Acacia)_
      - **[Balanites aegyptiaca](https://en.wikipedia.org/wiki/Balanites_aegyptiaca)** _(Desert Date)_
      - **[Parkia biglobosa](https://en.wikipedia.org/wiki/Parkia_biglobosa)** _(African Locust Bean Tree)_
      - **[Adansonia digitata](https://en.wikipedia.org/wiki/Adansonia_digitata)** _(Baobab)_

      ### Shrubs:
      - **[Ziziphus mauritiana](https://en.wikipedia.org/wiki/Ziziphus_mauritiana)** _(Jujube)_
      - **[Guiera senegalensis](https://en.wikipedia.org/wiki/Guiera_senegalensis)** _(Guiera)_
      - **[Piliostigma reticulatum](https://en.wikipedia.org/wiki/Piliostigma_reticulatum)** _(Camel’s Foot)_
      - **[Combretum micranthum](https://en.wikipedia.org/wiki/Combretum_micranthum)** _(Kinkeliba)_
      - **[Leptadenia pyrotechnica](https://en.wikipedia.org/wiki/Leptadenia_pyrotechnica)** _(Marakh)_


    </details>
3. Show suitable plant species for a selected point on the map.

## 📜 License

Licensed under the [LICENSE](LICENSE) file.