#!/usr/bin/env python3
"""
Verification script for expected factors of N
"""

N = 137524771864208156028430259349934309717
p = 10508623501177419659
q = 13086849276577416863

print("=" * 60)
print("FACTOR VERIFICATION")
print("=" * 60)
print()
print(f"N = {N}")
print(f"p = {p}")
print(f"q = {q}")
print()
print(f"p * q = {p * q}")
print()
print(f"Match: {p * q == N}")
print()

if p * q == N:
    print("✓ Expected factors are CORRECT")
    print(f"  p is {p.bit_length()}-bit")
    print(f"  q is {q.bit_length()}-bit")
    print(f"  N is {N.bit_length()}-bit")
else:
    print("✗ Expected factors are INCORRECT")
    
print()
print("=" * 60)
