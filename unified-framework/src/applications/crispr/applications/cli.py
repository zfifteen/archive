"""
CLI Application for CRISPR Spectral Resonance Analysis

Command-line interface for applying φ-phase transforms and arcsin bridge
to DNA sequences, extracting spectral features, and analyzing gRNA candidates.
"""

import argparse
import sys
import json
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from modules.phi_phase import (
    PhiPhaseTransform, 
    arcsin_bridge, 
    encode_dna_complex,
    combined_transform
)
from modules.spectral_features import (
    SpectralFeatureExtractor,
    compute_gc_content,
    assign_gc_quartile
)


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def analyze_sequence(
    sequence: str,
    k: float = 0.300,
    alpha: float = 0.95,
    fft_size: int = 256,
    window: str = 'hann',
    extract_features: bool = True
) -> Dict:
    """
    Analyze a single DNA sequence with φ-phase and arcsin transforms.
    
    Args:
        sequence: DNA sequence string
        k: φ-phase power parameter
        alpha: Arcsin compression factor
        fft_size: FFT size
        window: Window function type
        extract_features: Whether to extract spectral features
        
    Returns:
        Dictionary containing analysis results
    """
    # Encode sequence as complex waveform
    waveform_base = encode_dna_complex(sequence)
    
    # Apply transforms
    phi_transformed, arcsin_compressed, phi_phases = combined_transform(
        waveform_base, k=k, alpha=alpha
    )
    
    # Initialize feature extractor
    extractor = SpectralFeatureExtractor(
        fft_size=fft_size,
        window_type=window
    )
    
    # Compute spectra
    spectrum_base = extractor.compute_spectrum(waveform_base)
    spectrum_phi = extractor.compute_spectrum(phi_transformed)
    spectrum_final = extractor.compute_spectrum(arcsin_compressed)
    
    results = {
        'sequence': sequence,
        'length': len(sequence),
        'gc_content': compute_gc_content(sequence),
        'gc_quartile': assign_gc_quartile(compute_gc_content(sequence)),
        'k': k,
        'alpha': alpha,
    }
    
    if extract_features:
        # Extract all features
        features = extractor.extract_all_features(
            spectrum_base, 
            spectrum_final
        )
        results.update(features)
        
        # Add intermediate features
        results['delta_f1_phi_only'] = extractor.compute_delta_f1(
            spectrum_base, spectrum_phi
        )
        results['delta_entropy_phi_only'] = extractor.compute_delta_entropy(
            spectrum_base, spectrum_phi
        )
    
    return results


def k_sweep_analysis(
    sequence: str,
    k_min: float = 0.20,
    k_max: float = 0.40,
    k_step: float = 0.005,
    alpha: float = 0.95,
    fft_size: int = 256,
    window: str = 'hann'
) -> pd.DataFrame:
    """
    Perform k-parameter sweep analysis.
    
    Args:
        sequence: DNA sequence string
        k_min: Minimum k value
        k_max: Maximum k value
        k_step: Step size
        alpha: Arcsin compression factor
        fft_size: FFT size
        window: Window function type
        
    Returns:
        DataFrame with results for each k value
    """
    waveform_base = encode_dna_complex(sequence)
    extractor = SpectralFeatureExtractor(fft_size=fft_size, window_type=window)
    spectrum_base = extractor.compute_spectrum(waveform_base)
    
    k_values = np.arange(k_min, k_max + k_step/2, k_step)
    results = []
    
    for k in k_values:
        phi_transformed, arcsin_compressed, _ = combined_transform(
            waveform_base, k=k, alpha=alpha
        )
        spectrum_final = extractor.compute_spectrum(arcsin_compressed)
        
        features = extractor.extract_all_features(spectrum_base, spectrum_final)
        features['k'] = k
        results.append(features)
    
    return pd.DataFrame(results)


