import math
import numpy as np
import timeit

from domain import DiscreteZetaShift

def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3):
        if n == p:
            return True
        if n % p == 0:
            return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17):
        if a >= n:
            break
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def is_mersenne_prime(p):
    if p == 2:
        return True
    m = (1 << p) - 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % m
    return s == 0

UNIVERSAL = math.e
PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

class GeometricProjection:
    def __init__(self, name: str, rate: float, frequency: float, phase: float = 0, coordinate_system: str = "cylindrical", use_zeta: bool = False):
        self.name = name
        self.rate = rate
        self.frequency = frequency
        self.phase = phase
        self.coordinate_system = coordinate_system
        self.use_zeta = use_zeta
        self._correction_factor = rate / UNIVERSAL

    def project_numbers(self, numbers: np.array, max_n: int) -> np.array:
        n = np.array(numbers, dtype=float)
        if self.use_zeta:
            if len(n) < 2:
                frame_shifts = np.zeros_like(n)
            else:
                deltas = np.diff(n)
                deltas = np.append(deltas, deltas[-1])  # Repeat last gap for the final element
                delta_max = np.max(deltas)
                frame_shifts = np.zeros_like(n)
                for i in range(len(n)):
                    zeta = DiscreteZetaShift(n=n[i], delta_n=deltas[i], delta_max=delta_max)
                    frame_shifts[i] = zeta.compute_z() / n[i]  # Normalized frame shift: Δₙ / Δmax
        else:
            frame_shifts = np.array([math.log(i) / math.log(max_n) if i > 1 else 0.0 for i in n])

        if self.coordinate_system == "cylindrical":
            return self._cylindrical_projection(n, max_n, frame_shifts)
        elif self.coordinate_system == "spherical":
            return self._spherical_projection(n, max_n, frame_shifts)
        else:
            return self._hyperbolic_projection(n, max_n, frame_shifts)

    def _cylindrical_projection(self, n: np.array, max_n: int, frame_shifts: np.array) -> np.array:
        x = n
        y = n * np.log(n + 1) / UNIVERSAL * self._correction_factor * (1 + frame_shifts)
        z = np.sin(PI * self.frequency * n + self.phase) * (1 + 0.5 * frame_shifts)
        return np.column_stack((x, y, z))

    def _spherical_projection(self, n: np.array, max_n: int, frame_shifts: np.array) -> np.array:
        r = np.log(n + 1) * self._correction_factor
        theta = (2 * PI * self.frequency * n + self.phase) % (2 * PI)
        phi = (PI * n / np.log(n + 2)) % PI
        x = r * np.sin(phi) * np.cos(theta) * (1 + frame_shifts)
        y = r * np.sin(phi) * np.sin(theta) * (1 + frame_shifts)
        z = r * np.cos(phi) * (1 + frame_shifts)
        return np.column_stack((x, y, z))

    def _hyperbolic_projection(self, n: np.array, max_n: int, frame_shifts: np.array) -> np.array:
        u = np.log(n + 1) * self._correction_factor
        v = (self.frequency * n + self.phase) % (2 * PI)
        x = np.cosh(u) * np.cos(v) * (1 + frame_shifts)
        y = np.sinh(u) * np.sin(v) * (1 + frame_shifts)
        z = np.tanh(u * self.frequency) * (1 + 0.3 * frame_shifts)
        return np.column_stack((x, y, z))

class ChainedProjection:
    def __init__(self, projections):
        self.projections = projections

    def apply_chain(self, numbers: np.array, max_n: int) -> tuple:
        current_coords = numbers
        density_maps = []
        for proj in self.projections:
            coords = proj.project_numbers(current_coords, max_n)
            distances = np.sqrt(((coords[:, np.newaxis, :] - coords[np.newaxis, :, :]) ** 2).sum(axis=2))
            np.fill_diagonal(distances, 1e-10)
            density_map = np.sum(1.0 / (distances + 1e-10), axis=1) / len(coords)
            density_maps.append(density_map)
            current_coords = coords[:, 2]
        combined_density = np.prod(np.array(density_maps) + 0.1, axis=0) ** (1.0 / len(density_maps))
        return coords, combined_density

