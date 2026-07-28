# System Design Document: React Frontend & ThreeJS Architecture (Epic 6)

This document defines the architecture blueprint, UI page structure, global state layout, and 3D WebGL viewport components for the MedAI-OS React web application.

---

## 1. Application Layout & Pages Design

The application is structured as a medical dashboard consisting of nine dedicated workspaces:

- **Dashboard**: High-level telemetry displaying computed volumes counts, GPU server resource usages, active background queue metrics, and patient lists.
- **Upload**: Interactive dropzone supporting DICOM ZIP folder uploads and single NIfTI files with automated background parsing progress logs.
- **Study**: Database query page showing uploaded scans list, patient administrative records, and options to trigger AI actions.
- **3D Viewer**: High-fidelity computational viewport displaying orthopedic meshes with camera controls, slicing plane clip ranges, and anatomical coordinate grids.
- **Experiments**: SDK tracking panel showing metrics comparisons, validation runs, training graphs, and parameters.
- **Models**: Management grid detailing active registered AI plugins, hardware VRAM footprints, versions, and validation histories.
- **Datasets**: Tracking page listing versioned training sets, download URLs, and metadata tags (e.g. `v1.0`, `v2.1`).
- **Settings**: Administrative setup panel (server REST hosts URLs, API timeouts, GPU worker allocations).
- **Future Research**: Conceptual portal containing active planning drafts (e.g., Finite Element Analysis stubs, biomechanical simulator options).

---

## 2. Component Hierarchy Tree

```text
App (Router)
├── Navbar (Branding & Global User Profiles)
├── AppLayout
│   ├── Sidebar (Workspace selection navigation links)
│   └── MainContent
│       ├── DashboardPage
│       │   ├── TelemetryGrid (Stats cards: Scans count, Meshes, VRAM)
│       │   └── PatientTable (Active patients list)
│       ├── UploadPage
│       │   ├── FileDropzone (Drag-and-drop file handler)
│       │   └── UploadProgressBar (Voxel preprocessing state tracker)
│       ├── StudyPage
│       │   ├── SearchBar (Filter metadata entries)
│       │   └── VolumeList (Detail metadata list card)
│       └── ViewerPage
│           ├── WorkSpaceLayout
│           │   ├── Viewer2D (Axial, Coronal, Sagittal MPR views)
│           │   ├── Viewer3D (WebGL React Three Fiber canvas)
│           │   │   ├── OrbitControls (Camera rotation, zoom)
│           │   │   ├── LightingSystem (Ambient, directional lights)
│           │   │   ├── MeshContainer (Loaded STL/OBJ buffers)
│           │   │   ├── ClippingPlanes (Mesh cross-section slicing planes)
│           │   │   └── CoordinateAxesHelper (Anatomical RAS labels gizmo)
│           │   └── ToolbarPanel
│           │       ├── ControlSliders (Opacity, clipping depths)
│           │       └── AITriggerButton (Request inference call)
