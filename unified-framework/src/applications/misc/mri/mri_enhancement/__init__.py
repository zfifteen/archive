"""
MRI Enhancement Tool for DICOM-based Spine Analysis

This module provides comprehensive analysis of spine MRI DICOM files to differentiate
between traumatic and degenerative disorders, addressing misdiagnosis at VA facilities.

Key Features:
- DICOM scanning and validation
- Spine MRI analysis for traumatic vs degenerative changes
- Annotation generation with medical overlays
- Comprehensive PDF report generation
- HIPAA-compliant data handling

Authors: Copilot (Implementation)
Attribution: Based on medical requirements for VA facility diagnosis improvement
"""

from .dicom_scanner import DICOMScanner
from .image_analyzer import SpineMRIAnalyzer
from .annotation_generator import AnnotationGenerator
from .report_generator import ReportGenerator
from .config import MRIConfig

__version__ = "1.0.0"
__all__ = [
    "DICOMScanner",
    "SpineMRIAnalyzer", 
    "AnnotationGenerator",
    "ReportGenerator",
    "MRIConfig"
]