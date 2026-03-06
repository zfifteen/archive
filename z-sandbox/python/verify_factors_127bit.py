#!/usr/bin/env python3
"""
Simple test to verify the factors are correct first.
"""
from mpmath import mp

mp.dps = 50

N_int = 137524771864208156028430259349934309717
p_claimed = 10508623501177419659
q_claimed = 13086849276577416863

print(f"N = {N_int}")
print(f"p (claimed) = {p_claimed}")
print(f"q (claimed) = {q_claimed}")
print()

# Verify multiplication
product = p_claimed * q_claimed
print(f"p × q = {product}")
print(f"Match: {product == N_int}")
print()

# Verify divisibility
print(f"N % p = {N_int % p_claimed}")
print(f"N // p = {N_int // p_claimed}")
print(f"Match q: {N_int // p_claimed == q_claimed}")
print()

# Bit lengths
print(f"N bits: {N_int.bit_length()}")
print(f"p bits: {p_claimed.bit_length()}")
print(f"q bits: {q_claimed.bit_length()}")
print()

# Check primality (basic)
import sympy
print(f"p is prime: {sympy.isprime(p_claimed)}")
print(f"q is prime: {sympy.isprime(q_claimed)}")
