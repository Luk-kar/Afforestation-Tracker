// Initialize the Earth Engine API
var srtm = ee.Image("USGS/SRTMGL1_003");
var soilGrids = ee.Image('ISDASOIL/Africa/v1/carbon_total');
var soc_0_20cm = soilGrids.select('mean_0_20');
var worldCover = ee.Image('ESA/WorldCover/v100/2020');
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY');
var moisture = ee.ImageCollection('NASA/SMAP/SPL4SMGP/007');

// Define the Sahel region as a polygon
var sahelRegion = ee.Geometry.Polygon([
    [[-17.5, 15.0], [-17.5, 20.0], [39.0, 20.0], [43.0, 10.5], [35.0, 8.0], // New point added here for South Sudan
    [25.0, 10.0], [15.0, 8.0], [-5.0, 12.0], [-10.0, 13.0]]
]);

var elevationVis = {
    min: 0,
    max: 3000,
    palette: ['0000FF', '00FFFF', '00FF00', 'FFFF00', 'FF0000']
};

var slopeVis = {
    min: 0,
    max: 60,
    palette: ['00FFFF', '0000FF', '00FF00', 'FFFF00', 'FF0000']
};

var socVis = {
    min: 0,
    max: 200,
    palette: ['FFFFFF', 'C0C0C0', '808080', '404040', '000000', '00FF00', '008000', 'FFFF00', 'FFA500', 'FF0000']
};


var precipVis = {
    min: 0,
    max: 3000, // Adjust this value based on the expected range of precipitation
    palette: ['FFFFFF', 'C0C0C0', '808080', '404040', '000000', '0000FF', '00FFFF', '00FF00', 'FFFF00', 'FF0000']
};

var moistVis = {
    min: 0.0,
    max: 0.5,
    palette: ['red', 'yellow', 'green', 'blue']
};

var regionsVis = {
    bands: ['Map'],
    min: 10,
    max: 100,
    palette: [
        '006400', // Tree cover - Dark Green
        'FFBB22', // Shrubland - Light Orange
        'FFFF4C', // Grassland - Yellow
        'F096FF', // Cropland - Light Pink
        'FA0000', // Built-up - Bright Red
        'B4B4B4', // Bare / Sparse vegetation - Grey
        'F0F0F0', // Snow and ice - White
        '0064C8', // Permanent water bodies - Blue
        '0096A0', // Herbaceous wetland - Cyan
        '00CF75', // Mangroves - Green
        'FAE6A0'  // Moss and lichen - Light Yellow
    ]
};

// Visualization parameters for candidate regions
var candidateVis = {
    min: 0,
    max: 1,
    palette: ['red', 'green']
};

// Filter datasets to only include the Sahel region
var srtmSahel = srtm.clip(sahelRegion);
var soilGridsSahel = soilGrids.clip(sahelRegion);
var worldCoverSahel = worldCover.clip(sahelRegion);
var soc_0_20cm = soc_0_20cm.clip(sahelRegion);

// Define the time range for one year (e.g., 2023)
var startDate = '2023-01-01';
var endDate = '2023-12-31';

// Filter the CHIRPS data to the specified date range and region
var chirpsYear = chirps.filterDate(startDate, endDate).map(function (image) {
    return image.clip(sahelRegion);
});

// Sum the daily precipitation to get the annual precipitation
var annualPrecipitation = chirpsYear.sum();

// Calculate the slope in degrees
var slope = ee.Terrain.slope(srtmSahel);

// Define a time period of interest for moisture (modify dates as needed)
var filteredMoistureDataset = moisture.filterDate('2020-01-01', '2020-01-10').map(function (image) {
    return image.clip(sahelRegion);
});

// Select the 'sm_surface' and 'sm_rootzone' bands
var soilMoistureSurface = filteredMoistureDataset.select('sm_surface');
var soilMoistureRootZone = filteredMoistureDataset.select('sm_rootzone');

// Visualization parameters remain unchanged

// Identify regions with minimal slope
var suitableSlope = slope.lt(15);

// Identify regions with minimal soil organic carbon or sufficient moisture
var suitableSOC = soc_0_20cm.gt(20); // Example: suitable SOC greater than 20 g/kg
var suitableMoisture = soilMoistureSurface.mean().gte(0.1); // Suitable soil moisture greater than or equal to 10% VWC
var goodMoisture = suitableSOC.or(suitableMoisture);

// Combine criteria to identify candidate regions
var candidateRegions = annualPrecipitation.gte(200).and(suitableSlope).and(goodMoisture);

// Mask out areas that are not Grass or Shrubland or Barenland
var shrubland = worldCoverSahel.eq(20); // Shrubland class in ESA WorldCover
var grassland = worldCoverSahel.eq(30); // Grassland class in ESA WorldCover
var barenland = worldCoverSahel.eq(60); // Barenland class in ESA WorldCover
var vegetationMask = grassland.or(barenland);

// Apply the mask to the candidate regions
var afforestationCandidates = candidateRegions.and(vegetationMask);

// Add layers to the map centered on the Sahel region
Map.centerObject(sahelRegion, 5);
Map.addLayer(srtmSahel, elevationVis, 'Elevation');
Map.addLayer(slope, slopeVis, 'Slope');
Map.addLayer(soc_0_20cm, socVis, 'Soil Organic Carbon 0-20cm');
Map.addLayer(annualPrecipitation, precipVis, 'Annual Precipitation');
Map.addLayer(worldCoverSahel, regionsVis, 'ESA WorldCover 2020');
Map.addLayer(afforestationCandidates, candidateVis, 'Candidate Regions for Afforestation');

// Display the map
Map;
