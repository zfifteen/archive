import numpy as np
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

# -----------------------------------------------------------------------------
# What problem is this script solving?
# -----------------------------------------------------------------------------
# We solve the steady 1D advection-diffusion boundary-value problem
#
#       a * u_x = nu * u_xx,   x in [0, 1]
#       u(0) = 0,  u(1) = 1
#
# where:
#   - a  is advection velocity (transport to the right if a > 0, left if a < 0)
#   - nu is diffusion coefficient (smoothing strength)
#
# Rearranged into residual form:
#
#       R(u) = -a * u_x + nu * u_xx = 0
#
# This equation develops a thin boundary layer when |a| / nu is large.
# In that regime, centered advection can oscillate (non-monotone), while
# upwind-biased methods are more robust.
#
# The script compares:
#   1) Fully centered discretization (classic but can oscillate at high cell Pe)
#   2) Upwind advection + centered diffusion (more dissipative, more robust)
#   3) Hyperbolized diffusion (Nishikawa-style relaxation system)
#
# and plots all of them against the exact analytic solution.
#
# ==================== PARAMETERS ====================
a = 1.0          # Constant advection velocity used in the PDE.
nu = 0.0025      # Physical diffusion coefficient.
n = 81           # Number of grid points including both boundaries.
h = 1.0 / (n - 1)  # Uniform grid spacing on [0, 1].

# ==================== CLASSIC SOLVERS (for comparison) ====================
def solve_central(n, a, nu):
    """
    Solve steady advection-diffusion using centered differences for BOTH terms.

    Discretization at interior node i:

        -a * (u_{i+1} - u_{i-1})/(2h)
        + nu * (u_{i+1} - 2u_i + u_{i-1})/h^2 = 0

    This gives the tridiagonal linear equation:

        (nu/h^2 + a/(2h)) * u_{i-1}
      + (-2nu/h^2)          * u_i
      + (nu/h^2 - a/(2h)) * u_{i+1} = 0

    Dirichlet boundary conditions are imposed strongly:
      u_0 = 0, u_{n-1} = 1.
    """
    h = 1.0 / (n - 1)
    x = np.linspace(0, 1, n)  # Physical coordinates of grid points.

    # Dense matrix for clarity (n is small here); could be sparse in large runs.
    A = np.zeros((n, n))
    b = np.zeros(n)

    # Boundary rows enforce u(0)=0 and u(1)=1 exactly.
    A[0,0] = A[-1,-1] = 1.0
    b[0] = 0.0
    b[-1] = 1.0

    # Fill interior finite-difference stencil rows.
    for i in range(1, n-1):
        A[i,i-1] =  nu/h**2 + a/(2*h)
        A[i,i]   = -2*nu/h**2
        A[i,i+1] =  nu/h**2 - a/(2*h)

    # Solve A u = b for nodal unknowns u.
    return x, np.linalg.solve(A, b)

def solve_upwind_adv(n, a, nu):
    """
    Solve steady advection-diffusion with:
      - first-order upwind for advection
      - centered second derivative for diffusion

    Why this is useful:
      Upwinding adds numerical damping in the transport direction and is
      much less likely to oscillate when advection dominates diffusion.

    Sign-aware advection stencil:
      - If a >= 0 (flow right): use backward difference for u_x
      - If a <  0 (flow left):  use forward difference for u_x
    """
    h = 1.0 / (n - 1)
    x = np.linspace(0, 1, n)
    A = np.zeros((n, n))
    b = np.zeros(n)

    # Dirichlet boundary conditions.
    A[0,0] = A[-1,-1] = 1.0
    b[0] = 0.0
    b[-1] = 1.0

    # Interior rows depend on flow direction.
    for i in range(1, n-1):
        if a >= 0.0:
            # Right-going flow:
            #   u_x ≈ (u_i - u_{i-1})/h  (backward/upwind)
            #
            # Equation:
            #   -a(u_i - u_{i-1})/h + nu(u_{i+1} - 2u_i + u_{i-1})/h^2 = 0
            A[i,i-1] = nu/h**2 + a/h
            A[i,i]   = -2*nu/h**2 - a/h
            A[i,i+1] = nu/h**2
        else:
            # Left-going flow:
            #   u_x ≈ (u_{i+1} - u_i)/h  (forward/upwind relative to flow)
            #
            # Equation:
            #   -a(u_{i+1} - u_i)/h + nu(u_{i+1} - 2u_i + u_{i-1})/h^2 = 0
            A[i,i-1] = nu/h**2
            A[i,i]   = -2*nu/h**2 + a/h
            A[i,i+1] = nu/h**2 - a/h
    return x, np.linalg.solve(A, b)

