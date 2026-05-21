import xarray as xr
import numpy as np
import pandas as pd
from cmethods import adjust
import os
import gc
import warnings
warnings.filterwarnings("ignore")


global_rank = int(os.environ["SLURM_ARRAY_TASK_ID"])
epoch = global_rank
version = 'v3'
postfix = "_qm"

start_date = "20231201"  
end_date = "20240229"
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
date_list = date_range.strftime('%Y%m%d').tolist()

# for history period
year1 = 2013 
year2 = 2023

dir_root= "/path/to/workdir/"
dir_prism = "/path/to/PRISM/"

tp_prism = []
for year in range(year1, year2 + 1):
    print(year)
    tp_temp1 = xr.open_dataarray(dir_prism+f"tp_PRISM_2kmDomain_{year-1}.nc")
    tp_temp2 = xr.open_dataarray(dir_prism+f"tp_PRISM_2kmDomain_{year}.nc")
    tp1 = tp_temp1[tp_temp1.time.dt.month.isin([12])]
    tp2 = tp_temp2[tp_temp2.time.dt.month.isin([1, 2])]
    tp_prism.append(xr.concat([tp1, tp2], dim="time"))
    del tp_temp1, tp_temp2
    gc.collect()

tp_prism = xr.concat(tp_prism, dim="time")


lats = np.load(dir_prism+"latsCoords_2kmDomain.npy")
lons = np.load(dir_prism+"lonsCoords_2kmDomain.npy")  # -180-180
lat_min = 30 # lats.min()
lat_max = lats.max()
lon_min = lons.min()
lon_max = lons.max()
lats = lats[(lats>=lat_min) & (lats<=lat_max)]
tp_prism['latitude'] = lats
tp_prism['longitude'] = lons


dir_wwrf_reanalysis = '/path/to/wwrf_reanalysis/'
tp_6km = xr.open_mfdataset([f"{dir_wwrf_reanalysis}wwrf_reanalysis_tp_daily_{year}_DJF_interpPRISM.nc" for year in range(year1, year2+1)], combine='by_coords')['tp'].compute()
tp_6km['latitude'] = tp_prism['latitude'].values
tp_6km['longitude'] = tp_prism['longitude'].values
tp_6km = tp_6km.where(tp_prism.notnull(), np.nan)

members = list(range(0, 51)) 

leadtimes = list(range(0, 7))


# randomly select 25 numbers from 51 numbers (0 - 50)
for member_int in members:
    member = str(member_int).zfill(2)  
    tp_forecast_allinit_1lead = [[] for _ in range(len(leadtimes))]  # to store forecasts of all members for each lead time
    tp_forecast_allinit_1lead_qm = []
    
    for date in date_list: #['20250101', '20250101_00']:
        dir_in = dir_root+f"forecasts/STRETCHED-6km/outputs/ENS/{version}/epoch{epoch}/{date}/"
        filename = f"tp-ENS-{version}-epoch{epoch}-{date}-interpPRISM-{member}-12to12.nc"  # 12UTC to 12UTC

        print("Processing member", member)
        tp_forecast = xr.open_dataarray(dir_in+filename)
        tp_forecast = tp_forecast.where(tp_prism[0].notnull(), np.nan)
        # seperate lead times
        for lead in leadtimes:  # 0 to 12 hours
            tp_forecast_1lead = tp_forecast.isel(time=[lead])
            tp_forecast_allinit_1lead[lead].append(tp_forecast_1lead)
    tp_forecast_allinit_1lead = [xr.concat(tp_forecast_allinit_1lead[lead], dim="time") for lead in leadtimes]  # (n_dates, lat, lon) * 7
    
    for lead in leadtimes:  # 0 to 12 hours
        tp_qm = adjust(
            method="quantile_mapping",
            obs=tp_prism,
            simh=tp_6km, #.rename({"time": "t_simh"}),
            simp=tp_forecast_allinit_1lead[lead],  # (n_dates, lat, lon)
            kind="*",
            input_core_dims={"obs": "time", "simh": "time", "simp": "time"},
            n_quantiles=500,
        )['tp']
        tp_forecast_allinit_1lead_qm.append(tp_qm)
        del tp_qm
        gc.collect()
    
    # output quantile-mapped forecasts for all lead times for each date
    for idate, date in enumerate(date_list):
        filename = f"tp-ENS-{version}-epoch{epoch}-{date}-interpPRISM-{member}-12to12.nc"
        dir_out = dir_root+f"forecasts/STRETCHED-6km/outputs/ENS/{version}{postfix}/epoch{epoch}/{date}/"
        os.makedirs(dir_out, exist_ok=True)
        if os.path.exists(dir_out+filename):
            os.system(f"rm -f {dir_out+filename}")  # remove the file if it exists
        tp_qm_1date = xr.concat([tp_forecast_allinit_1lead_qm[lead][[idate]] for lead in leadtimes], dim="time")  # (7, lat, lon)
        tp_qm_1date = tp_qm_1date.clip(min=0, keep_attrs=True)  # Clip negative values to zero            
        tp_qm_1date.to_netcdf(dir_out+filename)

    del tp_forecast_allinit_1lead, tp_forecast_allinit_1lead_qm
    gc.collect()
