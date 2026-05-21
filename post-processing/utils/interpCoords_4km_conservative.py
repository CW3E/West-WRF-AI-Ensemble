import os
import numpy as np
import xarray as xr
# from scipy.interpolate import griddata
from scipy.spatial import KDTree

def interpCoords_4km_nearest_conservative(x, lat_src, lon_src, lat_dst, lon_dst, var):
    # lat_src and lon_src are 1-D arrays of source coordinates
    # lat_dst and lon_dst are 2-D arrays of target PRISM coordinates

    source_coords = np.vstack([lat_src, lon_src]).T
    target_coords = np.stack((lat_dst.flatten(), lon_dst.flatten()), axis=0)
    # Prepare the output array (time x number of stations)
    out = np.zeros(shape=(len(x.time.values), lat_dst.shape[0], lat_dst.shape[1])) * np.nan  # 3-D: time, lat, lon
    
    # The fixed distance for the 5x5 box in degrees (from center to outer point)
    distance_between_prism_gridpoints = 0.0416666666666643
    delta = distance_between_prism_gridpoints/5

    ## New approach to create a 5x5 grid of surrounding station coordinates
    lat_offsets = np.array([-2*delta, -delta, 0, delta, 2*delta])
    lon_offsets = np.array([-2*delta, -delta, 0, delta, 2*delta])

    # Create 5x5 coordinates around each target coordinate
    lon_offset_5x5, lat_offset_5x5 = np.meshgrid(lon_offsets, lat_offsets)
    surrounding_lats = [ilat + lat_offset_5x5.flatten() for ilat in target_coords[0]]  
    surrounding_lats = np.array(surrounding_lats)  # Convert to a 2D array  # (n_PRISM_grid, 25)
    surrounding_lons = [ilon + lon_offset_5x5.flatten() for ilon in target_coords[1]]  
    surrounding_lons = np.array(surrounding_lons)  # Convert to a 2D array  # (n_PRISM_grid, 25)

    station_coords = np.stack((surrounding_lats.flatten(), surrounding_lons.flatten()), axis=0)  # (2, 25*n_PRISM_grid)
    # Construct a cKDTree for the 2D lat-lon grid (meteorological data)
    tree = KDTree(source_coords)
    # Query the KDTree for the nearest neighbor indices for each target station (25 surrounding coordinates per station)
    path_neighbors = "/path/to/neighbors_remapping.npy" 

    if not os.path.exists(path_neighbors):
        print(f"Computing and saving neighbors: {path_neighbors}")
        idx_n = [tree.query(t_coords, k=1)[1] for t_coords in station_coords.transpose()] # k=1 for nearest neighbor. 1-25 are neighbors for the first point, 26-50 for the second, etc.
        np.save(path_neighbors, idx_n)
    else:
        idx_n = np.load(path_neighbors) 

    # Loop over all times in the dataset
    for i, t in enumerate(x.time.values):
        # Extract the field at the current time step
        field_at_time = x.sel(time=t).values
        # Extract the interpolated values from the meteorological field for each surrounding point
        interpolated_values = field_at_time[idx_n]
        # Reshape interpolated values to match the 5x5 grid (25 values per station)
        interpolated_values = interpolated_values.reshape((len(target_coords[0]), 25))
        # Compute the average over the 25 points (5x5 box) for each target station
        out[i, :, :] = np.nanmean(interpolated_values, axis=1).reshape(lat_dst.shape)  # Average across the 5x5 grid for each station   

    # Create an xarray dataset with the interpolated data
    
    ds = xr.DataArray(
        out,
        dims=['time', 'latitude', 'longitude'],
        coords={
            'time': x.time.values,
            'latitude': lat_dst[:, 0],
            'longitude': lon_dst[0, :],
        }
    )
    ds.name = var

    return ds



def interpCoords_4km_nearest_conservative_31km(x, lat_src, lon_src, lat_dst, lon_dst, var):
    # lat_src and lon_src are 1-D arrays of source coordinates
    # lat_dst and lon_dst are 2-D arrays of target PRISM coordinates

    source_coords = np.vstack([lat_src, lon_src]).T
    target_coords = np.stack((lat_dst.flatten(), lon_dst.flatten()), axis=0)
    # Prepare the output array (time x number of stations)
    out = np.zeros(shape=(len(x.time.values), lat_dst.shape[0], lat_dst.shape[1])) * np.nan  # 3-D: time, lat, lon
    
    # The fixed distance for the 5x5 box in degrees (from center to outer point)
    distance_between_prism_gridpoints = 0.0416666666666643
    delta = distance_between_prism_gridpoints/5
    ## New approach to create a 5x5 grid of surrounding station coordinates
    lat_offsets = np.array([-2*delta, -delta, 0, delta, 2*delta])
    lon_offsets = np.array([-2*delta, -delta, 0, delta, 2*delta])

    # Create 5x5 coordinates around each target coordinate
    lon_offset_5x5, lat_offset_5x5 = np.meshgrid(lon_offsets, lat_offsets)
    surrounding_lats = [ilat + lat_offset_5x5.flatten() for ilat in target_coords[0]]  
    surrounding_lats = np.array(surrounding_lats)  # Convert to a 2D array  # (n_PRISM_grid, 25)
    surrounding_lons = [ilon + lon_offset_5x5.flatten() for ilon in target_coords[1]]  
    surrounding_lons = np.array(surrounding_lons)  # Convert to a 2D array  # (n_PRISM_grid, 25)

    station_coords = np.stack((surrounding_lats.flatten(), surrounding_lons.flatten()), axis=0)  # (2, 25*n_PRISM_grid)
    # Construct a cKDTree for the 2D lat-lon grid (meteorological data)
    tree = KDTree(source_coords)
    # Query the KDTree for the nearest neighbor indices for each target station (25 surrounding coordinates per station)
    path_neighbors = "/path/to/neighbors_remapping_31km.npy" 

    if not os.path.exists(path_neighbors):
        print(f"Computing and saving neighbors: {path_neighbors}")
        idx_n = [tree.query(t_coords, k=1)[1] for t_coords in station_coords.transpose()] # k=1 for nearest neighbor. 1-25 are neighbors for the first point, 26-50 for the second, etc.
        np.save(path_neighbors, idx_n)
    else:
        idx_n = np.load(path_neighbors)  # Hash table?

    # Loop over all times in the dataset
    for i, t in enumerate(x.time.values):
        # Extract the field at the current time step
        field_at_time = x.sel(time=t).values
        # Extract the interpolated values from the meteorological field for each surrounding point
        interpolated_values = field_at_time[idx_n]
        # Reshape interpolated values to match the 5x5 grid (25 values per station)
        interpolated_values = interpolated_values.reshape((len(target_coords[0]), 25))
        # Compute the average over the 25 points (5x5 box) for each target station
        out[i, :, :] = np.nanmean(interpolated_values, axis=1).reshape(lat_dst.shape)  # Average across the 5x5 grid for each station   

    # Create an xarray dataset with the interpolated data
    
    ds = xr.DataArray(
        out,
        dims=['time', 'latitude', 'longitude'],
        coords={
            'time': x.time.values,
            'latitude': lat_dst[:, 0],
            'longitude': lon_dst[0, :],
        }
    )
    ds.name = var

    return ds
