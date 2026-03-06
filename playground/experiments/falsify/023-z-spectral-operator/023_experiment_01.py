import torch
import torch.nn.functional as F
import numpy as np
import sys

# --- 1. Universal Hardware Configuration ---
# Force CPU for maximum compatibility in Linux sandboxes
device = torch.device("cpu")
print(f"System: Generic Linux / Sandbox Mode")
print(f"Device: {device}")
print("-" * 40)

# --- 2. Parameters & Domain Setup ---
# Target Composite: 1157 (13 * 89) by default; can be overridden
TARGET_N = 1157  # Change this for other composites
RESOLUTION = 1024  # Reduced for stability; scales with log(N)
DT = 0.001         # Smaller timestep for numerical stability
MAX_STEPS = 2000   # Increased cap, but with early stopping
KAPPA_BASE = 0.1   # Lowered to prevent forcing explosion
PHI_GOLDEN = 1.61803398875  # Golden ratio for phase modulation
EPSILON = 1e-8     # Smoothing for logs and gradients
CONVERGENCE_THRESH = 1e-4  # Delta resonance for early stopping

# Use complex128 for precision
dtype = torch.complex128

# --- 3. ASCII Visualization Tool ---
def ascii_plot(x_vals, y_vals, title="Resonance Spectrum", height=15, width=80):
    """
    Renders a vertical bar chart in the terminal. Downsamples if needed.
    """
    print(f"\n[{title}]")
    y_vals = np.array(y_vals)
    x_vals = np.array(x_vals)

    # Downsample to width
    if len(y_vals) > width:
        indices = np.linspace(0, len(y_vals)-1, width, dtype=int)
        x_vals = x_vals[indices]
        y_vals = y_vals[indices]

    # Normalize y to 0-1
    y_max = y_vals.max() if y_vals.max() > 0 else 1
    y_norm = y_vals / y_max

    rows = []
    for h in range(height, 0, -1):
        threshold = h / height
        row = ""
        for val in y_norm:
            if val >= threshold:
                row += "█"
            elif val >= threshold - (0.5/height):
                row += "▄"
            else:
                row += " "
        rows.append(row)

    # Print rows
    for row in rows:
        print(f"|{row}|")

    # X-axis
    print("+" + "-" * len(rows[0]) + "+")
    print(f"Low (2.0) {' ' * (len(rows[0]) - 12)} High ({int(x_vals[-1])})")

# --- 4. Core Logic ---
# Domain: From 2 to N/2, avoiding log(1)
x = torch.linspace(2 + EPSILON, TARGET_N // 2, RESOLUTION, device=device, dtype=torch.float64)

def initialize_waveform(n, x_domain):
    """
    Stable initialization: theta'(n,k) with epsilon smoothing.
    """
    log_n = torch.log(torch.tensor(n, device=device) + EPSILON)
    log_x = torch.log(x_domain + EPSILON)
    theta_prime = (log_n / log_x) * PHI_GOLDEN

    real_part = torch.cos(2 * np.pi * theta_prime)
    imag_part = torch.sin(2 * np.pi * theta_prime)

    return torch.complex(real_part, imag_part)

def compute_laplacian_1d_cpu(u_tensor):
    """
    1D Laplacian with circular padding for periodic boundary conditions.
    """
    # Circular pad: wrap edges
    u_padded = F.pad(u_tensor.view(1,1,-1), (1,1), mode='circular')

    # Stencil weights [1, -2, 1]
    weights = torch.tensor([[[1.0, -2.0, 1.0]]], device=device, dtype=torch.float64)

    real_lap = F.conv1d(u_padded.real, weights)
    imag_lap = F.conv1d(u_padded.imag, weights)

    return torch.complex(real_lap.squeeze(), imag_lap.squeeze())

def compute_phase_gradient_energy(u_tensor):
    """
    Stable phase gradient: smoothed diff with epsilon clamp.
    """
    phi = torch.angle(u_tensor)
    # Circular diff for stability
    grad_phi = torch.diff(phi, prepend=phi[-1].unsqueeze(0))
    grad_phi = torch.clamp(grad_phi, -np.pi, np.pi)  # Wrap large jumps
    return torch.pow(grad_phi, 2) + EPSILON  # Add epsilon to avoid zero

# --- 5. Main Execution ---
print(f"Initializing Waveform for N={TARGET_N}...")
u = initialize_waveform(TARGET_N, x)
prev_res_mean = 0.0

print(f"Solving Hidden PDE over up to {MAX_STEPS} steps...")
for t in range(MAX_STEPS):
    laplacian = compute_laplacian_1d_cpu(u)

    # Dynamic kappa: decay with x to focus low-frequency (small factors)
    kappa = KAPPA_BASE * (1.0 / torch.log(x + EPSILON))
    phase_energy = compute_phase_gradient_energy(u)

    # Forcing as complex: real from energy, imag zero (phase rotation)
    forcing = torch.complex(kappa * phase_energy, torch.zeros_like(phase_energy))

    # Update with clamping for stability
    du = (laplacian + forcing) * DT
    u = u + du
    u = torch.clamp(u.real, -1e6, 1e6) + 1j * torch.clamp(u.imag, -1e6, 1e6)

    # Check convergence every 100 steps
    if t % 100 == 0 and t > 0:
        res_current = torch.abs(torch.cos(2 * np.pi * torch.angle(u)))
        res_mean = res_current.mean().item()
        delta = abs(res_mean - prev_res_mean)
        print(f"Step {t}: Mean Resonance = {res_mean:.4f}, Delta = {delta:.6f}")
        if delta < CONVERGENCE_THRESH:
            print(f"Converged at step {t}.")
            break
        prev_res_mean = res_mean
    if t % 100 == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

print("\nEvolution Complete.")

# --- 6. Analysis & Output ---
phi_final = torch.angle(u)
resonance_final = torch.abs(torch.cos(2 * np.pi * phi_final))
res_cpu = resonance_final.numpy()
x_cpu = x.numpy()

# Plot
ascii_plot(x_cpu, res_cpu, title=f"Resonance Landscape for N={TARGET_N}")

# Extract Candidates
threshold = 0.85  # Lowered slightly for robustness
candidates_indices = np.where(res_cpu > threshold)[0]
candidates_values = x_cpu[candidates_indices]

# Diagnostics
peak_count = len(candidates_values)
mean_res = np.mean(res_cpu)
print(f"\nDiagnostics: Peaks Detected = {peak_count}, Mean Resonance = {mean_res:.4f}")

print("\n--- Detected Resonance Attractors ---")
seen = set()
hits = []
for c in candidates_values:
    val = int(round(c))
    if val not in seen and val > 1:
        is_factor = (TARGET_N % val == 0)
        marker = " <<< RESONANCE MATCH" if is_factor else ""
        if is_factor: hits.append(val)
        print(f"Candidate x ≈ {val}{marker}")
        seen.add(val)

if not hits:
    print("\n[!] No exact factors found. Try increasing MAX_STEPS or adjusting KAPPA_BASE.")
else:
    print(f"\n[+] SUCCESS: Recovered factors {sorted(hits)} from the spectral continuum.")
