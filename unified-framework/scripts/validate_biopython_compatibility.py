#!/usr/bin/env python3
"""
BioPython Compatibility Validation Script

This script validates BioPython compatibility with the Z Framework codebase,
ensuring all BioPython functionality works correctly with the current Python
and BioPython versions.

Usage:
    python3 scripts/validate_biopython_compatibility.py
"""

import sys
import os
import traceback
import tempfile
from pathlib import Path
from typing import List, Dict, Any


def check_python_version() -> Dict[str, Any]:
    """Check Python version compatibility."""
    version = sys.version_info
    result = {
        'python_version': f"{version.major}.{version.minor}.{version.micro}",
        'major': version.major,
        'minor': version.minor,
        'micro': version.micro,
        'compatible': True,
        'issues': []
    }
    
    if version.major != 3:
        result['compatible'] = False
        result['issues'].append("Python 3.x required")
    
    if version.minor < 8:
        result['compatible'] = False
        result['issues'].append("Python 3.8+ required")
    
    if version >= (3, 13):
        result['issues'].append("Python 3.13+ may have BioPython C API compatibility issues")
    
    return result


def check_biopython_version() -> Dict[str, Any]:
    """Check BioPython version and import capability."""
    result = {
        'installed': False,
        'version': None,
        'compatible': False,
        'issues': []
    }
    
    try:
        import Bio
        result['installed'] = True
        result['version'] = Bio.__version__
        
        # Check version compatibility
        version_parts = Bio.__version__.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        
        if major >= 1 and minor >= 83:
            result['compatible'] = True
        else:
            result['issues'].append(f"BioPython {Bio.__version__} < 1.83 may have compatibility issues")
            
    except ImportError as e:
        result['issues'].append(f"BioPython not installed: {e}")
    except Exception as e:
        result['issues'].append(f"Error checking BioPython version: {e}")
    
    return result


def test_basic_bio_functionality() -> Dict[str, Any]:
    """Test basic BioPython functionality."""
    tests = []
    
    # Test Bio.Seq
    try:
        from Bio.Seq import Seq
        seq = Seq("ATGCGATCG")
        complement = seq.complement()
        reverse_complement = seq.reverse_complement()
        tests.append({
            'name': 'Bio.Seq basic operations',
            'passed': True,
            'details': f'Sequence: {seq}, Complement: {complement}, RC: {reverse_complement}'
        })
    except Exception as e:
        tests.append({
            'name': 'Bio.Seq basic operations', 
            'passed': False,
            'error': str(e)
        })
    
    # Test Bio.SeqIO
    try:
        from Bio import SeqIO
        from io import StringIO
        fasta_data = '>test\nATGCGATCG\n'
        records = list(SeqIO.parse(StringIO(fasta_data), 'fasta'))
        tests.append({
            'name': 'Bio.SeqIO parsing',
            'passed': len(records) == 1,
            'details': f'Parsed {len(records)} records'
        })
    except Exception as e:
        tests.append({
            'name': 'Bio.SeqIO parsing',
            'passed': False,
            'error': str(e)
        })
    
    # Test Bio.SeqFeature
    try:
        from Bio.SeqFeature import FeatureLocation
        location = FeatureLocation(10, 50, strand=1)
        tests.append({
            'name': 'Bio.SeqFeature',
            'passed': True,
            'details': f'Created location: {location}'
        })
    except Exception as e:
        tests.append({
            'name': 'Bio.SeqFeature',
            'passed': False,
            'error': str(e)
        })
    
    # Test Bio.Entrez (import only, no network requests)
    try:
        from Bio import Entrez
        Entrez.email = "test@example.com"
        tests.append({
            'name': 'Bio.Entrez import',
            'passed': True,
            'details': 'Successfully imported and configured'
        })
    except Exception as e:
        tests.append({
            'name': 'Bio.Entrez import',
            'passed': False,
            'error': str(e)
        })
    
    return {
        'tests': tests,
        'total': len(tests),
        'passed': sum(1 for t in tests if t['passed']),
        'failed': sum(1 for t in tests if not t['passed'])
    }


