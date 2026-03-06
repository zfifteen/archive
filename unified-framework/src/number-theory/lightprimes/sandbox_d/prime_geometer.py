#!/usr/bin/env python3
"""
prime_geometer.py

Self-contained implementation of geometric prime prediction with:
- Z-space triangulation
- Confidence-based mode transitions
- Twin prime tracking
- Miller-Rabin verification
"""

import argparse
import time
import math
import random
import numpy as np
import torch
import torch.nn as nn
from scipy.spatial import KDTree

# Constants
CONFIDENCE_THRESHOLD = 0.85  # Switch to predictive mode
FALLBACK_THRESHOLD = 0.65  # Revert to geometric mode
ACCURACY_TARGET = 0.92  # Target prediction accuracy
GROWTH_RATE = 8.0  # Confidence sensitivity
FOCUS_RADIUS = 1000  # Prediction sensitivity zone
MIN_GEOMETRIC_PRIMES = 1000  # Minimum primes before prediction
PREDICTION_WINDOW = 50  # Accuracy evaluation window


# ---------------------------
# Database and Embedding Code
# ---------------------------

class HarnessDatabase:
    """Container for initial prime data"""

    def __init__(self, primes, coords):
        self.primes = primes
        self.coords = coords

    @staticmethod
    def load(coords_path, primes_path):
        coords = np.load(coords_path)
        primes = np.loadtxt(primes_path, dtype=np.int64)
        return HarnessDatabase(primes, coords)


class StreamingDatabase:
    """Manages a sliding window of primes and their embeddings"""

    def __init__(self, window_size, dims):
        self.window_size = window_size
        self.dims = dims
        self.primes = []
        self.coords = []

    def add_point(self, prime, coord):
        self.primes.append(prime)
        self.coords.append(coord)
        if len(self.primes) > self.window_size:
            self.primes.pop(0)
            self.coords.pop(0)

    def __len__(self):
        return len(self.primes)


def embed_z(n, dims):
    """Dummy embedding function - replace with real implementation"""
    # In a real implementation, this would generate meaningful coordinates
    # For demonstration, we'll create a simple deterministic vector
    arr = np.zeros(dims)
    for i in range(dims):
        arr[i] = n ** (1 / (i + 1))  # Simple power-based features
    return arr


# ---------------------------
# Prime Verification
# ---------------------------

def miller_rabin(n, k=10):
    """Miller-Rabin probabilistic primality test."""
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n < 2:
        return False
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------------------------
# Geometric Prediction
# ---------------------------

class GeometricPredictor(nn.Module):
    """Neural network for prime location prediction via geometric extension"""

    def __init__(self, embed_dim, hidden_dim=64):
        super().__init__()
        self.embed_dim = embed_dim
        self.fc1 = nn.Linear(embed_dim * 3, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)
        self.scale = nn.Parameter(torch.tensor(1.0))

    def forward(self, A, B, C):
        """Predict next embedding from triangle ABC"""
        inputs = torch.cat([A, B, C])
        hidden = torch.relu(self.fc1(inputs))
        direction = self.fc2(hidden)
        norm = torch.norm(direction)
        if norm > 0:
            direction = direction / norm
        return C + self.scale * direction


def compute_theta(window_primes, coords, axes=(0, 2, 4), epsilon=0.01):
    """Compute adaptive theta threshold for geometric filtering"""
    if len(window_primes) < 2:
        return -np.inf
    primes = np.array(window_primes)
    coords = np.array(coords)  # Convert to numpy array
    gaps = np.diff(primes, prepend=primes[0] - 2)
    i, j, k = [ax % coords.shape[1] for ax in axes]
    zi, zj, zk = coords[:, i], coords[:, j], coords[:, k]
    product = zi * zj * zk
    gm = np.sign(product) * np.abs(product) ** (1 / 3)
    Zp = gm / np.exp(gaps)
    return np.min(Zp) - epsilon


def inverse_embedding(vec, last_prime, scaling=1.0):
    """Convert Z-space vector to approximate integer candidate"""
    magnitude = torch.norm(vec).item()
    candidate = last_prime + int(magnitude * scaling)
    return candidate + 1 if candidate % 2 == 0 else candidate


# ---------------------------
# Confidence Tracking
# ---------------------------

def confidence_function(accuracy):
    """Sigmoid confidence based on prediction accuracy"""
    return 1 / (1 + math.exp(-GROWTH_RATE * (accuracy - ACCURACY_TARGET)))


class PredictionTracker:
    """Manages prediction accuracy history and confidence"""

    def __init__(self, window_size=PREDICTION_WINDOW):
        self.history = []
        self.window_size = window_size

    def add_result(self, success):
        """Record prediction result (True/False)"""
        self.history.append(success)
        if len(self.history) > self.window_size:
            self.history.pop(0)

    @property
    def accuracy(self):
        """Current prediction accuracy"""
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)

    @property
    def confidence(self):
        """Current confidence score"""
        return confidence_function(self.accuracy)


