import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy.stats import gaussian_kde
from sklearn.cluster import DBSCAN
from mpl_toolkits.mplot3d import Axes3D

# Mathematical constants for different "filters"
UNIVERSAL = math.e
PHI = (1 + math.sqrt(5)) / 2
PI = math.pi
SQRT2 = math.sqrt(2)
EULER_MASCHERONI = 0.5772156649015329

class GeometricProjection:
    """
    A single geometric projection acting as a "polarizing filter" for number properties
    """
    def __init__(self, name: str, rate: float, frequency: float, phase: float = 0,
                 coordinate_system: str = "cylindrical"):
        self.name = name
        self.rate = rate
        self.frequency = frequency
        self.phase = phase
        self.coordinate_system = coordinate_system
        self._correction_factor = rate / UNIVERSAL

    def project_numbers(self, numbers: np.array, max_n: int) -> np.array:
        """Project numbers into this geometric space"""
        n = np.array(numbers)

        if self.coordinate_system == "cylindrical":
            return self._cylindrical_projection(n, max_n)
        elif self.coordinate_system == "spherical":
            return self._spherical_projection(n, max_n)
        elif self.coordinate_system == "hyperbolic":
            return self._hyperbolic_projection(n, max_n)
        else:
            return self._cartesian_projection(n, max_n)

    def _cylindrical_projection(self, n: np.array, max_n: int) -> np.array:
        """Original helical/cylindrical coordinate system"""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])

        x = n  # Radial distance
        y = n * (n / PI) * self._correction_factor * (1 + frame_shifts)  # Height
        z = np.sin(PI * self.frequency * n + self.phase) * (1 + 0.5 * frame_shifts)  # Angular

        return np.vstack((x, y, z)).T

    def _spherical_projection(self, n: np.array, max_n: int) -> np.array:
        """Spherical coordinate projection - good for detecting symmetric patterns"""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])

        # Map to spherical coordinates
        r = np.log(n + 1) * self._correction_factor  # Radial distance
        theta = (2 * PI * self.frequency * n + self.phase) % (2 * PI)  # Azimuthal
        phi = (PI * n / np.log(n + 2)) % PI  # Polar angle

        # Convert to Cartesian for analysis
        x = r * np.sin(phi) * np.cos(theta) * (1 + frame_shifts)
        y = r * np.sin(phi) * np.sin(theta) * (1 + frame_shifts)
        z = r * np.cos(phi) * (1 + frame_shifts)

        return np.vstack((x, y, z)).T

    def _hyperbolic_projection(self, n: np.array, max_n: int) -> np.array:
        """Hyperbolic projection - good for exponential growth patterns"""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])

        u = np.log(n + 1) * self._correction_factor
        v = (self.frequency * n + self.phase) % (2 * PI)

        # Hyperbolic coordinates
        x = np.cosh(u) * np.cos(v) * (1 + frame_shifts)
        y = np.sinh(u) * np.sin(v) * (1 + frame_shifts)
        z = np.tanh(u * self.frequency) * (1 + 0.3 * frame_shifts)

        return np.vstack((x, y, z)).T

    def _cartesian_projection(self, n: np.array, max_n: int) -> np.array:
        """Simple Cartesian projection with different scaling laws"""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])

        x = n
        y = (n ** (1 + self.frequency)) * self._correction_factor * (1 + frame_shifts)
        z = np.sin(2 * PI * self.frequency * np.log(n + 1) + self.phase) * (1 + frame_shifts)

        return np.vstack((x, y, z)).T

    def _compute_frame_shift(self, n: int, max_n: int) -> float:
        """Enhanced frame shift computation"""
        if n <= 1:
            return 0.0

        base_shift = math.log(n) / math.log(max_n)
        oscillation = 0.1 * math.sin(2 * PI * n / (math.log(n) + 1))

        # Add projection-specific modifications
        if self.coordinate_system == "spherical":
            oscillation *= math.cos(n * self.frequency)
        elif self.coordinate_system == "hyperbolic":
            oscillation *= math.tanh(n * self.frequency * 0.01)

        return base_shift + oscillation

