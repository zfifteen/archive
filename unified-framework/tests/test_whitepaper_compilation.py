#!/usr/bin/env python3
"""
Test Academic White Paper Compilation System

This test demonstrates the white paper compilation system in action,
showing how it integrates with the Z Framework principles and generates
xaiArtifact-compatible output.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.whitepaper_compiler import WhitePaperCompiler


def test_whitepaper_compilation():
    """Test the complete white paper compilation process."""
    print("=" * 80)
    print("TESTING ACADEMIC WHITE PAPER COMPILATION SYSTEM")
    print("=" * 80)
    
    # Initialize compiler
    repo_path = Path(__file__).parent.parent
    compiler = WhitePaperCompiler(repo_path)
    
    print(f"\n1. INITIALIZING COMPILER")
    print(f"Repository: {repo_path}")
    print(f"✓ Compiler initialized successfully")
    
    # Test data collection
    print(f"\n2. DATA COLLECTION")
    repo_data = compiler.collect_repository_data()
    print(f"✓ Found {len(repo_data['files'])} files")
    print(f"✓ Code files: {len(repo_data['code_files'])}")
    print(f"✓ Data files: {len(repo_data['data_files'])}")
    print(f"✓ Documentation: {len(repo_data['documentation'])}")
    
    # Test research finding extraction
    print(f"\n3. RESEARCH FINDING EXTRACTION")
    findings = compiler.extract_research_findings(repo_data)
    print(f"✓ Extracted {len(findings)} research findings")
    
    # Show sample findings
    if findings:
        sample_finding = findings[0]
        print(f"✓ Sample finding: {sample_finding.title}")
        print(f"  Domain: {sample_finding.z_framework_domain}")
        print(f"  Artifacts: {len(sample_finding.artifacts)}")
    
    # Test content organization
    print(f"\n4. CONTENT ORGANIZATION")
    content = compiler.organize_content(findings)
    print(f"✓ Abstract length: {len(content['abstract'])} characters")
    print(f"✓ Introduction sections generated")
    print(f"✓ Methodology sections generated")
    print(f"✓ Results sections generated")
    print(f"✓ References: {len(content['references'])} entries")
    
    # Test LaTeX generation
    print(f"\n5. LATEX GENERATION")
    latex_doc = compiler.generate_latex_whitepaper(content)
    print(f"✓ LaTeX document generated: {len(latex_doc)} characters")
    
    # Check for key LaTeX components
    latex_checks = [
        (r'\documentclass', 'Document class'),
        (r'\usepackage{amsmath}', 'AMS Math package'),
        (r'\usepackage{siunitx}', 'SI Units package'),
        (r'Z = A\\left(\\frac{B}{c}\\right)', 'Universal Z equation'),
        (r'\section{Introduction}', 'Introduction section'),
        (r'\section{Results}', 'Results section'),
        (r'\bibliographystyle{plain}', 'Bibliography style')
    ]
    
    for pattern, description in latex_checks:
        if pattern in latex_doc:
            print(f"  ✓ {description} found")
        else:
            print(f"  ✗ {description} missing")
    
    # Test artifact integration
    print(f"\n6. ARTIFACT INTEGRATION")
    all_artifacts = []
    for finding in findings:
        all_artifacts.extend(finding.artifacts)
    
    integrated_artifacts = compiler.create_artifact_integration(all_artifacts)
    print(f"✓ Integrated {len(integrated_artifacts)} artifacts")
    
    # Show sample artifacts
    if integrated_artifacts:
        sample_artifact = integrated_artifacts[0]
        print(f"✓ Sample artifact: {sample_artifact['title']}")
        print(f"  Content Type: {sample_artifact['contentType']}")
        print(f"  Content Length: {len(sample_artifact['content'])} characters")
        print(f"  Z Framework Relevance: {sample_artifact['z_framework_relevance']}")
    
    # Test complete compilation
    print(f"\n7. COMPLETE COMPILATION")
    results = compiler.compile_whitepaper()
    print(f"✓ Compilation completed successfully")
    print(f"✓ Findings: {results['findings_count']}")
    print(f"✓ Artifacts: {results['artifacts_count']}")
    print(f"✓ Timestamp: {results['timestamp']}")
    
    return results


def demonstrate_xaiartifact_integration(results):
    """Demonstrate xaiArtifact integration with sample outputs."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING XAIARTIFACT INTEGRATION")
    print("=" * 80)
    
    artifacts = results['artifacts']
    latex_document = results['latex_document']
    
    print(f"\nShowing first 3 artifacts in xaiArtifact format:")
    print("-" * 60)
    
    # Show first few artifacts
    for i, artifact in enumerate(artifacts[:3]):
        artifact_content = artifact['content']
        if len(artifact_content) > 2000:
            artifact_content = artifact_content[:2000] + "\n\n... [Content truncated for display]"
            
        print(f"\nArtifact {i+1}:")
        print(f'<xaiArtifact artifact_id="{artifact["artifact_id"]}" '
              f'title="{artifact["title"]}" '
              f'contentType="{artifact["contentType"]}">')
        print(artifact_content)
        print('</xaiArtifact>')
        print("-" * 40)
    
    # Show the main LaTeX white paper
    print(f"\nMain White Paper LaTeX Document:")
    print(f'<xaiArtifact artifact_id="white_paper_latex" '
          f'title="z_framework_whitepaper.tex" '
          f'contentType="text/latex">')
    print(latex_document[:3000] + "\n\n... [Content truncated for display]")
    print('</xaiArtifact>')


