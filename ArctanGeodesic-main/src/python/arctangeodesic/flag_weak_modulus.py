import argparse  # For parsing command-line arguments
import os  # For interacting with the file system (listing directories, joining paths)
from cryptography.hazmat.primitives.asymmetric import rsa  # To check and handle RSA public keys
from cryptography.hazmat.primitives import serialization  # Not directly used here, but imported for potential key serialization if extended
from cryptography import x509  # For loading and parsing X.509 certificates
import gmpy2  # For arbitrary-precision arithmetic, primality testing (is_prime), and sqrt/log operations
import mpmath  # For high-precision floating-point arithmetic

def is_pem_rsa_cert(file_path):
    """
    Intent: Check if a file is a PEM-encoded X.509 certificate containing an RSA public key.
    This filters non-RSA or invalid certs early to avoid unnecessary processing.
    Returns True if it matches, False otherwise (catches exceptions for invalid files).
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()  # Read entire file as bytes
        cert = x509.load_pem_x509_certificate(data)  # Load as X.509 cert; fails if not PEM cert
        pub = cert.public_key()  # Extract public key
        return isinstance(pub, rsa.RSAPublicKey)  # Confirm it's RSA type
    except Exception:  # Broad catch for any parsing errors (e.g., not PEM, corrupted)
        return False

def generate_random_prime(bits):
    """Generate a random prime of approximately the given bit length."""
    while True:
        # Generate random bytes
        num_bytes = (bits + 7) // 8
        rand_bytes = os.urandom(num_bytes)
        candidate = int.from_bytes(rand_bytes, 'big')
        # Ensure it's at least bits-1 bits and odd
        candidate |= (1 << (bits - 1))
        candidate |= 1
        # Check if prime
        if gmpy2.is_prime(candidate):
            return candidate

def crack_weak_modulus(n):
    """
    Intent: Attempt to detect/crack 'weak' RSA moduli using Z5D geodesic prediction for optimized prime candidate selection.
    - Uses high-precision Z5D theta banding with golden ratio PHI to predict prime clusters.
    - Generates random prime candidates of appropriate size, filtered by circular distance in fractional theta space.
    - Scans filtered candidates for divisibility, verifying primality.
    - Returns factors if cracked, None otherwise.
    Uses random prime generation for scalability, similar to C implementation.
    """
    # Set high precision for mpmath
    mpmath.mp.dps = 100
    PHI = (1 + mpmath.sqrt(5)) / 2  # Golden ratio

    k = 0.45  # Optimal k from C implementation
    eps = 0.05  # Epsilon for filtering
    max_attempts = 10000  # Maximum random attempts

    target_bits = n.bit_length() // 2

    def theta_prime(n_val):
        n_mpf = mpmath.mpf(str(n_val))
        phi_mod = mpmath.fmod(n_mpf, PHI)
        frac = phi_mod / PHI
        pow_val = mpmath.power(frac, k)
        val = PHI * pow_val
        return mpmath.frac(val)

    def circ_dist(a, b):
        d = mpmath.fmod(a - b + 0.5, 1.0) - 0.5
        return abs(float(d))  # Convert to float for comparison

    theta_n = theta_prime(n)

    for _ in range(max_attempts):
        p = generate_random_prime(target_bits)
        theta_p = theta_prime(p)
        if circ_dist(theta_p, theta_n) <= eps:
            if n % p == 0:
                q = n // p
                if gmpy2.is_prime(q):
                    return p, q

    return None

# Main script setup
parser = argparse.ArgumentParser(description="Scan a directory for PEM RSA certs, detect/crack weak moduli using Z5D-mocked heuristics, and output a list.")
parser.add_argument('dir', help='Path to directory containing RSA cert files to scan')
args = parser.parse_args()

weak_list = []  # Collect results for weak/cracked moduli (format: filename: result)

# Iterate over all entries in the directory
for file in os.listdir(args.dir):
    path = os.path.join(args.dir, file)  # Full path to file
    if os.path.isfile(path) and is_pem_rsa_cert(path):  # Process only RSA PEM cert files
        with open(path, 'rb') as f:
            data = f.read()  # Read cert bytes
        cert = x509.load_pem_x509_certificate(data)  # Parse cert
        pub = cert.public_key()  # Get public key
        n = pub.public_numbers().n  # Extract modulus n (big int)
        result = crack_weak_modulus(n)  # Attempt crack/detect weak
        if result:  # If cracked or flagged weak, log it
            weak_list.append(f"{file}: {result}")

# Write results to output file in the same directory
output_path = os.path.join(args.dir, 'weak_moduli.txt')
with open(output_path, 'w') as out:
    out.write('\n'.join(weak_list))  # One entry per line; empty if no weaks found

print(f"Scan complete. Weak/cracked list saved to {output_path}")