class GeometricTriangulator:
    """
    Combines multiple geometric projections to triangulate special numbers
    """
    def __init__(self):
        self.projections = []
        self.trained_parameters = {}

    def add_projection(self, projection: GeometricProjection):
        """Add a geometric projection filter"""
        self.projections.append(projection)

    def create_standard_projections(self):
        """Create a set of standard projections based on mathematical constants"""

        # Prime-focused projections
        self.add_projection(GeometricProjection(
            "PrimeSpiral", UNIVERSAL/PHI, 0.091, 0, "cylindrical"
        ))

        self.add_projection(GeometricProjection(
            "GoldenSphere", UNIVERSAL*PHI/PI, 0.161, PI/4, "spherical"
        ))

        self.add_projection(GeometricProjection(
            "LogarithmicHyperbolic", UNIVERSAL/PI, 0.072, 0, "hyperbolic"
        ))

        # Twin prime focused
        self.add_projection(GeometricProjection(
            "TwinPrimeFilter", UNIVERSAL*SQRT2/PI, 0.105, PI/6, "cylindrical"
        ))

        # Coprime/GCD structure focused
        self.add_projection(GeometricProjection(
            "CoprimeCartesian", UNIVERSAL/SQRT2, 0.382, 0, "cartesian"
        ))

        # Mersenne/special form focused
        self.add_projection(GeometricProjection(
            "MersenneSpherical", UNIVERSAL*2/PI, 0.250, PI/3, "spherical"
        ))

    def triangulate_candidates(self, number_range: tuple, sample_size: int = 1000,
                               target_type: str = "primes") -> dict:
        """
        Use multiple projections to triangulate candidates for special numbers
        """
        start_n, end_n = number_range
        n_sample = np.linspace(start_n, end_n, sample_size, dtype=int)

        # Get projections from all filters
        all_projections = {}
        density_maps = {}

        for proj in self.projections:
            coords = proj.project_numbers(n_sample, end_n)
            all_projections[proj.name] = coords

            # Compute density map for this projection
            density_maps[proj.name] = self._compute_density_map(coords, n_sample)

        # Triangulation: find numbers that show up as high-density in multiple projections
        triangulated_candidates = self._perform_triangulation(
            density_maps, n_sample, target_type
        )

        return {
            'candidates': triangulated_candidates,
            'projections': all_projections,
            'density_maps': density_maps,
            'consensus_map': self._compute_consensus_map(density_maps)
        }

    def _compute_density_map(self, coords: np.array, numbers: np.array) -> np.array:
        """Compute density map for a single projection"""
        if len(coords) < 3:
            return np.zeros(len(numbers))

        tree = KDTree(coords)
        density_map = np.zeros(len(coords))

        # Multi-scale density analysis
        k_neighbors = min(7, len(coords) - 1)
        if k_neighbors < 2:
            return density_map

        dists, _ = tree.query(coords, k=k_neighbors)

        for i in range(len(coords)):
            if dists[i, 1] > 0:  # Avoid division by zero
                # Use harmonic mean of neighbor distances
                harmonic_mean_dist = k_neighbors / np.sum(1.0 / (dists[i, 1:] + 1e-10))
                density_map[i] = 1.0 / (harmonic_mean_dist + 1e-10)

        return density_map

    def _compute_consensus_map(self, density_maps: dict) -> np.array:
        """Compute consensus across all projections"""
        maps = list(density_maps.values())
        if not maps:
            return np.array([])

        # Normalize each density map to [0,1]
        normalized_maps = []
        for density_map in maps:
            if np.max(density_map) > 0:
                normalized = (density_map - np.min(density_map)) / (np.max(density_map) - np.min(density_map))
                normalized_maps.append(normalized)

        if not normalized_maps:
            return np.zeros_like(maps[0])

        # Weighted consensus (geometric mean works well for avoiding false positives)
        consensus = np.ones_like(normalized_maps[0])
        for norm_map in normalized_maps:
            consensus *= (norm_map + 0.1)  # Add small constant to avoid zeros

        consensus = consensus ** (1.0 / len(normalized_maps))
        return consensus

    def _perform_triangulation(self, density_maps: dict, numbers: np.array,
                               target_type: str) -> np.array:
        """Perform the actual triangulation to find candidates"""
        consensus = self._compute_consensus_map(density_maps)

        if target_type == "primes":
            # For primes, look for high consensus + specific projection patterns
            threshold = np.percentile(consensus, 85)  # Top 15%

            # Additional filter: must be high in at least 2 different projection types
            coord_system_votes = {}
            for proj in self.projections:
                coord_sys = proj.coordinate_system
                if coord_sys not in coord_system_votes:
                    coord_system_votes[coord_sys] = np.zeros_like(consensus)

                # Normalize this projection's density
                proj_density = density_maps[proj.name]
                if np.max(proj_density) > 0:
                    normalized = proj_density / np.max(proj_density)
                    coord_system_votes[coord_sys] += normalized

            # Require high consensus AND votes from multiple coordinate systems
            multi_system_support = sum(1 for votes in coord_system_votes.values()
                                       if np.max(votes) > 0.5) >= 2

            if multi_system_support:
                candidates_mask = consensus > threshold
            else:
                candidates_mask = consensus > np.percentile(consensus, 95)  # Be more selective

        elif target_type == "twin_primes":
            # For twin primes, look for paired high-density regions
            threshold = np.percentile(consensus, 90)
            candidates_mask = consensus > threshold

            # Additional check: look for candidates that are 2 apart
            twin_candidates = []
            candidate_indices = np.where(candidates_mask)[0]

            for i in candidate_indices:
                if i < len(numbers) - 1:
                    if numbers[i+1] - numbers[i] == 2 and candidates_mask[i+1]:
                        twin_candidates.extend([numbers[i], numbers[i+1]])

            return np.array(twin_candidates)

        elif target_type == "coprimes":
            # For coprimes, look for patterns in specific projections
            coprime_projection = "CoprimeCartesian"
            if coprime_projection in density_maps:
                proj_density = density_maps[coprime_projection]
                threshold = np.percentile(proj_density, 80)
                candidates_mask = proj_density > threshold
            else:
                candidates_mask = consensus > np.percentile(consensus, 80)

        else:  # General case
            threshold = np.percentile(consensus, 85)
            candidates_mask = consensus > threshold

        return numbers[candidates_mask]

    def visualize_triangulation(self, results: dict, show_top_n: int = 3):
        """Visualize the triangulation results"""
        projections = results['projections']
        density_maps = results['density_maps']
        candidates = results['candidates']

        # Plot consensus map
        plt.figure(figsize=(12, 8))
        consensus = results['consensus_map']

        plt.subplot(2, 2, 1)
        plt.plot(consensus, alpha=0.7, color='purple', linewidth=2)
        plt.title("Consensus Density Map")
        plt.ylabel("Consensus Score")

        # Plot individual projection density maps
        colors = ['red', 'blue', 'green', 'orange', 'brown', 'pink']

        plt.subplot(2, 2, 2)
        for i, (name, density) in enumerate(list(density_maps.items())[:show_top_n]):
            plt.plot(density, alpha=0.6, color=colors[i % len(colors)], label=name)
        plt.title("Individual Projection Densities")
        plt.legend()

        # Show candidates
        plt.subplot(2, 2, 3)
        plt.hist(candidates, bins=30, alpha=0.7, color='gold', edgecolor='black')
        plt.title(f"Triangulated Candidates ({len(candidates)} found)")
        plt.xlabel("Number Value")
        plt.ylabel("Count")

        # 3D visualization of best projection
        if projections:
            best_proj_name = max(density_maps.keys(),
                                 key=lambda k: np.max(density_maps[k]))
            best_coords = projections[best_proj_name]

            ax = plt.subplot(2, 2, 4, projection='3d')

            # Color points by consensus score
            colors_3d = plt.cm.plasma(consensus / np.max(consensus))
            ax.scatter(best_coords[:, 0], best_coords[:, 1], best_coords[:, 2],
                       c=colors_3d, s=20, alpha=0.6)

            ax.set_title(f"Best Projection: {best_proj_name}")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

        plt.tight_layout()
        plt.show()

