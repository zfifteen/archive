#!/usr/bin/env python3
"""
stream_driver.py

Stream integers until the total specified primes is reached (including harness),
manage a 360-frame streaming window of Z-embeddings, and print only the final
performance summary with Miller-Rabin sanity. Integrates a neural-inspired layer
to adaptively refine Z(n) via learned deviation. Extended for twin prime detection,
spatial indexing with KDTree, and twin gap forecasting. Updates include twin pair
tracking, Z-gap analysis, and twin-specific summary stats while preserving original
prime streaming. Uses Z'-metric pre-filter (axes 0,2,4; adaptive theta) and
factorization-avoidant Miller-Rabin primality.
"""

import argparse
import time
import random
import numpy as np
import torch
import torch.nn as nn
from scipy.spatial import KDTree
from prime_hologram_harness import HarnessDatabase, embed_z
from prime_hologram_db import StreamingDatabase

def miller_rabin(n, k=10):
    """Miller-Rabin probabilistic primality test (factorization-avoidant)."""
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

class ZPredictor(nn.Module):
    """
    Neural module for Z refinement and twin gap prediction.
    Inputs: n (prime or twin index), delta (gap or mean twin gap).
    Output: ΔZ (deviation for primes) or predicted twin gap (twin mode).
    Architecture: 2-in MLP with hidden=num_epsilons, relu, sigmoid for twins.
    """
    def __init__(self, num_epsilons=20, gamma=1.0, twin_mode=False):
        super().__init__()
        self.fc1 = nn.Linear(2, num_epsilons)
        self.fc2 = nn.Linear(num_epsilons, 1)
        self.gamma = gamma
        self.twin_mode = twin_mode

    def forward(self, x_n, x_delta):
        input = torch.cat((x_n, x_delta), dim=1)
        hidden = torch.relu(self.fc1(input))
        out = self.fc2(hidden)
        if self.twin_mode:
            return torch.sigmoid(out) * 10.0  # Scale to reasonable gap range
        return out / self.gamma

def compute_theta(window_primes, coords, axes=(0,2,4), epsilon=0.01):
    """Compute adaptive theta as min Z' from window primes - epsilon."""
    if len(window_primes) < 2:
        return -np.inf
    primes = np.array(window_primes)
    gaps = np.diff(primes, prepend=primes[0] - 2)
    i, j, k = [ax % coords.shape[1] for ax in axes]
    zi, zj, zk = coords[:, i], coords[:, j], coords[:, k]
    product = zi * zj * zk
    gm = np.sign(product) * np.abs(product)**(1/3)
    Zp = gm / np.exp(gaps)
    min_Zp = np.min(Zp)
    return min_Zp - epsilon

