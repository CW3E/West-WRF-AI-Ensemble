import xarray as xr
import numpy as np
import pandas as pd

def change_time_to_leadtime(x:xr.DataArray, datehour_initial):
    # datehour_initial: 'YYYY-MM-DDTHH'
    initial_time = np.datetime64(datehour_initial) # pd.Timestamp(first_time)
    original_times = x.time.values
    leadtime_intervals = []
    for t in original_times:
        interval_days = (pd.Timestamp(t) - pd.Timestamp(initial_time)).total_seconds() / 86400
        interval_days = int(np.ceil(interval_days))
        # print(interval_hours)
        # Convert hours to datetime64 timedelta format
        leadtime_intervals.append(interval_days)
    # Rename time dimension to leadtime and update coordinates
    x = x.rename({'time': 'leadtime'})
    x = x.assign_coords(leadtime=leadtime_intervals)
    # Add new time dimension with length 1
    x = x.expand_dims({'time': [initial_time]})
    # Set attributes for clarity
    x.coords['leadtime'].attrs['units'] = 'days'
    x.coords['time'].attrs['long_name'] = 'initial time'
    return x
