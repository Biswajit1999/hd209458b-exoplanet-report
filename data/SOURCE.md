# Data source

`miri_lrs_four_leaf_spectra.txt` is downloaded, unmodified, from Zenodo
record **10.5281/zenodo.20089901** ("Supplementary Information: Magnesium
Silicate Clouds in the Atmosphere of HD 209458b from a Rule-Based
Tree-Structured Data Reduction", Chubb & Grant et al. 2026), file
`hd209_ExoTiC_tree_four_leaf_spectra.txt` — the data behind Figure 4 of the
paper. `ORIGINAL_README.txt` is the paper's own README for this file,
downloaded alongside it.

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/20089901`.

Nine whitespace-separated columns (a text header row precedes the data):

1. wavelength [micron]
2-3. leaf 1 (Rp/Rs)^2 and its error
4-5. leaf 2 (Rp/Rs)^2 and its error
6-7. leaf 3 (Rp/Rs)^2 and its error -- the primary spectrum used in the
     paper's retrievals
8-9. leaf 4 (Rp/Rs)^2 and its error

The four "leaves" are independent outputs of a tree-structured data
reduction pipeline applied to the same underlying JWST MIRI LRS
observation -- a way of directly quantifying how much reduction choices
affect the recovered spectrum.
