import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit app title
st.title("Relativistic Distortions on the Number Line")

# User inputs
v = st.slider("Boost speed v (as a fraction of c)", min_value=0.0, max_value=0.99, value=0.6, step=0.01)
c = 1.0

gamma = 1 / np.sqrt(1 - v**2)
x_vals = np.arange(-5, 6)

st.markdown("## 1. Length Contraction")
x_prime = x_vals / gamma
fig1, ax1 = plt.subplots(figsize=(6, 1))
ax1.scatter(x_vals, np.zeros_like(x_vals), label="S ticks (t=0)")
ax1.scatter(x_prime, np.ones_like(x_prime), label="S' ticks (t'=0)")
ax1.set_yticks([0, 1], labels=['S', "S'"])
ax1.legend()
ax1.set_title("Length Contraction")
st.pyplot(fig1)

st.markdown("## 2. Relativity of Simultaneity")
x_prime_2 = np.arange(-5, 6)
x_sheared = gamma * x_prime_2
fig2, ax2 = plt.subplots(figsize=(6, 1))
ax2.scatter(x_sheared, np.zeros_like(x_sheared), label="S: image of t'=0")
ax2.scatter(x_prime_2, np.ones_like(x_prime_2), label="S' ticks")
ax2.set_yticks([0, 1], labels=['S', "S'"])
ax2.legend()
ax2.set_title("Simultaneity Shear")
st.pyplot(fig2)

st.markdown("## 3. Velocity Addition Deformation")
u = np.linspace(-0.99, 0.99, 400)
u_linear = u + v
u_einstein = (u + v) / (1 + u*v)
fig3, ax3 = plt.subplots()
ax3.plot(u, u_linear, label="u + v", linestyle='--')
ax3.plot(u, u_einstein, label="u ⊕ v")
ax3.axhline(1, color='gray', linestyle=':')
ax3.axhline(-1, color='gray', linestyle=':')
ax3.set_title("Velocity Addition: Classical vs Relativistic")
ax3.set_xlabel("u")
ax3.set_ylabel("Resulting velocity")
ax3.legend()
ax3.grid(True)
st.pyplot(fig3)

st.markdown("## 4. Hyperbolic Rotation (Rapidity)")
t_vals = np.linspace(-1.5, 1.5, 200)
x_h = np.cosh(t_vals)
ct_h = np.sinh(t_vals)
theta = np.arctanh(v)
x_rot = x_h * np.cosh(theta) + ct_h * np.sinh(theta)
ct_rot = ct_h * np.cosh(theta) + x_h * np.sinh(theta)
fig4, ax4 = plt.subplots(figsize=(4, 4))
ax4.plot(x_h, ct_h, label='S')
ax4.plot(x_rot, ct_rot, label="S'")
ax4.set_aspect('equal')
ax4.set_title("Hyperbolic Rotation")
ax4.set_xlabel("x")
ax4.set_ylabel("ct")
ax4.legend()
ax4.grid(True)
st.pyplot(fig4)

st.markdown("## 5. Personal Number Squeeze")
n = st.number_input("Your personal number (e.g. age, favorite integer)", value=7)
xp = n / gamma
st.write(f"In the moving frame, your number appears at x′ ≈ {xp:.3f}")
st.progress(min(1.0, abs(xp) / max(1.0, abs(n))), text=f"Squeezed from {n} to {xp:.3f}")