def test_framework_integration() -> Dict[str, Any]:
    """Test BioPython integration with Z Framework components."""
    tests = []
    
    # Test ZGeodesicHotspotMapper
    try:
        sys.path.append('.')
        from src.Bio.QuantumTopology.geodesic_hotspot_mapper import ZGeodesicHotspotMapper
        from Bio.Seq import Seq
        
        mapper = ZGeodesicHotspotMapper()
        test_seq = Seq("ATGCGATCGATCGTAGCGATCGTAGCGATCG")
        
        # Test coordinate computation
        coordinates = mapper.compute_z_invariant_coordinates(test_seq)
        
        # Test hotspot detection
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        tests.append({
            'name': 'ZGeodesicHotspotMapper integration',
            'passed': True,
            'details': f'Processed sequence length {len(test_seq)}, found {hotspots["total_hotspots"]} hotspots'
        })
    except Exception as e:
        tests.append({
            'name': 'ZGeodesicHotspotMapper integration',
            'passed': False,
            'error': str(e)
        })
    
    # Test FASTA file operations
    try:
        from src.Bio.QuantumTopology.geodesic_hotspot_mapper import ZGeodesicHotspotMapper
        
        # Create temporary FASTA file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">test_seq1\nATGCGATCGATCGTAGCGATCGTAGCGATCG\n")
            f.write(">test_seq2\nTTTGGGCCCAAATTTGGGCCCAAAT\n")
            fasta_path = f.name
        
        mapper = ZGeodesicHotspotMapper()
        sequences = mapper.load_fasta(fasta_path)
        
        # Cleanup
        os.unlink(fasta_path)
        
        tests.append({
            'name': 'FASTA file operations',
            'passed': len(sequences) == 2,
            'details': f'Loaded {len(sequences)} sequences from FASTA'
        })
    except Exception as e:
        tests.append({
            'name': 'FASTA file operations',
            'passed': False,
            'error': str(e)
        })
    
    return {
        'tests': tests,
        'total': len(tests),
        'passed': sum(1 for t in tests if t['passed']),
        'failed': sum(1 for t in tests if not t['passed'])
    }


def test_sample_data_compatibility() -> Dict[str, Any]:
    """Test BioPython with existing sample data files."""
    tests = []
    
    # Test sample_sequences.fasta if it exists
    sample_fasta = Path('sample_sequences.fasta')
    if sample_fasta.exists():
        try:
            from Bio import SeqIO
            sequences = list(SeqIO.parse(sample_fasta, 'fasta'))
            tests.append({
                'name': 'sample_sequences.fasta parsing',
                'passed': len(sequences) > 0,
                'details': f'Successfully parsed {len(sequences)} sequences'
            })
        except Exception as e:
            tests.append({
                'name': 'sample_sequences.fasta parsing',
                'passed': False,
                'error': str(e)
            })
    else:
        tests.append({
            'name': 'sample_sequences.fasta parsing',
            'passed': True,
            'details': 'File not found (optional test)'
        })
    
    return {
        'tests': tests,
        'total': len(tests),
        'passed': sum(1 for t in tests if t['passed']),
        'failed': sum(1 for t in tests if not t['passed'])
    }


def generate_recommendations(python_check: Dict, biopython_check: Dict, 
                           basic_tests: Dict, integration_tests: Dict) -> List[str]:
    """Generate recommendations based on test results."""
    recommendations = []
    
    # Python version recommendations
    if python_check['major'] >= 3 and python_check['minor'] >= 13:
        recommendations.append(
            "⚠️  Python 3.13+ detected. Consider using Python 3.8-3.12 for better BioPython compatibility."
        )
    
    # BioPython version recommendations
    if not biopython_check['installed']:
        recommendations.append(
            "❌ BioPython not installed. Run: pip install 'biopython>=1.83,<2.0'"
        )
    elif not biopython_check['compatible']:
        recommendations.append(
            f"⚠️  BioPython {biopython_check['version']} may have compatibility issues. "
            "Consider upgrading to version 1.83 or later."
        )
    
    # Test failure recommendations
    if basic_tests['failed'] > 0:
        recommendations.append(
            "❌ Basic BioPython functionality tests failed. Check BioPython installation."
        )
    
    if integration_tests['failed'] > 0:
        recommendations.append(
            "❌ Framework integration tests failed. Check Z Framework dependencies."
        )
    
    # Success recommendations
    if (biopython_check['compatible'] and basic_tests['failed'] == 0 and 
        integration_tests['failed'] == 0):
        recommendations.append(
            "✅ All BioPython compatibility tests passed. Configuration is optimal."
        )
    
    return recommendations


