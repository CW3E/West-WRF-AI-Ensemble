import numpy as np
import xarray as xr
import sys
workdir = '/path/to/your/workdir/'  # change to your workdir
from postprocess_ens import postprocess
dir_era5 = '/path/to/your/ERA5-31km/'
dir_ens = '/path/to/your/ens_data/'
dir_ens2 = '/path/to/your/template_data/'
from interpolate_31km import interpolate_to_31km
from interpolate_6km import interpolate_to_6km
import os
import gc
import warnings
warnings.filterwarnings("ignore")
from multiprocessing import Pool

import datetime
start_time = datetime.datetime.now()

date = sys.argv[1]  # yyyy-mm-dd
yyyymmdd = date.replace('-', '')

def interpolate_sfc_31km(x, var_out, date_str, lons2d_31km, lats2d_31km):
    ## Interpolate from lat-lon (0.1-degree) to N320 grid: 
    values = interpolate_to_31km(x, dir_era5, method='linear')  

    ## Reshape to 2D array
    ## Place the vector of values in a xarray object (Why reshape? 542080/640=847)
    ## To fake a 2D array to skip an error of Anemoi. It has no physical meaning. Anemoi only supports 2D spatial dimensions.
    values = np.reshape(values, lats2d_31km.shape) # Reshape vector to x,y
    x31 = xr.Dataset(data_vars={var_out: (["y","x"], values)},
                        coords={
                        "y": np.arange(lats2d_31km.shape[0]), # 640
                        "x": np.arange(lats2d_31km.shape[1]), # 847                  
                        "lat": (["y","x"], lats2d_31km),
                        "lon": (["y","x"], lons2d_31km)})
    x31 = x31.assign_coords({"time": np.datetime64(f'{date_str}:00:00')}) 
    x31 = x31.expand_dims({"time":1})
    ## Add metadata to the coordinates and variables following CF convention, convert to float16
    x31 = postprocess(grid=x31, var=var_out)

    return x31


def interpolate_pl_31km(x, var_out, date_str, lons2d_31km, lats2d_31km, levels):
    ## loop over levels
    values_levels = []
    for level in levels:
        xi_lev = x.sel(level=level)
    
        ## Interpolate from lat-lon (0.1-degree) to N320 grid: 
        values = interpolate_to_31km(xi_lev, dir_era5, method='linear')  

        ## Reshape to 2D array
        values = np.reshape(values, lats2d_31km.shape) # Reshape vector to x,y
        values_levels.append(values)
    values_levels = np.stack(values_levels, axis=0) # Stack the levels
    
    x31 = xr.Dataset(data_vars={var_out: (["level", "y","x"], values_levels)},
                        coords={
                        "level": levels,
                        "y": np.arange(lats2d_31km.shape[0]), # 640
                        "x": np.arange(lats2d_31km.shape[1]), # 847                  
                        "lat": (["y","x"], lats2d_31km),
                        "lon": (["y","x"], lons2d_31km)})
    x31 = x31.assign_coords({"time": np.datetime64(f'{date_str}:00:00')}) 
    x31 = x31.expand_dims({"time":1})
    ## Add metadata to the coordinates and variables following CF convention, convert to float16
    x31 = postprocess(grid=x31, var=var_out)

    return x31


def get_static_31km(x, var_out, date_str, lons2d_31km, lats2d_31km):
    # For z_sfc and lsm
    x31 = xr.Dataset(data_vars={var_out: (["y","x"], x[var_out][0].values)},
                    coords={
                    "y": np.arange(lats2d_31km.shape[0]), # 640
                    "x": np.arange(lats2d_31km.shape[1]), # 847                  
                    "lat": (["y","x"], lats2d_31km),
                    "lon": (["y","x"], lons2d_31km)})
    x31 = x31.assign_coords(time=np.datetime64(f'{date_str}:00:00'))
    x31 = x31.expand_dims({"time":1})
    x31 = postprocess(grid=x31, var=var_out)

    return x31


