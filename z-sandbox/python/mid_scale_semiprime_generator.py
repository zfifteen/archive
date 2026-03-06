#!/usr/bin/env python3
"""
Mid-Scale Semiprime Generator for 512-768 Bit Validation

Generates cryptographically secure balanced semiprimes for validation of
z-sandbox's hybrid geometric-wave factorization methods.

Acceptance Criteria:
- Generate at least 10 random balanced semiprimes (512-768 bits)
- Use cryptographically secure randomness (secrets module)
- Ensure p and q are of roughly equal bit-length
- Exclude special forms (safe primes, Mersenne primes, etc.)
- No previously factored or historical challenges

Mathematical Foundation:
- Balanced semiprimes: |log₂(p) - log₂(q)| < 2 bits
- Uniform random sampling from prime space
- Miller-Rabin primality testing via sympy
"""

import argparse
import json
import secrets
import time
from pathlib import Path
from typing import Dict, List, Tuple
import sympy


def generate_random_prime(bits: int, max_attempts: int = 1000) -> int:
    """
    Generate a cryptographically secure random prime of specified bit length.
    
    Args:
        bits: Target bit length for the prime
        max_attempts: Maximum number of attempts to find a prime
        
    Returns:
        A random prime number of the specified bit length
        
    Raises:
        RuntimeError: If unable to find a prime within max_attempts
    """
    for attempt in range(max_attempts):
        # Generate random odd number with exact bit length
        # Set MSB and LSB to ensure exact bit length and oddness
        candidate = secrets.randbits(bits - 2)
        candidate = (1 << (bits - 1)) | (candidate << 1) | 1
        
        # Use sympy's isprime (Miller-Rabin + deterministic tests)
        if sympy.isprime(candidate):
            return candidate
    
    raise RuntimeError(f"Failed to find {bits}-bit prime after {max_attempts} attempts")


def is_special_form(p: int) -> bool:
    """
    Check if a prime has a special form that should be excluded.
    
    Special forms to exclude:
    - Safe primes: p where (p-1)/2 is also prime
    - Mersenne primes: p = 2^n - 1
    - Fermat primes: p = 2^(2^n) + 1
    - Sophie Germain primes: p where 2p+1 is also prime
    
    Args:
        p: Prime number to check
        
    Returns:
        True if p has a special form, False otherwise
    """
    # Check Mersenne form: 2^n - 1
    # If p+1 is a power of 2, it's Mersenne
    if (p + 1) & p == 0 and p > 1:
        return True
    
    # Check Fermat form: 2^(2^n) + 1
    # If p-1 is a power of 2, check if log₂(p-1) is also a power of 2
    pm1 = p - 1
    if pm1 & (pm1 - 1) == 0:  # p-1 is power of 2
        exp = (pm1).bit_length() - 1
        if exp & (exp - 1) == 0:  # exponent is power of 2
            return True
    
    # Check safe prime: (p-1)/2 is prime
    if p > 3 and p % 2 == 1:
        candidate = (p - 1) // 2
        if sympy.isprime(candidate):
            return True
    
    # Check Sophie Germain: 2p+1 is prime
    if sympy.isprime(2 * p + 1):
        return True
    
    return False


def generate_balanced_semiprime(
    target_bits: int,
    balance_tolerance: int = 2,
    max_attempts: int = 100
) -> Tuple[int, int, int, Dict]:
    """
    Generate a balanced semiprime N = p × q with cryptographically secure randomness.
    
    Args:
        target_bits: Target bit length for N (512-768)
        balance_tolerance: Maximum bit difference between p and q
        max_attempts: Maximum attempts to find suitable pair
        
    Returns:
        Tuple of (N, p, q, metadata) where:
        - N: The semiprime
        - p, q: The factors (p ≤ q)
        - metadata: Dictionary with generation details
        
    Raises:
        RuntimeError: If unable to generate suitable semiprime
    """
    # Target bit lengths for factors (approximately equal)
    p_bits = target_bits // 2
    q_bits = target_bits - p_bits
    
    start_time = time.time()
    
    for attempt in range(max_attempts):
        # Generate two random primes
        p = generate_random_prime(p_bits)
        q = generate_random_prime(q_bits)
        
        # Check for special forms (exclude them)
        if is_special_form(p) or is_special_form(q):
            continue
        
        # Compute semiprime
        N = p * q
        
        # Verify exact bit length
        if N.bit_length() != target_bits:
            continue
        
        # Verify balance
        p_actual_bits = p.bit_length()
        q_actual_bits = q.bit_length()
        bit_diff = abs(p_actual_bits - q_actual_bits)
        
        if bit_diff <= balance_tolerance:
            # Ensure p ≤ q for consistency
            if p > q:
                p, q = q, p
            
            elapsed = time.time() - start_time
            
            metadata = {
                "target_bits": target_bits,
                "N_bits": N.bit_length(),
                "p_bits": p.bit_length(),
                "q_bits": q.bit_length(),
                "balance_diff": bit_diff,
                "generation_time_sec": elapsed,
                "attempt": attempt + 1,
                "is_special_form": {
                    "p": is_special_form(p),
                    "q": is_special_form(q)
                }
            }
            
            return N, p, q, metadata
    
    raise RuntimeError(
        f"Failed to generate balanced {target_bits}-bit semiprime "
        f"after {max_attempts} attempts"
    )


