import os
import shutil
import tempfile
import uuid
import zipfile
from typing import Tuple
import numpy as np
from fastapi import UploadFile
from fastapi_sqlalchemy import db

from app.core.config import settings
from app.models.model_volume import Volume
from app.schemas.sche_volume import VolumeMetadataBase
from app.services.io.preprocess import VolumePreprocessor
from app.services.io.reader import SimpleITKVolumeReader
from app.services.srv_base import BaseService
from app.utils.exception_handler import CustomException, ExceptionType


class VolumeService(BaseService[Volume]):
    def __init__(self):
        super().__init__(Volume)
        self.reader = SimpleITKVolumeReader()
        self.preprocessor = VolumePreprocessor()

        # Define storage directories
        self.storage_dir = os.path.join(settings.BASE_DIR, "storage")
        self.original_dir = os.path.join(self.storage_dir, "original")
        self.processed_dir = os.path.join(self.storage_dir, "processed")

        # Create directories if they do not exist
        os.makedirs(self.original_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def process_dicom_zip(self, file: UploadFile, target_spacing: float = 1.0) -> Volume:
        # Generate unique volume identifier
        volume_uuid = str(uuid.uuid4())
        
        # Save original uploaded ZIP archive
        original_zip_path = os.path.join(self.original_dir, f"{volume_uuid}.zip")
        with open(original_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp(dir=self.storage_dir)
        try:
            # Unzip DICOM archive
            with zipfile.ZipFile(original_zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Locate the directory containing DICOM slices (it might be nested)
            dicom_dir = self._find_dicom_directory(temp_dir)
            if not dicom_dir:
                raise CustomException(
                    exception=ExceptionType.VALIDATION_ERROR,
                    message="No valid DICOM series found in ZIP archive."
                )

            # Read DICOM series
            array, meta = self.reader.read_series(dicom_dir)

            # Resample to isotropic spacing
            resampled_array, isotropic_meta = self.preprocessor.resample_isotropic(
                array, meta, target_spacing
            )

            # Save processed volume as a .npy file
            processed_file_path = os.path.join(self.processed_dir, f"{volume_uuid}.npy")
            np.save(processed_file_path, resampled_array)

            # Create Database Record
            volume_record = self.create({
                "patient_id": isotropic_meta.patient_id,
                "study_instance_uid": isotropic_meta.study_instance_uid,
                "series_instance_uid": isotropic_meta.series_instance_uid,
                "spacing": isotropic_meta.spacing,
                "dimensions": isotropic_meta.dimensions,
                "origin": isotropic_meta.origin,
                "direction": isotropic_meta.direction,
                "file_path": os.path.relpath(processed_file_path, settings.BASE_DIR),
                "original_file_path": os.path.relpath(original_zip_path, settings.BASE_DIR),
                "meta_info": isotropic_meta.meta_info
            })

            return volume_record

        except Exception as e:
            # Clean up saved zip if database write or reading failed
            if os.path.exists(original_zip_path):
                os.remove(original_zip_path)
            import traceback
            traceback.print_exc()
            raise CustomException(
                http_code=500,
                message=f"Failed to process DICOM ZIP: {str(e)}"
            )
        finally:
            # Ensure temporary directory is cleaned up
            shutil.rmtree(temp_dir, ignore_errors=True)

    def process_nifti_file(self, file: UploadFile, target_spacing: float = 1.0) -> Volume:
        volume_uuid = str(uuid.uuid4())
        
        # Save original uploaded NIfTI file
        original_nifti_path = os.path.join(self.original_dir, f"{volume_uuid}.nii.gz")
        with open(original_nifti_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # Read NIfTI file
            array, meta = self.reader.read_nifti(original_nifti_path)

            # Resample to isotropic spacing
            resampled_array, isotropic_meta = self.preprocessor.resample_isotropic(
                array, meta, target_spacing
            )

            # Save processed volume as a .npy file
            processed_file_path = os.path.join(self.processed_dir, f"{volume_uuid}.npy")
            np.save(processed_file_path, resampled_array)

            # Create Database Record
            volume_record = self.create({
                "patient_id": isotropic_meta.patient_id,
                "study_instance_uid": isotropic_meta.study_instance_uid,
                "series_instance_uid": isotropic_meta.series_instance_uid,
                "spacing": isotropic_meta.spacing,
                "dimensions": isotropic_meta.dimensions,
                "origin": isotropic_meta.origin,
                "direction": isotropic_meta.direction,
                "file_path": os.path.relpath(processed_file_path, settings.BASE_DIR),
                "original_file_path": os.path.relpath(original_nifti_path, settings.BASE_DIR),
                "meta_info": isotropic_meta.meta_info
            })

            return volume_record

        except Exception as e:
            if os.path.exists(original_nifti_path):
                os.remove(original_nifti_path)
            import traceback
            traceback.print_exc()
            raise CustomException(
                http_code=500,
                message=f"Failed to process NIfTI file: {str(e)}"
            )

    def _find_dicom_directory(self, root_dir: str) -> str:
        """Helper to find the first directory containing at least one .dcm file."""
        for dirpath, _, filenames in os.walk(root_dir):
            # Check if directory contains .dcm files or files with no extension that might be DICOM
            dicom_files = [f for f in filenames if f.lower().endswith(".dcm")]
            if dicom_files:
                return dirpath
            
            # Hybrid check: check if any file is valid DICOM by header signature
            for f in filenames[:5]:  # test first 5 files
                file_path = os.path.join(dirpath, f)
                try:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as fd:
                            fd.seek(128)
                            if fd.read(4) == b"DICM":
                                return dirpath
                except:
                    continue
        return None
