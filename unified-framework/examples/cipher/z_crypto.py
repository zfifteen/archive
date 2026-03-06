# z_crypto.py
# Reusable library for Z-framework keyed encryption, grounded in zeta shifts and curvature transformations.
# Dependencies: mpmath, sympy, hashlib, os, collections, abc

from abc import ABC
import collections
import hashlib
import os
import mpmath as mp
from sympy import divisors, isprime

mp.mp.dps = 50  # High precision for modular ops and large integers

PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

class UniversalZetaShift(ABC):
    def __init__(self, a, b, c):
        if a == 0 or b == 0 or c == 0:
            raise ValueError("Parameters cannot be zero.")
        self.a = mp.mpmathify(a)
        self.b = mp.mpmathify(b)
        self.c = mp.mpmathify(c)

    def compute_z(self):
        try:
            return self.a * (self.b / self.c)
        except ZeroDivisionError:
            return mp.inf

    def getD(self):
        try:
            return self.c / self.a
        except ZeroDivisionError:
            return mp.inf

    def getE(self):
        try:
            return self.c / self.b
        except ZeroDivisionError:
            return mp.inf

    def getF(self):
        try:
            d_over_e = self.getD() / self.getE()
            return PHI * ((d_over_e % PHI) / PHI) ** mp.mpf(0.3)
        except ZeroDivisionError:
            return mp.inf

    def getG(self):
        try:
            f = self.getF()
            return (self.getE() / f) / E_SQUARED
        except ZeroDivisionError:
            return mp.inf

    def getH(self):
        try:
            return self.getF() / self.getG()
        except ZeroDivisionError:
            return mp.inf

    def getI(self):
        try:
            g_over_h = self.getG() / self.getH()
            return PHI * ((g_over_h % PHI) / PHI) ** mp.mpf(0.3)
        except ZeroDivisionError:
            return mp.inf

    def getJ(self):
        try:
            return self.getH() / self.getI()
        except ZeroDivisionError:
            return mp.inf

    def getK(self):
        try:
            return (self.getI() / self.getJ()) / E_SQUARED
        except ZeroDivisionError:
            return mp.inf

    def getL(self):
        try:
            return self.getJ() / self.getK()
        except ZeroDivisionError:
            return mp.inf

    def getM(self):
        try:
            k_over_l = self.getK() / self.getL()
            return PHI * ((k_over_l % PHI) / PHI) ** mp.mpf(0.3)
        except ZeroDivisionError:
            return mp.inf

    def getN(self):
        try:
            return self.getL() / self.getM()
        except ZeroDivisionError:
            return mp.inf

    def getO(self):
        try:
            return self.getM() / self.getN()
        except ZeroDivisionError:
            return mp.inf

    @property
    def attributes(self):
        return {
            'a': self.a, 'b': self.b, 'c': self.c, 'z': self.compute_z(),
            'D': self.getD(), 'E': self.getE(), 'F': self.getF(), 'G': self.getG(),
            'H': self.getH(), 'I': self.getI(), 'J': self.getJ(), 'K': self.getK(),
            'L': self.getL(), 'M': self.getM(), 'N': self.getN(), 'O': self.getO()
        }

