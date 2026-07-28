import os
import shutil
import tempfile
import numpy as np
import pytest
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
import SimpleITK as sitk

from app.schemas.sche_volume import VolumeMetadataBase
from app.services.io.reader import SimpleITKVolumeReader
from app.services.io.preprocess import VolumePreprocessor


def create_mock_dicom_file(
    file_path: str,
    patient_id: str = "PAT001",
    study_uid: str = "1.2.840.10008.1.1",
    series_uid: str = "1.2.840.10008.1.2",
    instance_number: int = 1,
    z_position: float = 0.0,
):
    # Setup file metadata
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = f"1.2.840.10008.1.2.3.4.5.{instance_number}"
    file_meta.ImplementationClassUID = "1.2.3.4"
    file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"  # Explicit VR Little Endian

    ds = Dataset()
    ds.file_meta = file_meta

    # Patient / Study details
    ds.PatientID = patient_id
    ds.PatientName = "Test Patient"
    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = series_uid
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.Manufacturer = "MedAI-OS Mock"
    ds.InstanceNumber = instance_number

    # Spatial properties (LPS coordinates in DICOM)
    ds.ImagePositionPatient = [0.0, 0.0, float(z_position)]
    ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    ds.PixelSpacing = [0.8, 0.8]  # x and y spacing in mm
    ds.SliceThickness = 2.0        # z spacing in mm

    # Image properties
    ds.Rows = 16
    ds.Columns = 16
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleIntercept = "0"
    ds.RescaleSlope = "1"

    # Synthetic Pixel Data: gradient values (scaled to mimic bone/tissue densities)
    pixel_array = np.ones((16, 16), dtype=np.uint16) * instance_number * 200
    ds.PixelData = pixel_array.tobytes()

    pydicom.filewriter.write_file(file_path, ds, write_like_original=False)


@pytest.fixture
def dicom_series_dir():
    temp_dir = tempfile.mkdtemp()
    
    # Create a series of 5 slices (Z position: 0.0, 2.0, 4.0, 6.0, 8.0)
    for i in range(1, 6):
        create_mock_dicom_file(
            file_path=os.path.join(temp_dir, f"slice_{i}.dcm"),
            instance_number=i,
            z_position=float((i - 1) * 2.0),
        )
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def nifti_file_path():
    temp_dir = tempfile.mkdtemp()
    arr = np.ones((5, 16, 16), dtype=np.float32) * 100.0
    image = sitk.GetImageFromArray(arr)
    image.SetSpacing([0.8, 0.8, 2.0])
    image.SetOrigin([0.0, 0.0, 0.0])
    image.SetDirection([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0])
    
    path = os.path.join(temp_dir, "test_volume.nii.gz")
    sitk.WriteImage(image, path)
    
    yield path
    shutil.rmtree(temp_dir)


def test_volume_reader_dicom(dicom_series_dir):
    reader = SimpleITKVolumeReader()
    array, meta = reader.read_series(dicom_series_dir)

    # Check numpy array
    assert isinstance(array, np.ndarray)
    assert array.shape == (5, 16, 16)  # [z, y, x]
    
    # Check spatial properties
    assert meta.patient_id == "PAT001"
    assert meta.spacing == [0.8, 0.8, 2.0]
    assert meta.dimensions == [16, 16, 5]
    
    # Check LPS to RAS origin conversion:
    # LPS origin (0, 0, 0) maps to RAS (0, 0, 0)
    assert meta.origin == [0.0, 0.0, 0.0]


def test_volume_reader_nifti(nifti_file_path):
    reader = SimpleITKVolumeReader()
    array, meta = reader.read_nifti(nifti_file_path)

    assert isinstance(array, np.ndarray)
    assert array.shape == (5, 16, 16)
    assert meta.patient_id == "NIFTI_IMPORT"
    assert meta.spacing == pytest.approx([0.8, 0.8, 2.0])


def test_volume_preprocessor_resampling(dicom_series_dir):
    reader = SimpleITKVolumeReader()
    array, meta = reader.read_series(dicom_series_dir)

    preprocessor = VolumePreprocessor()
    resampled_array, new_meta = preprocessor.resample_isotropic(array, meta, target_spacing=1.0)

    # Verify isotropic output
    assert new_meta.spacing == [1.0, 1.0, 1.0]
    
    # Verify dimensions are computed correctly:
    # Original physical size: x = 16*0.8 = 12.8, y = 12.8, z = 5*2.0 = 10.0
    # Target spacing: 1.0
    # Expected size: x = round(12.8/1.0) = 13, y = 13, z = round(10.0/1.0) = 10
    assert new_meta.dimensions == [13, 13, 10]
    assert resampled_array.shape == (10, 13, 13)


def test_volume_preprocessor_windowing():
    preprocessor = VolumePreprocessor()
    
    # Create simple numpy array representing HU intensities
    # range [-1000, 1000]
    array = np.array([-1000.0, 0.0, 100.0, 300.0, 1000.0], dtype=np.float32)
    
    # Bone window preset: center=300, width=1000
    # Min window limit: 300 - 500 = -200
    # Max window limit: 300 + 500 = 800
    windowed = preprocessor.apply_window(array, center=300.0, width=1000.0)

    # Values mapping:
    # -1000 -> clipped to -200 -> normalized to 0.0
    # 0 -> maps to (0 - (-200)) / 1000 = 0.2
    # 100 -> maps to (100 - (-200)) / 1000 = 0.3
    # 300 -> maps to (300 - (-200)) / 1000 = 0.5
    # 1000 -> clipped to 800 -> normalized to 1.0
    assert np.allclose(windowed, [0.0, 0.2, 0.3, 0.5, 1.0])
