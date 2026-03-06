#!/usr/bin/env python3
"""
Test for the Automated Claim-Evidence Linking System

This test validates the functionality of the claim-evidence linking system
by creating sample claims and evidence, then testing the linking process.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the repository root to the Python path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from src.validation.claim_evidence_linking import (
    ClaimEvidenceLinkingSystem, 
    ClaimExtractor, 
    EvidenceParser, 
    SemanticMatcher,
    Claim,
    Evidence
)

def create_sample_documentation():
    """Create sample documentation with claims."""
    doc_content = """# Z Framework Validation Report

## Performance Claims

The Z5D algorithm demonstrates exceptional performance with over 99% accuracy in prime number identification.
Our implementation efficiently processes large datasets with minimal computational overhead.
The validation framework proves the correctness of our mathematical approach through rigorous testing.

## Technical Specifications

The system validates complex mathematical properties using advanced numerical methods.
Performance benchmarks show convergence within acceptable error tolerances.
Our algorithm demonstrates robust stability across different input ranges.

## Test Results

Comprehensive testing confirms the reliability of our implementation.
The framework successfully handles edge cases and boundary conditions.
Validation results prove the mathematical soundness of our approach.
"""
    return doc_content

def create_sample_test_results():
    """Create sample test result data."""
    test_results = [
        {
            "name": "TC01_prime_identification",
            "accuracy": 0.995,
            "precision": 0.992,
            "runtime": 2.34,
            "status": "pass",
            "success": True
        },
        {
            "name": "TC02_performance_benchmark",
            "performance": 0.987,
            "cpu_time": 1.56,
            "memory_usage": 45.2,
            "status": "pass",
            "success": True
        },
        {
            "name": "TC-LET-01-03_convergence_test",
            "convergence": True,
            "error_rate": 0.001,
            "stability": 0.998,
            "status": "pass",
            "success": True
        },
        {
            "name": "test_mathematical_validation",
            "accuracy": 0.999,
            "correctness": True,
            "status": "pass",
            "success": True
        },
        {
            "name": "TC05_edge_case_handling",
            "robustness": 0.994,
            "edge_case_success": 47,
            "total_edge_cases": 50,
            "status": "pass",
            "success": True
        }
    ]
    return test_results

def test_claim_extraction():
    """Test claim extraction functionality."""
    print("Testing claim extraction...")
    
    extractor = ClaimExtractor()
    
    # Create temporary documentation file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(create_sample_documentation())
        doc_file = f.name
    
    try:
        claims = extractor.extract_claims_from_file(doc_file)
        
        assert len(claims) > 0, "No claims extracted"
        assert all(claim.confidence > 0 for claim in claims), "Claims should have confidence scores"
        assert all(len(claim.keywords) > 0 for claim in claims), "Claims should have keywords"
        
        print(f"✅ Successfully extracted {len(claims)} claims")
        
        # Print sample claims for verification
        for i, claim in enumerate(claims[:3]):
            print(f"  Claim {i+1}: {claim.text[:60]}... (confidence: {claim.confidence:.3f})")
        
        return claims
        
    finally:
        os.unlink(doc_file)

def test_evidence_parsing():
    """Test evidence parsing functionality."""
    print("\nTesting evidence parsing...")
    
    parser = EvidenceParser()
    
    # Create temporary test results directory
    with tempfile.TemporaryDirectory() as temp_dir:
        results_file = Path(temp_dir) / "test_results.json"
        
        with open(results_file, 'w') as f:
            json.dump({"tests": create_sample_test_results()}, f)
        
        evidence_list = parser.parse_evidence_from_files(temp_dir)
        
        assert len(evidence_list) > 0, "No evidence parsed"
        assert all(ev.confidence > 0 for ev in evidence_list), "Evidence should have confidence scores"
        assert all(len(ev.metrics) > 0 for ev in evidence_list), "Evidence should have metrics"
        
        print(f"✅ Successfully parsed {len(evidence_list)} evidence items")
        
        # Print sample evidence for verification
        for i, evidence in enumerate(evidence_list[:3]):
            print(f"  Evidence {i+1}: {evidence.test_name} ({len(evidence.metrics)} metrics)")
        
        return evidence_list

def test_semantic_matching():
    """Test semantic matching functionality."""
    print("\nTesting semantic matching...")
    
    # Create sample claims and evidence
    claims = [
        Claim(
            id="claim_001",
            text="The Z5D algorithm demonstrates exceptional performance with over 99% accuracy",
            source="test_doc.md",
            line_number=1,
            confidence=0.8,
            keywords=["algorithm", "performance", "accuracy"]
        ),
        Claim(
            id="claim_002", 
            text="Our implementation efficiently processes large datasets with minimal computational overhead",
            source="test_doc.md",
            line_number=2,
            confidence=0.7,
            keywords=["implementation", "processes", "computational"]
        )
    ]
    
    evidence = [
        Evidence(
            id="evidence_TC01",
            test_name="TC01_prime_identification",
            metrics={"accuracy": 0.995, "precision": 0.992},
            status="pass",
            confidence=0.9,
            source_file="test_results.json"
        ),
        Evidence(
            id="evidence_TC02",
            test_name="TC02_performance_benchmark", 
            metrics={"performance": 0.987, "cpu_time": 1.56},
            status="pass",
            confidence=0.85,
            source_file="test_results.json"
        )
    ]
    
    matcher = SemanticMatcher()
    links = matcher.match_claims_to_evidence(claims, evidence)
    
    assert len(links) > 0, "No links created"
    assert all(link.similarity_score > 0 for link in links), "Links should have similarity scores"
    assert all(len(link.confidence_interval) == 2 for link in links), "Links should have confidence intervals"
    
    print(f"✅ Successfully created {len(links)} links")
    
    # Print sample links for verification
    for i, link in enumerate(links):
        print(f"  Link {i+1}: {link.claim_id} -> {link.evidence_id} "
              f"(similarity: {link.similarity_score:.3f}, status: {link.validation_status})")
    
    return links

def test_full_system():
    """Test the complete claim-evidence linking system."""
    print("\nTesting full system integration...")
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create documentation
        doc_file = temp_path / "README.md"
        with open(doc_file, 'w') as f:
            f.write(create_sample_documentation())
        
        # Create test results
        results_file = temp_path / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(create_sample_test_results(), f)
        
        # Initialize system
        system = ClaimEvidenceLinkingSystem(str(temp_path))
        
        # Run analysis
        matrix = system.run_analysis(quick_mode=True)
        
        assert len(matrix.claims) > 0, "No claims found in full system test"
        assert len(matrix.evidence) > 0, "No evidence found in full system test"
        assert matrix.statistics['total_links'] >= 0, "Statistics should be generated"
        
        # Save traceability matrix
        output_file = temp_path / "traceability_matrix.json"
        system.save_traceability_matrix(matrix, str(output_file))
        
        assert output_file.exists(), "Traceability matrix should be saved"
        
        # Verify saved file
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
        
        assert 'claims' in saved_data, "Saved file should contain claims"
        assert 'evidence' in saved_data, "Saved file should contain evidence"
        assert 'statistics' in saved_data, "Saved file should contain statistics"
        
        print(f"✅ Full system test completed successfully")
        print(f"  Claims: {len(matrix.claims)}")
        print(f"  Evidence: {len(matrix.evidence)}")
        print(f"  Links: {len(matrix.links)}")
        
        # Print summary
        system.print_summary(matrix)
        
        return matrix

def run_comprehensive_test():
    """Run all tests for the claim-evidence linking system."""
    print("🚀 Starting Claim-Evidence Linking System Tests")
    print("="*60)
    
    try:
        # Test individual components
        claims = test_claim_extraction()
        evidence = test_evidence_parsing()
        links = test_semantic_matching()
        
        # Test full system
        matrix = test_full_system()
        
        print("\n🎉 All tests PASSED!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function for running tests."""
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()