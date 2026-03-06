"""
Annotation Generator Module for MRI Enhancement Tool

Converts DICOM images to PNG format with medical overlays showing findings.
Generates circles, arrows, and text annotations for traumatic markers.
"""

import os
import logging
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pydicom

from .config import MRIConfig, AnnotationSettings
from .image_analyzer import Finding, FindingType, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class AnnotationStyle:
    """Style settings for a specific annotation type."""
    color: Tuple[int, int, int]  # BGR color
    thickness: int
    font_scale: float
    font_thickness: int


class AnnotationGenerator:
    """Generates annotated PNG images from DICOM data with medical overlays."""
    
    def __init__(self, config: MRIConfig):
        """Initialize annotation generator with configuration."""
        self.config = config
        self.settings = config.annotation_settings
        self.logger = logging.getLogger(__name__)
        
        # Define annotation styles for different finding types
        self.styles = {
            FindingType.TRAUMATIC: AnnotationStyle(
                color=self.settings.trauma_color,
                thickness=self.settings.line_thickness,
                font_scale=self.settings.font_scale,
                font_thickness=self.settings.font_thickness
            ),
            FindingType.DEGENERATIVE: AnnotationStyle(
                color=self.settings.degenerative_color,
                thickness=self.settings.line_thickness,
                font_scale=self.settings.font_scale,
                font_thickness=self.settings.font_thickness
            ),
            FindingType.UNCERTAIN: AnnotationStyle(
                color=self.settings.uncertain_color,
                thickness=self.settings.line_thickness,
                font_scale=self.settings.font_scale,
                font_thickness=self.settings.font_thickness
            )
        }
        
    def generate_annotations(self, dicom_file_path: str, 
                           analysis_result: AnalysisResult,
                           output_dir: str) -> List[str]:
        """
        Generate annotated PNG images for key slices.
        
        Args:
            dicom_file_path: Path to DICOM file or series
            analysis_result: Analysis results with findings
            output_dir: Directory to save annotated images
            
        Returns:
            List of paths to generated annotated images
        """
        self.logger.info(f"Generating annotations for {len(analysis_result.key_slices)} key slices")
        
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        # Load DICOM data
        if os.path.isfile(dicom_file_path):
            # Single DICOM file
            ds = pydicom.dcmread(dicom_file_path)
            volume = self._extract_pixel_array(ds)
            if len(volume.shape) == 2:
                volume = volume[np.newaxis, ...]  # Add slice dimension
        else:
            # Directory with DICOM series - simplified approach
            raise NotImplementedError("Directory processing not implemented in this version")
            
        # Generate annotations for key slices
        for slice_idx in analysis_result.key_slices:
            if slice_idx < volume.shape[0]:
                annotated_image = self._create_annotated_slice(
                    volume[slice_idx], slice_idx, analysis_result)
                
                # Save annotated image
                output_filename = f"slice_{slice_idx:03d}_annotated.png"
                output_path = os.path.join(output_dir, output_filename)
                
                success = cv2.imwrite(output_path, annotated_image)
                if success:
                    generated_files.append(output_path)
                    self.logger.debug(f"Saved annotated image: {output_path}")
                else:
                    self.logger.warning(f"Failed to save image: {output_path}")
                    
        self.logger.info(f"Generated {len(generated_files)} annotated images")
        return generated_files
        
    def _extract_pixel_array(self, ds: pydicom.Dataset) -> np.ndarray:
        """Extract and normalize pixel array from DICOM dataset."""
        pixel_array = ds.pixel_array.astype(np.float32)
        
        # Apply DICOM scaling if present
        if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
            pixel_array = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
            
        # Apply window/level if present
        if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
            center = ds.WindowCenter
            width = ds.WindowWidth
            
            # Handle multiple window settings
            if isinstance(center, (list, tuple)):
                center = center[0]
            if isinstance(width, (list, tuple)):
                width = width[0]
                
            # Apply windowing
            pixel_array = self._apply_windowing(pixel_array, center, width)
            
        # Normalize to 0-255 range
        pixel_array = cv2.normalize(pixel_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        return pixel_array
        
    def _apply_windowing(self, image: np.ndarray, center: float, width: float) -> np.ndarray:
        """Apply DICOM windowing (window center/width)."""
        min_value = center - width / 2
        max_value = center + width / 2
        
        # Clip values to window range
        windowed = np.clip(image, min_value, max_value)
        
        # Scale to 0-1 range
        if max_value > min_value:
            windowed = (windowed - min_value) / (max_value - min_value)
        else:
            windowed = windowed - min_value
            
        return windowed
        
    def _create_annotated_slice(self, slice_image: np.ndarray, 
                              slice_idx: int,
                              analysis_result: AnalysisResult) -> np.ndarray:
        """Create annotated version of a single slice."""
        # Convert grayscale to BGR for color annotations
        if len(slice_image.shape) == 2:
            annotated = cv2.cvtColor(slice_image, cv2.COLOR_GRAY2BGR)
        else:
            annotated = slice_image.copy()
            
        # Resize if needed
        target_size = self.settings.image_size
        if annotated.shape[:2] != target_size:
            annotated = cv2.resize(annotated, target_size)
            
        # Scale coordinates for resizing
        height_scale = target_size[1] / slice_image.shape[0]
        width_scale = target_size[0] / slice_image.shape[1]
        
        # Add findings annotations (filter out low confidence findings < 50% and low anterior ratios < 50%)
        findings_on_slice = [f for f in analysis_result.findings 
                           if slice_idx in f.slice_numbers and f.confidence >= 0.5 
                           and (f.measurements.get("anterior_ratio", 1.0) >= 0.5 or "anterior_ratio" not in f.measurements)]
        
        for finding in findings_on_slice:
            self._add_finding_annotation(annotated, finding, width_scale, height_scale)
            
        # Add slice information
        self._add_slice_info(annotated, slice_idx, len(findings_on_slice))
        
        # Add legend
        self._add_legend(annotated)
        
        return annotated
        
    def _add_finding_annotation(self, image: np.ndarray, finding: Finding,
                              width_scale: float, height_scale: float):
        """Add annotation for a specific finding."""
        style = self.styles.get(finding.finding_type, self.styles[FindingType.UNCERTAIN])
        
        # Scale coordinates
        x = int(finding.coordinates[0] * width_scale)
        y = int(finding.coordinates[1] * height_scale)
        
        # Choose annotation type based on finding category
        if finding.category == "vertebral_morphology":
            self._add_vertebral_annotation(image, finding, x, y, style)
        elif finding.category == "cord_neural":
            self._add_cord_annotation(image, finding, x, y, style)
        elif finding.category == "disc_changes":
            self._add_disc_annotation(image, finding, x, y, style)
        else:
            self._add_generic_annotation(image, finding, x, y, style)
            
    def _add_vertebral_annotation(self, image: np.ndarray, finding: Finding,
                                x: int, y: int, style: AnnotationStyle):
        """Add annotation for vertebral findings."""
        if "wedge" in finding.subcategory:
            # Draw arrow pointing to wedge fracture
            arrow_start = (x - 30, y - 30)
            arrow_end = (x, y)
            
            cv2.arrowedLine(image, arrow_start, arrow_end, 
                          style.color, style.thickness,
                          tipLength=self.settings.arrow_tip_length)
            
            # Add text label
            label = "Wedge Fracture"
            if self.settings.include_measurements and "anterior_ratio" in finding.measurements:
                ratio = finding.measurements["anterior_ratio"]
                label += f" ({ratio:.1%})"
                
        elif "burst" in finding.subcategory:
            # Draw circle around burst fracture
            radius = 25
            cv2.circle(image, (x, y), radius, style.color, style.thickness)
            
            label = "Burst Fracture"
            
        else:
            # Generic vertebral finding
            cv2.circle(image, (x, y), 15, style.color, style.thickness)
            label = finding.subcategory.replace("_", " ").title()
            
        # Add text label
        self._add_text_label(image, label, x, y - 40, style)
        
    def _add_cord_annotation(self, image: np.ndarray, finding: Finding,
                           x: int, y: int, style: AnnotationStyle):
        """Add annotation for spinal cord findings."""
        if "syrinx" in finding.subcategory:
            # Draw circle for syrinx
            radius = 12
            cv2.circle(image, (x, y), radius, style.color, style.thickness)
            
            # Add inner circle to show cavity
            cv2.circle(image, (x, y), radius//2, style.color, 1)
            
            label = "Syrinx"
            if self.settings.include_measurements and "width_ratio" in finding.measurements:
                width_ratio = finding.measurements["width_ratio"]
                label += f" ({width_ratio:.1%})"
                
        else:
            # Generic cord finding
            cv2.circle(image, (x, y), 10, style.color, style.thickness)
            label = finding.subcategory.replace("_", " ").title()
            
        self._add_text_label(image, label, x, y + 25, style)
        
    def _add_disc_annotation(self, image: np.ndarray, finding: Finding,
                           x: int, y: int, style: AnnotationStyle):
        """Add annotation for disc findings."""
        # Draw rectangle for disc
        rect_width, rect_height = 20, 8
        top_left = (x - rect_width//2, y - rect_height//2)
        bottom_right = (x + rect_width//2, y + rect_height//2)
        
        cv2.rectangle(image, top_left, bottom_right, style.color, style.thickness)
        
        label = finding.subcategory.replace("_", " ").title()
        self._add_text_label(image, label, x, y - 20, style)
        
    def _add_generic_annotation(self, image: np.ndarray, finding: Finding,
                              x: int, y: int, style: AnnotationStyle):
        """Add generic annotation for other findings."""
        cv2.circle(image, (x, y), 12, style.color, style.thickness)
        
        label = finding.subcategory.replace("_", " ").title()
        self._add_text_label(image, label, x, y - 20, style)
        
    def _add_text_label(self, image: np.ndarray, text: str, x: int, y: int,
                       style: AnnotationStyle):
        """Add text label with background for better visibility."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, style.font_scale, style.font_thickness)
        
        # Adjust position to keep text on image
        text_x = max(5, min(x - text_width//2, image.shape[1] - text_width - 5))
        text_y = max(text_height + 5, min(y, image.shape[0] - 5))
        
        # Draw background rectangle
        bg_color = (0, 0, 0)  # Black background
        cv2.rectangle(image, 
                     (text_x - 2, text_y - text_height - 2),
                     (text_x + text_width + 2, text_y + baseline + 2),
                     bg_color, -1)
        
        # Draw text
        cv2.putText(image, text, (text_x, text_y), font,
                   style.font_scale, style.color, style.font_thickness)
        
        # Add confidence score if enabled
        if self.settings.include_confidence_scores:
            # This would require the finding object to be passed
            pass
            
    def _add_slice_info(self, image: np.ndarray, slice_idx: int, finding_count: int):
        """Add slice information header."""
        info_text = f"Slice {slice_idx} - {finding_count} finding(s)"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        color = (255, 255, 255)  # White text
        
        # Position at top of image
        cv2.putText(image, info_text, (10, 25), font, font_scale, 
                   (0, 0, 0), font_thickness + 1)  # Black outline
        cv2.putText(image, info_text, (10, 25), font, font_scale, 
                   color, font_thickness)
        
    def _add_legend(self, image: np.ndarray):
        """Add legend showing color coding."""
        legend_items = [
            ("Traumatic", self.settings.trauma_color),
            ("Degenerative", self.settings.degenerative_color),
            ("Uncertain", self.settings.uncertain_color)
        ]
        
        # Position legend at bottom right
        start_x = image.shape[1] - 150
        start_y = image.shape[0] - 80
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        
        for i, (label, color) in enumerate(legend_items):
            y_pos = start_y + i * 20
            
            # Draw color indicator
            cv2.circle(image, (start_x, y_pos), 6, color, -1)
            
            # Draw label
            cv2.putText(image, label, (start_x + 15, y_pos + 5), 
                       font, font_scale, (255, 255, 255), font_thickness)
                       
    def create_overview_image(self, analysis_results: List[AnalysisResult],
                            output_path: str) -> str:
        """Create overview image showing all key findings."""
        # Create a summary visualization
        # This would combine multiple slices into a single overview
        # For now, return a placeholder
        
        overview = np.zeros((512, 1024, 3), dtype=np.uint8)
        
        # Add title
        title = "MRI Spine Analysis Overview"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overview, title, (300, 50), font, 1.5, (255, 255, 255), 2)
        
        # Add summary statistics
        total_findings = sum(len(result.findings) for result in analysis_results)
        traumatic_findings = sum(sum(1 for f in result.findings if f.finding_type == FindingType.TRAUMATIC)
                               for result in analysis_results)
        
        stats_text = [
            f"Total Findings: {total_findings}",
            f"Traumatic Findings: {traumatic_findings}",
            f"Series Analyzed: {len(analysis_results)}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(overview, text, (50, 150 + i * 30), font, 0.8, (255, 255, 255), 2)
            
        # Save overview
        cv2.imwrite(output_path, overview)
        self.logger.info(f"Created overview image: {output_path}")
        
        return output_path
        
    def batch_process_series(self, series_results: Dict[str, AnalysisResult],
                           dicom_files: Dict[str, str],
                           output_base_dir: str) -> Dict[str, List[str]]:
        """Batch process multiple series for annotation generation."""
        all_generated_files = {}
        
        for series_uid, analysis_result in series_results.items():
            if series_uid in dicom_files:
                # Create series-specific output directory
                series_output_dir = os.path.join(output_base_dir, f"series_{series_uid}")
                
                try:
                    generated_files = self.generate_annotations(
                        dicom_files[series_uid], analysis_result, series_output_dir)
                    all_generated_files[series_uid] = generated_files
                    
                except Exception as e:
                    self.logger.error(f"Error processing series {series_uid}: {e}")
                    all_generated_files[series_uid] = []
                    
        return all_generated_files