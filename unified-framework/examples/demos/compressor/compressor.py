import numpy as np
import mpmath as mp
from sympy import isprime
from scipy.stats import gaussian_kde

# Golden ratio and settings
PHI = float((1 + mp.sqrt(5)) / 2)
K_STAR = 0.3  # Empirically optimal
N_BINS = 256  # Like 8-bit quantization

def theta_prime(val, k=K_STAR, phi=PHI):
    """Golden-ratio modular transform."""
    mod_phi = float(mp.fmod(val, phi))
    frac = mod_phi / phi
    return phi * (frac ** k)

def build_bin_centers(data, n_bins=N_BINS):
    """Compute bin centers using θ′ transform over data range."""
    minv, maxv = np.min(data), np.max(data)
    # Uniformly sample in value space, then map to θ′ space
    sample_points = np.linspace(minv, maxv, n_bins)
    theta_vals = np.array([theta_prime(p) for p in sample_points])
    # Sort θ′, cluster at high-prime-density regions (optionally)
    centers = np.sort(theta_vals)
    return centers

def geodesic_quantize(data, bin_centers):
    """Assign each datum to the nearest θ′ bin center."""
    idxs = np.argmin(np.abs(data[:, None] - bin_centers[None, :]), axis=1)
    quantized = bin_centers[idxs]
    residuals = data - quantized
    return idxs, residuals

def geodesic_dequantize(idxs, bin_centers, residuals):
    """Reconstruct data from bins + residuals."""
    return bin_centers[idxs] + residuals

def compress(data, n_bins=N_BINS):
    """Full compression pipeline."""
    bin_centers = build_bin_centers(data, n_bins)
    idxs, residuals = geodesic_quantize(data, bin_centers)
    # Quantize residuals (optional: uniform, Lloyd-Max, etc.)
    # For demonstration, use 8-bit uniform quantization
    res_min, res_max = residuals.min(), residuals.max()
    res_q = np.round((residuals - res_min) / (res_max - res_min) * 255).astype(np.uint8)
    # Store bin indices and quantized residuals
    return idxs.astype(np.uint8), res_q, bin_centers, res_min, res_max

def decompress(idxs, res_q, bin_centers, res_min, res_max):
    """Decompression pipeline."""
    residuals = res_q.astype(np.float32) / 255 * (res_max - res_min) + res_min
    return geodesic_dequantize(idxs, bin_centers, residuals)

# --- Demo on image or random signal ---
if __name__ == "__main__":
    import cv2

    # Load grayscale image or generate random signal
    img = cv2.imread("myplot.png", cv2.IMREAD_GRAYSCALE)
    if img is None:
        data = np.random.rand(10000) * 255
    else:
        data = img.flatten().astype(np.float32)

    idxs, res_q, bin_centers, res_min, res_max = compress(data, n_bins=128)
    rec = decompress(idxs, res_q, bin_centers, res_min, res_max)
    rec_img = rec.reshape(img.shape) if img is not None else rec

    # --- Metrics ---
    mse = np.mean((rec - data) ** 2)
    psnr = 10 * np.log10(255**2 / mse)

    # --- Compare to uniform quantizer ---
    uq_idxs = np.round((data - data.min()) / (data.max() - data.min()) * 127).astype(np.uint8)
    uq_centers = np.linspace(data.min(), data.max(), 128)
    uq_rec = uq_centers[uq_idxs]
    uq_mse = np.mean((uq_rec - data) ** 2)
    uq_psnr = 10 * np.log10(255**2 / uq_mse)

    print(f"Golden-geodesic PSNR: {psnr:.2f}dB, Uniform PSNR: {uq_psnr:.2f}dB")
    print(f"Compression ratio: {len(idxs)+len(res_q)} bytes (geodesic) "
          f"vs {len(uq_idxs)} bytes (uniform)")

    # Optionally save or visualize
    if img is not None:
        cv2.imwrite("recon_geodesic.png", rec_img.clip(0,255).astype(np.uint8))
        cv2.imwrite("recon_uniform.png", uq_rec.reshape(img.shape).clip(0,255).astype(np.uint8))