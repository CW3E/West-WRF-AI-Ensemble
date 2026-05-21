import numpy as np
import warnings
warnings.filterwarnings("ignore")
from scipy.interpolate import RegularGridInterpolator


def interpolate_to_31km(xr_data, workdir, method='linear'):
    lats = np.load(f"{workdir}/N320-coords/lats_n320.npy")
    lons = np.load(f"{workdir}/N320-coords/lons_n320.npy")  # 0-360

    lat_grid = xr_data.coords['latitude'].values
    lon_grid = xr_data.coords['longitude'].values
    data_values = xr_data.values

    interpolator = RegularGridInterpolator(
        (lat_grid, lon_grid), data_values, method=method, bounds_error=False, fill_value=np.nan
    )

    # create target points [[lat1, lon1], [lat2, lon2], ...]
    target_points = np.column_stack((lats, lons))  # lat is the first column

    interpolated_values = interpolator(target_points)
    return interpolated_values
