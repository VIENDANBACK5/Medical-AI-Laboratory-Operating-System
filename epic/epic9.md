# System Design Document: Clinical Verification & Testing Strategy (Epic 9)

This document defines the quality assurance, mathematical verification, and clinical safety testing strategies for the MedAI-OS platform.

---

## 1. Multi-Tiered Testing Strategy

To guarantee patient safety, spatial precision, and database state invariants, testing is partitioned into five distinct layers:

```text
MedAI-OS Testing Matrix
├── Unit Tests (Fast, mathematical, no DB dependencies)
├── Integration Tests (FastAPI controllers, database state, I/O writes)
├── Performance & Telemetry (VRAM allocations, execution speed, FPS)
├── Validation Suites (Plugin schemas, watertight mesh checks)
└── Clinical Verification (Mesh vs. Voxel spatial deviation, phantoms)
```

---

## 2. Testing Specifications

### A. Unit Testing
- **Volume Preprocessing**: Asserts coordinate origin consistency, grid sizes, and spacing parameters after isotropic resampling.
- **Mesh Math**: Verifies sphere volume calculations against mathematical expectations.
- **SDK Fluent API**: Verifies state transitions and chained return types.

### B. Integration Testing
- **FASTAPI Routing**: Simulates multipart ZIP uploads and asserts HTTP status codes.
- **Database Transactions**: Asserts SQL parameter bindings and ensures rollbacks are executed on test finishes.
- **Background Tasks**: Validates async task state updates.

### C. Clinical & Medical Verification
- **Geometry Deviation**: Computes Hausdorff Distance between the reconstructed surface mesh boundary and the original voxel mask boundary. Verified deviation must not exceed $0.1\text{ mm}$ to ensure implant fitting accuracy.
- **Watertightness Checks**: Asserts mesh boundary edges count is exactly zero (no open holes).
- **Physical Calibration**: Employs standardized phantom datasets (e.g. geometric cubes) to verify physical scale metrics.

### D. Performance & VRAM Telemetry
- **Memory Leak Testing**: Tracks CUDA peak VRAM allocation before, during, and after inference runs using `torch.cuda.memory_allocated()` to confirm allocations are cleaned.
- **Query Latencies**: Tracks API response times under load.
- **Frame Rate (FPS)**: Asserts WebGL rendering canvas maintains stable $\ge 60\text{ FPS}$ on client-side visualizers.

---

## 3. Automated Validation Test Command Matrix

| Test Suite | Command | target validation |
| :--- | :--- | :--- |
| **I/O Engine** | `pytest tests/test_io.py` | DICOM sorting, LPS-RAS origin mappings |
| **REST Controllers** | `pytest tests/test_api_volume.py` | Upload endpoints, database record inserts |
| **Inference Engine** | `pytest tests/test_inference.py` | Dynamic plugin scanner, async job states |
| **Mesh Reconstructor**| `pytest tests/test_geometry.py` | Marching cubes, smoothing, watertight checks |
| **Research SDK** | `pytest tests/test_sdk.py` | Chaining validation, CLI sys.argv mock runs |
| **Memory Profiles** | `pytest tests/test_perf.py` | Peak CUDA allocations, garbage collections |
