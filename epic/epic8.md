# System Design Document: Generative Implant Recommendation CAD Module (Epic 8)

This document defines the architecture design for the experimental Patient-Specific Implant (PSI) generation subsystem. It enforces model-agnostic abstraction boundaries to support future geometric deep learning technologies.

---

## 1. Modular CAD Pipeline Design

The implant generation system operates as a separate experimental service layer (`app/services/implant/`) isolated from core production routers. It follows a multi-stage coordinate alignment and shape-fitting workflow:

```text
Defective Bone Mesh
  │
  ├──────► [ ICP Alignment ] ──► Align mirrored contralateral anatomy
  │
  ├──────► [ Generative AI ]  ──► PointNet / SDF / Mesh Transformers shape completion
  │
  ▼
Proposed Reconstruction Shape (Overlapping defect boundary)
  │
  ▼  [ CSG Boolean Math ]
Margin Fit Clearance Cut (Proposed shape minus defective bone)
  │
  ▼  [ Validation checks ]
Wall Thickness & Structural Stress Analysis
  │
  ▼  [ Exporters ]
STEP / IGES (via OpenCascade) / STL CAD Files
```

---

## 2. Model-Agnostic AI Interface

To allow researchers to plug in future Deep Learning networks without modifying database schemas:

```python
from abc import ABC, abstractmethod
import trimesh

class IImplantModel(ABC):
    @abstractmethod
    def complete_defect(self, incomplete_mesh: trimesh.Trimesh, defect_mask_path: str) -> trimesh.Trimesh:
        """Runs the generative shape completion pipeline and returns the closed anatomy."""
        pass
```

---

## 3. Supported Generative Architectures

The framework provides stub configurations and data-mappers to integrate five major geometric deep learning models:

- **PointNet / PointNet++**: Extracts edge features from raw point clouds of boundary defects and outputs coordinates for missing elements.
- **Mesh Transformers**: Processes vertex indices as sequence tokens to directly predict missing surface faces.
- **Implicit Surfaces / Signed Distance Functions (SDF)**: Evaluates a neural coordinate field to reconstruct smooth organic geometry.
- **Diffusion Models**: Formulates shape generation as denoising voxelized grids or point arrays.
- **Generative Design Optimizer**: Traditional FEA-based topological optimization to compute organic implant skeletons.

---

## 4. Fitting & Clearance Boolean Solver

To produce a clinical implant ready for surgery:
- **Mirroring & ICP**: In case of unilateral defects, the contralateral healthy region is mirrored across the sagittal plane and aligned using Iterative Closest Point (ICP).
- **Constructive Solid Geometry (CSG)**: Computes the Boolean Difference between the completed shape and defective bone.
- **Clearance Margins**: Shrinks contact edges by a tolerance clearance ($0.2\text{ mm}$) to ensure insertion fit.

---

## 5. CAD Integration & Exporters

Implant meshes are converted to standard engineering assets:
- **STL/PLY Exporters**: For rapid prototyping 3D printers.
- **OpenCascade Wrapper**: Integrates the `cad_exporter` to convert triangulated STL surfaces into continuous boundary representations (B-Rep) saved as **STEP** or **IGES** formats, allowing direct import into commercial CAD environments (AutoCAD, SOLIDWORKS).
