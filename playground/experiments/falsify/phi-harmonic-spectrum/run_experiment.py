#!/usr/bin/env python3
"""
Falsify Golden Ratio (φ) Harmonic Spectrum in Prime Gaps
Run experiment as per TECH-SPECS.md
"""

import numpy as np
import os
from prime_utils import load_prime_gaps
from analysis import (
    compute_psd,
    find_peaks_in_psd,
    get_phi_harmonics,
    get_pi_harmonics,
    get_e_harmonics,
    phi_alignment_score,
    alignment_score,
    z_score_phi_peaks,
    peak_prominence_score,
)
from models import permutation_test, spectral_concentration_test
from visualization import (
    plot_power_spectrum,
    plot_peak_alignment,
    plot_permutation_null,
    plot_multi_range_comparison,
)

# Define prime ranges (adjusted for feasibility; original spec has large ranges)
PRIME_RANGES = {
    "1e4_1e5": (10**4, 10**5),  # N ≈ 8k gaps for quick testing
}

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_for_range(range_name, prime_range):
    print(f"Processing range: {range_name}")
    log_gaps = load_prime_gaps(prime_range)
    if len(log_gaps) < 1000:
        print(f"Warning: Only {len(log_gaps)} gaps, skipping detailed analysis")
        return None

    N = len(log_gaps)
    phi_freqs = get_phi_harmonics(N)
    pi_freqs = get_pi_harmonics(N)
    e_freqs = get_e_harmonics(N)

    # Compute PSD
    freqs, psd = compute_psd(log_gaps)

    # Peak detection
    peak_freqs, peak_amps = find_peaks_in_psd(freqs, psd)

    # Scores
    phi_alignment = phi_alignment_score(peak_freqs, phi_freqs)
    pi_alignment = alignment_score(peak_freqs, pi_freqs)
    e_alignment = alignment_score(peak_freqs, e_freqs)
    z_scores = z_score_phi_peaks(phi_freqs, freqs, psd)
    prominences = peak_prominence_score(phi_freqs, freqs, psd)

    # Permutation test
    p_value, null_maxes = permutation_test(log_gaps, phi_freqs)

    # Spectral concentration
    phi_density, rand_density = spectral_concentration_test(phi_freqs, freqs, psd)

    # Plots
    plot_power_spectrum(
        freqs, psd, phi_freqs, f"{RESULTS_DIR}/power_spectrum_{range_name}.png"
    )
    plot_peak_alignment(
        peak_freqs,
        phi_freqs,
        save_path=f"{RESULTS_DIR}/peak_alignment_{range_name}.png",
    )
    observed_max = max([psd[np.argmin(np.abs(freqs - f))] for f in phi_freqs])
    plot_permutation_null(
        observed_max, null_maxes, f"{RESULTS_DIR}/permutation_null_{range_name}.png"
    )

    return {
        "N": N,
        "phi_freqs": phi_freqs,
        "phi_alignment": phi_alignment,
        "pi_alignment": pi_alignment,
        "e_alignment": e_alignment,
        "z_scores": z_scores,
        "prominences": prominences,
        "p_value": p_value,
        "phi_density": phi_density,
        "rand_density": rand_density,
        "freqs": freqs,
        "psd": psd,
    }


def generate_report(results):
    report = "# φ-Harmonic Spectrum Falsification Report\n\n"
    for range_name, res in results.items():
        report += f"## Range: {range_name}\n"
        report += f"- N (gaps): {res['N']}\n"
        report += f"- φ-Alignment Score: {res['phi_alignment']}\n"
        report += f"- π-Alignment Score: {res['pi_alignment']}\n"
        report += f"- e-Alignment Score: {res['e_alignment']}\n"
        report += f"- Max Z-Score: {max(res['z_scores']):.3f}\n"
        report += f"- Max Prominence: {max(res['prominences']):.3f}\n"
        report += f"- Permutation p-value: {res['p_value']:.4f}\n"
        report += f"- φ-Density vs Random: {res['phi_density']:.2f} vs {res['rand_density']:.2f}\n"
        report += f"- Falsified? {'Yes' if res['p_value'] > 0.05 else 'No (significant peaks)'}\n\n"

    with open(f"{RESULTS_DIR}/phi_harmonic_report.md", "w") as f:
        f.write(report)
    print("Report generated: results/phi_harmonic_report.md")


def main():
    results = {}
    for range_name, prime_range in PRIME_RANGES.items():
        res = run_for_range(range_name, prime_range)
        if res:
            results[range_name] = res

    if results:
        # Multi-range plot
        multi_data = {
            k: (v["freqs"], v["psd"], v["phi_freqs"]) for k, v in results.items()
        }
        plot_multi_range_comparison(
            multi_data, f"{RESULTS_DIR}/multi_range_comparison.png"
        )

        generate_report(results)
    else:
        print("No valid results to report.")


if __name__ == "__main__":
    main()
