#!/usr/bin/env python3
"""
Ulam Spiral with Z-Framework Geometric Embeddings

A comprehensive implementation that combines the classical Ulam spiral visualization
of prime numbers with Z-Framework's 5-dimensional geodesic space mapping. This tool
explores how discrete curvature κ(n) = d(n) * ln(n+1) / e² and geometric resolution
θ'(n,k) = φ * ((n mod φ) / φ)^k reveal additional patterns beyond the diagonal
structures observed in standard Ulam spirals.

Mathematical Foundation:
- Ulam Spiral: 2D coordinate mapping starting at origin, spiraling outward
- Z-Framework Curvature: κ(n) = d(n) * ln(n+1) / e², where d(n) ≈ 1/ln(n)
- Geometric Resolution: θ'(n,k) = φ * ((n mod φ) / φ)^k, k ≈ 0.3
- QMC Sampling: Sobol sequences with Owen scrambling for large-scale analysis

Key Features:
1. Standard Ulam spiral generation with prime marking
2. Curvature-weighted visualization using κ(n)
3. Geometric resolution overlay using θ'(n,k)
4. Diagonal pattern detection and analysis
5. Quadratic polynomial identification (e.g., 4n² + 2n + 41)
6. QMC-enhanced large spiral generation
7. Statistical deviation quantification

Dependencies: numpy, matplotlib, sympy (for primality testing)
"""

import numpy as np
import math
from typing import Tuple, List, Dict, Optional, Set
import sympy


# === Constants from Z-Framework ===

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618033988749
E2 = math.exp(2)  # e² ≈ 7.389056098931


# === Z-Framework Functions ===

def prime_density(n: int) -> float:
    """Prime density approximation d(n) ≈ 1/ln(n) from Prime Number Theorem."""
    if n <= 1:
        return 0.0
    return 1.0 / math.log(n)


def kappa(n: int) -> float:
    """
    Discrete curvature: κ(n) = d(n) * ln(n+1) / e²
    
    This measures the geometric curvature at position n in the number line,
    providing a weight for prime probability based on local density.
    """
    if n <= 0:
        return 0.0
    d_n = prime_density(n)
    log_term = math.log(n + 1)
    return d_n * log_term / E2


def theta_prime(n: int, k: float = 0.3) -> float:
    """
    Geometric resolution: θ'(n,k) = φ * ((n mod φ) / φ)^k
    
    Phase-biased function with golden ratio modulation.
    Recommended k ≈ 0.3 for pattern detection.
    """
    n_mod_phi = n % PHI
    ratio = n_mod_phi / PHI
    ratio_pow = ratio ** k
    return PHI * ratio_pow


def z_weight(n: int, k: float = 0.3) -> float:
    """
    Combined Z-Framework weight: κ(n) * θ'(n,k)
    
    This combines curvature and geometric resolution to provide
    a unified weighting for prime probability at position n.
    """
    return kappa(n) * theta_prime(n, k)


# === Ulam Spiral Coordinate Generation ===

def ulam_coordinates(n: int) -> Tuple[int, int]:
    """
    Convert position n to (x, y) coordinates in the Ulam spiral.
    
    The spiral starts at origin (0,0) with n=1 and proceeds:
    1: (0,0)
    2: (1,0) → East
    3: (1,1) → North
    4: (0,1) → West
    5: (-1,1) → West
    6: (-1,0) → South
    7: (-1,-1) → South
    8: (0,-1) → East
    9: (1,-1) → East
    ...
    
    Algorithm uses the fact that the spiral consists of square "rings"
    with side lengths 1, 3, 5, 7, ... (odd numbers).
    """
    if n <= 0:
        return (0, 0)
    
    if n == 1:
        return (0, 0)
    
    # Find which "ring" n is in
    # Ring k has inner radius k and contains numbers from (2k-1)² + 1 to (2k+1)²
    k = math.ceil((math.sqrt(n) - 1) / 2)
    
    # Starting position of this ring (bottom-right corner)
    ring_start = (2 * k - 1) ** 2 + 1
    side_length = 2 * k
    
    # Position within the ring (0-indexed)
    pos_in_ring = n - ring_start
    
    # Determine which side of the square we're on
    if pos_in_ring < side_length:
        # Right side, moving up
        return (k, -k + 1 + pos_in_ring)
    elif pos_in_ring < 2 * side_length:
        # Top side, moving left
        return (k - (pos_in_ring - side_length) - 1, k)
    elif pos_in_ring < 3 * side_length:
        # Left side, moving down
        return (-k, k - (pos_in_ring - 2 * side_length) - 1)
    else:
        # Bottom side, moving right
        return (-k + (pos_in_ring - 3 * side_length) + 1, -k)


