with open('z5d_scaling_test.py', 'r') as f:
    content = f.read()

# Replace the generate_semiprime function to generate close factors like RSA
content = content.replace('def generate_semiprime(bits: int) -> Tuple[str, int, int]:', '''def generate_semiprime(bits: int) -> Tuple[str, int, int]:
    """
    Generate a semi-prime with close factors (RSA-like).
    """
    prime_bits = bits // 2
    min_val = 2**(prime_bits - 1)
    max_val = 2**prime_bits - 1
    
    if SYMPY_AVAILABLE:
        p = nextprime(min_val + random.randint(0, min_val // 2))
        d = random.randint(2, min(2**(prime_bits//4), 10000))  # Small difference for close factors
        q = nextprime(p + d)
    else:
        # Fallback
        p = generate_prime(min_val, min_val + min_val // 2)
        d = random.randint(2, min(1000, min_val // 100))
        candidate = p + d
        while not is_prime(candidate):
            candidate += 1
        q = candidate
    
    n = p * q
    return str(n), p, q''')

with open('z5d_scaling_test.py', 'w') as f:
    f.write(content)

print("File edited")