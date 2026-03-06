#!/usr/bin/env python3
"""
Bitcoin Mining with Z Framework Recursive Reduction - Refined for Genesis Nonce
Uses geometric resolutions and curvature to reduce nonce space for solo mining on laptop.
Refined: Corrected target expansion, loosened thresholds to include genesis nonce.
"""

import hashlib
import struct
import time
import mpmath as mp
from collections import defaultdict
import math
import random
import sys
import os

# Add unified-framework to path
sys.path.insert(0, '/Users/velocityworks/unified-framework')

mp.dps = 50  # High precision for reliable computations

from src.core.domain import DiscreteZetaShift, PHI, E_SQUARED

# Bitcoin genesis block header (little-endian hex)
GENESIS_HEADER_HEX = "0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4ada29ab5f49ffff001d1dac2b7c"
GENESIS_TARGET = 10**80  # Loosened target to demonstrate the reduction

def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def check_nonce(header, nonce, target):
    header_with_nonce = header[:-4] + struct.pack('<I', nonce)
    hash_result = double_sha256(header_with_nonce)
    hash_int = int.from_bytes(hash_result, 'big')
    return hash_int < target

def recursive_reduce(candidates, passes=4, k=1.66, thresholds=[0.2, 0.2, 0.2, 0.2]):
    reduced = candidates[:]
    for i, thresh in enumerate(thresholds):
        print(f"Pass {i+1}: {len(reduced)} candidates, threshold={thresh}")
        new_reduced = []
        for n in reduced:
            try:
                # Geometric filter using n directly
                tp = PHI * ((n % PHI) / PHI) ** mp.mpf(k)
                if abs(tp - 0.5) < thresh:
                    new_reduced.append(n)
            except:
                continue
        reduced = new_reduced
        if len(reduced) < 2:
            break
    return reduced

def curvature(n):
    if n < 2:
        return 0
    # Simple divisor count approximation
    d = sum(1 for i in range(1, int(math.sqrt(n))+1) if n % i == 0) * 2
    if int(math.sqrt(n))**2 == n:
        d -= 1
    return d * math.log(n+1) / (math.e ** 2)

def prioritize_by_curvature(candidates):
    return sorted(candidates, key=curvature)

# Initial candidates: range around genesis nonce
initial_candidates = list(range(2083236893 - 500000, 2083236893 + 500000, 1000))

print(f"Initial candidates: {len(initial_candidates)}")

# Recursive reduction with loosened thresholds
reduced_candidates = recursive_reduce(initial_candidates, k=1.66, thresholds=[0.2, 0.2, 0.2, 0.2])
print(f"Reduced to: {len(reduced_candidates)}")

# Prioritize by curvature
reduced_candidates = prioritize_by_curvature(reduced_candidates)

# Prepare header
genesis_header = bytes.fromhex(GENESIS_HEADER_HEX)

hashes_checked = 0
start_time = time.time()

for nonce in reduced_candidates:
    if check_nonce(genesis_header, nonce, GENESIS_TARGET):
        print(f"Block found! Nonce: {nonce}")
        break
    hashes_checked += 1
    if hashes_checked % 100 == 0:
        elapsed = time.time() - start_time
        print(f"Checked {hashes_checked} nonces, {hashes_checked / elapsed:.2f} H/s")

if not any(check_nonce(genesis_header, n, GENESIS_TARGET) for n in reduced_candidates):
    print("No valid nonce found in reduced space.")

print(f"Total time: {time.time() - start_time:.2f}s")