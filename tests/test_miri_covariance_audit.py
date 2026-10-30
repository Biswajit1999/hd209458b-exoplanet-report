"""Covariance and reduction-leaf stress tests for published MIRI spectra."""
import miri_covariance_audit as audit
import numpy as np
import pytest


def toy():
    wavelength = np.array([5.3, 6.1, 7.2, 8.3, 9.0, 9.8])
    depth = np.array([0.014] * 3 + [0.015] * 3)
    error = np.full(6, 0.0001)
    return wavelength, depth, error


def test_diagonal_gls_matches_exact_equal_weight_contrast():
    w, d, e = toy()
    result = audit.contrast(w, d, e, rho=0)
    assert result["contrast_ppm"] == pytest.approx(1000)
    assert result["formal_sigma_ppm"] == pytest.approx(
        np.sqrt(2 / 3) * 100
    )


def test_constant_depth_offset_cancels_exactly():
    w, d, e = toy()
    baseline = audit.contrast(w, d, e, rho=0.5)
    shifted = audit.contrast(w, d + 0.02, e, rho=0.5)
    assert shifted["contrast_ppm"] == pytest.approx(baseline["contrast_ppm"])


def test_correlation_changes_formal_error_not_flat_band_contrast():
    w, d, e = toy()
    independent = audit.contrast(w, d, e, rho=0)
    correlated = audit.contrast(w, d, e, rho=0.5)
    assert correlated["contrast_ppm"] == pytest.approx(1000)
    assert correlated["formal_sigma_ppm"] != pytest.approx(
        independent["formal_sigma_ppm"]
    )


@pytest.mark.parametrize("rho", [-0.1, 1.0, 1.1])
def test_invalid_correlation_rejected(rho):
    w, d, e = toy()
    with pytest.raises(ValueError):
        audit.contrast(w, d, e, rho=rho)


def test_missing_feature_band_rejected():
    w, d, e = toy()
    with pytest.raises(ValueError):
        audit.contrast(w[:3], d[:3], e[:3])


def test_actual_published_table_replays_all_three_diagnostics():
    w, depths, errors = audit.load_table()
    assert len(w) == 28
    result = audit.run_audit(w, depths, errors)
    assert result["n_bins"] == 28
    assert len(result["correlation_sensitivity"]) == 4
    assert len(result["primary_bin_deletion"]["details"]) == 28
    assert len(result["leave_one_correlated_leaf_out"]) == 4
    assert all(np.isfinite(x) for x in result["leaf_contrasts_ppm"])
