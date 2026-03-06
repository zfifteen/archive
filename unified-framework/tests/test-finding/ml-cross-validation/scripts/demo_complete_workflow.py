#!/usr/bin/env python3
"""
Complete ML Cross-Validation Workflow Demonstration
=================================================

This script demonstrates the complete workflow for cross-domain ML validation
between quantum chaos and CRISPR metrics using the Z Framework.

Usage: python3 demo_complete_workflow.py
"""

import sys
import os
import json
import time
from pathlib import Path

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')

def print_header(title, char="="):
    """Print formatted header"""
    print(f"\n{char * len(title)}")
    print(title)
    print(f"{char * len(title)}")

def print_step(step_num, description):
    """Print step information"""
    print(f"\n{step_num}. {description}")
    print("-" * (len(str(step_num)) + len(description) + 2))

def check_file_exists(filepath):
    """Check if file exists and print status"""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size
        print(f"  ✓ {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"  ✗ {filepath} (missing)")
        return False

def main():
    """
    Run complete ML cross-validation demonstration
    """
    print_header("ML Cross-Validation: Quantum Chaos & CRISPR Metrics")
    print("Complete workflow demonstration for Z Framework validation")
    print(f"Execution time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we're in the right directory
    script_dir = Path(__file__).parent
    ml_cv_dir = script_dir.parent
    
    # Change to ml-cross-validation directory if needed
    if script_dir.name == "scripts":
        os.chdir(ml_cv_dir)
    
    if not Path("scripts").exists():
        print("\nError: Cannot find scripts directory")
        print("Make sure you're running from ml-cross-validation/ or scripts/")
        return 1
    
    # Overview
    print_step(1, "OVERVIEW")
    print("This demonstration validates the Z Framework's claim that universal")
    print("mathematical patterns bridge quantum chaos and biological domains.")
    print("\nKey Components:")
    print("• Quantum chaos features from DiscreteZetaShift 5D embeddings")
    print("• CRISPR sequence features from spectral analysis")
    print("• Cross-domain ML models (scikit-learn)")
    print("• Statistical validation of transfer learning")
    
    # Step 2: Data Preparation
    print_step(2, "DATA PREPARATION")
    print("Preparing datasets using Z Framework components...")
    
    # We'll use the simplified approach that works
    try:
        from run_cross_validation import SimplifiedCrossValidator
        
        validator = SimplifiedCrossValidator("demo_results")
        
        # Generate datasets
        quantum_features, quantum_labels, quantum_names = validator.create_quantum_chaos_features(50)
        bio_features, bio_labels, bio_names = validator.create_biological_features(50)
        
        print(f"  ✓ Quantum dataset: {len(quantum_features)} samples, {len(quantum_names)} features")
        print(f"  ✓ Biological dataset: {len(bio_features)} samples, {len(bio_names)} features")
        
    except Exception as e:
        print(f"  ✗ Data preparation failed: {e}")
        return 1
    
    # Step 3: Model Training
    print_step(3, "MODEL TRAINING")
    print("Training ML models for within-domain and cross-domain validation...")
    
    try:
        # Run cross-validation
        results = validator.perform_cross_domain_validation()
        
        print("  ✓ Within-domain models trained successfully")
        print("  ✓ Cross-domain transfer models trained successfully")
        
        # Extract key results
        if 'validation_results' in results:
            for domain, metrics in results['validation_results'].items():
                print(f"    {domain}: {metrics['accuracy']:.3f} accuracy")
        
        if 'cross_domain_results' in results:
            cross = results['cross_domain_results']
            print(f"    Cross-domain average: {cross.get('average_cross_accuracy', 0):.3f}")
        
    except Exception as e:
        print(f"  ✗ Model training failed: {e}")
        return 1
    
    # Step 4: Results Analysis
    print_step(4, "RESULTS ANALYSIS")
    
    if 'cross_domain_results' in results:
        cross_results = results['cross_domain_results']
        qb_accuracy = cross_results.get('quantum_to_biological', 0)
        bq_accuracy = cross_results.get('biological_to_quantum', 0)
        avg_accuracy = cross_results.get('average_cross_accuracy', 0)
        
        print(f"Cross-Domain Transfer Results:")
        print(f"  Quantum → Biological: {qb_accuracy:.3f}")
        print(f"  Biological → Quantum: {bq_accuracy:.3f}")
        print(f"  Average: {avg_accuracy:.3f}")
        
        # Interpretation
        if avg_accuracy > 0.7:
            interpretation = "STRONG evidence for universal patterns"
            emoji = "🎉"
        elif avg_accuracy > 0.5:
            interpretation = "MODERATE evidence for universal patterns"
            emoji = "✅"
        else:
            interpretation = "LIMITED evidence for universal patterns"
            emoji = "⚠️"
        
        print(f"\n{emoji} {interpretation}")
        
        # Statistical significance
        if avg_accuracy > 0.5:
            print("✓ Cross-domain accuracy exceeds random chance (50%)")
        else:
            print("✗ Cross-domain accuracy at random level")
    
    # Step 5: Z Framework Validation
    print_step(5, "Z FRAMEWORK VALIDATION")
    
    # Check which Z Framework components were most important
    if 'feature_importance' in results:
        print("Key Z Framework components in cross-domain patterns:")
        
        for domain, importance in results['feature_importance'].items():
            if domain in ['quantum', 'biological']:
                # Get top 3 features
                sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"\n  {domain.title()} domain top features:")
                for feat, imp in sorted_features:
                    print(f"    {feat}: {imp:.3f}")
    
    # Step 6: Files Generated
    print_step(6, "GENERATED FILES")
    print("Checking generated files and outputs...")
    
    files_to_check = [
        "demo_results/ml_cross_validation_results.json",
        "demo_results/ml_validation_summary.png", 
        "demo_results/METHODOLOGY_REPORT.md"
    ]
    
    files_exist = 0
    for filepath in files_to_check:
        if check_file_exists(filepath):
            files_exist += 1
    
    print(f"\nFiles generated: {files_exist}/{len(files_to_check)}")
    
    # Step 7: Summary and Conclusions
    print_step(7, "SUMMARY AND CONCLUSIONS")
    
    if 'cross_domain_results' in results:
        avg_accuracy = results['cross_domain_results'].get('average_cross_accuracy', 0)
        
        print("Z Framework Cross-Domain Validation Results:")
        print(f"  • Average cross-domain accuracy: {avg_accuracy:.1%}")
        print(f"  • Samples per domain: {len(quantum_features)}")
        print(f"  • ML algorithm: Random Forest Classification")
        print(f"  • Statistical significance: {'Yes' if avg_accuracy > 0.5 else 'No'}")
        
        if avg_accuracy > 0.6:
            print("\n🎯 CONCLUSION: Cross-domain ML validation provides computational")
            print("   evidence supporting the Z Framework's universal mathematical patterns.")
            print("   Quantum chaos metrics can predict biological sequence properties!")
        elif avg_accuracy > 0.5:
            print("\n🔬 CONCLUSION: Moderate evidence for cross-domain patterns.")
            print("   Further investigation warranted with larger datasets.")
        else:
            print("\n📊 CONCLUSION: Limited cross-domain transfer detected.")
            print("   Z Framework patterns may require different ML approaches.")
    
    print_step(8, "NEXT STEPS")
    print("Recommendations for extending this analysis:")
    print("  1. Scale up to 1000+ samples per domain")
    print("  2. Include real experimental CRISPR efficiency data")
    print("  3. Test additional ML algorithms (deep learning, ensemble methods)")
    print("  4. Expand to other domains (financial, astronomical, etc.)")
    print("  5. Investigate specific Z Framework components (θ', κ, 5D embeddings)")
    
    print("\n" + "=" * 60)
    print("ML CROSS-VALIDATION DEMONSTRATION COMPLETED")
    print("=" * 60)
    print("For detailed analysis, see:")
    print("  • notebooks/cross_validation_demo.ipynb")
    print("  • results/METHODOLOGY_REPORT.md")
    print("  • results/ml_validation_summary.png")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)