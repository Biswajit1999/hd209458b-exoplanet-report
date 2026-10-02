# Data source

The files below were downloaded, unmodified, from Zenodo
record **10.5281/zenodo.20089901** ("Supplementary Information: Magnesium
Silicate Clouds in the Atmosphere of HD 209458b from a Rule-Based
Tree-Structured Data Reduction", Chubb & Grant et al. 2026), file
`hd209_ExoTiC_tree_four_leaf_spectra.txt` — the data behind Figure 4 of the
paper. The two NetCDF files are the publication's PICASO 3.0 + Virga 1.0
posterior model products for Mg2SiO4 and mixed Mg2SiO4/MgSiO3 cloud
atmospheres. The `ORIGINAL_README*` files are the authors' accompanying notes.

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/20089901`.

Nine whitespace-separated columns (a text header row precedes the data):

1. wavelength [micron]
2-3. leaf 1 (Rp/Rs)^2 and its error
4-5. leaf 2 (Rp/Rs)^2 and its error
6-7. leaf 3 (Rp/Rs)^2 and its error -- the primary spectrum used in the
     paper's retrievals
8-9. leaf 4 (Rp/Rs)^2 and its error

The four “leaves” are correlated outputs of a tree-structured data-reduction
pipeline applied to the same underlying JWST/MIRI LRS observation. They share
the photons and most processing steps, so their max–min spread is a reduction-
choice sensitivity diagnostic, not an independent systematic-error sample.

## Integrity manifest

| File | Zenodo MD5 | SHA-256 of committed bytes |
|---|---|---|
| `miri_lrs_four_leaf_spectra.txt` | `8cf6d8289a806aa819b8f0fbf3469ecf` | `89ff8d763fa43e5e919e603333f8aeea424aac281d6b79e3cd43ea84c8859d29` |
| `ORIGINAL_README.txt` | `f6431c5a41bd83b57c63103785db354c` | `7125e5f871dc7784f7ccb251e9570284a404dbaba5c74a765fa68823244cc828` |
| `mg2sio4_full_median_and_max_logl_picaso_virga.nc` | `e7bbe01bfc917f3153fe0393d2efbbca` | `fe0e52ed1cc52d82071df5049200ac54e48997157488d23a15303e68c33527d5` |
| `mgxsioy_full_median_and_max_logl_picaso_virga.nc` | `878ea8dc90870ddd627ea9d83fb5b7e4` | `01d3de902b1eb5235ff2f4499f691aa16c4227a77c62d58b2c7b8f3538bca73b` |
| `ORIGINAL_README_PICASO_VIRGA.txt` | `e649370ba4c66a52cf888d13f1a07257` | `a2335c9a785ece9bc58fa9e0587b1a71aab3a668e96c93ee06fd0262c6503672` |

Zenodo record metadata lists the dataset as version v1. Retrieval of the
spectral table is recorded above; model products were retrieved on 3 October
2026 from the same immutable record.

## System-parameter snapshot

`nasa_exoplanet_archive_pscomppars.csv` was retrieved on 3 October 2026 from
the NASA Exoplanet Archive TAP `pscomppars` table for `HD 209458 b`. The query
selects only the columns displayed by the report. SHA-256:
`d0c5448e768027509072beafef1ad85ff9f4e0640cc870609bfca7102c28bb2e`.
