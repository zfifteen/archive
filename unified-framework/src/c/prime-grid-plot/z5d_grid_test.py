#!/usr/bin/env python3
"""
Z5D RSA Prime Grid Analysis - Using Z5D key generator for rapid testing
WARNING: FOR EDUCATIONAL USE ONLY
"""
import subprocess
import os
import re
import time
import argparse
from collections import Counter
import numpy as np
from pathlib import Path
import scipy.stats as stats  # For KDE
import seaborn as sns  # For enhanced density visualization

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

def get_adaptive_grid_size_v2(number):
    """Calculate adaptive grid size: minimum 8x8, scale up when dps/2 > 8"""
    decimal_places = len(str(number))
    calculated_size = decimal_places // 2
    grid_size = max(8, calculated_size)
    return grid_size

def map_to_adaptive_grid_v2(number):
    """Map number to adaptive grid coordinates v2"""
    grid_size = get_adaptive_grid_size_v2(number)

    # Convert number to string and split into halves
    num_str = str(number)
    mid_point = len(num_str) // 2

    left_half = num_str[:mid_point] if mid_point > 0 else "0"
    right_half = num_str[mid_point:] if mid_point < len(num_str) else "0"

    # Convert to integers
    left_val = int(left_half) if left_half else 0
    right_val = int(right_half) if right_half else 0

    # Map to grid coordinates using modulo
    x_coord = left_val % grid_size
    y_coord = right_val % grid_size

    return x_coord, y_coord, grid_size


def map_moduli_to_coords(moduli):
    """Map a list of moduli to adaptive grid coordinates with caching"""
    if not moduli:
        return [], None, None

    decimal_places = max(len(str(modulus)) for modulus in moduli)
    grid_size = max(8, decimal_places // 2)
    mid_point = decimal_places // 2

    coords = []
    for modulus in moduli:
        num_str = str(modulus).zfill(decimal_places)
        left_half = num_str[:mid_point] if mid_point > 0 else "0"
        right_half = num_str[mid_point:] if mid_point < len(num_str) else num_str

        left_val = int(left_half) if left_half else 0
        right_val = int(right_half) if right_half else 0

        x_coord = left_val % grid_size
        y_coord = right_val % grid_size
        coords.append((x_coord, y_coord))

    return coords, grid_size, decimal_places

def build_z5d_generator():
    """Check if Z5D generator exists and is built"""
    z5d_path = Path("../4096-pipeline")
    executable = z5d_path / "z5d_secure_key_gen"

    if not z5d_path.exists():
        print("❌ Z5D pipeline directory not found at ../4096-pipeline")
        return None

    if executable.exists():
        print(f"✓ Z5D generator found: {executable}")
        return executable

    # Try to build it
    print("Building Z5D generator...")
    try:
        result = subprocess.run(["make"], cwd=z5d_path, capture_output=True, text=True)
        if result.returncode == 0 and executable.exists():
            print(f"✓ Z5D generator built successfully: {executable}")
            return executable
        else:
            print(f"❌ Build failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Build error: {e}")
        return None

def generate_z5d_keys(executable, count):
    """Generate RSA keys using Z5D generator"""
    print(f"Generating {count} RSA-4096 key(s) using Z5D generator...")

    keys_generated = []
    script_dir = Path(__file__).resolve().parent
    generated_dir = script_dir / "generated"

    if not generated_dir.exists():
        generated_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        print(f"  Generating key {i+1}/{count}...", end=" ", flush=True)

        start_time = time.time()
        existing_keys = set(p.name for p in generated_dir.glob("*.key")) if generated_dir.exists() else set()
        existing_certs = set(p.name for p in generated_dir.glob("*.crt")) if generated_dir.exists() else set()
        try:
            # Run Z5D generator (normal mode to see output)
            result = subprocess.run([str(executable)],
                                  cwd=script_dir,
                                  capture_output=True, text=True, timeout=300)

            generation_time = time.time() - start_time

            if result.returncode == 0:
                # Parse output to get filenames
                output_lines = result.stdout.strip().split('\n')
                key_file = None
                cert_file = None

                for line in output_lines:
                    if line.startswith("Wrote private key:"):
                        key_file = line.split(": ")[1]
                    elif line.startswith("Wrote certificate:"):
                        cert_file = line.split(": ")[1]

                if not key_file:
                    # Fall back to detecting newly created files in generated/
                    current_keys = set(p.name for p in generated_dir.glob("*.key"))
                    current_certs = set(p.name for p in generated_dir.glob("*.crt"))

                    new_keys = sorted(current_keys - existing_keys)
                    new_certs = sorted(current_certs - existing_certs)

                    if new_keys:
                        key_file = f"generated/{new_keys[-1]}"
                    if new_certs:
                        cert_file = f"generated/{new_certs[-1]}"

                if key_file:
                    key_path = Path(key_file)
                    cert_path = Path(cert_file) if cert_file else None

                    if not key_path.is_absolute():
                        key_path = script_dir / key_path
                    if cert_path and not cert_path.is_absolute():
                        cert_path = script_dir / cert_path

                    keys_generated.append({
                        'key_file': str(key_path),
                        'cert_file': str(cert_path) if cert_path else None,
                        'generation_time': generation_time
                    })
                    print(f"✓ ({generation_time:.1f}s)")
                else:
                    print(f"❌ No key file found in output")
                    print(f"Debug output: {result.stdout[:200]}...")
            else:
                print(f"❌ Generation failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout after 5 minutes")
        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"Successfully generated {len(keys_generated)} keys")
    return keys_generated

