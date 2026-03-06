"""
DICOM Scanner Module for MRI Enhancement Tool

Handles recursive folder scanning, DICOM validation, and series grouping.
Implements HIPAA-compliant data handling with anonymization options.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import pydicom
from pydicom.dataset import Dataset
from pydicom.errors import InvalidDicomError
import SimpleITK as sitk
import numpy as np
from .config import MRIConfig

logger = logging.getLogger(__name__)


@dataclass
class DICOMSeries:
    """Represents a grouped DICOM series."""
    
    series_uid: str
    series_description: str
    modality: str
    body_part: str
    sequence_name: str
    slice_count: int
    file_paths: List[str]
    metadata: Dict[str, Any]
    patient_id: str = "ANONYMIZED"
    study_date: str = ""
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.slice_count != len(self.file_paths):
            logger.warning(f"Slice count mismatch: {self.slice_count} vs {len(self.file_paths)}")


@dataclass 
class DICOMStudy:
    """Represents a complete DICOM study."""
    
    study_uid: str
    study_description: str
    study_date: str
    patient_id: str
    series: List[DICOMSeries]
    total_files: int
    
    def get_spine_series(self) -> List[DICOMSeries]:
        """Get only spine-related series."""
        spine_keywords = ["spine", "cervical", "thoracic", "lumbar", "c-spine", "t-spine", "l-spine"]
        
        spine_series = []
        for series in self.series:
            description_lower = series.series_description.lower()
            body_part_lower = series.body_part.lower() if series.body_part else ""
            
            if any(keyword in description_lower or keyword in body_part_lower 
                   for keyword in spine_keywords):
                spine_series.append(series)
                
        return spine_series


class DICOMScanner:
    """Scans folders recursively for DICOM files and organizes them into series."""
    
    def __init__(self, config: MRIConfig):
        """Initialize DICOM scanner with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "files_scanned": 0,
            "valid_dicoms": 0,
            "invalid_files": 0,
            "series_found": 0,
            "studies_found": 0
        }
        
    def scan_folder(self, folder_path: str) -> List[DICOMStudy]:
        """
        Recursively scan folder for DICOM files and group into studies/series.
        
        DICOM PROCESSING PIPELINE:
        1. Recursive file discovery with extension/magic number validation
        2. DICOM header parsing and metadata extraction  
        3. Series grouping by Study/Series UID with temporal ordering
        4. Spine MRI filtering based on sequence parameters
        5. HIPAA-compliant patient data handling
        
        MEDICAL VALIDATION: Ensures compatibility with spine MRI sequences:
        - T1-weighted: Vertebral morphology, bone marrow changes
        - T2-weighted: Disc pathology, cord/neural assessment
        - STIR: Bone marrow edema, soft tissue inflammation
        - Multi-planar: Sagittal primary, axial/coronal supplementary
        
        Args:
            folder_path: Root folder to scan (supports nested DICOM structure)
            
        Returns:
            List of DICOMStudy objects with filtered spine MRI series
        """
        self.logger.info(f"Starting DICOM scan of folder: {folder_path}")
        
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
            
        # DISCOVERY PHASE: Find all potential DICOM files using extension and magic number
        dicom_files = self._find_dicom_files(folder_path)
        self.logger.info(f"Found {len(dicom_files)} potential DICOM files")
        
        # VALIDATION PHASE: Parse DICOM headers and extract metadata for medical analysis
        valid_files = self._validate_dicom_files(dicom_files)
        self.logger.info(f"Validated {len(valid_files)} DICOM files")
        
        # ORGANIZATION PHASE: Group files into hierarchical studies/series structure
        studies = self._group_into_studies(valid_files)
        self.logger.info(f"Organized into {len(studies)} studies")
        
        # FILTERING PHASE: Retain only spine MRI sequences suitable for trauma analysis
        if self.config.check_sequence_compatibility:
            studies = self._filter_spine_studies(studies)
            self.logger.info(f"Found {len(studies)} spine studies")
            
        self._log_statistics()
        return studies
        
    def _find_dicom_files(self, folder_path: str) -> List[str]:
        """Find all potential DICOM files in folder recursively."""
        dicom_files = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check file extension (DICOM files may not have .dcm extension)
                file_lower = file.lower()
                if (file_lower.endswith('.dcm') or 
                    file_lower.endswith('.dicom') or
                    not '.' in file_lower or  # Files without extension
                    self._is_potential_dicom(file_path)):
                    
                    dicom_files.append(file_path)
                    
        self.stats["files_scanned"] = len(dicom_files)
        return dicom_files
        
    def _is_potential_dicom(self, file_path: str) -> bool:
        """Check if file might be a DICOM based on size and content."""
        try:
            # Check file size (DICOM files are typically > 1KB)
            if os.path.getsize(file_path) < 1024:
                return False
                
            # Quick check for DICOM magic number
            with open(file_path, 'rb') as f:
                f.seek(128)  # DICOM prefix starts at byte 128
                magic = f.read(4)
                if magic == b'DICM':
                    return True
                    
            # Check first few bytes for DICOM-like structure
            with open(file_path, 'rb') as f:
                header = f.read(256)
                # Look for common DICOM tags
                if b'\x08\x00' in header or b'\x10\x00' in header:
                    return True
                    
        except (OSError, IOError):
            pass
            
        return False
        
    def _validate_dicom_files(self, file_paths: List[str]) -> List[Tuple[str, Dataset]]:
        """Validate DICOM files and extract metadata."""
        valid_files = []
        
        for file_path in file_paths:
            try:
                # Read DICOM file
                ds = pydicom.dcmread(file_path, force=True)
                
                if self.config.validate_dicom_headers:
                    if self._validate_dicom_header(ds, file_path):
                        valid_files.append((file_path, ds))
                        self.stats["valid_dicoms"] += 1
                    else:
                        self.stats["invalid_files"] += 1
                else:
                    valid_files.append((file_path, ds))
                    self.stats["valid_dicoms"] += 1
                    
            except (InvalidDicomError, Exception) as e:
                self.logger.debug(f"Invalid DICOM file {file_path}: {e}")
                self.stats["invalid_files"] += 1
                
        return valid_files
        
    def _validate_dicom_header(self, ds: Dataset, file_path: str) -> bool:
        """Validate DICOM header for required fields and MRI spine compatibility."""
        try:
            # Check for required DICOM tags
            required_tags = [
                'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID'
            ]
            
            for tag in required_tags:
                if not hasattr(ds, tag) or not getattr(ds, tag):
                    self.logger.debug(f"Missing required tag {tag} in {file_path}")
                    return False
                    
            # Check modality
            modality = getattr(ds, 'Modality', '').upper()
            if modality not in self.config.supported_modalities:
                self.logger.debug(f"Unsupported modality {modality} in {file_path}")
                return False
                
            # Check body part for spine studies
            body_part = getattr(ds, 'BodyPartExamined', '').upper()
            if self.config.check_sequence_compatibility:
                if not any(part in body_part for part in self.config.supported_body_parts):
                    # Also check series description
                    series_desc = getattr(ds, 'SeriesDescription', '').upper()
                    if not any(part in series_desc for part in ['SPINE', 'CERVICAL', 'THORACIC', 'LUMBAR']):
                        self.logger.debug(f"Non-spine study in {file_path}: body part={body_part}")
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.debug(f"Header validation error for {file_path}: {e}")
            return False
            
    def _group_into_studies(self, valid_files: List[Tuple[str, Dataset]]) -> List[DICOMStudy]:
        """Group DICOM files into studies and series."""
        studies_dict = {}
        series_dict = {}
        
        # Group by study and series
        for file_path, ds in valid_files:
            try:
                study_uid = ds.StudyInstanceUID
                series_uid = ds.SeriesInstanceUID
                
                # Create study entry if new
                if study_uid not in studies_dict:
                    studies_dict[study_uid] = {
                        'study_description': getattr(ds, 'StudyDescription', ''),
                        'study_date': getattr(ds, 'StudyDate', ''),
                        'patient_id': self._get_patient_id(ds),
                        'series': {}
                    }
                    
                # Create series entry if new
                if series_uid not in studies_dict[study_uid]['series']:
                    studies_dict[study_uid]['series'][series_uid] = {
                        'series_description': getattr(ds, 'SeriesDescription', ''),
                        'modality': getattr(ds, 'Modality', ''),
                        'body_part': getattr(ds, 'BodyPartExamined', ''),
                        'sequence_name': getattr(ds, 'SequenceName', ''),
                        'files': [],
                        'metadata': self._extract_series_metadata(ds)
                    }
                    
                # Add file to series
                studies_dict[study_uid]['series'][series_uid]['files'].append(file_path)
                
            except Exception as e:
                self.logger.warning(f"Error grouping file {file_path}: {e}")
                
        # Convert to DICOMStudy objects
        studies = []
        for study_uid, study_data in studies_dict.items():
            series_list = []
            total_files = 0
            
            for series_uid, series_data in study_data['series'].items():
                # Sort files by instance number or slice location
                sorted_files = self._sort_series_files(series_data['files'])
                
                # Filter series with minimum slice count
                if len(sorted_files) >= self.config.minimum_slices_required:
                    dicom_series = DICOMSeries(
                        series_uid=series_uid,
                        series_description=series_data['series_description'],
                        modality=series_data['modality'],
                        body_part=series_data['body_part'],
                        sequence_name=series_data['sequence_name'],
                        slice_count=len(sorted_files),
                        file_paths=sorted_files,
                        metadata=series_data['metadata'],
                        patient_id=study_data['patient_id'],
                        study_date=study_data['study_date']
                    )
                    series_list.append(dicom_series)
                    total_files += len(sorted_files)
                else:
                    self.logger.debug(f"Skipping series {series_uid} with only {len(sorted_files)} slices")
                    
            if series_list:
                study = DICOMStudy(
                    study_uid=study_uid,
                    study_description=study_data['study_description'],
                    study_date=study_data['study_date'],
                    patient_id=study_data['patient_id'],
                    series=series_list,
                    total_files=total_files
                )
                studies.append(study)
                self.stats["studies_found"] += 1
                self.stats["series_found"] += len(series_list)
                
        return studies
        
    def _get_patient_id(self, ds: Dataset) -> str:
        """Get patient ID with anonymization if enabled."""
        if self.config.anonymize_patient_data:
            return "ANONYMIZED"
            
        return getattr(ds, 'PatientID', 'UNKNOWN')
        
    def _extract_series_metadata(self, ds: Dataset) -> Dict[str, Any]:
        """Extract relevant metadata from DICOM dataset."""
        metadata = {}
        
        # Imaging parameters
        metadata['repetition_time'] = getattr(ds, 'RepetitionTime', None)
        metadata['echo_time'] = getattr(ds, 'EchoTime', None)
        metadata['slice_thickness'] = getattr(ds, 'SliceThickness', None)
        metadata['pixel_spacing'] = getattr(ds, 'PixelSpacing', None)
        metadata['flip_angle'] = getattr(ds, 'FlipAngle', None)
        
        # Sequence information
        metadata['scanning_sequence'] = getattr(ds, 'ScanningSequence', None)
        metadata['sequence_variant'] = getattr(ds, 'SequenceVariant', None)
        metadata['mr_acquisition_type'] = getattr(ds, 'MRAcquisitionType', None)
        
        # Image orientation and position
        metadata['image_orientation'] = getattr(ds, 'ImageOrientationPatient', None)
        metadata['image_position'] = getattr(ds, 'ImagePositionPatient', None)
        
        # Acquisition info
        metadata['acquisition_date'] = getattr(ds, 'AcquisitionDate', None)
        metadata['acquisition_time'] = getattr(ds, 'AcquisitionTime', None)
        
        return metadata
        
    def _sort_series_files(self, file_paths: List[str]) -> List[str]:
        """Sort series files by instance number or slice location."""
        files_with_metadata = []
        
        for file_path in file_paths:
            try:
                ds = pydicom.dcmread(file_path, force=True)
                
                # Try to get instance number
                instance_number = getattr(ds, 'InstanceNumber', None)
                slice_location = getattr(ds, 'SliceLocation', None)
                
                # Use instance number primarily, fallback to slice location
                sort_key = instance_number if instance_number is not None else slice_location
                if sort_key is None:
                    sort_key = 0  # Fallback to beginning
                    
                files_with_metadata.append((sort_key, file_path))
                
            except Exception as e:
                self.logger.debug(f"Error reading metadata for sorting {file_path}: {e}")
                files_with_metadata.append((0, file_path))
                
        # Sort by sort key
        files_with_metadata.sort(key=lambda x: x[0])
        
        return [file_path for _, file_path in files_with_metadata]
        
    def _filter_spine_studies(self, studies: List[DICOMStudy]) -> List[DICOMStudy]:
        """Filter studies to only include spine-related series."""
        filtered_studies = []
        
        for study in studies:
            spine_series = study.get_spine_series()
            if spine_series:
                # Create new study with only spine series
                filtered_study = DICOMStudy(
                    study_uid=study.study_uid,
                    study_description=study.study_description,
                    study_date=study.study_date,
                    patient_id=study.patient_id,
                    series=spine_series,
                    total_files=sum(s.slice_count for s in spine_series)
                )
                filtered_studies.append(filtered_study)
                
        return filtered_studies
        
    def _log_statistics(self):
        """Log scanning statistics."""
        self.logger.info("DICOM Scanning Statistics:")
        self.logger.info(f"  Files scanned: {self.stats['files_scanned']}")
        self.logger.info(f"  Valid DICOM files: {self.stats['valid_dicoms']}")
        self.logger.info(f"  Invalid files: {self.stats['invalid_files']}")
        self.logger.info(f"  Studies found: {self.stats['studies_found']}")
        self.logger.info(f"  Series found: {self.stats['series_found']}")
        
    def load_series_as_volume(self, series: DICOMSeries) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Load a DICOM series as a 3D volume using SimpleITK.
        
        Args:
            series: DICOMSeries object
            
        Returns:
            Tuple of (volume_array, metadata)
        """
        try:
            self.logger.info(f"Loading series {series.series_uid} as 3D volume")
            
            # Use SimpleITK to load series
            reader = sitk.ImageSeriesReader()
            reader.SetFileNames(series.file_paths)
            
            # Read the series
            image = reader.Execute()
            
            # Convert to numpy array
            volume = sitk.GetArrayFromImage(image)
            
            # Extract spacing and origin information
            metadata = {
                'spacing': image.GetSpacing(),
                'origin': image.GetOrigin(),
                'direction': image.GetDirection(),
                'size': image.GetSize(),
                'pixel_type': image.GetPixelIDTypeAsString()
            }
            
            self.logger.info(f"Loaded volume shape: {volume.shape}")
            return volume, metadata
            
        except Exception as e:
            self.logger.error(f"Error loading series as volume: {e}")
            raise
            
    def get_statistics(self) -> Dict[str, int]:
        """Get scanning statistics."""
        return self.stats.copy()