#!/usr/bin/env python3
"""
Standalone Forensic Traceability Report Generator for Patient A

This script directly implements the forensic claim analysis without complex dependencies.
"""

import os
import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors


class ClaimCategory(Enum):
    """Categories of medical claims in forensic reports."""
    TRAUMATIC_FINDING = "traumatic_finding"
    DEGENERATIVE_FINDING = "degenerative_finding"
    NORMAL_FINDING = "normal_finding"
    METHODOLOGICAL_CRITIQUE = "methodological_critique"
    MEASUREMENT_DISCREPANCY = "measurement_discrepancy"
    ASSESSMENT_CRITIQUE = "assessment_critique"


class MappingStatus(Enum):
    """Status of claim-to-finding mapping."""
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    PARTIALLY_SUPPORTED = "partially_supported"
    NO_CORRESPONDENCE = "no_correspondence"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class MedicalClaim:
    """Represents a medical claim from a forensic report."""
    claim_id: str
    category: ClaimCategory
    source_section: str
    claim_text: str
    anatomical_location: Optional[str] = None
    measurement_value: Optional[float] = None
    confidence_level: float = 0.0
    evidence_cited: List[str] = None
    va_report_reference: Optional[str] = None
    
    def __post_init__(self):
        if self.evidence_cited is None:
            self.evidence_cited = []


@dataclass
class VAFinding:
    """Represents a finding from VA reports."""
    finding_id: str
    report_name: str
    report_date: str
    finding_text: str
    anatomical_location: Optional[str] = None
    measurement_value: Optional[float] = None
    assessment: str = "normal"


@dataclass
class ClaimMappingResult:
    """Result of mapping a forensic claim to VA findings."""
    claim: MedicalClaim
    va_findings: List[VAFinding]
    mapping_status: MappingStatus
    confidence_score: float
    analysis_notes: str
    evidence_alignment: List[str]
    discrepancies: List[str]


