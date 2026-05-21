import xarray as xr
import numpy as np
import os
import sys
dir_root= "/path/to/workdir/"
sys.path.append(dir_root+'utils/')
from tp_6h_to_daily import tp_6h_to_daily_12to12
from interpCoords_4km_conservative import interpCoords_4km_nearest_conservative_31km
from datetime import datetime, timedelta
import pandas as pd
import gc

start_time = datetime.now()

global_rank = int(os.environ["SLURM_ARRAY_TASK_ID"])
members = list(range(0, 51))  
versions = ['A2'] 

epochs = [80, 82, 84, 86, 88, 90]
epoch = epochs[global_rank]
start_date = "YYYYMMDD"  # to be changed
end_date = "YYYYMMDD"  # to be changed
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
date_list = date_range.strftime('%Y%m%d').tolist()

## PRISM
dir_prism = "/path/to/PRISM/"
lats = np.load(dir_prism+"latsCoords_2kmDomain.npy")
lons = np.load(dir_prism+"lonsCoords_2kmDomain.npy")  # -180-180
lat_min = 30 # lats.min()
lat_max = lats.max()
lon_min = lons.min()
lon_max = lons.max()
lats = lats[(lats>=lat_min) & (lats<=lat_max)]
lon_grid, lat_grid = np.meshgrid(lons, lats)  # to be interpolated to


for date in date_list: 
    for version in versions:
        dir_out = dir_root+f"forecasts/GLOBAL-31km/outputs/ENS/{version}/epoch{epoch}/{date}/"
        dir_in = f"/path/to/original_outputs/{version}/{date}/epoch{epoch}/"
        os.makedirs(dir_out, exist_ok=True) 

        print(f"Interpolating tp for A2-{version}-epoch{epoch} initialized on {date}.")

        for member in members:
            member = str(member).zfill(2)   
            print("Processing member", member)
            filename = f"ENS-epoch{epoch}-{date}-subset-{member}.nc"
            filename_interp = f"tp-ENS-{version}-epoch{epoch}-{date}-interpPRISM-{member}-12to12.nc"  # 12UTC to 12UTC
            ds = xr.open_dataset(dir_in+filename)
            lat_ai = ds['latitude'].values
            lon_ai = ds['longitude'].values
                
            x_forecast = ds['tp']
            x_forecast = tp_6h_to_daily_12to12(x_forecast)  # 12UTC to 12UTC
            xtime_daily = x_forecast['time']  
            assert xtime_daily.shape[0] == 7 
            tp_interp = interpCoords_4km_nearest_conservative_31km(x_forecast, lat_ai, lon_ai, lat_grid, lon_grid, var='tp')
            tp_interp = tp_interp.clip(min=0, keep_attrs=True)  

            if os.path.exists(dir_out+filename_interp):
                os.system(f"rm -f {dir_out+filename_interp}")  # remove the file if it exists
            tp_interp.to_netcdf(dir_out+filename_interp)

            del ds, x_forecast
            gc.collect()

end_time = datetime.now() 
print(f"Running time: {end_time - start_time}")
