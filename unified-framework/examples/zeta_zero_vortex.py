import mpmath
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import collections
import math
from core.domain import DiscreteZetaShift

mpmath.mp.dps = 50  # High precision for zeta zeros and computations
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio for modular transformations
E_SQUARED = math.exp(2)  # Normalization constant for curvature bounds

def compute_zeta_zeros(J=100):
    zeros = [mpmath.zetazero(j+1) for j in range(J)]
    imag_zeros = [float(z.imag) for z in zeros]
    return imag_zeros

def unfold_zeros(imag_zeros):
    unfolded = []
    for t in imag_zeros:
        if t <= 0:
            continue
        log_term = mpmath.log(t / (2 * mpmath.pi * mpmath.exp(1)))
        unfolded_t = t / (2 * mpmath.pi * log_term)
        unfolded.append(float(unfolded_t))
    return np.array(unfolded)

def vortex_geometric_search(unfolded_zeros, num_predictions=10):
    predictions = []
    zeta = DiscreteZetaShift(len(unfolded_zeros))  # Start chain at current zero count
    for _ in range(num_predictions):
        attrs = zeta.attributes
        # Geometric minimization: Predict next unfolded_t minimizing O curvature
        candidate_t = unfolded_zeros[-1] + attrs['O'] / math.log(attrs['O'] + 1)  # Heuristic from var(log O) ~ log log n
        # Convert mpf to float to ensure compatibility with NumPy
        predictions.append(float(candidate_t))
        zeta = zeta.unfold_next()  # Unfold to next state
    return predictions

def plot_helical_vortex(unfolded_zeros, predictions):
    theta = 2 * np.pi * unfolded_zeros / PHI
    x = unfolded_zeros * np.cos(theta)
    y = unfolded_zeros * np.sin(theta)
    z = unfolded_zeros

    # Convert predictions to numpy array of floats to ensure compatibility
    predictions_array = np.array([float(p) for p in predictions])
    theta_pred = 2 * np.pi * predictions_array / PHI
    x_pred = predictions_array * np.cos(theta_pred)
    y_pred = predictions_array * np.sin(theta_pred)
    z_pred = predictions_array

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='blue', marker='o', s=20, label='Known Zeta Zeros')
    ax.plot(x, y, z, c='red', linewidth=1, label='Helical Geodesic')
    ax.scatter(x_pred, y_pred, z_pred, c='green', marker='x', s=30, label='Predicted Zeros')
    ax.set_xlabel('X (Cosine Projection)')
    ax.set_ylabel('Y (Sine Projection)')
    ax.set_zlabel('Z (Unfolded Height)')
    ax.set_title('Helical Vortex Geometric Search for Zeta Zeros')
    ax.legend()
    ax.view_init(elev=20, azim=45)
    plt.show()

def main(J=500, predictions=10):
    imag_zeros = compute_zeta_zeros(J)
    unfolded_zeros = unfold_zeros(imag_zeros)
    predicted_zeros = vortex_geometric_search(unfolded_zeros, predictions)
    print("Known Unfolded Zeros (first 5):", unfolded_zeros[:5])
    print("Predicted Unfolded Zeros:", predicted_zeros)
    plot_helical_vortex(unfolded_zeros, predicted_zeros)

if __name__ == "__main__":
    main()