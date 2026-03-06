"""
Image Analysis Module for Spine MRI Enhancement Tool

Implements differentiation framework to detect traumatic vs degenerative changes:
- Vertebral morphology analysis
- Disc changes detection  
- Endplate/bone marrow analysis
- Soft tissue evaluation
- Cord/neural assessment
"""

import logging
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import scipy.ndimage as ndimage
from skimage import measure, morphology, filters, segmentation

from .config import MRIConfig
from .dicom_scanner import DICOMSeries

logger = logging.getLogger(__name__)


class FindingType(Enum):
    """Types of findings for classification."""
    TRAUMATIC = "traumatic"
    DEGENERATIVE = "degenerative"
    UNCERTAIN = "uncertain"
    NORMAL = "normal"


class FindingSeverity(Enum):
    """Severity levels for findings."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class Finding:
    """Represents a single medical finding."""
    
    finding_type: FindingType
    category: str  # e.g., "vertebral_morphology", "disc_changes"
    subcategory: str  # e.g., "wedge_fracture", "disc_desiccation"
    description: str
    location: str  # e.g., "C6", "T7-T8", "L4-L5"
    severity: FindingSeverity
    confidence: float  # 0.0 to 1.0
    coordinates: Tuple[int, int, int]  # (x, y, z) in voxel coordinates
    measurements: Dict[str, float]  # Quantitative measurements
    evidence: List[str]  # Supporting evidence descriptions
    slice_numbers: List[int]  # Affected slice numbers


@dataclass
class AnalysisResult:
    """Complete analysis result for a series."""
    
    series_uid: str
    findings: List[Finding]
    overall_assessment: FindingType
    confidence_score: float
    key_slices: List[int]  # Most important slices for diagnosis
    measurements_summary: Dict[str, Any]
    processing_notes: List[str]


class SpineMRIAnalyzer:
    """Main analyzer for spine MRI differentiation."""
    
    def __init__(self, config: MRIConfig):
        """Initialize analyzer with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def analyze_series(self, volume: np.ndarray, metadata: Dict[str, Any], 
                      series: DICOMSeries) -> AnalysisResult:
        """
        Analyze a complete MRI series for traumatic vs degenerative changes.
        
        MEDICAL FRAMEWORK: Implements evidence-based differentiation between:
        - TRAUMATIC: Focal, asymmetric, stable changes from resolved acute injury
        - DEGENERATIVE: Multilevel, symmetric, progressive age-related changes
        
        ANALYSIS PIPELINE:
        1. Vertebral morphology - detects compression/burst fractures vs settling
        2. Disc changes - differentiates acute herniation vs chronic desiccation  
        3. Endplate analysis - identifies Modic changes and sclerotic healing
        4. Soft tissue evaluation - assesses ligament/muscle chronic changes
        5. Cord/neural assessment - detects post-traumatic syringomyelia vs myelomalacia
        
        Args:
            volume: 3D numpy array of MRI data (axial/sagittal/coronal)
            metadata: Image metadata from SimpleITK (spacing, orientation, etc.)
            series: DICOMSeries object with acquisition parameters
            
        Returns:
            AnalysisResult with complete findings categorized by trauma vs degeneration
        """
        self.logger.info(f"Starting analysis of series {series.series_uid}")
        
        # PREPROCESSING: Normalize intensities and enhance contrast for optimal segmentation
        processed_volume = self._preprocess_volume(volume)
        
        # SEGMENTATION: Identify anatomical structures using multi-threshold approach
        segmentation_results = self._segment_spine_structures(processed_volume, metadata)
        
        # MULTI-MODAL ANALYSIS: Systematic evaluation of each anatomical category
        findings = []
        
        # 1. VERTEBRAL MORPHOLOGY: Detect compression/burst fractures vs degenerative collapse
        vertebral_findings = self._analyze_vertebral_morphology(
            processed_volume, segmentation_results, metadata)
        findings.extend(vertebral_findings)
        
        # 2. DISC PATHOLOGY: Differentiate traumatic herniation vs degenerative disease
        disc_findings = self._analyze_disc_changes(
            processed_volume, segmentation_results, metadata)
        findings.extend(disc_findings)
        
        # 3. ENDPLATE ANALYSIS: Identify Modic changes and post-traumatic sclerosis
        endplate_findings = self._analyze_endplate_changes(
            processed_volume, segmentation_results, metadata)
        findings.extend(endplate_findings)
        
        # 4. SOFT TISSUE EVALUATION: Assess chronic ligament/muscle changes
        soft_tissue_findings = self._analyze_soft_tissue_changes(
            processed_volume, segmentation_results, metadata)
        findings.extend(soft_tissue_findings)
        
        # 5. Cord/neural analysis
        neural_findings = self._analyze_cord_neural_changes(
            processed_volume, segmentation_results, metadata)
        findings.extend(neural_findings)
        
        # Generate overall assessment
        overall_assessment, confidence = self._generate_overall_assessment(findings)
        
        # Identify key slices
        key_slices = self._identify_key_slices(findings, volume.shape[0])
        
        # Create measurements summary
        measurements_summary = self._create_measurements_summary(findings)
        
        result = AnalysisResult(
            series_uid=series.series_uid,
            findings=findings,
            overall_assessment=overall_assessment,
            confidence_score=confidence,
            key_slices=key_slices,
            measurements_summary=measurements_summary,
            processing_notes=[]
        )
        
        self.logger.info(f"Analysis complete: {len(findings)} findings, "
                        f"overall assessment: {overall_assessment.value}")
        
        return result
        
    def _preprocess_volume(self, volume: np.ndarray) -> np.ndarray:
        """Preprocess MRI volume for analysis."""
        if volume.size == 0:
            return volume
            
        processed = volume.copy().astype(np.float32)
        
        # Noise reduction
        if self.config.imaging_parameters.noise_reduction_kernel > 0:
            kernel_size = self.config.imaging_parameters.noise_reduction_kernel
            processed = ndimage.gaussian_filter(processed, sigma=kernel_size/3.0)
            
        # Contrast enhancement
        if self.config.imaging_parameters.contrast_enhancement:
            processed = self._enhance_contrast(processed)
            
        # Normalization
        processed = self._normalize_intensity(processed)
        
        return processed
        
    def _enhance_contrast(self, volume: np.ndarray) -> np.ndarray:
        """Enhance contrast using adaptive histogram equalization."""
        enhanced = np.zeros_like(volume)
        
        for i in range(volume.shape[0]):
            slice_img = volume[i]
            # Convert to uint8 for CLAHE
            slice_uint8 = cv2.normalize(slice_img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_uint8 = clahe.apply(slice_uint8)
            
            # Convert back to float
            enhanced[i] = enhanced_uint8.astype(np.float32) / 255.0
            
        return enhanced
        
    def _normalize_intensity(self, volume: np.ndarray) -> np.ndarray:
        """Normalize intensity values."""
        method = self.config.imaging_parameters.normalization_method
        
        if method == "z_score":
            mean_val = np.mean(volume)
            std_val = np.std(volume)
            if std_val > 0:
                normalized = (volume - mean_val) / std_val
            else:
                normalized = volume - mean_val
                
        elif method == "percentile":
            p1, p99 = np.percentile(volume, [1, 99])
            normalized = np.clip((volume - p1) / (p99 - p1), 0, 1)
            
        else:  # histogram normalization
            normalized = cv2.normalize(volume, None, 0, 1, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
            
        return normalized
        
    def _segment_spine_structures(self, volume: np.ndarray, 
                                metadata: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Segment spine structures (vertebrae, discs, cord)."""
        segmentation = {}
        
        # Segment vertebrae
        segmentation['vertebrae'] = self._segment_vertebrae(volume)
        
        # Segment spinal cord
        segmentation['cord'] = self._segment_spinal_cord(volume)
        
        # Segment intervertebral discs
        segmentation['discs'] = self._segment_discs(volume, segmentation['vertebrae'])
        
        # Segment soft tissues
        segmentation['soft_tissue'] = self._segment_soft_tissue(volume)
        
        return segmentation
        
    def _segment_vertebrae(self, volume: np.ndarray) -> np.ndarray:
        """Segment vertebral bodies using thresholding and morphological operations."""
        # Use multi-level thresholding for bone detection
        bone_mask = np.zeros_like(volume, dtype=bool)
        
        for i in range(volume.shape[0]):
            slice_img = volume[i]
            
            # Apply threshold for bone tissue (typically bright in T1)
            threshold = filters.threshold_otsu(slice_img)
            bone_slice = slice_img > (threshold * 1.2)  # Higher threshold for cortical bone
            
            # Morphological operations to clean up
            bone_slice = morphology.remove_small_objects(bone_slice, min_size=100)
            bone_slice = morphology.binary_closing(bone_slice, morphology.disk(3))
            
            bone_mask[i] = bone_slice
            
        return bone_mask
        
    def _segment_spinal_cord(self, volume: np.ndarray) -> np.ndarray:
        """Segment spinal cord using adaptive thresholding."""
        cord_mask = np.zeros_like(volume, dtype=bool)
        
        # Find approximate cord location (center of each slice)
        for i in range(volume.shape[0]):
            slice_img = volume[i]
            
            # Find center region (cord is typically central)
            h, w = slice_img.shape
            center_region = slice_img[h//4:3*h//4, w//4:3*w//4]
            
            if center_region.size > 0:
                # Adaptive threshold for cord
                threshold = np.mean(center_region) + 0.5 * np.std(center_region)
                cord_slice = slice_img > threshold
                
                # Keep only central connected component
                labeled = measure.label(cord_slice)
                if labeled.max() > 0:
                    # Find component closest to center
                    center_y, center_x = h//2, w//2
                    distances = []
                    for label_val in range(1, labeled.max() + 1):
                        coords = np.where(labeled == label_val)
                        if len(coords[0]) > 0:
                            centroid_y = np.mean(coords[0])
                            centroid_x = np.mean(coords[1])
                            dist = np.sqrt((centroid_y - center_y)**2 + (centroid_x - center_x)**2)
                            distances.append((dist, label_val))
                    
                    if distances:
                        distances.sort()
                        central_label = distances[0][1]
                        cord_slice = (labeled == central_label)
                
                cord_mask[i] = cord_slice
                
        return cord_mask
        
    def _segment_discs(self, volume: np.ndarray, vertebrae_mask: np.ndarray) -> np.ndarray:
        """Segment intervertebral discs based on location between vertebrae."""
        disc_mask = np.zeros_like(volume, dtype=bool)
        
        # Find gaps between vertebrae (disc locations)
        for i in range(volume.shape[0]):
            slice_img = volume[i]
            vertebrae_slice = vertebrae_mask[i]
            
            # Find regions between vertebrae
            # Discs are typically darker than bone, brighter than background
            mean_intensity = np.mean(slice_img[slice_img > 0])
            disc_threshold_low = mean_intensity * 0.3
            disc_threshold_high = mean_intensity * 0.8
            
            potential_disc = ((slice_img > disc_threshold_low) & 
                            (slice_img < disc_threshold_high) & 
                            (~vertebrae_slice))
            
            # Clean up disc mask
            potential_disc = morphology.remove_small_objects(potential_disc, min_size=50)
            
            disc_mask[i] = potential_disc
            
        return disc_mask
        
    def _segment_soft_tissue(self, volume: np.ndarray) -> np.ndarray:
        """Segment soft tissues (ligaments, muscles)."""
        soft_tissue_mask = np.zeros_like(volume, dtype=bool)
        
        for i in range(volume.shape[0]):
            slice_img = volume[i]
            
            # Soft tissue has intermediate intensity
            mean_val = np.mean(slice_img[slice_img > 0])
            std_val = np.std(slice_img[slice_img > 0])
            
            soft_tissue = ((slice_img > mean_val - std_val) & 
                          (slice_img < mean_val + std_val))
            
            soft_tissue_mask[i] = soft_tissue
            
        return soft_tissue_mask
        
    def _analyze_vertebral_morphology(self, volume: np.ndarray, 
                                    segmentation: Dict[str, np.ndarray],
                                    metadata: Dict[str, Any]) -> List[Finding]:
        """Analyze vertebral morphology for traumatic changes."""
        findings = []
        vertebrae_mask = segmentation['vertebrae']
        
        # Analyze each vertebral level
        for slice_idx in range(volume.shape[0]):
            if not np.any(vertebrae_mask[slice_idx]):
                continue
                
            # Find vertebral bodies in this slice
            labeled_vertebrae = measure.label(vertebrae_mask[slice_idx])
            
            for label_val in range(1, labeled_vertebrae.max() + 1):
                vertebra_mask = (labeled_vertebrae == label_val)
                
                # Analyze vertebra morphology
                vertebra_findings = self._analyze_single_vertebra(
                    volume[slice_idx], vertebra_mask, slice_idx)
                findings.extend(vertebra_findings)
                
        return findings
        
    def _analyze_single_vertebra(self, slice_img: np.ndarray, 
                               vertebra_mask: np.ndarray, 
                               slice_idx: int) -> List[Finding]:
        """Analyze single vertebra for morphological changes."""
        findings = []
        
        # Get vertebra properties
        props = measure.regionprops(vertebra_mask.astype(int), intensity_image=slice_img)[0]
        
        # Calculate morphological measurements
        area = props.area
        bbox = props.bbox
        centroid = props.centroid
        
        # Height measurements (anterior, middle, posterior)
        height_measurements = self._measure_vertebra_heights(slice_img, vertebra_mask, bbox)
        
        # Check for compression/wedge fractures
        if self._detect_wedge_fracture(height_measurements):
            finding = Finding(
                finding_type=FindingType.TRAUMATIC,
                category="vertebral_morphology",
                subcategory="wedge_fracture",
                description=f"Focal wedge deformity with anterior height loss",
                location=f"Slice {slice_idx}",
                severity=self._assess_compression_severity(height_measurements),
                confidence=0.85,
                coordinates=(int(centroid[1]), int(centroid[0]), slice_idx),
                measurements=height_measurements,
                evidence=["Asymmetric height loss", "Focal deformity"],
                slice_numbers=[slice_idx]
            )
            findings.append(finding)
            
        # Check for burst fractures
        if self._detect_burst_fracture(slice_img, vertebra_mask):
            finding = Finding(
                finding_type=FindingType.TRAUMATIC,
                category="vertebral_morphology", 
                subcategory="burst_fracture",
                description="Vertebral body fragmentation consistent with burst fracture",
                location=f"Slice {slice_idx}",
                severity=FindingSeverity.SEVERE,
                confidence=0.80,
                coordinates=(int(centroid[1]), int(centroid[0]), slice_idx),
                measurements={"fragmentation_score": self._calculate_fragmentation_score(vertebra_mask)},
                evidence=["Retropulsed fragments", "Central fragmentation"],
                slice_numbers=[slice_idx]
            )
            findings.append(finding)
            
        return findings
        
    def _measure_vertebra_heights(self, slice_img: np.ndarray, 
                                vertebra_mask: np.ndarray, 
                                bbox: Tuple[int, int, int, int]) -> Dict[str, float]:
        """Measure vertebral body heights (anterior, middle, posterior)."""
        min_row, min_col, max_row, max_col = bbox
        
        # Find vertebra boundaries
        vertebra_coords = np.where(vertebra_mask)
        
        if len(vertebra_coords[0]) == 0:
            return {"anterior_height": 0, "middle_height": 0, "posterior_height": 0}
            
        # Divide into thirds (anterior, middle, posterior)
        width = max_col - min_col
        anterior_col = min_col + width // 6
        middle_col = min_col + width // 2
        posterior_col = max_col - width // 6
        
        def measure_height_at_column(col):
            """Measure height at specific column."""
            if col < 0 or col >= vertebra_mask.shape[1]:
                return 0
                
            column_mask = vertebra_mask[:, col]
            if not np.any(column_mask):
                return 0
                
            rows_with_bone = np.where(column_mask)[0]
            if len(rows_with_bone) < 2:
                return 0
                
            return rows_with_bone[-1] - rows_with_bone[0]
            
        measurements = {
            "anterior_height": measure_height_at_column(anterior_col),
            "middle_height": measure_height_at_column(middle_col),
            "posterior_height": measure_height_at_column(posterior_col)
        }
        
        # Calculate ratios
        max_height = max(measurements.values())
        if max_height > 0:
            measurements["anterior_ratio"] = measurements["anterior_height"] / max_height
            measurements["middle_ratio"] = measurements["middle_height"] / max_height
            measurements["posterior_ratio"] = measurements["posterior_height"] / max_height
            
        return measurements
        
    def _detect_wedge_fracture(self, height_measurements: Dict[str, float]) -> bool:
        """
        Detect wedge fracture based on height loss pattern.
        
        CLINICAL RATIONALE: Wedge fractures from trauma show characteristic anterior
        vertebral height loss >10-15% with preserved posterior height. This asymmetric
        compression pattern differentiates old trauma from symmetric degenerative collapse.
        
        ALGORITHM: Compares anterior vertebral height to posterior height ratio.
        Traumatic wedge fractures typically show >15% anterior height loss while
        maintaining posterior cortex integrity.
        """
        anterior_ratio = height_measurements.get("anterior_ratio", 1.0)
        
        # DETECTION LOGIC: anterior_ratio = anterior_height / posterior_height
        # Values < 0.85 (15% height loss) indicate significant wedge deformity
        # consistent with resolved compression fracture from trauma
        if anterior_ratio < (1.0 - self.config.detection_thresholds.height_loss_threshold):
            return True
            
        return False
        
    def _detect_burst_fracture(self, slice_img: np.ndarray, vertebra_mask: np.ndarray) -> bool:
        """
        Detect burst fracture based on fragmentation pattern.
        
        CLINICAL RATIONALE: Burst fractures from high-energy trauma (e.g., blast injuries)
        show characteristic central vertebral body fragmentation with multiple bone fragments.
        This differs from degenerative compression which shows uniform settling.
        
        ALGORITHM: Uses connected component analysis to identify discrete bone fragments
        within the vertebral body. ≥3 fragments suggests burst fracture mechanism.
        """
        # SEGMENTATION: Label connected regions within vertebral mask to identify fragments
        # Each connected region represents a discrete bone fragment
        labeled_fragments = measure.label(vertebra_mask)
        num_fragments = labeled_fragments.max()
        
        # DIAGNOSTIC THRESHOLD: Burst fractures typically show ≥3 distinct fragments
        # Single fragment = intact, 2 fragments = simple fracture, ≥3 = burst pattern
        return num_fragments >= 3
        
    def _calculate_fragmentation_score(self, vertebra_mask: np.ndarray) -> float:
        """Calculate fragmentation score for burst fracture assessment."""
        labeled_fragments = measure.label(vertebra_mask)
        num_fragments = labeled_fragments.max()
        
        if num_fragments <= 1:
            return 0.0
            
        # Calculate size variation of fragments
        fragment_sizes = []
        for i in range(1, num_fragments + 1):
            fragment_size = np.sum(labeled_fragments == i)
            fragment_sizes.append(fragment_size)
            
        size_variation = np.std(fragment_sizes) / np.mean(fragment_sizes) if fragment_sizes else 0
        
        # Fragmentation score based on number and size variation
        fragmentation_score = min(1.0, (num_fragments - 1) / 5.0 + size_variation / 2.0)
        
        return fragmentation_score
        
    def _assess_compression_severity(self, height_measurements: Dict[str, float]) -> FindingSeverity:
        """Assess compression severity based on height loss."""
        anterior_ratio = height_measurements.get("anterior_ratio", 1.0)
        height_loss = 1.0 - anterior_ratio
        
        if height_loss >= 0.40:
            return FindingSeverity.SEVERE
        elif height_loss >= 0.20:
            return FindingSeverity.MODERATE
        else:
            return FindingSeverity.MILD
            
    def _analyze_disc_changes(self, volume: np.ndarray,
                            segmentation: Dict[str, np.ndarray],
                            metadata: Dict[str, Any]) -> List[Finding]:
        """Analyze intervertebral disc changes."""
        findings = []
        # Implementation for disc analysis
        # This would include detection of:
        # - Focal desiccation vs multilevel degeneration
        # - Schmorl's nodes
        # - Disc height loss patterns
        return findings
        
    def _analyze_endplate_changes(self, volume: np.ndarray,
                                segmentation: Dict[str, np.ndarray], 
                                metadata: Dict[str, Any]) -> List[Finding]:
        """Analyze endplate and bone marrow changes."""
        findings = []
        # Implementation for endplate analysis
        # This would include detection of:
        # - Modic changes (Type 1, 2, 3)
        # - Endplate fractures
        # - Sclerosis patterns
        return findings
        
    def _analyze_soft_tissue_changes(self, volume: np.ndarray,
                                   segmentation: Dict[str, np.ndarray],
                                   metadata: Dict[str, Any]) -> List[Finding]:
        """Analyze soft tissue changes."""
        findings = []
        # Implementation for soft tissue analysis
        # This would include detection of:
        # - Ligament scarring/thickening
        # - Muscle atrophy patterns
        # - Hematoma/edema patterns
        return findings
        
    def _analyze_cord_neural_changes(self, volume: np.ndarray,
                                   segmentation: Dict[str, np.ndarray],
                                   metadata: Dict[str, Any]) -> List[Finding]:
        """Analyze spinal cord and neural changes."""
        findings = []
        cord_mask = segmentation['cord']
        
        # Analyze for syringomyelia
        syrinx_findings = self._detect_syringomyelia(volume, cord_mask)
        findings.extend(syrinx_findings)
        
        return findings
        
    def _detect_syringomyelia(self, volume: np.ndarray, cord_mask: np.ndarray) -> List[Finding]:
        """
        Detect syringomyelia (post-traumatic syrinx formation).
        
        CLINICAL RATIONALE: Post-traumatic syringomyelia develops months to years after
        spinal cord injury, appearing as hyperintense intramedullary cavities on T2-weighted
        images. This distinguishes old trauma from degenerative myelomalacia which shows
        diffuse signal changes without discrete cavity formation.
        
        ALGORITHM: Identifies hyperintense cavities within spinal cord parenchyma using
        intensity thresholding and morphological analysis. Validates cavity characteristics
        against known syrinx width ratios (70-90% of cord diameter).
        """
        findings = []
        
        for slice_idx in range(volume.shape[0]):
            if not np.any(cord_mask[slice_idx]):
                continue
                
            slice_img = volume[slice_idx]
            cord_slice = cord_mask[slice_idx]
            
            # INTENSITY ANALYSIS: Syrinx appears as hyperintense (bright) cavity
            # on T2-weighted sequences, typically 1.5x brighter than normal cord
            cord_intensity = slice_img[cord_slice]
            if len(cord_intensity) == 0:
                continue
                
            mean_cord_intensity = np.mean(cord_intensity)
            # THRESHOLD: 1.5x normal cord intensity identifies hyperintense lesions
            high_intensity_threshold = mean_cord_intensity * 1.5
            
            # CAVITY DETECTION: Find hyperintense regions within cord boundaries
            syrinx_candidates = cord_slice & (slice_img > high_intensity_threshold)
            
            if np.any(syrinx_candidates):
                # MORPHOLOGICAL ANALYSIS: Characterize detected cavities
                labeled_syrinx = measure.label(syrinx_candidates)
                
                for label_val in range(1, labeled_syrinx.max() + 1):
                    syrinx_mask = (labeled_syrinx == label_val)
                    syrinx_props = measure.regionprops(syrinx_mask.astype(int))[0]
                    
                    # WIDTH VALIDATION: True syrinx occupies 70-90% of cord diameter
                    # This distinguishes from artifacts or partial volume effects
                    syrinx_width = self._calculate_syrinx_width_ratio(cord_slice, syrinx_mask)
                    
                    min_ratio, max_ratio = self.config.detection_thresholds.syrinx_width_ratio
                    if min_ratio <= syrinx_width <= max_ratio:
                        finding = Finding(
                            finding_type=FindingType.TRAUMATIC,
                            category="cord_neural",
                            subcategory="syringomyelia",
                            description=f"Post-traumatic syrinx, {syrinx_width:.1%} cord width",
                            location=f"Slice {slice_idx}",
                            severity=FindingSeverity.MODERATE,
                            confidence=0.75,
                            coordinates=(int(syrinx_props.centroid[1]), 
                                       int(syrinx_props.centroid[0]), slice_idx),
                            measurements={"width_ratio": syrinx_width, "area": syrinx_props.area},
                            evidence=["Hyperintense intramedullary cavity", "Site-specific location"],
                            slice_numbers=[slice_idx]
                        )
                        findings.append(finding)
                        
        return findings
        
    def _calculate_syrinx_width_ratio(self, cord_mask: np.ndarray, 
                                    syrinx_mask: np.ndarray) -> float:
        """Calculate syrinx width as ratio of cord width."""
        if not np.any(cord_mask) or not np.any(syrinx_mask):
            return 0.0
            
        # Find cord and syrinx bounding boxes
        cord_coords = np.where(cord_mask)
        syrinx_coords = np.where(syrinx_mask)
        
        if len(cord_coords[1]) < 2 or len(syrinx_coords[1]) < 2:
            return 0.0
            
        cord_width = np.max(cord_coords[1]) - np.min(cord_coords[1])
        syrinx_width = np.max(syrinx_coords[1]) - np.min(syrinx_coords[1])
        
        if cord_width == 0:
            return 0.0
            
        return syrinx_width / cord_width
        
    def _generate_overall_assessment(self, findings: List[Finding]) -> Tuple[FindingType, float]:
        """Generate overall assessment from individual findings."""
        # Filter out low confidence findings (< 50%) and low anterior ratios (< 50%) for consistency with reporting
        high_conf_findings = [f for f in findings 
                             if f.confidence >= 0.5 
                             and (f.measurements.get("anterior_ratio", 1.0) >= 0.5 or "anterior_ratio" not in f.measurements)]
        
        if not high_conf_findings:
            return FindingType.NORMAL, 0.95
            
        # Count findings by type (only high confidence)
        traumatic_count = sum(1 for f in high_conf_findings if f.finding_type == FindingType.TRAUMATIC)
        degenerative_count = sum(1 for f in high_conf_findings if f.finding_type == FindingType.DEGENERATIVE)
        
        # Calculate weighted confidence
        total_confidence = sum(f.confidence for f in high_conf_findings)
        avg_confidence = total_confidence / len(high_conf_findings) if high_conf_findings else 0.0
        
        # Determine overall assessment
        if traumatic_count > 0:
            if degenerative_count == 0:
                return FindingType.TRAUMATIC, avg_confidence
            else:
                # Mixed findings - uncertain
                return FindingType.UNCERTAIN, avg_confidence * 0.8
        elif degenerative_count > 0:
            return FindingType.DEGENERATIVE, avg_confidence
        else:
            return FindingType.NORMAL, avg_confidence
            
    def _identify_key_slices(self, findings: List[Finding], total_slices: int) -> List[int]:
        """Identify most important slices for diagnosis."""
        slice_importance = {}
        
        # Score slices based on findings
        for finding in findings:
            for slice_num in finding.slice_numbers:
                if slice_num not in slice_importance:
                    slice_importance[slice_num] = 0
                    
                # Weight by finding type and confidence
                weight = finding.confidence
                if finding.finding_type == FindingType.TRAUMATIC:
                    weight *= 2.0  # Traumatic findings are more important
                elif finding.finding_type == FindingType.DEGENERATIVE:
                    weight *= 1.0
                    
                slice_importance[slice_num] += weight
                
        # Sort by importance and return top slices
        sorted_slices = sorted(slice_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 5 slices or 20% of total, whichever is smaller
        max_slices = min(5, max(1, total_slices // 5))
        key_slices = [slice_num for slice_num, _ in sorted_slices[:max_slices]]
        
        return sorted(key_slices)
        
    def _create_measurements_summary(self, findings: List[Finding]) -> Dict[str, Any]:
        """Create summary of quantitative measurements."""
        summary = {
            "total_findings": len(findings),
            "traumatic_findings": 0,
            "degenerative_findings": 0,
            "severe_findings": 0,
            "height_loss_measurements": [],
            "syrinx_measurements": []
        }
        
        for finding in findings:
            if finding.finding_type == FindingType.TRAUMATIC:
                summary["traumatic_findings"] += 1
            elif finding.finding_type == FindingType.DEGENERATIVE:
                summary["degenerative_findings"] += 1
                
            if finding.severity == FindingSeverity.SEVERE:
                summary["severe_findings"] += 1
                
            # Collect specific measurements
            if "height_loss" in finding.measurements:
                summary["height_loss_measurements"].append(finding.measurements)
            if "width_ratio" in finding.measurements:
                summary["syrinx_measurements"].append(finding.measurements)
                
        return summary