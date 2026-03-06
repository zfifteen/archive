import sympy as sp
import numpy as np
from scipy.stats import pearsonr

def extract_digits(n, base):
    """Extract digits of n in given base (O(log n) passive)."""
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % base)
        n //= base
    return digits[::-1]  # MSB first

def symmetry_block(n, k):
    """Symmetry Block: Trust C(n,k) == C(n, n-k); infer from mirrored digits/parity."""
    if k > n - k:  # Assume symmetry, use min
        k = n - k
    mirrored_k = n - k
    if (k % 2) != (mirrored_k % 2):
        return True  # Trust asymmetry -> leak hint
    digits_k = len(str(k))
    digits_mir = len(str(mirrored_k))
    if digits_k != digits_mir:
        return True  # Mismatch -> disruption
    return False  # Symmetric clean

def recursion_block(n, k):
    """Recursion Block: Trust C(n,k) = C(n-1,k-1) + C(n-1,k); infer chain from edges. FIXED: Adjusted parity check to (k % 2 == 0) and ((n-k) % 2 == 0) for symmetric even priors."""
    if k <= 1 or k >= n - 1:
        return False  # Edge clean
    prior1 = k
    prior2 = n - k
    if (prior1 % 2 == 0) and (prior2 % 2 == 0):
        return False  # Trust propagated zero
    return True  # Trust sum break -> potential leak

def digit_subset_block(n, k, base=10):  # Approx base for digits
    """Digit Subset Block: Trust Lucas - leak if k digits not subset of n's."""
    digits_n = extract_digits(n, base)
    digits_k = extract_digits(k, base)
    max_len = max(len(digits_n), len(digits_k))
    digits_n += [0] * (max_len - len(digits_n))
    digits_k += [0] * (max_len - len(digits_k))
    for i in range(max_len):
        if digits_k[i] > digits_n[i]:
            return True  # Trust subset violation -> leak
    return False  # Subset holds -> clean

def carry_count_block(n, k, base=10):
    """Carry Count Block: Trust Kummer - count carries in k + (n-k) base base."""
    nk = n - k
    digits_k = extract_digits(k, base)
    digits_nk = extract_digits(nk, base)
    max_len = max(len(digits_k), len(digits_nk))
    digits_k += [0] * (max_len - len(digits_k))
    digits_nk += [0] * (max_len - len(digits_nk))
    carry_count = 0
    carry = 0
    for i in range(max_len):
        total = digits_k[i] + digits_nk[i] + carry
        if total >= base:
            carry_count += 1
            carry = 1
        else:
            carry = 0
    return carry_count == 1

def fractal_pattern_block(n, k):
    """Fractal Pattern Block: Trust Sierpinski mod 2 - disruption if not subset bits."""
    if (n & k) != k:
        return True  # Trust non-subset -> leak/disruption
    if bin(k).count('1') % 3 != bin(n).count('1') % 3:  # Rough fractal echo
        return True
    return False  # Subset holds -> clean pattern

def combinatorial_sum_block(n, r=1, i=0, a=1):
    """Combinatorial Sum Block: Trust sum_{k≡i mod r} C(n,k) a^{n-k} gcd non-trivial with n for r ≤ FAC ≤ p. FIXED: Residue check on digits."""
    if r == 1:
        return False  # Trivial mod 1
    digits_n = [int(d) for d in str(n)]
    for d in digits_n:
        if d % r != i % r:
            return True  # Residue mismatch -> leak
    return False  # All match -> clean

def is_clean(n, k, r=2, i=0):
    """Check if all blocks are clean (False)."""
    blocks = [
        symmetry_block(n, k),
        recursion_block(n, k),
        digit_subset_block(n, k),
        carry_count_block(n, k),
        fractal_pattern_block(n, k),
        combinatorial_sum_block(n, r=r, i=i)
    ]
    return all(not b for b in blocks)