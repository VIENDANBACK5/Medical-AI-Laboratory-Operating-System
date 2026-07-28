import io
import os
import time
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.model_mask import Mask
from app.services.ai.manager import AIEngineManager
from app.services.ai.inference_service import AIInferenceService
from tests.test_api_volume import create_dicom_zip_bytes


def test_ai_plugin_discovery():
    manager = AIEngineManager()
    models = manager.list_models()
    
    # Assert at least our mock plugin is discovered
    assert len(models) >= 1
    model_names = [m.name for m in models]
    assert "mock_bone_seg" in model_names
    
    # Verify retrieving the plugin
    plugin = manager.get_plugin("mock_bone_seg")
    assert plugin is not None
    info = plugin.get_info()
    assert info.version == "1.0.0"
    assert info.task_type == "segmentation"
    assert info.labels == {0: "background", 1: "bone"}


def test_api_list_models(client):
    response = client.get("/api/v1/inference/models")
    assert response.status_code == 200
    
    payload = response.json()
    assert isinstance(payload["data"], list)
    model_names = [m["name"] for m in payload["data"]]
    assert "mock_bone_seg" in model_names


def test_async_inference_and_download_flow(client):
    # 1. Upload a volume first
    zip_bytes = create_dicom_zip_bytes()
    upload_res = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("dicom_scan.zip", zip_bytes, "application/zip")}
    )
    assert upload_res.status_code == 201
    volume_data = upload_res.json()["data"]
    volume_id = volume_data["id"]
    
    # 2. Trigger segmentation
    trigger_res = client.post(
        f"/api/v1/inference/segment/{volume_id}",
        json={"model_name": "mock_bone_seg"}
    )
    assert trigger_res.status_code == 202
    
    trigger_data = trigger_res.json()["data"]
    task_id = trigger_data["task_id"]
    assert task_id is not None
    
    # Note: TestClient runs FastAPI BackgroundTasks synchronously,
    # so by this line, the task has already finished executing!
    
    # 3. Poll task status
    status_res = client.get(f"/api/v1/inference/tasks/{task_id}")
    assert status_res.status_code == 200
    
    status_data = status_res.json()["data"]
    assert status_data["status"] == "SUCCESS"
    assert status_data["progress"] == 100
    mask_id = status_data["result_id"]
    assert mask_id is not None
    
    # 4. Query mask details
    mask_res = client.get(f"/api/v1/inference/masks/{mask_id}")
    assert mask_res.status_code == 200
    mask_data = mask_res.json()["data"]
    assert mask_data["model_name"] == "mock_bone_seg"
    assert mask_data["volume_id"] == volume_id
    
    # Verify files saved on disk
    npy_path = os.path.join(settings.BASE_DIR, mask_data["file_path"])
    assert os.path.exists(npy_path)
    
    # Validate numpy array coordinates and shape
    mask_arr = np.load(npy_path)
    assert mask_arr.shape == (6, 13, 13)  # Matches volume dimensions from mock DICOM
    
    # 5. Download mask
    download_res = client.get(f"/api/v1/inference/masks/{mask_id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/octet-stream"
    
    downloaded_arr = np.load(io.BytesIO(download_res.content))
    assert np.array_equal(downloaded_arr, mask_arr)
    
    # 6. Delete mask
    delete_res = client.delete(f"/api/v1/inference/masks/{mask_id}")
    assert delete_res.status_code == 204
    
    # Verify disk files cleared
    assert not os.path.exists(npy_path)
    
    # Verify mask detail API returns error
    get_after_delete = client.get(f"/api/v1/inference/masks/{mask_id}")
    assert get_after_delete.status_code != 200
