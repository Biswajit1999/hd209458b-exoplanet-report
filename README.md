# HD 209458 b — Exoplanet Atmosphere Report

"Osiris" — the first known exoplanet observed to transit its star
(1999, months after its radial-velocity discovery) and the first
exoplanet whose atmosphere was directly detected (2002, sodium via HST
STIS). This repo works from a 2026 JWST MIRI transmission spectrum
testing for magnesium silicate clouds, comparing four correlated
reduction-tree leaves applied to the same underlying data.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## Data sources

- **System parameters** — from the NASA Exoplanet Archive TAP
  service (`pscomppars` table).
- **JWST MIRI LRS spectrum** — the reduced transmission spectrum behind
  Figure 4 of Chubb, Grant et al. (2026), "Magnesium Silicate Clouds in the
  Atmosphere of HD 209458b from a Rule-Based Tree-Structured Data
  Reduction", released publicly on Zenodo
  ([10.5281/zenodo.20089901](https://doi.org/10.5281/zenodo.20089901)). Four
  correlated "leaf" reductions of the same underlying data are included —
  they share the same exposures and most of the same processing, differing
  only in specific reduction-tree choices.
- **Analysis** — `scripts/analyze_spectrum.py` computes the weighted mean
  transit depth of the primary reduction, and compares the average
  photon-noise error to the average spread across the four leaves. Run it
  yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    JWST MIRI LRS spectrum + original paper README (Zenodo)
scripts/analyze_spectrum.py   analysis producing the figure + statistics
figures/                 generated plot + summary_statistics.csv
tests/                   unit tests + a regression check against the real data
```

## Tests

`tests/test_analysis.py` checks the weighted-mean formula and the
four-leaf data loader, and reruns the full pipeline on the real
downloaded spectrum, verifying it still reproduces the numbers this
README documents. Runs automatically on every push via GitHub Actions;
run locally with:

```bash
pytest tests/ -v
```

## What the numbers show

28 wavelength bins, 5.2-11.9 microns. Mean transit depth 14458 ppm.
The mean spread between the four reduction-tree leaves (122 ppm) is
larger than the mean photon-noise error on any single leaf's spectrum
(92 ppm) — a demonstration that data-reduction choices can matter as
much as statistical noise for this kind of observation, which is the
central point of the source paper.

## Limitations

The max-min spread across the four leaves is a useful sensitivity
metric, not a statistically calibrated systematic uncertainty: the
four reductions share the same photons and much of the same
processing pipeline, so this spread isn't independent of the photon
noise it's being compared against, and it isn't a variance
decomposition in the formal sense. The source paper's own
tree-structured framework treats reduction-choice uncertainty more
rigorously than this repo's simple max-min comparison does.

## References

1. Charbonneau, D. et al., 2002. Detection of an Extrasolar Planet
   Atmosphere. *The Astrophysical Journal*, 568(1), pp.377-384.
2. Chubb, K.L., Grant, D. et al., 2026. Magnesium Silicate Clouds in the
   Atmosphere of HD 209458b from a Rule-Based Tree-Structured Data
   Reduction. Zenodo record
   [10.5281/zenodo.20089901](https://doi.org/10.5281/zenodo.20089901).
3. Henry, G.W. et al., 2000. A Transiting "51 Peg-like" Planet. *The
   Astrophysical Journal Letters*, 529(1), pp.L41-L44.
4. Vidal-Madjar, A. et al., 2003. An extended upper atmosphere around the
   extrasolar planet HD209458b. *Nature*, 422, pp.143-146.
5. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
