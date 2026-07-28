import io
import os
import zipfile
import tempfile
import shutil
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.test_io import create_mock_dicom_file


def create_dicom_zip_bytes(series_uid: str = None) -> bytes:
    """Generates an in-memory ZIP archive containing 3 mock DICOM slices."""
    if series_uid is None:
        import uuid
        series_uid = f"1.2.840.10008.1.2.{uuid.uuid4().int}"
    zip_buffer = io.BytesIO()
    temp_dir = tempfile.mkdtemp()
    try:
        # Create slices
        for i in range(1, 4):
            slice_path = os.path.join(temp_dir, f"slice_{i}.dcm")
            create_mock_dicom_file(
                file_path=slice_path,
                instance_number=i,
                z_position=float((i - 1) * 2.0),
                series_uid=series_uid,
            )
        
        # Write to zip
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for f in os.listdir(temp_dir):
                zip_file.write(os.path.join(temp_dir, f), f)
                
    finally:
        shutil.rmtree(temp_dir)
        
    return zip_buffer.getvalue()


def create_mock_nifti_bytes() -> bytes:
    """Generates an in-memory NIfTI file representation."""
    import SimpleITK as sitk
    temp_dir = tempfile.mkdtemp()
    try:
        image = sitk.Image([8, 8, 3], sitk.sitkFloat32)
        image.SetSpacing([1.0, 1.0, 1.0])
        path = os.path.join(temp_dir, "test.nii.gz")
        sitk.WriteImage(image, path)
        with open(path, "rb") as fd:
            data = fd.read()
    finally:
        shutil.rmtree(temp_dir)
    return data


def test_upload_dicom_zip_api(client):
    zip_bytes = create_dicom_zip_bytes()
    
    # Trigger upload
    response = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("dicom_scan.zip", zip_bytes, "application/zip")},
        params={"target_spacing": 1.0}
    )
    
    # Assert successful API response
    assert response.status_code == 201
    payload = response.json()
    assert payload["http_code"] == 201
    
    data = payload["data"]
    assert data["patient_id"] == "PAT001"
    assert data["spacing"] == [1.0, 1.0, 1.0]
    
    # Verify file saved on disk
    saved_file_path = os.path.join(settings.BASE_DIR, data["file_path"])
    assert os.path.exists(saved_file_path)
    
    # Load and check numpy array saved matches dimensions [z, y, x]
    # Physical size x = 16*0.8 = 12.8, target spacing = 1.0 -> round to 13
    # Physical size y = 16*0.8 = 12.8 -> round to 13
    # Physical size z = 3*2.0 = 6.0 -> round to 6
    arr = np.load(saved_file_path)
    assert arr.shape == (6, 13, 13)


def test_upload_nifti_api(client):
    nii_bytes = create_mock_nifti_bytes()
    
    response = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("scan.nii.gz", nii_bytes, "application/gzip")},
        params={"target_spacing": 1.0}
    )
    
    assert response.status_code == 201
    payload = response.json()
    data = payload["data"]
    assert data["patient_id"] == "NIFTI_IMPORT"


def test_get_volumes_list_api(client):
    # Retrieve all list endpoint
    response = client.get("/api/v1/volumes/all")
    assert response.status_code == 200
    
    payload = response.json()
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) >= 2  # At least the two from previous upload tests


def test_get_volume_detail_api(client):
    # First query all list to get a valid volume ID
    list_response = client.get("/api/v1/volumes/all")
    volume_id = list_response.json()["data"][0]["id"]
    
    # Fetch detail
    detail_response = client.get(f"/api/v1/volumes/{volume_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == volume_id


def test_download_volume_api(client):
    list_response = client.get("/api/v1/volumes/all")
    volume_id = list_response.json()["data"][0]["id"]
    
    download_response = client.get(f"/api/v1/volumes/{volume_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/octet-stream"
    
    # Validate numpy array can be successfully read from download stream
    stream = io.BytesIO(download_response.content)
    arr = np.load(stream)
    assert isinstance(arr, np.ndarray)


def test_delete_volume_api(client):
    # Upload one first to delete
    zip_bytes = create_dicom_zip_bytes()
    upload_response = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("delete_me.zip", zip_bytes, "application/zip")}
    )
    volume_data = upload_response.json()["data"]
    volume_id = volume_data["id"]
    
    # Check that paths exist on disk before deletion
    npy_path = os.path.join(settings.BASE_DIR, volume_data["file_path"])
    zip_path = os.path.join(settings.BASE_DIR, volume_data["original_file_path"])
    assert os.path.exists(npy_path)
    assert os.path.exists(zip_path)
    
    # Run deletion
    delete_response = client.delete(f"/api/v1/volumes/{volume_id}")
    assert delete_response.status_code == 204
    
    # Verify files deleted from disk
    assert not os.path.exists(npy_path)
    assert not os.path.exists(zip_path)
    
    # Verify database record deleted
    get_response = client.get(f"/api/v1/volumes/{volume_id}")
    # fastapi-base-main template raises 404/NotFound exception format
    assert get_response.status_code != 200
