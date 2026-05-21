def postprocess(grid, var):  # , level=None
    # Convert to float 32
    grid=grid.astype('float32')
    ##################################
    ####### COORDINATES ##############
    # Change latitude to CF
    grid.lat.attrs = {
        'long_name': 'Latitude',
        'standard_name': 'latitude',
        'units': 'degrees_north'
        }
    # Change longitude to CF
    grid.lon.attrs = {
        'long_name': 'Longitude',
        'standard_name': 'longitude',
        'units': 'degrees_east'
        }
    # # Change Y to CF
    # grid.y.attrs = {
    #     'long_name': 'y coordinate of projection',
    #     'standard_name': 'projection_y_coordinate',
    #     'axis': 'Y'
    #     }
    # # Change X to CF
    # grid.x.attrs = {
    #     'long_name': 'x coordinate of projection',
    #     'standard_name': 'projection_x_coordinate',
    #     'axis': 'X'
    #     }
    ##################################
    ####### CONSTANT VARIABLES #######
    # z_sfc (Geopotential at surface)
    if var=="z_sfc":
        grid.z_sfc.attrs= {
        'description':    'Geopotential at surface',
        'standard_name':  'geopotential_at_surface',
        'long_name':      'Geopotential at surface',
        'units':          'm2 s-2'}
    # lsm (land-sea mask)
    if var=="lsm":
        grid.lsm.attrs={
        'description':    'Land Mask',
        'standard_name':  'land_mask',
        'long_name':      'Land Mask',
        'notes':          '1=land, 0=water',
        'units':          ''}
    ################################
    ####### SINGLE VARIABLES #######
    vars=['tp','ivt','iwv','2t','d2m','10u','10v','msl','sp','t_sfc']
    # tp (6-hourly accumulated precipitation)
    if var=="tp":
        grid.tp.attrs={
        'standard_name':  'precipitation_amount_6_hours',
        'long_name':      'Accumulated Precipitation Over Past 6 Hours',
        'units':          'mm'}
    # ivtu (zonal component of the integrated vapor transport)
    if var=="ivt_u":
        grid.ivt_u.attrs={
        'description':    'Integrated Vapor Transport Zonal',
        'standard_name':  'integrated_vapor_transport_zonal',
        'long_name':      'Integrated Vapor Transport Zonal',
        'units':          'kg m-1 s-1'}
    # ivtv (meridional component of the integrated vapor transport)
    if var=="ivt_v":
        grid.ivt_v.attrs={
        'description':    'Integrated Vapor Transport Meridional',
        'standard_name':  'integrated_vapor_transport_meridional',
        'long_name':      'Integrated Vapor Transport Meridional',
        'units':          'kg m-1 s-1'}
    # ivt (integrated vapor transport)
    if var=="ivt":
        grid.ivt.attrs={
        'description':    'Integrated Vapor Transport ',
        'standard_name':  'integrated_vapor_transport',
        'long_name':      'Integrated Vapor Transport',
        'units':          'kg m-1 s-1'}
    # iwv (integrated water vapor)
    if var=="iwv":
        grid.iwv.attrs={
        'description':    'Integrated Water Vapor',
        'standard_name':  'integrated_water_vapor',
        'long_name':      'Integrated Water Vapor',
        'units':          'kg m-2'}
    # 2t (2-meter temperature)
    if var=="2t":
        grid["2t"].attrs={
        'description':    'Temperature at 2 m',
        'standard_name':  'air_temperature',
        'long_name':      'Temperature at 2 m',
        'units':          'K'}
    # d2m (2-meter dew-point temperature)
    if var=="d2m":
        grid.d2m.attrs={
        'description':    'Dewpoint Temperature at 2 m',
        'standard_name':  'dew_point_temperature',
        'long_name':      'Dewpoint Temperature at 2 m',
        'units':          'K'}
    # 10u (10-meters zonal wind velocity)
    if var=="10u":
        grid["10u"].attrs={
        'description':    'u-Component of Wind at 10 m (grid)',
        'standard_name':  'eastward_wind',
        'long_name':      'u-Component of Wind at 10 m (grid)',
        'units':          'm s-1'}
    # 10v (10-meters meridional wind velocity)
    if var=="10v":
        grid["10v"].attrs={
        'description':    'v-Component of Wind at 10 m (grid)',
        'standard_name':  'northward_wind',
        'long_name':      'v-Component of Wind at 10 m (grid)',
        'units':          'm s-1'}
    # msl (mean sea level pressure)
    if var=="msl":
        grid.msl.attrs={
        'description':    'Sea-Level Pressure',
        'standard_name':  'air_pressure_at_sea_level',
        'long_name':      'Sea-Level Pressure',
        'units':          'Pa'}
    # sp (surface pressure)
    if var=="sp":
        grid.sp.attrs={
        'description':    'Pressure at the Surface',
        'standard_name':  'surface_air_pressure',
        'long_name':      'Pressure at the Surface',
        'units':          'Pa'}
    # t_sfc (temperature at the surface: skin-temperature over land and sea surface temperature over the ocean)    
    if var=="t_sfc":
        grid.t_sfc.attrs={
        'description':    'Temperature at the Surface',
        'standard_name':  'surface_temperature',
        'long_name':      'Temperature at the Surface',
        'units':          'K'}
    # tcc (total cloud fraction)
    if var=="tcc":
        grid.tcc.attrs={
        'description':    'Total cloud cover',
        'standard_name':  'cloud_area_fraction',
        'long_name':      'Total cloud cover',
        'units':          '(0 - 1)'}
    # tisr (TOA incident short-wave (solar) radiation)
    if var=="tisr":
        grid.tisr.attrs={
        'description':    'TOA incident short-wave (solar) radiation',
        'standard_name':  'unknown',
        'long_name':      'TOA incident short-wave (solar) radiation',
        'units':          'J m**-2'}
    ##################################    

    ####### PRESSURE VARIABLES #######
    # z (geopotential)
    if var=="z":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'Geopotential',
        'standard_name':  'geopotential',
        'long_name':      'Geopotential',
        'units':          'm2 s-2',
        # 'level':          str(level)+' hPa', 
        }
    # t (temperature)
    if var=="t":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'Temperature',
        'standard_name':  'air_temperature',
        'long_name':      'Temperature',
        'units':          'K',
        # 'level':          str(level)+' hPa', 
        }
    # q (specific humidity)
    if var=="q":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'Specific Humidity',
        'standard_name':  'specific_humidity',
        'long_name':      'Specific Humidity',
        'units':          'kg kg-1',
        # 'level':          str(level)+' hPa', 
        }
    # u (zonal wind velocity)
    if var=="u":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'u-Component of Wind (Earth)',
        'standard_name':  'eastward_wind',
        'long_name':      'u-Component of Wind (Earth)',
        'units':          'm s-1',
        # 'level':          str(level)+' hPa',
        }
    # v (meridional wind velocity)
    if var=="v":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'v-Component of Wind (Earth)',
        'standard_name':  'northward_wind',
        'long_name':      'v-Component of Wind (Earth)',
        'units':          'm s-1',
        # 'level':          str(level)+' hPa', 
        }
    # w (vertical wind velocity)
    if var=="w":
        var_level=var#+"_"+str(level)
        grid[var_level].attrs={
        'description':    'Omega',
        'standard_name':  'vertical_wind',
        'long_name':      'Omega',
        'units':          'Pa s-1',
        # 'level':          str(level)+' hPa',
        }
    ### Return object
    return grid

