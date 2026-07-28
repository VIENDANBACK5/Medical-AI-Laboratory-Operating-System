# MedAI-OS · React 3D Clinical Suite (frontend)

A React + [react-three-fiber](https://docs.pmnd.rs/react-three-fiber) client that
drives the full backend pipeline end to end:

**Login → Upload/select a Volume → AI Segmentation → Mesh Reconstruction (+ printability check) → AI Implant Recommendation → download STL/OBJ/PLY.**

Both the segmentation and implant model dropdowns are populated **dynamically**
from the backend's plugin registries (`GET /inference/models`, `GET /implants/models`),
so newly dropped-in plugins (e.g. a real `totalsegmentator_bone`, or a future
generative implant model) show up automatically without any frontend change.

## Setup

```bash
cd frontend
npm install
npm run dev      # starts Vite dev server on http://localhost:5173
```

```bash
npm run build     # production build to frontend/dist
npm run preview   # preview the production build locally
```

## Run

1. Start the backend API (from the repo root):

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend dev server (above) and open <http://localhost:5173>.

3. In the sidebar:
   - **API Server Node**: defaults to `http://localhost:8000/api/v1`.
   - **User Authentication**: Register (first run), then Log In — the JWT is
     stored in `localStorage` and sent as `Authorization: Bearer <token>` on
     every request.
   - **Volumetric Ingestion**: upload a DICOM `.zip` or NIfTI `.nii.gz`, or pick
     an existing volume from the list.
   - **AI Segmentation**: pick a discovered model and run it; progress is
     polled until the resulting mask is ready.
   - **3D Mesh Reconstruction**: tune smoothing/decimation, pick an export
     format (STL/OBJ/PLY), reconstruct, and view the bone mesh in the 3D
     viewport. A printability report (watertight / winding / Euler number)
     appears automatically.
   - **Implant PSI Recommendation**: pick an implant model (e.g. the
     `mirror_implant` contralateral-mirroring baseline), generate, and view the
     proposed implant (gold) alongside the bone mesh (grey).
   - Download either mesh from the floating viewport HUD.

## Notes

- CORS is already open on the backend (`BACKEND_CORS_ORIGINS=["*"]`), so no dev
  proxy is required.
- STL/OBJ/PLY bytes are fetched with the `Authorization` header and parsed
  client-side (`STLLoader`/`OBJLoader`/`PLYLoader` from `three/examples/jsm`),
  so the auth-protected download endpoints work directly.
- This client requires Node.js/npm locally to install and run; it was not
  built/verified in the assistant's sandbox because Node was not available
  there. Run `npm install && npm run build` yourself to confirm the production
  build compiles cleanly.