def extract_public_modulus(key_file):
    """Extract only the public modulus n from RSA key"""
    try:
        # Use openssl to extract the public modulus
        cmd = ["openssl", "rsa", "-in", key_file, "-noout", "-modulus"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ OpenSSL modulus extraction failed: {result.stderr}")
            return None

        # Parse modulus (format: "Modulus=HEXSTRING")
        modulus_line = result.stdout.strip()
        if not modulus_line.startswith("Modulus="):
            print("❌ Unexpected modulus format")
            return None

        modulus_hex = modulus_line[8:]  # Remove "Modulus=" prefix
        n = int(modulus_hex, 16)

        return n

    except Exception as e:
        print(f"❌ Modulus extraction error: {e}")
        return None

def grid_factorize(n, timeout_seconds=60):
    """Attempt to factor n using grid-based search"""
    print(f"Attempting grid factorization of {len(str(n))}-digit modulus...")

    start_time = time.time()

    # For RSA-4096, this is a demonstration - real cryptographic factorization
    # would require sophisticated algorithms like quadratic sieve or GNFS

    # Calculate approximate square root using string arithmetic
    n_str = str(n)
    n_digits = len(n_str)
    sqrt_digits = (n_digits + 1) // 2

    print(f"Expected factor size: ~{sqrt_digits} digit primes")
    print(f"Grid size would be: {get_adaptive_grid_size_v2(10**(sqrt_digits-1))}×{get_adaptive_grid_size_v2(10**(sqrt_digits-1))}")

    # For demonstration: try very small factors only (this will fail on real RSA-4096)
    print("Attempting trial division up to 10,000 (demonstration only)...")

    limit = 10000
    for i in range(3, limit, 2):
        if time.time() - start_time > timeout_seconds:
            print(f"⚠️  Timeout after {timeout_seconds}s")
            return None, None

        if i % 1000 == 3:  # Progress indicator
            print(f"  Tested up to {i}...")

        if n % i == 0:
            p = i
            q = n // i
            print(f"✓ Found factors: {p} × {q}")
            return p, q

    print(f"❌ No small factors found (expected for cryptographic RSA)")
    print(f"Note: Real RSA-4096 factorization requires advanced algorithms")
    return None, None

def train_grid_model(training_moduli):
    """Train grid model on training data to identify high-density regions"""
    if not training_moduli:
        print("❌ No training moduli provided")
        return None

    print(f"\nTRAINING GRID MODEL ON {len(training_moduli)} RSA MODULI")
    print("=" * 55)

    # Analyze grid characteristics
    sample_modulus = training_moduli[0]
    decimal_places = len(str(sample_modulus))
    grid_size = get_adaptive_grid_size_v2(sample_modulus)

    print(f"Training sample: {str(sample_modulus)[:50]}...{str(sample_modulus)[-20:]}")
    print(f"Decimal places: {decimal_places}")
    print(f"Grid size: {grid_size}×{grid_size}")
    print(f"Total grid cells: {grid_size**2:,}")

    # Map training moduli to grid coordinates
    coord_counts = {}
    for modulus in training_moduli:
        x, y, _ = map_to_adaptive_grid_v2(modulus)
        coord_key = (x, y)
        coord_counts[coord_key] = coord_counts.get(coord_key, 0) + 1

    # Identify "high-density" regions (any cell with >= 1 modulus in training)
    high_density_coords = list(coord_counts.keys())

    total_grid_cells = grid_size * grid_size
    model_coverage = len(high_density_coords) / total_grid_cells

    print(f"Training results:")
    print(f"  Training moduli mapped: {len(training_moduli)}")
    print(f"  Unique cells occupied: {len(high_density_coords)}")
    print(f"  Model coverage: {model_coverage:.6f}x of total grid")
    print(f"  Predicted 'hot zones': {len(high_density_coords):,} cells")

    return {
        'grid_size': grid_size,
        'high_density_coords': high_density_coords,
        'total_grid_cells': total_grid_cells,
        'model_coverage': model_coverage,
        'training_count': len(training_moduli)
    }

# Rename to avoid pytest interpreting as test function
def evaluate_grid_model(model, test_moduli):
    """Evaluate grid model predictive power on unseen test data"""
    if not model or not test_moduli:
        print("❌ Invalid model or test data")
        return None

    print(f"\nEVALUATING GRID MODEL ON {len(test_moduli)} NEW RSA MODULI")
    print("=" * 55)

    # Evaluate if new moduli fall in predicted high-density regions
    hits = 0
    misses = 0

    for modulus in test_moduli:
        x, y, _ = map_to_adaptive_grid_v2(modulus)
        if (x, y) in model['high_density_coords']:
            hits += 1
        else:
            misses += 1

    hit_rate = (hits / len(test_moduli)) * 100 if test_moduli else 0
    expected_hit_rate = model['model_coverage'] * 100

    print(f"Evaluation results:")
    print(f"  Test moduli: {len(test_moduli)}")
    print(f"  Hits (predicted regions): {hits}")
    print(f"  Misses (unpredicted regions): {misses}")
    print(f"  Actual hit rate: {hit_rate:.1f}%")
    print(f"  Expected hit rate (random): {expected_hit_rate:.3f}%")

    if hit_rate > expected_hit_rate * 1.5:
        status = "✓ Model shows predictive power"
        conclusion = "Grid method may have found meaningful patterns"
    elif hit_rate < expected_hit_rate * 0.5:
        status = "⚠️ Model performs worse than random"
        conclusion = "Grid method may be anti-predictive"
    else:
        status = "~ Model performs as expected for random distribution"
        conclusion = "No evidence of exploitable patterns (expected for secure RSA)"

    print(f"  Status: {status}")
    print(f"  Conclusion: {conclusion}")

    return {
        'hit_rate': hit_rate,
        'expected_hit_rate': expected_hit_rate,
        'hits': hits,
        'misses': misses,
        'status': status,
        'conclusion': conclusion
    }

def analyze_z5d_primes(primes):
    """Analyze prime factors using adaptive grid"""
    if not primes:
        print("❌ No primes to analyze")
        return None

    print(f"\nANALYZING {len(primes)} Z5D-GENERATED PRIMES")
    print("=" * 50)

    # Analyze first prime for grid characteristics
    sample_prime = primes[0]
    decimal_places = len(str(sample_prime))
    calculated_size = decimal_places // 2
    grid_size = get_adaptive_grid_size_v2(sample_prime)

    print(f"Sample prime: {str(sample_prime)[:50]}...{str(sample_prime)[-20:]}")
    print(f"Decimal places: {decimal_places}")
    print(f"Calculated grid size: {calculated_size}")
    print(f"Actual grid size: {grid_size}×{grid_size}")
    print(f"Total grid cells: {grid_size**2:,}")

    # Map all primes to grid coordinates
    coords = []
    coord_counts = {}

    for prime in primes:
        x, y, _ = map_to_adaptive_grid_v2(prime)
        coords.append((x, y))
        coord_key = (x, y)
        coord_counts[coord_key] = coord_counts.get(coord_key, 0) + 1

    # Calculate metrics
    total_unique_coords = len(coord_counts)
    densities = list(coord_counts.values())
    max_density = max(densities) if densities else 0
    avg_density = np.mean(densities) if densities else 0

    # Test 50th percentile threshold
    threshold = np.percentile(densities, 50) if densities else 0
    high_density_coords = [coord for coord, count in coord_counts.items() if count >= threshold]

    # Calculate reduction metrics
    total_grid_cells = grid_size * grid_size
    reduction_percent = (1 - len(high_density_coords) / total_grid_cells) * 100 if total_grid_cells > 0 else 0
    grid_utilization = (total_unique_coords / total_grid_cells) * 100 if total_grid_cells > 0 else 0

    # Check capture rate
    captured_primes = sum(1 for prime in primes
                         if map_to_adaptive_grid_v2(prime)[:2] in high_density_coords)
    capture_rate = (captured_primes / len(primes)) * 100 if primes else 0

    # Calculate compression ratio
    compression_ratio = int(1 / (len(high_density_coords) / total_grid_cells)) if len(high_density_coords) > 0 else 0

    print(f"\nGRID ANALYSIS RESULTS:")
    print(f"  Grid utilization: {grid_utilization:.1f}% ({total_unique_coords}/{total_grid_cells} cells)")
    print(f"  Density stats: avg={avg_density:.1f}, max={max_density}")
    print(f"  50%ile threshold: {threshold:.1f}")
    print(f"  High-density cells: {len(high_density_coords)}")
    print(f"  Reduction: {reduction_percent:.2f}%")
    print(f"  Capture rate: {capture_rate:.1f}%")
    print(f"  Search multiplier: {len(high_density_coords) / total_grid_cells:.6f}x")
    print(f"  Compression ratio: {compression_ratio}:1")

    status = "✓ Perfect" if capture_rate == 100 else f"~ {capture_rate:.0f}%"
    print(f"  Status: {status}")

    return {
        'grid_size': grid_size,
        'decimal_places': decimal_places,
        'total_grid_cells': total_grid_cells,
        'reduction_percent': reduction_percent,
        'capture_rate': capture_rate,
        'compression_ratio': compression_ratio,
        'grid_utilization': grid_utilization,
        'high_density_cells': len(high_density_coords),
        'unique_coords': total_unique_coords
    }


def analyze_z5d_moduli(moduli):
    """Analyze RSA moduli using the adaptive grid heuristic"""
    if not moduli:
        print("❌ No moduli to analyze")
        return None

    print(f"\nANALYZING {len(moduli)} RSA MODULI")
    print("=" * 45)

    coords, grid_size, decimal_places = map_moduli_to_coords(moduli)

    sample_modulus = moduli[0]
    calculated_size = decimal_places // 2

    print(f"Sample modulus: {str(sample_modulus)[:50]}...{str(sample_modulus)[-20:]}")
    print(f"Decimal places: {decimal_places}")
    print(f"Calculated grid size: {calculated_size}")
    print(f"Actual grid size: {grid_size}×{grid_size}")
    print(f"Total grid cells: {grid_size**2:,}")
    coord_counts = Counter(coords)

    total_unique_coords = len(coord_counts)
    densities = list(coord_counts.values())
    max_density = max(densities) if densities else 0
    avg_density = np.mean(densities) if densities else 0

    threshold = np.percentile(densities, 50) if densities else 0
    high_density_coords = [coord for coord, count in coord_counts.items() if count >= threshold]

    total_grid_cells = grid_size * grid_size
    reduction_percent = (1 - len(high_density_coords) / total_grid_cells) * 100 if total_grid_cells > 0 else 0
    grid_utilization = (total_unique_coords / total_grid_cells) * 100 if total_grid_cells > 0 else 0

    high_density_coord_set = set(high_density_coords)
    captured_moduli = sum(1 for coord in coords if coord in high_density_coord_set)
    capture_rate = (captured_moduli / len(moduli)) * 100 if moduli else 0

    compression_ratio = int(1 / (len(high_density_coords) / total_grid_cells)) if len(high_density_coords) > 0 else 0

    print(f"\nGRID ANALYSIS RESULTS:")
    print(f"  Grid utilization: {grid_utilization:.1f}% ({total_unique_coords}/{total_grid_cells} cells)")
    print(f"  Density stats: avg={avg_density:.1f}, max={max_density}")
    print(f"  50%ile threshold: {threshold:.1f}")
    print(f"  High-density cells: {len(high_density_coords)}")
    print(f"  Reduction: {reduction_percent:.2f}%")
    print(f"  Capture rate: {capture_rate:.1f}%")
    print(f"  Search multiplier: {len(high_density_coords) / total_grid_cells:.6f}x")
    print(f"  Compression ratio: {compression_ratio}:1")

    status = "✓ Perfect" if capture_rate == 100 else f"~ {capture_rate:.0f}%"
    print(f"  Status: {status}")

    return {
        'grid_size': grid_size,
        'decimal_places': decimal_places,
        'total_grid_cells': total_grid_cells,
        'reduction_percent': reduction_percent,
        'capture_rate': capture_rate,
        'compression_ratio': compression_ratio,
        'grid_utilization': grid_utilization,
        'high_density_cells': len(high_density_coords),
        'unique_coords': total_unique_coords,
        'coord_counts': coord_counts,
        'coords': coords,
        'densities': densities,
        'high_density_coords': high_density_coords
    }


def generate_moduli_plots(plot_dir, analysis, generation_times, extraction_times):
    """Generate visualizations for the analyzed moduli"""
    plot_path = Path(plot_dir)
    plot_path.mkdir(parents=True, exist_ok=True)

    grid_size = analysis['grid_size']
    total_grid_cells = analysis['total_grid_cells']
    coord_counts = analysis['coord_counts']
    coords = analysis['coords']
    densities = analysis['densities'] or [0]
    high_density_cells = analysis['high_density_cells']

    # Heatmap of grid occupancy
    if coord_counts:
        heatmap = np.zeros((grid_size, grid_size), dtype=int)
        for (x, y), count in coord_counts.items():
            if 0 <= x < grid_size and 0 <= y < grid_size:
                heatmap[y, x] = count

        fig, ax = plt.subplots(figsize=(8, 6))
        vmax = heatmap.max()
        if vmax > 0:
            im = ax.imshow(heatmap + 1e-9, cmap='viridis', norm=LogNorm(vmin=1, vmax=vmax))
        else:
            im = ax.imshow(heatmap, cmap='viridis')
        ax.set_title(f"RSA Moduli Grid Heatmap ({grid_size}×{grid_size})")
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')
        fig.colorbar(im, ax=ax, label='Moduli per cell (log scale)')
        fig.tight_layout()
        fig.savefig(plot_path / 'moduli_heatmap.png', dpi=150)
        plt.close(fig)

    # Scatter plot of coordinates
    if coords:
        xs, ys = zip(*coords)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(xs, ys, c='dodgerblue', edgecolors='black', s=20, alpha=0.7)
        ax.set_title('RSA Moduli Coordinates on Adaptive Grid')
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')
        ax.set_xlim(-1, grid_size)
        ax.set_ylim(-1, grid_size)
        ax.grid(alpha=0.2)
        fig.tight_layout()
        fig.savefig(plot_path / 'moduli_scatter.png', dpi=150)
        plt.close(fig)

    # Cumulative coverage curve
    densities_sorted = sorted(coord_counts.values(), reverse=True) if coord_counts else []
    if densities_sorted:
        cumulative_moduli = np.cumsum(densities_sorted)
        cumulative_cells = np.arange(1, len(densities_sorted) + 1)
        coverage_percent = (cumulative_cells / total_grid_cells) * 100
        capture_percent = (cumulative_moduli / cumulative_moduli[-1]) * 100

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(coverage_percent, capture_percent, label='Actual coverage', linewidth=2)
        ax.plot([0, 100], [0, 100], linestyle='--', color='gray', label='Random baseline')
        ax.set_title('Cumulative Grid Coverage vs. Moduli Capture')
        ax.set_xlabel('Cumulative grid coverage (%)')
        ax.set_ylabel('Cumulative moduli captured (%)')
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(plot_path / 'cumulative_coverage.png', dpi=150)
        plt.close(fig)

    # Generation & extraction timing bars
    if generation_times or extraction_times:
        indices = np.arange(max(len(generation_times), len(extraction_times)))
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_width = 0.35
        if generation_times:
            gen_vals = [generation_times[i] if i < len(generation_times) else 0 for i in indices]
            ax.bar(indices - bar_width/2, gen_vals, bar_width, label='Generation (s)', color='steelblue')
        if extraction_times:
            ext_vals = [extraction_times[i] if i < len(extraction_times) else 0 for i in indices]
            ax.bar(indices + bar_width/2, ext_vals, bar_width, label='Modulus extraction (s)', color='orange')
        ax.set_title('Per-Key Timing Breakdown')
        ax.set_xlabel('Key index')
        ax.set_ylabel('Seconds')
        ax.set_xticks(indices)
        ax.legend()
        ax.grid(alpha=0.2, axis='y')
        fig.tight_layout()
        fig.savefig(plot_path / 'timing_breakdown.png', dpi=150)
        plt.close(fig)

    # Capture rate vs expected random baseline
    expected_random = (high_density_cells / total_grid_cells) * 100 if total_grid_cells else 0
    actual_capture = analysis['capture_rate']

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(['Actual capture', 'Expected random'], [actual_capture, expected_random], color=['seagreen', 'gray'])
    ax.set_ylim(0, 100)
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Capture Rate vs. Random Baseline')
    for idx, value in enumerate([actual_capture, expected_random]):
        ax.text(idx, value + 1, f"{value:.1f}%", ha='center')
    fig.tight_layout()
    fig.savefig(plot_path / 'capture_vs_random.png', dpi=150)
    plt.close(fig)

    # New: 2D Kernel Density Estimate (KDE) plot for smooth density visualization
    if coords:
        xs, ys = zip(*coords)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.kdeplot(x=xs, y=ys, cmap='viridis', fill=True, ax=ax)
        ax.set_title('Kernel Density Estimate of Moduli Distribution')
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')
        ax.set_xlim(0, grid_size)
        ax.set_ylim(0, grid_size)
        fig.tight_layout()
        fig.savefig(plot_path / 'moduli_kde.png', dpi=150)
        plt.close(fig)

    # New: Annotated high-density scatter plot with density-based sizing
    if coords:
        fig, ax = plt.subplots(figsize=(8, 6))
        # Create list of point sizes based on density
        point_sizes = []
        for x, y in coords:
            density = coord_counts.get((x, y), 0)
            point_sizes.append(20 + (density * 10))  # Scale size by density

        scatter = ax.scatter(xs, ys, s=point_sizes, c=point_sizes, cmap='viridis', alpha=0.7)
        ax.set_title('High-Density Annotated Scatter (Size by Density)')
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')
        ax.set_xlim(-1, grid_size)
        ax.set_ylim(-1, grid_size)
        ax.grid(alpha=0.2)
        fig.colorbar(scatter, ax=ax, label='Point Density')
        # Annotate highest density points
        max_density = max(densities) if densities else 0
        for (x, y), count in coord_counts.items():
            if count >= max_density * 0.8:  # Annotate top 20% densities
                ax.annotate(f'{count}', (x, y), xytext=(5, 5), textcoords='offset points',
                            fontsize=8, color='red')
        fig.tight_layout()
        fig.savefig(plot_path / 'annotated_density_scatter.png', dpi=150)
        plt.close(fig)

    # New: 2D Contour plot of densities
    if coord_counts:
        X, Y = np.mgrid[0:grid_size:complex(0, grid_size), 0:grid_size:complex(0, grid_size)]
        Z = np.zeros((grid_size, grid_size))
        for (x, y), count in coord_counts.items():
            if 0 <= x < grid_size and 0 <= y < grid_size:
                Z[int(y), int(x)] = count  # Note: y is row, x is column

        fig, ax = plt.subplots(figsize=(8, 6))
        contour = ax.contourf(X, Y, Z, cmap='viridis', levels=10)
        ax.set_title('Contour Plot of Moduli Density')
        ax.set_xlabel('x coordinate')
        ax.set_ylabel('y coordinate')
        fig.colorbar(contour, ax=ax, label='Density Level')
        fig.tight_layout()
        fig.savefig(plot_path / 'moduli_contour.png', dpi=150)
        plt.close(fig)

def cleanup_generated_files(keys_generated):
    """Clean up generated key and certificate files"""
    print(f"\nCleaning up {len(keys_generated)} generated files...")

    for key_info in keys_generated:
        for file_path in [key_info.get('key_file'), key_info.get('cert_file')]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"  Removed: {file_path}")
                except Exception as e:
                    print(f"  ❌ Could not remove {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Z5D RSA Prime Grid Analysis')
    parser.add_argument('--keys', type=int, default=1,
                       help='Number of RSA-4096 keys to generate and analyze (default: 1)')
    parser.add_argument('--keep-files', action='store_true',
                       help='Keep generated key files (default: cleanup)')
    parser.add_argument('--plot-dir', type=str, default='plots',
                       help='Directory to store generated plots (default: ./plots)')
    parser.add_argument('--no-plots', action='store_true',
                       help='Disable plot generation')
    parser.add_argument('--evaluate-model', action='store_true',
                       help='Split collected moduli into train/test sets and evaluate grid coverage')

    args = parser.parse_args()

    print("Z5D RSA PRIME GRID ANALYSIS")
    print("=" * 35)
    print("WARNING: FOR EDUCATIONAL USE ONLY")
    print(f"Target: Generate {args.keys} RSA-4096 key(s)")
    print()

    # Build/find Z5D generator
    executable = build_z5d_generator()
    if not executable:
        return 1

    # Generate RSA keys
    start_time = time.time()
    keys_generated = generate_z5d_keys(executable, args.keys)

    if not keys_generated:
        print("❌ No keys generated successfully")
        return 1

    # Extract public moduli for grid analysis
    all_moduli = []
    extraction_times = []

    for i, key_info in enumerate(keys_generated):
        print(f"Extracting modulus from key {i+1}...", end=" ")
        extract_start = time.time()
        n = extract_public_modulus(key_info['key_file'])

        if n:
            all_moduli.append(n)
            extraction_times.append(time.time() - extract_start)
            print(f"✓ ({len(str(n))} digits)")
        else:
            print("❌ Extraction failed")

    total_time = time.time() - start_time

    if not all_moduli:
        print("❌ No moduli extracted successfully")
        if not args.keep_files:
            cleanup_generated_files(keys_generated)
        return 1

    print(f"\nExtracted {len(all_moduli)} RSA moduli in {total_time:.1f}s total")

    # Analyze moduli with adaptive grid
    results = analyze_z5d_moduli(all_moduli)

    if results:
        print(f"\n" + "=" * 60)
        print("Z5D RSA MODULI GRID ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Keys generated: {len(keys_generated)}")
        print(f"Moduli analyzed: {len(all_moduli)}")
        print(f"Grid configuration: {results['grid_size']}×{results['grid_size']}")
        print(f"Search space reduction: {results['reduction_percent']:.2f}%")
        print(f"Compression ratio: {results['compression_ratio']}:1")
        print(f"Capture rate: {results['capture_rate']:.1f}%")
        print(f"Total pipeline time: {total_time:.1f}s")
        print()
        print("Educational demonstration: Adaptive grid filtering on authentic RSA moduli")

        if not args.no_plots:
            plot_dir = Path(args.plot_dir)
            generation_times = [info.get('generation_time', 0) for info in keys_generated]
            generate_moduli_plots(plot_dir, results, generation_times, extraction_times)
            print(f"Plot artifacts saved to {plot_dir.resolve()}")

        if args.evaluate_model:
            if len(all_moduli) < 2:
                print("⚠️  Need at least two moduli to evaluate the grid model (train/test split).")
            else:
                split_index = max(1, len(all_moduli) // 2)
                train_moduli = all_moduli[:split_index]
                test_moduli = all_moduli[split_index:]
                model = train_grid_model(train_moduli)
                evaluation = evaluate_grid_model(model, test_moduli)
                if evaluation:
                    print("\nMODEL EVALUATION SUMMARY")
                    print(f"  Train set size: {len(train_moduli)}")
                    print(f"  Test set size: {len(test_moduli)}")
                    print(f"  Hit rate: {evaluation['hit_rate']:.1f}%")
                    print(f"  Expected random hit rate: {evaluation['expected_hit_rate']:.3f}%")

    # Cleanup unless requested to keep files
    if not args.keep_files:
        cleanup_generated_files(keys_generated)

    return 0

if __name__ == "__main__":
    exit(main())
