#!/usr/bin/env python
"""
Demonstration of CRISPR Spectral Resonance Optimization

This script demonstrates the complete workflow for analyzing CRISPR gRNA
sequences using φ-phase transforms and spectral feature extraction.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.phi_phase import (
    encode_dna_complex,
    PhiPhaseTransform,
    arcsin_bridge,
    combined_transform,
)
from modules.spectral_features import (
    SpectralFeatureExtractor,
    compute_gc_content,
    assign_gc_quartile,
)


def plot_waveform_comparison(waveforms, labels, title="DNA Waveform Comparison"):
    """Plot comparison of waveforms in complex plane."""
    fig, axes = plt.subplots(1, len(waveforms), figsize=(5 * len(waveforms), 4))

    if len(waveforms) == 1:
        axes = [axes]

    for i, (waveform, label) in enumerate(zip(waveforms, labels)):
        ax = axes[i]
        ax.scatter(waveform.real, waveform.imag, alpha=0.6, s=20)
        ax.set_xlabel("Real")
        ax.set_ylabel("Imaginary")
        ax.set_title(label)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color="k", linewidth=0.5)
        ax.axvline(x=0, color="k", linewidth=0.5)
        ax.set_aspect("equal")

    plt.suptitle(title)
    plt.tight_layout()
    return fig


def plot_spectrum_comparison(spectra, labels, title="Spectral Comparison"):
    """Plot comparison of magnitude spectra."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for spectrum, label in zip(spectra, labels):
        ax.plot(spectrum, label=label, alpha=0.7)

    ax.set_xlabel("Frequency Bin")
    ax.set_ylabel("Magnitude")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def demonstrate_single_sequence():
    """Demonstrate analysis of a single sequence."""
    print("=" * 80)
    print("DEMONSTRATION: Single Sequence Analysis")
    print("=" * 80)

    # Example gRNA sequence
    sequence = "ATCGATCGATCGATCGATCG"
    print(f"\nSequence: {sequence}")
    print(f"Length: {len(sequence)}")
    print(f"GC content: {compute_gc_content(sequence):.1f}%")
    print(f"GC quartile: Q{assign_gc_quartile(compute_gc_content(sequence))}")

    # Step 1: Encode to complex waveform
    print("\n1. Encoding to complex waveform...")
    waveform_base = encode_dna_complex(sequence)
    print(f"   Waveform shape: {waveform_base.shape}")
    print(f"   First 5 values: {waveform_base[:5]}")

    # Step 2: Apply φ-phase transform
    print("\n2. Applying φ-phase transform (k=0.300)...")
    phi_transform = PhiPhaseTransform(k=0.300)
    waveform_phi = phi_transform.apply_transform(waveform_base)
    print(f"   Transform applied")

    # Step 3: Apply arcsin bridge
    print("\n3. Applying arcsin bridge (α=0.95)...")
    waveform_final = arcsin_bridge(waveform_phi, alpha=0.95)
    print(f"   Compression applied")

    # Step 4: Compute spectra
    print("\n4. Computing FFT spectra...")
    extractor = SpectralFeatureExtractor(fft_size=256, window_type="hann")

    spectrum_base = extractor.compute_spectrum(waveform_base)
    spectrum_phi = extractor.compute_spectrum(waveform_phi)
    spectrum_final = extractor.compute_spectrum(waveform_final)

    print(f"   Spectrum shape: {spectrum_base.shape}")

    # Step 5: Extract features
    print("\n5. Extracting spectral features...")
    features = extractor.extract_all_features(spectrum_base, spectrum_final)

    print(f"\n   Key Features:")
    print(f"   - ΔEntropy: {features['delta_entropy']:.4f}")
    print(f"   - Δf₁: {features['delta_f1']:.2f}%")
    print(f"   - Δsidelobe: {features['delta_sidelobe']:.4f}")
    print(
        f"   - Composite disruption score: {features['composite_disruption_score']:.2f}"
    )
    print(f"   - MSC (self): ~1.0")
    print(f"   - Sidelobe asymmetry: {features['sidelobe_asymmetry_transformed']:.4f}")

    # Visualization
    print("\n6. Generating visualizations...")

    # Plot waveforms
    fig1 = plot_waveform_comparison(
        [waveform_base, waveform_phi, waveform_final],
        ["Baseline", "φ-phase", "φ-phase + Arcsin"],
        title=f"DNA Waveform Analysis: {sequence[:10]}...",
    )

    # Plot spectra
    fig2 = plot_spectrum_comparison(
        [spectrum_base, spectrum_phi, spectrum_final],
        ["Baseline", "φ-phase", "φ-phase + Arcsin"],
        title=f"Magnitude Spectra: {sequence[:10]}...",
    )

    return fig1, fig2, features


