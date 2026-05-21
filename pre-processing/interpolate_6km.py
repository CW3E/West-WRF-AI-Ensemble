import numpy as np
import warnings
warnings.filterwarnings("ignore")
from scipy.interpolate import RegularGridInterpolator


def interpolate_to_6km(xr_data, lon2d, lat2d, method='linear'):
    """
    Interpolate the xarray dataset to the CW3E 6km coordinate system defined by lons2d and lats2d.
    lons should be in the range of 0-360 degrees.
    
    Parameters:
    - xr_data (xarray.DataArray): The input xarray dataset.
    - method (str): The interpolation method to use (default is 'linear'). Options: 'linear', 'nearest', 'cubic'.
    
    Returns:
    - np.array: An array of interpolated values at the given longitude-latitude locations.
    """
    lon2d_new = np.where(lon2d<0, lon2d+360, lon2d)  # Convert to 0-360, to avoid nan at the 180 degree line
    # Convert the input xarray dataset to numpy arrays for easier handling
    lon_grid = xr_data.coords['longitude'].values  # 0-360
    lat_grid = xr_data.coords['latitude'].values  
    # lon_grid = np.where(lon_grid > 180, lon_grid - 360, lon_grid)
    data_values = xr_data.values

    interpolator = RegularGridInterpolator(
        (lat_grid, lon_grid), data_values, method=method, bounds_error=False, fill_value=np.nan
    )

    points = np.vstack([lat2d.ravel(), lon2d_new.ravel()]).T
    interpolated_values = interpolator(points).reshape(lat2d.shape)

    return interpolated_values
