"""
Forensic Traceability Report Generator

Generates comprehensive traceability reports comparing forensic claims with VA findings.
"""

import os
from datetime import datetime
from typing import List, Dict, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, red, blue, orange, green, HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                               TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

from src.applications.forensic_claim_analysis.claim_analyzer import MedicalClaim, ClaimCategory, ForensicClaimAnalyzer
from src.applications.forensic_claim_analysis.findings_mapper import ClaimMappingResult, MappingStatus, FindingsMapper


class ForensicTraceabilityReportGenerator:
    """Generates comprehensive traceability reports for forensic claim analysis."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#1f4e79')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2c5aa0')
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=HexColor('#3d6db0')
        ))
        
        # Finding style
        self.styles.add(ParagraphStyle(
            name='Finding',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        ))
        
        # Discrepancy style (highlighted)
        self.styles.add(ParagraphStyle(
            name='Discrepancy',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            textColor=HexColor('#d63031'),
            backColor=HexColor('#fff5f5')
        ))
        
        # Alignment style (positive)
        self.styles.add(ParagraphStyle(
            name='Alignment',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            textColor=HexColor('#00b894'),
            backColor=HexColor('#f0fff4')
        ))
    
    def generate_traceability_report(self, 
                                   analyzer: ForensicClaimAnalyzer,
                                   mapper: FindingsMapper,
                                   output_path: str,
                                   patient_id: str = "Patient A") -> str:
        """Generate a comprehensive traceability report."""
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content)
        story = []
        
        # Title page
        story.extend(self._build_title_page(analyzer, patient_id))
        
        # Executive summary
        story.extend(self._build_executive_summary(analyzer, mapper))
        
        # Claims analysis section
        story.extend(self._build_claims_analysis_section(analyzer))
        
        # Traceability mapping section
        story.extend(self._build_traceability_section(mapper))
        
        # Detailed findings comparison
        story.extend(self._build_detailed_comparison(mapper))
        
        # Conclusions and recommendations
        story.extend(self._build_conclusions_section(mapper))
        
        # Build the PDF
        doc.build(story)
        
        return output_path
    
    def _build_title_page(self, analyzer: ForensicClaimAnalyzer, patient_id: str) -> List:
        """Build the title page content."""
        content = []
        
        # Main title
        content.append(Paragraph(
            "Medical Forensic Report Traceability Analysis",
            self.styles['ReportTitle']
        ))
        content.append(Spacer(1, 20))
        
        # Subtitle
        content.append(Paragraph(
            f"Claim-to-Findings Mapping Report for {patient_id}",
            self.styles['Heading2']
        ))
        content.append(Spacer(1, 30))
        
        # Report metadata
        metadata_data = [
            ["Report Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ["Analysis Date:", analyzer.report_metadata.get('evaluation_date', 'N/A')],
            ["Evaluator:", analyzer.report_metadata.get('evaluator', '[Redacted]')],
            ["Total Claims Analyzed:", str(len(analyzer.claims))],
            ["Studies Reviewed:", str(analyzer.report_metadata.get('studies_analyzed', 'N/A'))],
            ["Series Analyzed:", str(analyzer.report_metadata.get('series_analyzed', 'N/A'))],
            ["Total Findings:", str(analyzer.report_metadata.get('total_findings', 'N/A'))]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(metadata_table)
        content.append(Spacer(1, 30))
        
        # Purpose statement
        purpose_text = """
        <b>Purpose:</b> This report provides a comprehensive traceability analysis mapping claims 
        from the medical forensic evaluation against findings from VA radiology reports to identify 
        discrepancies, contradictions, and areas of alignment in the medical assessment of traumatic 
        versus degenerative spinal changes.
        """
        content.append(Paragraph(purpose_text, self.styles['Normal']))
        content.append(PageBreak())
        
        return content
    
    def _build_executive_summary(self, analyzer: ForensicClaimAnalyzer, mapper: FindingsMapper) -> List:
        """Build executive summary section."""
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Claims summary
        claims_summary = analyzer.generate_claims_summary()
        traceability_summary = mapper.generate_traceability_summary()
        
        summary_text = f"""
        This analysis examined <b>{claims_summary['total_claims']} medical claims</b> extracted from 
        the forensic evaluation against corresponding findings in VA radiology reports. 
        
        <b>Key Findings:</b>
        <br/>• <b>{traceability_summary.get('high_confidence_contradictions', 0)} high-confidence contradictions</b> 
        were identified between forensic claims and VA assessments
        <br/>• <b>{claims_summary.get('high_confidence_claims', 0)} high-confidence forensic claims</b> 
        challenge VA diagnostic conclusions
        <br/>• <b>{traceability_summary.get('total_discrepancies_identified', 0)} specific discrepancies</b> 
        were documented across all anatomical regions examined
        <br/>• Average mapping confidence score: <b>{traceability_summary.get('average_confidence_score', 0):.2f}</b>
        
        <b>Primary Areas of Concern:</b>
        <br/>1. Contradictory assessments of vertebral morphology at cervical levels
        <br/>2. Disagreement on the significance of height loss measurements
        <br/>3. Methodological limitations in VA imaging protocols
        <br/>4. Incomplete correlation of clinical symptoms with imaging findings
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_claims_analysis_section(self, analyzer: ForensicClaimAnalyzer) -> List:
        """Build claims analysis section."""
        content = []
        
        content.append(Paragraph("Forensic Claims Analysis", self.styles['SectionHeader']))
        
        # Claims by category
        for category in ClaimCategory:
            claims = analyzer.get_claims_by_category(category)
            if not claims:
                continue
                
            content.append(Paragraph(
                f"{category.value.replace('_', ' ').title()} ({len(claims)} claims)",
                self.styles['SubsectionHeader']
            ))
            
            for claim in claims:
                claim_text = f"""
                <b>Claim {claim.claim_id}:</b> {claim.claim_text}
                <br/><i>Source:</i> {claim.source_section}
                <br/><i>Confidence:</i> {claim.confidence_level:.2f}
                """
                if claim.anatomical_location:
                    claim_text += f"<br/><i>Location:</i> {claim.anatomical_location}"
                
                content.append(Paragraph(claim_text, self.styles['Finding']))
                content.append(Spacer(1, 10))
        
        return content
    
    def _build_traceability_section(self, mapper: FindingsMapper) -> List:
        """Build traceability mapping section."""
        content = []
        
        content.append(Paragraph("Claim-to-Findings Traceability Mapping", self.styles['SectionHeader']))
        
        # Summary table
        summary = mapper.generate_traceability_summary()
        mapping_data = [
            ["Mapping Status", "Count", "Percentage"],
            ["Contradicted", str(summary['mapping_status_breakdown'].get('contradicted', 0)), 
             f"{(summary['mapping_status_breakdown'].get('contradicted', 0) / summary['total_claims_analyzed'] * 100):.1f}%"],
            ["Supported", str(summary['mapping_status_breakdown'].get('supported', 0)),
             f"{(summary['mapping_status_breakdown'].get('supported', 0) / summary['total_claims_analyzed'] * 100):.1f}%"],
            ["Partially Supported", str(summary['mapping_status_breakdown'].get('partially_supported', 0)),
             f"{(summary['mapping_status_breakdown'].get('partially_supported', 0) / summary['total_claims_analyzed'] * 100):.1f}%"],
            ["No Correspondence", str(summary['mapping_status_breakdown'].get('no_correspondence', 0)),
             f"{(summary['mapping_status_breakdown'].get('no_correspondence', 0) / summary['total_claims_analyzed'] * 100):.1f}%"],
            ["Insufficient Data", str(summary['mapping_status_breakdown'].get('insufficient_data', 0)),
             f"{(summary['mapping_status_breakdown'].get('insufficient_data', 0) / summary['total_claims_analyzed'] * 100):.1f}%"]
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(mapping_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _build_detailed_comparison(self, mapper: FindingsMapper) -> List:
        """Build detailed findings comparison section."""
        content = []
        
        content.append(Paragraph("Detailed Claim-Finding Comparisons", self.styles['SectionHeader']))
        
        # Focus on contradicted and high-confidence mappings
        important_mappings = [
            r for r in mapper.mapping_results 
            if r.mapping_status in [MappingStatus.CONTRADICTED, MappingStatus.INSUFFICIENT_DATA] 
            or r.confidence_score >= 0.8
        ]
        
        for i, mapping in enumerate(important_mappings, 1):
            content.append(Paragraph(f"Comparison {i}: {mapping.claim.claim_id}", self.styles['SubsectionHeader']))
            
            # Claim details
            claim_text = f"""
            <b>Forensic Claim:</b> {mapping.claim.claim_text}
            <br/><b>Category:</b> {mapping.claim.category.value.replace('_', ' ').title()}
            <br/><b>Source Section:</b> {mapping.claim.source_section}
            <br/><b>Confidence Level:</b> {mapping.claim.confidence_level:.2f}
            """
            content.append(Paragraph(claim_text, self.styles['Normal']))
            
            # VA findings
            if mapping.va_findings:
                va_text = "<b>Corresponding VA Findings:</b><br/>"
                for finding in mapping.va_findings:
                    va_text += f"• <i>{finding.report_name} ({finding.report_date}):</i> {finding.finding_text}<br/>"
                content.append(Paragraph(va_text, self.styles['Normal']))
            
            # Mapping analysis
            content.append(Paragraph(f"<b>Mapping Status:</b> {mapping.mapping_status.value.replace('_', ' ').title()}", 
                                   self.styles['Normal']))
            content.append(Paragraph(f"<b>Analysis:</b> {mapping.analysis_notes}", self.styles['Normal']))
            
            # Evidence alignment
            if mapping.evidence_alignment:
                content.append(Paragraph("<b>Evidence Alignment:</b>", self.styles['Normal']))
                for evidence in mapping.evidence_alignment:
                    content.append(Paragraph(f"• {evidence}", self.styles['Alignment']))
            
            # Discrepancies
            if mapping.discrepancies:
                content.append(Paragraph("<b>Identified Discrepancies:</b>", self.styles['Normal']))
                for discrepancy in mapping.discrepancies:
                    content.append(Paragraph(f"• {discrepancy}", self.styles['Discrepancy']))
            
            content.append(Spacer(1, 15))
        
        return content
    
    def _build_conclusions_section(self, mapper: FindingsMapper) -> List:
        """Build conclusions and recommendations section."""
        content = []
        
        content.append(Paragraph("Conclusions and Recommendations", self.styles['SectionHeader']))
        
        summary = mapper.generate_traceability_summary()
        contradicted_count = summary['mapping_status_breakdown'].get('contradicted', 0)
        total_claims = summary['total_claims_analyzed']
        
        conclusions_text = f"""
        <b>Summary of Findings:</b>
        
        This traceability analysis reveals significant discrepancies between the forensic medical 
        evaluation and VA radiology assessments. Of {total_claims} claims analyzed, 
        {contradicted_count} ({(contradicted_count/total_claims*100):.1f}%) directly contradict 
        VA findings, indicating potential diagnostic disagreements that warrant further investigation.
        
        <b>Key Discrepancies Identified:</b>
        
        1. <b>Vertebral Morphology Assessment:</b> Forensic analysis identifies wedge deformities 
        at cervical levels that contradict VA reports of "normal vertebral heights."
        
        2. <b>Imaging Protocol Limitations:</b> Forensic evaluation critiques VA methodology, 
        citing insufficient slice thickness and lack of sagittal emphasis for detecting chronic 
        traumatic changes.
        
        3. <b>Clinical Correlation Gaps:</b> VA reports fail to correlate documented symptoms 
        (dizziness) with potential traumatic sequelae identified in forensic analysis.
        
        4. <b>Measurement Discrepancies:</b> Quantitative height loss measurements differ between 
        assessments, suggesting different analytical approaches or measurement techniques.
        
        <b>Recommendations:</b>
        
        1. <b>Re-evaluation with Enhanced Protocols:</b> Consider repeat imaging with optimized 
        sequences specifically designed for traumatic change detection.
        
        2. <b>Independent Review:</b> Obtain additional independent radiological review focusing 
        on areas of disagreement.
        
        3. <b>Clinical Correlation:</b> Ensure comprehensive integration of clinical symptoms 
        with imaging findings.
        
        4. <b>Documentation Standards:</b> Establish standardized measurement protocols to 
        reduce inter-observer variability.
        
        <b>Clinical Significance:</b>
        
        The identified discrepancies have potential implications for patient care, disability 
        assessments, and treatment planning. The forensic analysis suggests that traumatic 
        changes may have been under-recognized in the initial VA assessments, which could 
        impact appropriate treatment and compensation decisions.
        """
        
        content.append(Paragraph(conclusions_text, self.styles['Normal']))
        
        return content