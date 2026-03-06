#!/usr/bin/env python3
"""
Knowledge Base Consolidation Verification Script

This script verifies that all the artifacts and documentation for Issue #671
have been properly created and are accessible.
"""

import os
import json
from pathlib import Path

def verify_consolidation():
    """Verify that all required artifacts from Issue #671 are present."""
    
    print("=" * 70)
    print("KNOWLEDGE BASE CONSOLIDATION VERIFICATION")
    print("Issue #671: Consolidate Empirical Insights and Thales Artifacts")
    print("=" * 70)
    
    verification_results = {
        'artifacts_present': {},
        'documentation_updated': {},
        'references_working': {},
        'overall_status': 'PENDING'
    }
    
    # Check 1: Primary Knowledge Base Entry
    print("\n1. Knowledge Base Entry Creation")
    print("-" * 40)
    
    kb_path = "docs/knowledge-base/empirical_insights.md"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            content = f.read()
            
        # Verify key sections are present
        required_sections = [
            "Empirical Results Tables",
            "Thales Geodesic Model Improvements", 
            "Validation Methodology",
            "Performance and Optimization Benchmarks",
            "Reproducibility Steps",
            "Artifact References"
        ]
        
        sections_found = []
        for section in required_sections:
            if section in content:
                sections_found.append(section)
                print(f"   ✅ {section}")
            else:
                print(f"   ❌ {section}")
        
        verification_results['artifacts_present']['empirical_insights_md'] = {
            'exists': True,
            'size_bytes': len(content),
            'sections_found': len(sections_found),
            'sections_required': len(required_sections),
            'complete': len(sections_found) == len(required_sections)
        }
        
        print(f"   📊 Sections: {len(sections_found)}/{len(required_sections)} complete")
        print(f"   📄 Size: {len(content)} characters")
        
    else:
        print(f"   ❌ Missing: {kb_path}")
        verification_results['artifacts_present']['empirical_insights_md'] = {'exists': False}
    
    # Check 2: Validation Artifacts
    print("\n2. Validation Artifacts")
    print("-" * 40)
    
    # thales_trials.json
    trials_path = "docs/validation/thales_trials.json"
    if os.path.exists(trials_path):
        try:
            with open(trials_path, 'r') as f:
                trials_data = json.load(f)
            
            total_trials = trials_data.get('verification_summary', {}).get('total_trials', 0)
            accuracy = trials_data.get('verification_summary', {}).get('accuracy_percentage', 0)
            
            print(f"   ✅ thales_trials.json - {total_trials} trials, {accuracy}% accuracy")
            
            verification_results['artifacts_present']['thales_trials_json'] = {
                'exists': True,
                'total_trials': total_trials,
                'accuracy': accuracy,
                'data_keys': len(trials_data)
            }
            
        except Exception as e:
            print(f"   ⚠️  thales_trials.json exists but invalid: {e}")
            verification_results['artifacts_present']['thales_trials_json'] = {
                'exists': True,
                'valid': False,
                'error': str(e)
            }
    else:
        print(f"   ❌ Missing: {trials_path}")
        verification_results['artifacts_present']['thales_trials_json'] = {'exists': False}
    
    # val_thales_geo.py
    val_script_path = "val_thales_geo.py"
    if os.path.exists(val_script_path):
        with open(val_script_path, 'r') as f:
            script_content = f.read()
        
        # Check for key functions
        key_functions = ['validate_thales_geodesic_enhancements', 'main']
        functions_found = sum(1 for func in key_functions if func in script_content)
        
        print(f"   ✅ val_thales_geo.py - {functions_found}/{len(key_functions)} key functions")
        
        verification_results['artifacts_present']['val_thales_geo_py'] = {
            'exists': True,
            'size_bytes': len(script_content),
            'functions_found': functions_found,
            'executable': os.access(val_script_path, os.X_OK)
        }
        
    else:
        print(f"   ❌ Missing: {val_script_path}")
        verification_results['artifacts_present']['val_thales_geo_py'] = {'exists': False}
    
    # Check 3: Documentation Updates
    print("\n3. Documentation Updates")
    print("-" * 40)
    
    # README.md update
    if os.path.exists("README.md"):
        with open("README.md", 'r') as f:
            readme_content = f.read()
        
        kb_referenced = "empirical_insights.md" in readme_content
        print(f"   {'✅' if kb_referenced else '❌'} README.md - Knowledge base {'referenced' if kb_referenced else 'not referenced'}")
        
        verification_results['documentation_updated']['readme_md'] = {
            'kb_referenced': kb_referenced
        }
    
    # Knowledge base README update
    kb_readme_path = "docs/knowledge-base/README.md"
    if os.path.exists(kb_readme_path):
        with open(kb_readme_path, 'r') as f:
            kb_readme_content = f.read()
        
        insights_referenced = "empirical_insights.md" in kb_readme_content
        print(f"   {'✅' if insights_referenced else '❌'} KB README - Empirical insights {'referenced' if insights_referenced else 'not referenced'}")
        
        verification_results['documentation_updated']['kb_readme_md'] = {
            'insights_referenced': insights_referenced
        }
    
    # Check 4: Existing Artifacts Referenced
    print("\n4. Existing Artifacts Accessibility")
    print("-" * 40)
    
    referenced_artifacts = [
        "THALES_THEOREM_IMPLEMENTATION_SUMMARY.md",
        "thales_verification_results_20250905_202111.json",
        "full_thales_verification.py",
        "validate_thales_claims.py",
        "demo_thales_verification.py",
        "scripts/demo_experiment.py"
    ]
    
    artifacts_accessible = 0
    for artifact in referenced_artifacts:
        if os.path.exists(artifact):
            print(f"   ✅ {artifact}")
            artifacts_accessible += 1
        else:
            print(f"   ❌ {artifact}")
    
    verification_results['references_working']['artifacts_accessible'] = artifacts_accessible
    verification_results['references_working']['artifacts_total'] = len(referenced_artifacts)
    
    print(f"   📊 Artifacts: {artifacts_accessible}/{len(referenced_artifacts)} accessible")
    
    # Overall Assessment
    print("\n" + "=" * 70)
    print("CONSOLIDATION VERIFICATION SUMMARY")
    print("=" * 70)
    
    # Calculate overall success
    kb_created = verification_results['artifacts_present'].get('empirical_insights_md', {}).get('complete', False)
    validation_artifacts = (
        verification_results['artifacts_present'].get('thales_trials_json', {}).get('exists', False) and
        verification_results['artifacts_present'].get('val_thales_geo_py', {}).get('exists', False)
    )
    docs_updated = (
        verification_results['documentation_updated'].get('readme_md', {}).get('kb_referenced', False) and
        verification_results['documentation_updated'].get('kb_readme_md', {}).get('insights_referenced', False)
    )
    artifacts_accessible_ratio = verification_results['references_working']['artifacts_accessible'] / verification_results['references_working']['artifacts_total']
    
    success_criteria = {
        'Knowledge Base Entry Complete': kb_created,
        'Validation Artifacts Created': validation_artifacts,
        'Documentation Updated': docs_updated,
        'Existing Artifacts Accessible': artifacts_accessible_ratio >= 0.8
    }
    
    all_success = all(success_criteria.values())
    
    for criterion, status in success_criteria.items():
        print(f"   {'✅' if status else '❌'} {criterion}")
    
    verification_results['overall_status'] = 'SUCCESS' if all_success else 'PARTIAL'
    
    print(f"\n   🎯 Overall Status: {'✅ CONSOLIDATION COMPLETE' if all_success else '⚠️  CONSOLIDATION PARTIAL'}")
    
    # Save verification results
    with open('kb_consolidation_verification.json', 'w') as f:
        json.dump(verification_results, f, indent=2)
    
    print(f"\n📁 Verification results saved to: kb_consolidation_verification.json")
    
    return verification_results

if __name__ == "__main__":
    results = verify_consolidation()
    exit_code = 0 if results['overall_status'] == 'SUCCESS' else 1
    exit(exit_code)