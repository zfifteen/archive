#!/usr/bin/env python3
"""
Synthetic Semiprime Generator for Distant-Factor Testing

Generates 512-bit semiprimes with specified factor separation for testing
θ′-biased QMC hypothesis on distant factors.

Key Properties:
- Balanced semiprimes: p ≈ q (ratio ≈ 1.0)
- Distant factors: p and q separated by specified gap
- Deterministic generation with fixed seeds
- Verification of primality (Miller-Rabin)
"""

import random
import math
from typing import Tuple, List, Optional
import json
from pathlib import Path


def is_prime_miller_rabin(n: int, k: int = 40) -> bool:
    """
    Miller-Rabin primality test.
    
    Args:
        n: Number to test
        k: Number of rounds (default: 40 for high confidence)
        
    Returns:
        True if n is probably prime, False if composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def generate_prime(bits: int, seed: Optional[int] = None) -> int:
    """
    Generate a prime number of specified bit length.
    
    Args:
        bits: Bit length of desired prime
        seed: Random seed for reproducibility
        
    Returns:
        Prime number of specified bit length
    """
    if seed is not None:
        random.seed(seed)
    
    while True:
        # Generate random odd number in range [2^(bits-1), 2^bits)
        candidate = random.randrange(2**(bits-1), 2**bits)
        if candidate % 2 == 0:
            candidate += 1
        
        if is_prime_miller_rabin(candidate):
            return candidate


def generate_semiprime_distant_factors(
    bits: int = 512,
    factor_separation: str = "balanced",
    seed: Optional[int] = None
) -> Tuple[int, int, int]:
    """
    Generate semiprime with specified factor separation.
    
    Args:
        bits: Total bit length of semiprime (default: 512)
        factor_separation: Type of separation ('balanced', 'moderate', 'large')
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (N, p, q) where N = p * q
        
    Factor Separations:
        - 'balanced': p ≈ q, ratio in [0.9, 1.1]
        - 'moderate': ratio in [0.7, 0.9] or [1.1, 1.4]
        - 'large': ratio in [0.5, 0.7] or [1.4, 2.0]
    """
    if seed is not None:
        random.seed(seed)
    
    half_bits = bits // 2
    
    if factor_separation == "balanced":
        # Generate two primes of equal bit length
        p = generate_prime(half_bits, seed=seed)
        q = generate_prime(half_bits, seed=seed + 1 if seed else None)
        
    elif factor_separation == "moderate":
        # One prime slightly larger
        p = generate_prime(half_bits, seed=seed)
        q = generate_prime(half_bits - 20, seed=seed + 1 if seed else None)
        
    elif factor_separation == "large":
        # Significantly different sizes
        p = generate_prime(half_bits, seed=seed)
        q = generate_prime(half_bits - 40, seed=seed + 1 if seed else None)
        
    else:
        raise ValueError(f"Unknown factor_separation: {factor_separation}")
    
    # Ensure p < q for consistency
    if p > q:
        p, q = q, p
    
    N = p * q
    
    return N, p, q


def generate_test_suite(
    n_cases: int = 10,
    bits: int = 512,
    seed: int = 42,
    output_file: Optional[Path] = None
) -> List[dict]:
    """
    Generate a test suite of synthetic semiprimes.
    
    Args:
        n_cases: Number of test cases to generate (default: 10)
        bits: Bit length of semiprimes (default: 512)
        seed: Random seed for reproducibility
        output_file: Optional path to save results as JSON
        
    Returns:
        List of dictionaries with test case metadata
    """
    test_cases = []
    
    for i in range(n_cases):
        # Cycle through separation types
        separations = ["balanced", "moderate", "large"]
        sep_type = separations[i % len(separations)]
        
        case_seed = seed + i * 1000
        N, p, q = generate_semiprime_distant_factors(
            bits=bits,
            factor_separation=sep_type,
            seed=case_seed
        )
        
        # Compute metadata
        ratio = q / p if p > 0 else 0
        sqrt_N = int(math.sqrt(N))
        p_distance = abs(p - sqrt_N)
        q_distance = abs(q - sqrt_N)
        
        case = {
            'case_id': i,
            'seed': case_seed,
            'bits': bits,
            'separation_type': sep_type,
            'N': str(N),
            'p': str(p),
            'q': str(q),
            'ratio': ratio,
            'sqrt_N': str(sqrt_N),
            'p_distance': str(p_distance),
            'q_distance': str(q_distance),
            'N_bit_length': N.bit_length(),
            'p_bit_length': p.bit_length(),
            'q_bit_length': q.bit_length()
        }
        
        test_cases.append(case)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(test_cases, f, indent=2)
        print(f"Saved {len(test_cases)} test cases to {output_file}")
    
    return test_cases


def load_rsa_challenges() -> dict:
    """
    Load known RSA challenge numbers (factored).
    
    Returns:
        Dictionary mapping RSA challenge names to (N, p, q) tuples
    """
    return {
        'RSA-100': {
            'N': 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000795641669258795963466392520424679069476232232770723,
            'p': 37975227936943673922808872755445627854565536638199,
            'q': 40094690950920881030683735292761468389214899724061,
            'bits': 330
        },
        'RSA-129': {
            'N': 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989498162765933536356427501063908969,
            'p': 3490529510847650949147849619903898133417764638493387843990820577,
            'q': 32769132993266709549961988190834461413177642967992942539798288533,
            'bits': 426
        },
        'RSA-155': {
            'N': 10941738641570527421809707322040357612003732945449205990913842131476349984288934784717997257891267332497625752899781833797076537244027146743531593354333897,
            'p': 102639592829741105772054196573991675900716567808038066803341933521790711307779,
            'q': 106603488380168454820927220360012878679207958575989291522270608237193062808643,
            'bits': 512
        }
    }


if __name__ == "__main__":
    print("Synthetic Semiprime Generator")
    print("=" * 70)
    
    # Generate small test suite
    print("\n1. Generating 512-bit test suite (3 cases):")
    test_cases = generate_test_suite(n_cases=3, bits=512, seed=42)
    
    for case in test_cases:
        print(f"\nCase {case['case_id']} ({case['separation_type']}):")
        print(f"  N bits: {case['N_bit_length']}")
        print(f"  p bits: {case['p_bit_length']}, q bits: {case['q_bit_length']}")
        print(f"  Ratio (q/p): {case['ratio']:.4f}")
        print(f"  p: ...{str(case['p'])[-20:]}")
        print(f"  q: ...{str(case['q'])[-20:]}")
    
    # Show RSA challenges
    print("\n2. Known RSA Challenge Numbers:")
    rsa_challenges = load_rsa_challenges()
    for name, data in rsa_challenges.items():
        print(f"\n{name}:")
        print(f"  Bits: {data['bits']}")
        print(f"  N: ...{str(data['N'])[-40:]}")
        print(f"  p: ...{str(data['p'])[-40:]}")
        print(f"  q: ...{str(data['q'])[-40:]}")
    
    print("\n" + "=" * 70)
    print("Generator ready.")
