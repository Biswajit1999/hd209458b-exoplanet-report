"""Executable checks on the weighted-mean statistic and a regression
guard that the pipeline still reproduces the documented headline
numbers when run on the real downloaded data."""

import csv

import analyze_spectrum as spec
import numpy as np
import pytest


def test_weighted_mean_matches_hand_computed_case():
    values = np.array([1.0, 2.0])
    errors = np.array([1.0, 0.5])  # weights 1 and 4
    mean, err = spec.weighted_mean(values, errors)
    assert np.isclose(mean, 1.8, rtol=1e-10)
    assert np.isclose(err, np.sqrt(1.0 / 5.0), rtol=1e-10)


def test_load_spectrum_returns_four_leaves_of_equal_length():
    wave, leaves, errs = spec.load_spectrum(spec.DATA_DIR / "miri_lrs_four_leaf_spectra.txt")
    assert set(leaves.keys()) == {1, 2, 3, 4}
    for leaf_id in (1, 2, 3, 4):
        assert len(leaves[leaf_id]) == len(wave)
        assert len(errs[leaf_id]) == len(wave)


def test_pipeline_reproduces_documented_headline_numbers():
    result = spec.analyze()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["n_wavelength_bins"]) == 28
    assert abs(float(rows["primary_weighted_mean_depth"]) - 14457.9) < 0.5
    assert abs(float(rows["mean_reduction_pipeline_spread"]) - 122.2) < 0.5
    assert result["summary"]["bins_where_spread_exceeds_mean_reported_error"] == 18
    assert result["summary"]["feature_contrast_range_across_leaves_ppm"] == pytest.approx(
        [267.18638468547357, 294.0730099291293]
    )


def test_archived_cloud_models_are_shape_compared_with_one_offset():
    result = spec.analyze()
    rows = {row["model"]: row for row in result["model_comparison"]}
    assert set(rows) == {"Mg2SiO4", "Mg2SiO4+MgSiO3"}
    assert rows["Mg2SiO4"]["shape_only_chi2"] == pytest.approx(69.89652695076175)
    assert rows["Mg2SiO4+MgSiO3"]["shape_only_chi2"] == pytest.approx(84.07372412228243)


def test_loader_rejects_nonpositive_uncertainty(tmp_path):
    malformed = tmp_path / "bad.txt"
    malformed.write_text("header\n5 " + " ".join(["1", "-1"] * 4) + "\n")
    with pytest.raises(ValueError, match="uncertainties"):
        spec.load_spectrum(malformed)
