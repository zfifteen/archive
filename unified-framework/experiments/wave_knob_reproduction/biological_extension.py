#!/usr/bin/env python3
"""
Biological Extension - Cross-Domain Wave Pattern Validation
===========================================================

This script tests the universality of wave-knob patterns by applying similar
scanning techniques to biological sequences. It validates the hypothesis that
wave-like interference patterns are universal across domains.

Based on PR #713's claim of cross-domain extensions to WAVE-CRISPR with
similar r ≥ 0.92 correlations in biological sequence analysis.
"""

import sys
import os
import argparse
import random
import json
from typing import List, Dict, Any, Tuple
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import time

# Try to import Biopython if available
try:
    from Bio.Seq import Seq
    from Bio.SeqUtils import GC
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    print("Warning: Biopython not available. Using basic sequence generation.")

class BiologicalWaveScanner:
    """
    Biological sequence scanner using wave-knob principles.
    
    This class applies the wave-knob scanning concept to biological sequences,
    looking for resonance patterns in motif detection and sequence analysis.
    """
    
    def __init__(self, sequence: str = None, sequence_length: int = 10000):
        """
        Initialize biological wave scanner.
        
        Args:
            sequence: DNA sequence to analyze (None for generated sequence)
            sequence_length: Length of sequence to generate if none provided
        """
        if sequence is not None:
            self.sequence = sequence.upper()
        else:
            self.sequence = self._generate_sequence(sequence_length)
        
        self.sequence_length = len(self.sequence)
        self.total_scans = 0
        
    def _generate_sequence(self, length: int) -> str:
        """
        Generate a realistic DNA sequence with some structure.
        
        Args:
            length: Sequence length
            
        Returns:
            Generated DNA sequence
        """
        # Generate sequence with some periodic structure to mimic real genomic patterns
        bases = 'ATGC'
        sequence = []
        
        # Add some periodic motifs to create structure
        motifs = ['ATGC', 'GCAT', 'TACG', 'CGTA', 'ATAT', 'GCGC']
        
        for i in range(length):
            if i % 100 < 20:  # 20% periodic regions
                motif = motifs[i % len(motifs)]
                sequence.append(motif[i % len(motif)])
            else:  # 80% random regions
                sequence.append(random.choice(bases))
        
        return ''.join(sequence)
    
    def motif_scan(self, window: int, step: int, motif: str = 'ATG') -> Tuple[int, List[int]]:
        """
        Scan for motif occurrences using wave-knob parameters.
        
        Args:
            window: Scan window size
            step: Step size between scans  
            motif: Motif to search for
            
        Returns:
            Tuple of (motif_count, positions_found)
        """
        self.total_scans += 1
        motif_positions = []
        
        # Scan through sequence with given window and step
        for start in range(0, min(self.sequence_length - window, self.sequence_length), step):
            end = start + window
            if end > self.sequence_length:
                break
                
            # Look for motif in this window
            window_seq = self.sequence[start:end]
            pos = window_seq.find(motif)
            
            if pos != -1:
                motif_positions.append(start + pos)
        
        # Remove duplicates and sort
        unique_positions = sorted(list(set(motif_positions)))
        return len(unique_positions), unique_positions
    
    def gc_content_scan(self, window: int, step: int) -> Tuple[int, List[float]]:
        """
        Scan for GC content variation using wave-knob parameters.
        
        Args:
            window: Scan window size
            step: Step size between scans
            
        Returns:
            Tuple of (high_gc_regions_count, gc_contents)
        """
        self.total_scans += 1
        gc_contents = []
        high_gc_count = 0
        
        # Scan through sequence
        for start in range(0, min(self.sequence_length - window, self.sequence_length), step):
            end = start + window
            if end > self.sequence_length:
                break
            
            window_seq = self.sequence[start:end]
            
            # Calculate GC content
            gc_count = window_seq.count('G') + window_seq.count('C')
            gc_content = gc_count / len(window_seq) if len(window_seq) > 0 else 0
            gc_contents.append(gc_content)
            
            # Count high GC regions (>60%)
            if gc_content > 0.6:
                high_gc_count += 1
        
        return high_gc_count, gc_contents
    
    def complexity_scan(self, window: int, step: int) -> Tuple[int, List[float]]:
        """
        Scan for sequence complexity using wave-knob parameters.
        
        Complexity is measured as the number of unique k-mers in a window.
        
        Args:
            window: Scan window size
            step: Step size between scans
            
        Returns:
            Tuple of (high_complexity_regions_count, complexity_scores)
        """
        self.total_scans += 1
        complexity_scores = []
        high_complexity_count = 0
        k_mer_size = 3  # Use 3-mers for complexity
        
        # Scan through sequence
        for start in range(0, min(self.sequence_length - window, self.sequence_length), step):
            end = start + window
            if end > self.sequence_length:
                break
            
            window_seq = self.sequence[start:end]
            
            # Count unique k-mers
            k_mers = set()
            for i in range(len(window_seq) - k_mer_size + 1):
                k_mer = window_seq[i:i + k_mer_size]
                k_mers.add(k_mer)
            
            # Complexity score: ratio of unique k-mers to possible k-mers
            max_possible = min(len(window_seq) - k_mer_size + 1, 4**k_mer_size)
            complexity = len(k_mers) / max_possible if max_possible > 0 else 0
            complexity_scores.append(complexity)
            
            # High complexity threshold
            if complexity > 0.7:
                high_complexity_count += 1
        
        return high_complexity_count, complexity_scores
    
    def auto_tune_biological_scan(self, scan_type: str = 'motif', target_count: int = 1, 
                                 max_iterations: int = 50, initial_window: int = 100, 
                                 initial_step: int = 10, motif: str = 'ATG') -> Dict[str, Any]:
        """
        Auto-tune biological scanning parameters to find R* where count = target.
        
        Args:
            scan_type: Type of scan ('motif', 'gc_content', 'complexity')
            target_count: Target count to achieve
            max_iterations: Maximum tuning iterations
            initial_window: Starting window size
            initial_step: Starting step size  
            motif: Motif to search for (if scan_type is 'motif')
            
        Returns:
            Dictionary with tuning results
        """
        start_time = time.time()
        
        window = initial_window
        step = initial_step
        found_target = False
        
        results = {
            'scan_type': scan_type,
            'sequence_length': self.sequence_length,
            'target_count': target_count,
            'motif': motif if scan_type == 'motif' else None,
            'iterations': 0,
            'locked': False,
            'final_window': window,
            'final_step': step,
            'final_R': 0.0,
            'count': 0,
            'convergence_history': [],
            'total_scans': 0,
            'elapsed_time': 0.0
        }
        
        for iteration in range(max_iterations):
            # Perform scan based on type
            if scan_type == 'motif':
                count, _ = self.motif_scan(window, step, motif)
            elif scan_type == 'gc_content':
                count, _ = self.gc_content_scan(window, step)
            elif scan_type == 'complexity':
                count, _ = self.complexity_scan(window, step)
            else:
                raise ValueError(f"Unknown scan type: {scan_type}")
            
            R = window / step if step > 0 else float('inf')
            
            # Record iteration history
            results['convergence_history'].append({
                'iteration': iteration + 1,
                'window': window,
                'step': step,
                'R': R,
                'count': count,
                'adjustment': 'none'
            })
            
            if count == target_count:
                # Found target - lock in
                found_target = True
                results['count'] = count
                break
            elif count == 0:
                # No features found - increase R (expand search)
                if window < self.sequence_length // 4:
                    window = int(window * 1.5)
                    results['convergence_history'][-1]['adjustment'] = 'expand_window'
                else:
                    step = max(1, step - 1)
                    results['convergence_history'][-1]['adjustment'] = 'reduce_step'
            elif count > target_count:
                # Too many features - decrease R (narrow search)
                if window > step * 2:
                    window = max(step * 2, int(window * 0.7))
                    results['convergence_history'][-1]['adjustment'] = 'shrink_window'
                else:
                    step += 1
                    results['convergence_history'][-1]['adjustment'] = 'increase_step'
            else:
                # Fine-tune
                if count < target_count:
                    window = int(window * 1.2)
                    results['convergence_history'][-1]['adjustment'] = 'fine_expand'
        
        # Record final state
        results['iterations'] = min(iteration + 1, max_iterations)
        results['locked'] = found_target
        results['final_window'] = window
        results['final_step'] = step
        results['final_R'] = window / step if step > 0 else float('inf')
        results['total_scans'] = self.total_scans
        results['elapsed_time'] = time.time() - start_time
        
        return results
    
    def biological_r_sweep(self, window_range: Tuple[int, int, int], 
                          step_range: Tuple[int, int, int], 
                          scan_type: str = 'motif', motif: str = 'ATG') -> List[Dict[str, Any]]:
        """
        Perform R-sweep experiment on biological sequence.
        
        Args:
            window_range: (start, stop, step) for window values
            step_range: (start, stop, step) for step values
            scan_type: Type of scan to perform
            motif: Motif to search for (if applicable)
            
        Returns:
            List of scan results
        """
        results = []
        
        windows = range(*window_range)
        steps = range(*step_range)
        
        for window in windows:
            for step in steps:
                if step == 0:
                    continue
                
                # Perform scan based on type
                if scan_type == 'motif':
                    count, positions = self.motif_scan(window, step, motif)
                    extra_data = {'positions': positions[:5]}  # Limit output
                elif scan_type == 'gc_content':
                    count, gc_values = self.gc_content_scan(window, step)
                    extra_data = {'mean_gc': np.mean(gc_values) if gc_values else 0,
                                'std_gc': np.std(gc_values) if gc_values else 0}
                elif scan_type == 'complexity':
                    count, complexity_values = self.complexity_scan(window, step)
                    extra_data = {'mean_complexity': np.mean(complexity_values) if complexity_values else 0,
                                'std_complexity': np.std(complexity_values) if complexity_values else 0}
                else:
                    count, extra_data = 0, {}
                
                result = {
                    'scan_type': scan_type,
                    'window': window,
                    'step': step,
                    'R': window / step,
                    'count': count,
                    'is_resonance_valley': count == 1,
                    **extra_data
                }
                results.append(result)
        
        return results


