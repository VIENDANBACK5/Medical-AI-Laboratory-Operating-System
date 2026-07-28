# System Design Document: Volumetric 3D Geometry Processing Pipeline (Epic 7)

This document defines the mathematical, algorithmic, and software architecture for transforming discrete voxel matrices into continuous optimized 3D meshes (STL, PLY, OBJ), utilizing VTK, Open3D, CGAL, and PyMeshLab plugins.

---

## 1. Algorithmic Data Pipeline

The geometry engine converts volumetric segmentation labels into physical 3D printing formats in six sequential steps:

```text
Voxel Mask Array
  │
  ▼  [1. Marching Cubes]
Vertices, Faces & Normals (Anisotropic space coordinates)
  │
  ▼  [2. Spatial Scaling]
Physical Coordinates (RAS coordinate space in mm units)
  │
  ▼  [3. Mesh Smoothing]
Polished Surface Mesh (Laplace/Taubin filters - staircasing removed)
  │
  ▼  [4. Mesh Decimation]
Simplified Triangle count (Quadric Error Metric - reduced file sizes)
  │
  ▼  [5. Topology Repair]
Watertight Solid Geometry (Normals aligned, boundary holes closed)
  │
  ▼  [6. Exporters]
STL / PLY / OBJ outputs (Clinical deployment & 3D Printing ready)
```

---

## 2. Library Integration & Plugin Interfaces

To prevent hard-coupling with any single geometry framework, the system exposes an abstract geometry pipeline interface. Individual libraries are wrapped as hot-swappable plugins.

```python
from abc import ABC, abstractmethod
import trimesh

class IGeometryPlugin(ABC):
    @abstractmethod
    def reconstruct(self, voxel_mask: bytes, spacing: tuple) -> trimesh.Trimesh:
        """Runs Marching Cubes surface extraction."""
        pass

    @abstractmethod
    def smooth(self, mesh: trimesh.Trimesh, iterations: int) -> trimesh.Trimesh:
        """Applies surface smoothing without volume loss."""
        pass

    @abstractmethod
    def simplify(self, mesh: trimesh.Trimesh, face_count: int) -> trimesh.Trimesh:
        """Reduces polygon counts using error-metric decimation."""
        pass

    @abstractmethod
    def repair(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Fills holes and validates manifold properties."""
        pass
```

### A. Open3D Plugin
- **Simplification**: Employs `open3d.geometry.TriangleMesh.simplify_quadric_decimation` for fast face reduction.
- **Normals**: Aligns vertex normal vectors using covariance matrices computation.

### B. VTK (Visualization Toolkit) Plugin
- **Marching Cubes**: Employs `vtkDiscreteMarchingCubes` to support smooth multi-labeled tissue boundaries.
- **Smoothing**: Employs `vtkWindowedSincPolyDataFilter` (Taubin smoothing) to prevent structural shrinkage.

### C. CGAL (Computational Geometry Algorithms Library) Plugin
- **Repair**: Employs `CGAL::Polygon_mesh_processing::triangulate_hole` and self-intersection solvers to guarantee watertight manifold structures.
- **Boolean operations**: Highly robust Constructive Solid Geometry (CSG) subtraction math.

### D. PyMeshLab Plugin
- **Decimation**: Employs MeshLab's high-fidelity quadric decimation filters.

---

## 3. Data Formats & Exporters

Reconstructed objects are saved to disk or network storage:
- **STL (Standard Triangle Language)**: Standard raw triangles representation for 3D printing slicers.
- **PLY (Polygon File Format)**: Encodes vertex normal vectors and label colors for interactive clinical visualizer rendering.
- **OBJ (Wavefront OBJ)**: General graphics coordinate structure for integration with external biomechanical simulation engines.
