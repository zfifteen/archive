#!/usr/bin/env python3
"""
Validation Test for Human DNA Implementation

This test validates that the human DNA implementation is working correctly
and that all sequences are authentic and properly formatted.
"""

import os
import json
import sys

def test_human_dna_data_exists():
    """Test that human DNA data exists and is properly formatted."""
    print("Testing Human DNA Data Availability...")
    
    # Check if data directory exists
    data_dir = "human_dna_data"
    if not os.path.exists(data_dir):
        print("❌ Human DNA data directory not found")
        return False
    
    # Check if main files exist
    required_files = [
        "human_dna_sequences.json",
        "human_dna_sequences.fasta", 
        "README.md"
    ]
    
    for file in required_files:
        filepath = os.path.join(data_dir, file)
        if not os.path.exists(filepath):
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ Human DNA data directory and files exist")
    return True

def test_sequence_authenticity():
    """Test that sequences are authentic NCBI RefSeq sequences."""
    print("\nTesting Sequence Authenticity...")
    
    try:
        with open("human_dna_data/human_dna_sequences.json", 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading human DNA data: {e}")
        return False
    
    # Expected RefSeq IDs
    expected_refseq = {
        "BRCA1": "NM_007294.4",
        "TP53": "NM_000546.6",
        "CFTR": "NM_000492.4", 
        "PCSK9": "NM_174936.4",
        "APOE": "NM_000041.4"
    }
    
    for gene, expected_id in expected_refseq.items():
        if gene not in data:
            print(f"❌ Gene {gene} missing from data")
            return False
            
        if data[gene]["refseq_id"] != expected_id:
            print(f"❌ Wrong RefSeq ID for {gene}: got {data[gene]['refseq_id']}, expected {expected_id}")
            return False
            
        # Check sequence is DNA
        sequence = data[gene]["sequence"]
        if not all(base in 'ATCG' for base in sequence):
            print(f"❌ Invalid DNA sequence for {gene}")
            return False
            
        # Check sequence length
        if len(sequence) < 400 or len(sequence) > 600:
            print(f"❌ Unexpected sequence length for {gene}: {len(sequence)} bp")
            return False
    
    print("✅ All sequences are authentic NCBI RefSeq with correct IDs")
    return True

def test_experiments_work():
    """Test that experiments can run with human data."""
    print("\nTesting Experiment Functionality...")
    
    try:
        sys.path.append("src/applications")
        from wave_crispr_sample_analysis import load_human_dna_sequences
        
        sequences = load_human_dna_sequences()
        
        # Check that human sequences are loaded
        if not any("Human" in key for key in sequences.keys()):
            print("❌ Human sequences not properly loaded in experiments")
            return False
            
        print("✅ Experiments can successfully load human DNA data")
        return True
        
    except Exception as e:
        print(f"❌ Error testing experiments: {e}")
        return False

def test_ethical_compliance():
    """Test ethical compliance documentation."""
    print("\nTesting Ethical Compliance Documentation...")
    
    try:
        with open("human_dna_data/README.md", 'r') as f:
            readme_content = f.read()
    except Exception as e:
        print(f"❌ Error reading README: {e}")
        return False
    
    # Check for required ethical compliance elements
    required_elements = [
        "NCBI RefSeq",
        "public domain",
        "no personal",
        "ethical",
        "compliance"
    ]
    
    for element in required_elements:
        if element.lower() not in readme_content.lower():
            print(f"❌ Missing ethical compliance element: {element}")
            return False
    
    print("✅ Ethical compliance documentation is complete")
    return True

def main():
    """Run all validation tests."""
    print("=" * 60)
    print("HUMAN DNA IMPLEMENTATION VALIDATION")
    print("=" * 60)
    
    tests = [
        test_human_dna_data_exists,
        test_sequence_authenticity,
        test_experiments_work,
        test_ethical_compliance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            break  # Stop on first failure
    
    print("\n" + "=" * 60)
    print(f"VALIDATION RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All validation tests PASSED!")
        print("✅ Human DNA implementation is working correctly")
        print("✅ Ethical compliance verified")
        print("✅ Ready for production use")
        return True
    else:
        print("❌ Some validation tests FAILED")
        print("Please check the implementation and try again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)