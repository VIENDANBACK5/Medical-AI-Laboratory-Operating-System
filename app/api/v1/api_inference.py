import os
from typing import Any, List
from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import FileResponse

from app.utils.login_manager import login_required
from app.core.config import settings
from app.schemas.sche_response import DataResponse
from app.schemas.sche_base import SortParams, PaginationParams
from app.schemas.sche_inference import (
    ModelInfoResponse,
    InferenceTriggerRequest,
    InferenceTriggerResponse,
    TaskStatusResponse,
    MaskResponse,
)
from app.services.ai.inference_service import AIInferenceService
from app.utils.exception_handler import CustomException, ExceptionType

router = APIRouter(prefix="/inference", dependencies=[Depends(login_required)])

inference_service = AIInferenceService()


@router.get(
    "/models",
    response_model=DataResponse[List[ModelInfoResponse]],
    status_code=status.HTTP_200_OK,
)
def list_models() -> Any:
    """Lists all dynamically discovered AI plugins in the registry."""
    try:
        models = inference_service.manager.list_models()
        return DataResponse(http_code=status.HTTP_200_OK, data=models)
    except Exception as e:
        raise CustomException(exception=e)


@router.post(
    "/segment/{volume_id}",
    response_model=DataResponse[InferenceTriggerResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_segmentation(
    volume_id: int,
    request_data: InferenceTriggerRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Triggers an asynchronous volumetric segmentation on the specified volume.
    Returns a task ID for tracking progress.
    """
    try:
        # Check if the requested model exists
        try:
            inference_service.manager.get_plugin(request_data.model_name)
        except KeyError as ke:
            raise CustomException(
                http_code=status.HTTP_404_NOT_FOUND,
                message=str(ke)
            )

        # Queue the job and generate task ID
        task_id = inference_service.queue_inference(volume_id, request_data.model_name)
        
        # Add the computational task to background thread execution queue
        background_tasks.add_task(
            inference_service.run_inference_task,
            task_id,
            volume_id,
            request_data.model_name,
        )

        return DataResponse(
            http_code=status.HTTP_202_ACCEPTED,
            data=InferenceTriggerResponse(
                task_id=task_id,
                status="PENDING",
                message="AI inference task successfully queued in the background."
            )
        )
    except CustomException as ce:
        raise ce
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/tasks/{task_id}",
    response_model=DataResponse[TaskStatusResponse],
    status_code=status.HTTP_200_OK,
)
def get_task_status(task_id: str) -> Any:
    """Checks the status of an active background segmentation task."""
    task_info = inference_service.get_task_status(task_id)
    if not task_info:
        raise CustomException(
            http_code=status.HTTP_404_NOT_FOUND,
            message=f"Inference task ticket '{task_id}' not found."
        )
        
    return DataResponse(
        http_code=status.HTTP_200_OK,
        data=TaskStatusResponse(
            task_id=task_id,
            status=task_info["status"],
            progress=task_info["progress"],
            volume_id=task_info["volume_id"],
            model_name=task_info["model_name"],
            error=task_info["error"],
            result_id=task_info["result_id"],
        )
    )


@router.get(
    "/masks/all",
    response_model=DataResponse[List[MaskResponse]],
    status_code=status.HTTP_200_OK,
)
def get_all_masks(sort_params: SortParams = Depends()) -> Any:
    """Lists every completed segmentation mask (across all volumes)."""
    try:
        data, metadata = inference_service.get_all(sort_params)
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/masks",
    response_model=DataResponse[List[MaskResponse]],
    status_code=status.HTTP_200_OK,
)
def get_masks_by_filter(
    sort_params: SortParams = Depends(),
    pagination_params: PaginationParams = Depends(),
) -> Any:
    """Lists segmentation masks, paginated and sorted."""
    try:
        data, metadata = inference_service.get_by_filter(
            pagination_params=pagination_params, sort_params=sort_params
        )
        return DataResponse(http_code=status.HTTP_200_OK, data=data, metadata=metadata)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/masks/{mask_id}",
    response_model=DataResponse[MaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_mask_detail(mask_id: int) -> Any:
    """Retrieves spatial metadata and metrics for a completed segmentation mask."""
    try:
        mask = inference_service.get_by_id(id=mask_id)
        return DataResponse(http_code=status.HTTP_200_OK, data=mask)
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/benchmark/compare",
    response_model=DataResponse[Any],
    status_code=status.HTTP_200_OK,
)
def benchmark_compare(mask_ids: str = "") -> Any:
    """
    Compare inference metrics across multiple segmentation masks.
    Pass mask_ids as comma-separated integers: ?mask_ids=1,2,3
    Returns a comparison table of model_name, inference_time_sec, vram_consumed_mb.
    """
    try:
        if not mask_ids.strip():
            # Return all masks as benchmark overview
            data, _ = inference_service.get_all(sort_params=None)
        else:
            ids = [int(x.strip()) for x in mask_ids.split(",") if x.strip().isdigit()]
            data = [inference_service.get_by_id(id=mid) for mid in ids]

        comparison = []
        for mask in data:
            comparison.append({
                "mask_id":            mask.id,
                "volume_id":          mask.volume_id,
                "model_name":         mask.model_name,
                "model_version":      mask.model_version,
                "inference_time_sec": round(mask.inference_time_sec or 0, 3),
                "vram_consumed_mb":   round(mask.vram_consumed_mb or 0, 1),
                "created_at":         str(mask.created_at) if hasattr(mask, "created_at") else None,
            })

        # Sort by inference_time_sec ascending (fastest first = leaderboard)
        comparison.sort(key=lambda x: x["inference_time_sec"])

        return DataResponse(
            http_code=status.HTTP_200_OK,
            data={"results": comparison, "count": len(comparison)},
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/benchmark/leaderboard",
    response_model=DataResponse[Any],
    status_code=status.HTTP_200_OK,
)
def benchmark_leaderboard() -> Any:
    """
    Returns a leaderboard of all registered AI models ranked by average inference speed.
    Groups masks by model_name and computes: count, avg_time, avg_vram.
    """
    try:
        data, _ = inference_service.get_all(sort_params=None)

        stats: dict = {}
        for mask in data:
            name = mask.model_name or "unknown"
            if name not in stats:
                stats[name] = {
                    "model_name": name,
                    "run_count":  0,
                    "total_time": 0.0,
                    "total_vram": 0.0,
                }
            stats[name]["run_count"]  += 1
            stats[name]["total_time"] += mask.inference_time_sec or 0
            stats[name]["total_vram"] += mask.vram_consumed_mb   or 0

        leaderboard = []
        for s in stats.values():
            n = s["run_count"]
            leaderboard.append({
                "model_name":       s["model_name"],
                "run_count":        n,
                "avg_inference_sec": round(s["total_time"] / n, 3) if n else 0,
                "avg_vram_mb":      round(s["total_vram"] / n, 1) if n else 0,
            })

        leaderboard.sort(key=lambda x: x["avg_inference_sec"])

        return DataResponse(
            http_code=status.HTTP_200_OK,
            data={"leaderboard": leaderboard},
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.get(
    "/masks/{mask_id}/download",
    status_code=status.HTTP_200_OK,
)
def download_mask(mask_id: int) -> FileResponse:
    """Downloads the completed numpy segmentation mask array (.npy) file."""
    try:
        mask = inference_service.get_by_id(id=mask_id)
        full_path = os.path.join(settings.BASE_DIR, mask.file_path)
        
        if not os.path.exists(full_path):
            raise CustomException(
                http_code=status.HTTP_404_NOT_FOUND,
                message="Segmentation mask file not found on disk."
            )
            
        return FileResponse(
            path=full_path,
            filename=f"mask_{mask.id}.npy",
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise CustomException(exception=e)


@router.delete(
    "/masks/{mask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_mask(mask_id: int) -> None:
    """Deletes a completed mask record and wipes its file off the local disk."""
    try:
        mask = inference_service.get_by_id(id=mask_id)
        full_path = os.path.join(settings.BASE_DIR, mask.file_path)
        
        # Remove array file from disk
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass
                
        inference_service.delete_by_id(id=mask_id)
    except Exception as e:
        raise CustomException(exception=e)
