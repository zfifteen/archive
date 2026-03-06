
import math
import numpy as np
import matplotlib.pyplot as plt

# Constants aligned with Universal Form Transformer
UNIVERSAL = math.e  # Cosmic anchor (c in Z = T(v/c))
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio for prime resonance
PI = math.pi  # Circular constant for oscillatory patterns
SQRT2 = math.sqrt(2)  # Scaling factor for geometric balance

class ChainedProjection:
    """
    Chains multiple geometric projections to refine number patterns, applying sequential
    transformations guided by Z = T(v/c) to enhance signals for primes, coprimes, and other
    special numbers.
    """
    def __init__(self, projections):
        self.projections = projections

    def apply_chain(self, numbers: np.array, max_n: int) -> tuple:
        """Apply a sequence of projections, using z-coordinates as input to the next."""
        current_coords = np.array(numbers, dtype=float)
        density_maps = []
        for proj in self.projections:
            coords = proj.project_numbers(current_coords, max_n)
            density_map = np.zeros(len(coords))
            for i in range(len(coords)):
                distances = np.sqrt(((coords - coords[i]) ** 2).sum(axis=1))
                distances[i] = 1e-10
                density_map[i] = np.sum(1.0 / (distances + 1e-10)) / len(coords)
            density_maps.append(density_map)
            current_coords = coords[:, 2]  # Use z-coordinate for next projection
        combined_density = np.ones_like(density_maps[0])
        for dm in density_maps:
            combined_density *= (dm + 0.1)
        combined_density = combined_density ** (1.0 / len(density_maps))
        return coords, combined_density.tolist()

