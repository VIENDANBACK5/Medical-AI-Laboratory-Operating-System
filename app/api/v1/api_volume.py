import os
from typing import Any, List
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.sche_base import PaginationParams, SortParams
from app.schemas.sche_response import DataResponse
from app.schemas.sche_volume import VolumeResponse
from app.services.srv_volume import VolumeService
from app.utils.exception_handler import CustomException, ExceptionType
from app.utils.login_manager import login_required

router = APIRouter(prefix="/volumes", dependencies=[Depends(login_required)])

volume_service = VolumeService()


@router.post(
    "/upload",
    response_model=DataResponse[VolumeResponse],
    status_code=status.HTTP_201_CREATED,
)
def upload_volume(
    file: UploadFile = File(...),
    target_spacing: float = 1.0,
) -> Any:
    """
    Upload a DICOM series as a ZIP archive, or a single NIfTI (.nii or .nii.gz) file.
    Resamples the volume to the target_spacing (default: 1.0mm isotropic RAS space).
    """
    filename = file.filename or ""
    try:
        if filename.lower().endswith(".zip"):
            db_volume = volume_service.process_dicom_zip(file, target_spacing)
        elif filename.lower().endswith((".nii", ".nii.gz")):
            db_volume = volume_service.process_nifti_file(file, target_spacing)
        else:
            raise CustomException(
                exception=ExceptionType.VALIDATION_ERROR,
                message="Unsupported file format. Please upload a ZIP archive of DICOM slices, or a NIfTI file."
            )
        return DataResponse(http_code=status.HTTP_201_CREATED, data=db_volume)
    except CustomException as ce:
        raise ce
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException(http_code=500, message=str(e))


@router.get(
    "/all",
    response_model=DataResponse[List[VolumeResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all(sort_params: SortParams = Depends()) -> Any:
    try:
        data, metadata = volume_service.get_all(sort_params)
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "",
    response_model=DataResponse[List[VolumeResponse]],
    status_code=status.HTTP_200_OK,
)
def get_by_filter(
    sort_params: SortParams = Depends(),
    pagination_params: PaginationParams = Depends(),
) -> Any:
    try:
        data, metadata = volume_service.get_by_filter(
            pagination_params=pagination_params, sort_params=sort_params
        )
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{volume_id}",
    response_model=DataResponse[VolumeResponse],
    status_code=status.HTTP_200_OK,
)
def get_by_id(volume_id: int) -> Any:
    try:
        volume = volume_service.get_by_id(id=volume_id)
        return DataResponse(http_code=status.HTTP_200_OK, data=volume)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/{volume_id}/download",
    status_code=status.HTTP_200_OK,
)
def download_processed_volume(volume_id: int) -> FileResponse:
    """Downloads the processed isotropic numpy volume (.npy) file."""
    try:
        volume = volume_service.get_by_id(id=volume_id)
        full_path = os.path.join(settings.BASE_DIR, volume.file_path)
        
        if not os.path.exists(full_path):
            raise CustomException(
                exception=ExceptionType.NOT_FOUND,
                message="Processed volume file not found on disk."
            )
            
        return FileResponse(
            path=full_path,
            filename=f"volume_{volume.id}.npy",
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.delete(
    "/{volume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_by_id(volume_id: int) -> None:
    try:
        # Get volume details to clean up files
        volume = volume_service.get_by_id(id=volume_id)
        
        # Clean up files on disk
        for relative_path in [volume.file_path, volume.original_file_path]:
            if relative_path:
                full_path = os.path.join(settings.BASE_DIR, relative_path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass # Ignore disk deletion errors during records cleanup
                        
        volume_service.delete_by_id(id=volume_id)
    except Exception as e:
        raise CustomException(exception=e)