def analyze_forensic_report(report_text: str) -> Tuple[Dict, List[MedicalClaim]]:
    """Analyze forensic report and extract claims."""
    
    # Extract patient information
    patient_info = {}
    age_match = re.search(r'Age:\s*(\d+)', report_text)
    if age_match:
        patient_info['age'] = age_match.group(1)
        
    gender_match = re.search(r'Gender:\s*(\w+)', report_text)
    if gender_match:
        patient_info['gender'] = gender_match.group(1)
    
    # Extract report metadata
    metadata = {}
    eval_date_match = re.search(r'Date of Evaluation:\s*([^\n\r]+)', report_text)
    if eval_date_match:
        metadata['evaluation_date'] = eval_date_match.group(1).strip()
        
    studies_match = re.search(r'Studies Analyzed:\s*(\d+)', report_text)
    if studies_match:
        metadata['studies_analyzed'] = int(studies_match.group(1))
        
    series_match = re.search(r'Series Analyzed:\s*(\d+)', report_text)
    if series_match:
        metadata['series_analyzed'] = int(series_match.group(1))
        
    findings_match = re.search(r'Total Findings:\s*(\d+)', report_text)
    if findings_match:
        metadata['total_findings'] = int(findings_match.group(1))
    
    # Extract claims
    claims = []
    
    # Overall assessment claim
    if "Evidence of traumatic changes identified" in report_text:
        claims.append(MedicalClaim(
            claim_id="OVERALL-1",
            category=ClaimCategory.TRAUMATIC_FINDING,
            source_section="Overall Assessment",
            claim_text="Evidence of traumatic changes identified",
            confidence_level=0.95
        ))
    
    # CT Head assessment claims
    ct_head_section = re.search(r'1\.\s+CT Head without Contrast.*?(?=2\.|$)', report_text, re.DOTALL)
    if ct_head_section:
        section_text = ct_head_section.group(0)
        
        # VA finding claim
        claims.append(MedicalClaim(
            claim_id="VA-CT-1",
            category=ClaimCategory.NORMAL_FINDING,
            source_section="CT Head without Contrast",
            claim_text="Normal ventricular size, no acute hemorrhage, mass effect, midline shift, or calvarial fractures",
            va_report_reference="CT Head without Contrast (Sep 10, 2025)",
            confidence_level=0.8
        ))
        
        # Forensic critique claims
        if "chronic traumatic sequelae" in section_text:
            claims.append(MedicalClaim(
                claim_id="TRAUMATIC-1",
                category=ClaimCategory.TRAUMATIC_FINDING,
                source_section="CT Head without Contrast - My Assessment",
                claim_text="chronic traumatic sequelae, such as post-traumatic syringomyelia or subtle cord/brainstem changes from a 20-year-old combat injury",
                anatomical_location="head/brainstem",
                confidence_level=0.85
            ))
        
        if "insufficient to detect" in section_text:
            claims.append(MedicalClaim(
                claim_id="CRITIQUE-1",
                category=ClaimCategory.METHODOLOGICAL_CRITIQUE,
                source_section="CT Head without Contrast - My Assessment",
                claim_text="4 mm axial slices without contrast or sagittal emphasis are insufficient to detect such chronic changes",
                confidence_level=0.9
            ))
        
        if "incomplete assessment" in section_text:
            claims.append(MedicalClaim(
                claim_id="CRITIQUE-2",
                category=ClaimCategory.ASSESSMENT_CRITIQUE,
                source_section="CT Head without Contrast - My Assessment",
                claim_text="leading to an incomplete assessment",
                confidence_level=0.85
            ))
    
    # Cervical spine assessment claims
    cervical_section = re.search(r'2\.\s+MRI Cervical Spine.*?(?=3\.|$)', report_text, re.DOTALL)
    if cervical_section:
        section_text = cervical_section.group(0)
        
        # VA finding claim
        claims.append(MedicalClaim(
            claim_id="VA-CERVICAL-1",
            category=ClaimCategory.NORMAL_FINDING,
            source_section="MRI Cervical Spine without Contrast",
            claim_text="Normal vertebral heights, no marrow edema, compression fracture, or subluxation",
            anatomical_location="cervical_spine",
            va_report_reference="MRI Cervical Spine without Contrast (Aug 21, 2025)",
            confidence_level=0.8
        ))
        
        claims.append(MedicalClaim(
            claim_id="VA-CERVICAL-2",
            category=ClaimCategory.DEGENERATIVE_FINDING,
            source_section="MRI Cervical Spine without Contrast",
            claim_text="Decreased disc space at C5-C6. Disc osteophyte complexes at C3-C4, C4-C5, C5-C6",
            anatomical_location="C5-C6",
            va_report_reference="MRI Cervical Spine without Contrast (Aug 21, 2025)",
            confidence_level=0.8
        ))
        
        # Forensic contradictory claims
        if "wedge deformities" in section_text:
            claims.append(MedicalClaim(
                claim_id="TRAUMATIC-2",
                category=ClaimCategory.TRAUMATIC_FINDING,
                source_section="MRI Cervical Spine - My Assessment",
                claim_text="wedge deformities at levels like C5-C6, contradicting the VA's report of normal vertebral heights",
                anatomical_location="C5-C6",
                confidence_level=0.9
            ))
        
        if "post-traumatic changes" in section_text:
            claims.append(MedicalClaim(
                claim_id="TRAUMATIC-3", 
                category=ClaimCategory.TRAUMATIC_FINDING,
                source_section="MRI Cervical Spine - My Assessment",
                claim_text="decreased disc space and osteophyte complexes at C5-C6 likely reflect chronic post-traumatic changes",
                anatomical_location="C5-C6",
                confidence_level=0.85
            ))
    
    analysis_results = {
        "patient_info": patient_info,
        "report_metadata": metadata,
        "total_claims": len(claims)
    }
    
    return analysis_results, claims


