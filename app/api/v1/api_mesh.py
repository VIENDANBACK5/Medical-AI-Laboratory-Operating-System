import os
from typing import Any, List
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.sche_response import DataResponse
from app.schemas.sche_base import SortParams, PaginationParams
from app.schemas.sche_mesh import MeshTriggerRequest, MeshResponse, PrintabilityResponse
from app.services.geometry.mesh_service import MeshService
from app.utils.exception_handler import CustomException, ExceptionType
from app.utils.login_manager import login_required

router = APIRouter(prefix="/meshes", dependencies=[Depends(login_required)])

mesh_service = MeshService()


@router.post(
    "/reconstruct/{mask_id}",
    response_model=DataResponse[MeshResponse],
    status_code=status.HTTP_201_CREATED,
)
def reconstruct_mesh(
    mask_id: int,
    request_data: MeshTriggerRequest,
) -> Any:
    """
    Triggers 3D surface mesh reconstruction from a volumetric segmentation mask.
    Applies Laplacian smoothing and Quadric decimation, then repairs and exports to STL.
    """
    try:
        mesh_record = mesh_service.generate_mesh_record(
            mask_id=mask_id,
            smooth_iterations=request_data.smooth_iterations,
            decimate_ratio=request_data.decimate_ratio,
            export_format=request_data.export_format,
        )
        return DataResponse(http_code=status.HTTP_201_CREATED, data=mesh_record)
    except FileNotFoundError as fnfe:
        raise CustomException(
            http_code=status.HTTP_404_NOT_FOUND,
            message=str(fnfe)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException(exception=e)


@router.get(
    "/all",
    response_model=DataResponse[List[MeshResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all(sort_params: SortParams = Depends()) -> Any:
    try:
        data, metadata = mesh_service.get_all(sort_params)
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "",
    response_model=DataResponse[List[MeshResponse]],
    status_code=status.HTTP_200_OK,
)
def get_by_filter(
    sort_params: SortParams = Depends(),
    pagination_params: PaginationParams = Depends(),
) -> Any:
    try:
        data, metadata = mesh_service.get_by_filter(
            pagination_params=pagination_params, sort_params=sort_params
        )
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{mesh_id}",
    response_model=DataResponse[MeshResponse],
    status_code=status.HTTP_200_OK,
)
def get_by_id(mesh_id: int) -> Any:
    try:
        mesh = mesh_service.get_by_id(id=mesh_id)
        return DataResponse(http_code=status.HTTP_200_OK, data=mesh)
    except Exception as e:
        raise CustomException(exception=e)


_MESH_MEDIA_TYPES = {
    "stl": "application/sla",
    "obj": "model/obj",
    "ply": "application/octet-stream",
}


@router.get(
    "/{mesh_id}/download",
    status_code=status.HTTP_200_OK,
)
def download_mesh(mesh_id: int) -> FileResponse:
    """Downloads the reconstructed 3D surface mesh (STL / OBJ / PLY)."""
    try:
        mesh = mesh_service.get_by_id(id=mesh_id)
        full_path = os.path.join(settings.BASE_DIR, mesh.file_path)

        if not os.path.exists(full_path):
            raise CustomException(
                http_code=status.HTTP_404_NOT_FOUND,
                message="Mesh file not found on disk."
            )

        ext = os.path.splitext(full_path)[1].lstrip(".").lower() or "stl"
        return FileResponse(
            path=full_path,
            filename=f"reconstruction_{mesh.id}.{ext}",
            media_type=_MESH_MEDIA_TYPES.get(ext, "application/octet-stream"),
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{mesh_id}/printability",
    response_model=DataResponse[PrintabilityResponse],
    status_code=status.HTTP_200_OK,
)
def check_printability(mesh_id: int) -> Any:
    """Assess whether the reconstructed mesh is ready for 3D printing."""
    try:
        report = mesh_service.assess_printability(mesh_id=mesh_id)
        return DataResponse(
            http_code=status.HTTP_200_OK, data=PrintabilityResponse(**report)
        )
    except FileNotFoundError as fnfe:
        raise CustomException(http_code=status.HTTP_404_NOT_FOUND, message=str(fnfe))
    except Exception as e:
        raise CustomException(exception=e)


@router.delete(
    "/{mesh_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_mesh_record(mesh_id: int) -> None:
    """Deletes a mesh record and cleans its physical STL file off disk."""
    try:
        mesh = mesh_service.get_by_id(id=mesh_id)
        full_path = os.path.join(settings.BASE_DIR, mesh.file_path)
        
        # Clean disk file
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass
                
        mesh_service.delete_by_id(id=mesh_id)
    except Exception as e:
        raise CustomException(exception=e)
