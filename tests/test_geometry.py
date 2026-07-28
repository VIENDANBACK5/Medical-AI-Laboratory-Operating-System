import io
import os
import numpy as np
import pytest
import trimesh
from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.geometry.reconstruction import skimageMeshEngine
from app.services.geometry.smoothing import smooth_mesh
from app.services.geometry.decimation import decimate_mesh
from app.services.geometry.repair import repair_and_verify
from tests.test_api_volume import create_dicom_zip_bytes


def make_synthetic_sphere_mask(shape=(16, 16, 16), radius=5.0) -> np.ndarray:
    """Generates a synthetic binary solid sphere mask array."""
    grid_z, grid_y, grid_x = np.mgrid[0:shape[0], 0:shape[1], 0:shape[2]]
    center = (shape[0] / 2.0 - 0.5, shape[1] / 2.0 - 0.5, shape[2] / 2.0 - 0.5)
    distance = np.sqrt(
        (grid_z - center[0]) ** 2
        + (grid_y - center[1]) ** 2
        + (grid_x - center[2]) ** 2
    )
    return (distance <= radius).astype(np.uint8)


def test_marching_cubes_and_mesh_reconstruction():
    mask = make_synthetic_sphere_mask()
    spacing = (1.0, 1.0, 1.0)
    
    engine = skimageMeshEngine()
    mesh = engine.generate_mesh(mask, spacing)
    
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    
    # Mathematical Sphere Volume Verification:
    # V = 4/3 * pi * r^3. For r=5.0: V ~ 523.6 mm^3.
    # Triangulated approximations are slightly smaller or larger depending on boundary criteria.
    assert 480.0 <= mesh.volume <= 560.0


def test_mesh_smoothing_and_decimation():
    mask = make_synthetic_sphere_mask()
    spacing = (1.0, 1.0, 1.0)
    
    engine = skimageMeshEngine()
    mesh = engine.generate_mesh(mask, spacing)
    original_vertex_count = len(mesh.vertices)
    original_face_count = len(mesh.faces)
    
    # Test Laplacian Smoothing
    smoothed = smooth_mesh(mesh, iterations=15)
    assert len(smoothed.vertices) == original_vertex_count  # vertex counts remain unchanged
    # Vertices coordinates should have shifted slightly
    assert not np.array_equal(smoothed.vertices, mesh.vertices)
    
    # Test Quadric Decimation
    decimated = decimate_mesh(mesh, decimate_ratio=0.2)
    assert len(decimated.faces) < original_face_count
    # Target face count should be close to 20%
    assert len(decimated.faces) <= int(original_face_count * 0.25)


def test_mesh_repair_watertightness():
    mask = make_synthetic_sphere_mask()
    spacing = (1.0, 1.0, 1.0)
    
    engine = skimageMeshEngine()
    mesh = engine.generate_mesh(mask, spacing)
    
    # Perform clean and repair checks
    repaired = repair_and_verify(mesh)
    assert repaired.is_watertight  # Sphere mesh should be watertight after cleanups
    assert len(repaired.faces) > 0


def test_mesh_api_reconstruct_and_cleanup_flow(client):
    # 1. Upload scan
    zip_bytes = create_dicom_zip_bytes()
    upload_res = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("dicom_scan.zip", zip_bytes, "application/zip")}
    )
    assert upload_res.status_code == 201
    volume_id = upload_res.json()["data"]["id"]
    
    # 2. Segment volume to get a mask
    seg_res = client.post(
        f"/api/v1/inference/segment/{volume_id}",
        json={"model_name": "mock_bone_seg"}
    )
    assert seg_res.status_code == 202
    task_id = seg_res.json()["data"]["task_id"]
    
    # Retrieve Mask ID
    task_status_res = client.get(f"/api/v1/inference/tasks/{task_id}")
    mask_id = task_status_res.json()["data"]["result_id"]
    assert mask_id is not None
    
    # 3. Trigger Mesh Reconstruction
    mesh_res = client.post(
        f"/api/v1/meshes/reconstruct/{mask_id}",
        json={"smooth_iterations": 10, "decimate_ratio": 0.2}
    )
    assert mesh_res.status_code == 201
    
    mesh_data = mesh_res.json()["data"]
    mesh_id = mesh_data["id"]
    assert mesh_data["is_watertight"] is True
    assert mesh_data["vertex_count"] > 0
    assert mesh_data["triangle_count"] > 0
    
    # Check that STL file exists on disk
    stl_path = os.path.join(settings.BASE_DIR, mesh_data["file_path"])
    assert os.path.exists(stl_path)
    
    # 4. Fetch mesh detail
    detail_res = client.get(f"/api/v1/meshes/{mesh_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["id"] == mesh_id
    
    # 5. Fetch all meshes list
    list_res = client.get("/api/v1/meshes/all")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1
    
    # 6. Download STL
    download_res = client.get(f"/api/v1/meshes/{mesh_id}/download")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/sla"
    
    # Validate content length corresponds to stl size on disk
    assert len(download_res.content) == os.path.getsize(stl_path)
    
    # 7. Delete mesh record
    delete_res = client.delete(f"/api/v1/meshes/{mesh_id}")
    assert delete_res.status_code == 204
    
    # Check STL file is deleted from disk
    assert not os.path.exists(stl_path)
    
    # Check detail API returns error
    get_after_delete = client.get(f"/api/v1/meshes/{mesh_id}")
    assert get_after_delete.status_code != 200