def demo_geometric_triangulation():
    """Demonstrate the triangulation approach"""

    # Create triangulator with multiple projections
    triangulator = GeometricTriangulator()
    triangulator.create_standard_projections()

    print(f"Created {len(triangulator.projections)} geometric projections:")
    for proj in triangulator.projections:
        print(f"  - {proj.name} ({proj.coordinate_system})")

    # Test on a medium range
    test_range = (1000, 2000)
    print(f"\nTriangulating in range {test_range}...")

    # Find prime candidates
    results = triangulator.triangulate_candidates(
        test_range, sample_size=300, target_type="primes"
    )

    candidates = results['candidates']
    print(f"Found {len(candidates)} prime candidates")
    print(f"Top 10 candidates: {sorted(candidates)[:10]}")

    # Quick validation
    def is_prime(n):
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0: return False
        return True

    # Check first 20 candidates
    test_candidates = sorted(candidates)[:20]
    correct = sum(1 for c in test_candidates if is_prime(c))
    precision = correct / len(test_candidates) if test_candidates else 0

    print(f"Precision on first 20 candidates: {precision:.3f}")

    # Visualize results
    triangulator.visualize_triangulation(results)

    return triangulator, results

if __name__ == "__main__":
    triangulator, results = demo_geometric_triangulation()