def generate_mid_scale_suite(
    num_targets: int = 10,
    bit_range: Tuple[int, int] = (512, 768),
    output_file: str = "mid_scale_targets.json"
) -> List[Dict]:
    """
    Generate a suite of mid-scale balanced semiprimes for validation.
    
    Args:
        num_targets: Number of targets to generate (default: 10)
        bit_range: Tuple of (min_bits, max_bits) for target range
        output_file: Path to save generated targets
        
    Returns:
        List of target dictionaries with N, p, q, and metadata
    """
    min_bits, max_bits = bit_range
    targets = []
    
    print(f"Generating {num_targets} mid-scale targets ({min_bits}-{max_bits} bits)")
    print("=" * 80)
    
    # Distribute targets across bit range
    bit_step = (max_bits - min_bits) // max(1, num_targets - 1) if num_targets > 1 else 0
    
    for i in range(num_targets):
        # Determine target bits for this semiprime
        if num_targets == 1:
            target_bits = min_bits
        else:
            target_bits = min_bits + i * bit_step
            # Ensure we don't exceed max_bits
            target_bits = min(target_bits, max_bits)
        
        print(f"\nTarget {i+1}/{num_targets}: {target_bits} bits")
        print("-" * 80)
        
        try:
            N, p, q, metadata = generate_balanced_semiprime(target_bits)
            
            target = {
                "id": f"MID-{target_bits}b-{i+1:02d}",
                "N": str(N),
                "p": str(p),
                "q": str(q),
                "metadata": metadata
            }
            
            targets.append(target)
            
            print(f"✓ Generated {target['id']}")
            print(f"  N: {N.bit_length()} bits")
            print(f"  p: {p.bit_length()} bits")
            print(f"  q: {q.bit_length()} bits")
            print(f"  Balance: ±{metadata['balance_diff']} bits")
            print(f"  Time: {metadata['generation_time_sec']:.2f}s")
            
        except Exception as e:
            print(f"✗ Failed to generate target {i+1}: {e}")
            continue
    
    # Save to file
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump({
                "suite_name": "Mid-Scale Validation Suite",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "bit_range": list(bit_range),
                "num_targets": len(targets),
                "targets": targets
            }, f, indent=2)
        
        print(f"\n{'=' * 80}")
        print(f"✓ Saved {len(targets)} targets to {output_path}")
    
    return targets


def validate_target(target: Dict) -> bool:
    """
    Validate a generated target meets all requirements.
    
    Args:
        target: Target dictionary with N, p, q
        
    Returns:
        True if valid, False otherwise
    """
    try:
        N = int(target['N'])
        p = int(target['p'])
        q = int(target['q'])
        
        # Check factorization
        if p * q != N:
            print(f"✗ {target['id']}: p*q != N")
            return False
        
        # Check primality
        if not sympy.isprime(p):
            print(f"✗ {target['id']}: p is not prime")
            return False
        
        if not sympy.isprime(q):
            print(f"✗ {target['id']}: q is not prime")
            return False
        
        # Check no special forms
        if is_special_form(p):
            print(f"✗ {target['id']}: p has special form")
            return False
        
        if is_special_form(q):
            print(f"✗ {target['id']}: q has special form")
            return False
        
        # Check balance
        bit_diff = abs(p.bit_length() - q.bit_length())
        if bit_diff > 2:
            print(f"✗ {target['id']}: factors not balanced (diff={bit_diff})")
            return False
        
        print(f"✓ {target['id']}: Valid")
        return True
        
    except Exception as e:
        print(f"✗ {target['id']}: Validation error: {e}")
        return False


def main():
    """CLI entry point for mid-scale semiprime generation."""
    parser = argparse.ArgumentParser(
        description="Generate mid-scale balanced semiprimes for z-sandbox validation"
    )
    parser.add_argument(
        "--num-targets", "-n",
        type=int,
        default=10,
        help="Number of targets to generate (default: 10)"
    )
    parser.add_argument(
        "--min-bits",
        type=int,
        default=512,
        help="Minimum bit length (default: 512)"
    )
    parser.add_argument(
        "--max-bits",
        type=int,
        default=768,
        help="Maximum bit length (default: 768)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="mid_scale_targets.json",
        help="Output file path (default: mid_scale_targets.json)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing target file"
    )
    
    args = parser.parse_args()
    
    if args.validate:
        # Validate existing file
        with open(args.output, 'r') as f:
            data = json.load(f)
        
        print(f"Validating {len(data['targets'])} targets from {args.output}")
        print("=" * 80)
        
        valid_count = 0
        for target in data['targets']:
            if validate_target(target):
                valid_count += 1
        
        print("\n" + "=" * 80)
        print(f"Validation: {valid_count}/{len(data['targets'])} targets valid")
        
    else:
        # Generate new targets
        targets = generate_mid_scale_suite(
            num_targets=args.num_targets,
            bit_range=(args.min_bits, args.max_bits),
            output_file=args.output
        )
        
        print(f"\n{'=' * 80}")
        print(f"Summary: Generated {len(targets)}/{args.num_targets} targets")


if __name__ == "__main__":
    main()
