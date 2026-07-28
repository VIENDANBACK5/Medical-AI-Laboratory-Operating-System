from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.schemas.sche_base import BaseModelResponse


class ModelInfoResponse(BaseModel):
    name: str
    version: str
    task_type: str
    labels: Dict[int, str]


class InferenceTriggerRequest(BaseModel):
    model_name: str


class InferenceTriggerResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    volume_id: int
    model_name: str
    error: Optional[str] = None
    result_id: Optional[int] = None


class MaskResponse(BaseModelResponse):
    volume_id: int
    model_name: str
    model_version: str
    file_path: str
    inference_time_sec: Optional[float] = None
    vram_consumed_mb: Optional[float] = None
    meta_info: Optional[Dict[str, Any]] = None
