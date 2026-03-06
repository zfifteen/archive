#!/usr/bin/env python3
"""
Categorical Biproduct Enhanced GVA

Implements biproduct decomposition of torus embeddings with:
- Per-dimension variance analysis
- Adaptive sampling allocation
- Matrix-based transformations
- Component-wise distance computation

Mission Charter Compliance: See EXPERIMENT_REPORT.md for full charter elements.
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass

# Add python/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

try:
    from mpmath import mp, mpf, sqrt, log, exp, power, frac
except ImportError:
    print("Error: mpmath not installed. Install with: pip install mpmath")
    sys.exit(1)

# High precision
mp.dps = 150

# Golden ratio
PHI = mpf((1 + sqrt(5)) / 2)


@dataclass
class BiproductComponent:
    """Represents one component in a biproduct decomposition."""
    index: int
    dimension: int
    variance: float
    weight: float
    sample_allocation: int


class CategoricalGVA:
    """
    Categorical biproduct-enhanced GVA.
    
    Decomposes d-dimensional torus into k biproduct components,
    applies variance-adaptive sampling, and uses matrix representations
    for efficient transformations.
    """
    
    def __init__(
        self,
        total_dims: int = 5,
        n_components: int = 5,
        k: float = 0.3,
        variance_adaptive: bool = True
    ):
        """
        Initialize categorical GVA.
        
        Args:
            total_dims: Total torus dimensions
            n_components: Number of biproduct components (≤ total_dims)
            k: Geometric resolution parameter
            variance_adaptive: Enable variance-adaptive sampling
        """
        self.total_dims = total_dims
        self.n_components = min(n_components, total_dims)
        self.k = k
        self.variance_adaptive = variance_adaptive
        
        # Each component is one dimension (can be generalized)
        self.components = [
            BiproductComponent(
                index=i,
                dimension=1,
                variance=0.0,
                weight=1.0,
                sample_allocation=0
            )
            for i in range(self.n_components)
        ]
        
        # Transformation matrix (identity initially)
        self.transform_matrix = np.eye(self.n_components, dtype=float)
    
    def embed_component(self, n: int, component_idx: int) -> float:
        """
        Embed integer into a single biproduct component.
        
        Args:
            n: Integer to embed
            component_idx: Component index
            
        Returns:
            Coordinate in [0, 1)
        """
        c = exp(2)  # e²
        x = mpf(n) / c
        
        # Iterate to the specific component
        for i in range(component_idx + 1):
            x_mod = x % PHI
            x = PHI * power(x_mod / PHI, self.k)
        
        return float(frac(x))
    
    def embed_categorical(self, n: int) -> np.ndarray:
        """
        Embed integer via biproduct decomposition.
        
        Args:
            n: Integer to embed
            
        Returns:
            Coordinate vector (n_components,)
        """
        coords = np.array([
            self.embed_component(n, i) 
            for i in range(self.n_components)
        ])
        
        # Apply transformation matrix
        return self.transform_matrix @ coords
    
    def component_distance(
        self,
        coord1: float,
        coord2: float,
        kappa: float
    ) -> float:
        """
        Compute Riemannian distance in a single component.
        
        Args:
            coord1: First coordinate
            coord2: Second coordinate
            kappa: Curvature parameter
            
        Returns:
            Component distance
        """
        # Wraparound distance on circle
        d = min(abs(coord1 - coord2), 1.0 - abs(coord1 - coord2))
        # Riemannian metric
        return d * (1 + kappa * d)
    
    def distance_categorical(
        self,
        coords1: np.ndarray,
        coords2: np.ndarray,
        N: int
    ) -> float:
        """
        Compute Riemannian distance via biproduct decomposition.
        
        Args:
            coords1: First point
            coords2: Second point
            N: Modulus for curvature
            
        Returns:
            Total Riemannian distance
        """
        # Discrete curvature
        kappa = float(4 * log(mpf(N) + 1) / exp(2))
        
        # Sum over components (each weighted)
        total = 0.0
        for i, (c1, c2) in enumerate(zip(coords1, coords2)):
            component_dist = self.component_distance(c1, c2, kappa)
            weight = self.components[i].weight if i < len(self.components) else 1.0
            total += (weight * component_dist) ** 2
        
        return math.sqrt(total)
    
    def estimate_component_variances(
        self,
        candidates: List[int]
    ) -> None:
        """
        Estimate variance in each biproduct component from sample.
        
        Args:
            candidates: List of candidate integers
        """
        # Embed all candidates
        coords = np.array([self.embed_categorical(c) for c in candidates])
        
        # Compute per-component variance
        variances = np.var(coords, axis=0)
        
        for i, var in enumerate(variances):
            if i < len(self.components):
                self.components[i].variance = float(var)
    
    def allocate_samples_adaptive(
        self,
        total_samples: int
    ) -> None:
        """
        Allocate samples to components based on variance.
        
        High-variance components get more samples for better coverage.
        
        Args:
            total_samples: Total sample budget
        """
        if not self.variance_adaptive:
            # Uniform allocation
            samples_per_component = total_samples // self.n_components
            for comp in self.components:
                comp.sample_allocation = samples_per_component
            return
        
        # Allocate proportional to sqrt(variance)
        total_var = sum(math.sqrt(c.variance + 1e-12) for c in self.components)
        
        if total_var < 1e-12:
            # Fallback to uniform
            samples_per_component = total_samples // self.n_components
            for comp in self.components:
                comp.sample_allocation = samples_per_component
        else:
            for comp in self.components:
                proportion = math.sqrt(comp.variance + 1e-12) / total_var
                comp.sample_allocation = max(1, int(proportion * total_samples))
    
    def compute_transformation_matrix(
        self,
        candidates: List[int],
        method: str = "pca"
    ) -> None:
        """
        Compute transformation matrix for coordinate rotation.
        
        Args:
            candidates: Sample candidates for covariance estimation
            method: Transformation method ("pca" or "identity")
        """
        if method == "identity":
            self.transform_matrix = np.eye(self.n_components, dtype=float)
            return
        
        # Embed candidates without transformation
        old_matrix = self.transform_matrix
        self.transform_matrix = np.eye(self.n_components, dtype=float)
        
        coords = np.array([self.embed_categorical(c) for c in candidates])
        
        # PCA-based transformation
        if method == "pca":
            # Center coordinates
            mean_coords = np.mean(coords, axis=0)
            centered = coords - mean_coords
            
            # Compute covariance
            cov = np.cov(centered.T)
            
            # Eigendecomposition
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            
            # Sort by eigenvalue (descending)
            idx = np.argsort(eigenvalues)[::-1]
            eigenvectors = eigenvectors[:, idx]
            
            # Transformation matrix (rotate to principal components)
            self.transform_matrix = eigenvectors.T
        
        # Restore old matrix
        # (In practice, we'd use the new one, but for initial testing keep identity)
        # self.transform_matrix = old_matrix


def profile_categorical_gva(
    N: int,
    p_true: int,
    q_true: int,
    radius: int = 1000,
    dims: int = 5,
    n_components: int = 5,
    k: float = 0.3,
    n_samples: int = 100,
    variance_adaptive: bool = True,
    use_pca: bool = False
) -> Dict[str, Any]:
    """
    Profile categorical GVA on a known semiprime.
    
    Args:
        N: Semiprime to factor
        p_true: True prime factor p
        q_true: True prime factor q
        radius: Search radius
        dims: Total dimensions
        n_components: Biproduct components
        k: Geometric resolution
        n_samples: Sample count
        variance_adaptive: Enable adaptive sampling
        use_pca: Use PCA transformation
        
    Returns:
        Profiling metrics dictionary
    """
    sqrt_n = int(math.isqrt(N))
    
    # Initialize categorical GVA
    gva = CategoricalGVA(
        total_dims=dims,
        n_components=n_components,
        k=k,
        variance_adaptive=variance_adaptive
    )
    
    # Generate candidates
    np.random.seed(42)
    candidates = np.random.randint(
        max(2, sqrt_n - radius),
        sqrt_n + radius,
        size=n_samples
    ).tolist()
    
    # Estimate component variances
    t_start_var = time.perf_counter()
    gva.estimate_component_variances(candidates[:min(100, len(candidates))])
    t_variance_est = time.perf_counter() - t_start_var
    
    # Allocate samples
    gva.allocate_samples_adaptive(n_samples)
    
    # Compute transformation matrix
    t_start_transform = time.perf_counter()
    if use_pca:
        gva.compute_transformation_matrix(candidates[:min(100, len(candidates))], method="pca")
    t_transform = time.perf_counter() - t_start_transform
    
    # Embed true factors
    t_start_embed = time.perf_counter()
    p_coords = gva.embed_categorical(p_true)
    q_coords = gva.embed_categorical(q_true)
    t_embed_factors = time.perf_counter() - t_start_embed
    
    # Embed all candidates
    t_start_batch = time.perf_counter()
    candidate_coords = [gva.embed_categorical(c) for c in candidates]
    t_embed_batch = time.perf_counter() - t_start_batch
    
    # Compute distances
    t_start_dist = time.perf_counter()
    distances_to_p = [
        gva.distance_categorical(c, p_coords, N)
        for c in candidate_coords
    ]
    distances_to_q = [
        gva.distance_categorical(c, q_coords, N)
        for c in candidate_coords
    ]
    t_distance_batch = time.perf_counter() - t_start_dist
    
    # Variance analysis
    coords_array = np.array(candidate_coords)
    variance_per_component = np.var(coords_array, axis=0).tolist()
    total_variance = sum(variance_per_component)
    
    # Find nearest candidates
    idx_nearest_p = int(np.argmin(distances_to_p))
    idx_nearest_q = int(np.argmin(distances_to_q))
    
    min_dist_p = distances_to_p[idx_nearest_p]
    min_dist_q = distances_to_q[idx_nearest_q]
    
    nearest_to_p = candidates[idx_nearest_p]
    nearest_to_q = candidates[idx_nearest_q]
    
    found_p = (p_true in candidates)
    found_q = (q_true in candidates)
    
    return {
        "modulus": N,
        "p_true": p_true,
        "q_true": q_true,
        "method": "categorical_biproduct",
        "dimensions": dims,
        "n_components": n_components,
        "k_parameter": k,
        "n_samples": n_samples,
        "variance_adaptive": variance_adaptive,
        "use_pca": use_pca,
        "timing": {
            "variance_estimation_sec": t_variance_est,
            "transformation_sec": t_transform,
            "embed_factors_sec": t_embed_factors,
            "embed_batch_sec": t_embed_batch,
            "embed_per_candidate_sec": t_embed_batch / n_samples,
            "distance_batch_sec": t_distance_batch,
            "distance_per_candidate_sec": t_distance_batch / n_samples,
            "total_sec": t_variance_est + t_transform + t_embed_batch + t_distance_batch
        },
        "variance": {
            "per_component": variance_per_component,
            "total": total_variance,
            "mean": total_variance / n_components,
            "max_component": int(np.argmax(variance_per_component)),
            "min_component": int(np.argmin(variance_per_component)),
            "component_ratio": max(variance_per_component) / (min(variance_per_component) + 1e-12)
        },
        "sample_allocation": [c.sample_allocation for c in gva.components],
        "component_weights": [c.weight for c in gva.components],
        "distances": {
            "min_to_p": min_dist_p,
            "min_to_q": min_dist_q,
            "nearest_candidate_to_p": nearest_to_p,
            "nearest_candidate_to_q": nearest_to_q,
            "p_error": abs(nearest_to_p - p_true),
            "q_error": abs(nearest_to_q - q_true),
            "mean_dist_to_p": float(np.mean(distances_to_p)),
            "std_dist_to_p": float(np.std(distances_to_p)),
            "mean_dist_to_q": float(np.mean(distances_to_q)),
            "std_dist_to_q": float(np.std(distances_to_q))
        },
        "found_factors": {
            "p_in_sample": found_p,
            "q_in_sample": found_q
        }
    }


def main():
    """Run categorical GVA profiling."""
    print("=" * 80)
    print("Categorical Biproduct Enhanced GVA")
    print("=" * 80)
    print()
    
    # Test case
    N = 18446736050711510819
    p = 4294948663
    q = 4294941307
    
    print(f"Test: 64-bit semiprime")
    print(f"  N = {N}")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print()
    
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Profile with different configurations
    configs = [
        {"variance_adaptive": False, "use_pca": False, "label": "baseline_cat"},
        {"variance_adaptive": True, "use_pca": False, "label": "var_adaptive"},
        {"variance_adaptive": True, "use_pca": True, "label": "var_adaptive_pca"},
    ]
    
    all_results = []
    for config in configs:
        print(f"Configuration: {config['label']}")
        
        result = profile_categorical_gva(
            N=N,
            p_true=p,
            q_true=q,
            radius=10000,
            dims=5,
            n_components=5,
            k=0.3,
            n_samples=1000,
            variance_adaptive=config["variance_adaptive"],
            use_pca=config["use_pca"]
        )
        result["config_label"] = config["label"]
        all_results.append(result)
        
        print(f"  Embedding: {result['timing']['embed_per_candidate_sec']*1e6:.2f} µs/candidate")
        print(f"  Distance:  {result['timing']['distance_per_candidate_sec']*1e6:.2f} µs/candidate")
        print(f"  Variance:  Total={result['variance']['total']:.6f}, Ratio={result['variance']['component_ratio']:.2f}")
        print(f"  Min dist to p: {result['distances']['min_to_p']:.6f}")
        print()
    
    # Save results
    output_file = results_dir / "categorical_profile.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    print("\nCategorical profiling complete.")


if __name__ == "__main__":
    main()
