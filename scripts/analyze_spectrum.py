"""Reproduce reduction-sensitivity and cloud-model diagnostics for HD 209458 b.

The four spectra are correlated leaves of one reduction tree. The two model
curves are posterior products from the source publication, fitted to a larger
combined dataset. Consequently, every comparison here is descriptive: no
chi-square value is interpreted as a detection significance or Bayes factor.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
LEAF_IDS = (1, 2, 3, 4)
MODEL_FILES = {
    "Mg2SiO4": DATA_DIR / "mg2sio4_full_median_and_max_logl_picaso_virga.nc",
    "Mg2SiO4+MgSiO3": DATA_DIR / "mgxsioy_full_median_and_max_logl_picaso_virga.nc",
}


def load_spectrum(path: Path) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray]]:
    table = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if table.ndim != 2 or table.shape[1] != 9:
        raise ValueError("expected nine-column spectrum table")
    wavelength = table[:, 0]
    leaves = {leaf: table[:, 2 * leaf - 1] for leaf in LEAF_IDS}
    errors = {leaf: table[:, 2 * leaf] for leaf in LEAF_IDS}
    if not np.all(np.diff(wavelength) > 0) or any(np.any(errors[leaf] <= 0) for leaf in LEAF_IDS):
        raise ValueError("wavelengths must increase and uncertainties must be positive")
    return wavelength, leaves, errors


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    weights = errors**-2
    return float(np.average(values, weights=weights)), float(np.sqrt(1 / weights.sum()))


def load_model(path: Path, wavelength: np.ndarray) -> np.ndarray:
    with xr.open_dataset(path) as dataset:
        model_wavelength = dataset["wavelength"].values
        model_depth = dataset["median_transit_depth"].values
    order = np.argsort(model_wavelength)
    if wavelength.min() < model_wavelength.min() or wavelength.max() > model_wavelength.max():
        raise ValueError("observations lie outside model wavelength support")
    return np.interp(wavelength, model_wavelength[order], model_depth[order])


def shape_only_comparison(
    observed: np.ndarray, errors: np.ndarray, model: np.ndarray
) -> tuple[float, float, np.ndarray]:
    """Fit one vertical offset, then return offset, chi-square, and residuals."""
    offset = float(np.average(observed - model, weights=errors**-2))
    residuals = (observed - model - offset) / errors
    return offset, float(np.sum(residuals**2)), residuals


def band_contrast(
    wavelength: np.ndarray, depth: np.ndarray, errors: np.ndarray
) -> tuple[float, float]:
    """Return the predeclared 8.0–10.2 minus 5.2–7.8 µm contrast."""
    reference = wavelength < 7.8
    feature = (wavelength >= 8.0) & (wavelength <= 10.2)
    reference_mean, reference_error = weighted_mean(depth[reference], errors[reference])
    feature_mean, feature_error = weighted_mean(depth[feature], errors[feature])
    return feature_mean - reference_mean, float(np.hypot(reference_error, feature_error))


def analyze() -> dict[str, object]:
    FIG_DIR.mkdir(exist_ok=True)
    wavelength, leaves, errors = load_spectrum(DATA_DIR / "miri_lrs_four_leaf_spectra.txt")
    stacked = np.vstack([leaves[leaf] for leaf in LEAF_IDS])
    error_stack = np.vstack([errors[leaf] for leaf in LEAF_IDS])
    spread_ppm = np.ptp(stacked, axis=0) * 1e6
    mean_error_ppm = error_stack.mean(axis=0) * 1e6

    leaf_rows = []
    for leaf in LEAF_IDS:
        mean, mean_error = weighted_mean(leaves[leaf], errors[leaf])
        contrast, contrast_error = band_contrast(wavelength, leaves[leaf], errors[leaf])
        leaf_rows.append(
            {
                "leaf": leaf,
                "weighted_mean_depth_ppm": mean * 1e6,
                "photon_only_mean_error_ppm": mean_error * 1e6,
                "feature_minus_reference_ppm": contrast * 1e6,
                "photon_only_contrast_error_ppm": contrast_error * 1e6,
            }
        )

    primary, primary_error = leaves[3], errors[3]
    flat, _ = weighted_mean(primary, primary_error)
    flat_chi2 = float(np.sum(((primary - flat) / primary_error) ** 2))
    model_rows, model_curves, residuals = [], {}, {}
    for name, path in MODEL_FILES.items():
        curve = load_model(path, wavelength)
        offset, chi2, standardized = shape_only_comparison(primary, primary_error, curve)
        model_curves[name] = curve + offset
        residuals[name] = standardized
        model_rows.append(
            {
                "model": name,
                "fitted_vertical_offset_ppm": offset * 1e6,
                "shape_only_chi2": chi2,
                "n_bins": len(wavelength),
            }
        )

    summary = {
        "scope": "descriptive audit of publication-supplied data and posterior model products",
        "n_wavelength_bins": len(wavelength),
        "wavelength_range_um": [float(wavelength.min()), float(wavelength.max())],
        "primary_leaf": 3,
        "primary_weighted_mean_depth_ppm": leaf_rows[2]["weighted_mean_depth_ppm"],
        "mean_leaf_spread_ppm": float(spread_ppm.mean()),
        "median_leaf_spread_ppm": float(np.median(spread_ppm)),
        "mean_reported_error_across_leaves_ppm": float(mean_error_ppm.mean()),
        "bins_where_spread_exceeds_mean_reported_error": int(np.sum(spread_ppm > mean_error_ppm)),
        "flat_primary_chi2": flat_chi2,
        "feature_definition": "8.0–10.2 minus 5.2–7.8 micrometres",
        "feature_contrast_range_across_leaves_ppm": [
            float(min(row["feature_minus_reference_ppm"] for row in leaf_rows)),
            float(max(row["feature_minus_reference_ppm"] for row in leaf_rows)),
        ],
        "inference_boundary": (
            "Correlated reductions and posterior-derived model curves preclude independent "
            "detection-significance or model-selection claims from these diagnostics."
        ),
    }
    (FIG_DIR / "analysis_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for filename, rows in (("leaf_metrics.csv", leaf_rows), ("model_comparison.csv", model_rows)):
        with (FIG_DIR / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    with (FIG_DIR / "summary_statistics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_wavelength_bins", len(wavelength), "count"])
        writer.writerow(["wavelength_min", f"{wavelength.min():.3f}", "micron"])
        writer.writerow(["wavelength_max", f"{wavelength.max():.3f}", "micron"])
        writer.writerow(["primary_weighted_mean_depth", f"{leaf_rows[2]['weighted_mean_depth_ppm']:.1f}", "ppm (leaf 3)"])
        writer.writerow(["primary_weighted_mean_depth_error", f"{leaf_rows[2]['photon_only_mean_error_ppm']:.2f}", "ppm"])
        writer.writerow(["mean_photon_noise_error", f"{primary_error.mean() * 1e6:.1f}", "ppm"])
        writer.writerow(["mean_reduction_pipeline_spread", f"{spread_ppm.mean():.1f}", "ppm"])

    colors = {1: "#a5b6c5", 2: "#c8a29a", 3: "#172a3a", 4: "#b5ad80"}
    model_colors = {"Mg2SiO4": "#158078", "Mg2SiO4+MgSiO3": "#b5563f"}
    fig = plt.figure(figsize=(13.4, 8.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(1.35, 1))
    spectrum_ax = fig.add_subplot(grid[0, :])
    residual_ax = fig.add_subplot(grid[1, 0])
    sensitivity_ax = fig.add_subplot(grid[1, 1])
    for leaf in (1, 2, 4, 3):
        spectrum_ax.errorbar(
            wavelength, leaves[leaf] * 1e6, yerr=errors[leaf] * 1e6,
            fmt="o", ms=4.2 if leaf == 3 else 3, color=colors[leaf],
            alpha=1 if leaf == 3 else 0.48, lw=0.8,
            label=f"leaf {leaf}" + (" · primary" if leaf == 3 else ""),
        )
    for name, curve in model_curves.items():
        spectrum_ax.plot(wavelength, curve * 1e6, color=model_colors[name], lw=2.2, label=f"{name} · shape aligned")
    spectrum_ax.axvspan(8.0, 10.2, color="#d9b95b", alpha=0.11)
    spectrum_ax.set(title="HD 209458 b · JWST/MIRI LRS reduction and cloud-model audit", ylabel="Transit depth [ppm]")
    spectrum_ax.legend(frameon=False, ncol=3, fontsize=9)
    for name, values in residuals.items():
        residual_ax.plot(wavelength, values, "o-", ms=3.5, lw=1.2, color=model_colors[name], label=name)
    residual_ax.axhline(0, color="#5f6870", lw=1)
    residual_ax.set(xlabel="Wavelength [µm]", ylabel="Primary residual / reported σ", title="Shape-only residuals")
    residual_ax.legend(frameon=False, fontsize=9)
    sensitivity_ax.plot(wavelength, spread_ppm, "o-", color="#8c3f33", label="leaf max–min spread")
    sensitivity_ax.plot(wavelength, mean_error_ppm, "o-", color="#315f78", label="mean reported 1σ")
    sensitivity_ax.fill_between(wavelength, 0, spread_ppm, color="#8c3f33", alpha=0.08)
    sensitivity_ax.set(xlabel="Wavelength [µm]", ylabel="Depth scale [ppm]", title="Reduction sensitivity vs reported error")
    sensitivity_ax.legend(frameon=False, fontsize=9)
    for axis in (spectrum_ax, residual_ax, sensitivity_ax):
        axis.grid(alpha=0.16)
    fig.savefig(FIG_DIR / "hd209458b_transmission_spectrum.png", dpi=220)
    plt.close(fig)
    return {"summary": summary, "leaf_metrics": leaf_rows, "model_comparison": model_rows}


def main() -> None:
    print(json.dumps(analyze(), indent=2))


if __name__ == "__main__":
    main()