# ---------------------------
# Main Function
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Geometric prime prediction with confidence-based mode transitions"
    )
    parser.add_argument("--coords", required=True, help="Path to harness coords .npy")
    parser.add_argument("--primes", required=True, help="Path to harness primes .txt")
    parser.add_argument("--prime-count", type=int, default=10000,
                        help="Total primes to reach (including harness)")
    parser.add_argument("--twin-mode", action="store_true", help="Enable twin prime tracking")
    parser.add_argument("--forecast", action="store_true", help="Enable predictive focusing")
    args = parser.parse_args()

    # ----- Database Initialization -----
    harness = HarnessDatabase.load(args.coords, args.primes)
    initial_primes = harness.primes.tolist()
    initial_count = len(initial_primes)
    dims = harness.coords.shape[1]

    stream_db = StreamingDatabase(window_size=360, dims=dims)
    for p, coord in zip(initial_primes, harness.coords):
        stream_db.add_point(p, coord)

    # ----- System State Initialization -----
    current_mode = "geometric"  # geometric, predictive
    tracker = PredictionTracker()
    focus_theta = None
    focus_center = None
    prediction_cache = set()
    twin_pairs = []
    twin_embeddings = []
    twin_tree = None

    last_prime = initial_primes[-1]
    primes_found = 0
    new_target = max(0, args.prime_count - initial_count)
    current = last_prime + 2
    theta = compute_theta(initial_primes, harness.coords)

    # ----- Neural Predictor Setup -----
    predictor = GeometricPredictor(dims)
    optimizer = torch.optim.Adam(predictor.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()

    # Pretrain with harness data
    if len(initial_primes) >= 3:
        for _ in range(100):
            optimizer.zero_grad()
            i = random.randint(0, len(initial_primes) - 3)
            A = torch.tensor(harness.coords[i], dtype=torch.float32)
            B = torch.tensor(harness.coords[i + 1], dtype=torch.float32)
            C = torch.tensor(harness.coords[i + 2], dtype=torch.float32)
            actual = torch.tensor(harness.coords[i + 3], dtype=torch.float32)

            pred = predictor(A, B, C)
            loss = loss_fn(pred, actual)
            loss.backward()
            optimizer.step()

    # ----- Twin Prime Setup -----
    prime_set = set(initial_primes)
    if args.twin_mode:
        twin_pairs = [(p, p + 2) for p in initial_primes[:-1] if (p + 2) in prime_set]
        if twin_pairs:
            twin_embeddings = [
                np.concatenate((harness.coords[initial_primes.index(p)],
                                harness.coords[initial_primes.index(p + 2)]))
                for p, _ in twin_pairs
            ]
            twin_tree = KDTree(twin_embeddings)

    # ----- Main Streaming Loop -----
    start_time = time.time()
    ints_scanned = 0
    mr_calls = 0

    while primes_found < new_target:
        ints_scanned += 1

        # ===== MODE: GEOMETRIC FILTERING =====
        if current_mode == "geometric":
            # Apply Z'-metric pre-filter
            gap = current - last_prime
            zvec = embed_z(current, dims)
            i, j, k = 0, 2, 4
            zi, zj, zk = zvec[i % dims], zvec[j % dims], zvec[k % dims]
            product = zi * zj * zk
            gm = np.sign(product) * np.abs(product) ** (1 / 3)
            Zp = gm / np.exp(gap) if gap > 0 else 0

            # Check if in focus region (lowered threshold)
            threshold = theta  # Default threshold
            if (args.forecast and focus_theta is not None and focus_center is not None
                    and abs(current - focus_center) < FOCUS_RADIUS):
                threshold = focus_theta

            if Zp >= threshold:
                # Verify candidate with Miller-Rabin
                mr_calls += 1
                is_prime = miller_rabin(current)

                if is_prime:
                    # Twin prime detection
                    is_twin = False
                    if args.twin_mode:
                        mr_calls += 1
                        is_twin = miller_rabin(current + 2) and (current + 2 - current == 2)

                    # Update system state
                    primes_found += 1
                    prime_set.add(current)
                    stream_db.add_point(current, zvec)
                    last_prime = current

                    # Twin registration
                    if is_twin:
                        twin_pairs.append((current, current + 2))
                        if args.twin_mode:
                            z_next = embed_z(current + 2, dims)
                            twin_embeddings.append(np.concatenate((zvec, z_next)))
                            twin_tree = KDTree(twin_embeddings) if twin_embeddings else None

                    # Make internal prediction when possible
                    if len(stream_db.primes) >= 3 and primes_found >= MIN_GEOMETRIC_PRIMES:
                        # Get last three primes
                        primes = stream_db.primes[-3:]
                        coords = np.array(stream_db.coords[-3:])  # Convert to numpy array

                        # Predict next location
                        A = torch.tensor(coords[0], dtype=torch.float32)
                        B = torch.tensor(coords[1], dtype=torch.float32)
                        C = torch.tensor(coords[2], dtype=torch.float32)
                        with torch.no_grad():
                            pred_vec = predictor(A, B, C)
                        pred_candidate = inverse_embedding(pred_vec, last_prime)

                        # Add to prediction cache
                        prediction_cache.add(pred_candidate)

                        # Train predictor
                        actual_vec = embed_z(current, dims)
                        optimizer.zero_grad()
                        pred = predictor(A, B, C)
                        loss = loss_fn(pred, torch.tensor(actual_vec, dtype=torch.float32))
                        loss.backward()
                        optimizer.step()

                        # Update theta
                        theta = compute_theta(stream_db.primes, np.array(stream_db.coords))  # Convert to numpy array

        # ===== MODE: PREDICTIVE VERIFICATION =====
        elif current_mode == "predictive" and current in prediction_cache:
            # Verify predicted candidate
            mr_calls += 1
            is_prime = miller_rabin(current)

            if is_prime:
                # Successful prediction
                tracker.add_result(True)

                # Update system state
                primes_found += 1
                prime_set.add(current)
                zvec = embed_z(current, dims)
                stream_db.add_point(current, zvec)
                last_prime = current

                # Twin detection and registration
                if args.twin_mode:
                    mr_calls += 1
                    if miller_rabin(current + 2):
                        twin_pairs.append((current, current + 2))
                        if twin_tree is not None:
                            z_next = embed_z(current + 2, dims)
                            twin_embeddings.append(np.concatenate((zvec, z_next)))
                            twin_tree = KDTree(twin_embeddings)

                # Generate next prediction
                if len(stream_db.primes) >= 3:
                    primes = stream_db.primes[-3:]
                    coords = np.array(stream_db.coords[-3:])  # Convert to numpy array
                    A = torch.tensor(coords[0], dtype=torch.float32)
                    B = torch.tensor(coords[1], dtype=torch.float32)
                    C = torch.tensor(coords[2], dtype=torch.float32)

                    with torch.no_grad():
                        pred_vec = predictor(A, B, C)
                    pred_candidate = inverse_embedding(pred_vec, last_prime)

                    prediction_cache = {pred_candidate}
            else:
                # Failed prediction
                tracker.add_result(False)
                prediction_cache.discard(current)

        # ===== MODE TRANSITION LOGIC =====
        # Switch to predictive mode when confident
        if (current_mode == "geometric" and
                tracker.confidence > CONFIDENCE_THRESHOLD and
                len(prediction_cache) > 0):
            current_mode = "predictive"
            focus_theta = None  # Reset focus
            # Jump to the nearest predicted candidate
            if prediction_cache:
                current = min(prediction_cache)

        # Fallback to geometric mode on low confidence
        elif (current_mode == "predictive" and
              tracker.confidence < FALLBACK_THRESHOLD):
            current_mode = "geometric"
            prediction_cache.clear()
            # Resume sequential scanning
            current = last_prime + 2

        # ===== PREDICTIVE FOCUSING =====
        if (args.forecast and
                current_mode == "geometric" and
                len(prediction_cache) > 0):
            # Get most probable prediction
            focus_center = min(prediction_cache, key=lambda x: abs(x - current))

            # Lower theta in focus region
            focus_theta = theta * 0.7 if theta > -np.inf else theta

        # Advance to next candidate
        if current_mode == "geometric":
            current += 2
        elif current_mode == "predictive":
            if current in prediction_cache:
                # Remove processed candidate
                prediction_cache.discard(current)

            # Move to next predicted candidate or resume scanning
            if prediction_cache:
                current = min(prediction_cache)
            else:
                current = last_prime + 2
                current_mode = "geometric"  # Fallback if no predictions

    # ----- Performance Summary -----
    total_time = time.time() - start_time
    tests_per_sec = ints_scanned / total_time if total_time > 0 else float('inf')
    primes_per_sec = primes_found / total_time if total_time > 0 else float('inf')

    print("\n===== GEOMETRIC PRIME DISCOVERY COMPLETE =====")
    print(f"  Primes found: {primes_found} (target: {new_target})")
    print(f"  Integers scanned: {ints_scanned}")
    print(f"  Miller-Rabin calls: {mr_calls}")
    print(f"  Final confidence: {tracker.confidence:.2f}")
    print(f"  Prediction accuracy: {tracker.accuracy:.2%}")
    print(f"  Time elapsed: {total_time:.2f} seconds")
    print(f"  Primes/sec: {primes_per_sec:.2f}")
    print(f"  Tests/sec: {tests_per_sec:.2f}")

    if args.twin_mode:
        print("\n===== TWIN PRIME SUMMARY =====")
        print(f"  Twin pairs found: {len(twin_pairs)}")
        if twin_pairs:
            print(f"  Last twin pair: {twin_pairs[-1]}")

    # Final sanity check
    if primes_found > 0:
        last_prime = stream_db.primes[-1]
        is_prime = miller_rabin(last_prime)
        print(f"\nSanity check: Last prime {last_prime} {'valid' if is_prime else 'INVALID'}")


if __name__ == "__main__":
    main()