def analyze_biological_wave_patterns(sequence_length: int = 10000, 
                                    window_range: Tuple[int, int, int] = (20, 200, 20),
                                    step_range: Tuple[int, int, int] = (5, 50, 5),
                                    scan_types: List[str] = None) -> Dict[str, Any]:
    """
    Analyze biological wave patterns and compare to mathematical patterns.
    
    Args:
        sequence_length: Length of sequence to generate/analyze
        window_range: Range for window parameter sweep
        step_range: Range for step parameter sweep
        scan_types: Types of scans to perform
        
    Returns:
        Analysis results
    """
    if scan_types is None:
        scan_types = ['motif', 'gc_content', 'complexity']
    
    scanner = BiologicalWaveScanner(sequence_length=sequence_length)
    
    print(f"Analyzing biological wave patterns:")
    print(f"  Sequence length: {sequence_length}")
    print(f"  Window range: {window_range}")
    print(f"  Step range: {step_range}")
    print(f"  Scan types: {scan_types}")
    
    analysis_results = {}
    
    for scan_type in scan_types:
        print(f"\n  Processing {scan_type} scan...")
        
        # Perform R-sweep
        results = scanner.biological_r_sweep(window_range, step_range, scan_type)
        
        if not results:
            continue
        
        # Extract data for correlation analysis
        R_values = [r['R'] for r in results]
        counts = [r['count'] for r in results]
        windows = [r['window'] for r in results]
        
        # Correlations (similar to mathematical wave analysis)
        correlation_R_count, p_value_R_count = pearsonr(R_values, counts) if len(R_values) >= 2 else (0, 1)
        correlation_window_count, p_value_window_count = pearsonr(windows, counts) if len(windows) >= 2 else (0, 1)
        
        # Resonance valley analysis
        resonance_valleys = [r for r in results if r['is_resonance_valley']]
        
        analysis_results[scan_type] = {
            'total_scans': len(results),
            'correlations': {
                'R_vs_count': {
                    'correlation': correlation_R_count,
                    'p_value': p_value_R_count,
                    'significant': p_value_R_count < 0.05,
                    'pr713_biological_target': abs(correlation_R_count) >= 0.92  # Biological target
                },
                'window_vs_count': {
                    'correlation': correlation_window_count,
                    'p_value': p_value_window_count,
                    'significant': p_value_window_count < 0.05
                }
            },
            'resonance_valleys': len(resonance_valleys),
            'count_statistics': {
                'mean': np.mean(counts) if counts else 0,
                'std': np.std(counts) if counts else 0,
                'range': [min(counts), max(counts)] if counts else [0, 0]
            },
            'results': results
        }
        
        print(f"    R vs count correlation: r = {correlation_R_count:.3f} (p = {p_value_R_count:.2e})")
        print(f"    Resonance valleys: {len(resonance_valleys)}")
        print(f"    Target met (r ≥ 0.92): {'✅' if abs(correlation_R_count) >= 0.92 else '❌'}")
    
    return {
        'sequence_length': sequence_length,
        'scan_parameters': {
            'window_range': window_range,
            'step_range': step_range
        },
        'scan_results': analysis_results
    }


