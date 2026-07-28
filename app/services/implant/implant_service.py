import os
import uuid
import numpy as np
from fastapi_sqlalchemy import db

from app.core.config import settings
from app.models.model_mask import Mask
from app.models.model_implant import ImplantRecord
from app.services.implant.manager import ImplantEngineManager
from app.services.geometry.reconstruction import skimageMeshEngine
from app.services.geometry.smoothing import smooth_mesh
from app.services.geometry.repair import repair_and_verify
from app.services.geometry.exporter import export_mesh
from app.services.srv_base import BaseService


class ImplantService(BaseService[ImplantRecord]):
    """Orchestrates implant recommendation: run an implant plugin on a bone mask,
    then reconstruct, repair and export the proposed implant as a printable mesh.
    """

    def __init__(self):
        super().__init__(ImplantRecord)
        self.manager = ImplantEngineManager()
        self.engine = skimageMeshEngine()

        self.storage_dir = os.path.join(settings.BASE_DIR, "storage")
        self.implants_dir = os.path.join(self.storage_dir, "implants")
        os.makedirs(self.implants_dir, exist_ok=True)

    def generate_implant_record(
        self,
        mask_id: int,
        model_name: str = "mirror_implant",
        smooth_iterations: int = 10,
        decimate_ratio: float = 0.2,
        export_format: str = "stl",
        session=None,
    ) -> ImplantRecord:
        db_sess = session if session else db.session

        export_format = (export_format or "stl").lower()
        if export_format not in ("stl", "obj", "ply"):
            raise ValueError(f"Unsupported export format '{export_format}'. Use stl, obj, or ply.")

        # 1. Load the source bone mask and its spatial metadata.
        mask = db_sess.query(Mask).get(mask_id)
        if not mask:
            raise FileNotFoundError(f"Segmentation mask record with ID {mask_id} not found.")

        volume = mask.volume
        if not volume:
            raise FileNotFoundError(f"Associated raw volume for mask {mask_id} not found.")

        mask_path = os.path.join(settings.BASE_DIR, mask.file_path)
        if not os.path.exists(mask_path):
            raise FileNotFoundError(f"Voxel array file not found at {mask_path}")

        mask_array = np.load(mask_path)

        # volume.spacing is SimpleITK x,y,z order; reverse to array order [dz, dy, dx].
        spacing = tuple(reversed(volume.spacing))

        # 2. Run the implant plugin to propose the defect-filling voxel region.
        plugin = self.manager.get_plugin(model_name)
        plugin.initialize()
        implant_mask = plugin.generate(mask_array, spacing)

        # 3. Reconstruct + smooth + repair the implant into a watertight mesh,
        #    reusing the shared geometry pipeline.
        mesh = self.engine.generate_mesh(implant_mask, spacing)
        if smooth_iterations > 0:
            mesh = smooth_mesh(mesh, iterations=smooth_iterations)
        if 0.0 < decimate_ratio < 1.0:
            from app.services.geometry.decimation import decimate_mesh
            mesh = decimate_mesh(mesh, decimate_ratio=decimate_ratio)
        mesh = repair_and_verify(mesh)

        vertex_count = len(mesh.vertices)
        triangle_count = len(mesh.faces)
        is_watertight = bool(mesh.is_watertight)
        volume_mm3 = float(mesh.volume) if is_watertight else 0.0

        # 4. Export the implant mesh to disk.
        implant_uuid = str(uuid.uuid4())
        implant_path = os.path.join(self.implants_dir, f"{implant_uuid}.{export_format}")
        export_mesh(mesh, implant_path, file_type=export_format)

        info = plugin.get_info()

        # 5. Persist the implant record.
        implant_record = ImplantRecord(
            mask_id=mask_id,
            plugin_name=info.name,
            plugin_version=info.version,
            method=info.method,
            vertex_count=vertex_count,
            triangle_count=triangle_count,
            volume_mm3=volume_mm3,
            is_watertight=is_watertight,
            file_path=os.path.relpath(implant_path, settings.BASE_DIR),
            meta_info={
                "smooth_iterations": smooth_iterations,
                "decimate_ratio": decimate_ratio,
                "export_format": export_format,
            },
        )

        db_sess.add(implant_record)
        db_sess.commit()
        db_sess.refresh(implant_record)

        return implant_record