class GeometricTriangulator:
    def __init__(self):
        self.projections = []

    def create_standard_projections(self):
        self.projections = [
            GeometricProjection("PrimeSpiral", UNIVERSAL/PHI, 0.1, 0, "cylindrical", use_zeta=True),
            GeometricProjection("GoldenSphere", UNIVERSAL*PHI/PI, 0.161, PI/4, "spherical", use_zeta=True),
            GeometricProjection("LogarithmicHyperbolic", UNIVERSAL/PI, 0.072, 0, "hyperbolic", use_zeta=True)
        ]

    def triangulate_candidates(self, number_range: tuple = None, sample_size: int = 1000, target_type: str = "primes", numbers: np.array = None, skip_triangles: bool = False) -> dict:
        if numbers is None:
            start_n, end_n = number_range
            n_sample = np.linspace(start_n, end_n, sample_size, dtype=int)
        else:
            n_sample = numbers
            end_n = int(max(n_sample))
        chained_proj = ChainedProjection(self.projections)
        final_coords, combined_density = chained_proj.apply_chain(n_sample, end_n)
        candidates = self._perform_triangulation(combined_density, n_sample, target_type)
        if not skip_triangles:
            triangles = self._construct_triangles(final_coords, combined_density, n_sample, target_type)
        else:
            triangles = []
        return {
            'candidates': list(candidates),
            'final_coords': final_coords.tolist(),
            'density_map': combined_density.tolist(),
            'triangles': triangles
        }

    def _perform_triangulation(self, density_map: list, numbers: np.array, target_type: str) -> np.array:
        density_map = np.array(density_map)
        threshold = np.percentile(density_map, 85) if len(density_map) > 0 else 0
        candidates = numbers[density_map > threshold]
        if len(candidates) == 0:
            return np.array([])
        if target_type == "mersenne_primes":
            return candidates
        return candidates

    def _construct_triangles(self, coords: np.array, density_map: list, numbers: np.array, target_type: str) -> list:
        density_map = np.array(density_map)
        high_density_indices = np.where(density_map > np.percentile(density_map, 85))[0]
        if len(high_density_indices) < 3:
            return []
        # Compute frame shifts consistently with zeta for triangles
        if len(numbers) >= 2:
            deltas = np.diff(numbers)
            deltas = np.append(deltas, deltas[-1])
            delta_max = np.max(deltas)
            frame_shifts_all = np.zeros_like(numbers, dtype=float)
            for i in range(len(numbers)):
                zeta = DiscreteZetaShift(n=numbers[i], delta_n=deltas[i], delta_max=delta_max)
                frame_shifts_all[i] = zeta.compute_z() / numbers[i]
        else:
            frame_shifts_all = np.zeros_like(numbers, dtype=float)
        max_frame_shift = np.max(frame_shifts_all) if len(frame_shifts_all) > 0 else 1e-10
        triangles = []

        def compute_angle(a, b, c):
            ab = np.array(b) - np.array(a)
            ac = np.array(c) - np.array(a)
            cos_angle = np.dot(ab, ac) / (np.linalg.norm(ab) * np.linalg.norm(ac) + 1e-10)
            cos_angle = np.clip(cos_angle, -1, 1)
            return np.arccos(cos_angle)

        for i in range(len(high_density_indices) - 2):
            idx1, idx2, idx3 = high_density_indices[i:i+3]
            triangle = [coords[idx1], coords[idx2], coords[idx3]]
            numbers_tri = [numbers[idx1], numbers[idx2], numbers[idx3]]
            frame_shifts = [frame_shifts_all[idx] for idx in [idx1, idx2, idx3]]
            z_values = [n * (fs / max_frame_shift) if fs > 0 else 0 for n, fs in zip(numbers_tri, frame_shifts)]
            area = self._compute_triangle_area(triangle)
            angles = [compute_angle(triangle[0], triangle[1], triangle[2]),
                      compute_angle(triangle[1], triangle[0], triangle[2]),
                      compute_angle(triangle[2], triangle[0], triangle[1])]
            centroid = np.mean(triangle, axis=0)
            centroid_distance = np.linalg.norm(centroid)
            z_variance = np.var(z_values) if z_values else 0
            if target_type == "mersenne_primes":
                triangle_type = "mersenne" if z_variance > 1000 else "non_mersenne"
            else:
                triangle_type = "general"
            triangles.append({
                'vertices': [v.tolist() for v in triangle],
                'numbers': numbers_tri,
                'z_values': z_values,
                'area': area,
                'angles': angles,
                'centroid_distance': float(centroid_distance),
                'type': triangle_type
            })
        return triangles

    def _compute_triangle_area(self, triangle: list) -> float:
        a, b, c = triangle
        ab = np.array(b) - np.array(a)
        ac = np.array(c) - np.array(a)
        cross_product = np.cross(ab, ac)
        return 0.5 * np.linalg.norm(cross_product)

def generate_primes(target):
    found = []
    candidate = 2
    while len(found) < target:
        if is_prime(candidate):
            found.append(candidate)
        candidate += 1
    return found

primes = generate_primes(30)
print("Generated", len(primes), "primes up to", primes[-1])

def standard_check():
    mersenne = [p for p in primes if is_mersenne_prime(p)]
    return mersenne

def geometric_check():
    triangulator = GeometricTriangulator()
    triangulator.create_standard_projections()
    numbers = np.array(primes)
    results = triangulator.triangulate_candidates(numbers=numbers, target_type="mersenne_primes", skip_triangles=True)
    candidates = results['candidates']
    mersenne = [p for p in candidates if is_mersenne_prime(p)]
    return mersenne, len(candidates)

standard_mersenne = standard_check()
geometric_mersenne, num_candidates = geometric_check()

print("Standard found:", sorted(standard_mersenne))
print("Geometric found:", sorted(geometric_mersenne))
print("Candidates checked in geometric:", num_candidates, "out of", len(primes))

if set(standard_mersenne) == set(geometric_mersenne):
    print("A/B test: Matches - all Mersenne primes found")
else:
    print("A/B test: Does not match - some missed:", set(standard_mersenne) - set(geometric_mersenne))

standard_time = timeit.timeit(standard_check, number=1000) / 1000
geometric_time = timeit.timeit(lambda: geometric_check()[0], number=1000) / 1000

print(f"Benchmark - Standard average time: {standard_time:.6f} seconds")
print(f"Benchmark - Geometric average time: {geometric_time:.6f} seconds")
print(f"Speedup factor: {standard_time / geometric_time:.2f}x" if geometric_time > 0 else "Infinite speedup")
print(f"Reduction in checks: {(1 - num_candidates / len(primes)) * 100:.2f}%")