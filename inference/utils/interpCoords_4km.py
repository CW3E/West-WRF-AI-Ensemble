# from scipy.spatial import cdist
from scipy.spatial import KDTree
# Function to find the nearest station
def find_nearest_station(ds, target_latitudes, target_longitudes):
    print("Interpolating...")
    ## Latitude and longitudes of WRF
    latitudes = ds['lat'].values
    longitudes = ds['lon'].values
    # Create a 2D array of the station coordinates
    data_coords = np.vstack([latitudes, longitudes]).T
    # Use a KDTree to efficiently find nearest neighbors
    tree = KDTree(data_coords)
    # Stack target latitudes and longitudes into a 2D array for efficient distance computation
    target_coords = np.vstack([target_latitudes, target_longitudes]).T
    # Query the KDTree for nearest neighbor indices
    nearest_stations_idx = tree.query(target_coords, k=1)[1]
    ## Get values at the nearest stations and build out xarray Dataset
    out = ds.isel(stationID = nearest_stations_idx)
    # Replace latitude and longitudes by target latitudes and target longitudes
    num_gridpoints = len(out.stationID.values)
    out = out.assign_coords(stationID=("stationID", np.arange(num_gridpoints)), lat=("stationID", target_latitudes), lon=("stationID", target_longitudes))
    # Return nearest stations to each target point
    print("Done!")
    return out

# # Function to find the nearest station
# def find_nearest_station(ds, target_latitudes, target_longitudes):
#     print("Interpolating...")
#     latitudes = ds['lat'].values
#     longitudes = ds['lon'].values
#     # Step 1: Create list of station coordinates
#     data_coords = list(zip(latitudes, longitudes))
#     # Step 2: Initialize a list to store nearest stations for each target point
#     nearest_stations = []
#     # Step 3: Loop through each target point
#     for target_lat, target_lon in zip(target_latitudes, target_longitudes):
#         # Step 4: Compute the distance for each station to the target point
#         distances = [haversine(target_lat, target_lon, lat, lon) for lat, lon in data_coords] 
#         # Step 5: Find the index of the nearest station
#         nearest_station_idx = np.argmin(distances)
#         # Compute the nearest station's coordinates and distance
#         # nearest_station_coords = data_coords[nearest_station_idx]
#         # nearest_station_distance = distances[nearest_station_idx]
#         # Store the nearest station's idx
#         nearest_stations.append(nearest_station_idx)
#     # Return nearest stations to each target point
#     print("Done!")
#     return nearest_stations




