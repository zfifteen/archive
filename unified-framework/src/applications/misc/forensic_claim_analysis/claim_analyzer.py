"""
Claim Analyzer Module

Analyzes medical forensic reports and extracts claims for traceability mapping.
"""

import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple


class ClaimCategory(Enum):
    """Categories of medical claims in forensic reports."""
    TRAUMATIC_FINDING = "traumatic_finding"
    DEGENERATIVE_FINDING = "degenerative_finding"
    NORMAL_FINDING = "normal_finding"
    METHODOLOGICAL_CRITIQUE = "methodological_critique"
    MEASUREMENT_DISCREPANCY = "measurement_discrepancy"
    ASSESSMENT_CRITIQUE = "assessment_critique"


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


class ForensicClaimAnalyzer:
    """Analyzes forensic medical reports and extracts claims."""
    
    def __init__(self):
        """Initialize the forensic claim analyzer."""
        self.claims = []
        self.patient_info = {}
        self.report_metadata = {}
        
    def parse_forensic_report(self, report_text: str) -> Dict[str, any]:
        """Parse the complete forensic report and extract structured data."""
        # Extract patient information
        self.patient_info = self._extract_patient_info(report_text)
        
        # Extract report metadata
        self.report_metadata = self._extract_report_metadata(report_text)
        
        # Extract claims from different sections
        self.claims = self._extract_claims(report_text)
        
        return {
            "patient_info": self.patient_info,
            "report_metadata": self.report_metadata,
            "claims": self.claims,
            "total_claims": len(self.claims)
        }
    
    def _extract_patient_info(self, report_text: str) -> Dict[str, str]:
        """Extract patient information from the report."""
        patient_info = {}
        
        # Extract basic patient data
        age_match = re.search(r'Age:\s*(\d+)', report_text)
        if age_match:
            patient_info['age'] = age_match.group(1)
            
        gender_match = re.search(r'Gender:\s*(\w+)', report_text)
        if gender_match:
            patient_info['gender'] = gender_match.group(1)
            
        # Extract group ID if present
        group_id_match = re.search(r'Group ID #:\s*\[([^\]]+)\]', report_text)
        if group_id_match:
            patient_info['group_id'] = group_id_match.group(1)
            
        return patient_info
    
    def _extract_report_metadata(self, report_text: str) -> Dict[str, str]:
        """Extract report metadata."""
        metadata = {}
        
        # Extract evaluator info
        evaluator_match = re.search(r'Evaluator:\s*\[([^\]]+)\]', report_text)
        if evaluator_match:
            metadata['evaluator'] = evaluator_match.group(1)
            
        # Extract evaluation date
        eval_date_match = re.search(r'Date of Evaluation:\s*([^\n\r]+)', report_text)
        if eval_date_match:
            metadata['evaluation_date'] = eval_date_match.group(1).strip()
            
        # Extract report generation date
        report_date_match = re.search(r'Report Generated:\s*([^\n\r]+)', report_text)
        if report_date_match:
            metadata['report_date'] = report_date_match.group(1).strip()
            
        # Extract analysis statistics
        studies_match = re.search(r'Studies Analyzed:\s*(\d+)', report_text)
        if studies_match:
            metadata['studies_analyzed'] = int(studies_match.group(1))
            
        series_match = re.search(r'Series Analyzed:\s*(\d+)', report_text)
        if series_match:
            metadata['series_analyzed'] = int(series_match.group(1))
            
        findings_match = re.search(r'Total Findings:\s*(\d+)', report_text)
        if findings_match:
            metadata['total_findings'] = int(findings_match.group(1))
            
        return metadata
    
    def _extract_claims(self, report_text: str) -> List[MedicalClaim]:
        """Extract medical claims from the forensic report."""
        claims = []
        claim_counter = 1
        
        # Extract VA report critique claims
        va_sections = self._extract_va_report_sections(report_text)
        
        for section_name, section_text in va_sections.items():
            section_claims = self._analyze_va_section(section_name, section_text, claim_counter)
            claims.extend(section_claims)
            claim_counter += len(section_claims)
            
        # Extract overall assessment claims
        overall_claims = self._extract_overall_assessment_claims(report_text, claim_counter)
        claims.extend(overall_claims)
        
        return claims
    
    def _extract_va_report_sections(self, report_text: str) -> Dict[str, str]:
        """Extract VA report sections for analysis."""
        sections = {}
        
        # Pattern to match numbered VA report sections
        section_pattern = r'(\d+\.\s+[^(]+\([^)]+\))\s*(.*?)(?=\d+\.\s+[^(]+\([^)]+\)|$)'
        matches = re.findall(section_pattern, report_text, re.DOTALL)
        
        for header, content in matches:
            sections[header.strip()] = content.strip()
            
        return sections
    
    def _analyze_va_section(self, section_name: str, section_text: str, start_id: int) -> List[MedicalClaim]:
        """Analyze a VA report section and extract claims."""
        claims = []
        claim_id = start_id
        
        # Extract VA findings
        va_findings_match = re.search(r'VA Findings:\s*(.*?)(?=My Assessment:|$)', section_text, re.DOTALL)
        if va_findings_match:
            va_findings = va_findings_match.group(1).strip()
            
            # Create claim for VA findings
            claims.append(MedicalClaim(
                claim_id=f"VA-{claim_id}",
                category=ClaimCategory.NORMAL_FINDING if "normal" in va_findings.lower() else ClaimCategory.DEGENERATIVE_FINDING,
                source_section=section_name,
                claim_text=va_findings,
                va_report_reference=section_name,
                confidence_level=0.8
            ))
            claim_id += 1
        
        # Extract forensic assessment claims
        assessment_match = re.search(r'My Assessment:\s*(.*?)$', section_text, re.DOTALL)
        if assessment_match:
            assessment_text = assessment_match.group(1).strip()
            
            # Look for specific claims in the assessment
            assessment_claims = self._extract_assessment_claims(assessment_text, section_name, claim_id)
            claims.extend(assessment_claims)
            
        return claims
    
    def _extract_assessment_claims(self, assessment_text: str, section_name: str, start_id: int) -> List[MedicalClaim]:
        """Extract claims from forensic assessment text."""
        claims = []
        claim_id = start_id
        
        # Look for traumatic findings claims
        traumatic_patterns = [
            r'wedge deformities?\s+at\s+([A-Z]\d+-[A-Z]\d+)',
            r'focal[,\s]+asymmetric changes',
            r'post-traumatic syringomyelia',
            r'chronic traumatic sequelae',
            r'combat injury'
        ]
        
        for pattern in traumatic_patterns:
            matches = re.finditer(pattern, assessment_text, re.IGNORECASE)
            for match in matches:
                location = match.group(1) if match.groups() else None
                claims.append(MedicalClaim(
                    claim_id=f"TRAUMATIC-{claim_id}",
                    category=ClaimCategory.TRAUMATIC_FINDING,
                    source_section=section_name,
                    claim_text=match.group(0),
                    anatomical_location=location,
                    confidence_level=0.9
                ))
                claim_id += 1
        
        # Look for methodological critique claims
        critique_patterns = [
            r'insufficient to detect',
            r'incomplete assessment',
            r'did not correlate',
            r'contradicting',
            r'leading to an incomplete assessment'
        ]
        
        for pattern in critique_patterns:
            matches = re.finditer(pattern, assessment_text, re.IGNORECASE)
            for match in matches:
                claims.append(MedicalClaim(
                    claim_id=f"CRITIQUE-{claim_id}",
                    category=ClaimCategory.METHODOLOGICAL_CRITIQUE,
                    source_section=section_name,
                    claim_text=match.group(0),
                    confidence_level=0.85
                ))
                claim_id += 1
        
        # Look for measurement discrepancy claims
        measurement_patterns = [
            r'height loss ratios?\s*[<>]\s*(\d+\.?\d*)',
            r'decreased disc space',
            r'(\d+)\s*mm\s*axial slices'
        ]
        
        for pattern in measurement_patterns:
            matches = re.finditer(pattern, assessment_text, re.IGNORECASE)
            for match in matches:
                value = None
                if match.groups():
                    try:
                        value = float(match.group(1))
                    except (ValueError, IndexError):
                        pass
                        
                claims.append(MedicalClaim(
                    claim_id=f"MEASUREMENT-{claim_id}",
                    category=ClaimCategory.MEASUREMENT_DISCREPANCY,
                    source_section=section_name,
                    claim_text=match.group(0),
                    measurement_value=value,
                    confidence_level=0.9
                ))
                claim_id += 1
                
        return claims
    
    def _extract_overall_assessment_claims(self, report_text: str, start_id: int) -> List[MedicalClaim]:
        """Extract claims from overall assessment section."""
        claims = []
        
        # Look for overall assessment
        overall_match = re.search(r'Overall Assessment:\s*(.*?)(?=Executive Summary|$)', report_text, re.DOTALL)
        if overall_match:
            overall_text = overall_match.group(1).strip()
            
            if "traumatic changes identified" in overall_text.lower():
                claims.append(MedicalClaim(
                    claim_id=f"OVERALL-{start_id}",
                    category=ClaimCategory.TRAUMATIC_FINDING,
                    source_section="Overall Assessment",
                    claim_text=overall_text,
                    confidence_level=0.95
                ))
                
        return claims
    
    def get_claims_by_category(self, category: ClaimCategory) -> List[MedicalClaim]:
        """Get all claims of a specific category."""
        return [claim for claim in self.claims if claim.category == category]
    
    def get_claims_by_location(self, location: str) -> List[MedicalClaim]:
        """Get all claims related to a specific anatomical location."""
        return [claim for claim in self.claims if claim.anatomical_location and location.lower() in claim.anatomical_location.lower()]
    
    def generate_claims_summary(self) -> Dict[str, any]:
        """Generate a summary of extracted claims."""
        category_counts = {}
        for category in ClaimCategory:
            category_counts[category.value] = len(self.get_claims_by_category(category))
            
        return {
            "total_claims": len(self.claims),
            "category_breakdown": category_counts,
            "high_confidence_claims": len([c for c in self.claims if c.confidence_level >= 0.9]),
            "anatomical_locations": list(set([c.anatomical_location for c in self.claims if c.anatomical_location]))
        }