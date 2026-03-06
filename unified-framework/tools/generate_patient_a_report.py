#!/usr/bin/env python3
"""
Generate Forensic Traceability Report for Patient A

This script analyzes the provided medical forensic report and generates a traceability
report mapping claims against VA findings for Patient A.
"""

import os
import sys
from datetime import datetime

# Add the project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# Import the forensic analysis modules
from src.applications.forensic_claim_analysis.claim_analyzer import ForensicClaimAnalyzer
from src.applications.forensic_claim_analysis.findings_mapper import FindingsMapper  
from src.applications.forensic_claim_analysis.report_generator import ForensicTraceabilityReportGenerator


def get_medical_forensic_report_text():
    """Return the medical forensic report text from the issue description."""
    return """
Medical Forensic Report

Evaluator: [Redacted] Date of Evaluation: September 12, 2025 Time of Evaluation: 11:40 AM EDT Patient Information: [Redacted] Group ID #: [Redacted] DOB: [Redacted] Age: 50 Gender: Male Location: [Redacted]

Spine MRI Analysis Report

Traumatic vs. Degenerative Assessment

Report Generated: September 12, 2025 at 10:25

Studies Analyzed: 2

Series Analyzed: 9

Total Findings: 1218

Overall Assessment: Evidence of traumatic changes identified

Executive Summary

I present this analysis of my MRI series examining spine pathology with particular attention to differentiating traumatic from degenerative changes.

Key Findings: My analysis focused on detecting focal, asymmetric changes consistent with old injuries versus multifocal, symmetric degenerative patterns. Special attention was given to identifying markers of resolved acute trauma including wedge deformities, burst fractures, and post-traumatic syringomyelia.

Detailed Forensic Analysis and Comparison with VA Reports

I reviewed the following VA radiology reports in light of my findings from the spine MRI analysis to determine the accuracy of the initial diagnoses:

CT Head without Contrast (Sep 10, 2025)

MRI Cervical Spine without Contrast (Aug 21, 2025)

MRI Thoracic Spine without Contrast (Aug 21, 2025)

Thoracic Spine X-ray 2 Views (Jul 17, 2025)

1. CT Head without Contrast (Sep 10, 2025)

VA Findings: Normal ventricular size, no acute hemorrhage, mass effect, midline shift, or calvarial fractures. Clear paranasal sinuses. Impression: No acute intracranial issues related to dizziness.

My Assessment: I found no evidence of acute intracranial pathology on this CT, which aligns with the absence of recent trauma. However, I suspect that chronic traumatic sequelae, such as post-traumatic syringomyelia or subtle cord/brainstem changes from a 20-year-old combat injury, could explain the reported dizziness. The CT's 4 mm axial slices without contrast or sagittal emphasis are insufficient to detect such chronic changes, leading to an incomplete assessment. The VA did not correlate dizziness with my identified spinal trauma (e.g., focal wedge deformities) despite the dizziness being documented in the report.

2. MRI Cervical Spine without Contrast (Aug 21, 2025)

VA Findings: Normal vertebral heights, no marrow edema, compression fracture, or subluxation. Decreased disc space at C5-C6. Disc osteophyte complexes at C3-C4, C4-C5, C5-C6 (mild canal narrowing, severe right foraminal stenosis), and C6-C7. No cord signal abnormality. Impression: Degenerative disease.

My Assessment: The slices contain wedge deformities at levels like C5-C6, contradicting the VA's report of normal vertebral heights. The "decreased disc space" and osteophyte complexes at C5-C6 likely reflect chronic post-traumatic changes (e.g., anterior height loss ratios
"""


def generate_patient_a_report():
    """Generate the traceability report for Patient A."""
    print("🔬 Medical Forensic Claim Analysis - Patient A")
    print("=" * 60)
    
    # Initialize components
    analyzer = ForensicClaimAnalyzer()
    mapper = FindingsMapper()
    report_generator = ForensicTraceabilityReportGenerator()
    
    # Get the forensic report text
    report_text = get_medical_forensic_report_text()
    
    print("📊 Step 1: Analyzing forensic report and extracting claims...")
    
    # Parse the forensic report
    analysis_results = analyzer.parse_forensic_report(report_text)
    
    print(f"   ✓ Extracted {analysis_results['total_claims']} medical claims")
    print(f"   ✓ Patient: {analysis_results['patient_info'].get('age', 'N/A')} year old {analysis_results['patient_info'].get('gender', 'N/A')}")
    print(f"   ✓ Evaluation Date: {analysis_results['report_metadata'].get('evaluation_date', 'N/A')}")
    
    # Display claims summary
    claims_summary = analyzer.generate_claims_summary()
    print(f"\n📋 Claims Summary:")
    for category, count in claims_summary['category_breakdown'].items():
        if count > 0:
            print(f"   • {category.replace('_', ' ').title()}: {count}")
    
    print(f"\n🎯 Step 2: Loading VA findings and performing traceability mapping...")
    
    # Load VA findings (embedded in the report text)
    va_findings = mapper.load_va_findings(report_text)
    print(f"   ✓ Loaded {len(va_findings)} VA findings from reports")
    
    # Map claims to findings
    mapping_results = mapper.map_claims_to_findings(analyzer.claims)
    print(f"   ✓ Completed mapping for {len(mapping_results)} claims")
    
    # Generate traceability summary
    traceability_summary = mapper.generate_traceability_summary()
    print(f"\n📈 Traceability Analysis Results:")
    print(f"   • High-confidence contradictions: {traceability_summary['high_confidence_contradictions']}")
    print(f"   • Total discrepancies identified: {traceability_summary['total_discrepancies_identified']}")
    print(f"   • Average confidence score: {traceability_summary['average_confidence_score']:.2f}")
    
    print(f"\n📝 Step 3: Generating comprehensive traceability report...")
    
    # Create output directory
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"patient_a_traceability_report_{timestamp}.pdf")
    
    try:
        generated_report = report_generator.generate_traceability_report(
            analyzer=analyzer,
            mapper=mapper,
            output_path=output_path,
            patient_id="Patient A"
        )
        
        print(f"   ✓ Report generated successfully: {generated_report}")
        
        # Display key findings
        print(f"\n🔍 Key Findings Summary:")
        contradicted_mappings = [r for r in mapping_results if r.mapping_status.value == 'contradicted']
        for mapping in contradicted_mappings[:3]:  # Show top 3
            print(f"   • CONTRADICTION: {mapping.claim.claim_id}")
            print(f"     Claim: {mapping.claim.claim_text[:80]}...")
            print(f"     Analysis: {mapping.analysis_notes[:100]}...")
            print()
        
        print(f"\n✅ Analysis Complete!")
        print(f"📄 Full traceability report available at: {output_path}")
        print(f"🎯 This report maps {len(analyzer.claims)} forensic claims against VA findings")
        print(f"⚠️  Identified {traceability_summary['high_confidence_contradictions']} high-confidence contradictions")
        
        return output_path
        
    except Exception as e:
        print(f"   ❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    try:
        report_path = generate_patient_a_report()
        
        if report_path and os.path.exists(report_path):
            print(f"\n🎉 Patient A Traceability Report Generated Successfully!")
            print(f"📁 Report location: {os.path.abspath(report_path)}")
            
            # Display file size
            file_size = os.path.getsize(report_path)
            print(f"📊 Report size: {file_size:,} bytes")
            
            return 0
        else:
            print(f"\n❌ Failed to generate report")
            return 1
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())