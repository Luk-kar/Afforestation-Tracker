from lxml import etree
from io import StringIO

# Define the HTML content (shortened for brevity and relevance)
html_content = """
        <div class="block-container st-emotion-cache-13ln4jf ea3mdgi5" data-testid="stAppViewBlockContainer">
            <div data-testid="stVerticalBlockBorderWrapper" data-test-scroll-behavior="normal" class="st-emotion-cache-0 e1f1d6gn0">
                <div class="st-emotion-cache-1wmy9hl e1f1d6gn1">
                    <div width="704" data-testid="stVerticalBlock" class="st-emotion-cache-1n76uvr e1f1d6gn2">
                        <div data-stale="false" width="704" class="element-container st-emotion-cache-1vxmjmh e1f1d6gn4" data-testid="element-container">
                            <div class="stMarkdown" style="width: 704px;" data-testid="stMarkdown">
                                <div data-testid="stMarkdownContainer" class="st-emotion-cache-uzeiqp e1nzilvr4">
                                    <div data-testid="stHeadingWithActionElements" class="st-emotion-cache-asc41u e1nzilvr2">
                                        <h1 style="text-align: center;" level="1" id="e1b2b30">Afforestation Tracker 🗺️🌴<span data-testid="stHeaderActionElements" class="st-emotion-cache-gi0tri e1nzilvr1"><a href="#e1b2b30" class="st-emotion-cache-yinll1 e1nzilvr3"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3"></path><line x1="8" y1="12" x2="16" y2="12"></line></svg></a></span></h1></div>
                                </div>
                            </div>
                        </div>
                        <div data-stale="false" width="704" class="element-container st-emotion-cache-1vxmjmh e1f1d6gn4" data-testid="element-container">
                            <div class="stMarkdown" style="width: 704px;" data-testid="stMarkdown">
                                <div data-testid="stMarkdownContainer" class="st-emotion-cache-uzeiqp e1nzilvr4">
                                    <p style="text-align: center;">Click on the map to view data for a specific point 👆</p>
                                </div>
                            </div>
                        </div>
                        <div data-stale="false" width="704" class="element-container st-emotion-cache-1vxmjmh e1f1d6gn4" data-testid="element-container">
                            <iframe allow="accelerometer; ambient-light-sensor; autoplay; battery; camera; clipboard-write; document-domain; encrypted-media; fullscreen; geolocation; gyroscope; layout-animations; legacy-image-formats; magnetometer; microphone; midi; oversized-images; payment; picture-in-picture; publickey-credentials-get; sync-xhr; usb; vr ; wake-lock; xr-spatial-tracking"
                            src="http://localhost:8505/component/streamlit_folium.st_folium/index.html?streamlitUrl=http%3A%2F%2Flocalhost%3A8505%2F" width="704" height="520" style="color-scheme: normal; display: initial;" scrolling="no" sandbox="allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-downloads"
                            title="streamlit_folium.st_folium"></iframe>
                        </div>
                        <div data-stale="false" width="704" class="element-container st-emotion-cache-1vxmjmh e1f1d6gn4" data-testid="element-container">
                            <div class="stAlert" data-testid="stAlert">
                                <div role="alert" data-baseweb="notification" data-testid="stNotification" class="st-ae st-af st-ag st-ah st-ai st-aj st-ak st-al st-am st-an st-ao st-ap st-aq st-ar st-as st-at st-au st-av st-aw st-ax st-ay st-az st-bb st-b1 st-b2 st-b3 st-b4 st-b5 st-b6 st-b7 st-b8">
                                    <div class="st-b9 st-ba">
                                        <div data-testid="stNotificationContentSuccess" class="st-emotion-cache-wmn9kq e1e4pi9i0">
                                            <div class="st-emotion-cache-1nmtqlb e1eexb540">
                                                <div style="width: 100%;" data-testid="stMarkdownContainer" class="st-emotion-cache-uzeiqp e1nzilvr4">
                                                    <p>Latitude: 12.9444 | Longitude: 11.8889</p>
                                                    <p>Address: Mozogun, Yunusari, Yobe, Nigeria</p>
                                                    <p>Afforestation Candidate: <strong>Yes</strong></p>
                                                    <p>Elevation: 320 meters, Slope: 1.9°, Rainy Season Root Zone Soil Moisture: 7.22 %, Yearly Precipitation: 468.83 mm, Soil Organic Carbon: 19 g/kg, World Cover: <strong>Grassland</strong></p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div data-testid="stHorizontalBlock" class="st-emotion-cache-ocqkz7 e1f1d6gn5">
                            <div data-testid="column" class="st-emotion-cache-keje6w e1f1d6gn3">
                                <div data-testid="stVerticalBlockBorderWrapper" data-test-scroll-behavior="normal" class="st-emotion-cache-0 e1f1d6gn0">
                                    <div class="st-emotion-cache-1wmy9hl e1f1d6gn1">
                                        <div width="344" data-testid="stVerticalBlock" class="st-emotion-cache-1njjmvq e1f1d6gn2">
                                            <div data-stale="false" width="344" class="element-container st-emotion-cache-lj8h43 e1f1d6gn4" data-testid="element-container">
                                                <div class="stAlert" data-testid="stAlert">
                                                    <div role="alert" data-baseweb="notification" data-testid="stNotification" class="st-ae st-af st-ag st-ah st-ai st-aj st-ak st-ef st-am st-ei st-ao st-ap st-aq st-ar st-as st-at st-eh st-av st-aw st-ax st-ay st-az st-bb st-b1 st-b2 st-b3 st-b4 st-b5 st-b6 st-b7 st-b8">
                                                        <div class="st-b9 st-ba">
                                                            <div data-testid="stNotificationContentWarning" class="st-emotion-cache-wmn9kq e1e4pi9i0">
                                                                <div class="st-emotion-cache-1nmtqlb e1eexb540">
                                                                    <div style="width: 100%;" data-testid="stMarkdownContainer" class="st-emotion-cache-uzeiqp e1nzilvr4">
                                                                        <p>The widget with key "latitude" was created with a default value but also had its value set via the Session State API.</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div data-stale="false" width="344" class="element-container st-emotion-cache-lj8h43 e1f1d6gn4" data-testid="element-container">
                                                <div class="stNumberInput" data-testid="stNumberInput" style="width: 344px;">
                                                    <label data-testid="stWidgetLabel" aria-hidden="true" for="number_input_7" class="st-emotion-cache-up131x e1y5xkzn3" disabled="">
                                                        <div data-testid="stMarkdownContainer" class="st-emotion-cache-1whx7iy e1nzilvr4">
                                                            <p>Latitude</p>
                                                        </div>
                                                    </label>
                                                    <div class=" st-emotion-cache-6v4t1a e116k4er3" data-testid="stNumberInputContainer">
                                                        <div data-baseweb="input" class="st-bc st-b4 st-bd st-b9 st-be st-bf st-bg st-bh st-bi st-bj st-bk st-bl st-bm st-b2 st-bn st-av st-ay st-bo st-bp st-ae st-af st-ag st-ah st-ai st-aj st-bq st-br st-bs st-bt st-bu st-bv st-bw">
                                                            <div data-baseweb="base-input" class="st-b4 st-b9 st-bx st-b2 st-bn st-ae st-af st-ag st-ah st-ai st-aj st-cg st-bu st-bo st-bp">
                                                                <input aria-label="Latitude" aria-invalid="false" aria-required="false" autocomplete="on" id="number_input_7" inputmode="text" name="" placeholder="" type="number" min="-Infinity" max="Infinity"
                                                                step="0.5" data-testid="stNumberInput-Input" class="st-bc st-bz st-be st-bf st-bg st-bh st-c0 st-c1 st-c2 st-c3 st-c4 st-b9 st-c5 st-c6 st-ch st-c8 st-c9 st-ca st-cb st-cc st-ae st-af st-ag st-cd st-ai st-aj st-cg st-ci st-ce st-cj"
                                                                value="12.9444" disabled="">
                                                            </div>
                                                        </div>
                                                        <div class="st-emotion-cache-76z9jo e116k4er2">
                                                            <button class="step-down st-emotion-cache-zbmw0q e116k4er1" data-testid="stNumberInput-StepDown" disabled="" tabindex="-1">
                                                                <svg viewBox="0 0 8 8" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp53 st-emotion-cache-14zer8g ex0cdmw0">
                                                                    <path d="M0 3v2h8V3H0z"></path>
                                                                </svg>
                                                            </button>
                                                            <button class="step-up st-emotion-cache-zbmw0q e116k4er1" data-testid="stNumberInput-StepUp" disabled="" tabindex="-1">
                                                                <svg viewBox="0 0 8 8" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp53 st-emotion-cache-14zer8g ex0cdmw0">
                                                                    <path d="M3 0v3H0v2h3v3h2V5h3V3H5V0H3z"></path>
                                                                </svg>
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div class="st-emotion-cache-uapcc7 e116k4er0">
                                                        <div data-testid="InputInstructions" class="st-emotion-cache-1li7dat e1y5xkzn1"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div data-testid="column" class="st-emotion-cache-keje6w e1f1d6gn3">
                                <div data-testid="stVerticalBlockBorderWrapper" data-test-scroll-behavior="normal" class="st-emotion-cache-0 e1f1d6gn0">
                                    <div class="st-emotion-cache-1wmy9hl e1f1d6gn1">
                                        <div width="344" data-testid="stVerticalBlock" class="st-emotion-cache-1njjmvq e1f1d6gn2">
                                            <div data-stale="false" width="344" class="element-container st-emotion-cache-lj8h43 e1f1d6gn4" data-testid="element-container">
                                                <div class="stNumberInput" data-testid="stNumberInput" style="width: 344px;">
                                                    <label data-testid="stWidgetLabel" aria-hidden="true" for="number_input_8" class="st-emotion-cache-up131x e1y5xkzn3" disabled="">
                                                        <div data-testid="stMarkdownContainer" class="st-emotion-cache-1whx7iy e1nzilvr4">
                                                            <p>Longitude</p>
                                                        </div>
                                                    </label>
                                                    <div class=" st-emotion-cache-6v4t1a e116k4er3" data-testid="stNumberInputContainer">
                                                        <div data-baseweb="input" class="st-bc st-b4 st-bd st-b9 st-be st-bf st-bg st-bh st-bi st-bj st-bk st-bl st-bm st-b2 st-bn st-av st-ay st-bo st-bp st-ae st-af st-ag st-ah st-ai st-aj st-bq st-br st-bs st-bt st-bu st-bv st-bw">
                                                            <div data-baseweb="base-input" class="st-b4 st-b9 st-bx st-b2 st-bn st-ae st-af st-ag st-ah st-ai st-aj st-cg st-bu st-bo st-bp">
                                                                <input aria-label="Longitude" aria-invalid="false" aria-required="false" autocomplete="on" id="number_input_8" inputmode="text" name="" placeholder="" type="number" min="-Infinity" max="Infinity"
                                                                step="0.5" data-testid="stNumberInput-Input" class="st-bc st-bz st-be st-bf st-bg st-bh st-c0 st-c1 st-c2 st-c3 st-c4 st-b9 st-c5 st-c6 st-ch st-c8 st-c9 st-ca st-cb st-cc st-ae st-af st-ag st-cd st-ai st-aj st-cg st-ci st-ce st-cj"
                                                                value="11.8889" disabled="">
                                                            </div>
                                                        </div>
                                                        <div class="st-emotion-cache-76z9jo e116k4er2">
                                                            <button class="step-down st-emotion-cache-zbmw0q e116k4er1" data-testid="stNumberInput-StepDown" disabled="" tabindex="-1">
                                                                <svg viewBox="0 0 8 8" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp53 st-emotion-cache-14zer8g ex0cdmw0">
                                                                    <path d="M0 3v2h8V3H0z"></path>
                                                                </svg>
                                                            </button>
                                                            <button class="step-up st-emotion-cache-zbmw0q e116k4er1" data-testid="stNumberInput-StepUp" disabled="" tabindex="-1">
                                                                <svg viewBox="0 0 8 8" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" color="inherit" class="eyeqlp53 st-emotion-cache-14zer8g ex0cdmw0">
                                                                    <path d="M3 0v3H0v2h3v3h2V5h3V3H5V0H3z"></path>
                                                                </svg>
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div class="st-emotion-cache-uapcc7 e116k4er0">
                                                        <div data-testid="InputInstructions" class="st-emotion-cache-1li7dat e1y5xkzn1"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div data-stale="false" width="704" class="element-container st-emotion-cache-1vxmjmh e1f1d6gn4" data-testid="element-container">
                            <iframe data-testid="stIFrame" allow="accelerometer; ambient-light-sensor; autoplay; battery; camera; clipboard-write; document-domain; encrypted-media; fullscreen; geolocation; gyroscope; layout-animations; legacy-image-formats; magnetometer; microphone; midi; oversized-images; payment; picture-in-picture; publickey-credentials-get; sync-xhr; usb; vr ; wake-lock; xr-spatial-tracking"
                            style="color-scheme: normal;" srcdoc="
    <style>
        .scrollable-legend {
            height: 340px;
            overflow-x: scroll;
            overflow-y: hidden;
            white-space: nowrap;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: #f9f9f9;
            display: flex;
            align-items: flex-start;
        }
        .legend-entry {
            display: inline-block;
            cursor: move;
            padding: 10px;
            border: 1px solid #ccc;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: max-content;
            margin-right: 10px;
        }
        .legend-title {
            font-weight: bold;
        }
        .legend-detail {
            display: flex;
            align-items: center;
            margin-top: 5px;
        }
        .color-indicator {
            width: 20px;
            height: 20px;
            border: 1px solid grey;
            margin-right: 5px;
        }
    </style>
    <div class='scrollable-legend'>
                <div class='legend-entry' id='afforestation_candidates_legend'>
                    <div class='legend-title'>Planting Zones</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FF0000;'></div>
                            <span>Not Suitable</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FF00;'></div>
                            <span>Suitable</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='precipitation_legend'>
                    <div class='legend-title'>Precipitation</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFFFF;'></div>
                            <span>0-200 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #C0C0C0;'></div>
                            <span>200-400 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #808080;'></div>
                            <span>400-600 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #404040;'></div>
                            <span>600-800 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #000000;'></div>
                            <span>800-1000 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0000FF;'></div>
                            <span>1000-1200 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FFFF;'></div>
                            <span>1200-1400 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FF00;'></div>
                            <span>1400-1600 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFF00;'></div>
                            <span>1600-1800 mm</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FF0000;'></div>
                            <span>1800-2000 mm</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='soil_moisture_legend'>
                    <div class='legend-title'>Root Zone Moisture</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FF0000;'></div>
                            <span>0.0-12.5</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFF00;'></div>
                            <span>12.5-25.0</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #008000;'></div>
                            <span>25.0.-37.5</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0000FF;'></div>
                            <span>37.5-50.0</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='soc_0_20cm_legend'>
                    <div class='legend-title'>Soil Organic Carbon (0-20 cm) g/kg</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFFFF;'></div>
                            <span>0-40 g/kg</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #C0C0C0;'></div>
                            <span>40-80 g/kg</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #808080;'></div>
                            <span>80-120 g/kg</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #404040;'></div>
                            <span>120-160 g/kg</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #000000;'></div>
                            <span>160-200 g/kg</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='world_cover_legend'>
                    <div class='legend-title'>World Cover</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #006400;'></div>
                            <span>Tree Cover</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFBB22;'></div>
                            <span>Shrubland</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFF4C;'></div>
                            <span>Grassland</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #F096FF;'></div>
                            <span>Cropland</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FA0000;'></div>
                            <span>Built-up</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #B4B4B4;'></div>
                            <span>Bare / Sparse Vegetation</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #F0F0F0;'></div>
                            <span>Snow and Ice</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0064C8;'></div>
                            <span>Permanent Water Bodies</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0096A0;'></div>
                            <span>Herbaceous Wetland</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00CF75;'></div>
                            <span>Mangroves</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FAE6A0;'></div>
                            <span>Moss and Lichen</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='slope_legend'>
                    <div class='legend-title'>Slope (degrees)</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0000FF;'></div>
                            <span>0-12°</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FFFF;'></div>
                            <span>12-24°</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FF00;'></div>
                            <span>24-36°</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFF00;'></div>
                            <span>36-48°</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FF0000;'></div>
                            <span>48-60°</span>
                        </div>
                </div></div>
                <div class='legend-entry' id='elevation_legend'>
                    <div class='legend-title'>Elevation (m)</div>
                    <div class='legend-details'>
            
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #0000FF;'></div>
                            <span>0-600 m</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FFFF;'></div>
                            <span>600-1200 m</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #00FF00;'></div>
                            <span>1200-1800 m</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FFFF00;'></div>
                            <span>1800-2400 m</span>
                        </div>
                
                        <div class='legend-detail'>
                            <div class='color-indicator' style='background-color: #FF0000;'></div>
                            <span>2400-3000 m</span>
                        </div>
                </div></div></div>
    <script>
        document.querySelectorAll('.legend-entry').forEach(el => {
            el.addEventListener('mousedown', function(e) {
                let shiftX = e.clientX - el.getBoundingClientRect().left;
                let shiftY = e.clientY - el.getBoundingClientRect().top;
                function moveAt(pageX, pageY) {
                    el.style.left = pageX - shiftX + 'px';
                    el.style.top = pageY - shiftY + 'px';
                }
                function onMouseMove(e) {
                    moveAt(e.pageX, e.pageY);
                }
                document.addEventListener('mousemove', onMouseMove);
                el.onmouseup = function() {
                    document.removeEventListener('mousemove', onMouseMove);
                    el.onmouseup = null;
                };
                el.ondragstart = function() { return false; };
            });
        });
    </script>
    " width="704" height="400" scrolling="auto" sandbox="allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-downloads" title="st.iframe"></iframe>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

# Parse the HTML content
parser = etree.HTMLParser()
tree = etree.parse(StringIO(html_content), parser)

# XPath expressions for latitude and longitude inputs
# xpath_latitude = "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput']::label[contains(text(), 'Longitude')]"
xpath_latitude = "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput'][contains(., 'Longitude')]"
xpath_longitude = "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput'][contains(., 'Longitude')]"
# xpath_longitude = "//div[@data-testid='stAppViewBlockContainer']//div[@data-testid='stNumberInput'][descendant::label[contains(text(), 'Longitude')]]"

# Execute the XPath expressions
latitude_input_element = tree.xpath(xpath_latitude)
longitude_input_element = tree.xpath(xpath_longitude)

# Test the results
print("Latitude Input Found:", latitude_input_element != [])
print("Longitude Input Found:", longitude_input_element != [])

# For further inspection, print details about the found elements
for elem in latitude_input_element:
    print(
        "Latitude Input Element ID:", elem.xpath(".//input/@id")[0]
    )  # Should print 'latitude_input'

for elem in longitude_input_element:
    print(
        "Longitude Input Element ID:", elem.xpath(".//input/@id")[0]
    )  # Should print 'longitude_input'