def interpolate_sfc_6km(x, var_out, date_str, lons2d_6km, lats2d_6km):
    values = interpolate_to_6km(x, lons2d_6km, lats2d_6km, method='linear') 
    # print(np.isnan(values).sum())
    x6 = xr.Dataset(data_vars={var_out: (["y","x"], values)},
                    coords={
                        "y": np.arange(5, lats2d_6km.shape[0]+5), # 960, +5 is to match the WWRF grid
                        "x": np.arange(5, lats2d_6km.shape[1]+5), # 1379                   
                        "lat": (["y","x"], lats2d_6km),
                        "lon": (["y","x"], lons2d_6km)})
    x6 = x6.assign_coords({"time": np.datetime64(f'{date_str}:00:00')}) 
    x6 = x6.expand_dims({"time":1})
    ## Add metadata to the coordinates and variables following CF convention, convert to float16
    x6 = postprocess(grid=x6, var=var_out)

    return x6


def interpolate_pl_6km(x, var_out, date_str, lons2d_6km, lats2d_6km, levels):
    values_levels = []
    for level in levels:
        xi_lev = x.sel(level=level)
        ## Interpolate from lat-lon (0.1-degree) to 6km grid: 
        values = interpolate_to_6km(xi_lev, lons2d_6km, lats2d_6km, method='linear') 
        # print(np.isnan(values).sum())
        values_levels.append(values)
    values_levels = np.stack(values_levels, axis=0) # Stack the levels
    
    x6 = xr.Dataset(data_vars={var_out: (["level", "y","x"], values_levels)},
                    coords={
                        "level": levels,
                        "y": np.arange(5, lats2d_6km.shape[0]+5), # 960, +5 is to match the WWRF grid
                        "x": np.arange(5, lats2d_6km.shape[1]+5), # 1379                      
                        "lat": (["y","x"], lats2d_6km),
                        "lon": (["y","x"], lons2d_6km)})
    x6 = x6.assign_coords({"time": np.datetime64(f'{date_str}:00:00')}) 
    x6 = x6.expand_dims({"time":1})
    ## Add metadata to the coordinates and variables following CF convention, convert to float16
    x6 = postprocess(grid=x6, var=var_out)

    return x6


def get_static_6km(x, var_out, date_str, lons2d_6km, lats2d_6km):
    x6 = xr.Dataset(data_vars={var_out: (["y","x"], x[var_out][0].values)},
                    coords={
                        "y": np.arange(5, lats2d_6km.shape[0]+5), # 960, +5 is to match the WWRF grid
                        "x": np.arange(5, lats2d_6km.shape[1]+5), # 1379                     
                        "lat": (["y","x"], lats2d_6km),
                        "lon": (["y","x"], lons2d_6km)})
    x6 = x6.assign_coords(time=np.datetime64(f'{date_str}:00:00'))
    x6 = x6.expand_dims({"time":1})
    x6 = postprocess(grid=x6, var=var_out)
    return x6

path_output = workdir

variables_out_sl = ['tp','ivt_u','ivt_v','iwv', '2t', 'd2m','10u','10v','msl','sp','t_sfc']  
variables_in_sl  = ['tp','viwve','viwvn','tcwv','t2m','d2m','u10','v10','msl','sp','t_sfc']
variables_out_static = ["lsm", "z_sfc"]
variables_in_static  = ["lsm", "z_sfc"]
variables_out_pl = ["z", "t", "q", "u", "v"]
variables_in_pl  = ["z", "t", "q", "u", "v"]
levels = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50]


lats_31km = np.load(f"{dir_era5}/N320-coords/lats_n320.npy")
lons_31km = np.load(f"{dir_era5}/N320-coords/lons_n320.npy")  # 0-360
lons_31km = np.where(lons_31km > 180, lons_31km - 360, lons_31km)  # Two reasons: 1) avoid errors in Amenoi, 2) to be consistent with the the regional dataset

lats2d_31km = np.reshape(lats_31km, (640,847)) # Reshape vector to x,y. There are 640 latitude circles in N320.
lons2d_31km = np.reshape(lons_31km, (640,847)) # Reshape vector to x,y. There are 640 latitude circles in N320.

