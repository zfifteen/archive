import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from mpl_toolkits.mplot3d import Axes3D

# Physical constant for Z-metric
SPEED_OF_LIGHT = 299_792_458  # units consistent with your number line

class GeometricProjection:
    """
    Projects integers into various geometric spaces.
    """
    def __init__(self, name: str, rate: float, frequency: float,
                 phase: float = 0, coordinate_system: str = "cylindrical"):
        self.name = name
        self.rate = rate
        self.frequency = frequency
        self.phase = phase
        self.coordinate_system = coordinate_system
        self._correction_factor = rate / math.e  # universal base

    def project_numbers(self, numbers: np.ndarray, max_n: int) -> np.ndarray:
        if self.coordinate_system == "cylindrical":
            return self._cylindrical(numbers, max_n)
        elif self.coordinate_system == "spherical":
            return self._spherical(numbers, max_n)
        elif self.coordinate_system == "hyperbolic":
            return self._hyperbolic(numbers, max_n)
        else:
            return self._cartesian(numbers, max_n)

    def _compute_frame_shift(self, n: int, max_n: int) -> float:
        if n <= 1:
            return 0.0
        base_shift = math.log(n) / math.log(max_n)
        oscillation = 0.1 * math.sin(2 * math.pi * n / (math.log(n) + 1))
        if self.coordinate_system == "spherical":
            oscillation *= math.cos(n * self.frequency)
        elif self.coordinate_system == "hyperbolic":
            oscillation *= math.tanh(n * self.frequency * 0.01)
        return base_shift + oscillation

    def _cylindrical(self, n, max_n):
        fs = np.array([self._compute_frame_shift(i, max_n) for i in n])
        x = n
        y = n * (n / math.pi) * self._correction_factor * (1 + fs)
        z = np.sin(math.pi * self.frequency * n + self.phase) * (1 + 0.5 * fs)
        return np.vstack((x, y, z)).T

    def _spherical(self, n, max_n):
        fs = np.array([self._compute_frame_shift(i, max_n) for i in n])
        r = np.log(n + 1) * self._correction_factor
        theta = (2 * math.pi * self.frequency * n + self.phase) % (2 * math.pi)
        phi = (math.pi * n / np.log(n + 2)) % math.pi
        x = r * np.sin(phi) * np.cos(theta) * (1 + fs)
        y = r * np.sin(phi) * np.sin(theta) * (1 + fs)
        z = r * np.cos(phi) * (1 + fs)
        return np.vstack((x, y, z)).T

    def _hyperbolic(self, n, max_n):
        fs = np.array([self._compute_frame_shift(i, max_n) for i in n])
        u = np.log(n + 1) * self._correction_factor
        v = (self.frequency * n + self.phase) % (2 * math.pi)
        x = np.cosh(u) * np.cos(v) * (1 + fs)
        y = np.sinh(u) * np.sin(v) * (1 + fs)
        z = np.tanh(u * self.frequency) * (1 + 0.3 * fs)
        return np.vstack((x, y, z)).T

    def _cartesian(self, n, max_n):
        fs = np.array([self._compute_frame_shift(i, max_n) for i in n])
        x = n
        y = (n ** (1 + self.frequency)) * self._correction_factor * (1 + fs)
        z = np.sin(2 * math.pi * self.frequency * np.log(n + 1) + self.phase) * (1 + fs)
        return np.vstack((x, y, z)).T


class GeometricTriangulator:
    """
    Combines projections and Z-metric invariance to triangulate special numbers.
    """
    def __init__(self):
        self.projections = []

    def add_projection(self, proj: GeometricProjection):
        self.projections.append(proj)

    def create_standard_projections(self):
        # Prime filters
        self.add_projection(GeometricProjection("PrimeSpiral", math.e / ((1 + math.sqrt(5)) / 2), 0.091, 0, "cylindrical"))
        self.add_projection(GeometricProjection("GoldenSphere", math.e * ((1 + math.sqrt(5)) / 2) / math.pi, 0.161, math.pi/4, "spherical"))
        self.add_projection(GeometricProjection("LogarithmicHyperbolic", math.e / math.pi, 0.072, 0, "hyperbolic"))
        # Special forms
        self.add_projection(GeometricProjection("TwinPrimeFilter", math.e * math.sqrt(2) / math.pi, 0.105, math.pi/6, "cylindrical"))
        self.add_projection(GeometricProjection("CoprimeCartesian", math.e / math.sqrt(2), 0.382, 0, "cartesian"))
        self.add_projection(GeometricProjection("MersenneSpherical", math.e * 2 / math.pi, 0.250, math.pi/3, "spherical"))

    def triangulate_candidates(self, number_range: tuple, sample_size: int = 1000, target_type: str = "primes"):
        start, end = number_range
        numbers = np.linspace(start, end, sample_size, dtype=int)

        # Project & density for each filter
        density_maps = {}
        for proj in self.projections:
            coords = proj.project_numbers(numbers, end)
            density_maps[proj.name] = self._compute_density_map(coords)

        # Compute Z-metric invariance
        remainders = numbers % SPEED_OF_LIGHT
        zeta_cumulative = np.cumsum(remainders)
        zeta_shift = zeta_cumulative / SPEED_OF_LIGHT

        # Consensus now includes Z-metric as an extra “map”
        consensus = self._compute_consensus_map(density_maps, zeta_shift)

        # Triangulate based on consensus + type
        candidates = self._perform_triangulation(consensus, density_maps, numbers, target_type)
        return {
            "numbers": numbers,
            "density_maps": density_maps,
            "zeta_shift": zeta_shift,
            "consensus_map": consensus,
            "candidates": candidates
        }

    def _compute_density_map(self, coords: np.ndarray) -> np.ndarray:
        if len(coords) < 3:
            return np.zeros(0)
        tree = KDTree(coords)
        k = min(7, len(coords) - 1)
        dists, _ = tree.query(coords, k=k)
        dens = np.zeros(len(coords))
        for i in range(len(coords)):
            if dists[i,1] > 0:
                hm = k / np.sum(1.0 / (dists[i,1:] + 1e-10))
                dens[i] = 1.0 / (hm + 1e-10)
        return dens

    def _compute_consensus_map(self, density_maps: dict, zeta_shift: np.ndarray) -> np.ndarray:
        # Normalize all projection maps
        norms = []
        for dm in density_maps.values():
            if np.max(dm) > 0:
                norms.append((dm - dm.min()) / (dm.max() - dm.min()))
        # Normalize ZetaShift
        zs = (zeta_shift - zeta_shift.min()) / (zeta_shift.max() - zeta_shift.min())
        norms.append(zs)

        # Geometric mean across all “maps”
        consensus = np.ones_like(norms[0])
        for arr in norms:
            consensus *= (arr + 1e-3)
        return consensus ** (1.0 / len(norms))

    def _perform_triangulation(self, consensus: np.ndarray, density_maps: dict,
                               numbers: np.ndarray, target_type: str) -> np.ndarray:
        # Simple prime filter example
        thresh = np.percentile(consensus, 85)
        mask = consensus > thresh
        return numbers[mask]


# Example demo
if __name__ == "__main__":
    tri = GeometricTriangulator()
    tri.create_standard_projections()
    res = tri.triangulate_candidates((1000, 2000), sample_size=500, target_type="primes")

    print(f"Found {len(res['candidates'])} candidates with Z-metric invariance injected")
    print("Top 10:", sorted(res['candidates'])[:10])