class DiscreteZetaShift(UniversalZetaShift):
    def __init__(self, n, v=1.0, delta_max=E_SQUARED):
        self.vortex = collections.deque()  # Instance-level vortex
        n = mp.mpmathify(n)
        d_n = len(divisors(int(n)))  # sympy for divisors, cast to int if needed
        kappa = d_n * mp.log(n + 1) / E_SQUARED
        delta_n = v * kappa
        super().__init__(a=n, b=delta_n, c=delta_max)
        self.v = v
        self.f = round(float(self.getG()))  # Cast to float for rounding
        self.w = round(float(2 * mp.pi / PHI))

        self.vortex.append(self)
        while len(self.vortex) > self.f:
            self.vortex.popleft()

    def unfold_next(self):
        successor = DiscreteZetaShift(self.a + 1, v=self.v, delta_max=self.c)
        self.vortex.append(successor)
        while len(self.vortex) > successor.f:
            self.vortex.popleft()
        return successor

    def get_3d_coordinates(self):
        attrs = self.attributes
        theta_d = PHI * ((attrs['D'] % PHI) / PHI) ** mp.mpf(0.3)
        theta_e = PHI * ((attrs['E'] % PHI) / PHI) ** mp.mpf(0.3)
        x = self.a * mp.cos(theta_d)
        y = self.a * mp.sin(theta_e)
        z = attrs['F'] / E_SQUARED
        return (float(x), float(y), float(z))

    def get_4d_coordinates(self):
        attrs = self.attributes
        x, y, z = self.get_3d_coordinates()
        t = -self.c * (attrs['O'] / PHI)
        return (float(t), x, y, z)

    def get_5d_coordinates(self):
        attrs = self.attributes
        theta_d = PHI * ((attrs['D'] % PHI) / PHI) ** mp.mpf(0.3)
        theta_e = PHI * ((attrs['E'] % PHI) / PHI) ** mp.mpf(0.3)
        x = self.a * mp.cos(theta_d)
        y = self.a * mp.sin(theta_e)
        z = attrs['F'] / E_SQUARED
        w = attrs['I']
        u = attrs['O']
        return (float(x), float(y), float(z), float(w), float(u))

    @classmethod
    def generate_key(cls, N, seed_n=2):
        zeta = cls(seed_n)
        trajectory_o = [zeta.getO()]
        for _ in range(1, N):
            zeta = zeta.unfold_next()
            trajectory_o.append(zeta.getO())
        hash_input = ''.join(mp.nstr(o, 20) for o in trajectory_o)  # Higher precision
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]

    @classmethod
    def get_coordinates_array(cls, dim=3, N=100, seed=2, v=1.0, delta_max=E_SQUARED):
        zeta = cls(seed, v, delta_max)
        shifts = [zeta]
        for _ in range(1, N):
            zeta = zeta.unfold_next()
            shifts.append(zeta)
        if dim == 3:
            coords = [shift.get_3d_coordinates() for shift in shifts]
        elif dim == 4:
            coords = [shift.get_4d_coordinates() for shift in shifts]
        else:
            raise ValueError("dim must be 3 or 4")
        is_primes = [isprime(int(shift.a)) for shift in shifts]  # Cast to int
        return coords, is_primes

def theta_prime(n, k=mp.mpf('0.3')):
    return PHI * ((n % PHI) / PHI) ** k

def compute_r(s, N=10):
    zeta = DiscreteZetaShift(s)
    O_list = [zeta.getO()]
    for _ in range(N - 1):
        zeta = zeta.unfold_next()
        O_list.append(zeta.getO())
    prod_O = mp.prod(O_list)
    phi_N = PHI ** N
    return prod_O / phi_N

def xor_bytes(a, b):
    if len(a) != len(b):
        raise ValueError("Byte strings must be same length for XOR")
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt(plaintext_bytes: bytes, passphrase: str, N: int = 10) -> bytes:
    """Encrypt plaintext bytes using Z-framework keyed scheme."""
    if not plaintext_bytes:
        # Handle empty plaintext
        key = hashlib.sha256(passphrase.encode()).digest()
        iv = os.urandom(32)
        return iv + (0).to_bytes(4, 'big')
    
    key = hashlib.sha256(passphrase.encode()).digest()  # 32 bytes
    iv = os.urandom(32)  # Match key length
    key_prime = xor_bytes(key, iv)
    s_prime = mp.mpmathify(int.from_bytes(key_prime, 'big'))
    r = compute_r(s_prime, N)
    theta = theta_prime(r)
    m = mp.mpmathify(int.from_bytes(plaintext_bytes, 'big'))
    e_float = m * theta
    e_int = int(mp.nint(e_float))  # Convert mpf to int
    e_bytes = e_int.to_bytes((e_int.bit_length() + 7) // 8, 'big')
    len_e = len(e_bytes)
    return iv + len_e.to_bytes(4, 'big') + e_bytes

def decrypt(ciphertext: bytes, passphrase: str, N: int = 10) -> bytes:
    """Decrypt ciphertext to plaintext bytes using Z-framework keyed scheme."""
    key = hashlib.sha256(passphrase.encode()).digest()
    iv = ciphertext[:32]
    len_e = int.from_bytes(ciphertext[32:36], 'big')
    
    if len_e == 0:
        # Handle empty plaintext case
        return b""
    
    e_bytes = ciphertext[36:36 + len_e]
    e_int = mp.mpmathify(int.from_bytes(e_bytes, 'big'))
    key_prime = xor_bytes(key, iv)
    s_prime = mp.mpmathify(int.from_bytes(key_prime, 'big'))
    r = compute_r(s_prime, N)
    theta = theta_prime(r)
    m_float = e_int / theta
    m_int = int(mp.nint(m_float))  # Convert mpf to int
    
    if m_int == 0:
        return b""
    
    return m_int.to_bytes((m_int.bit_length() + 7) // 8, 'big')