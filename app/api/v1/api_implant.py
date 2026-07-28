import os
from typing import Any, List
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.sche_response import DataResponse
from app.schemas.sche_base import SortParams, PaginationParams
from app.schemas.sche_implant import (
    ImplantModelInfoResponse,
    ImplantTriggerRequest,
    ImplantResponse,
)
from app.services.implant.implant_service import ImplantService
from app.utils.exception_handler import CustomException
from app.utils.login_manager import login_required

router = APIRouter(prefix="/implants", dependencies=[Depends(login_required)])

implant_service = ImplantService()

_MESH_MEDIA_TYPES = {
    "stl": "application/sla",
    "obj": "model/obj",
    "ply": "application/octet-stream",
}


@router.get(
    "/models",
    response_model=DataResponse[List[ImplantModelInfoResponse]],
    status_code=status.HTTP_200_OK,
)
def list_implant_models() -> Any:
    """List all auto-discovered implant generation plugins."""
    try:
        models = implant_service.manager.list_models()
        return DataResponse(http_code=status.HTTP_200_OK, data=models)
    except Exception as e:
        raise CustomException(exception=e)


@router.post(
    "/recommend/{mask_id}",
    response_model=DataResponse[ImplantResponse],
    status_code=status.HTTP_201_CREATED,
)
def recommend_implant(mask_id: int, request_data: ImplantTriggerRequest) -> Any:
    """Generate a recommended implant that fills the defect in a bone mask.

    Runs the selected implant plugin, reconstructs the proposed region into a
    watertight mesh, and exports it (STL / OBJ / PLY).
    """
    try:
        try:
            implant_service.manager.get_plugin(request_data.model_name)
        except KeyError as ke:
            raise CustomException(http_code=status.HTTP_404_NOT_FOUND, message=str(ke))

        implant_record = implant_service.generate_implant_record(
            mask_id=mask_id,
            model_name=request_data.model_name,
            smooth_iterations=request_data.smooth_iterations,
            decimate_ratio=request_data.decimate_ratio,
            export_format=request_data.export_format,
        )
        return DataResponse(http_code=status.HTTP_201_CREATED, data=implant_record)
    except CustomException as ce:
        raise ce
    except FileNotFoundError as fnfe:
        raise CustomException(http_code=status.HTTP_404_NOT_FOUND, message=str(fnfe))
    except ValueError as ve:
        raise CustomException(http_code=status.HTTP_400_BAD_REQUEST, message=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException(exception=e)


@router.get(
    "/all",
    response_model=DataResponse[List[ImplantResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all(sort_params: SortParams = Depends()) -> Any:
    try:
        data, metadata = implant_service.get_all(sort_params)
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "",
    response_model=DataResponse[List[ImplantResponse]],
    status_code=status.HTTP_200_OK,
)
def get_by_filter(
    sort_params: SortParams = Depends(),
    pagination_params: PaginationParams = Depends(),
) -> Any:
    try:
        data, metadata = implant_service.get_by_filter(
            pagination_params=pagination_params, sort_params=sort_params
        )
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{implant_id}",
    response_model=DataResponse[ImplantResponse],
    status_code=status.HTTP_200_OK,
)
def get_by_id(implant_id: int) -> Any:
    try:
        implant = implant_service.get_by_id(id=implant_id)
        return DataResponse(http_code=status.HTTP_200_OK, data=implant)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{implant_id}/download",
    status_code=status.HTTP_200_OK,
)
def download_implant(implant_id: int) -> FileResponse:
    """Downloads the recommended implant mesh (STL / OBJ / PLY)."""
    try:
        implant = implant_service.get_by_id(id=implant_id)
        full_path = os.path.join(settings.BASE_DIR, implant.file_path)

        if not os.path.exists(full_path):
            raise CustomException(
                http_code=status.HTTP_404_NOT_FOUND,
                message="Implant mesh file not found on disk.",
            )

        ext = os.path.splitext(full_path)[1].lstrip(".").lower() or "stl"
        return FileResponse(
            path=full_path,
            filename=f"implant_{implant.id}.{ext}",
            media_type=_MESH_MEDIA_TYPES.get(ext, "application/octet-stream"),
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.delete(
    "/{implant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_implant(implant_id: int) -> None:
    """Deletes an implant record and removes its mesh file from disk."""
    try:
        implant = implant_service.get_by_id(id=implant_id)
        full_path = os.path.join(settings.BASE_DIR, implant.file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass
        implant_service.delete_by_id(id=implant_id)
    except Exception as e:
        raise CustomException(exception=e)
