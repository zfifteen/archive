import numpy as np
from scipy.signal import czt
from typing import Dict, Any

# Constants from SantaLucia 1998 (kcal/mol)
NEAREST_NEIGHBOR_DG = {
    "AA": -1.00, "TT": -1.00, "AT": -0.88, "TA": -0.58,
    "CA": -1.45, "TG": -1.45, "GT": -1.44, "AC": -1.44,
    "CT": -1.28, "AG": -1.28, "GA": -1.30, "TC": -1.30,
    "CG": -2.17, "GC": -2.24, "GG": -1.84, "CC": -1.84,
}
_DG_MIN = -2.24
_DG_MAX = -0.58

def encode_crispr_sequence(seq: str, r_ratio: float = 20.0) -> np.ndarray:
    """
    Unified encoding combining:
    1. Base-specific breathing (Real part from wave-crispr-signal)
    2. Thermodynamic stability (Imaginary part from dna-breathing-dynamics)
    3. Helical phase modulation (from both)
    """
    seq = seq.upper().replace("U", "T")
    n = len(seq)
    if n == 0: return np.array([])

    # 1. Real Part: Opening-rate contrast
    alpha = float(np.log(max(r_ratio, 1.0000001)))
    # 2. Imaginary Part: Nearest-neighbor stability
    
    complex_signal = np.zeros(n, dtype=complex)
    
    for i in range(n):
        # Real part based on breathing
        base = seq[i]
        real_part = -alpha if base in "AT" else alpha
        
        # Imaginary part based on thermodynamics
        if i < n - 1:
            dinuc = seq[i:i+2]
            dg = NEAREST_NEIGHBOR_DG.get(dinuc, -1.5)
        else:
            dg = -1.5 # Neutral end
        
        norm_imag = (dg - _DG_MIN) / (_DG_MAX - _DG_MIN)
        complex_signal[i] = complex(real_part, norm_imag)
    
    # Helical phase modulation (10.5 bp turn)
    phases = np.exp(1j * 2 * np.pi * np.arange(n) / 10.5)
    return complex_signal * phases

def calculate_crispr_score(seq: str) -> Dict[str, Any]:
    """
    Extract spectral features using CZT for high resolution.
    """
    if len(seq) < 20:
        return {"error": "Sequence too short (min 20bp)"}
        
    z = encode_crispr_sequence(seq)
    
    # CZT Analysis centered at helical frequency (1/10.5)
    f0 = 1 / 10.5
    bw = 0.01
    M = 128
    
    f_low = f0 - bw
    f_high = f0 + bw
    a = np.exp(-2j * np.pi * f_low)
    w = np.exp(2j * np.pi * (f_high - f_low) / M)
    
    spectrum = czt(z, a=a, w=w, m=M)
    magnitudes = np.abs(spectrum)
    
    peak_mag = np.max(magnitudes)
    avg_mag = np.mean(magnitudes)
    snr = peak_mag / (avg_mag + 1e-9)
    
    # Phase coherence
    coherence = np.abs(np.mean(z / (np.abs(z) + 1e-9)))
    
    # Combined "Z-Score" (empirical formula to be refined)
    score = (peak_mag * coherence * snr) / 10.0
    
    return {
        "sequence": seq,
        "peak_magnitude": float(peak_mag),
        "coherence": float(coherence),
        "snr": float(snr),
        "combined_score": float(score)
    }

if __name__ == "__main__":
    # Test with a known good guide (e.g. from Brunello)
    guide = "GCTCGTCCATGCCGAGAGTG" # Dummy but valid-looking
    print(calculate_crispr_score(guide))
