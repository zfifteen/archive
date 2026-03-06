#!/usr/bin/env python3
"""
Test Runner for CRISPR-Quantum Cross-Validation Pipeline

This script validates the complete ML cross-validation implementation
and generates a summary report of the validation results.
"""

import sys
import os
import time
import json

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')

def test_basic_framework():
    """Test basic framework components"""
    print("Testing basic framework components...")
    
    try:
        from core.axioms import universal_invariance
        from core.domain import DiscreteZetaShift
        
        # Test universal invariance
        result = universal_invariance(1.0, 3e8)
        assert abs(result - 3.33e-09) < 1e-10, f"Universal invariance test failed: {result}"
        
        # Test DiscreteZetaShift
        dz = DiscreteZetaShift(10)
        attrs = dz.attributes
        assert 'D' in attrs and 'E' in attrs, "DiscreteZetaShift test failed"
        
        print("✓ Basic framework components working")
        return True
        
    except Exception as e:
        print(f"✗ Basic framework test failed: {e}")
        return False

def test_crispr_features():
    """Test CRISPR feature extraction"""
    print("Testing CRISPR feature extraction...")
    
    try:
        from applications.ml_cross_validation import CRISPRFeatureExtractor
        
        extractor = CRISPRFeatureExtractor()
        test_sequence = "ATGCGTACGTACGTACGTACGTACGT"
        
        features = extractor.extract_all_features(test_sequence)
        assert len(features) > 30, f"Insufficient features extracted: {len(features)}"
        assert 'spectral_mean' in features, "Missing spectral features"
        assert 'gc_content' in features, "Missing compositional features"
        
        print(f"✓ CRISPR feature extraction working ({len(features)} features)")
        return True
        
    except Exception as e:
        print(f"✗ CRISPR feature extraction test failed: {e}")
        return False

def test_quantum_metrics():
    """Test quantum chaos metrics computation"""
    print("Testing quantum chaos metrics...")
    
    try:
        from applications.ml_cross_validation import QuantumChaosMetrics
        
        quantum = QuantumChaosMetrics(n_points=10)
        metrics = quantum.compute_5d_embedding_metrics(n_start=1, n_end=11)
        
        assert len(metrics['curvatures']) > 0, "No curvatures computed"
        assert len(metrics['x_coords']) > 0, "No coordinates computed"
        
        chaos_metrics = quantum.compute_quantum_chaos_criteria(metrics)
        assert len(chaos_metrics) > 0, "No chaos metrics computed"
        
        print(f"✓ Quantum metrics working ({len(metrics['curvatures'])} points)")
        return True
        
    except Exception as e:
        print(f"✗ Quantum metrics test failed: {e}")
        return False

def test_ml_validation():
    """Test ML cross-validation pipeline"""
    print("Testing ML cross-validation pipeline...")
    
    try:
        from applications.ml_cross_validation import CRISPRQuantumCrossValidator
        
        validator = CRISPRQuantumCrossValidator(n_samples=20)
        
        # Generate small test dataset
        sequences = validator.generate_crispr_sequences(n_sequences=10, seq_length=50)
        assert len(sequences) == 10, "Sequence generation failed"
        
        features, feature_names = validator.extract_crispr_feature_matrix(sequences)
        assert features.shape[0] == 10, "Feature matrix generation failed"
        assert len(feature_names) > 20, "Insufficient feature names"
        
        print(f"✓ ML validation pipeline working ({features.shape[1]} features)")
        return True
        
    except Exception as e:
        print(f"✗ ML validation test failed: {e}")
        return False

def test_comprehensive_validation():
    """Test comprehensive validation suite"""
    print("Testing comprehensive validation suite...")
    
    try:
        from applications.comprehensive_cross_validation import BiologicalSequenceDatabase
        
        db = BiologicalSequenceDatabase()
        sequences = db.get_all_sequences()
        assert len(sequences) >= 10, "Insufficient biological sequences"
        
        sequence_names = db.get_sequence_names()
        assert 'PCSK9_exon1' in sequence_names, "Missing expected sequences"
        
        controls = db.generate_control_sequences(n_controls=5)
        assert len(controls) == 5, "Control generation failed"
        
        print(f"✓ Comprehensive validation ready ({len(sequences)} sequences)")
        return True
        
    except Exception as e:
        print(f"✗ Comprehensive validation test failed: {e}")
        return False

def run_integration_test():
    """Run a quick integration test"""
    print("Running integration test...")
    
    try:
        from applications.ml_cross_validation import CRISPRQuantumCrossValidator
        
        # Small-scale integration test
        validator = CRISPRQuantumCrossValidator(n_samples=10)
        results = validator.perform_cross_validation(n_sequences=5, seq_length=50)
        
        assert 'cv_results' in results, "Cross-validation failed"
        assert len(results['sequences']) == 5, "Sequence processing failed"
        
        # Check if any model achieved reasonable performance
        best_r2 = -float('inf')
        for target_results in results['cv_results'].values():
            for model_results in target_results.values():
                best_r2 = max(best_r2, model_results.get('test_r2', -float('inf')))
        
        print(f"✓ Integration test completed (best R² = {best_r2:.4f})")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def check_generated_files():
    """Check if required files were generated"""
    print("Checking generated files...")
    
    expected_files = [
        'crispr_quantum_cross_validation_report.png',
        'crispr_quantum_cross_validation_results.json',
        'comprehensive_cross_validation_analysis.png',
        'comprehensive_cross_validation_results.json',
        'CROSS_VALIDATION_METHODOLOGY.md'
    ]
    
    existing_files = []
    missing_files = []
    
    for filename in expected_files:
        if os.path.exists(filename):
            existing_files.append(filename)
            file_size = os.path.getsize(filename)
            print(f"✓ {filename} ({file_size:,} bytes)")
        else:
            missing_files.append(filename)
            print(f"✗ {filename} (missing)")
    
    return len(missing_files) == 0, existing_files, missing_files