def batch_analyze_sequences(
    sequences: List[str],
    k: float = 0.300,
    alpha: float = 0.95,
    fft_size: int = 256,
    window: str = 'hann',
    output_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Analyze multiple sequences in batch.
    
    Args:
        sequences: List of DNA sequences
        k: φ-phase power parameter
        alpha: Arcsin compression factor
        fft_size: FFT size
        window: Window function type
        output_file: Optional path to save results
        
    Returns:
        DataFrame with results for all sequences
    """
    results = []
    
    for i, seq in enumerate(sequences):
        print(f"Analyzing sequence {i+1}/{len(sequences)}...", end='\r')
        result = analyze_sequence(seq, k=k, alpha=alpha, fft_size=fft_size, window=window)
        result['sequence_id'] = i
        results.append(result)
    
    print()  # New line after progress
    
    df = pd.DataFrame(results)
    
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
    
    return df


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CRISPR Spectral Resonance Analysis CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single sequence
  python cli.py --sequence ATGCTGCGGAGACCTGGAGAGAAAG --k 0.300 --alpha 0.95
  
  # K-sweep analysis
  python cli.py --sequence ATGCTGCGGAGACCTGGAGAGAAAG --k-sweep --k-min 0.20 --k-max 0.40
  
  # Batch analysis from file
  python cli.py --input sequences.txt --output results.csv
  
  # Use config file
  python cli.py --config configs/k300.yaml --input sequences.txt
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--sequence', type=str, help='Single DNA sequence to analyze')
    input_group.add_argument('--input', type=str, help='File with sequences (one per line)')
    input_group.add_argument('--config', type=str, help='YAML config file')
    
    # Transform parameters
    parser.add_argument('--k', type=float, default=0.300, help='φ-phase power parameter (default: 0.300)')
    parser.add_argument('--alpha', type=float, default=0.95, help='Arcsin compression factor (default: 0.95)')
    
    # K-sweep options
    parser.add_argument('--k-sweep', action='store_true', help='Perform k-parameter sweep')
    parser.add_argument('--k-min', type=float, default=0.20, help='Minimum k for sweep (default: 0.20)')
    parser.add_argument('--k-max', type=float, default=0.40, help='Maximum k for sweep (default: 0.40)')
    parser.add_argument('--k-step', type=float, default=0.005, help='Step size for k sweep (default: 0.005)')
    
    # FFT parameters
    parser.add_argument('--fft-size', type=int, default=256, help='FFT size (default: 256)')
    parser.add_argument('--window', type=str, default='hann', 
                       choices=['hann', 'hamming', 'blackman', 'none'],
                       help='Window function (default: hann)')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output file path (CSV or JSON)')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv',
                       help='Output format (default: csv)')
    
    args = parser.parse_args()
    
    # Load config if provided
    if args.config:
        config = load_config(args.config)
        # Override with config values
        if 'phi_phase' in config and 'k' in config['phi_phase']:
            args.k = config['phi_phase']['k']
        if 'arcsin_bridge' in config and 'alpha' in config['arcsin_bridge']:
            args.alpha = config['arcsin_bridge']['alpha']
        if 'N' in config:
            args.fft_size = config['N']
        if 'window' in config:
            args.window = config['window']
    
    # Process input
    if args.sequence:
        # Single sequence analysis
        if args.k_sweep:
            print(f"Performing k-sweep analysis from {args.k_min} to {args.k_max}...")
            results_df = k_sweep_analysis(
                args.sequence,
                k_min=args.k_min,
                k_max=args.k_max,
                k_step=args.k_step,
                alpha=args.alpha,
                fft_size=args.fft_size,
                window=args.window
            )
        else:
            print(f"Analyzing sequence (k={args.k}, α={args.alpha})...")
            result = analyze_sequence(
                args.sequence,
                k=args.k,
                alpha=args.alpha,
                fft_size=args.fft_size,
                window=args.window
            )
            results_df = pd.DataFrame([result])
    
    elif args.input:
        # Batch analysis from file
        print(f"Loading sequences from {args.input}...")
        with open(args.input, 'r') as f:
            sequences = [line.strip() for line in f if line.strip()]
        
        print(f"Analyzing {len(sequences)} sequences...")
        results_df = batch_analyze_sequences(
            sequences,
            k=args.k,
            alpha=args.alpha,
            fft_size=args.fft_size,
            window=args.window,
            output_file=args.output
        )
    
    # Display and save results
    if args.output:
        if args.format == 'csv' or args.output.endswith('.csv'):
            results_df.to_csv(args.output, index=False)
            print(f"Results saved to {args.output}")
        elif args.format == 'json' or args.output.endswith('.json'):
            results_df.to_json(args.output, orient='records', indent=2)
            print(f"Results saved to {args.output}")
    else:
        # Print to console
        print("\nResults:")
        print(results_df.to_string())


if __name__ == '__main__':
    main()