def main():
    # ----- Parse arguments -----
    parser = argparse.ArgumentParser(
        description="Stream primes or twins until target count, update Z-embedding window, and forecast."
    )
    parser.add_argument("--coords", required=True, help="Path to harness coords .npy")
    parser.add_argument("--primes", required=True, help="Path to harness primes .txt")
    parser.add_argument("--forecast", action="store_true", help="Enable forecasting")
    parser.add_argument("--prime-count", type=int, default=10000,
                        help="Total primes or twins to reach (including harness)")
    parser.add_argument("--tune-freq", type=int, default=10, help="Fine-tuning frequency")
    parser.add_argument("--twin-mode", action="store_true", help="Focus on twin primes")
    parser.add_argument("--candidate", type=int, default=None, help="Candidate large number to guess if prime")
    args = parser.parse_args()

    # ----- Load and seed streaming window -----
    harness = HarnessDatabase.load(args.coords, args.primes)
    initial_primes = harness.primes.tolist()
    if not all(isinstance(p, (int, np.integer)) for p in initial_primes):
        raise ValueError("Initial primes must be integers")
    initial_count = len(initial_primes)
    dims = harness.coords.shape[1]
    if dims < 3:
        raise ValueError("Require dims >=3 for Z' pre-filter")

    stream_db = StreamingDatabase(window_size=initial_count, dims=dims)
    window_primes = initial_primes.copy()
    for p, coord in zip(initial_primes, harness.coords):
        stream_db.add_point(p, coord)

    # ----- Initialize twin tracking -----
    # Convert initial_primes to a set for faster membership testing
    prime_set = set(initial_primes)
    twin_pairs = [(p, p+2) for p in initial_primes[:-1] if (p+2) in prime_set]
    twin_embeds = []
    for p1, p2 in twin_pairs:
        z1 = stream_db.coords[initial_primes.index(p1)]
        z2 = stream_db.coords[initial_primes.index(p2)]
        twin_embeds.append(np.concatenate((z1, z2)))
    twin_count = len(twin_pairs)
    tree = KDTree(twin_embeds) if twin_embeds else None

    # ----- Adjust target -----
    new_target = max(0, args.prime_count - (twin_count if args.twin_mode else initial_count))

    # ----- Neural predictor setup -----
    model = ZPredictor(num_epsilons=20, gamma=1.0, twin_mode=args.twin_mode)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    # Prepare initial training data
    primes_arr = np.array(initial_primes, dtype=np.float32)
    gaps = np.diff(primes_arr)
    dummy_gap = np.mean(gaps) if len(gaps) > 0 else 1.0
    gaps = np.insert(gaps, 0, dummy_gap)
    classical_Z = primes_arr / np.exp(gaps)
    mean_Z = np.mean(classical_Z)
    deviations = classical_Z - mean_Z

    if args.twin_mode:
        twin_indices = np.arange(twin_count, dtype=np.float32)
        twin_gaps = np.array([2.0] * twin_count, dtype=np.float32)  # Twin gaps are 2
        X_n = torch.from_numpy(twin_indices).unsqueeze(1)
        X_delta = torch.from_numpy(twin_gaps).unsqueeze(1)
        Y_dev = torch.from_numpy(twin_gaps - np.mean(twin_gaps)).unsqueeze(1)
    else:
        X_n = torch.from_numpy(primes_arr).unsqueeze(1)
        X_delta = torch.from_numpy(gaps).unsqueeze(1)
        Y_dev = torch.from_numpy(deviations).unsqueeze(1)

    # Pretrain
    for epoch in range(50):
        optimizer.zero_grad()
        dev_pred = model(X_n, X_delta)
        loss = loss_fn(dev_pred, Y_dev)
        loss.backward()
        optimizer.step()

    def guess_prime(candidate):
        nonlocal mr_calls
        gap = candidate - last_prime
        if gap <= 0:
            print("Candidate must be greater than last prime.")
            return False
        classical_Z = candidate / np.exp(gap) if gap > 0 else 0.0
        assumed_dev = classical_Z - mean_Z
        n_t = torch.tensor([[float(candidate)]] if not args.twin_mode else [[float(twin_count) + 1.0]])
        delta_t = torch.tensor([[float(gap)]] if not args.twin_mode else [[2.0]])
        predicted_dev = model(n_t, delta_t).item()
        tolerance = 0.01
        if abs(predicted_dev - assumed_dev) < tolerance:
            print(f"Trajectory match within tolerance {tolerance}. Testing primality...")
            mr_calls += 1
            is_prime = miller_rabin(candidate)
            if args.twin_mode:
                mr_calls += 1
                is_next_prime = miller_rabin(candidate + 2)
                if is_prime and is_next_prime:
                    print(f"Amazing discovery! The pair ({candidate}, {candidate + 2}) is a twin prime!")
                    print(f"Details:")
                    print(f"  Candidate: {candidate}")
                    print(f"  Gap from last prime: {gap}")
                    print(f"  Classical Z: {classical_Z:.4f}")
                    print(f"  Mean Z: {mean_Z:.4f}")
                    print(f"  Predicted dev/gap: {predicted_dev:.4f}")
                    print(f"  Assumed dev: {assumed_dev:.4f}")
                    return True
                else:
                    print("Not a twin prime.")
                    return False
            else:
                if is_prime:
                    print(f"Amazing discovery! {candidate} is a prime!")
                    print(f"Details:")
                    print(f"  Gap from last prime: {gap}")
                    print(f"  Classical Z: {classical_Z:.4f}")
                    print(f"  Mean Z: {mean_Z:.4f}")
                    print(f"  Predicted dev: {predicted_dev:.4f}")
                    print(f"  Assumed dev: {assumed_dev:.4f}")
                    return True
                else:
                    print("Not prime.")
                    return False
        else:
            print(f"Trajectory not matched.")
            return False

    if args.candidate is not None:
        if guess_prime(args.candidate):
            import sys
            sys.exit(0)
        else:
            print("Proceeding with streaming loop.")

    # ----- Initialize counters & timer -----
    start_time = time.time()
    ints_scanned = 0
    primes_found = 0
    twin_found = 0
    forecasts = 0
    mr_calls = 0

    last_prime = initial_primes[-1]
    last_prime_idx = initial_count
    last_gap = primes_arr[-1] - primes_arr[-2] if len(primes_arr) > 1 else dummy_gap
    recent_gaps = list(gaps[-5:])
    recent_twin_gaps = [2.0] * min(5, twin_count)

    current = last_prime + 1
    if current % 2 == 0:
        current += 1

    theta = compute_theta(window_primes, stream_db.coords)

    guess_prime(last_prime)

    # ----- Streaming loop -----
    while (twin_found if args.twin_mode else primes_found) < new_target:
        ints_scanned += 1
        gap = current - last_prime
        zvec = embed_z(current, dims)
        i, j, k = 0, 2, 4
        zi, zj, zk = zvec[i % dims], zvec[j % dims], zvec[k % dims]
        product = zi * zj * zk
        gm = np.sign(product) * np.abs(product)**(1/3)
        Zp = gm / np.exp(gap) if gap > 0 else 0

        if Zp >= theta:
            mr_calls += 1
            is_prime = miller_rabin(current)
            is_twin = False
            z_next = None
            if is_prime and args.twin_mode:
                mr_calls += 1
                if miller_rabin(current + 2) and current + 2 - current == 2:
                    is_twin = True
                    z_next = embed_z(current + 2, dims)
                    twin_found += 1
                    twin_pairs.append((current, current + 2))
                    twin_embeds.append(np.concatenate((zvec, z_next)))
                    tree = KDTree(twin_embeds) if twin_embeds else None
                    recent_twin_gaps.append(2.0)
                    recent_twin_gaps = recent_twin_gaps[-5:]

            if is_prime and not args.twin_mode:
                primes_found += 1

            if is_prime:
                delta_n = gap
                if delta_n == 0: delta_n = 1e-6
                exp_delta = np.exp(delta_n)
                classical_Z = current / exp_delta if exp_delta != 0 else 1.0
                n_tensor = torch.tensor([[float(current if not args.twin_mode else twin_count)]], dtype=torch.float32)
                delta_tensor = torch.tensor([[float(delta_n if not args.twin_mode else 2.0)]], dtype=torch.float32)
                with torch.no_grad():
                    dev_Z = model(n_tensor, delta_tensor).item()
                Z_corrected = classical_Z * (1 + dev_Z) if not args.twin_mode else classical_Z
                zvec = zvec * (Z_corrected / classical_Z) if classical_Z != 0 else zvec
                stream_db.add_point(current, zvec)
                window_primes.append(current)
                if len(window_primes) > initial_count:
                    window_primes = window_primes[1:]

                last_prime = current
                last_gap = delta_n
                recent_gaps.append(delta_n)
                recent_gaps = recent_gaps[-5:]

                if (primes_found if not args.twin_mode else twin_found) % args.tune_freq == 0:
                    new_classical_Z = current / np.exp(delta_n)
                    new_dev = (new_classical_Z - mean_Z) if not args.twin_mode else (2.0 - np.mean(recent_twin_gaps))
                    X_n = torch.cat([X_n, n_tensor], dim=0)[-initial_count:]
                    X_delta = torch.cat([X_delta, delta_tensor], dim=0)[-initial_count:]
                    Y_dev = torch.cat([Y_dev, torch.tensor([[new_dev]], dtype=torch.float32)], dim=0)[-initial_count:]
                    optimizer.zero_grad()
                    dev_pred = model(X_n, X_delta)
                    loss = loss_fn(dev_pred, Y_dev)
                    loss.backward()
                    optimizer.step()
                    theta = compute_theta(window_primes, stream_db.coords)

                if args.forecast:
                    forecasts += 1
                    next_gap = np.mean(recent_twin_gaps if args.twin_mode else recent_gaps)
                    next_n = current + next_gap
                    next_n_t = torch.tensor([[float(twin_count + 1 if args.twin_mode else next_n)]], dtype=torch.float32)
                    next_gap_t = torch.tensor([[float(next_gap)]], dtype=torch.float32)
                    with torch.no_grad():
                        dev_next = model(next_n_t, next_gap_t).item()
                    exp_next_gap = np.exp(next_gap)
                    classical_next_Z = next_n / exp_next_gap if exp_next_gap != 0 else 1.0
                    Z_next = classical_next_Z if args.twin_mode else classical_next_Z * (1 + dev_next)
                    next_base = embed_z(int(next_n), dims)
                    next_vec = next_base * (Z_next / classical_next_Z) if classical_next_Z != 0 else next_base
                    if args.twin_mode and z_next is not None and tree is not None:
                        query_vec = np.concatenate((next_vec, embed_z(int(next_n + 2), dims)))
                        dist, _ = tree.query(query_vec)
                        if dist < 0.5:
                            current = int(next_n) - 2  # Prioritize region
                    else:
                        _ = stream_db.query_radius(next_vec, radius=4.0)

        current += 2

    # ----- Summary -----
    total_time = time.time() - start_time
    tests_per_s = ints_scanned / total_time if total_time > 0 else float("inf")
    primes_per_s = (twin_found if args.twin_mode else primes_found) / total_time if total_time > 0 else float("inf")

    print("\nStreaming complete.\n")
    print("Summary:")
    print(f"  Total integers scanned: {ints_scanned}")
    print(f"  {'Twins' if args.twin_mode else 'Primes'} requested: {new_target}")
    print(f"  {'Twins' if args.twin_mode else 'Primes'} found: {twin_found if args.twin_mode else primes_found}")
    if args.twin_mode:
        print(f"  Total twin primes (with harness): {twin_count + twin_found}")
        print(f"  Avg twin gap: {np.mean(recent_twin_gaps):.2f}")
        if tree and twin_embeds:
            avg_density = len(twin_embeds) / len(stream_db.coords)
            print(f"  Twin density (KDTree estimate): {avg_density:.4f}")
    if args.forecast:
        print(f"  Forecasts made: {forecasts}")
    print(f"  Miller-Rabin calls: {mr_calls}")
    print(f"  Total runtime: {total_time:.2f} sec")
    print(f"  Tests per second: {tests_per_s:.2f}")
    print(f"  {'Twins' if args.twin_mode else 'Primes'} per second: {primes_per_s:.2f}")
    print(f"  Avg time per test: {total_time/ints_scanned*1e3:.2f} ms")
    if args.forecast and forecasts:
        print(f"  Avg time per forecast: {total_time/forecasts*1e3:.2f} ms")

    if last_prime is not None:
        print(f"\nLast {'Twin Pair' if args.twin_mode else 'Prime'} Details:")
        if args.twin_mode and twin_pairs:
            print(f"  The {twin_count + twin_found}th twin pair is {twin_pairs[-1]}")
            print(f"  Z-embedding (first prime): {stream_db.coords[window_primes.index(twin_pairs[-1][0])].tolist()}")
            mr_calls += 1
            mr_calls += 1
            mr_pass = miller_rabin(twin_pairs[-1][0]) and miller_rabin(twin_pairs[-1][1])
        else:
            print(f"  The {last_prime_idx}th prime found is {last_prime}")
            print(f"  Z-embedding: {stream_db.coords[-1].tolist()}")
            mr_calls += 1
            mr_pass = miller_rabin(last_prime)
        print(f"  Sanity check (Miller-Rabin): {'Passed' if mr_pass else 'Failed'}")

if __name__ == "__main__":
    main()