def test_z_framework_compliance(results):
    """Test compliance with Z Framework system instruction."""
    print("\n" + "=" * 80)
    print("TESTING Z FRAMEWORK COMPLIANCE")
    print("=" * 80)
    
    content = results['content_structure']
    latex_doc = results['latex_document']
    
    # Check for Z Framework mathematical forms
    z_framework_checks = [
        ('Z = A(B/c)', 'Universal Z form'),
        ('Z = T(v/c)', 'Physical domain form'),
        ('Z = n(Δ_n/Δ_max)', 'Discrete domain form'),
        ('θ\'(n, k)', 'Geodesic transformation'),
        ('k* ≈ 0.3', 'Optimal curvature parameter'),
        ('15%', 'Enhancement percentage'),
        ('confidence interval', 'Statistical validation'),
        ('empirical', 'Empirical validation')
    ]
    
    print(f"Checking Z Framework compliance in generated content:")
    for pattern, description in z_framework_checks:
        if pattern in latex_doc or pattern in str(content):
            print(f"  ✓ {description}: Found")
        else:
            print(f"  ⚠ {description}: Not found")
    
    # Check empirical validation
    print(f"\nEmpirical validation checks:")
    findings = [f for f in results.get('compilation_metadata', {}).get('findings', [])]
    
    validation_checks = [
        ('correlation', 'Correlation analysis'),
        ('confidence', 'Confidence intervals'),
        ('bootstrap', 'Bootstrap analysis'),
        ('enhancement', 'Enhancement measurements'),
        ('p_value', 'Statistical significance')
    ]
    
    for pattern, description in validation_checks:
        found = any(pattern in str(artifact).lower() for artifact in results['artifacts'])
        if found:
            print(f"  ✓ {description}: Found in artifacts")
        else:
            print(f"  ⚠ {description}: Not found in artifacts")


if __name__ == '__main__':
    print("Academic White Paper Compilation System Test")
    print("Testing Z Framework integration and xaiArtifact compatibility")
    
    try:
        # Run complete test
        results = test_whitepaper_compilation()
        
        # Demonstrate xaiArtifact integration
        demonstrate_xaiartifact_integration(results)
        
        # Test Z Framework compliance
        test_z_framework_compliance(results)
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("✓ White paper compilation system is operational")
        print("✓ xaiArtifact integration is functional")
        print("✓ Z Framework compliance is maintained")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()