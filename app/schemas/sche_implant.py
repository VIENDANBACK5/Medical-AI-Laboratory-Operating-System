from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.schemas.sche_base import BaseModelResponse
from app.schemas.sche_mesh import MeshFormat


class ImplantModelInfoResponse(BaseModel):
    name: str
    version: str
    method: str
    description: str


class ImplantTriggerRequest(BaseModel):
    model_name: str = Field(default="mirror_implant")
    smooth_iterations: int = Field(default=10, ge=0, le=100)
    decimate_ratio: float = Field(default=0.5, gt=0.0, le=1.0)
    export_format: MeshFormat = Field(default="stl")


class ImplantResponse(BaseModelResponse):
    mask_id: int
    plugin_name: str
    plugin_version: str
    method: str
    vertex_count: int
    triangle_count: int
    volume_mm3: Optional[float] = None
    is_watertight: bool
    file_path: str
    meta_info: Optional[Dict[str, Any]] = None