def demonstrate_k_sweep():
    """Demonstrate k-parameter sweep analysis."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: K-Parameter Sweep")
    print("=" * 80)

    sequence = "GCTAGCTAGCTAGCTAGCTA"
    print(f"\nSequence: {sequence}")

    # Encode
    waveform_base = encode_dna_complex(sequence)

    # Sweep k from 0.20 to 0.40
    print("\nPerforming k-sweep (0.20 to 0.40, step=0.05)...")
    phi_transform = PhiPhaseTransform(k=0.3)  # Initial k
    k_values, transformed_waveforms = phi_transform.sweep_k(
        waveform_base, k_min=0.20, k_max=0.40, k_step=0.05
    )

    print(f"Tested {len(k_values)} k values: {k_values}")

    # Extract features for each k
    extractor = SpectralFeatureExtractor(fft_size=256)
    spectrum_base = extractor.compute_spectrum(waveform_base)

    results = []
    for k, waveform_k in zip(k_values, transformed_waveforms):
        # Apply arcsin
        waveform_final = arcsin_bridge(waveform_k, alpha=0.95)
        spectrum_final = extractor.compute_spectrum(waveform_final)

        # Extract features
        features = extractor.extract_all_features(spectrum_base, spectrum_final)
        results.append(
            {
                "k": k,
                "delta_entropy": features["delta_entropy"],
                "delta_f1": features["delta_f1"],
                "composite_score": features["composite_disruption_score"],
            }
        )

    # Plot results
    print("\nK-sweep results:")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    k_vals = [r["k"] for r in results]

    axes[0].plot(k_vals, [r["delta_entropy"] for r in results], "o-")
    axes[0].set_xlabel("k parameter")
    axes[0].set_ylabel("ΔEntropy")
    axes[0].set_title("Entropy vs k")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(k_vals, [r["delta_f1"] for r in results], "o-")
    axes[1].set_xlabel("k parameter")
    axes[1].set_ylabel("Δf₁ (%)")
    axes[1].set_title("Fundamental Peak Change vs k")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(k_vals, [r["composite_score"] for r in results], "o-")
    axes[2].set_xlabel("k parameter")
    axes[2].set_ylabel("Composite Score")
    axes[2].set_title("Composite Disruption Score vs k")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # Find optimal k
    optimal_idx = np.argmax([r["composite_score"] for r in results])
    optimal_k = results[optimal_idx]["k"]
    print(f"\nOptimal k (max composite score): {optimal_k:.3f}")

    return fig, results


def demonstrate_batch_analysis():
    """Demonstrate batch analysis of multiple sequences."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Batch Analysis")
    print("=" * 80)

    # Multiple test sequences
    sequences = [
        "ATCGATCGATCGATCGATCG",  # Balanced
        "AAAACCCCGGGGTTTTAAAA",  # GC-rich blocks
        "GCGCGCGCGCGCGCGCGCGC",  # High GC, alternating
        "ATATATATATATATATATAT",  # Low GC, repetitive
        "TACGTACGTACGTACGTACG",  # Mixed
    ]

    print(f"\nAnalyzing {len(sequences)} sequences...")

    extractor = SpectralFeatureExtractor(fft_size=256)
    results = []

    for i, seq in enumerate(sequences):
        # Encode and transform
        waveform_base = encode_dna_complex(seq)
        _, waveform_final, _ = combined_transform(waveform_base, k=0.3, alpha=0.95)

        # Compute spectra
        spectrum_base = extractor.compute_spectrum(waveform_base)
        spectrum_final = extractor.compute_spectrum(waveform_final)

        # Extract features
        features = extractor.extract_all_features(spectrum_base, spectrum_final)

        results.append(
            {
                "sequence": seq[:10] + "...",
                "gc_content": compute_gc_content(seq),
                "delta_entropy": features["delta_entropy"],
                "delta_f1": features["delta_f1"],
                "composite_score": features["composite_disruption_score"],
            }
        )

    # Print results table
    print("\nResults:")
    print(
        f"{'Sequence':<15} {'GC%':<8} {'ΔEntropy':<12} {'Δf₁ (%)':<12} {'Composite':<12}"
    )
    print("-" * 70)
    for r in results:
        print(
            f"{r['sequence']:<15} {r['gc_content']:>6.1f}% "
            f"{r['delta_entropy']:>10.4f}  {r['delta_f1']:>10.2f}  "
            f"{r['composite_score']:>10.2f}"
        )

    return results


def main():
    """Main demonstration entry point."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print(
        "║" + " " * 10 + "CRISPR Spectral Resonance Optimization Demo" + " " * 25 + "║"
    )
    print("╚" + "=" * 78 + "╝")

    # Demo 1: Single sequence
    try:
        fig1, fig2, features = demonstrate_single_sequence()
        print("\n✓ Single sequence analysis complete")
    except Exception as e:
        print(f"\n✗ Error in single sequence demo: {e}")

    # Demo 2: K-sweep
    try:
        fig_sweep, sweep_results = demonstrate_k_sweep()
        print("\n✓ K-parameter sweep complete")
    except Exception as e:
        print(f"\n✗ Error in k-sweep demo: {e}")

    # Demo 3: Batch analysis
    try:
        batch_results = demonstrate_batch_analysis()
        print("\n✓ Batch analysis complete")
    except Exception as e:
        print(f"\n✗ Error in batch demo: {e}")

    print("\n" + "=" * 80)
    print("All demonstrations complete!")
    print("=" * 80)

    # Show plots (if not in headless mode)
    try:
        plt.show()
    except Exception:
        print("\nNote: Running in headless mode, plots not displayed")
        print("Figures generated but not shown")


if __name__ == "__main__":
    main()
