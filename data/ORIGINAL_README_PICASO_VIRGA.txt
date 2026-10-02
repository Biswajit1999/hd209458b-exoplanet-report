Files for the picaso/Virga grid-retrievals from "Magnesium Silicate Clouds in the Atmosphere of HD 209458b from a Rule-Based Tree-Structured Data Reduction", Chubb & Grant et al. 2026
mg2sio4_full_median_and_max_logl_picaso_virga.nc - for the Mg2SiO4 atmosphere
mgxsioy_full_median_and_max_logl_picaso_virga.nc - for the combined Mg2SiO4/MgSiO3 atmosphere


NetCDF Data File containing full model outputs of the best fit, 1sigma, and 3sigma model fitted to the transmission spectrum results generated using the ExoTiC-MIRI reduction and fitting pipeline for JWST/MIRI LRS observations of HD209458b. Models were run using the PICASO 3.0 climate code and Virga 1.0 cloud code and include the full chemistry, temperature-pressure profiles, and cloud opacities for each cloud run.

The file format is NetCDF4 and can be read using Python packages such as xarray or netCDF4.
Example:

import xarray as xr
ds = xr.open_dataset("mg2sio4_full_median_and_max_logl.nc")
print(ds)
