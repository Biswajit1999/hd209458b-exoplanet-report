"""Validate archive identity, generated metrics, and public claim boundaries."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_spectrum import analyze


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


expected_hashes = {
    "miri_lrs_four_leaf_spectra.txt": "70be34f6104f5fb8ea2f4acf569641be06c29c4501cd162340732c544325595c",
    "ORIGINAL_README.txt": "9d9e9ee244e17f78b95d83dce865cc5de1909e439daed97b072dc416021caa13",
    "ORIGINAL_README_PICASO_VIRGA.txt": "a2335c9a785ece9bc58fa9e0587b1a71aab3a668e96c93ee06fd0262c6503672",
    "mg2sio4_full_median_and_max_logl_picaso_virga.nc": "fe0e52ed1cc52d82071df5049200ac54e48997157488d23a15303e68c33527d5",
    "mgxsioy_full_median_and_max_logl_picaso_virga.nc": "01d3de902b1eb5235ff2f4499f691aa16c4227a77c62d58b2c7b8f3538bca73b",
    "nasa_exoplanet_archive_pscomppars.csv": "d0c5448e768027509072beafef1ad85ff9f4e0640cc870609bfca7102c28bb2e",
}
for name, expected in expected_hashes.items():
    raw = (ROOT / "data" / name).read_bytes()
    if not name.endswith(".nc"):
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == expected, f"archive product digest drift: {name}: {digest} != {expected}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
source = (ROOT / "data/SOURCE.md").read_text(encoding="utf-8")
require("independent outputs" not in source, "correlated leaves described as independent")
for phrase in ("not an independent likelihood-ratio", "four leaves are correlated"):
    require(phrase in readme, f"missing inference boundary: {phrase}")

result = analyze()
summary = result["summary"]
require(summary["n_wavelength_bins"] == 28, "unexpected wavelength-bin count")
require(summary["bins_where_spread_exceeds_mean_reported_error"] == 18, "spread-count drift")
require(np.isclose(summary["mean_leaf_spread_ppm"], 122.24055118868374), "mean spread drift")
model_rows = {row["model"]: row for row in result["model_comparison"]}
require(np.isclose(model_rows["Mg2SiO4"]["shape_only_chi2"], 69.89652695076175), "Mg2SiO4 diagnostic drift")
require(np.isclose(model_rows["Mg2SiO4+MgSiO3"]["shape_only_chi2"], 84.07372412228243), "mixed-cloud diagnostic drift")
figure = (ROOT / "figures/hd209458b_transmission_spectrum.png").read_bytes()
require(figure.startswith(b"\x89PNG\r\n\x1a\n"), "figure is not PNG")
stored = json.loads((ROOT / "figures/analysis_summary.json").read_text(encoding="utf-8"))
require(stored == summary, "stored summary drift")
print("Evidence valid: five Zenodo products; NASA snapshot; 28 bins; four leaves; two cloud models.")
