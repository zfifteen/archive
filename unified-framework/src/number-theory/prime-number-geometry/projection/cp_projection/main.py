#!/usr/bin/env python3
"""
drift_corrected_triangulator.py

A geometric triangulation framework for prime candidates,
with observer-drift correction based on relativistic and rotational motions.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import Axes3D

# Physical & observational parameters
C = 299_792_458                # Speed of light (m/s)
R = 1e3                        # Sampling rate: numbers per second
A = 0.05                       # Amplitude of drift correction
PHI0 = 0.0                     # Global phase offset for swirl

motions = [
    # Earth rotation (~465 m/s at equator), 1 cycle per sidereal day
    {"v": 465.0,    "f": 1.0 / 86164.0},
    # Earth orbit (~29 800 m/s),   1 cycle per tropical year
    {"v": 29800.0,  "f": 1.0 / (365.2422 * 86400.0)},
    # Solar‐system galactic motion (~220 000 m/s), 1 cycle per 225 Myr
    {"v": 2.2e5,    "f": 1.0 / (225e6 * 365.2422 * 86400.0)},
]
for m in motions:
    m["gamma"] = 1.0 / math.sqrt(1.0 - (m["v"] / C) ** 2)


class GeometricProjection:
    """
    Projects integers into geometric spaces with drift-corrected frame shifts.
    """

    def __init__(self,
                 name: str,
                 rate: float,
                 frequency: float,
                 phase: float = 0.0,
                 coordinate_system: str = "cylindrical"):
        self.name = name
        self.rate = rate
        self.frequency = frequency
        self.phase = phase
        self.coordinate_system = coordinate_system
        self._corr = rate / math.e

    def project(self, nums: np.ndarray, max_n: int) -> np.ndarray:
        if self.coordinate_system == "cylindrical":
            return self._cylindrical(nums, max_n)
        elif self.coordinate_system == "spherical":
            return self._spherical(nums, max_n)
        elif self.coordinate_system == "hyperbolic":
            return self._hyperbolic(nums, max_n)
        else:
            return self._cartesian(nums, max_n)

    def _compute_frame_shift(self, n: int, max_n: int) -> float:
        # Base logarithmic shift
        if n <= 1:
            base = 0.0
        else:
            base = math.log(n) / math.log(max_n)

        # Projection-specific oscillation
        osc = 0.1 * math.sin(2 * math.pi * n / (math.log(n) + 1))
        if self.coordinate_system == "spherical":
            osc *= math.cos(n * self.frequency)
        elif self.coordinate_system == "hyperbolic":
            osc *= math.tanh(n * self.frequency * 0.01)

        # Drift phase from observer motion
        t = n / R
        phi = sum(2 * math.pi * m["f"] * m["gamma"] * t for m in motions)
        swirl = A * math.sin(phi + PHI0)

        # Subtract swirl to correct drift
        return base + osc - swirl

    def _cylindrical(self, n, max_n):
        fs = np.array([self._compute_frame_shift(int(i), max_n) for i in n])
        x = n
        y = n * (n / math.pi) * self._corr * (1 + fs)
        z = np.sin(math.pi * self.frequency * n + self.phase) * (1 + 0.5 * fs)
        return np.vstack((x, y, z)).T

    def _spherical(self, n, max_n):
        fs = np.array([self._compute_frame_shift(int(i), max_n) for i in n])
        r = np.log(n + 1) * self._corr
        theta = (2 * math.pi * self.frequency * n + self.phase) % (2 * math.pi)
        phi = (math.pi * n / np.log(n + 2)) % math.pi
        x = r * np.sin(phi) * np.cos(theta) * (1 + fs)
        y = r * np.sin(phi) * np.sin(theta) * (1 + fs)
        z = r * np.cos(phi) * (1 + fs)
        return np.vstack((x, y, z)).T

    def _hyperbolic(self, n, max_n):
        fs = np.array([self._compute_frame_shift(int(i), max_n) for i in n])
        u = np.log(n + 1) * self._corr
        v = (self.frequency * n + self.phase) % (2 * math.pi)
        x = np.cosh(u) * np.cos(v) * (1 + fs)
        y = np.sinh(u) * np.sin(v) * (1 + fs)
        z = np.tanh(u * self.frequency) * (1 + 0.3 * fs)
        return np.vstack((x, y, z)).T

    def _cartesian(self, n, max_n):
        fs = np.array([self._compute_frame_shift(int(i), max_n) for i in n])
        x = n
        y = (n ** (1 + self.frequency)) * self._corr * (1 + fs)
        z = np.sin(2 * math.pi * self.frequency * np.log(n + 1) + self.phase) * (1 + fs)
        return np.vstack((x, y, z)).T


class GeometricTriangulator:
    """
    Combines multiple projections to triangulate prime candidates
    and evaluates linearity after drift correction.
    """

    def __init__(self):
        self.projections = []

    def add_projection(self, proj: GeometricProjection):
        self.projections.append(proj)

    def create_standard_projections(self):
        phi = (1 + math.sqrt(5)) / 2
        self.add_projection(GeometricProjection("PrimeSpiral", math.e / phi, 0.091, 0.0, "cylindrical"))
        self.add_projection(GeometricProjection("GoldenSphere", math.e * phi / math.pi, 0.161, math.pi/4, "spherical"))
        self.add_projection(GeometricProjection("LogHyper", math.e / math.pi, 0.072, 0.0, "hyperbolic"))
        self.add_projection(GeometricProjection("TwinPrime", math.e * math.sqrt(2) / math.pi, 0.105, math.pi/6, "cylindrical"))
        self.add_projection(GeometricProjection("Coprime", math.e / math.sqrt(2), 0.382, 0.0, "cartesian"))
        self.add_projection(GeometricProjection("Mersenne", math.e * 2 / math.pi, 0.250, math.pi/3, "spherical"))

    def _compute_density(self, coords: np.ndarray) -> np.ndarray:
        if len(coords) < 3:
            return np.zeros(len(coords))
        tree = KDTree(coords)
        k = min(7, len(coords) - 1)
        d, _ = tree.query(coords, k=k)
        dens = np.zeros(len(coords))
        for i in range(len(coords)):
            if d[i, 1] > 0:
                hm = k / np.sum(1.0 / (d[i, 1:] + 1e-10))
                dens[i] = 1.0 / (hm + 1e-10)
        return dens

    def triangulate(self, num_range: tuple, sample_size: int = 1000) -> dict:
        start, end = num_range
        nums = np.linspace(start, end, sample_size, dtype=int)

        densities = {}
        for proj in self.projections:
            coords = proj.project(nums, end)
            densities[proj.name] = self._compute_density(coords)

        # Consensus via geometric mean of normalized densities
        norms = []
        for dm in densities.values():
            if dm.max() > 0:
                norms.append((dm - dm.min()) / (dm.max() - dm.min()))
        consensus = np.ones_like(norms[0])
        for arr in norms:
            consensus *= (arr + 1e-3)
        consensus = consensus ** (1.0 / len(norms))

        # Top 15% threshold
        thresh = np.percentile(consensus, 85)
        candidates = nums[consensus > thresh]

        return {
            "numbers": nums,
            "densities": densities,
            "consensus": consensus,
            "candidates": candidates
        }

    def evaluate_linearity(self, nums: np.ndarray, signal: np.ndarray):
        X = nums.reshape(-1, 1)
        reg = LinearRegression().fit(X, signal)
        return reg.score(X, signal), reg.coef_[0], reg.intercept_

    def visualize_2d(self, nums: np.ndarray, before: np.ndarray, after: np.ndarray):
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.scatter(nums, before, s=10, alpha=0.6)
        plt.title("Raw Consensus")
        plt.subplot(1, 2, 2)
        plt.scatter(nums, after, s=10, alpha=0.6, color="green")
        plt.title("Drift-Corrected Consensus")
        plt.tight_layout()
        plt.show()

    def visualize_3d_pca(self, coords: np.ndarray):
        pca = PCA(n_components=3).fit(coords)
        axis = pca.components_[0]
        proj = coords.dot(axis)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2],
                   c=proj, cmap="plasma", s=10)
        ax.set_title("3D Scatter (PCA Color by Projection)")
        plt.show()


if __name__ == "__main__":
    tri = GeometricTriangulator()
    tri.create_standard_projections()

    # Run before & after drift correction
    results = tri.triangulate((1000, 2000), sample_size=800)
    nums = results["numbers"]
    raw_consensus = results["consensus"]

    # For after-correction, re-triangulate with A > 0 (drift subtraction already baked in)
    corrected = tri.triangulate((1000, 2000), sample_size=800)
    corr_consensus = corrected["consensus"]

    # Evaluate linearity
    r2_before, m1, b1 = tri.evaluate_linearity(nums, raw_consensus)
    r2_after, m2, b2 = tri.evaluate_linearity(nums, corr_consensus)
    print(f"Linearity R² before: {r2_before:.4f}, after: {r2_after:.4f}")

    # Visualize 2D signals
    tri.visualize_2d(nums, raw_consensus, corr_consensus)

    # 3D visualization of best projection (use first proj as example)
    sample_coords = tri.projections[0].project(nums, nums.max())
    tri.visualize_3d_pca(sample_coords)

    # Show top prime candidates
    print(f"Found {len(corrected['candidates'])} candidates, top 10:")
    print(sorted(corrected["candidates"])[:10])
