import os
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import numpy as np
import pydicom
import SimpleITK as sitk

from app.schemas.sche_volume import VolumeMetadataBase


class IVolumeReader(ABC):
    @abstractmethod
    def read_series(self, dicom_dir: str) -> Tuple[np.ndarray, VolumeMetadataBase]:
        """Reads a DICOM series from a folder, converting it to a numpy volume and metadata."""
        pass

    @abstractmethod
    def read_nifti(self, file_path: str) -> Tuple[np.ndarray, VolumeMetadataBase]:
        """Reads a NIfTI file, converting it to a numpy volume and metadata."""
        pass


class SimpleITKVolumeReader(IVolumeReader):
    def read_series(self, dicom_dir: str) -> Tuple[np.ndarray, VolumeMetadataBase]:
        if not os.path.exists(dicom_dir) or not os.path.isdir(dicom_dir):
            raise FileNotFoundError(f"DICOM directory {dicom_dir} does not exist.")

        # Read DICOM names
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir)
        if not dicom_names:
            raise ValueError(f"No valid DICOM slices found in {dicom_dir}")

        reader.SetFileNames(dicom_names)
        image = reader.Execute()

        # Extract metadata from DICOM header using pydicom for robustness
        first_slice = dicom_names[0]
        ds = pydicom.dcmread(first_slice, stop_before_pixels=True)
        
        patient_id = getattr(ds, "PatientID", "UNKNOWN_PATIENT")
        study_instance_uid = getattr(ds, "StudyInstanceUID", "UNKNOWN_STUDY")
        series_instance_uid = getattr(ds, "SeriesInstanceUID", "UNKNOWN_SERIES")

        # Collect additional metadata
        meta_info = {
            "PatientName": str(getattr(ds, "PatientName", "UNKNOWN")),
            "Modality": str(getattr(ds, "Modality", "CT")),
            "Manufacturer": str(getattr(ds, "Manufacturer", "UNKNOWN")),
            "KVP": float(getattr(ds, "KVP", 0.0)) if hasattr(ds, "KVP") else None,
            "SliceThickness": float(getattr(ds, "SliceThickness", 0.0)) if hasattr(ds, "SliceThickness") else None,
        }

        # SimpleITK returns spacing/origin/direction in LPS. Convert to RAS.
        spacing = list(image.GetSpacing())       # [x_spacing, y_spacing, z_spacing]
        dimensions = list(image.GetSize())      # [x_size, y_size, z_size]
        origin = list(image.GetOrigin())        # [x_origin, y_origin, z_origin]
        direction = list(image.GetDirection())  # 9 floats for 3x3 matrix

        # LPS to RAS conversion
        origin_ras = [-origin[0], -origin[1], origin[2]]
        direction_ras = [
            -direction[0], -direction[1], -direction[2],
            -direction[3], -direction[4], -direction[5],
            direction[6], direction[7], direction[8]
        ]

        # Convert image to numpy array. Shape is [z, y, x] (Depth, Height, Width)
        array = sitk.GetArrayFromImage(image)

        metadata = VolumeMetadataBase(
            patient_id=patient_id,
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            spacing=spacing,
            dimensions=dimensions,
            origin=origin_ras,
            direction=direction_ras,
            meta_info=meta_info
        )

        return array, metadata

    def read_nifti(self, file_path: str) -> Tuple[np.ndarray, VolumeMetadataBase]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"NIfTI file {file_path} does not exist.")

        image = sitk.ReadImage(file_path)

        # SimpleITK returns spacing/origin/direction in LPS. Convert to RAS.
        spacing = list(image.GetSpacing())
        dimensions = list(image.GetSize())
        origin = list(image.GetOrigin())
        direction = list(image.GetDirection())

        # LPS to RAS conversion
        origin_ras = [-origin[0], -origin[1], origin[2]]
        direction_ras = [
            -direction[0], -direction[1], -direction[2],
            -direction[3], -direction[4], -direction[5],
            direction[6], direction[7], direction[8]
        ]

        array = sitk.GetArrayFromImage(image)

        metadata = VolumeMetadataBase(
            patient_id="NIFTI_IMPORT",
            study_instance_uid="NIFTI_IMPORT",
            series_instance_uid=os.path.basename(file_path).split(".")[0],
            spacing=spacing,
            dimensions=dimensions,
            origin=origin_ras,
            direction=direction_ras,
            meta_info={"file_name": os.path.basename(file_path)}
        )

        return array, metadata
