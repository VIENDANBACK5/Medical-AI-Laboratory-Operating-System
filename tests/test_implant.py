import os
import uuid
import numpy as np

from app.core.config import settings
from app.services.implant.manager import ImplantEngineManager
from app.services.implant.plugins.mirror_implant_plugin import MirrorImplantPlugin
from app.services.implant.implant_service import ImplantService
from tests.test_api_volume import create_dicom_zip_bytes


def make_defective_bone_mask(shape=(24, 24, 24)) -> np.ndarray:
    """A slab that is symmetric about the x midline, with a cube carved out of
    the right side to simulate a bone defect the implant should fill."""
    mask = np.zeros(shape, dtype=np.uint8)
    mask[6:18, 6:18, 4:20] = 1          # symmetric slab about x center (=12)
    mask[8:16, 8:16, 14:19] = 0         # defect on the right (high x) side
    return mask


def test_implant_plugin_discovery():
    manager = ImplantEngineManager()
    names = [m.name for m in manager.list_models()]
    assert "mirror_implant" in names

    plugin = manager.get_plugin("mirror_implant")
    info = plugin.get_info()
    assert info.method == "mirroring"


def test_mirror_plugin_generates_defect_region():
    plugin = MirrorImplantPlugin()
    plugin.initialize()
    mask = make_defective_bone_mask()

    implant = plugin.generate(mask, spacing=(1.0, 1.0, 1.0))

    # Implant must be non-empty and should not overlap existing bone.
    assert implant.sum() > 0
    assert np.sum((implant == 1) & (mask == 1)) == 0

    # The defect was on the right (high x); most implant voxels should sit there.
    xs = np.where(implant == 1)[2]
    assert xs.mean() > mask.shape[2] / 2.0


def test_symmetric_mask_raises_no_defect():
    plugin = MirrorImplantPlugin()
    plugin.initialize()
    # Perfectly symmetric slab -> nothing to reconstruct.
    mask = np.zeros((20, 20, 20), dtype=np.uint8)
    mask[6:14, 6:14, 6:14] = 1

    try:
        plugin.generate(mask, spacing=(1.0, 1.0, 1.0))
        assert False, "Expected ValueError for symmetric mask"
    except ValueError:
        pass


def _seed_volume_and_mask(session, mask_array: np.ndarray):
    """Insert a Volume + Mask record and write the mask array to disk."""
    from app.models.model_volume import Volume
    from app.models.model_mask import Mask

    masks_dir = os.path.join(settings.BASE_DIR, "storage", "masks")
    os.makedirs(masks_dir, exist_ok=True)
    mask_path = os.path.join(masks_dir, f"{uuid.uuid4()}.npy")
    np.save(mask_path, mask_array)

    volume = Volume(
        patient_id="IMPLANT_TEST",
        series_instance_uid=f"implant-{uuid.uuid4()}",
        spacing=[1.0, 1.0, 1.0],
        dimensions=list(reversed(mask_array.shape)),
        origin=[0.0, 0.0, 0.0],
        direction=[1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0],
        file_path="storage/processed/placeholder.npy",
        meta_info={},
    )
    session.add(volume)
    session.commit()
    session.refresh(volume)

    mask = Mask(
        volume_id=volume.id,
        model_name="mock_bone_seg",
        model_version="1.0.0",
        file_path=os.path.relpath(mask_path, settings.BASE_DIR),
        meta_info={"labels": {0: "background", 1: "bone"}},
    )
    session.add(mask)
    session.commit()
    session.refresh(mask)
    return mask, mask_path


def test_implant_service_end_to_end():
    from app.core.database import SessionLocal

    session = SessionLocal()
    mask_path = None
    try:
        mask, mask_path = _seed_volume_and_mask(session, make_defective_bone_mask())

        service = ImplantService()
        record = service.generate_implant_record(
            mask_id=mask.id,
            model_name="mirror_implant",
            smooth_iterations=5,
            decimate_ratio=0.5,
            export_format="stl",
            session=session,
        )

        assert record.id is not None
        assert record.method == "mirroring"
        assert record.vertex_count > 0
        assert record.triangle_count > 0

        implant_path = os.path.join(settings.BASE_DIR, record.file_path)
        assert os.path.exists(implant_path)

        # cleanup generated implant file
        os.remove(implant_path)
        session.delete(record)
        session.commit()
    finally:
        if mask_path and os.path.exists(mask_path):
            os.remove(mask_path)
        session.close()


def test_mesh_obj_export_and_printability(client):
    # Upload -> segment -> reconstruct as OBJ -> printability check.
    zip_bytes = create_dicom_zip_bytes()
    volume_id = client.post(
        "/api/v1/volumes/upload",
        files={"file": ("scan.zip", zip_bytes, "application/zip")},
    ).json()["data"]["id"]

    task_id = client.post(
        f"/api/v1/inference/segment/{volume_id}",
        json={"model_name": "mock_bone_seg"},
    ).json()["data"]["task_id"]
    mask_id = client.get(f"/api/v1/inference/tasks/{task_id}").json()["data"]["result_id"]

    mesh_res = client.post(
        f"/api/v1/meshes/reconstruct/{mask_id}",
        json={"smooth_iterations": 10, "decimate_ratio": 0.3, "export_format": "obj"},
    )
    assert mesh_res.status_code == 201
    mesh_data = mesh_res.json()["data"]
    mesh_id = mesh_data["id"]
    assert mesh_data["file_path"].endswith(".obj")

    dl = client.get(f"/api/v1/meshes/{mesh_id}/download")
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "model/obj"

    printability = client.get(f"/api/v1/meshes/{mesh_id}/printability")
    assert printability.status_code == 200
    report = printability.json()["data"]
    assert report["is_watertight"] is True
    assert report["ready_to_print"] is True
    assert "issues" in report
