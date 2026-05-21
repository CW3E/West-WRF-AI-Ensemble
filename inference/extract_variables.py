import xarray as xr
import numpy as np
import os
import sys

version = str(sys.argv[1])
epoch = int(sys.argv[2])
date = sys.argv[3]
member = sys.argv[4]

dir_output = f"/path/to/output/"
os.chdir(dir_output)

variables = '2t,ivt_u,ivt_v,tp,latitude,longitude'   # ,iwv,z_500
variables = variables.split(',')

# for member in members:
# member = str(member).zfill(2)
filename = f"ENS-{version}-epoch{epoch}-{date}-{member}.nc"
filename_subset = f"ENS-{version}-epoch{epoch}-{date}-subset-{member}.nc"
# os.system(f"cdo selname,{variables} {filename} {filename_subset}")
# filename_subset = f"ENS-{version}-epoch{epoch}-{date}-subset-interp-{member}.nc"
ds = xr.open_dataset(filename)
ds_subset = ds[variables]

# ivt = np.sqrt(ds_subset['ivt_u']**2 + ds_subset['ivt_v']**2)
# ivt.name = 'ivt'
# # ivt.attrs = {
# #     'description':    'Integrated Vapor Transport ',
# #     'standard_name':  'integrated_vapor_transport',
# #     'long_name':      'Integrated Vapor Transport',
# #     'units':          'kg m-1 s-1'}
# ds_subset['ivt'] = ivt

comp = dict(zlib=True, complevel=5)
encoding = {var: comp for var in ds_subset.data_vars}

ds_subset.to_netcdf(filename_subset, format='NETCDF4', encoding=encoding)
# print(f"Processed {filename} to {filename_subset}")

# filename_subset = f"ENS-{version}-epoch{epoch}-{date}-subset-{member}.nc"
# os.system(f"cdo selname,{variables} {filename} {filename_subset}")
 