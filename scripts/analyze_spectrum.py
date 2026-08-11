"""Analyze the real JWST MIRI LRS transmission spectrum of HD 209458 b.

Data source: Zenodo record 10.5281/zenodo.20089901, "Supplementary
Information: Magnesium Silicate Clouds in the Atmosphere of HD 209458b from
a Rule-Based Tree-Structured Data Reduction" (Chubb & Grant et al.), file
hd209_ExoTiC_tree_four_leaf_spectra.txt -- Figure 4 data from the paper.
Retrieved directly from Zenodo; reproduced unmodified in data/.

The file contains four independent "leaf" reductions from a tree-structured
data-reduction pipeline (a way of testing how reduction choices affect the
recovered spectrum). Per the paper's own README, "leaf 3" is the version
used in the majority of their retrievals, so it is treated as the primary
spectrum here; the other three are plotted alongside it as a genuine
reduction-uncertainty band -- how much the answer changes purely from
reduction-pipeline choices, holding the underlying data fixed.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def load_spectrum(path: Path):
    wave, leaves = [], {1: [], 2: [], 3: [], 4: []}
    errs = {1: [], 2: [], 3: [], 4: []}
    with path.open() as handle:
        for line in handle:
            parts = line.split()
            if len(parts) != 9:
                continue
            try:
                values = list(map(float, parts))
            except ValueError:
                continue
            wave.append(values[0])
            leaves[1].append(values[1]); errs[1].append(values[2])
            leaves[2].append(values[3]); errs[2].append(values[4])
            leaves[3].append(values[5]); errs[3].append(values[6])
            leaves[4].append(values[7]); errs[4].append(values[8])
    return (
        np.array(wave),
        {k: np.array(v) for k, v in leaves.items()},
        {k: np.array(v) for k, v in errs.items()},
    )


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    weights = 1.0 / errors**2
    mean = np.sum(values * weights) / np.sum(weights)
    mean_error = np.sqrt(1.0 / np.sum(weights))
    return mean, mean_error


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    wave, leaves, errs = load_spectrum(DATA_DIR / "miri_lrs_four_leaf_spectra.txt")

    primary_depth = leaves[3]
    primary_err = errs[3]
    mean_depth, mean_depth_error = weighted_mean(primary_depth, primary_err)

    # Reduction-choice spread: at each wavelength, the max-min across the four leaves,
    # a real estimate of pipeline systematic uncertainty independent of photon noise.
    stacked = np.vstack([leaves[i] for i in (1, 2, 3, 4)])
    reduction_spread_ppm = (stacked.max(axis=0) - stacked.min(axis=0)) * 1e6
    mean_reduction_spread = reduction_spread_ppm.mean()
    mean_photon_error = primary_err.mean() * 1e6

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_wavelength_bins", len(wave), "count"])
        writer.writerow(["wavelength_min", f"{wave.min():.3f}", "micron"])
        writer.writerow(["wavelength_max", f"{wave.max():.3f}", "micron"])
        writer.writerow(["primary_weighted_mean_depth", f"{mean_depth*1e6:.1f}", "ppm (leaf 3)"])
        writer.writerow(["primary_weighted_mean_depth_error", f"{mean_depth_error*1e6:.2f}", "ppm"])
        writer.writerow(["mean_photon_noise_error", f"{mean_photon_error:.1f}", "ppm"])
        writer.writerow(["mean_reduction_pipeline_spread", f"{mean_reduction_spread:.1f}", "ppm"])

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    leaf_colors = {1: "#9fb8cc", 2: "#c9a0a0", 3: "#1f6f5c", 4: "#c9c090"}
    leaf_labels = {1: "leaf 1", 2: "leaf 2", 3: "leaf 3 (primary, used in retrievals)", 4: "leaf 4"}
    for leaf_id in (1, 2, 4, 3):  # draw primary last so it's on top
        ax.errorbar(
            wave, leaves[leaf_id] * 1e6, yerr=errs[leaf_id] * 1e6,
            fmt="o" if leaf_id == 3 else ".", ms=6 if leaf_id == 3 else 3.5,
            color=leaf_colors[leaf_id], ecolor=leaf_colors[leaf_id],
            alpha=1.0 if leaf_id == 3 else 0.55, elinewidth=1,
            label=leaf_labels[leaf_id],
        )
    ax.set_xlabel("Wavelength [micron]")
    ax.set_ylabel("Transit depth (Rp/Rs)^2 [ppm]")
    ax.set_title("HD 209458 b transmission spectrum (JWST MIRI LRS, real reduced data)\nfour independent tree-reduction pipeline outputs")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "hd209458b_transmission_spectrum.png", dpi=200)

    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'hd209458b_transmission_spectrum.png'}")
    print(f"n={len(wave)}, primary (leaf 3) mean depth = {mean_depth*1e6:.1f} +/- {mean_depth_error*1e6:.2f} ppm")
    print(
        f"Mean photon-noise error = {mean_photon_error:.1f} ppm vs. mean reduction-pipeline "
        f"spread across the 4 leaves = {mean_reduction_spread:.1f} ppm"
    )


if __name__ == "__main__":
    main()
