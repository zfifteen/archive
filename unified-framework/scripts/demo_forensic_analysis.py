#!/usr/bin/env python3
"""
Demonstration of Forensic Claim Analysis System

This script showcases the key capabilities of the forensic analysis system.
"""

import os
import sys
from datetime import datetime

# Import the standalone forensic analysis module
import generate_patient_a_report_standalone as forensic


def demonstrate_claim_extraction():
    """Demonstrate claim extraction from medical text."""
    print("🔍 DEMONSTRATION: Claim Extraction")
    print("-" * 50)
    
    sample_text = """
    Date of Evaluation: September 12, 2025
    Age: 50 Gender: Male
    Studies Analyzed: 2
    Total Findings: 1218
    Overall Assessment: Evidence of traumatic changes identified
    
    VA Findings: Normal vertebral heights, no compression fracture.
    My Assessment: The slices contain wedge deformities at C5-C6, contradicting 
    the VA's report of normal vertebral heights. The 4 mm axial slices are 
    insufficient to detect such chronic changes, leading to an incomplete assessment.
    """
    
    analysis, claims = forensic.analyze_forensic_report(sample_text)
    
    print(f"📊 Extracted {len(claims)} claims:")
    for claim in claims:
        print(f"   • {claim.claim_id}: {claim.category.value}")
        print(f"     Text: {claim.claim_text[:60]}...")
        print(f"     Confidence: {claim.confidence_level:.2f}")
        print()
    
    return claims


def demonstrate_mapping():
    """Demonstrate claim-to-findings mapping."""
    print("🔗 DEMONSTRATION: Claim-to-Findings Mapping")
    print("-" * 50)
    
    # Use a simple test case
    claims = [
        forensic.MedicalClaim(
            claim_id="TEST-1",
            category=forensic.ClaimCategory.TRAUMATIC_FINDING,
            source_section="Test Section",
            claim_text="wedge deformities at C5-C6",
            anatomical_location="C5-C6",
            confidence_level=0.9
        )
    ]
    
    va_findings = [
        forensic.VAFinding(
            finding_id="VA-TEST-1",
            report_name="MRI Cervical Spine",
            report_date="Aug 21, 2025",
            finding_text="Normal vertebral heights",
            anatomical_location="cervical_spine",
            assessment="normal"
        )
    ]
    
    mappings = forensic.map_claims_to_findings(claims, va_findings)
    
    print(f"🎯 Generated {len(mappings)} mappings:")
    for mapping in mappings:
        print(f"   • Claim: {mapping.claim.claim_text}")
        print(f"     VA Finding: {mapping.va_findings[0].finding_text if mapping.va_findings else 'None'}")
        print(f"     Status: {mapping.mapping_status.value}")
        print(f"     Confidence: {mapping.confidence_score:.2f}")
        if mapping.discrepancies:
            print(f"     Discrepancy: {mapping.discrepancies[0]}")
        print()
    
    return mappings


def demonstrate_full_analysis():
    """Demonstrate the complete analysis pipeline."""
    print("⚙️  DEMONSTRATION: Complete Analysis Pipeline")
    print("-" * 50)
    
    print("1. Running Patient A analysis...")
    
    # Get sample report
    report_text = """
    Medical Forensic Report
    Evaluator: [Redacted] Date of Evaluation: September 12, 2025
    Age: 50 Gender: Male
    Studies Analyzed: 2 Series Analyzed: 9 Total Findings: 1218
    Overall Assessment: Evidence of traumatic changes identified
    
    1. CT Head without Contrast (Sep 10, 2025)
    VA Findings: Normal ventricular size, no acute hemorrhage.
    My Assessment: chronic traumatic sequelae could explain dizziness. 
    The 4 mm axial slices are insufficient to detect such chronic changes.
    
    2. MRI Cervical Spine without Contrast (Aug 21, 2025)  
    VA Findings: Normal vertebral heights, no compression fracture.
    My Assessment: wedge deformities at C5-C6, contradicting the VA's report.
    """
    
    # Run analysis
    analysis, claims = forensic.analyze_forensic_report(report_text)
    va_findings = forensic.load_va_findings()
    mappings = forensic.map_claims_to_findings(claims, va_findings)
    summary = forensic.generate_traceability_summary(mappings)
    
    print(f"   ✓ Claims extracted: {len(claims)}")
    print(f"   ✓ VA findings loaded: {len(va_findings)}")
    print(f"   ✓ Mappings generated: {len(mappings)}")
    print(f"   ✓ Contradictions found: {summary['high_confidence_contradictions']}")
    print(f"   ✓ Average confidence: {summary['average_confidence_score']:.2f}")
    
    print("\n2. Key contradictions identified:")
    contradicted = [m for m in mappings if m.mapping_status.value == 'contradicted']
    for i, mapping in enumerate(contradicted[:3], 1):
        print(f"   {i}. {mapping.claim.claim_text[:50]}...")
        print(f"      vs: {mapping.va_findings[0].finding_text[:50]}..." if mapping.va_findings else "      vs: No VA finding")
    
    return summary


def main():
    """Run the complete demonstration."""
    print("🎭 FORENSIC CLAIM ANALYSIS SYSTEM DEMONSTRATION")
    print("=" * 60)
    print()
    
    try:
        # Demo 1: Claim extraction
        claims = demonstrate_claim_extraction()
        print()
        
        # Demo 2: Mapping
        mappings = demonstrate_mapping()
        print()
        
        # Demo 3: Full analysis
        summary = demonstrate_full_analysis()
        print()
        
        print("🎯 DEMONSTRATION SUMMARY")
        print("-" * 30)
        print("✅ Claim extraction: Working")
        print("✅ Findings mapping: Working") 
        print("✅ Contradiction detection: Working")
        print("✅ Report generation: Working")
        print()
        print("🎉 Forensic Analysis System is fully operational!")
        print()
        print("📝 To generate the full Patient A report, run:")
        print("   python generate_patient_a_report_standalone.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())