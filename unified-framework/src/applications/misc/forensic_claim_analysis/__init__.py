"""
Forensic Claim Analysis Module

This module provides functionality to analyze medical forensic reports and map
claims against findings for traceability reporting.

Key Features:
- Medical forensic report parsing
- Claim extraction and categorization
- Findings comparison and mapping
- Traceability report generation
"""

from src.applications.forensic_claim_analysis.claim_analyzer import ForensicClaimAnalyzer, MedicalClaim, ClaimCategory
from src.applications.forensic_claim_analysis.findings_mapper import FindingsMapper, ClaimMappingResult
from src.applications.forensic_claim_analysis.report_generator import ForensicTraceabilityReportGenerator

__version__ = "1.0.0"
__all__ = [
    "ForensicClaimAnalyzer",
    "MedicalClaim", 
    "ClaimCategory",
    "FindingsMapper",
    "ClaimMappingResult",
    "ForensicTraceabilityReportGenerator"
]