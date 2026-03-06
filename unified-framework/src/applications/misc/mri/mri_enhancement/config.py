"""
Configuration module for MRI Enhancement Tool

Defines detection thresholds, parameters, and settings for spine MRI analysis.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import json


@dataclass
class DetectionThresholds:
    """Thresholds for detecting various traumatic vs degenerative changes."""
    
    # Vertebral morphology thresholds
    height_loss_threshold: float = 0.10  # >10% height loss for wedge detection
    compression_ratio_threshold: float = 0.80  # Vertebral body compression ratio
    kyphosis_angle_threshold: float = 15.0  # Degrees for focal kyphosis
    
    # Disc change thresholds  
    disc_height_loss_threshold: float = 0.25  # 25% disc height loss
    desiccation_intensity_threshold: float = 0.40  # Normalized T2 intensity
    
    # Endplate/bone marrow thresholds
    modic_type_threshold: float = 0.60  # Signal intensity ratio for Modic changes
    sclerosis_detection_threshold: float = 0.30  # Bone sclerosis detection
    
    # Soft tissue thresholds
    ligament_thickness_threshold: float = 3.0  # mm for ligament thickening
    scar_tissue_intensity_threshold: float = 0.70  # Scar tissue detection
    
    # Cord/neural thresholds
    syrinx_width_ratio: Tuple[float, float] = (0.70, 0.90)  # 70-90% cord width
    cord_atrophy_threshold: float = 0.75  # Cord area ratio
    gliosis_intensity_threshold: float = 0.80  # T2 hyperintensity


@dataclass  
class ImagingParameters:
    """Parameters for image processing and analysis."""
    
    # Image preprocessing
    contrast_enhancement: bool = True
    noise_reduction_kernel: int = 3
    normalization_method: str = "histogram"  # "histogram", "z_score", "percentile"
    
    # Segmentation parameters
    vertebrae_segmentation_method: str = "threshold"  # "threshold", "region_growing", "ml"
    cord_segmentation_method: str = "adaptive"  # "adaptive", "watershed", "ml"
    disc_segmentation_method: str = "gradient"  # "gradient", "intensity", "ml"
    
    # Analysis parameters
    slice_thickness_mm: float = 3.0  # Expected slice thickness
    voxel_spacing_mm: Tuple[float, float, float] = (0.5, 0.5, 3.0)  # x, y, z spacing
    roi_padding_mm: float = 5.0  # Padding around regions of interest


@dataclass
class AnnotationSettings:
    """Settings for generating annotated images."""
    
    # Output image settings
    output_format: str = "PNG"  # Output image format
    image_quality: int = 95  # Image quality (1-100)
    image_size: Tuple[int, int] = (512, 512)  # Output image dimensions
    
    # Annotation colors (BGR format for OpenCV)
    trauma_color: Tuple[int, int, int] = (0, 0, 255)  # Red for trauma findings
    degenerative_color: Tuple[int, int, int] = (0, 255, 255)  # Yellow for degenerative
    uncertain_color: Tuple[int, int, int] = (0, 165, 255)  # Orange for uncertain
    
    # Annotation styles
    line_thickness: int = 2
    font_scale: float = 0.6
    font_thickness: int = 2
    arrow_tip_length: float = 0.05
    
    # Text annotations
    include_measurements: bool = True
    include_confidence_scores: bool = True
    label_font_size: int = 12


@dataclass
class ReportSettings:
    """Settings for PDF report generation."""
    
    # Report structure
    include_executive_summary: bool = True
    include_detailed_findings: bool = True
    include_image_gallery: bool = True
    include_citations: bool = True
    include_timeline_analysis: bool = True
    
    # PDF formatting
    page_size: str = "LETTER"  # "LETTER", "A4"
    font_family: str = "Helvetica"
    font_size_body: int = 11
    font_size_heading: int = 14
    font_size_title: int = 18
    
    # Image embedding
    max_images_per_page: int = 4
    image_compression: bool = True
    thumbnail_size: Tuple[int, int] = (200, 200)
    
    # Citation settings
    citation_style: str = "medical"  # "medical", "apa", "vancouver"
    pubmed_api_enabled: bool = True
    max_citations_per_finding: int = 3


@dataclass
class MRIConfig:
    """Main configuration class for MRI Enhancement Tool."""
    
    # Component settings
    detection_thresholds: DetectionThresholds = field(default_factory=DetectionThresholds)
    imaging_parameters: ImagingParameters = field(default_factory=ImagingParameters)
    annotation_settings: AnnotationSettings = field(default_factory=AnnotationSettings)
    report_settings: ReportSettings = field(default_factory=ReportSettings)
    
    # Processing settings
    max_parallel_jobs: int = 4
    memory_limit_mb: int = 2048
    temp_directory: str = "/tmp/mri_enhancement"
    
    # HIPAA compliance settings
    anonymize_patient_data: bool = True
    remove_metadata: bool = True
    secure_temp_files: bool = True
    log_access: bool = True
    
    # Validation settings
    validate_dicom_headers: bool = True
    check_sequence_compatibility: bool = True
    minimum_slices_required: int = 10
    supported_modalities: List[str] = field(default_factory=lambda: ["MR"])
    supported_body_parts: List[str] = field(default_factory=lambda: ["SPINE", "C-SPINE", "T-SPINE", "L-SPINE"])
    
    @classmethod
    def from_json(cls, config_path: str) -> 'MRIConfig':
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
            
        # Convert nested dictionaries back to dataclasses
        if 'detection_thresholds' in config_dict and isinstance(config_dict['detection_thresholds'], dict):
            config_dict['detection_thresholds'] = DetectionThresholds(**config_dict['detection_thresholds'])
        if 'imaging_parameters' in config_dict and isinstance(config_dict['imaging_parameters'], dict):
            config_dict['imaging_parameters'] = ImagingParameters(**config_dict['imaging_parameters'])
        if 'annotation_settings' in config_dict and isinstance(config_dict['annotation_settings'], dict):
            config_dict['annotation_settings'] = AnnotationSettings(**config_dict['annotation_settings'])
        if 'report_settings' in config_dict and isinstance(config_dict['report_settings'], dict):
            config_dict['report_settings'] = ReportSettings(**config_dict['report_settings'])
            
        return cls(**config_dict)
    
    def to_json(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Convert dataclass to dict, handling nested dataclasses
        config_dict = self._to_dict()
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def _to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):  # Nested dataclass
                result[key] = value.__dict__
            else:
                result[key] = value
        return result
    
    def validate(self) -> List[str]:
        """Validate configuration settings and return list of warnings/errors."""
        warnings = []
        
        # Validate thresholds are in reasonable ranges
        if not 0.05 <= self.detection_thresholds.height_loss_threshold <= 0.50:
            warnings.append("Height loss threshold should be between 5% and 50%")
            
        if not 0.50 <= self.detection_thresholds.compression_ratio_threshold <= 0.95:
            warnings.append("Compression ratio threshold should be between 50% and 95%")
            
        # Validate memory limits
        if self.memory_limit_mb < 512:
            warnings.append("Memory limit is very low, may cause processing failures")
            
        # Validate parallel job settings
        if self.max_parallel_jobs > os.cpu_count():
            warnings.append(f"Parallel jobs ({self.max_parallel_jobs}) exceeds CPU count ({os.cpu_count()})")
            
        # Validate temp directory
        if not os.path.exists(os.path.dirname(self.temp_directory)):
            warnings.append(f"Temp directory parent does not exist: {self.temp_directory}")
            
        return warnings
    
    def create_temp_directory(self) -> str:
        """Create and return the temporary directory path."""
        os.makedirs(self.temp_directory, exist_ok=True)
        return self.temp_directory


# Default configuration instance
DEFAULT_CONFIG = MRIConfig()


def get_default_config() -> MRIConfig:
    """Get the default configuration."""
    return DEFAULT_CONFIG


def load_config(config_path: str = None) -> MRIConfig:
    """Load configuration from file or return default."""
    if config_path and os.path.exists(config_path):
        return MRIConfig.from_json(config_path)
    return get_default_config()


# Configuration for different spine regions
CERVICAL_CONFIG = MRIConfig(
    detection_thresholds=DetectionThresholds(
        height_loss_threshold=0.15,  # More sensitive for cervical spine
        kyphosis_angle_threshold=10.0,  # Lower threshold for cervical lordosis loss
        syrinx_width_ratio=(0.60, 0.85)  # Different ratio for cervical cord
    )
)

THORACIC_CONFIG = MRIConfig(
    detection_thresholds=DetectionThresholds(
        height_loss_threshold=0.10,  # Standard threshold
        kyphosis_angle_threshold=20.0,  # Higher threshold for thoracic kyphosis
        syrinx_width_ratio=(0.70, 0.90)  # Standard ratio
    )
)

LUMBAR_CONFIG = MRIConfig(
    detection_thresholds=DetectionThresholds(
        height_loss_threshold=0.08,  # More sensitive for lumbar spine
        disc_height_loss_threshold=0.30,  # Higher threshold for lumbar discs
        ligament_thickness_threshold=4.0  # Thicker ligaments in lumbar spine
    )
)


def get_spine_config(spine_region: str) -> MRIConfig:
    """Get configuration optimized for specific spine region."""
    region_configs = {
        "cervical": CERVICAL_CONFIG,
        "thoracic": THORACIC_CONFIG, 
        "lumbar": LUMBAR_CONFIG,
        "c-spine": CERVICAL_CONFIG,
        "t-spine": THORACIC_CONFIG,
        "l-spine": LUMBAR_CONFIG
    }
    
    return region_configs.get(spine_region.lower(), DEFAULT_CONFIG)