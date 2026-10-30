"""Sensitivity of the HD 209458 b MIRI broad-band contrast to assumed spectral covariance.

The four reduction leaves share photons. Their spread is not four independent
measurements of atmospheric physics. The Toeplitz correlation model here is a
hypothetical stress test, NOT a covariance measured by JWST or the source paper.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "miri_lrs_four_leaf_spectra.txt"


def load_table(path: Path = DATA) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    table = np.atleast_2d(np.loadtxt(path, skiprows=1))
    if table.shape[1] != 9 or table.shape[0] < 5:
        raise ValueError("Expected nine columns and at least five bins")
    wavelength = table[:, 0]
    depths = table[:, [1, 3, 5, 7]].T
    errors = table[:, [2, 4, 6, 8]].T
    if not np.all(np.isfinite(table)) or np.any(errors <= 0):
        raise ValueError("Non-finite values or non-positive uncertainties")
    if np.any(np.diff(wavelength) <= 0):
        raise ValueError("Wavelength must be strictly increasing")
    return wavelength, depths, errors


def contrast(wavelength: np.ndarray, depth: np.ndarray, error: np.ndarray,
             rho: float = 0.0) -> dict[str, float]:
    """GLS mean difference, including cross-band covariance in its variance."""
    if not (0 <= rho < 1) or len(wavelength) != len(depth) or len(depth) != len(error):
        raise ValueError("Invalid correlation or vector lengths")
    if not (np.all(np.isfinite(depth)) and np.all(np.isfinite(error))
            and np.all(error > 0)):
        raise ValueError("Invalid spectrum or uncertainties")
    ref = np.flatnonzero(wavelength < 7.8)
    feat = np.flatnonzero((wavelength >= 8.0) & (wavelength <= 10.2))
    if len(ref) < 2 or len(feat) < 2:
        raise ValueError("At least two bins required in each declared band")
    indices = np.arange(len(wavelength))
    corr = rho ** np.abs(indices[:, None] - indices[None, :])
    cov = corr * error[:, None] * error[None, :]
    coeff = np.zeros(len(wavelength))
    for group, sign in ((ref, -1), (feat, 1)):
        local = cov[np.ix_(group, group)]
        weight = np.linalg.solve(local, np.ones(len(group)))
        coeff[group] += sign * weight / weight.sum()
    value = float(coeff @ depth)
    variance = float(coeff @ cov @ coeff)
    if variance <= 0:
        raise ArithmeticError("Non-positive contrast variance")
    return {"contrast_ppm": value * 1e6, "formal_sigma_ppm": np.sqrt(variance) * 1e6,
            "n_reference": len(ref), "n_feature": len(feat), "rho": rho}


def run_audit(wavelength: np.ndarray, depths: np.ndarray,
              errors: np.ndarray) -> dict:
    if depths.shape != errors.shape or depths.shape != (4, len(wavelength)):
        raise ValueError("Expected four correlated reduction leaves")
    primary = 2  # leaf 3 is the publication's primary reduction
    correlation = [contrast(wavelength, depths[primary], errors[primary], rho)
                   for rho in (0.0, 0.25, 0.5, 0.75)]
    base = correlation[0]["contrast_ppm"]
    jackknife = []
    for i in range(len(wavelength)):
        keep = np.arange(len(wavelength)) != i
        result = contrast(wavelength[keep], depths[primary, keep],
                          errors[primary, keep])
        jackknife.append({"deleted_bin": i, "wavelength_um": float(wavelength[i]),
                          "contrast_ppm": result["contrast_ppm"],
                          "shift_from_baseline_ppm": result["contrast_ppm"] - base})
    leaves = [contrast(wavelength, depths[i], errors[i])["contrast_ppm"]
              for i in range(4)]
    leave_one_leaf = [
        {"omitted_leaf": i + 1, "mean_remaining_contrast_ppm":
         float(np.mean([leaves[j] for j in range(4) if j != i]))}
        for i in range(4)
    ]
    return {
        "scope": "28-bin published MIRI spectra; descriptive reduction sensitivity only",
        "n_bins": len(wavelength), "primary_leaf": 3,
        "assumed_covariance": "Cij=sigma_i*sigma_j*rho^abs(i-j), not measured",
        "correlation_sensitivity": correlation,
        "primary_bin_deletion": {
            "max_absolute_shift_ppm": max(abs(x["shift_from_baseline_ppm"])
                                          for x in jackknife),
            "details": jackknife
        },
        "leaf_contrasts_ppm": leaves,
        "mean_of_correlated_leaves_ppm": float(np.mean(leaves)),
        "leave_one_correlated_leaf_out": leave_one_leaf,
        "limitations": [
            "No empirical spectral or cross-leaf covariance supplied.",
            "Reduction leaves are correlated, not independent replicates.",
            "Formal errors are conditional on the hypothetical Toeplitz model.",
            "No independent cloud detection or Bayes factor follows."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_audit(*load_table())
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
