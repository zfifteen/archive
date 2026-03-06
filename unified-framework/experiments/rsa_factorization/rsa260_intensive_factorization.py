# Import the existing RSA factorization framework
import sys
import os
# Ensure src is in the Python path for absolute import to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from src.applications.primes.core.rsa_probe_validation import (
    RSA_CHALLENGE_NUMBERS, 
    probe_semiprime_with_timeout, 
    compensated_k_estimation
)