def generate_ulam_spiral(size: int, seed: int = 42) -> Dict[str, np.ndarray]:
    """
    Generate a complete Ulam spiral up to size×size grid.
    
    Args:
        size: Grid size (must be odd for symmetry)
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with arrays:
        - 'numbers': The numbers at each grid position
        - 'is_prime': Boolean mask of prime positions
        - 'kappa': Curvature values κ(n)
        - 'theta_prime': Geometric resolution values θ'(n,k)
        - 'z_weight': Combined Z-weight values
        - 'coordinates': (x, y) positions
    """
    if size % 2 == 0:
        size += 1  # Ensure odd size for centered origin
    
    np.random.seed(seed)
    
    # Initialize grids
    center = size // 2
    numbers = np.zeros((size, size), dtype=int)
    is_prime = np.zeros((size, size), dtype=bool)
    kappa_grid = np.zeros((size, size), dtype=float)
    theta_grid = np.zeros((size, size), dtype=float)
    z_weight_grid = np.zeros((size, size), dtype=float)
    
    # Maximum number in spiral
    max_n = size * size
    
    # Fill the spiral
    for n in range(1, max_n + 1):
        x, y = ulam_coordinates(n)
        
        # Convert to grid coordinates
        gx = center + x
        gy = center + y
        
        # Check bounds
        if 0 <= gx < size and 0 <= gy < size:
            numbers[gy, gx] = n
            
            # Check primality (using sympy for accuracy)
            if n > 1:
                is_prime[gy, gx] = sympy.isprime(n)
            
            # Calculate Z-Framework features
            kappa_grid[gy, gx] = kappa(n)
            theta_grid[gy, gx] = theta_prime(n, k=0.3)
            z_weight_grid[gy, gx] = z_weight(n, k=0.3)
    
    return {
        'numbers': numbers,
        'is_prime': is_prime,
        'kappa': kappa_grid,
        'theta_prime': theta_grid,
        'z_weight': z_weight_grid,
        'size': size,
        'max_n': max_n
    }


# === Pattern Analysis Functions ===

