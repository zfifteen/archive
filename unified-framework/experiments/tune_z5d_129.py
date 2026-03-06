import mpmath

mpmath.mp.dps = 50

# Known factors for RSA-129
p_str = "3490529510847650949147849619903898133417764638493387843990820577"
q_str = "32769132993266709549961988190834461413177642967992942539798288533"

p = mpmath.mpf(p_str)
q = mpmath.mpf(q_str)

def inverse_li(target_p):
    ln_p = mpmath.log(target_p)
    k0 = target_p * ln_p
    k_low = k0 * 0.5
    k_high = k0 * 2
    for _ in range(200):
        k_mid = (k_low + k_high) / 2
        li_mid = mpmath.ei(mpmath.log(k_mid))
        if li_mid < target_p:
            k_low = k_mid
        else:
            k_high = k_mid
    li_final = mpmath.ei(mpmath.log(k_mid))
    print(f"target: {float(target_p)}, li_final: {float(li_final)}, diff: {float(target_p - li_final)}")
    return float(k_mid)

k_p = inverse_li(p)
k_q = inverse_li(q)

print(f"k_p: {k_p}")
print(f"k_q: {k_q}")

# Now, compute li_k_p and needed correction
mp_k_p = mpmath.mpf(k_p)
li_k_p = mpmath.ei(mpmath.log(mp_k_p))
phi = (1 + mpmath.sqrt(5)) / 2
mod_phi = mpmath.fmod(mp_k_p, phi)
geo_p = phi * (mod_phi / phi) ** 0.3
correction_needed_p = p - li_k_p
kstar = 0.04449  # from RSA-100, perhaps optimize
c_needed_p = correction_needed_p / ((mp_k_p ** kstar) * geo_p) if correction_needed_p != 0 else 0

mp_k_q = mpmath.mpf(k_q)
li_k_q = mpmath.ei(mpmath.log(mp_k_q))
mod_phi_q = mpmath.fmod(mp_k_q, phi)
geo_q = phi * (mod_phi_q / phi) ** 0.3
correction_needed_q = q - li_k_q
c_needed_q = correction_needed_q / ((mp_k_q ** kstar) * geo_q) if correction_needed_q != 0 else 0

print(f"c_needed_p: {float(c_needed_p)}")
print(f"c_needed_q: {float(c_needed_q)}")

c = float((c_needed_p + c_needed_q) / 2) if c_needed_p != 0 and c_needed_q != 0 else 0
print(f"Averaged c: {c}")

# Now, test with tuned c
def z5d_prime(k):
    mp_k = mpmath.mpf(k)
    ln_k = mpmath.log(mp_k)
    li_k = mpmath.ei(ln_k)
    # geodesic correction
    mod_phi = mpmath.fmod(mp_k, phi)
    geo = phi * (mod_phi / phi) ** 0.3
    # correction terms
    correction = c * (mp_k ** kstar) * geo
    pred_p = li_k + correction
    return float(pred_p)

pred_p_p = z5d_prime(k_p)
pred_p_q = z5d_prime(k_q)

print(f"Pred p: {pred_p_p}, actual: {float(p)}, diff: {pred_p_p - float(p)}")
print(f"Pred q: {pred_p_q}, actual: {float(q)}, diff: {pred_p_q - float(q)}")