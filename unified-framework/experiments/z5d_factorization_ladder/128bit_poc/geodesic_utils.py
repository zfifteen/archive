import mpmath as mp

mp.dps = 50
PHI = mp.phi

def theta_prime(n, k=0.3):
    mod = mp.fmod(n, PHI)
    return PHI * mp.power(mod / PHI, k)

def curvature(n):
    d = mp.e ** 2
    return mp.div(d * mp.log(n + 1), d)