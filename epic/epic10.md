# System Design Document: Platform Milestone Roadmap (Epic 10)

This document establishes the structural timeline and validation checkpoints for the MedAI-OS platform. Every milestone constitutes an independent, runnable, and demoable product increment.

---

## 1. Roadmap Overview & Demo Checks

```text
Milestone 1 (Ingestion MVP) ──► Demo: CLI/REST scan upload & metadata parsing
       │
Milestone 2 (MPR Visualizer) ──► Demo: 2D orthogonal slices (Axial, Coronal, Sagittal)
       │
Milestone 3 (Segmentation Engine) ──► Demo: Queue-based bone mask segmentation
       │
Milestone 4 (Surface Mesh Engine) ──► Demo: Interactive 3D WebGL mesh rendering
       │
Milestone 5 (Production Exporter) ──► Demo: Watertight STL mesh output check
       │
Milestone 6 (Research SDK) ──► Demo: Headless batch comparisons (Dice/HD95)
       │
Milestone 7 (Generative CAD) ──► Demo: Mirrored defect implant export (STEP)
```

---

## 2. Milestone Details

### Milestone 1: Ingestion MVP
- **Components Built**: `SimpleITKVolumeReader` standardizing scan coordinate spaces, `VolumePreprocessor` resampling arrays, `Volume` database schema, and `/upload` route.
- **Independent Demo**: User uploads a clinical DICOM series via the swagger documentation page (`/docs`). The server registers the volume in SQLite/Postgres and responds with patient metadata and isotropic spacing in less than 5 seconds.

### Milestone 2: Multi-planar Visualizer
- **Components Built**: CornerstoneJS frontend integrations, Zustand state store managers, and `/download` voxel chunk controllers.
- **Independent Demo**: User selects a volume ID on the frontend dashboard. The browser queries the API, caches slices, and renders Axial, Coronal, and Sagittal orthogonal cross-sections with window level controls.

### Milestone 3: AI Segmentation Engine
- **Components Built**: `AIEngineManager` plugin registration, `AIInferenceService` background thread task trackers, `/segment` endpoint, and `Mask` schema.
- **Independent Demo**: User calls `/api/v1/inference/segment/{id}` selecting model `mock_bone_seg`. The server executes background calculations, updates task logs, and saves the binary bone mask.

### Milestone 4: Surface Mesh Engine
- **Components Built**: `skimageMeshEngine` marching cubes, Laplacian smoothing filters, Open3D simplification wrappers, and Three.js/R3F meshes viewers.
- **Independent Demo**: User requests 3D rendering for an output mask. The client loads geometry buffers and displays an interactive 3D bone structure with rotate/zoom capabilities.

### Milestone 5: Production Exporter
- **Components Built**: `repair_and_verify` normal cleaners and boundary closures, STL exporters, and `/meshes/{id}/download` streaming files.
- **Independent Demo**: User clicks the download button in the dashboard. The server generates a watertight STL mesh, verifies boundaries count is 0, and downloads the SLA-printable CAD asset.

### Milestone 6: Research SDK
- **Components Built**: Python `sdk` package modules, fluent chaining managers, Dice/Hausdorff scoring metrics, and CLI terminals.
- **Independent Demo**: User runs `python -m sdk.cli --dataset v1.0 --model MedSAM --epochs 5 --report my_paper_report.md` in the terminal. The SDK runs training, computes metrics, and writes an evaluation markdown report without starting the Web visualizer.

### Milestone 7: Generative CAD
- **Components Built**: Mirroring modules, Boolean margin clearances subtractors, and STEP/IGES format wrappers.
- **Independent Demo**: User uploads a cranial defect skull mesh. The AI mirrors the contralateral bone, aligns coordinates using ICP, cuts matching clearance edges, and exports a surgical-ready STEP file.
