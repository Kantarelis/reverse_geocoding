import time
import pandas as pd
import folium
import folium.plugins as plugins
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# # Measuer Run Time
start_time = time.time()

# ====================================== Control panel ============================================
Number_of_Addresses = "Many"                                    # It's either 'One' or 'Many'.
starting_location = [59.338315,18.089960]                       # Takes form of [Latitude, Longitude]
starting_location_zoom = 12                                     # Takes values from 1 to 18
(manual_latitude, manual_longitude) = (46.3144754, 11.0480288)  # Set Manually coordinates while Number_of_Addresses is set to 'One'.
delay_time_in_seconds = 0.5                                     # Set the delay of requests from geopy server (less than 0.5 pointless)
toggle_minimap_display = True                                   # It's either 'Ture or 'False'.
toggle_draw_toolkit = True                                      # Draw Toolkit
# =================================================================================================

# Form and Name of the Reverse Geocoder
geolocator = Nominatim(user_agent="Reverse_Geocoder")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=delay_time_in_seconds)

# Define Folium's map settings
folium_map = folium.Map(location=starting_location,
                        zoom_start=starting_location_zoom,
                         max_bounds=True)

# Create Themes with LayerControl for Folium Map
folium.TileLayer('openstreetmap').add_to(folium_map)
folium.TileLayer('Stamen Terrain').add_to(folium_map)
folium.TileLayer('Cartodbpositron').add_to(folium_map)
folium.TileLayer('CartoDB dark_matter').add_to(folium_map)
folium.TileLayer('stamenwatercolor').add_to(folium_map)
folium.TileLayer('stamentoner').add_to(folium_map)

if (Number_of_Addresses == "One"):
    location = reverse(str(manual_latitude) + "," + str(manual_longitude))
    print(location)
    
    folium.Marker(location=[manual_latitude, manual_longitude]).add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    folium_map.save("map.html")

elif (Number_of_Addresses == "Many"):
    # get the csv data and convert to DataFrame
    df = pd.read_csv("/home/varoth/Desktop/Work/Geoploting/Reverse_Geocoding/coordinates.csv")

    # database = pd.DataFrame([df['Latitude'], df["Longitude"]])
    database = pd.DataFrame(df[['Latitude', "Longitude"]])

    # Shape the data
    rows, cols = df.shape
    
    # Filter for Latitude
    alm_correct_latitudes = []
    alm_broken_latitudes = []
    for i in range (rows):
        filter = database.iat[i, 0]

        def is_float(filter):
            try:
                float(filter)
                return True
            except ValueError:
                return False

        if is_float(filter) is True:
            correct_x = float(filter)
            alm_correct_latitudes.append(correct_x)
        else:
            broken_x = str(filter)
            alm_broken_latitudes.append(broken_x)

    # Filter for Longitude
    alm_correct_longitudes = []
    alm_broken_longitudes = []
    for i in range (rows):
        filter = database.iat[i, 1]

        def is_float(filter):
            try:
                float(filter)
                return True
            except ValueError:
                return False

        if is_float(filter) is True:
            correct_y = float(filter)
            alm_correct_longitudes.append(correct_y)
        else:
            broken_y = str(filter)
            alm_broken_longitudes.append(broken_y)

    # Create Correct Database and Broken Database
    alm_correct_database = pd.DataFrame({"Latitude":alm_correct_latitudes, "Longitude":alm_correct_longitudes})
    alm_broken_database = pd.DataFrame({"Latitude":alm_broken_latitudes, "Longitude":alm_broken_longitudes})

    nan_value = float("NaN")
    alm_correct_database.replace("", nan_value, inplace=True)
    na_free = alm_correct_database.dropna()
    Nan_broken_database = alm_correct_database[~alm_correct_database.index.isin(na_free.index)]

    alm_correct_database.dropna(subset = ["Latitude"], inplace=True)
    alm_correct_database.dropna(subset = ["Longitude"], inplace=True)
    correct_database = alm_correct_database

    # Shape Correct Data Base
    correct_rows, correct_cols = correct_database.shape
    
    # Save Broken Coordinates into a csv file.
    Nan_broken_database.to_csv("broken_coordinates.csv")
    
    # Reverse Gepolot
    results = []
    for i in range (correct_rows):
        locations = reverse((str(correct_database.iloc[i, 0]) + "," + str(correct_database.iloc[i, 1])), language='en', exactly_one=True)
        results.append(locations)

    addresses = pd.DataFrame(results)
    addresses.to_csv("addresses_results.csv")
    
    # Pass Data to Folium Map
    plugins.FastMarkerCluster(data=list(zip(correct_database['Latitude'].values, correct_database['Longitude'].values))).add_to(folium_map)
    
    # Create Fullscreen Button
    plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True
    ).add_to(folium_map)

    # Create Minimap
    minimap = plugins.MiniMap(toggle_display=toggle_minimap_display)
    folium_map.add_child(minimap)

    # Locate Control
    folium.LayerControl().add_to(folium_map)
    plugins.LocateControl(auto_start=False).add_to(folium_map)

    # Create Draw Toolkit
    draw = plugins.Draw(export=toggle_draw_toolkit)
    draw.add_to(folium_map)
    folium_map.save("map.html")

else:
    print("Please insert a valid 'Number_of_Addresses' input, either 'One' or 'Many'.")

print("Process finished --- %s seconds ---" % (time.time() - start_time))