template_6km = xr.open_dataset(workdir+f"netcdf/template/lsm_6km_template.nc")  
lats2d_6km = template_6km['lat'].values  # (960, 1379)
lons2d_6km = template_6km['lon'].values  # -180 to 180  
del template_6km
gc.collect()

comp = dict(zlib=True, complevel=5)  # compression settings for netCDF4 output

def process(imem):
    
    if imem == 0:

    ###########################
    #---- Control run
    ###########################

        ds_pl = xr.open_dataset(dir_ens+f"{date}_00/oper_ctl_pl_{date}_0000.grib", engine='cfgrib', 
                                backend_kwargs={"indexpath": ""})
        # init_date = ds_pl.time  
        
        dates = ds_pl.valid_time  # 0 and 6 hours
        dates = dates.dt.strftime("%Y-%m-%dT%H")[:2].values
        ds_pl = ds_pl.rename({"isobaricInhPa":"level"})  
        for ivar, (var_out, var_in) in enumerate(zip(variables_out_pl, variables_in_pl)):
            ds_pl = ds_pl.rename({var_in:var_out}) 

        ds_sl1 = xr.open_dataset(dir_ens+f"{date}_00/oper_ctl_sfc_{date}_0000.grib", engine='cfgrib', 
                                 backend_kwargs={'filter_by_keys': {'edition': 1}, "indexpath": ""})  # other variables
        ds_sl2 = xr.open_dataset(dir_ens+f"{date}_00/oper_ctl_sfc_{date}_0000.grib", engine='cfgrib', 
                                 backend_kwargs={'filter_by_keys': {'edition': 2}, "indexpath": ""})  # viwve, viwvn
        # ds_sl1 = ds_sl1.isel(step=[0, 6])
        # ds_sl2 = ds_sl2.isel(step=[0, 6])

        # Combine SKT and SST
        ds_lsm = xr.open_dataset(dir_ens2+f"lsm_template.grib", engine='cfgrib', backend_kwargs={"indexpath": ""})
        lsm = ds_lsm['lsm'] # no time dimension
        t_sfc = xr.where(lsm == 0, ds_sl1['sst'], ds_sl1['skt'])  # replace skt with sst over ocean
        t_sfc = t_sfc.transpose('step', 'latitude', 'longitude')
        t_sfc.name = 't_sfc'
        ds_sl1 = ds_sl1.drop_vars(['sst', 'skt'])
        # ds_sl1 = ds_sl1.assign(t_sfc=t_sfc)
        ds_sl1['t_sfc'] = t_sfc

        ds_sl = xr.merge([ds_sl1, ds_sl2])
        del ds_sl1, ds_sl2
        gc.collect()

        assert all(ds_sl['valid_time'].dt.strftime("%Y-%m-%dT%H").values==dates)

        for ivar, (var_out, var_in) in enumerate(zip(variables_out_sl, variables_in_sl)):
            ds_sl = ds_sl.rename({var_in:var_out}) 


        ## Global 31km

        ### single level variables

        vars_sl_31 = []
        for ivar, var_out in enumerate(variables_out_sl):
            x = ds_sl[var_out]
            ## Loop over the two steps
            x31_2steps = []
            for itime, time_str in enumerate(dates):  # new
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime)
                x31 = interpolate_sfc_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km)
                x31_2steps.append(x31)
                xi.close()
                x31.close()
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_sl_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_sl_31 = xr.merge(vars_sl_31)

        ### Static variables

        vars_static_31 = []
        for ivar, var_out in enumerate(variables_out_static):
            x31_2steps = []
            for itime, time_str in enumerate(dates):
                print(f"{var_out} - {time_str}")
                xi = xr.open_dataset(workdir+f"netcdf/template/{var_out}_31km_template.nc")
                x31 = get_static_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km)
                x31_2steps.append(x31)
                x31.close()
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_static_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the static variables
        vars_static_31 = xr.merge(vars_static_31)

        ### Pressure level variables

        vars_pl_31 = []
        for ivar, var_out in enumerate(variables_out_pl):
            x = ds_pl[var_out]
            ## Loop over the two steps
            x31_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime)
                x31 = interpolate_pl_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km, levels)
                x31_2steps.append(x31)
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_pl_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_pl_31 = xr.merge(vars_pl_31)

        vars_all_31 = xr.merge([vars_static_31, vars_sl_31, vars_pl_31])
        vars_all_31 = vars_all_31.assign_coords(number=np.array([0]))  # number==0 (new)
        vars_all_31 = vars_all_31.transpose('time', 'number', 'level', 'y', 'x')
        encoding = {var: comp for var in vars_all_31.data_vars}
        vars_all_31.to_netcdf(f'{path_output}/netcdf/{date}_06/ENS_31km_{yyyymmdd}_0.nc', encoding=encoding)

        del vars_all_31, vars_static_31, vars_sl_31, vars_pl_31
        gc.collect()


        ## CW3E 6km

        ### single level variables 

        vars_sl_6 = []
        for ivar, var_out in enumerate(variables_out_sl):
            x = ds_sl[var_out]
            ## Loop over the two steps
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime).loc[70:0, 150:295]        
                ## Interpolate from lat-lon (0.1-degree) to 6km grid: 
                x6 = interpolate_sfc_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km)
                x6_2steps.append(x6)
                xi.close()
                x6.close()
                del xi, x6
                gc.collect()
            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_sl_6.append(x6_2steps)
            del x6_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_sl_6 = xr.merge(vars_sl_6)

        ### Static variables

        vars_static_6 = []
        for ivar, var_out in enumerate(variables_out_static):
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                print(f"{var_out} - {time_str}")
                xi = xr.open_dataset(workdir+f"netcdf/template/{var_out}_6km_template.nc")
                x6 = get_static_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km)
                x6_2steps.append(x6)
                x6.close()
                del xi, x6
                gc.collect()
            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_static_6.append(x6_2steps)
            del x6_2steps
            gc.collect()

        ## Concatenate the static variables
        vars_static_6 = xr.merge(vars_static_6)

        ### Pressure level variables

        vars_pl_6 = []
        for ivar, var_out in enumerate(variables_out_pl):
            x = ds_pl[var_out]
            ## Loop over the two steps
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime).loc[:, 70:0, 150:295]
                x6 = interpolate_pl_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km, levels)
                x6_2steps.append(x6)
                del xi, x6
                gc.collect()

            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_pl_6.append(x6_2steps)
            del x6_2steps
            gc.collect()
            
        ## Concatenate the single-level variables
        vars_pl_6 = xr.merge(vars_pl_6)

        ### combine all variables and output
        vars_all_6 = xr.merge([vars_static_6, vars_sl_6, vars_pl_6])
        vars_all_6 = vars_all_6.assign_coords(number=np.array([0]))  # number==0 (new)
        vars_all_6 = vars_all_6.transpose('time', 'number', 'level', 'y', 'x')
        encoding = {var: comp for var in vars_all_6.data_vars}
        vars_all_6.to_netcdf(f'{path_output}/netcdf/{date}_06/ENS_6km_{yyyymmdd}_0.nc', encoding=encoding)

        del vars_all_6, vars_static_6, vars_sl_6, vars_pl_6
        gc.collect()

    else:

    ###########################
    #---- Perturbed run
    ###########################

        ds_sl1 = xr.open_dataset(dir_ens+f"{date}_00/oper_per_sfc_{date}_0000.grib", engine='cfgrib', 
                                 backend_kwargs={'filter_by_keys': {'edition': 1}, "indexpath": ""})  # other variables
        ds_sl2 = xr.open_dataset(dir_ens+f"{date}_00/oper_per_sfc_{date}_0000.grib", engine='cfgrib', 
                                 backend_kwargs={'filter_by_keys': {'edition': 2}, "indexpath": ""})  # viwve, viwvn

        # Combine SKT and SST
        ds_lsm = xr.open_dataset(dir_ens2+"lsm_template.grib", engine='cfgrib', backend_kwargs={"indexpath": ""})
        lsm = ds_lsm['lsm'] # no time dimension
        print(ds_sl1['sst'].dims)
        t_sfc = xr.where(lsm == 0, ds_sl1['sst'], ds_sl1['skt'])  # replace skt with sst over ocean
        t_sfc = t_sfc.transpose('number', 'step', 'latitude', 'longitude')
        t_sfc.name = 't_sfc'
        ds_sl1 = ds_sl1.drop_vars(['sst', 'skt'])
        # ds_sl1 = ds_sl1.assign(t_sfc=t_sfc)
        ds_sl1['t_sfc'] = t_sfc

        ds_sl = xr.merge([ds_sl1, ds_sl2])
        del ds_sl1, ds_sl2
        gc.collect()

        # assert all(ds_sl['valid_time'].dt.strftime("%Y-%m-%dT%H").values==dates)

        for ivar, (var_out, var_in) in enumerate(zip(variables_out_sl, variables_in_sl)):
            ds_sl = ds_sl.rename({var_in:var_out}) 


        ds_pl1 = xr.open_dataset(dir_ens+f"{date}_00/oper_per_pl_{date}_0000_0.grib", engine='cfgrib', backend_kwargs={"indexpath": ""})
        ds_pl2 = xr.open_dataset(dir_ens+f"{date}_00/oper_per_pl_{date}_0000_6.grib", engine='cfgrib', backend_kwargs={"indexpath": ""})
        # init_date = ds_pl.time  
        date1 = ds_pl1.valid_time  # 0 hour
        date2 = ds_pl2.valid_time  # 6 hours
        dates = xr.concat([date1, date2], dim='step')  # Combine the two times
        print(dates)
        dates = dates.dt.strftime("%Y-%m-%dT%H").values #[date.dt.strftime("%Y-%m-%dT%H").values for date in [date1, date2]]  # Get the string representation of the dates

        ds_pl1 = ds_pl1.rename({"isobaricInhPa":"level"})  
        ds_pl2 = ds_pl2.rename({"isobaricInhPa":"level"})  
        for ivar, (var_out, var_in) in enumerate(zip(variables_out_pl, variables_in_pl)):
            ds_pl1 = ds_pl1.rename({var_in:var_out}) 
            ds_pl2 = ds_pl2.rename({var_in:var_out}) 

        ## Global 31km

        # for imem in range(1, 2):  # Loop over the ensemble members
            
        ### single level variables
        vars_sl_31 = []

        for ivar, var_out in enumerate(variables_out_sl):
            x = ds_sl[var_out][imem-1]
            ## Loop over the two steps
            x31_2steps = []
            for itime, time_str in enumerate(dates):  # new
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime)
                # print(xi['valid_time'].values)
                x31 = interpolate_sfc_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km)
                x31_2steps.append(x31)
                xi.close()
                x31.close()
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_sl_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_sl_31 = xr.merge(vars_sl_31)

        ### Static variables

        vars_static_31 = []
        for ivar, var_out in enumerate(variables_out_static):
            x31_2steps = []
            for itime, time_str in enumerate(dates):
                print(f"{var_out} - {time_str}")
                xi = xr.open_dataset(workdir+f"netcdf/template/{var_out}_31km_template.nc")
                x31 = get_static_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km)
                x31_2steps.append(x31)
                x31.close()
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_static_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the static variables
        vars_static_31 = xr.merge(vars_static_31)

        ### Pressure level variables

        vars_pl_31 = []
        for ivar, var_out in enumerate(variables_out_pl):
            # x = ds_pl[var_out]
            ## Loop over the two steps
            x31_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                if itime == 0:
                    # x = ds_pl1[var_out][imem-1]
                    xi = ds_pl1[var_out][imem-1]
                else:
                    xi = ds_pl2[var_out][imem-1]
                x31 = interpolate_pl_31km(xi, var_out, time_str, lons2d_31km, lats2d_31km, levels)
                x31_2steps.append(x31)
                del xi, x31
                gc.collect()
            ## Concatenate the two steps
            x31_2steps = xr.concat(x31_2steps, dim="time")
            vars_pl_31.append(x31_2steps)
            del x31_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_pl_31 = xr.merge(vars_pl_31)

        vars_all_31 = xr.merge([vars_static_31, vars_sl_31, vars_pl_31])
        vars_all_31 = vars_all_31.assign_coords(number=np.array([imem]))  # number==0 (new)
        vars_all_31 = vars_all_31.transpose('time', 'number', 'level', 'y', 'x')
        encoding = {var: comp for var in vars_all_31.data_vars}
        vars_all_31.to_netcdf(f'{path_output}/netcdf/{date}_06/ENS_31km_{yyyymmdd}_{imem}.nc', encoding=encoding)

        del vars_all_31, vars_static_31, vars_sl_31, vars_pl_31
        gc.collect()


        ## CW3E 6km

            
        ### single level variables 
        vars_sl_6 = []
        for ivar, var_out in enumerate(variables_out_sl):
            x = ds_sl[var_out][imem-1]
            ## Loop over the two steps
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                xi = x.isel(step=itime).loc[70:0, 150:295]        
                ## Interpolate from lat-lon (0.1-degree) to 6km grid: 
                x6 = interpolate_sfc_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km)
                x6_2steps.append(x6)
                xi.close()
                x6.close()
                del xi, x6
                gc.collect()
            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_sl_6.append(x6_2steps)
            del x6_2steps
            gc.collect()
        ## Concatenate the single-level variables
        vars_sl_6 = xr.merge(vars_sl_6)

        ### Static variables

        vars_static_6 = []
        for ivar, var_out in enumerate(variables_out_static):
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                print(f"{var_out} - {time_str}")
                xi = xr.open_dataset(workdir+f"netcdf/template/{var_out}_6km_template.nc")
                x6 = get_static_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km)
                x6_2steps.append(x6)
                x6.close()
                del xi, x6
                gc.collect()
            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_static_6.append(x6_2steps)
            del x6_2steps
            gc.collect()

        ## Concatenate the static variables
        vars_static_6 = xr.merge(vars_static_6)

        ### Pressure level variables

        vars_pl_6 = []
        for ivar, var_out in enumerate(variables_out_pl):
            # x = ds_pl[var_out]
            ## Loop over the two steps
            x6_2steps = []
            for itime, time_str in enumerate(dates):
                ## Select date of the year
                print(f"{var_out} - {time_str}")
                if itime == 0:
                    # x = ds_pl1[var_out][imem-1]
                    xi = ds_pl1[var_out][imem-1].loc[:, 70:0, 150:295]
                else:
                    xi = ds_pl2[var_out][imem-1].loc[:, 70:0, 150:295]
                x6 = interpolate_pl_6km(xi, var_out, time_str, lons2d_6km, lats2d_6km, levels)
                x6_2steps.append(x6)
                del xi, x6
                gc.collect()

            ## Concatenate the two steps
            x6_2steps = xr.concat(x6_2steps, dim="time")
            vars_pl_6.append(x6_2steps)
            del x6_2steps
            gc.collect()
            
        ## Concatenate the single-level variables
        vars_pl_6 = xr.merge(vars_pl_6)

        ### combine all variables and output
        vars_all_6 = xr.merge([vars_static_6, vars_sl_6, vars_pl_6])
        vars_all_6 = vars_all_6.assign_coords(number=np.array([imem]))  # number==0 (new)
        vars_all_6 = vars_all_6.transpose('time', 'number', 'level', 'y', 'x')
        encoding = {var: comp for var in vars_all_6.data_vars}
        vars_all_6.to_netcdf(f'{path_output}/netcdf/{date}_06/ENS_6km_{yyyymmdd}_{imem}.nc', encoding=encoding)

        del vars_all_6, vars_static_6, vars_sl_6, vars_pl_6
        gc.collect()


member_groups = [list(range(i*4, i*4+4)) for i in range(0, 13, 1)]
member_groups[-1] = member_groups[-1][:-1]

global_rank=int(os.environ["SLURM_ARRAY_TASK_ID"])
members = member_groups[global_rank]
print(members)
with Pool(processes=4) as pool:
    # results = pool.map(process, members)
    for imem in members:
        pool.apply_async(process, args=(imem,))

    pool.close()     
    pool.join()      

end_time = datetime.datetime.now() # time.time()
print(f"Running time: {end_time - start_time}")