def load_va_findings() -> List[VAFinding]:
    """Load VA findings from the provided report data."""
    findings = [
        VAFinding(
            finding_id="VA-1-CT-HEAD",
            report_name="CT Head without Contrast",
            report_date="Sep 10, 2025",
            finding_text="Normal ventricular size, no acute hemorrhage, mass effect, midline shift, or calvarial fractures. Clear paranasal sinuses.",
            anatomical_location="head",
            assessment="normal"
        ),
        VAFinding(
            finding_id="VA-2-CERVICAL-MAIN",
            report_name="MRI Cervical Spine without Contrast",
            report_date="Aug 21, 2025", 
            finding_text="Normal vertebral heights, no marrow edema, compression fracture, or subluxation.",
            anatomical_location="cervical_spine",
            assessment="normal"
        ),
        VAFinding(
            finding_id="VA-2-CERVICAL-C5C6",
            report_name="MRI Cervical Spine without Contrast",
            report_date="Aug 21, 2025",
            finding_text="Decreased disc space at C5-C6",
            anatomical_location="C5-C6",
            assessment="degenerative"
        ),
        VAFinding(
            finding_id="VA-2-CERVICAL-STENOSIS",
            report_name="MRI Cervical Spine without Contrast", 
            report_date="Aug 21, 2025",
            finding_text="severe right foraminal stenosis at C5-C6",
            anatomical_location="C5-C6",
            assessment="degenerative"
        )
    ]
    return findings


def map_claims_to_findings(claims: List[MedicalClaim], va_findings: List[VAFinding]) -> List[ClaimMappingResult]:
    """Map forensic claims to VA findings."""
    mapping_results = []
    
    for claim in claims:
        # Find relevant VA findings
        relevant_findings = []
        
        for finding in va_findings:
            # Location-based matching
            if claim.anatomical_location and finding.anatomical_location:
                if claim.anatomical_location.lower() in finding.anatomical_location.lower() or \
                   finding.anatomical_location.lower() in claim.anatomical_location.lower():
                    relevant_findings.append(finding)
                    continue
            
            # Category-based matching for contradictions
            if claim.category == ClaimCategory.TRAUMATIC_FINDING and finding.assessment == "normal":
                relevant_findings.append(finding)
        
        if not relevant_findings:
            mapping_results.append(ClaimMappingResult(
                claim=claim,
                va_findings=[],
                mapping_status=MappingStatus.NO_CORRESPONDENCE,
                confidence_score=0.0,
                analysis_notes="No corresponding VA findings identified for this claim.",
                evidence_alignment=[],
                discrepancies=["Claim not addressed in VA reports"]
            ))
            continue
        
        # Analyze mapping
        if claim.category == ClaimCategory.TRAUMATIC_FINDING:
            normal_findings = [f for f in relevant_findings if f.assessment == "normal"]
            if normal_findings:
                mapping_results.append(ClaimMappingResult(
                    claim=claim,
                    va_findings=relevant_findings,
                    mapping_status=MappingStatus.CONTRADICTED,
                    confidence_score=0.9,
                    analysis_notes=f"Forensic claim of traumatic finding directly contradicts VA assessment of normal findings",
                    evidence_alignment=[],
                    discrepancies=[
                        f"Forensic analysis identifies traumatic changes but VA reports normal findings",
                        f"Specific contradiction: '{claim.claim_text}' vs '{normal_findings[0].finding_text}'"
                    ]
                ))
            else:
                mapping_results.append(ClaimMappingResult(
                    claim=claim,
                    va_findings=relevant_findings,
                    mapping_status=MappingStatus.PARTIALLY_SUPPORTED,
                    confidence_score=0.7,
                    analysis_notes="Traumatic finding may correlate with some degenerative changes in VA reports",
                    evidence_alignment=["Both identify changes at similar anatomical locations"],
                    discrepancies=["Disagreement on traumatic vs degenerative etiology"]
                ))
        
        elif claim.category == ClaimCategory.METHODOLOGICAL_CRITIQUE:
            mapping_results.append(ClaimMappingResult(
                claim=claim,
                va_findings=relevant_findings,
                mapping_status=MappingStatus.INSUFFICIENT_DATA,
                confidence_score=0.85,
                analysis_notes="Forensic analysis identifies methodological limitations in VA assessment",
                evidence_alignment=[],
                discrepancies=[f"Methodological critique: {claim.claim_text}"]
            ))
        
        else:
            # Default case
            mapping_results.append(ClaimMappingResult(
                claim=claim,
                va_findings=relevant_findings,
                mapping_status=MappingStatus.PARTIALLY_SUPPORTED,
                confidence_score=0.5,
                analysis_notes="Partial alignment between forensic claim and VA findings",
                evidence_alignment=[],
                discrepancies=[]
            ))
    
    return mapping_results


