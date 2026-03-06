import matplotlib.pyplot as plt
import numpy as np

def plot_semiprime_triangle(p, q, ax=None):
    """
    Plots a triangle representing the semiprime N = p * q in log-space.

    Coordinates:
    - P: (ln p, 0)
    - Q: (0, ln q)
    - N: (ln p, ln q)
    """
    # If no axes provided, create a new figure
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    # 1. Calculate Logarithmic Coordinates
    ln_p = np.log(p)
    ln_q = np.log(q)

    # Define Points as Vectors
    P = np.array([ln_p, 0])
    Q = np.array([0, ln_q])
    N = np.array([ln_p, ln_q]) # The Semiprime N

    # 2. Plot the Triangle PQN
    # Order: P -> N -> Q -> P (to close the loop)
    x_coords = [P[0], N[0], Q[0], P[0]]
    y_coords = [P[1], N[1], Q[1], P[1]]

    ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='Triangle PQN')
    ax.fill(x_coords, y_coords, 'skyblue', alpha=0.3)

    # 3. Add Reference Lines (The "Box")
    # Dashed lines from origin to P and Q to show the axes components
    ax.plot([0, ln_p], [0, 0], 'k--', alpha=0.5)
    ax.plot([0, 0], [0, ln_q], 'k--', alpha=0.5)

    # 4. Mark Vertices
    ax.scatter([P[0], Q[0], N[0]], [P[1], Q[1], N[1]], color='red', zorder=5)

    # Labels for Vertices
    ax.text(P[0], P[1] - 0.15 * ln_q, f'P ({np.round(ln_p, 2)}, 0)', ha='center')
    ax.text(Q[0] - 0.1 * ln_p, Q[1], f'Q (0, {np.round(ln_q, 2)})', va='center', ha='right')
    ax.text(N[0] + 0.05 * ln_p, N[1] + 0.05 * ln_q, f'N ({np.round(ln_p, 2)}, {np.round(ln_q, 2)})', ha='left')

    # 5. Calculate and Annotate Angles
    # Angle at P: tan(P) = Opp/Adj = (Length NQ) / (Length NP) = ln p / ln q
    # Note: Length NQ is along x-axis (ln p), Length NP is along y-axis (ln q)
    # Wait: Vector NP is (0, ln q) -> Length is ln q
    #       Vector NQ is (-ln p, 0) -> Length is ln p
    # In triangle PQN (Right Angle at N):
    #   Angle at P is opposite side NQ (len ln p)
    #   tan(P) = (ln p) / (ln q)
    angle_P_deg = np.degrees(np.arctan(ln_p / ln_q))
    angle_Q_deg = np.degrees(np.arctan(ln_q / ln_p))

    # Annotate Angle P
    ax.text(P[0] - 0.1 * ln_p, P[1] + 0.1 * ln_q, f'{angle_P_deg:.1f}°',
            color='darkgreen', fontsize=10, fontweight='bold')

    # Annotate Angle Q
    ax.text(Q[0] + 0.05 * ln_p, Q[1] - 0.1 * ln_q, f'{angle_Q_deg:.1f}°',
            color='darkgreen', fontsize=10, fontweight='bold')

    # Mark Right Angle at N
    sq_size = 0.08 * min(ln_p, ln_q)
    rect = plt.Rectangle((N[0] - sq_size, N[1] - sq_size), sq_size, sq_size, fill=False, color='black')
    ax.add_patch(rect)

    # 6. Styling
    ax.set_title(f'Log-Space Semiprime Triangle\n$N={p*q}$ ($p={p}, q={q}$)')
    ax.set_xlabel(r'$\ln(x)$')
    ax.set_ylabel(r'$\ln(y)$')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect('equal')

    # Set dynamic limits with padding
    ax.set_xlim(-0.3 * ln_p, 1.5 * ln_p)
    ax.set_ylim(-0.3 * ln_q, 1.5 * ln_q)

if __name__ == "__main__":
    # Example 1: N = 15 (3 * 5)
    p1, q1 = 3, 5

    # Example 2: N = 6 (2 * 3)
    p2, q2 = 2, 3

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    plot_semiprime_triangle(p1, q1, ax=ax1)
    plot_semiprime_triangle(p2, q2, ax=ax2)

    plt.tight_layout()
    plt.show()