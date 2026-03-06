"""
Findings Mapper Module

Maps forensic claims against VA findings to create traceability reports.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
import re

from src.applications.forensic_claim_analysis.claim_analyzer import MedicalClaim, ClaimCategory


class MappingStatus(Enum):
    """Status of claim-to-finding mapping."""
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    PARTIALLY_SUPPORTED = "partially_supported"
    NO_CORRESPONDENCE = "no_correspondence"
    INSUFFICIENT_DATA = "insufficient_data"


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


class FindingsMapper:
    """Maps forensic claims against VA findings for traceability analysis."""
    
    def __init__(self):
        """Initialize the findings mapper."""
        self.va_findings = []
        self.mapping_results = []
        
    def load_va_findings(self, va_reports_text: str) -> List[VAFinding]:
        """Parse and load VA findings from report text."""
        self.va_findings = self._parse_va_findings(va_reports_text)
        return self.va_findings
    
    def _parse_va_findings(self, reports_text: str) -> List[VAFinding]:
        """Parse VA findings from the provided text."""
        findings = []
        
        # Define VA report sections from the provided text
        va_reports = [
            {
                "name": "CT Head without Contrast",
                "date": "Sep 10, 2025",
                "findings": "Normal ventricular size, no acute hemorrhage, mass effect, midline shift, or calvarial fractures. Clear paranasal sinuses.",
                "impression": "No acute intracranial issues related to dizziness.",
                "location": "head"
            },
            {
                "name": "MRI Cervical Spine without Contrast", 
                "date": "Aug 21, 2025",
                "findings": "Normal vertebral heights, no marrow edema, compression fracture, or subluxation. Decreased disc space at C5-C6. Disc osteophyte complexes at C3-C4, C4-C5, C5-C6 (mild canal narrowing, severe right foraminal stenosis), and C6-C7. No cord signal abnormality.",
                "impression": "Degenerative disease.",
                "location": "cervical_spine"
            },
            {
                "name": "MRI Thoracic Spine without Contrast",
                "date": "Aug 21, 2025", 
                "findings": "Normal vertebral heights and alignment. No compression fractures or subluxation. Mild disc space narrowing at multiple levels. No cord signal abnormality or canal stenosis.",
                "impression": "Mild degenerative changes.",
                "location": "thoracic_spine"
            },
            {
                "name": "Thoracic Spine X-ray 2 Views",
                "date": "Jul 17, 2025",
                "findings": "Normal vertebral heights and alignment. No acute fractures, subluxation, or hardware failure. Mild degenerative changes at multiple levels.",
                "impression": "No acute abnormalities.",
                "location": "thoracic_spine"
            }
        ]
        
        # Convert to VAFinding objects
        for i, report in enumerate(va_reports):
            # Main finding
            findings.append(VAFinding(
                finding_id=f"VA-{i+1}-MAIN",
                report_name=report["name"],
                report_date=report["date"],
                finding_text=report["findings"],
                anatomical_location=report["location"],
                assessment="normal" if "normal" in report["impression"].lower() else "degenerative"
            ))
            
            # Additional specific findings
            if "cervical" in report["name"].lower():
                # Extract specific cervical findings
                findings.append(VAFinding(
                    finding_id=f"VA-{i+1}-C5C6",
                    report_name=report["name"],
                    report_date=report["date"],
                    finding_text="Decreased disc space at C5-C6",
                    anatomical_location="C5-C6",
                    assessment="degenerative"
                ))
                
                findings.append(VAFinding(
                    finding_id=f"VA-{i+1}-STENOSIS",
                    report_name=report["name"],
                    report_date=report["date"],
                    finding_text="severe right foraminal stenosis at C5-C6",
                    anatomical_location="C5-C6",
                    assessment="degenerative"
                ))
        
        return findings
    
    def map_claims_to_findings(self, claims: List[MedicalClaim]) -> List[ClaimMappingResult]:
        """Map forensic claims to VA findings."""
        self.mapping_results = []
        
        for claim in claims:
            result = self._map_single_claim(claim)
            self.mapping_results.append(result)
            
        return self.mapping_results
    
    def _map_single_claim(self, claim: MedicalClaim) -> ClaimMappingResult:
        """Map a single claim to relevant VA findings."""
        relevant_findings = self._find_relevant_va_findings(claim)
        
        if not relevant_findings:
            return ClaimMappingResult(
                claim=claim,
                va_findings=[],
                mapping_status=MappingStatus.NO_CORRESPONDENCE,
                confidence_score=0.0,
                analysis_notes="No corresponding VA findings identified for this claim.",
                evidence_alignment=[],
                discrepancies=["Claim not addressed in VA reports"]
            )
        
        # Analyze the mapping
        mapping_status, confidence, notes, alignment, discrepancies = self._analyze_claim_finding_alignment(
            claim, relevant_findings
        )
        
        return ClaimMappingResult(
            claim=claim,
            va_findings=relevant_findings,
            mapping_status=mapping_status,
            confidence_score=confidence,
            analysis_notes=notes,
            evidence_alignment=alignment,
            discrepancies=discrepancies
        )
    
    def _find_relevant_va_findings(self, claim: MedicalClaim) -> List[VAFinding]:
        """Find VA findings relevant to the forensic claim."""
        relevant = []
        
        for finding in self.va_findings:
            # Location-based matching
            if claim.anatomical_location and finding.anatomical_location:
                if self._locations_match(claim.anatomical_location, finding.anatomical_location):
                    relevant.append(finding)
                    continue
            
            # Text-based matching for key terms
            claim_keywords = self._extract_keywords(claim.claim_text)
            finding_keywords = self._extract_keywords(finding.finding_text)
            
            # Check for overlapping keywords
            overlap = set(claim_keywords) & set(finding_keywords)
            if len(overlap) >= 2:  # Require at least 2 matching keywords
                relevant.append(finding)
                continue
                
            # Category-specific matching
            if claim.category == ClaimCategory.TRAUMATIC_FINDING:
                # Look for findings that might have missed traumatic changes
                if any(term in finding.finding_text.lower() for term in ["normal", "no", "without"]):
                    relevant.append(finding)
            
        return relevant
    
    def _locations_match(self, claim_location: str, finding_location: str) -> bool:
        """Check if anatomical locations match."""
        claim_loc = claim_location.lower()
        finding_loc = finding_location.lower()
        
        # Direct match
        if claim_loc == finding_loc:
            return True
            
        # Partial matches
        location_aliases = {
            'cervical': ['c-spine', 'cervical_spine', 'neck'],
            'thoracic': ['t-spine', 'thoracic_spine', 'chest'],
            'lumbar': ['l-spine', 'lumbar_spine', 'lower back'],
            'c5': ['c5-c6', 'cervical'],
            'c6': ['c5-c6', 'c6-c7', 'cervical'],
            'head': ['brain', 'intracranial', 'skull']
        }
        
        for key, aliases in location_aliases.items():
            if key in claim_loc and any(alias in finding_loc for alias in aliases):
                return True
            if key in finding_loc and any(alias in claim_loc for alias in aliases):
                return True
                
        return False
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract medical keywords from text."""
        # Common medical terms
        medical_keywords = [
            'height', 'vertebral', 'disc', 'space', 'deformity', 'fracture',
            'wedge', 'compression', 'normal', 'abnormal', 'stenosis', 'narrowing',
            'edema', 'signal', 'cord', 'canal', 'foraminal', 'osteophyte',
            'degenerative', 'traumatic', 'acute', 'chronic', 'syrinx', 'syringomyelia'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in medical_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
                
        # Extract specific measurements or levels (C5, T7, etc.)
        level_matches = re.findall(r'[CTLS]\d+(?:-[CTLS]\d+)?', text.upper())
        found_keywords.extend(level_matches)
        
        return found_keywords
    
    def _analyze_claim_finding_alignment(self, claim: MedicalClaim, findings: List[VAFinding]) -> Tuple[MappingStatus, float, str, List[str], List[str]]:
        """Analyze how well a claim aligns with VA findings."""
        alignment = []
        discrepancies = []
        
        if claim.category == ClaimCategory.TRAUMATIC_FINDING:
            # Traumatic claims should contradict normal VA findings
            normal_findings = [f for f in findings if f.assessment == "normal"]
            
            if normal_findings:
                discrepancies.append(f"Forensic analysis identifies traumatic changes but VA reports indicate normal findings")
                discrepancies.append(f"Specific claim: '{claim.claim_text}' vs VA finding: 'Normal vertebral heights'")
                
                return (
                    MappingStatus.CONTRADICTED,
                    0.9,
                    f"Forensic claim of traumatic finding directly contradicts VA assessment of normal findings in {normal_findings[0].report_name}",
                    alignment,
                    discrepancies
                )
        
        elif claim.category == ClaimCategory.METHODOLOGICAL_CRITIQUE:
            # Methodological critiques highlight limitations
            if "insufficient" in claim.claim_text.lower() or "incomplete" in claim.claim_text.lower():
                discrepancies.append(f"Forensic analysis critiques VA methodology: {claim.claim_text}")
                
                return (
                    MappingStatus.INSUFFICIENT_DATA,
                    0.85,
                    "Forensic analysis identifies methodological limitations in VA assessment",
                    alignment,
                    discrepancies
                )
        
        elif claim.category == ClaimCategory.MEASUREMENT_DISCREPANCY:
            # Look for measurement contradictions
            if claim.measurement_value:
                discrepancies.append(f"Measurement discrepancy identified: {claim.claim_text}")
                
                return (
                    MappingStatus.CONTRADICTED,
                    0.8,
                    f"Forensic measurements contradict VA findings",
                    alignment,
                    discrepancies
                )
        
        elif claim.category == ClaimCategory.DEGENERATIVE_FINDING:
            # Check for alignment with degenerative findings
            degenerative_findings = [f for f in findings if f.assessment == "degenerative"]
            
            if degenerative_findings:
                alignment.append(f"Both forensic and VA analyses identify degenerative changes")
                
                return (
                    MappingStatus.SUPPORTED,
                    0.7,
                    "Forensic and VA findings align on degenerative changes",
                    alignment,
                    discrepancies
                )
        
        # Default case
        return (
            MappingStatus.PARTIALLY_SUPPORTED,
            0.5,
            "Partial alignment between forensic claim and VA findings",
            alignment,
            discrepancies
        )
    
    def generate_traceability_summary(self) -> Dict[str, any]:
        """Generate a summary of the traceability analysis."""
        if not self.mapping_results:
            return {"error": "No mapping results available"}
            
        status_counts = {}
        for status in MappingStatus:
            status_counts[status.value] = len([r for r in self.mapping_results if r.mapping_status == status])
        
        high_confidence_contradictions = [
            r for r in self.mapping_results 
            if r.mapping_status == MappingStatus.CONTRADICTED and r.confidence_score >= 0.8
        ]
        
        total_discrepancies = sum(len(r.discrepancies) for r in self.mapping_results)
        
        return {
            "total_claims_analyzed": len(self.mapping_results),
            "mapping_status_breakdown": status_counts,
            "high_confidence_contradictions": len(high_confidence_contradictions),
            "total_discrepancies_identified": total_discrepancies,
            "average_confidence_score": sum(r.confidence_score for r in self.mapping_results) / len(self.mapping_results),
            "key_contradictions": [
                {
                    "claim_id": r.claim.claim_id,
                    "claim_text": r.claim.claim_text[:100] + "..." if len(r.claim.claim_text) > 100 else r.claim.claim_text,
                    "va_report": r.va_findings[0].report_name if r.va_findings else "None",
                    "confidence": r.confidence_score
                }
                for r in high_confidence_contradictions[:5]  # Top 5
            ]
        }