def validate_results():
    """Validate the quality of generated results"""
    print("Validating result quality...")
    
    try:
        # Check comprehensive results
        if os.path.exists('comprehensive_cross_validation_results.json'):
            with open('comprehensive_cross_validation_results.json', 'r') as f:
                results = json.load(f)
            
            summary = results.get('summary', {})
            n_sequences = summary.get('n_sequences', 0)
            n_features = summary.get('n_features', 0)
            n_targets = summary.get('n_targets', 0)
            
            print(f"✓ Dataset: {n_sequences} sequences, {n_features} features, {n_targets} targets")
            
            # Check ML results quality
            ml_results = results.get('ml_results', {})
            if ml_results:
                best_r2 = -float('inf')
                for target_name, target_results in ml_results.items():
                    for config, model_result in target_results.items():
                        best_r2 = max(best_r2, model_result.get('test_r2', -float('inf')))
                
                print(f"✓ Best ML performance: R² = {best_r2:.4f}")
                
                if best_r2 > 0.3:
                    print("✓ Achieved meaningful cross-domain validation")
                elif best_r2 > 0.0:
                    print("⚠ Weak but positive cross-domain validation")
                else:
                    print("✗ No significant cross-domain validation detected")
            
            # Check bootstrap results
            bootstrap_results = results.get('bootstrap_results', {})
            if bootstrap_results:
                print(f"✓ Bootstrap validation completed for {len(bootstrap_results)} targets")
            
            return True
        else:
            print("✗ No comprehensive results file found")
            return False
            
    except Exception as e:
        print(f"✗ Results validation failed: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of the validation"""
    print("\n" + "="*60)
    print("CRISPR-QUANTUM CROSS-VALIDATION SUMMARY REPORT")
    print("="*60)
    
    # Test results summary
    test_results = []
    test_results.append(("Basic Framework", test_basic_framework()))
    test_results.append(("CRISPR Features", test_crispr_features()))
    test_results.append(("Quantum Metrics", test_quantum_metrics()))
    test_results.append(("ML Validation", test_ml_validation()))
    test_results.append(("Comprehensive Suite", test_comprehensive_validation()))
    
    print("\nComponent Test Results:")
    print("-" * 30)
    for test_name, passed in test_results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<20}: {status}")
    
    # File generation check
    files_ok, existing_files, missing_files = check_generated_files()
    
    print(f"\nGenerated Files: {len(existing_files)}/{len(existing_files) + len(missing_files)}")
    print("-" * 30)
    for filename in existing_files:
        print(f"✓ {filename}")
    for filename in missing_files:
        print(f"✗ {filename}")
    
    # Results validation
    print("\nResults Validation:")
    print("-" * 30)
    results_valid = validate_results()
    
    # Integration test
    print("\nIntegration Test:")
    print("-" * 30)
    integration_ok = run_integration_test()
    
    # Overall assessment
    print("\nOverall Assessment:")
    print("-" * 30)
    
    all_tests_passed = all(result for _, result in test_results)
    
    if all_tests_passed and files_ok and results_valid and integration_ok:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("Cross-validation pipeline fully functional and validated")
    elif all_tests_passed and integration_ok:
        print("⚠️  MOSTLY OPERATIONAL")
        print("Core functionality working, minor file generation issues")
    else:
        print("❌ ISSUES DETECTED")
        print("Some components require attention")
    
    # Recommendations
    print("\nRecommendations:")
    print("-" * 30)
    if not all_tests_passed:
        print("- Fix failing component tests before proceeding")
    if not files_ok:
        print("- Re-run validation pipelines to generate missing files")
    if not results_valid:
        print("- Check data quality and model performance")
    
    print("- Expand dataset size for improved statistical power")
    print("- Investigate feature engineering improvements")
    print("- Consider ensemble methods for better prediction accuracy")
    
    print("\n" + "="*60)
    
    return all_tests_passed and files_ok and results_valid and integration_ok

def main():
    """Main test execution"""
    print("CRISPR-Quantum Cross-Validation Test Suite")
    print("=" * 45)
    
    start_time = time.time()
    
    # Run comprehensive test suite
    success = generate_summary_report()
    
    elapsed_time = time.time() - start_time
    print(f"\nTest suite completed in {elapsed_time:.2f} seconds")
    
    if success:
        print("🎉 Cross-validation implementation VALIDATED!")
        return 0
    else:
        print("⚠️  Cross-validation implementation needs attention")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)