class GeometricProjection:
    """
    A geometric projection filtering number properties into a 3D space to reveal patterns.
    Guided by the Universal Form Transformer Z = T(v/c).
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
        """Project numbers into a 3D geometric space for pattern analysis."""
        n = np.array(numbers, dtype=float)
        if self.coordinate_system == "cylindrical":
            return self._cylindrical_projection(n, max_n)
        elif self.coordinate_system == "spherical":
            return self._spherical_projection(n, max_n)
        else:
            return self._hyperbolic_projection(n, max_n)

    def _cylindrical_projection(self, n: np.array, max_n: int) -> np.array:
        """Cylindrical projection tuned for prime patterns."""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])
        x = n
        y = n * np.log(n + 1) / UNIVERSAL * self._correction_factor * (1 + frame_shifts)
        z = np.sin(PI * self.frequency * n + self.phase) * (1 + 0.5 * frame_shifts)
        return np.array([[x[i], y[i], z[i]] for i in range(len(n))])

    def _spherical_projection(self, n: np.array, max_n: int) -> np.array:
        """Spherical projection for symmetric patterns (e.g., coprimes)."""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])
        r = np.log(n + 1) * self._correction_factor
        theta = (2 * PI * self.frequency * n + self.phase) % (2 * PI)
        phi = (PI * n / np.log(n + 2)) % PI
        x = r * np.sin(phi) * np.cos(theta) * (1 + frame_shifts)
        y = r * np.sin(phi) * np.sin(theta) * (1 + frame_shifts)
        z = r * np.cos(phi) * (1 + frame_shifts)
        return np.array([[x[i], y[i], z[i]] for i in range(len(n))])

    def _hyperbolic_projection(self, n: np.array, max_n: int) -> np.array:
        """Hyperbolic projection for twin prime gaps."""
        frame_shifts = np.array([self._compute_frame_shift(i, max_n) for i in n])
        u = np.log(n + 1) * self._correction_factor
        v = (self.frequency * n + self.phase) % (2 * PI)
        x = np.cosh(u) * np.cos(v) * (1 + frame_shifts)
        y = np.sinh(u) * np.sin(v) * (1 + frame_shifts)
        z = np.tanh(u * self.frequency) * (1 + 0.3 * frame_shifts)
        return np.array([[x[i], y[i], z[i]] for i in range(len(n))])

    def _compute_frame_shift(self, n: float, max_n: int) -> float:
        """Compute frame shift for dynamic adjustment (Universal Frame Shift Transformer)."""
        if n <= 1:
            return 0.0
        return math.log(n) / math.log(max_n)

class GeometricTriangulator:
    """
    Triangulates special numbers (primes, coprimes, twin primes) from chained projections.
    Breakthrough: Uses chained filters and triangle geometry to encode number patterns.
    """
    def __init__(self):
        self.projections = []

    def create_standard_projections(self):
        """Create projections tuned for primes, coprimes, and twin primes."""
        self.projections = [
            GeometricProjection("PrimeSpiral", UNIVERSAL/PHI, 0.1, 0, "cylindrical"),  # Primes
            GeometricProjection("GoldenSphere", UNIVERSAL*PHI/PI, 0.161, PI/4, "spherical"),  # Coprimes
            GeometricProjection("LogarithmicHyperbolic", UNIVERSAL/PI, 0.072, 0, "hyperbolic")  # Twin primes
        ]

    def triangulate_candidates(self, number_range: tuple, sample_size: int = 1000,
                               target_type: str = "primes") -> dict:
        """Triangulate candidates using chained projections and triangular structures."""
        start_n, end_n = number_range
        n_sample = np.linspace(start_n, end_n, sample_size, dtype=int)
        chained_proj = ChainedProjection(self.projections)
        final_coords, combined_density = chained_proj.apply_chain(n_sample, end_n)
        candidates = self._perform_triangulation(combined_density, n_sample, target_type)
        triangles = self._construct_triangles(final_coords, combined_density, n_sample, target_type)
        return {
            'candidates': list(candidates),
            'final_coords': final_coords.tolist(),
            'density_map': combined_density,
            'triangles': triangles
        }

    def _compute_density_map(self, coords: np.array, numbers: np.array) -> np.array:
        """Compute density map using inverse distance weighting."""
        density_map = np.zeros(len(coords))
        for i in range(len(coords)):
            distances = np.sqrt(((coords - coords[i]) ** 2).sum(axis=1))
            distances[i] = 1e-10
            density_map[i] = np.sum(1.0 / (distances + 1e-10)) / len(coords)
        return density_map

    def _perform_triangulation(self, density_map: list, numbers: np.array,
                               target_type: str) -> np.array:
        """Identify candidates based on density and number type."""
        density_map = np.array(density_map)
        threshold = np.percentile(density_map, 85)
        candidates = numbers[density_map > threshold]
        if len(candidates) == 0:
            return np.array([])
        if target_type == "coprimes":
            candidates = [n for n in candidates if any(math.gcd(n, m) == 1 for m in candidates if m != n)]
        elif target_type == "twin_primes":
            twin_candidates = []
            candidates = np.sort(candidates)
            for i in range(len(candidates) - 1):
                if candidates[i+1] - candidates[i] == 2:
                    twin_candidates.extend([candidates[i], candidates[i+1]])
            candidates = np.array(twin_candidates)
        return candidates

    def _construct_triangles(self, coords: np.array, density_map: list, numbers: np.array,
                             target_type: str) -> list:
        """Construct triangles from high-density points, classified by number type."""
        density_map = np.array(density_map)
        high_density_indices = np.where(density_map > np.percentile(density_map, 85))[0]
        if len(high_density_indices) < 3:
            return []
        max_frame_shift = max([math.log(n) / math.log(max(numbers)) for n in numbers if n > 1] or [1e-10])
        triangles = []

        def is_prime(n):
            if n < 2: return False
            if n == 2: return True
            if n % 2 == 0: return False
            for i in range(3, int(math.sqrt(n)) + 1, 2):
                if n % i == 0: return False
            return True

        def is_coprime_pair(n, m):
            return math.gcd(n, m) == 1

        for i in range(len(high_density_indices) - 2):
            idx1, idx2, idx3 = high_density_indices[i:i+3]
            triangle = [coords[idx1], coords[idx2], coords[idx3]]
            numbers_tri = [numbers[idx1], numbers[idx2], numbers[idx3]]
            frame_shifts = [math.log(n) / math.log(max(numbers)) if n > 1 else 0 for n in numbers_tri]
            z_values = [n * (fs / max_frame_shift) if fs > 0 else 0 for n, fs in zip(numbers_tri, frame_shifts)]
            area = self._compute_triangle_area(triangle)

            # Classify triangle type
            z_variance = np.var(z_values) if z_values else 0
            if target_type == "primes":
                triangle_type = "prime" if z_variance > 1000 and sum(is_prime(n) for n in numbers_tri) >= 2 else "non_prime"
            elif target_type == "coprimes":
                triangle_type = "coprime" if area < 5 and all(is_coprime_pair(numbers_tri[i], numbers_tri[j])
                                                              for i in range(3) for j in range(i+1, 3)) else "non_coprime"
            elif target_type == "twin_primes":
                triangle_type = "twin_prime" if any(numbers_tri[i+1] - numbers_tri[i] == 2
                                                    for i in range(len(numbers_tri)-1)) else "non_twin"
            else:
                triangle_type = "general"

            triangles.append({
                'vertices': [v.tolist() for v in triangle],
                'numbers': numbers_tri,
                'z_values': z_values,
                'area': area,
                'type': triangle_type
            })
        return triangles

    def _compute_triangle_area(self, triangle: list) -> float:
        """Compute the area of a triangle in 3D space."""
        a, b, c = triangle
        ab = np.array(b) - np.array(a)
        ac = np.array(c) - np.array(a)
        cross_product = np.cross(ab, ac)
        return 0.5 * np.sqrt((cross_product ** 2).sum())

    def visualize_triangulation(self, results: dict, show_top_n: int = 3):
        """Visualize chained projection results, with color-coded triangles by number type."""
        try:
            final_coords = np.array(results['final_coords'])
            density_map = np.array(results['density_map'])
            candidates = np.array(results['candidates'])
            triangles = results['triangles']

            plt.figure(figsize=(12, 10))

            # Density Map
            plt.subplot(2, 2, 1)
            plt.plot(density_map, alpha=0.7, color='purple')
            plt.title("Chained Density Map")
            plt.ylabel("Density Score")

            # Candidate Histogram
            plt.subplot(2, 2, 2)
            plt.hist(candidates, bins=30, alpha=0.7, color='gold', edgecolor='black') if len(candidates) > 0 else plt.text(0.5, 0.5, "No Candidates", ha='center')
            plt.title(f"Triangulated Candidates ({len(candidates)} found)")
            plt.xlabel("Number Value")
            plt.ylabel("Count")

            # 3D Projection with Triangles
            ax = plt.subplot(2, 2, 3, projection='3d')
            colors_3d = plt.cm.plasma(density_map / np.max(density_map)) if np.max(density_map) > 0 else plt.cm.plasma(density_map)
            ax.scatter(final_coords[:, 0], final_coords[:, 1], final_coords[:, 2],
                       c=colors_3d, s=20, alpha=0.6)

            for triangle in triangles[:show_top_n]:
                verts = np.array(triangle['vertices'])
                color = {'prime': 'red', 'coprime': 'blue', 'twin_prime': 'green',
                         'non_prime': 'gray', 'non_coprime': 'gray', 'non_twin': 'gray',
                         'general': 'gray'}.get(triangle['type'], 'gray')
                ax.plot(verts[:, 0], verts[:, 1], verts[:, 2], color=color, alpha=0.3)

            ax.set_title("Chained Projection with Triangles")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

            # Triangle Area vs Type Likelihood
            if triangles:
                areas = [t['area'] for t in triangles]
                likelihoods = []
                for t in triangles:
                    if t['type'] == "prime":
                        likelihood = sum(is_prime(n) for n in t['numbers']) / 3
                    elif t['type'] == "coprime":
                        likelihood = sum(1 for i in range(3) for j in range(i+1, 3)
                                         if math.gcd(t['numbers'][i], t['numbers'][j]) == 1) / 3
                    elif t['type'] == "twin_prime":
                        likelihood = sum(1 for i in range(len(t['numbers'])-1)
                                         if t['numbers'][i+1] - t['numbers'][i] == 2) / 2
                    else:
                        likelihood = 0
                    likelihoods.append(likelihood)

                colors = [{'prime': 'red', 'coprime': 'blue', 'twin_prime': 'green',
                           'non_prime': 'gray', 'non_coprime': 'gray', 'non_twin': 'gray',
                           'general': 'gray'}.get(t['type'], 'gray') for t in triangles]
                plt.subplot(2, 2, 4)
                plt.scatter(areas, likelihoods, c=colors, alpha=0.6)
                plt.title("Triangle Areas vs Number Type Likelihood")
                plt.xlabel("Triangle Area")
                plt.ylabel("Likelihood (Fraction of Matching Vertices)")
                plt.grid(True)

            plt.tight_layout()
            plt.show()

        except ImportError:
            print("Matplotlib not available; skipping visualization.")
        except Exception as e:
            print(f"Visualization error: {e}")

def demo_geometric_triangulation():
    """Demonstrate chained triangulation for primes, coprimes, and twin primes."""
    triangulator = GeometricTriangulator()
    triangulator.create_standard_projections()
    test_range = (1000, 2000)

    for target_type in ["primes", "coprimes", "twin_primes"]:
        print(f"\nTriangulating {target_type} in range {test_range}...")
        try:
            results = triangulator.triangulate_candidates(test_range, sample_size=300, target_type=target_type)
            candidates = results['candidates']
            print(f"Found {len(candidates)} {target_type} candidates")
            print(f"Top 10 candidates: {sorted(candidates)[:10]}")

            print(f"\nTriangle analysis for {target_type}:")
            for i, triangle in enumerate(results['triangles'][:5]):
                print(f"Triangle {i+1}: Numbers {triangle['numbers']}, Z Values {triangle['z_values']}, "
                      f"Area {triangle['area']:.3f}, Type {triangle['type']}")

            triangulator.visualize_triangulation(results)
        except Exception as e:
            print(f"Error processing {target_type}: {e}")

    return triangulator, results

if __name__ == "__main__":
    triangulator, results = demo_geometric_triangulation()
