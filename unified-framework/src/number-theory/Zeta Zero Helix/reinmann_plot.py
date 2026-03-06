import argparse
import mpmath
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mpmath.mp.dps = 50

def main():
    parser = argparse.ArgumentParser(
        description="3D helical embedding of Riemann zeros (loaded from file)"
    )
    parser.add_argument(
        '--limit', '-n',
        type=int,
        default=None,
        help='Upper limit of zeros to read from the file'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        default='zeros1',
        help='Path to the file containing zeros'
    )
    args = parser.parse_args()

    # Load zeros from file, apply --limit if provided
    with open(args.file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    if args.limit is not None:
        lines = lines[:args.limit]
    imag_zeros = np.array([float(line) for line in lines])
    J = len(imag_zeros)

    # Unfold zeros
    unfolded = []
    for t in imag_zeros:
        log_term = mpmath.log(t / (2 * mpmath.pi * mpmath.exp(1)))
        unfolded_t = t / (2 * mpmath.pi * log_term)
        unfolded.append(float(unfolded_t))
    unfolded = np.array(unfolded)

    # Helical embedding
    phi = (1 + np.sqrt(5)) / 2
    theta = 2 * np.pi * unfolded / phi
    x = unfolded * np.cos(theta)
    y = unfolded * np.sin(theta)
    z = unfolded

    # Plotting
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='blue', marker='o', s=20, label='Riemann Zeros')
    ax.plot(x, y, z, c='red', linewidth=1, label='Helical Geodesic')
    ax.set_xlabel('X (Cosine Projection)')
    ax.set_ylabel('Y (Sine Projection)')
    ax.set_zlabel('Z (Unfolded Height)')
    ax.set_title('3D Helical Embedding of Riemann Zeros')
    ax.legend(loc='upper right')
    ax.view_init(elev=20, azim=45)

    # Parameter panel
    param_str = (
        f"Parameters:\n"
        f"  J (zeros)    = {J}\n"
        f"  mp.dps       = {mpmath.mp.dps}\n"
        f"  φ (golden)   = {phi:.6f}\n"
        f"  limit        = {args.limit}\n"
        f"  file         = {args.file}"
    )
    fig.subplots_adjust(left=0.3)
    ax.text2D(
        0.05, 0.5, param_str,
        transform=ax.transAxes,
        fontsize=10,
        va='center',
        ha='left',
        family='monospace',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray")
    )

    plt.show()


if __name__ == '__main__':
    main()
