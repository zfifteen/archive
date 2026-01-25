#!/usr/bin/env python3
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import datetime

def generate_weak_cert(filename, p, q, subject_name):
    e = 65537
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    # Create private key numbers
    private_numbers = rsa.RSAPrivateNumbers(
        p=p,
        q=q,
        d=d,
        dmp1=d % (p - 1),
        dmq1=d % (q - 1),
        iqmp=pow(q, -1, p),
        public_numbers=rsa.RSAPublicNumbers(e=e, n=n)
    )

    private_key = private_numbers.private_key(default_backend())

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write PEM cert
    with open(filename, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

# Generate weak certs
# Weak 1: Close primes (Fermat vulnerable)
generate_weak_cert('test_certs/weak_close.pem', 1000000007, 1000000009, 'WeakClose')

# Weak 2: Smaller close primes
generate_weak_cert('test_certs/weak_small.pem', 10007, 10009, 'WeakSmall')

# Strong: Not close
generate_weak_cert('test_certs/strong.pem', 1000000007, 1000000021, 'Strong')

print("Test certificates generated in test_certs/")