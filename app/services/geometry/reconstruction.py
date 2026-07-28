from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np
import trimesh
from skimage.measure import marching_cubes


class IMeshEngine(ABC):
    @abstractmethod
    def generate_mesh(
        self, mask: np.ndarray, spacing: Tuple[float, float, float]
    ) -> trimesh.Trimesh:
        """
        Extracts 3D triangular surface mesh from volumetric binary mask.
        
        Args:
            mask: 3D binary numpy array [z, y, x]
            spacing: Voxel spacing in mm [dz, dy, dx]
            
        Returns:
            trimesh.Trimesh object
        """
        pass


class skimageMeshEngine(IMeshEngine):
    def generate_mesh(
        self, mask: np.ndarray, spacing: Tuple[float, float, float]
    ) -> trimesh.Trimesh:
        if mask is None or mask.size == 0:
            raise ValueError("Input mask array is empty.")
            
        # Ensure mask is binary and has bone boundaries
        if mask.max() == 0:
            raise ValueError("Voxel mask does not contain any positive tissue labels.")

        # Run marching cubes. Level=0.5 splits binary boundary [0, 1].
        # skimage.measure.marching_cubes expects spacing in the order of array axes,
        # which is [dz, dy, dx] corresponding to array dimensions [z, y, x].
        vertices, faces, normals, _ = marching_cubes(
            volume=mask,
            level=0.5,
            spacing=spacing
        )

        # Create a Trimesh object
        mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=faces,
            vertex_normals=normals,
            validate=True
        )

        return mesh
