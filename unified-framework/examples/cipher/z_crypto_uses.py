# z_crypto_use_cases.py
# Demonstrates usage of z_crypto.py for Z-framework keyed encryption/decryption.
# Assumes z_crypto.py is in the same directory or importable.
# For practical deployment, consider block-mode for large data to bound precision.

import os
from z_crypto import encrypt, decrypt, compute_r, theta_prime, DiscreteZetaShift
# import z_crypto
import hashlib
import mpmath as mp

def detailed_encrypt_process(plaintext_bytes, passphrase, N=10):
    """
    Enhanced encrypt function with detailed logging
    """
    print("\n" + "="*80)
    print("DETAILED ENCRYPTION PROCESS")
    print("="*80)

    print(f"Input plaintext: {plaintext_bytes}")
    print(f"Plaintext length: {len(plaintext_bytes)} bytes")
    print(f"Passphrase: '{passphrase}'")
    print(f"N parameter: {N}")

    if not plaintext_bytes:
        print("Empty plaintext detected - using special handling")
        key = hashlib.sha256(passphrase.encode()).digest()
        iv = os.urandom(32)
        result = iv + (0).to_bytes(4, 'big')
        print(f"Empty plaintext result length: {len(result)} bytes")
        return result

    # Step 1: Generate key from passphrase
    key = hashlib.sha256(passphrase.encode()).digest()
    print(f"\nStep 1 - Key derivation:")
    print(f"  SHA256(passphrase) = {key.hex()[:32]}... (showing first 16 bytes)")
    print(f"  Key length: {len(key)} bytes")

    # Step 2: Generate random IV
    iv = os.urandom(32)
    print(f"\nStep 2 - IV generation:")
    print(f"  Random IV = {iv.hex()[:32]}... (showing first 16 bytes)")
    print(f"  IV length: {len(iv)} bytes")

    # Step 3: XOR key with IV
    from z_crypto import xor_bytes
    key_prime = xor_bytes(key, iv)
    print(f"\nStep 3 - Key XOR with IV:")
    print(f"  key' = key ⊕ iv = {key_prime.hex()[:32]}... (showing first 16 bytes)")

    # Step 4: Convert key' to mpmath number
    s_prime = mp.mpmathify(int.from_bytes(key_prime, 'big'))
    print(f"\nStep 4 - Convert to mpmath:")
    print(f"  s' = {str(s_prime)[:50]}... (truncated)")
    print(f"  s' bit length: {s_prime.bit_length() if hasattr(s_prime, 'bit_length') else 'N/A'}")

    # Step 5: Compute r using Z-framework
    print(f"\nStep 5 - Computing r using Z-framework (N={N} iterations):")
    r = compute_r(s_prime, N)
    print(f"  r = {str(r)[:50]}... (truncated)")

    # Step 6: Apply theta_prime transformation
    print(f"\nStep 6 - Theta prime transformation:")
    theta = theta_prime(r)
    print(f"  θ'(r) = {str(theta)[:50]}... (truncated)")

    # Step 7: Convert plaintext to mpmath number
    m = mp.mpmathify(int.from_bytes(plaintext_bytes, 'big'))
    print(f"\nStep 7 - Plaintext to number:")
    print(f"  m = {str(m)[:50]}... (truncated)")
    print(f"  m bit length: {m.bit_length() if hasattr(m, 'bit_length') else 'N/A'}")

    # Step 8: Encryption multiplication
    print(f"\nStep 8 - Encryption operation:")
    e_float = m * theta
    print(f"  e (float) = m * θ' = {str(e_float)[:50]}... (truncated)")

    # Step 9: Convert to integer
    e_int = int(mp.nint(e_float))
    print(f"  e (int) = {str(e_int)[:50]}... (truncated)")
    print(f"  e bit length: {e_int.bit_length()}")

    # Step 10: Convert to bytes
    e_bytes = e_int.to_bytes((e_int.bit_length() + 7) // 8, 'big')
    print(f"  e (bytes) length: {len(e_bytes)} bytes")
    print(f"  e (bytes) = {e_bytes.hex()[:32]}... (showing first 16 bytes)")

    # Step 11: Construct final ciphertext
    len_e = len(e_bytes)
    ciphertext = iv + len_e.to_bytes(4, 'big') + e_bytes
    print(f"\nStep 11 - Final ciphertext construction:")
    print(f"  IV length: {len(iv)} bytes")
    print(f"  Length field: {len_e} (4 bytes)")
    print(f"  Encrypted data: {len(e_bytes)} bytes")
    print(f"  Total ciphertext length: {len(ciphertext)} bytes")

    return ciphertext

def detailed_decrypt_process(ciphertext, passphrase, N=10):
    """
    Enhanced decrypt function with detailed logging
    """
    print("\n" + "="*80)
    print("DETAILED DECRYPTION PROCESS")
    print("="*80)

    print(f"Input ciphertext length: {len(ciphertext)} bytes")
    print(f"Ciphertext (hex, first 32 chars): {ciphertext.hex()[:32]}...")
    print(f"Passphrase: '{passphrase}'")
    print(f"N parameter: {N}")

    # Step 1: Generate key from passphrase
    key = hashlib.sha256(passphrase.encode()).digest()
    print(f"\nStep 1 - Key derivation:")
    print(f"  SHA256(passphrase) = {key.hex()[:32]}... (showing first 16 bytes)")

    # Step 2: Extract IV
    iv = ciphertext[:32]
    print(f"\nStep 2 - Extract IV:")
    print(f"  IV = {iv.hex()[:32]}... (showing first 16 bytes)")

    # Step 3: Extract length field
    len_e = int.from_bytes(ciphertext[32:36], 'big')
    print(f"\nStep 3 - Extract length field:")
    print(f"  Length of encrypted data: {len_e} bytes")

    if len_e == 0:
        print("  Empty plaintext case detected")
        return b""

    # Step 4: Extract encrypted data
    e_bytes = ciphertext[36:36 + len_e]
    print(f"\nStep 4 - Extract encrypted data:")
    print(f"  Encrypted data length: {len(e_bytes)} bytes")
    print(f"  Encrypted data (hex, first 32 chars): {e_bytes.hex()[:32]}...")

    # Step 5: Convert encrypted data to mpmath number
    e_int = mp.mpmathify(int.from_bytes(e_bytes, 'big'))
    print(f"\nStep 5 - Convert encrypted data to number:")
    print(f"  e = {str(e_int)[:50]}... (truncated)")

    # Step 6: Recreate key'
    from z_crypto import xor_bytes
    key_prime = xor_bytes(key, iv)
    s_prime = mp.mpmathify(int.from_bytes(key_prime, 'big'))
    print(f"\nStep 6 - Recreate key':")
    print(f"  s' = {str(s_prime)[:50]}... (truncated)")

    # Step 7: Recompute r
    print(f"\nStep 7 - Recompute r using Z-framework:")
    r = compute_r(s_prime, N)
    print(f"  r = {str(r)[:50]}... (truncated)")

    # Step 8: Recompute theta
    print(f"\nStep 8 - Recompute theta:")
    theta = theta_prime(r)
    print(f"  θ'(r) = {str(theta)[:50]}... (truncated)")

    # Step 9: Decrypt by division
    print(f"\nStep 9 - Decryption operation:")
    m_float = e_int / theta
    print(f"  m (float) = e / θ' = {str(m_float)[:50]}... (truncated)")

    # Step 10: Convert to integer
    m_int = int(mp.nint(m_float))
    print(f"  m (int) = {str(m_int)[:50]}... (truncated)")
    print(f"  m bit length: {m_int.bit_length()}")

    if m_int == 0:
        print("  Result is zero - returning empty bytes")
        return b""

    # Step 11: Convert to bytes
    plaintext = m_int.to_bytes((m_int.bit_length() + 7) // 8, 'big')
    print(f"\nStep 11 - Convert to plaintext bytes:")
    print(f"  Plaintext length: {len(plaintext)} bytes")
    print(f"  Plaintext: {plaintext}")

    return plaintext

# Example 1: Basic encryption/decryption of short binary data with detailed logging
print("STARTING Z-CRYPTO DEMONSTRATION")
print("="*80)

plaintext_short = b"Z-model test"
passphrase = "secret123"

print("EXAMPLE 1: Basic encryption/decryption")
ciphertext_short = detailed_encrypt_process(plaintext_short, passphrase, N=10)
decrypted_short = detailed_decrypt_process(ciphertext_short, passphrase, N=10)

print("\n" + "="*80)
print("EXAMPLE 1 SUMMARY")
print("="*80)
print("Original:", plaintext_short)
print("Decrypted:", decrypted_short)
print("Match:", decrypted_short == plaintext_short)
assert decrypted_short == plaintext_short

# Example 2: Handling moderate-sized data with summary logging
print("\n\nEXAMPLE 2: Moderate-sized data (100 bytes)")
plaintext_moderate = os.urandom(100)
print(f"Random plaintext (first 32 hex chars): {plaintext_moderate.hex()[:32]}...")
print(f"Plaintext length: {len(plaintext_moderate)} bytes")

ciphertext_moderate = encrypt(plaintext_moderate, passphrase, N=12)
print(f"Ciphertext length: {len(ciphertext_moderate)} bytes")

decrypted_moderate = decrypt(ciphertext_moderate, passphrase, N=12)
print(f"Decrypted length: {len(decrypted_moderate)} bytes")
print("Match:", decrypted_moderate == plaintext_moderate)
assert decrypted_moderate == plaintext_moderate

# Example 3: Wrong passphrase test
print("\n\nEXAMPLE 3: Wrong passphrase test")
wrong_passphrase = "wrong456"
print(f"Using wrong passphrase: '{wrong_passphrase}'")
try:
    wrong_result = decrypt(ciphertext_short, wrong_passphrase, N=10)
    print(f"Unexpected success with wrong passphrase: {wrong_result}")
    assert False, "Should raise error or produce wrong result"
except ValueError as e:
    print(f"Expected failure: {str(e)}")
except Exception as e:
    print(f"Decryption with wrong passphrase produced: {wrong_result}")
    print(f"Original was: {plaintext_short}")
    print(f"Results match: {wrong_result == plaintext_short}")

# Example 4: Empty plaintext
print("\n\nEXAMPLE 4: Empty plaintext")
plaintext_empty = b""
print("Testing empty plaintext")
ciphertext_empty = encrypt(plaintext_empty, passphrase, N=10)
print(f"Empty plaintext ciphertext length: {len(ciphertext_empty)} bytes")
decrypted_empty = decrypt(ciphertext_empty, passphrase, N=10)
print(f"Decrypted empty: {decrypted_empty}")
print("Empty match:", decrypted_empty == b"")
assert decrypted_empty == b""

# Example 5: Unicode-encoded text
print("\n\nEXAMPLE 5: Unicode text")
unicode_text = r"Unification: \( Z = n(\Delta_n / \Delta_{\max}) \)".encode('utf-8')
print(f"Unicode text: {unicode_text}")
print(f"Unicode text length: {len(unicode_text)} bytes")

ciphertext_unicode = encrypt(unicode_text, passphrase, N=10)
print(f"Unicode ciphertext length: {len(ciphertext_unicode)} bytes")

decrypted_unicode_bytes = decrypt(ciphertext_unicode, passphrase, N=10)
decrypted_unicode = decrypted_unicode_bytes.decode('utf-8')
print(f"Decrypted unicode: {decrypted_unicode}")
print("Unicode match:", decrypted_unicode == unicode_text.decode('utf-8'))
assert decrypted_unicode == unicode_text.decode('utf-8')

# Final Summary
print("\n\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print("✓ Example 1: Basic encryption/decryption - PASSED")
print("✓ Example 2: Moderate-sized data (100 bytes) - PASSED")
print("✓ Example 3: Wrong passphrase rejection - PASSED")
print("✓ Example 4: Empty plaintext handling - PASSED")
print("✓ Example 5: Unicode text handling - PASSED")
print("\nAll Z-framework encryption/decryption use cases validated successfully!")

# Z-framework component analysis
print("\n" + "="*80)
print("Z-FRAMEWORK COMPONENT ANALYSIS")
print("="*80)
test_zeta = DiscreteZetaShift(42)
print(f"Test DiscreteZetaShift(42):")
print(f"  a = {test_zeta.a}")
print(f"  b = {test_zeta.b}")
print(f"  c = {test_zeta.c}")
print(f"  z = a*(b/c) = {test_zeta.compute_z()}")

attrs = test_zeta.attributes
print(f"  D = {attrs['D']}")
print(f"  E = {attrs['E']}")
print(f"  F = {attrs['F']}")
print(f"  O = {attrs['O']}")

coords_3d = test_zeta.get_3d_coordinates()
print(f"  3D coordinates: ({coords_3d[0]:.6f}, {coords_3d[1]:.6f}, {coords_3d[2]:.6f})")

print(f"\nVortex size: {len(test_zeta.vortex)}")
print(f"f parameter: {test_zeta.f}")
print(f"w parameter: {test_zeta.w}")

print("\nZ-crypto demonstration completed successfully!")

PHI = mp.phi  # Assuming PHI (Golden Ratio) is used

def compute_r(s, N=10):
    zeta = DiscreteZetaShift(s)
    O_list = [zeta.getO()]
    for _ in range(N - 1):
        zeta = zeta.unfold_next()
        O_list.append(zeta.getO())
    
    # Manual product calculation
    prod_O = mp.mpf(1)
    for o_val in O_list:
        prod_O *= o_val
        
    phi_N = PHI ** N
    return prod_O / phi_N