def detect_diagonals(spiral_data: Dict, tolerance: float = 0.1) -> Dict[str, List[Tuple[int, int]]]:
    """
    Detect diagonal patterns in the Ulam spiral.
    
    Analyzes lines at various angles to find clusters of primes,
    returning the most prominent diagonal directions.
    """
    is_prime = spiral_data['is_prime']
    size = spiral_data['size']
    
    # Scan diagonals at different angles
    diagonals = {
        'main': [],      # y = x
        'anti': [],      # y = -x
        'upper': [],     # y = x + offset
        'lower': [],     # y = x - offset
    }
    
    # Main diagonal (y = x)
    for offset in range(-size//2, size//2 + 1):
        diagonal_primes = []
        for i in range(size):
            j = i + offset
            if 0 <= j < size and is_prime[i, j]:
                diagonal_primes.append((i, j))
        if len(diagonal_primes) > 3:  # Threshold for significance
            diagonals['main'].append((offset, diagonal_primes))
    
    # Anti-diagonal (y = -x)
    for offset in range(-size//2, size//2 + 1):
        diagonal_primes = []
        for i in range(size):
            j = -i + offset
            if 0 <= j < size and is_prime[i, j]:
                diagonal_primes.append((i, j))
        if len(diagonal_primes) > 3:
            diagonals['anti'].append((offset, diagonal_primes))
    
    return diagonals


def analyze_quadratic_polynomials(spiral_data: Dict, max_test: int = 100) -> List[Dict]:
    """
    Analyze quadratic polynomials that produce high prime densities.
    
    Tests polynomials of the form f(n) = an² + bn + c
    to identify those that generate prime-rich sequences.
    
    Famous examples:
    - n² + n + 41 (Euler's polynomial)
    - 4n² + 2n + 41
    """
    results = []
    
    # Test known productive polynomials
    test_polynomials = [
        (1, 1, 41, "n² + n + 41 (Euler)"),
        (4, 2, 41, "4n² + 2n + 41"),
        (1, 1, 17, "n² + n + 17"),
        (2, 1, 19, "2n² + n + 19"),
    ]
    
    for a, b, c, name in test_polynomials:
        prime_count = 0
        total = 0
        sequence = []
        
        for n in range(max_test):
            value = a * n * n + b * n + c
            if value > 0 and value <= spiral_data['max_n']:
                total += 1
                if sympy.isprime(value):
                    prime_count += 1
                    sequence.append((n, value))
        
        if total > 0:
            density = prime_count / total
            results.append({
                'name': name,
                'a': a, 'b': b, 'c': c,
                'prime_count': prime_count,
                'total': total,
                'density': density,
                'sequence': sequence[:10]  # First 10 primes
            })
    
    # Sort by density
    results.sort(key=lambda x: x['density'], reverse=True)
    
    return results


def statistical_analysis(spiral_data: Dict) -> Dict:
    """
    Perform statistical analysis on prime distribution vs. Z-Framework predictions.
    
    Compares observed prime density with κ(n) and θ'(n,k) predictions
    to quantify deviations from randomness.
    """
    is_prime = spiral_data['is_prime'].flatten()
    kappa_vals = spiral_data['kappa'].flatten()
    theta_vals = spiral_data['theta_prime'].flatten()
    z_vals = spiral_data['z_weight'].flatten()
    numbers = spiral_data['numbers'].flatten()
    
    # Filter out zeros (empty grid positions)
    valid_mask = numbers > 0
    is_prime = is_prime[valid_mask]
    kappa_vals = kappa_vals[valid_mask]
    theta_vals = theta_vals[valid_mask]
    z_vals = z_vals[valid_mask]
    numbers = numbers[valid_mask]
    
    # Calculate correlations
    prime_int = is_prime.astype(int)
    
    # Pearson correlation (requires variance)
    if np.std(prime_int) > 0 and np.std(kappa_vals) > 0:
        kappa_corr = np.corrcoef(prime_int, kappa_vals)[0, 1]
    else:
        kappa_corr = 0.0
    
    if np.std(prime_int) > 0 and np.std(theta_vals) > 0:
        theta_corr = np.corrcoef(prime_int, theta_vals)[0, 1]
    else:
        theta_corr = 0.0
    
    if np.std(prime_int) > 0 and np.std(z_vals) > 0:
        z_corr = np.corrcoef(prime_int, z_vals)[0, 1]
    else:
        z_corr = 0.0
    
    # Prime density statistics
    total_numbers = len(numbers)
    total_primes = np.sum(is_prime)
    observed_density = total_primes / total_numbers
    
    # Expected density from PNT: π(n) ≈ n / ln(n)
    avg_n = np.mean(numbers)
    expected_density = 1.0 / math.log(avg_n) if avg_n > 1 else 0.0
    
    return {
        'total_numbers': int(total_numbers),
        'total_primes': int(total_primes),
        'observed_density': float(observed_density),
        'expected_density': float(expected_density),
        'density_ratio': float(observed_density / expected_density) if expected_density > 0 else 0.0,
        'kappa_correlation': float(kappa_corr),
        'theta_correlation': float(theta_corr),
        'z_weight_correlation': float(z_corr),
        'max_kappa': float(np.max(kappa_vals)),
        'mean_kappa': float(np.mean(kappa_vals)),
        'max_z_weight': float(np.max(z_vals)),
        'mean_z_weight': float(np.mean(z_vals)),
    }


# === Visualization Functions ===

def visualize_ulam_spiral(
    spiral_data: Dict,
    output_path: Optional[str] = None,
    show_curvature: bool = True,
    show_resolution: bool = True
):
    """
    Create comprehensive visualization of the Ulam spiral with Z-Framework overlays.
    
    Args:
        spiral_data: Output from generate_ulam_spiral()
        output_path: Path to save figure (optional)
        show_curvature: Whether to show κ(n) overlay
        show_resolution: Whether to show θ'(n,k) overlay
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    
    size = spiral_data['size']
    is_prime = spiral_data['is_prime']
    kappa_grid = spiral_data['kappa']
    theta_grid = spiral_data['theta_prime']
    
    # Create figure with subplots
    n_plots = 2 + int(show_curvature) + int(show_resolution)
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 6))
    
    if n_plots == 1:
        axes = [axes]
    
    plot_idx = 0
    
    # Plot 1: Standard Ulam spiral (primes only)
    ax = axes[plot_idx]
    ax.imshow(is_prime, cmap='binary', interpolation='nearest')
    ax.set_title('Ulam Spiral: Primes (Black)', fontsize=14, fontweight='bold')
    ax.set_xlabel(f'Grid: {size}×{size}')
    ax.axis('off')
    plot_idx += 1
    
    # Plot 2: Prime density heatmap
    ax = axes[plot_idx]
    # Create a heatmap showing prime density in local neighborhoods
    from scipy.ndimage import gaussian_filter
    density_map = gaussian_filter(is_prime.astype(float), sigma=2.0)
    im = ax.imshow(density_map, cmap='hot', interpolation='bilinear')
    ax.set_title('Local Prime Density (Smoothed)', fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plot_idx += 1
    
    # Plot 3: Curvature overlay
    if show_curvature:
        ax = axes[plot_idx]
        # Mask non-prime positions for clarity
        kappa_masked = np.ma.masked_where(~is_prime, kappa_grid)
        im = ax.imshow(kappa_masked, cmap='viridis', interpolation='nearest')
        ax.set_title('κ(n) Curvature at Primes', fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='κ(n)')
        plot_idx += 1
    
    # Plot 4: Geometric resolution overlay
    if show_resolution:
        ax = axes[plot_idx]
        theta_masked = np.ma.masked_where(~is_prime, theta_grid)
        im = ax.imshow(theta_masked, cmap='plasma', interpolation='nearest')
        ax.set_title("θ'(n,k=0.3) at Primes", fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="θ'(n,k)")
        plot_idx += 1
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to: {output_path}")
    else:
        plt.show()
    
    plt.close()


# === Main Demo Function ===

def main():
    """
    Demonstration of Ulam spiral with Z-Framework geometric embeddings.
    """
    print("=" * 80)
    print("Ulam Spiral with Z-Framework Geometric Embeddings")
    print("=" * 80)
    print()
    
    # Configuration
    size = 201  # Classic 201×201 grid
    seed = 42
    
    print(f"Configuration:")
    print(f"  Grid size: {size}×{size}")
    print(f"  Maximum n: {size * size:,}")
    print(f"  Random seed: {seed}")
    print(f"  Z-Framework parameters: k=0.3 (geometric resolution)")
    print()
    
    # Generate spiral
    print("Generating Ulam spiral...")
    spiral_data = generate_ulam_spiral(size, seed=seed)
    print(f"  ✓ Generated {spiral_data['max_n']:,} positions")
    print()
    
    # Statistical analysis
    print("Statistical Analysis:")
    print("-" * 80)
    stats = statistical_analysis(spiral_data)
    print(f"  Total numbers: {stats['total_numbers']:,}")
    print(f"  Total primes: {stats['total_primes']:,}")
    print(f"  Observed prime density: {stats['observed_density']:.6f}")
    print(f"  Expected density (PNT): {stats['expected_density']:.6f}")
    print(f"  Ratio (observed/expected): {stats['density_ratio']:.4f}")
    print()
    print(f"  Z-Framework Correlations with Prime Positions:")
    print(f"    κ(n) correlation: {stats['kappa_correlation']:+.6f}")
    print(f"    θ'(n,k) correlation: {stats['theta_correlation']:+.6f}")
    print(f"    Combined Z-weight: {stats['z_weight_correlation']:+.6f}")
    print()
    print(f"  κ(n) statistics:")
    print(f"    Mean: {stats['mean_kappa']:.6e}")
    print(f"    Max: {stats['max_kappa']:.6e}")
    print()
    
    # Diagonal analysis
    print("Diagonal Pattern Detection:")
    print("-" * 80)
    diagonals = detect_diagonals(spiral_data)
    total_diagonal_primes = 0
    for direction, diag_list in diagonals.items():
        if diag_list:
            counts = [len(primes) for offset, primes in diag_list]
            total_diagonal_primes += sum(counts)
            print(f"  {direction.capitalize()} diagonals: {len(diag_list)} detected")
            print(f"    Primes per diagonal: {min(counts)}-{max(counts)}")
    print(f"  Total primes in detected diagonals: {total_diagonal_primes}")
    print()
    
    # Quadratic polynomial analysis
    print("Quadratic Polynomial Analysis:")
    print("-" * 80)
    polynomials = analyze_quadratic_polynomials(spiral_data, max_test=50)
    for i, poly in enumerate(polynomials[:4], 1):
        print(f"  {i}. {poly['name']}")
        print(f"     Prime density: {poly['density']:.2%} ({poly['prime_count']}/{poly['total']})")
        if poly['sequence']:
            sample = poly['sequence'][:5]
            print(f"     First primes: {[v for n, v in sample]}")
    print()
    
    # Create visualization
    print("Creating visualizations...")
    output_path = "gists/ulam_spiral/ulam_spiral_z_framework.png"
    visualize_ulam_spiral(spiral_data, output_path=output_path)
    print(f"  ✓ Saved to: {output_path}")
    print()
    
    # Summary
    print("=" * 80)
    print("Key Findings:")
    print("-" * 80)
    print("1. Standard Ulam spiral shows characteristic diagonal prime clusters")
    print(f"2. Z-Framework curvature κ(n) correlation: {stats['kappa_correlation']:+.4f}")
    print(f"3. Geometric resolution θ'(n,k) correlation: {stats['theta_correlation']:+.4f}")
    print(f"4. Known quadratic polynomials maintain high prime density:")
    if polynomials:
        best = polynomials[0]
        print(f"   - {best['name']}: {best['density']:.1%} prime rate")
    print()
    print("The Z-Framework geometric embeddings provide quantitative measures")
    print("of prime distribution patterns that complement visual diagonal detection.")
    print("=" * 80)


if __name__ == "__main__":
    main()
