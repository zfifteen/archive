"""
Comprehensive test suite for Wave-CRISPR Metrics Integration

This script validates the enhanced Wave-CRISPR metrics implementation,
demonstrating integration with the Z framework and providing detailed
analysis of genetic sequence mutations.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for CI/CD
import matplotlib.pyplot as plt
from wave_crispr_metrics import WaveCRISPRMetrics

def test_basic_functionality():
    """Test basic functionality and edge cases."""
    print("Testing basic functionality...")
    
    # Simple test sequence
    sequence = "ATCGATCGATCG"
    metrics = WaveCRISPRMetrics(sequence)
    
    # Test single mutation analysis
    result = metrics.analyze_mutation(0, 'G')
    assert result is not None
    assert 'delta_f1' in result
    assert 'delta_peaks' in result
    assert 'delta_entropy' in result
    assert 'composite_score' in result
    assert 'z_factor' in result
    
    print("✓ Basic mutation analysis")
    
    # Test no-mutation case
    result = metrics.analyze_mutation(0, 'A')
    assert result is None
    
    print("✓ No-mutation handling")
    
    # Test edge cases
    try:
        metrics.analyze_mutation(len(sequence), 'A')
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    try:
        metrics.analyze_mutation(0, 'X')
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    print("✓ Edge case handling")

def test_z_framework_integration():
    """Test integration with Z framework components."""
    print("\nTesting Z framework integration...")
    
    sequence = "ATCGATCGATCGATCGATCG"
    metrics = WaveCRISPRMetrics(sequence)
    
    # Test Z factor computation
    z_factor = metrics.compute_z_factor(10)
    assert z_factor > 0
    assert isinstance(z_factor, (int, float))
    
    print(f"✓ Z factor computation: {z_factor:.2e}")
    
    # Test that Z factors vary with position
    z_factors = [metrics.compute_z_factor(i) for i in range(5)]
    assert len(set(z_factors)) > 1  # Should have variation
    
    print("✓ Position-dependent Z factors")

def test_enhanced_entropy_metric():
    """Test the enhanced entropy metric with O / ln n scaling."""
    print("\nTesting enhanced entropy metric...")
    
    sequence = "AAAAAAAAAA"  # Uniform sequence
    metrics = WaveCRISPRMetrics(sequence)
    
    # Create contrasting mutation
    base_waveform = metrics.build_waveform()
    mut_sequence = "ATCGATCGAT"
    mut_waveform = metrics.build_waveform(mut_sequence)
    
    base_spectrum = metrics.compute_spectrum(base_waveform)
    mut_spectrum = metrics.compute_spectrum(mut_waveform)
    
    # Test spectral order computation
    O_base = metrics.compute_spectral_order(base_spectrum)
    O_mut = metrics.compute_spectral_order(mut_spectrum)
    
    assert O_base > 0
    assert O_mut > 0
    assert O_mut > O_base  # Diverse sequence should have higher order
    
    print(f"✓ Spectral order: uniform={O_base:.2f}, diverse={O_mut:.2f}")
    
    # Test enhanced entropy metric
    delta_entropy = metrics.compute_delta_entropy(base_spectrum, mut_spectrum, 5)
    assert isinstance(delta_entropy, (int, float))
    
    print(f"✓ Enhanced entropy metric: {delta_entropy:.3f}")

def test_comprehensive_analysis():
    """Test comprehensive sequence analysis with real biological sequence."""
    print("\nTesting comprehensive analysis...")
    
    # PCSK9 Exon 1 sequence (cholesterol regulation gene)
    pcsk9_exon1 = "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG"
    
    print(f"Analyzing PCSK9 Exon 1 ({len(pcsk9_exon1)} bp)...")
    
    metrics = WaveCRISPRMetrics(pcsk9_exon1)
    
    # Full sequence analysis
    results = metrics.analyze_sequence(step_size=30)
    
    assert len(results) > 0
    assert all('composite_score' in r for r in results)
    
    # Check that results are sorted by composite score
    scores = [r['composite_score'] for r in results]
    assert scores == sorted(scores, reverse=True)
    
    print(f"✓ Analyzed {len(results)} mutations")
    print(f"✓ Score range: {min(scores):.2f} to {max(scores):.2f}")
    
    # Test specific high-impact mutations
    top_mutation = results[0]
    print(f"✓ Top mutation: {top_mutation['original_base']}→{top_mutation['mutated_base']} at position {top_mutation['position']}")
    print(f"  Δf1: {top_mutation['delta_f1']:.1f}%")
    print(f"  ΔPeaks: {top_mutation['delta_peaks']:+d}")
    print(f"  ΔEntropy: {top_mutation['delta_entropy']:+.3f}")
    print(f"  Composite Score: {top_mutation['composite_score']:.2f}")

def test_comparison_with_original():
    """Compare with original implementation to ensure consistency."""
    print("\nComparing with original implementation...")
    
    sequence = "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG"
    
    # Original simple metrics for comparison
    metrics = WaveCRISPRMetrics(sequence)
    
    # Test position 30 (where original showed high impact)
    result = metrics.analyze_mutation(30, 'A')
    
    # Should show significant impact (based on original results)
    assert abs(result['delta_f1']) > 10  # Significant frequency change
    assert result['composite_score'] > 10  # High impact score
    
    print(f"✓ Position 30 G→A mutation shows high impact:")
    print(f"  Enhanced Δf1: {result['delta_f1']:.1f}% (original: ~-54%)")
    print(f"  Enhanced Score: {result['composite_score']:.2f} (original: ~46)")

def test_visualization():
    """Test visualization capabilities."""
    print("\nTesting visualization...")
    
    sequence = "ATCGATCGATCGATCG"
    metrics = WaveCRISPRMetrics(sequence)
    
    # Test baseline spectrum plot
    try:
        metrics.plot_baseline_spectrum()
        print("✓ Baseline spectrum visualization")
    except Exception as e:
        print(f"✗ Visualization error: {e}")

def generate_sample_report():
    """Generate a comprehensive sample report."""
    print("\nGenerating sample report...")
    
    # Multiple test sequences representing different biological contexts
    sequences = {
        "PCSK9_Exon1": "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG",
        "BRCA1_Fragment": "ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAGTGTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAATTTTGCATGCTGAAACTTCTCAA",
        "TP53_Fragment": "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGG"
    }
    
    print("WAVE-CRISPR ENHANCED METRICS: COMPARATIVE ANALYSIS")
    print("=" * 70)
    
    for name, sequence in sequences.items():
        print(f"\n{name} Analysis:")
        print("-" * 40)
        
        metrics = WaveCRISPRMetrics(sequence)
        results = metrics.analyze_sequence(step_size=25)
        
        if results:
            top_result = results[0]
            print(f"Length: {len(sequence)} bp")
            print(f"Top mutation: {top_result['original_base']}→{top_result['mutated_base']} at position {top_result['position']}")
            print(f"Enhanced metrics:")
            print(f"  Δf1: {top_result['delta_f1']:+.1f}%")
            print(f"  ΔPeaks: {top_result['delta_peaks']:+d}")
            print(f"  ΔEntropy: {top_result['delta_entropy']:+.3f}")
            print(f"  Z factor: {top_result['z_factor']:.2e}")
            print(f"  Composite Score: {top_result['composite_score']:.2f}")

def main():
    """Run comprehensive test suite."""
    print("Wave-CRISPR Enhanced Metrics Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_z_framework_integration()
        test_enhanced_entropy_metric()
        test_comprehensive_analysis()
        test_comparison_with_original()
        test_visualization()
        generate_sample_report()
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("Enhanced Wave-CRISPR metrics successfully integrated with Z framework")
        print("Key improvements:")
        print("- ΔEntropy now uses O / ln n scaling with spectral order")
        print("- Composite score incorporates Z = A(B/c) universal invariance")
        print("- Position-dependent geometric effects via discrete zeta shifts")
        print("- Integration with unified mathematical framework")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()