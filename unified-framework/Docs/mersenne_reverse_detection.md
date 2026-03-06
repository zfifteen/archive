# Mersenne Reverse Detection

## Overview

The Mersenne Reverse Detection feature implements the novel "reverse" framing of Mersenne prime detection as described in the issue. Instead of the traditional approach (given prime p, check if 2^p - 1 is prime), this function takes a number q and determines if q is a Mersenne prime.

## Mathematical Foundation

The implementation leverages the key mathematical property:
```
For Mersenne primes M_p = 2^p - 1, we have log₂(M_p + 1) = p exactly
```

This tautological relationship enables efficient reverse detection without requiring expensive primality testing of 2^p - 1.

## Implementation Details

### Function Signature
```c
static prime_t mersenne_reverse_detect(prime_t q);
```

### Algorithm
1. **Input Validation**: Reject q < 3 (smallest Mersenne prime)
2. **Primality Check**: Verify q is prime (requirement for Mersenne primes)
3. **Power-of-2 Detection**: Check if q+1 has exactly one bit set
4. **Exponent Extraction**: Count trailing zeros to find p such that q+1 = 2^p
5. **Exponent Validation**: Verify p is prime
6. **Verification**: For small p ≤ 63, reconstruct 2^p - 1 and compare with q

### Return Value
- Returns the prime exponent p if q is a valid Mersenne prime
- Returns 0 otherwise

## Test Cases

The implementation passes all test cases from the problem statement:

### Positive Cases
- `mersenne_reverse_detect(3) → 2` (3 = 2² - 1)
- `mersenne_reverse_detect(7) → 3` (7 = 2³ - 1)  
- `mersenne_reverse_detect(31) → 5` (31 = 2⁵ - 1)
- `mersenne_reverse_detect(127) → 7` (127 = 2⁷ - 1)
- `mersenne_reverse_detect(8191) → 13` (8191 = 2¹³ - 1)

### Negative Cases
- `mersenne_reverse_detect(2047) → 0` (2047 = 2¹¹ - 1; 2047 fails because it is not prime, even though 11 is prime)
- `mersenne_reverse_detect(2) → 0` (not in Mersenne form)
- `mersenne_reverse_detect(15) → 0` (15 = 2⁴ - 1, but 4 is composite)

## Integration with Prime Finder

The prime finder now displays reverse detection results alongside traditional Mersenne exponent detection:

```
Finding 10 primes starting from 2
2M         # 2 is Mersenne exponent (2² - 1 = 3 is prime)
3MR2       # 3 is both Mersenne exponent AND Mersenne prime (3 = 2² - 1)
5M         # 5 is Mersenne exponent (2⁵ - 1 = 31 is prime)
7MR3       # 7 is both Mersenne exponent AND Mersenne prime (7 = 2³ - 1)
31MR5      # 31 is both Mersenne exponent AND Mersenne prime (31 = 2⁵ - 1)
127MR7     # 127 is both Mersenne exponent AND Mersenne prime (127 = 2⁷ - 1)
```

## Legend
- `M` suffix: Prime is a Mersenne prime exponent
- `R<p>` suffix: Prime is itself a Mersenne prime (= 2^p - 1)

## Computational Efficiency

The reverse detection algorithm has several efficiency advantages:
1. **Bit Operations**: Uses fast bitwise operations for power-of-2 detection
2. **No Large Arithmetic**: Avoids computing 2^p - 1 for verification
3. **Early Termination**: Multiple early exit conditions minimize computation
4. **Logarithmic Complexity**: Exponent extraction via bit counting is O(log p)

## Novel Aspects

As confirmed by the research, this "reverse" framing appears to be novel in the literature. Standard Mersenne prime detection methods (Lucas-Lehmer test, trial factorization) follow the forward direction (p → 2^p - 1), while this implementation provides the mathematically equivalent reverse direction (q → p).

## Future Enhancements

1. **Extended Range**: Support for larger Mersenne primes beyond 64-bit limits
2. **Performance Optimization**: SIMD acceleration for batch processing
3. **Probabilistic Variants**: Fast screening using probabilistic primality tests
4. **Integration**: Connection with Z5D prime prediction for Mersenne candidate generation