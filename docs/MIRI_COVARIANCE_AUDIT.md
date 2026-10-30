# MIRI reduction-leaf and spectral-covariance sensitivity

This independent Python audit uses the existing 28-bin, four-leaf JWST/MIRI LRS table from the source publication; no new light-curve reduction or retrieval is performed.

Three diagnostics are deliberately separated: (1) a generalized least-squares contrast between the predeclared 8.0–10.2 and <7.8 micrometre bands, under a **hypothetical** Toeplitz spectral correlation C_ij = sigma_i sigma_j rho^|i-j| for rho = 0, 0.25, 0.5 and 0.75; (2) leave-one-wavelength-bin-out sensitivity for the primary reduction leaf 3; and (3) leave-one-reduction-leaf-out sensitivity of the four-leaf descriptive contrast mean.

The GLS band means use within-band inverse covariance weights. The contrast variance uses the **full** covariance, including cross-band terms, to avoid silently treating the bands as independent. The wavelength-bin deletion diagnostic is influence analysis, not an independent resampling distribution. The four leaves share observations and pipeline decisions; they are not independent experiments, so their spread is not a statistical confidence interval.

Run `python scripts/miri_covariance_audit.py --output /tmp/miri_covariance.json` and `python -m pytest -q tests/test_miri_covariance_audit.py`. The script reads only the existing published source table. It does not overwrite the report's pinned figures or original summary.

**Limitations:** No measured spectral or inter-leaf covariance matrix is available here. The Toeplitz parameter rho is a sensitivity knob rather than an inferred instrumental property. The source-paper cloud curves are posterior products and cannot be independently compared as if they were predeclared model predictions. No independent magnesium-silicate detection, Bayes factor, or atmospheric retrieval significance is claimed.

Source: Chubb, Grant et al. (2026), supplementary data DOI: https://doi.org/10.5281/zenodo.20089901.
