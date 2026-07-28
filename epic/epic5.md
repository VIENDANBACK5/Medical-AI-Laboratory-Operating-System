# System Design Document: FastAPI Backend Orchestration Architecture (Epic 5)

This document defines the production-grade architecture design for the MedAI-OS FastAPI backend, enforcing clean separation of concerns and layered abstraction boundaries.

---

## 1. Separation of Architectural Layers

The backend strictly segregates duties into five architectural layers:

```text
MedAI-OS Backend
├── API Layer (Routers & Pydantic DTOs)
├── Application Layer (Orchestration & Workflow Services)
├── Domain Layer (SQLAlchemy Models & Entities)
├── Infrastructure Layer (Database, Storage & Task Runner)
└── Research Layer (Python SDK Core Tools)
```

### A. API Layer (`app/api/`)
- **Responsibility**: Handles HTTP ingress/egress. Validates inputs using Pydantic, checks permissions/JWTs, and routes requests.
- **Constraint**: No direct database calls (`session.query`), raw filesystem manipulation, or AI preprocessing math are allowed in routers.

### B. Application Layer (`app/services/`)
- **Responsibility**: Coordinates complex business workflows (e.g., unzip -> read DICOM -> resample -> save -> commit database record).
- **Constraint**: Decoupled from HTTP protocols; functions take native Python types/objects.

### C. Domain Layer (`app/models/`, `app/schemas/`)
- **Responsibility**: Holds the business entities (`Volume`, `Mask`, `MeshRecord`) and data verification contracts.
- **Constraint**: Must not import services or external API drivers.

### D. Infrastructure Layer (`app/core/`, `app/utils/`)
- **Responsibility**: Database sessions (`SessionLocal`), configuration mapping, error handlers, and file operations.

### E. Research Layer (`sdk/`)
- **Responsibility**: Standalone programmatic API and metrics computation tools for offline scientific studies.

---

## 2. Comprehensive API Endpoints Listing

| Category | Endpoint | HTTP Method | Description |
| :--- | :--- | :---: | :--- |
| **Auth** | `/api/v1/auth/login` | `POST` | Generates JWT credentials |
| **Auth** | `/api/v1/auth/register` | `POST` | Registers new system users |
| **Volume** | `/api/v1/volumes/upload` | `POST` | Ingests ZIP (DICOM series) or NIfTI scan |
| **Volume** | `/api/v1/volumes/all` | `GET` | Paginated lists of active scans |
| **Volume** | `/api/v1/volumes/{id}` | `GET` | Fetches coordinate/spacing metadata |
| **Volume** | `/api/v1/volumes/{id}/download` | `GET` | Streams the resampled `.npy` volume |
| **Volume** | `/api/v1/volumes/{id}` | `DELETE` | Removes DB row and wipes numpy file |
| **Inference**| `/api/v1/inference/models` | `GET` | Lists auto-discovered AI plugins |
| **Inference**| `/api/v1/inference/segment/{id}`| `POST` | Triggers background segmentation |
| **Inference**| `/api/v1/inference/tasks/{id}` | `GET` | Polls progress state and tracking logs |
| **Inference**| `/api/v1/inference/masks/{id}` | `GET` | Queries mask metrics and path details |
| **Inference**| `/api/v1/inference/masks/{id}/download`| `GET` | Streams the predicted `.npy` bone mask |
| **Inference**| `/api/v1/inference/masks/{id}` | `DELETE` | Purges mask row and binary file |
| **Mesh** | `/api/v1/meshes/reconstruct/{id}`| `POST` | Triggers 3D marching cubes surface gen |
| **Mesh** | `/api/v1/meshes/all` | `GET` | Paginated lists of reconstructions |
| **Mesh** | `/api/v1/meshes/{id}` | `GET` | Queries vertices count, volume, watertight |
| **Mesh** | `/api/v1/meshes/{id}/download` | `GET` | Downloads the binary STL file |
| **Mesh** | `/api/v1/meshes/{id}` | `DELETE` | Removes mesh record and wipes STL file |

---

## 3. Data Transfer Objects (DTO) Schema Mapping

All payload exchange wraps inputs and outputs with strict validation:

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class InferenceTriggerRequest(BaseModel):
    model_name: str = Field(..., description="Target registered model name (e.g., 'mock_bone_seg')")

class MeshTriggerRequest(BaseModel):
    smooth_iterations: int = Field(default=10, ge=0, le=100)
    decimate_ratio: float = Field(default=0.1, gt=0.0, le=1.0)
```

---

## 4. Error Handling Strategy

Standardized exception mappings are processed by FastAPI middlewares, outputting clean HTTP error structures:

```json
{
  "http_code": 404,
  "message": "Segmentation mask record with ID 999 not found.",
  "data": null,
  "metadata": null
}
```

---

## 5. Security & Authentication Layer

Access is protected via OAuth2 Password Bearer flow:
1. **Password Hashing**: Uses `passlib[bcrypt]` to secure password verification records.
2. **Access Tokens**: Issues HMAC-SHA256 signed JSON Web Tokens (JWT) containing user UUID and role list.
3. **Role Dependency**: Guards endpoints using FastAPI dependencies (e.g. `Depends(RoleChecker(["researcher", "admin"]))`).

---

## 6. Storage & Disk Layout

Voxel and geometry data cache is isolated on local disks or block stores:
```text
storage/
├── original/     # Uploaded DICOM zip files and NIfTI volumes
├── processed/    # Normalized isotropic RAS float arrays (.npy)
├── masks/        # Predicted bone segmentations (.npy)
└── meshes/       # Reconstructed continuous STL files (.stl)
```

---

## 7. Background Tasks & Queue Architecture

To prevent CPU/GPU heavy calculations from blocking API responsiveness:
1. **Enqueuing**: The API issues a task UUID and responds with status `202 ACCEPTED` instantly.
2. **Execution**: FastAPI `BackgroundTasks` processes calculations in separate thread contexts.
3. **Database Thread Isolation**: Direct database context connections (`SessionLocal()`) are initialized inside tasks to bypass request-middleware constraints.
4. **Queue Transition**: The architecture decouples the service layer to easily plug in Celery/Redis workers for cluster scale.