def main():
    """Main validation function."""
    print("=" * 80)
    print("BioPython Compatibility Validation for Z Framework")
    print("=" * 80)
    
    # Check Python version
    print("\n🐍 Python Version Check")
    print("-" * 40)
    python_check = check_python_version()
    print(f"Python version: {python_check['python_version']}")
    if python_check['issues']:
        for issue in python_check['issues']:
            print(f"⚠️  {issue}")
    else:
        print("✅ Python version compatible")
    
    # Check BioPython version
    print("\n🧬 BioPython Version Check")
    print("-" * 40)
    biopython_check = check_biopython_version()
    if biopython_check['installed']:
        print(f"BioPython version: {biopython_check['version']}")
        if biopython_check['compatible']:
            print("✅ BioPython version compatible")
        else:
            for issue in biopython_check['issues']:
                print(f"⚠️  {issue}")
    else:
        print("❌ BioPython not installed")
        for issue in biopython_check['issues']:
            print(f"   {issue}")
    
    # Test basic functionality
    print("\n🧪 Basic BioPython Functionality Tests")
    print("-" * 40)
    basic_tests = test_basic_bio_functionality()
    for test in basic_tests['tests']:
        status = "✅" if test['passed'] else "❌"
        print(f"{status} {test['name']}")
        if test['passed'] and 'details' in test:
            print(f"   Details: {test['details']}")
        elif not test['passed'] and 'error' in test:
            print(f"   Error: {test['error']}")
    
    print(f"\nBasic tests: {basic_tests['passed']}/{basic_tests['total']} passed")
    
    # Test framework integration
    print("\n🔧 Framework Integration Tests")
    print("-" * 40)
    integration_tests = test_framework_integration()
    for test in integration_tests['tests']:
        status = "✅" if test['passed'] else "❌"
        print(f"{status} {test['name']}")
        if test['passed'] and 'details' in test:
            print(f"   Details: {test['details']}")
        elif not test['passed'] and 'error' in test:
            print(f"   Error: {test['error']}")
    
    print(f"\nIntegration tests: {integration_tests['passed']}/{integration_tests['total']} passed")
    
    # Test sample data compatibility
    print("\n📁 Sample Data Compatibility Tests")
    print("-" * 40)
    sample_tests = test_sample_data_compatibility()
    for test in sample_tests['tests']:
        status = "✅" if test['passed'] else "❌"
        print(f"{status} {test['name']}")
        if 'details' in test:
            print(f"   Details: {test['details']}")
        elif 'error' in test:
            print(f"   Error: {test['error']}")
    
    # Generate recommendations
    print("\n💡 Recommendations")
    print("-" * 40)
    recommendations = generate_recommendations(
        python_check, biopython_check, basic_tests, integration_tests
    )
    for rec in recommendations:
        print(f"   {rec}")
    
    # Overall summary
    print("\n📊 Summary")
    print("-" * 40)
    total_tests = basic_tests['total'] + integration_tests['total'] + sample_tests['total']
    total_passed = basic_tests['passed'] + integration_tests['passed'] + sample_tests['passed']
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {total_passed}")
    print(f"Tests failed: {total_tests - total_passed}")
    print(f"Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests and biopython_check['compatible']:
        print("\n🎉 All compatibility checks passed!")
        return 0
    else:
        print("\n⚠️  Some compatibility issues detected. See recommendations above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())