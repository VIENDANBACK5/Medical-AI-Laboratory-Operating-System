import os
import uuid
import numpy as np
from fastapi_sqlalchemy import db
from scipy.ndimage import label

from app.core.config import settings
from app.models.model_mask import Mask
from app.models.model_mesh import MeshRecord
from app.services.geometry.reconstruction import skimageMeshEngine
from app.services.geometry.smoothing import smooth_mesh
from app.services.geometry.decimation import decimate_mesh
from app.services.geometry.repair import repair_and_verify
from app.services.geometry.exporter import export_mesh
from app.services.srv_base import BaseService


def remove_small_components(mask: np.ndarray, min_size: int = 1000) -> np.ndarray:
    """
    Removes small isolated connected components (voxel noise) from a 3D binary mask.
    """
    labeled_array, num_features = label(mask)
    if num_features == 0:
        return mask
    sizes = np.bincount(labeled_array.ravel())
    # Find labels that meet the size threshold (excluding background 0)
    valid_labels = np.where(sizes >= min_size)[0]
    valid_labels = valid_labels[valid_labels != 0]
    if len(valid_labels) == 0:
        # Fallback: keep the single largest component
        largest_label = np.argmax(sizes[1:]) + 1
        return (labeled_array == largest_label).astype(np.uint8)
    return np.isin(labeled_array, valid_labels).astype(np.uint8)


class MeshService(BaseService[MeshRecord]):
    def __init__(self):
        super().__init__(MeshRecord)
        self.engine = skimageMeshEngine()
        
        # Setup storage directories
        self.storage_dir = os.path.join(settings.BASE_DIR, "storage")
        self.meshes_dir = os.path.join(self.storage_dir, "meshes")
        os.makedirs(self.meshes_dir, exist_ok=True)

    def generate_mesh_record(
        self,
        mask_id: int,
        smooth_iterations: int = 10,
        decimate_ratio: float = 0.1,
        export_format: str = "stl",
        session = None
    ) -> MeshRecord:
        """
        Coordinates the complete reconstruction, optimization, repair, 
        and STL export pipeline for a given segmentation mask ID.
        """
        # Support running within direct SessionLocal scopes or HTTP request contexts
        db_sess = session if session else db.session

        # 1. Retrieve the Mask and its associated Volume metadata
        mask = db_sess.query(Mask).get(mask_id)
        if not mask:
            raise FileNotFoundError(f"Segmentation mask record with ID {mask_id} not found.")

        volume = mask.volume
        if not volume:
            raise FileNotFoundError(f"Associated raw volume for mask {mask_id} not found.")

        # 2. Load the binary label voxel matrix from disk
        mask_path = os.path.join(settings.BASE_DIR, mask.file_path)
        if not os.path.exists(mask_path):
            raise FileNotFoundError(f"Voxel array file not found at {mask_path}")
        
        mask_array = np.load(mask_path)

        # volume.spacing is stored in SimpleITK x,y,z order [dx, dy, dz]. The mask
        # array is in numpy z,y,x order, so the spacing must be reversed to
        # [dz, dy, dx] to line up with the array axes for marching cubes.
        spacing = tuple(reversed(volume.spacing))  # [dz, dy, dx]

        # 3. Clean voxel noise before running marching cubes
        mask_array = remove_small_components(mask_array, min_size=1000)

        # 4. Step A: Marching Cubes Surface Extraction
        mesh = self.engine.generate_mesh(mask_array, spacing)

        # 5. Step B: Mesh repair (Normals fixing, hole filling, watertight closure)
        # Repair is executed first to clean topology before decimation/smoothing destroys borders
        mesh = repair_and_verify(mesh)

        # 6. Step C: Taubin Vertex Smoothing
        if smooth_iterations > 0:
            mesh = smooth_mesh(mesh, iterations=smooth_iterations)

        # 7. Step D: Quadric Decimation (Triangle Simplification)
        if decimate_ratio < 1.0:
            mesh = decimate_mesh(mesh, decimate_ratio=decimate_ratio)

        # 8. Extract topology stats and volumes
        vertex_count = len(mesh.vertices)
        triangle_count = len(mesh.faces)
        
        # Calculate signed volume absolute value to approximate volume for non-watertight structures
        volume_mm3 = abs(float(mesh.volume))
        is_watertight = bool(mesh.is_watertight)

        # 8. Save mesh file to disk in the requested format (STL / OBJ / PLY)
        export_format = (export_format or "stl").lower()
        if export_format not in ("stl", "obj", "ply"):
            raise ValueError(f"Unsupported export format '{export_format}'. Use stl, obj, or ply.")
        mesh_uuid = str(uuid.uuid4())
        mesh_path = os.path.join(self.meshes_dir, f"{mesh_uuid}.{export_format}")
        export_mesh(mesh, mesh_path, file_type=export_format)

        # 9. Create and save MeshRecord in database
        mesh_record = MeshRecord(
            mask_id=mask_id,
            vertex_count=vertex_count,
            triangle_count=triangle_count,
            volume_mm3=volume_mm3,
            is_watertight=is_watertight,
            file_path=os.path.relpath(mesh_path, settings.BASE_DIR),
            meta_info={
                "smooth_iterations": smooth_iterations,
                "decimate_ratio": decimate_ratio,
                "export_format": export_format,
            }
        )

        db_sess.add(mesh_record)
        db_sess.commit()
        db_sess.refresh(mesh_record)

        return mesh_record

    def assess_printability(self, mesh_id: int, session=None) -> dict:
        """Evaluate whether a stored mesh is ready for 3D printing.

        Loads the mesh file from disk and inspects the geometric properties that
        gate a successful print: a closed (watertight) surface, consistent face
        winding/normals, non-empty geometry, and a valid manifold (Euler number).
        """
        import trimesh

        db_sess = session if session else db.session
        record = db_sess.query(MeshRecord).get(mesh_id)
        if not record:
            raise FileNotFoundError(f"Mesh record with ID {mesh_id} not found.")

        mesh_path = os.path.join(settings.BASE_DIR, record.file_path)
        if not os.path.exists(mesh_path):
            raise FileNotFoundError(f"Mesh file not found at {mesh_path}")

        mesh = trimesh.load(mesh_path, force="mesh")

        is_watertight = bool(mesh.is_watertight)
        winding_consistent = bool(mesh.is_winding_consistent)
        is_empty = bool(mesh.is_empty) or len(mesh.faces) == 0
        bbox = (mesh.extents.tolist() if not is_empty else [0.0, 0.0, 0.0])

        issues = []
        if is_empty:
            issues.append("Mesh is empty (no faces).")
        if not is_watertight:
            issues.append("Mesh is not watertight; open boundaries must be closed before printing.")
        if not winding_consistent:
            issues.append("Face winding/normals are inconsistent.")

        return {
            "mesh_id": mesh_id,
            "is_watertight": is_watertight,
            "winding_consistent": winding_consistent,
            "is_empty": is_empty,
            "volume_mm3": float(mesh.volume) if is_watertight else 0.0,
            "area_mm2": float(mesh.area) if not is_empty else 0.0,
            "euler_number": int(mesh.euler_number) if not is_empty else 0,
            "bounding_box_mm": [float(x) for x in bbox],
            "ready_to_print": is_watertight and winding_consistent and not is_empty,
            "issues": issues,
        }
