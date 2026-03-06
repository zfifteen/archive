#!/usr/bin/env python3
"""
Proof-of-Concept: Universal Frame-Shift Geodesic Semiprime Factorization

This script implements the “frame-shift transformer” approach:
 1. Embeds n and √n into a holographic Z-space.
 2. Uses a lightweight neural predictor (stub) to estimate Δₚ.
 3. Attempts direct prime factor guess via predictor and Miller-Rabin test.
 4. If guess fails, performs a Fermat‐inspired geodesic search from x ≈ √n + Δₚ.
 5. Returns factors (p, q) when x² − n is a perfect square.
"""

import sys
import math
import random
import torch
import torch.nn as nn

class ZPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        # Simple 2→32→1 MLP stub
        self.fc1 = nn.Linear(2, 32)
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x_n, x_delta):
        x = torch.cat([x_n, x_delta], dim=-1)
        h = torch.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(h))

def miller_rabin(n, k=40):
    # Miller-Rabin primality test (probabilistic)
    # k=40 rounds for high confidence in cryptographic ranges
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
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

def guess_prime_factor(n, model, device):
    # Attempt to guess a prime factor p ≈ √n - Δ_p using predictor
    # Test primality with Miller-Rabin and divisibility
    root_n = math.sqrt(n)  # Use float sqrt for precision
    if n < 10**6:
        dev_delta = 0.0
    else:
        x_n = torch.tensor([[root_n / math.e**2]], dtype=torch.float32, device=device)
        x_delta = torch.tensor([[math.log(n) / 2]], dtype=torch.float32, device=device)
        model.eval()
        with torch.no_grad():
            pred = model(x_n, x_delta).item()
        dev_delta = pred * (n**0.25) / 10.0

    candidate_p = int(round(root_n - dev_delta))
    if candidate_p < 2:
        return None, None

    # Optional parity adjustment (align to odd if even >2)
    if candidate_p % 2 == 0 and candidate_p > 2:
        candidate_p -= 1  # Shift to nearest odd

    if miller_rabin(candidate_p) and n % candidate_p == 0:
        q = n // candidate_p
        return min(candidate_p, q), max(candidate_p, q)  # Return sorted p <= q
    return None, None

def is_perfect_square(x: int) -> bool:
    if x < 0:
        return False
    r = math.isqrt(x)
    return r * r == x

def factor_semiprime(n: int,
                     model: nn.Module,
                     device: str = 'cpu',
                     max_iters: int = 1000000):
    # 1. First, attempt direct guess of prime factor
    p, q = guess_prime_factor(n, model, device)
    if p:
        return p, q

    # 2. If guess fails, fall back to frame initialization and geodesic search
    root_n = math.ceil(math.sqrt(n))

    # 3. Predict deviation Δₚ via ZPredictor (stub)
    if n < 10**6:
        dev_delta = 0.0
    else:
        x_n     = torch.tensor([[root_n / math.e**2]],
                                dtype=torch.float32,
                                device=device)
        x_delta = torch.tensor([[math.log(n) / 2]],
                                dtype=torch.float32,
                                device=device)

        model.eval()
        with torch.no_grad():
            pred = model(x_n, x_delta).item()
        dev_delta = pred * (n**0.25) / 10.0

    # 4. Initialize search variable x ≡ ceil(√n) + Δₚ, aligned in parity
    current = int(round(root_n + dev_delta))
    if (current - root_n) % 2 != 0:
        current += 1  # preserve even/odd parity for Fermat

    # 5. Geodesic streaming loop (step = 2 preserves parity)
    for _ in range(max_iters):
        diff = current * current - n
        if is_perfect_square(diff):
            b = math.isqrt(diff)
            p, q = current - b, current + b
            if p * q == n:
                return p, q
        current += 2

    # If no factor found within max_iters
    return None, None

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <semiprime_n>")
        sys.exit(1)

    n = int(sys.argv[1])
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Instantiate the (untrained) ZPredictor stub
    model = ZPredictor().to(device)
    # To plug in a real trained predictor, uncomment:
    # model.load_state_dict(torch.load('zpredictor.pt', map_location=device))

    p, q = factor_semiprime(n, model, device)
    if p:
        print(f"✔ Factors of {n}: {p} × {q}")
    else:
        print(f"✘ Failed to factor {n} within iteration budget.")

if __name__ == "__main__":
    main()
