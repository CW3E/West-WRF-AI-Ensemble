import numpy as np
import xarray as xr


def tp_6h_to_daily_12to12(x):
    """Convert 6-hourly precipitation to daily. (6, 12, 18, 0 | 6, 12, 18, 0 |, ...)"""
    x = x.where(x<9999, np.nan)  # Mask the first time step (1e36)
    if x.time.dt.hour.values[0] == 0:
        x1 = x[3:]
    elif x.time.dt.hour.values[0] == 6:
        x1 = x[2:] 
    elif x.time.dt.hour.values[0] == 12:
        x1 = x[1:]  
    elif x.time.dt.hour.values[0] == 18:
        x1 = x
    else:
        raise ValueError("Unexpected time value: {}".format(x.time.dt.hour.values[0]))
    # print("number of negative 6h values", (x1 < 0).sum().values)
    x_daily = x1.coarsen(time=4, boundary='trim').sum()
    # print(x_daily.time)
    x_daily['time'] = x_daily.time.dt.floor('D')
    return x_daily