# ==================== HYPERBOLIZED UPWIND DIFFUSION ====================
def solve_hyperbolic(n, a, nu, tau=None, dt=None, nt_max=80000):
    """
    Nishikawa first-order hyperbolic system for steady advection-diffusion.

    The 2x2 system with state U = [u, q]^T and flux F(U):

        u_t  + (a*u + q)_x      = 0
        tau*q_t + (nu*u)_x       = -q

    Flux vector:  F = [a*u + q,  (nu/tau)*u]^T
    Source:       S = [0,        -q/tau     ]^T

    At steady state (u_t = q_t = 0):
        q = -nu * u_x
        (a*u + q)_x = 0  =>  a*u_x = nu*u_xx

    So the original PDE is recovered exactly (no tau-dependent error).

    The flux Jacobian has eigenvalues
        lambda = (a +/- sqrt(a^2 + 4*nu/tau)) / 2
    which are one positive, one negative, so information propagates in
    both directions.  A Rusanov (local Lax-Friedrichs) numerical flux is
    used at each cell interface for the full state vector.

    Parameters:
      tau    relaxation time scale; defaults to h/2 (Nishikawa O(h) scaling)
      dt     pseudo-time step; if None, choose a conservative stable value
      nt_max max pseudo-time iterations
    """
    h = 1.0 / (n - 1)
    x = np.linspace(0, 1, n)

    if tau is None:
        tau = h / 2.0  # Nishikawa scaling tau ~ O(h)

    dt_limit = stable_dt_limit(h, a, nu, tau)

    if dt is None:
        dt = dt_limit
    elif dt > dt_limit:
        warnings.warn(
            (
                "Provided dt exceeds conservative limit for explicit updates: "
                f"dt={dt:.3e}, limit={dt_limit:.3e}. "
                "Convergence/stability may degrade."
            ),
            RuntimeWarning,
            stacklevel=2,
        )

    # Initial guess for u: linear interpolation between Dirichlet boundaries.
    u = np.linspace(0, 1, n)
    # Initial auxiliary diffusive flux q. Starts at zero then relaxes.
    q = np.zeros(n)

    # Maximum wave speed bound for Rusanov dissipation:
    #   |a| + sqrt(nu/tau) >= spectral radius of the flux Jacobian
    s_max = abs(a) + np.sqrt(nu / tau) + 1e-8
    nu_over_tau = nu / tau

    # Pseudo-time marching loop.
    for it in range(nt_max):
        # Use old state on RHS and write updates into new arrays (explicit Euler).
        u_new = u.copy()
        q_new = q.copy()

        # Re-impose Dirichlet boundary conditions on u.
        u_new[0] = 0.0
        u_new[-1] = 1.0
        # Extrapolate q at boundaries (ghost-cell-like treatment).
        q_new[0] = q[1]
        q_new[-1] = q[-2]

        max_res = 0.0
        for i in range(1, n-1):
            # --- Rusanov flux at interface i-1/2 ---
            # Physical flux F = [a*u + q, (nu/tau)*u]
            # Left state: (u[i-1], q[i-1]), Right state: (u[i], q[i])
            Fhat_im_u = (0.5 * (a * (u[i-1] + u[i]) + q[i-1] + q[i])
                         - 0.5 * s_max * (u[i] - u[i-1]))
            Fhat_im_q = (0.5 * nu_over_tau * (u[i-1] + u[i])
                         - 0.5 * s_max * (q[i] - q[i-1]))

            # --- Rusanov flux at interface i+1/2 ---
            Fhat_ip_u = (0.5 * (a * (u[i] + u[i+1]) + q[i] + q[i+1])
                         - 0.5 * s_max * (u[i+1] - u[i]))
            Fhat_ip_q = (0.5 * nu_over_tau * (u[i] + u[i+1])
                         - 0.5 * s_max * (q[i+1] - q[i]))

            # Semi-discrete equations:
            #   du/dt = -(Fhat_ip_u - Fhat_im_u) / h
            #   dq/dt = -(Fhat_ip_q - Fhat_im_q) / h  -  q/tau
            du_dt = -(Fhat_ip_u - Fhat_im_u) / h
            dq_dt = -(Fhat_ip_q - Fhat_im_q) / h - q[i] / tau

            # Forward Euler pseudo-time update.
            u_new[i] += dt * du_dt
            q_new[i] += dt * dq_dt

            # Track largest local residual-like rate for convergence stopping.
            max_res = max(max_res, abs(du_dt), abs(dq_dt))

        # Advance pseudo-time state.
        u = u_new
        q = q_new

        # Stop when updates become very small.
        if max_res < 5e-7:
            print(f"Hyperbolic solver converged in {it} iterations")
            break

        # Sparse progress logging for long runs.
        if it % 20000 == 0:
            print(f"Iter {it:5d}, max res {max_res:.2e}")
    else:
        print("Warning: Hyperbolic solver did not fully converge")

    return x, u