def create_biological_plots(analysis: Dict[str, Any], output_path: str = None):
    """
    Create biological wave pattern plots.
    
    Args:
        analysis: Biological analysis results
        output_path: Output file path (None for display)
    """
    scan_results = analysis['scan_results']
    n_scans = len(scan_results)
    
    if n_scans == 0:
        print("No scan results for plotting")
        return
    
    fig, axes = plt.subplots(n_scans, 2, figsize=(12, 4 * n_scans))
    
    if n_scans == 1:
        axes = axes.reshape(1, -1)
    
    for i, (scan_type, data) in enumerate(scan_results.items()):
        results = data['results']
        R_values = [r['R'] for r in results]
        counts = [r['count'] for r in results]
        resonance_valleys = [r for r in results if r['is_resonance_valley']]
        
        # Plot 1: Count vs R ratio
        axes[i, 0].scatter(R_values, counts, alpha=0.7, s=30, label=f'{scan_type} features')
        
        # Highlight resonance valleys
        if resonance_valleys:
            valley_R = [r['R'] for r in resonance_valleys]
            valley_counts = [r['count'] for r in resonance_valleys]
            axes[i, 0].scatter(valley_R, valley_counts, color='red', s=60, 
                              label=f'Valleys (n={len(resonance_valleys)})', zorder=5)
        
        corr = data['correlations']['R_vs_count']
        axes[i, 0].set_xlabel('R = window/step')
        axes[i, 0].set_ylabel(f'{scan_type.title()} Count')
        axes[i, 0].set_title(f'Biological Wave Pattern: {scan_type.title()}\n'
                            f'r = {corr["correlation"]:.3f}, p = {corr["p_value"]:.2e}')
        axes[i, 0].grid(True, alpha=0.3)
        axes[i, 0].legend()
        
        # Plot 2: Count distribution
        axes[i, 1].hist(counts, bins=min(20, len(set(counts))), alpha=0.7, edgecolor='black')
        axes[i, 1].set_xlabel(f'{scan_type.title()} Count')
        axes[i, 1].set_ylabel('Frequency')
        axes[i, 1].set_title(f'Count Distribution: {scan_type.title()}')
        axes[i, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Biological plots saved to {output_path}")
    else:
        plt.show()


def main():
    """Main CLI interface for biological extension."""
    parser = argparse.ArgumentParser(description='Biological Wave Pattern Extension')
    
    parser.add_argument('--sequence-length', type=int, default=10000,
                       help='DNA sequence length to generate')
    parser.add_argument('--sequence-file', type=str,
                       help='File containing DNA sequence (FASTA or plain text)')
    parser.add_argument('--window-range', type=str, default='20,200,20',
                       help='Window range: start,stop,step')
    parser.add_argument('--step-range', type=str, default='5,50,5',
                       help='Step range: start,stop,step')
    parser.add_argument('--scan-types', type=str, default='motif,gc_content,complexity',
                       help='Comma-separated scan types')
    parser.add_argument('--motif', type=str, default='ATG',
                       help='Motif to search for')
    parser.add_argument('--auto-tune', action='store_true',
                       help='Run auto-tune experiment')
    parser.add_argument('--output', type=str, default='data/biological_patterns.json',
                       help='Output JSON file')
    parser.add_argument('--plots', type=str,
                       help='Biological plots output file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Parse ranges
    try:
        window_range = tuple(map(int, args.window_range.split(',')))
        step_range = tuple(map(int, args.step_range.split(',')))
        scan_types = args.scan_types.split(',')
    except ValueError:
        print("Error: Invalid range or scan type format")
        return 1
    
    # Load or generate sequence
    sequence = None
    if args.sequence_file:
        try:
            with open(args.sequence_file, 'r') as f:
                content = f.read()
                # Simple parsing - assume FASTA or plain sequence
                if content.startswith('>'):
                    lines = content.split('\n')[1:]  # Skip header
                    sequence = ''.join(lines).replace(' ', '').replace('\n', '')
                else:
                    sequence = content.replace(' ', '').replace('\n', '')
            print(f"Loaded sequence from {args.sequence_file} (length: {len(sequence)})")
        except Exception as e:
            print(f"Error loading sequence file: {e}")
            return 1
    
    if args.auto_tune:
        # Run auto-tune experiment
        scanner = BiologicalWaveScanner(sequence=sequence, 
                                       sequence_length=args.sequence_length)
        
        print("Running biological auto-tune experiments...")
        results = {}
        
        for scan_type in scan_types:
            print(f"\n  Auto-tuning {scan_type} scan...")
            result = scanner.auto_tune_biological_scan(
                scan_type=scan_type, 
                target_count=1,
                max_iterations=50,
                motif=args.motif
            )
            results[scan_type] = result
            
            print(f"    Locked: {result['locked']}, R*: {result['final_R']:.3f}, "
                  f"Iterations: {result['iterations']}")
        
        output_data = {
            'experiment_type': 'auto_tune',
            'sequence_length': scanner.sequence_length,
            'results': results
        }
    else:
        # Run R-sweep analysis
        analysis = analyze_biological_wave_patterns(
            sequence_length=args.sequence_length,
            window_range=window_range,
            step_range=step_range,
            scan_types=scan_types
        )
        
        # Display summary
        print(f"\nBiological Wave Pattern Analysis Summary:")
        
        target_met_count = 0
        for scan_type, data in analysis['scan_results'].items():
            corr = data['correlations']['R_vs_count']
            target_met = corr['pr713_biological_target']
            target_met_count += target_met
            
            print(f"  {scan_type}:")
            print(f"    Correlation: r = {corr['correlation']:.3f} (p = {corr['p_value']:.2e})")
            print(f"    Target met (r ≥ 0.92): {'✅' if target_met else '❌'}")
            print(f"    Resonance valleys: {data['resonance_valleys']}")
        
        print(f"\nOverall biological target achievement: {target_met_count}/{len(scan_types)} scan types")
        
        output_data = analysis
        
        # Generate plots if requested
        if args.plots:
            os.makedirs(os.path.dirname(args.plots), exist_ok=True)
            create_biological_plots(analysis, args.plots)
    
    # Save results
    try:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to {args.output}")
    except Exception as e:
        print(f"Warning: Could not save results: {e}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())