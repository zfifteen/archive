# Import the existing RSA factorization framework
from src.applications.primes.core.rsa_probe_validation import (
    RSA_CHALLENGE_NUMBERS, 
    probe_semiprime_with_timeout, 
    compensated_k_estimation
)