# ==================== LOADING RATIO ====================
def loading_ratio(u, dx, a, nu):
    """
    Heuristic advection-vs-diffusion loading indicator (dimensionless).

    This is not a formal stability theorem; it is an interpretable metric
    that tends to increase when transport/injection features dominate
    diffusive smoothing.

    Components:
      tv       = total variation of u (sum |u_{i+1} - u_i|)
      inject   = mean |a * u_x|         (advection-driven gradient transport)
      smooth   = nu * mean |u_xx|       (diffusion-driven curvature smoothing)

    Returned ratio:
      Λ = tv * inject / smooth

    Tiny epsilons avoid division by zero for degenerate flat fields.
    """
    # Total variation: larger when solution has steep jumps/oscillations.
    tv = np.sum(np.abs(np.diff(u)))

    # First derivative on edges between points.
    ux = np.diff(u) / dx

    # Advection "injection" proxy.
    inject = np.mean(np.abs(a * ux)) + 1e-12

    # Second derivative (discrete curvature) at cell centers.
    uxx = np.diff(ux) / dx

    # Diffusive smoothing proxy.
    smooth_max = nu * np.mean(np.abs(uxx)) + 1e-12
    return (tv * inject) / smooth_max

def exact_solution(x, a, nu, pe_eps=1e-10):
    """
    Exact solution for:
      a*u_x = nu*u_xx, u(0)=0, u(1)=1

    Numerical note:
      For |Pe| very small, denominator expm1(Pe) suffers cancellation.
      We switch to the Pe->0 limit u(x)=x.
    """
    x = np.asarray(x, dtype=float)
    pe = a / nu
    if abs(pe) < pe_eps:
        return x.copy()
    return np.expm1(pe * x) / np.expm1(pe)


def stable_dt_limit(h, a, nu, tau, safety=0.45):
    """
    Conservative pseudo-time limit for explicit marching of the
    Nishikawa hyperbolic system.

    The maximum wave speed is bounded by |a| + sqrt(nu/tau),
    giving CFL condition dt <= safety * h / lambda_max.
    """
    lambda_max = abs(a) + np.sqrt(nu / tau) + 1e-8
    return safety * h / lambda_max


def main():
    # ==================== RUN & PLOT ====================
    # Compute all three numerical solutions on the same mesh.
    x_c, u_c = solve_central(n, a, nu)
    x_u, u_u = solve_upwind_adv(n, a, nu)
    x_h, u_h = solve_hyperbolic(n, a, nu)

    # Cell Péclet number: local advection/diffusion balance on one grid cell.
    #   Pe_cell = a*h/nu
    # Rough intuition:
    #   |Pe_cell| << 1 -> diffusion dominates
    #   |Pe_cell| >> 1 -> advection dominates (harder for centered schemes)
    print(f"Cell Peclet ≈ {a * h / nu:.1f}")
    print(
        f"Central       → range=[{u_c.min():.3f}, {u_c.max():.3f}]   "
        f"Λ ≈ {loading_ratio(u_c, h, a, nu):.3f}  (oscillates)"
    )
    print(
        f"Upwind adv    → range=[{u_u.min():.3f}, {u_u.max():.3f}]   "
        f"Λ ≈ {loading_ratio(u_u, h, a, nu):.3f}  (monotone)"
    )
    print(
        f"Hyperbolic    → range=[{u_h.min():.3f}, {u_h.max():.3f}]   "
        f"Λ ≈ {loading_ratio(u_h, h, a, nu):.3f}  (Nishikawa)"
    )

    # Exact analytic solution.
    x_exact = np.linspace(0, 1, 500)
    u_exact = exact_solution(x_exact, a, nu)

    # Plot all curves on one figure for direct qualitative comparison.
    plt.figure(figsize=(11, 6))
    plt.plot(x_c, u_c, 'r--', label='Central advection + Central diffusion', lw=2)
    plt.plot(x_u, u_u, 'b-', label='Upwind advection + Central diffusion', lw=2)
    plt.plot(x_h, u_h, 'g-', label='Hyperbolized (full upwind on diffusion)', lw=2.5)
    plt.plot(x_exact, u_exact, 'k-', label='Exact analytic', lw=1.5)

    # Basic plot cosmetics.
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('u')
    plt.title(
        f'1D Advection-Diffusion @ Cell Pe ≈ {a*h/nu:.1f}\n'
        'Your loading ratio Λ correlates with when central schemes fail'
    )
    plt.legend()
    plt.tight_layout()

    # Save next to this script, independent of where the command is run from.
    out_path = Path(__file__).with_name('hyperbolic_advection_diffusion_demo.png')
    plt.savefig(out_path, dpi=220)
    print(f"Saved plot to {out_path}")

    # Display interactive window if backend supports it.
    plt.show()


if __name__ == "__main__":
    main()
