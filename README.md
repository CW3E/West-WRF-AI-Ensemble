# West-WRF-AI-Ensemble
This repository contains the scripts that generate the AI-based large ensemble presented in the manuscript titled "High-resolution large ensemble for extreme precipitation forecasting with multiple AI weather models". Provided code covers data pre-processing, AI model inference, and AI forecast post-processing. The following are the specific contents of each folder:

* pre-processing: script to regrid EPS initial conditions in GRIB format to the NetCDF-formatted N320 grid (~ 31 km) and the West-WRF domain (6 km), and subsequently convert these NetCDF files into Zarr format.
* inference: scripts to generate forecasts using West-WRF AI models and global AI models.
* pre-processing: Scripts to calculate 24-hour accumulated precipitation based on 6-hourly forecasts, and to regrid it to the PRISM grid (~4 km) using budget-conserving interpolation.