def generate_traceability_summary(mapping_results: List[ClaimMappingResult]) -> Dict:
    """Generate summary of traceability analysis."""
    status_counts = {}
    for status in MappingStatus:
        status_counts[status.value] = len([r for r in mapping_results if r.mapping_status == status])
    
    high_confidence_contradictions = [
        r for r in mapping_results 
        if r.mapping_status == MappingStatus.CONTRADICTED and r.confidence_score >= 0.8
    ]
    
    total_discrepancies = sum(len(r.discrepancies) for r in mapping_results)
    
    return {
        "total_claims_analyzed": len(mapping_results),
        "mapping_status_breakdown": status_counts,
        "high_confidence_contradictions": len(high_confidence_contradictions),
        "total_discrepancies_identified": total_discrepancies,
        "average_confidence_score": sum(r.confidence_score for r in mapping_results) / len(mapping_results) if mapping_results else 0
    }


def generate_pdf_report(analysis_results: Dict, claims: List[MedicalClaim], 
                       mapping_results: List[ClaimMappingResult], output_path: str) -> str:
    """Generate the PDF traceability report."""
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Setup styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Title'], fontSize=18, 
                             spaceAfter=20, alignment=TA_CENTER, textColor=HexColor('#1f4e79')))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading1'], fontSize=14,
                             spaceAfter=12, spaceBefore=20, textColor=HexColor('#2c5aa0')))
    styles.add(ParagraphStyle(name='Finding', parent=styles['Normal'], fontSize=10, 
                             spaceAfter=6, leftIndent=20))
    styles.add(ParagraphStyle(name='Discrepancy', parent=styles['Normal'], fontSize=10,
                             spaceAfter=6, leftIndent=20, textColor=HexColor('#d63031')))
    
    # Build content
    story = []
    
    # Title page
    story.append(Paragraph("Medical Forensic Report Traceability Analysis", styles['ReportTitle']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Claim-to-Findings Mapping Report for Patient A", styles['Heading2']))
    story.append(Spacer(1, 30))
    
    # Metadata table
    metadata_data = [
        ["Report Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ["Analysis Date:", analysis_results['report_metadata'].get('evaluation_date', 'N/A')],
        ["Total Claims Analyzed:", str(analysis_results['total_claims'])],
        ["Studies Reviewed:", str(analysis_results['report_metadata'].get('studies_analyzed', 'N/A'))],
        ["Series Analyzed:", str(analysis_results['report_metadata'].get('series_analyzed', 'N/A'))],
        ["Total Findings:", str(analysis_results['report_metadata'].get('total_findings', 'N/A'))]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metadata_table)
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    
    traceability_summary = generate_traceability_summary(mapping_results)
    
    summary_text = f"""
    This analysis examined <b>{traceability_summary['total_claims_analyzed']} medical claims</b> extracted from 
    the forensic evaluation against corresponding findings in VA radiology reports.
    
    <b>Key Findings:</b>
    <br/>• <b>{traceability_summary['high_confidence_contradictions']} high-confidence contradictions</b> 
    were identified between forensic claims and VA assessments
    <br/>• <b>{traceability_summary['total_discrepancies_identified']} specific discrepancies</b> 
    were documented across all anatomical regions examined
    <br/>• Average mapping confidence score: <b>{traceability_summary['average_confidence_score']:.2f}</b>
    
    <b>Primary Areas of Concern:</b>
    <br/>1. Contradictory assessments of vertebral morphology at cervical levels
    <br/>2. Disagreement on the significance of height loss measurements  
    <br/>3. Methodological limitations in VA imaging protocols
    <br/>4. Incomplete correlation of clinical symptoms with imaging findings
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Claims Analysis
    story.append(Paragraph("Forensic Claims Analysis", styles['SectionHeader']))
    
    for claim in claims:
        claim_text = f"""
        <b>Claim {claim.claim_id}:</b> {claim.claim_text}
        <br/><i>Category:</i> {claim.category.value.replace('_', ' ').title()}
        <br/><i>Source:</i> {claim.source_section}
        <br/><i>Confidence:</i> {claim.confidence_level:.2f}
        """
        if claim.anatomical_location:
            claim_text += f"<br/><i>Location:</i> {claim.anatomical_location}"
        
        story.append(Paragraph(claim_text, styles['Finding']))
        story.append(Spacer(1, 10))
    
    # Traceability Mapping
    story.append(Paragraph("Claim-to-Findings Traceability Mapping", styles['SectionHeader']))
    
    # Summary table
    mapping_data = [
        ["Mapping Status", "Count", "Percentage"],
        ["Contradicted", str(traceability_summary['mapping_status_breakdown'].get('contradicted', 0)), 
         f"{(traceability_summary['mapping_status_breakdown'].get('contradicted', 0) / traceability_summary['total_claims_analyzed'] * 100):.1f}%"],
        ["Supported", str(traceability_summary['mapping_status_breakdown'].get('supported', 0)),
         f"{(traceability_summary['mapping_status_breakdown'].get('supported', 0) / traceability_summary['total_claims_analyzed'] * 100):.1f}%"],
        ["Partially Supported", str(traceability_summary['mapping_status_breakdown'].get('partially_supported', 0)),
         f"{(traceability_summary['mapping_status_breakdown'].get('partially_supported', 0) / traceability_summary['total_claims_analyzed'] * 100):.1f}%"],
        ["No Correspondence", str(traceability_summary['mapping_status_breakdown'].get('no_correspondence', 0)),
         f"{(traceability_summary['mapping_status_breakdown'].get('no_correspondence', 0) / traceability_summary['total_claims_analyzed'] * 100):.1f}%"],
        ["Insufficient Data", str(traceability_summary['mapping_status_breakdown'].get('insufficient_data', 0)),
         f"{(traceability_summary['mapping_status_breakdown'].get('insufficient_data', 0) / traceability_summary['total_claims_analyzed'] * 100):.1f}%"]
    ]
    
    mapping_table = Table(mapping_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
    mapping_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(mapping_table)
    story.append(Spacer(1, 20))
    
    # Detailed Comparisons
    story.append(Paragraph("Detailed Claim-Finding Comparisons", styles['SectionHeader']))
    
    contradicted_mappings = [r for r in mapping_results if r.mapping_status == MappingStatus.CONTRADICTED]
    
    for i, mapping in enumerate(contradicted_mappings, 1):
        story.append(Paragraph(f"Contradiction {i}: {mapping.claim.claim_id}", styles['Heading3']))
        
        claim_text = f"""
        <b>Forensic Claim:</b> {mapping.claim.claim_text}
        <br/><b>Category:</b> {mapping.claim.category.value.replace('_', ' ').title()}
        <br/><b>Analysis:</b> {mapping.analysis_notes}
        """
        story.append(Paragraph(claim_text, styles['Normal']))
        
        if mapping.va_findings:
            va_text = "<b>Corresponding VA Findings:</b><br/>"
            for finding in mapping.va_findings:
                va_text += f"• <i>{finding.report_name}:</i> {finding.finding_text}<br/>"
            story.append(Paragraph(va_text, styles['Normal']))
        
        if mapping.discrepancies:
            story.append(Paragraph("<b>Identified Discrepancies:</b>", styles['Normal']))
            for discrepancy in mapping.discrepancies:
                story.append(Paragraph(f"• {discrepancy}", styles['Discrepancy']))
        
        story.append(Spacer(1, 15))
    
    # Conclusions
    story.append(Paragraph("Conclusions and Recommendations", styles['SectionHeader']))
    
    conclusions_text = f"""
    <b>Summary of Findings:</b>
    
    This traceability analysis reveals significant discrepancies between the forensic medical 
    evaluation and VA radiology assessments. Of {traceability_summary['total_claims_analyzed']} claims analyzed, 
    {traceability_summary['high_confidence_contradictions']} directly contradict VA findings, indicating 
    potential diagnostic disagreements that warrant further investigation.
    
    <b>Key Discrepancies Identified:</b>
    
    1. <b>Vertebral Morphology Assessment:</b> Forensic analysis identifies wedge deformities 
    at cervical levels that contradict VA reports of "normal vertebral heights."
    
    2. <b>Imaging Protocol Limitations:</b> Forensic evaluation critiques VA methodology, 
    citing insufficient slice thickness and lack of sagittal emphasis for detecting chronic 
    traumatic changes.
    
    3. <b>Clinical Correlation Gaps:</b> VA reports fail to correlate documented symptoms 
    (dizziness) with potential traumatic sequelae identified in forensic analysis.
    
    <b>Clinical Significance:</b>
    
    The identified discrepancies have potential implications for patient care, disability 
    assessments, and treatment planning. The forensic analysis suggests that traumatic 
    changes may have been under-recognized in the initial VA assessments.
    """
    
    story.append(Paragraph(conclusions_text, styles['Normal']))
    
    # Build the PDF
    doc.build(story)
    
    return output_path


def main():
    """Main function to generate Patient A traceability report."""
    print("🔬 Medical Forensic Claim Analysis - Patient A")
    print("=" * 60)
    
    # Medical forensic report text
    report_text = """
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
    
    print("📊 Step 1: Analyzing forensic report and extracting claims...")
    
    # Analyze the forensic report
    analysis_results, claims = analyze_forensic_report(report_text)
    
    print(f"   ✓ Extracted {analysis_results['total_claims']} medical claims")
    print(f"   ✓ Patient: {analysis_results['patient_info'].get('age', 'N/A')} year old {analysis_results['patient_info'].get('gender', 'N/A')}")
    print(f"   ✓ Evaluation Date: {analysis_results['report_metadata'].get('evaluation_date', 'N/A')}")
    
    print(f"\n🎯 Step 2: Loading VA findings and performing traceability mapping...")
    
    # Load VA findings
    va_findings = load_va_findings()
    print(f"   ✓ Loaded {len(va_findings)} VA findings from reports")
    
    # Map claims to findings
    mapping_results = map_claims_to_findings(claims, va_findings)
    print(f"   ✓ Completed mapping for {len(mapping_results)} claims")
    
    # Generate summary
    traceability_summary = generate_traceability_summary(mapping_results)
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
        generated_report = generate_pdf_report(analysis_results, claims, mapping_results, output_path)
        
        print(f"   ✓ Report generated successfully: {generated_report}")
        
        # Display key findings
        print(f"\n🔍 Key Findings Summary:")
        contradicted_mappings = [r for r in mapping_results if r.mapping_status == MappingStatus.CONTRADICTED]
        for mapping in contradicted_mappings:
            print(f"   • CONTRADICTION: {mapping.claim.claim_id}")
            print(f"     Claim: {mapping.claim.claim_text[:80]}...")
            print(f"     Analysis: {mapping.analysis_notes[:100]}...")
            print()
        
        print(f"\n✅ Analysis Complete!")
        print(f"📄 Full traceability report available at: {output_path}")
        print(f"🎯 This report maps {len(claims)} forensic claims against VA findings")
        print(f"⚠️  Identified {traceability_summary['high_confidence_contradictions']} high-confidence contradictions")
        
        return output_path
        
    except Exception as e:
        print(f"   ❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    try:
        report_path = main()
        
        if report_path and os.path.exists(report_path):
            print(f"\n🎉 Patient A Traceability Report Generated Successfully!")
            print(f"📁 Report location: {os.path.abspath(report_path)}")
            
            # Display file size
            file_size = os.path.getsize(report_path)
            print(f"📊 Report size: {file_size:,} bytes")
            
            sys.exit(0)
        else:
            print(f"\n❌ Failed to generate report")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)