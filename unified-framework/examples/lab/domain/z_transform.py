import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from sympy import sieve as sympy_sieve
import math
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.interpolate import griddata

class ZTransform:
    """
    A class implementing the Universal Form Z = A(B/C) transformation,
    connecting prime gap analysis to three foundational visualizations.
    """

    # Constants representing natural invariants
    PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
    E = np.e  # Euler's number
    HELIX_FREQ = 0.1003033  # Helical frequency for geometric projection
    K_STAR = 1.9878  # Constant for zeta shift calculations

    def __init__(self, max_n=10000000, epsilon=1e-10):
        """
        Initialize the Z-Transform framework.

        Args:
            max_n: Maximum integer to analyze
            epsilon: Small value to prevent division by zero
        """
        self.max_n = max_n
        self.epsilon = epsilon

        # Generate sequence of integers
        self.n_values = np.arange(1, max_n + 1)

        # Compute primes up to max_n
        self.primes = self._compute_primes(max_n)
        self.prime_indices = np.searchsorted(self.n_values, self.primes)

        print(f"Initialized ZTransform with {len(self.primes)} primes up to {max_n}")

    def _compute_primes(self, limit):
        """Compute primes up to the given limit"""
        return np.array(list(sympy_sieve.primerange(2, limit + 1)))

    def compute_gaps_and_deviations(self):
        """Calculate prime gaps and their deviation from expected log values"""
        real_gaps = np.diff(self.primes)

        # Expected gaps based on Prime Number Theorem approximation
        expected_gaps = np.log(self.primes[:-1])

        # Normalized deviations
        deviations = real_gaps / expected_gaps - 1

        return {
            'primes': self.primes[:-1],  # Corresponding prime for each gap
            'real_gaps': real_gaps,
            'expected_gaps': expected_gaps,
            'deviations': deviations,
            'gap_velocity': real_gaps / expected_gaps  # "Velocity" in the framework
        }

    def compute_z_values(self):
        """
        Compute Z values for all n using the Universal Form Z = A(B/C)

        Z = Harmonic(n) * (ln(n)/ζ(n))
        """
        # A: Harmonic number approximation (ln(n) + γ)
        gamma = 0.57721  # Euler-Mascheroni constant
        harmonic_n = np.log(self.n_values) + gamma

        # B: Natural logarithm of n
        log_n = np.log(self.n_values)

        # C: Riemann zeta approximation for real values > 1
        # For n >= 2: ζ(n) ≈ 1 + 1/2^n + 1/3^n + ... (truncated sum)
        # For n = 1: set to infinity and handle separately
        zeta_values = np.zeros_like(self.n_values, dtype=float)

        # Handle n=1 separately (zeta(1) is undefined/infinity)
        zeta_values[0] = np.inf  # Will result in Z=0 for n=1

        # Calculate zeta for n >= 2
        for i, n in enumerate(self.n_values[1:], 1):
            if n == 1:
                zeta_values[i] = np.inf
            else:
                # For numerical stability, we approximate zeta with a finite sum
                k_terms = 1000  # Number of terms to use in approximation
                k_values = np.arange(1, k_terms + 1)
                zeta_values[i] = np.sum(1 / np.power(k_values, n))

        # Handle potential numerical issues
        C_values = zeta_values.copy()
        C_values[C_values < self.epsilon] = self.epsilon  # Prevent division by zero

        # Compute Z = A(B/C)
        z_values = harmonic_n * (log_n / C_values)

        # Replace any NaN/inf values with 0
        z_values = np.nan_to_num(z_values)

        return z_values

    def lorentz_transform(self, v, coords, c_analog=None):
        """
        Apply a Lorentz-like transformation to coordinates based on velocity v

        Args:
            v: Velocity parameter (typically prime gap velocity)
            coords: Original coordinates
            c_analog: Speed limit analog (defaults to PHI)
        """
        if c_analog is None:
            c_analog = self.PHI

        # Compute gamma factor
        gamma = 1 / np.sqrt(1 - np.minimum(v**2 / c_analog**2, 0.99))

        # Expand dimensions for broadcasting
        gamma = np.expand_dims(gamma, axis=1)

        # Apply Lorentz-like transformation
        transformed_coords = gamma * coords

        return transformed_coords

    def plot_gap_deviation(self):
        """
        Plot 1: Prime Gap Deviation (Velocity Profile)
        Shows how actual prime gaps deviate from expected gaps
        """
        gap_data = self.compute_gaps_and_deviations()
        primes = gap_data['primes']
        deviations = gap_data['deviations']
        gap_velocity = gap_data['gap_velocity']

        plt.figure(figsize=(12, 7))

        # Create scatter plot with color based on velocity
        sc = plt.scatter(primes, deviations, c=gap_velocity, cmap='viridis',
                         alpha=0.7, s=20, edgecolor='none')

        # Highlight extreme deviations
        threshold = np.mean(deviations) + 1.5 * np.std(deviations)
        extreme_mask = deviations > threshold
        plt.scatter(primes[extreme_mask], deviations[extreme_mask],
                    color='red', s=30, edgecolor='black', label=f'High Deviation (>{threshold:.2f})')

        # Add colorbar
        cbar = plt.colorbar(sc)
        cbar.set_label('Gap Velocity (actual/expected)')

        # Add line at y=0 (no deviation)
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)

        # Add annotation for max deviation
        max_idx = np.argmax(deviations)
        plt.annotate(f"Max Dev: {deviations[max_idx]:.2f} at p={primes[max_idx]}",
                     xy=(primes[max_idx], deviations[max_idx]),
                     xytext=(0.7, 0.95), textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', color='black'))

        # Scale axes using natural invariants
        plt.xscale('log')
        y_scale = self.E / np.log(np.max(primes))
        plt.ylim(bottom=min(deviations) * y_scale, top=max(deviations) * y_scale)

        plt.title('Prime Gap Deviation (Velocity Profile)')
        plt.xlabel('Prime Number')
        plt.ylabel('Deviation from Expected Gap')
        plt.grid(True, alpha=0.3)
        plt.legend()

        plt.tight_layout()
        plt.savefig('gap_deviation.png', dpi=300)
        plt.close()

        return gap_data

    def plot_zeta_shift(self):
        """
        Plot 2: Zeta Shift (Frame Curvature Map)
        Visualizes how Z-values correlate with primes through zeta function analysis
        """
        # Get Z-values for all numbers in range
        z_values = self.compute_z_values()

        # Get Z-values specifically for primes
        prime_indices = self.prime_indices
        prime_z = z_values[prime_indices - 1]  # -1 because indices are 1-based in our setup

        # Calculate zeta shift ratio (relates to curvature in the prime landscape)
        shift_ratio = np.zeros_like(z_values)
        for i, n in enumerate(self.n_values):
            # Skip the first few values which can cause numerical issues
            if n <= 2:
                shift_ratio[i] = 0
                continue

            # For each n, calculate how its Z-value shifts relative to theoretical
            theoretical = np.log(n) / self.K_STAR
            actual = z_values[i-1]  # -1 for 0-indexing
            shift_ratio[i-1] = (actual - theoretical) / (theoretical + self.epsilon)

        # Apply hyperbolic warping to enhance visibility
        warped_z = np.sinh(z_values / np.max(z_values) * np.pi)

        plt.figure(figsize=(12, 7))

        # Plot all Z-values with symlog scale for better visibility
        plt.scatter(self.n_values, warped_z, c='lightblue', s=10, alpha=0.5, label='All integers')

        # Highlight primes with distinctive markers
        plt.scatter(self.primes, np.sinh(prime_z / np.max(z_values) * np.pi),
                    color='red', marker='*', s=80, label='Prime numbers', zorder=5)

        # Add reference line based on theoretical model
        x_ref = np.linspace(10, self.max_n, 100)
        y_ref = np.sinh(np.log(x_ref) / (np.max(z_values) * self.K_STAR) * np.pi)
        plt.plot(x_ref, y_ref, 'k--', alpha=0.5, label='Theoretical reference')

        plt.xscale('log')
        plt.yscale('symlog')
        plt.grid(True, alpha=0.3)
        plt.title('Zeta Shift (Frame Curvature Map)')
        plt.xlabel('n')
        plt.ylabel('Warped Z Value (sinh transform)')
        plt.legend()

        plt.tight_layout()
        plt.savefig('zeta_shift.png', dpi=300)
        plt.close()

        return {
            'n_values': self.n_values,
            'z_values': z_values,
            'prime_indices': self.prime_indices,
            'prime_z': prime_z,
            'shift_ratio': shift_ratio
        }

    def plot_geometric_projection(self):
        """
        Plot 3: Geometric Projection (3D Topology)
        Projects numbers into 3D space based on their properties
        """
        # Use subset if there are too many points
        sample_size = min(500, self.max_n)
        if self.max_n > sample_size:
            # Sample more densely in lower ranges
            log_indices = np.geomspace(1, self.max_n, sample_size).astype(int)
            n_subset = self.n_values[log_indices - 1]
        else:
            n_subset = self.n_values

        # Create 3D plot
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Compute coordinates for the 3D helix projection
        theta = n_subset * self.HELIX_FREQ

        # Radius influenced by number properties
        r = np.log(n_subset + 1) / (np.log(n_subset + self.E) + self.epsilon)

        # Compute 3D coordinates with phi-based curvature
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = theta * np.tanh(theta / self.PHI)  # z with φ-based curvature

        # Create coordinate array for all points
        coords = np.column_stack([x, y, z])

        # Plot all points
        ax.scatter(x, y, z, c=n_subset, cmap='viridis', s=30, alpha=0.7, label='Integers')

        # Highlight primes that are in the subset
        prime_mask = np.isin(n_subset, self.primes)
        if np.any(prime_mask):
            ax.scatter(x[prime_mask], y[prime_mask], z[prime_mask],
                       color='red', marker='*', s=100, edgecolor='black',
                       label='Primes', zorder=10)

        # Calculate density map for topology analysis
        from scipy.spatial import cKDTree
        kdtree = cKDTree(coords)
        density = np.zeros(len(coords))

        # Calculate local point density
        for i, coord in enumerate(coords):
            # Find number of neighbors within a radius
            radius = 0.2 * np.sqrt(np.max(r))
            neighbors = kdtree.query_ball_point(coord, radius)
            density[i] = len(neighbors)

        # Set plot aesthetics
        ax.set_title('Geometric Projection (3D Topology)', fontsize=14)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z (φ-based curvature)')
        ax.legend()

        plt.tight_layout()
        plt.savefig('geometric_projection.png', dpi=300)
        plt.close()

        return {
            'n_subset': n_subset,
            'coords': coords,
            'prime_mask': prime_mask,
            'density': density,
            'r': r,
            'theta': theta
        }

    def plot_invariant_frame_map(self, gap_data, zeta_data, geom_data):
        """
        Plot 4: Invariant Frame Map (Meta-Plot)
        Combines information from the three fundamental plots to create a meta-score
        that highlights significant numbers in the prime landscape
        """
        # Find common set of n values across all datasets
        common_n = np.intersect1d(gap_data['primes'], geom_data['n_subset'])

        # For memory efficiency, cap the size if needed
        if len(common_n) > 10000:
            common_n = common_n[:10000]

        # Extract relevant measures from each dataset
        gap_velocity = gap_data['gap_velocity']
        shift_ratio = zeta_data['shift_ratio']
        coords = geom_data['coords']

        # Get indices for lookup
        common_indices = np.array([np.where(gap_data['primes'] == n)[0][0] for n in common_n if n in gap_data['primes']])

        # Extract values for common indices
        gap_velocity_common = gap_velocity[common_indices]

        # Normalize measures for fair comparison
        gap_velocity_norm = (gap_velocity_common - np.mean(gap_velocity_common)) / (np.std(gap_velocity_common) + self.epsilon)

        # Extract geometric projection coordinates for common n
        geom_indices = np.array([np.where(geom_data['n_subset'] == n)[0][0] for n in common_n if n in geom_data['n_subset']])
        proj_coords = coords[geom_indices]

        # Calculate average projection coordinates
        avg_proj_coords = proj_coords - np.mean(proj_coords, axis=0)
        avg_proj_coords = avg_proj_coords / (np.std(avg_proj_coords, axis=0) + self.epsilon)

        # Apply Lorentz transformation
        lorentz_z = self.lorentz_transform(np.abs(gap_velocity_norm), avg_proj_coords, c_analog=self.PHI)

        # Calculate meta-score that integrates all three visualizations
        meta_score = np.zeros(len(common_n))

        for i in range(len(common_n)):
            # Gap component: how much the gap deviates from expected
            gap_component = np.abs(gap_velocity_norm[i])

            # Projection component: distance from origin in transformed space
            proj_component = np.linalg.norm(lorentz_z[i])

            # Zeta component: How strongly the point relates to zeta properties
            # Find closest n in zeta_data
            n_idx = np.searchsorted(zeta_data['n_values'], common_n[i])
            if n_idx >= len(zeta_data['shift_ratio']):
                n_idx = len(zeta_data['shift_ratio']) - 1
            zeta_component = np.abs(zeta_data['shift_ratio'][n_idx])

            # Combine components with weighting
            meta_score[i] = (0.4 * gap_component +
                             0.4 * proj_component +
                             0.2 * zeta_component)

        # Create 2D plot with meta-score
        plt.figure(figsize=(12, 8))

        # Use Gaussian Mixture Model for clustering
        meta_score_reshaped = meta_score.reshape(-1, 1)
        gm = GaussianMixture(n_components=5, random_state=42).fit(meta_score_reshaped)
        labels = gm.predict(meta_score_reshaped)

        # Scatter plot with GMM cluster colors
        scatter = plt.scatter(common_n, meta_score, c=labels, cmap='viridis',
                              alpha=0.7, s=50, edgecolor='none')

        # Highlight actual primes in the common set
        prime_mask = np.isin(common_n, self.primes)
        plt.scatter(common_n[prime_mask], meta_score[prime_mask],
                    color='red', marker='*', s=100, edgecolor='black', label='Primes')

        # Identify high-scoring numbers
        threshold = np.percentile(meta_score, 95)
        high_scores = meta_score > threshold
        high_score_numbers = common_n[high_scores]

        # Calculate precision (how many high-scoring numbers are actually primes)
        high_score_primes = np.isin(high_score_numbers, self.primes)
        precision = np.sum(high_score_primes) / len(high_score_numbers) if len(high_score_numbers) > 0 else 0

        # Add annotation with precision
        plt.annotate(f"Precision: {precision:.2%}", xy=(0.02, 0.95),
                     xycoords='axes fraction', fontsize=12,
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

        plt.xscale('log')
        plt.grid(True, alpha=0.3)
        plt.colorbar(scatter, label='Cluster')
        plt.title('Invariant Frame Map (Meta-Analysis of Prime Properties)')
        plt.xlabel('n')
        plt.ylabel('Meta-Score (Combined Significance)')
        plt.legend()

        plt.tight_layout()
        plt.savefig('invariant_frame_map.png', dpi=300)
        plt.close()

        return {
            'common_n': common_n,
            'meta_score': meta_score,
            'high_score_numbers': high_score_numbers,
            'precision': precision,
            'lorentz_z': lorentz_z
        }

    def run_full_analysis(self):
        """Run the complete analysis pipeline and generate all plots"""
        print(f"Running full Z-transform analysis with {len(self.primes)} primes up to {self.max_n}")

        # Plot 1: Prime Gap Deviation
        gap_data = self.plot_gap_deviation()
        print("Generated Prime Gap Deviation plot")

        # Plot 2: Zeta Shift
        zeta_data = self.plot_zeta_shift()
        print("Generated Zeta Shift plot")

        # Plot 3: Geometric Projection
        geom_data = self.plot_geometric_projection()
        print("Generated Geometric Projection plot")

        # Plot 4: Invariant Frame Map
        meta_data = self.plot_invariant_frame_map(gap_data, zeta_data, geom_data)
        print(f"Generated Invariant Frame Map with precision: {meta_data['precision']:.2%}")

        # Print high-scoring non-prime numbers (potentially significant)
        high_score_nonprimes = [n for n in meta_data['high_score_numbers']
                                if n not in self.primes]
        print(f"\nHigh-scoring non-prime numbers: {high_score_nonprimes[:10]}")

        return {
            'gap_data': gap_data,
            'zeta_data': zeta_data,
            'geom_data': geom_data,
            'meta_data': meta_data
        }


# Example usage:
if __name__ == "__main__":
    # Initialize with default max_n=6000
    analyzer = ZTransform(max_n=10000000)

    # Run full analysis pipeline
    results = analyzer.run_full_analysis()

    # Print summary
    print("\nAnalysis Summary:")
    print(f"Max deviation at prime: {results['gap_data']['primes'][np.argmax(results['gap_data']['deviations'])]}")
    print(f"Meta-analysis precision: {results['meta_data']['precision']:.2%}")
    print(f"First 5 high-scoring numbers: {results['meta_data']['high_score_numbers'][:5]}")