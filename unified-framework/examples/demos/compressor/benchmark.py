import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr, mean_squared_error as mse, structural_similarity as ssim
import os
from compressor import compress, decompress

def save_image(arr, filename):
    cv2.imwrite(filename, arr.clip(0,255).astype(np.uint8))

def filesize(filename):
    return os.path.getsize(filename)

def run_benchmark(img_path):
    # Load image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    data = img.flatten().astype(np.float32)
    shape = img.shape

    # --- Uniform Quantization ---
    uq_idxs = np.round((data - data.min()) / (data.max() - data.min()) * 127).astype(np.uint8)
    uq_centers = np.linspace(data.min(), data.max(), 128)
    uq_rec = uq_centers[uq_idxs].reshape(shape)
    save_image(uq_rec, "rec_uniform.png")
    uq_size = filesize("rec_uniform.png")
    uq_psnr = psnr(img, uq_rec)
    uq_mse = mse(img, uq_rec)
    uq_ssim = ssim(img, uq_rec)

    # --- Golden-Geodesic Quantization ---
    idxs, res_q, bin_centers, res_min, res_max = compress(data, n_bins=128)
    geod_rec = decompress(idxs, res_q, bin_centers, res_min, res_max).reshape(shape)
    save_image(geod_rec, "rec_geodesic.png")
    geod_size = filesize("rec_geodesic.png")
    geod_psnr = psnr(img, geod_rec)
    geod_mse = mse(img, geod_rec)
    geod_ssim = ssim(img, geod_rec)

    # --- PNG (Lossless) ---
    save_image(img, "orig.png")
    cv2.imwrite("img_png.png", img)
    png_size = filesize("img_png.png")

    # --- JPEG (Lossy) ---
    for q in [95, 75, 50]:
        cv2.imwrite(f"img_jpeg{q}.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        jpeg_rec = cv2.imread(f"img_jpeg{q}.jpg", cv2.IMREAD_GRAYSCALE)
        jpeg_size = filesize(f"img_jpeg{q}.jpg")
        jpeg_psnr = psnr(img, jpeg_rec)
        jpeg_mse = mse(img, jpeg_rec)
        jpeg_ssim = ssim(img, jpeg_rec)
        print(f"JPEG{q} | Size: {jpeg_size} | PSNR: {jpeg_psnr:.2f} | MSE: {jpeg_mse:.2f} | SSIM: {jpeg_ssim:.3f}")

    print("--- Summary ---")
    print(f"Original size: {filesize('orig.png')}")
    print(f"Uniform Quantization | Size: {uq_size} | PSNR: {uq_psnr:.2f} | MSE: {uq_mse:.2f} | SSIM: {uq_ssim:.3f}")
    print(f"Geodesic Quantization | Size: {geod_size} | PSNR: {geod_psnr:.2f} | MSE: {geod_mse:.2f} | SSIM: {geod_ssim:.3f}")
    print(f"PNG | Size: {png_size} | PSNR: inf (lossless) | MSE: 0 | SSIM: 1.0")

run_benchmark("myplot.png")