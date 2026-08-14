"""Executable checks on the weighted-mean statistic and a regression
guard that the pipeline still reproduces the documented headline
numbers when run on the real downloaded data."""

import csv

import numpy as np
import analyze_spectrum as spec


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
    spec.FIG_DIR.mkdir(exist_ok=True)
    spec.main()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["n_wavelength_bins"]) == 28
    assert abs(float(rows["primary_weighted_mean_depth"]) - 14457.9) < 0.5
    assert abs(float(rows["mean_reduction_pipeline_spread"]) - 122.2) < 0.5
