from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal
from app.schemas.sche_base import BaseModelResponse


MeshFormat = Literal["stl", "obj", "ply"]


class MeshTriggerRequest(BaseModel):
    smooth_iterations: int = Field(default=10, ge=0, le=100)
    decimate_ratio: float = Field(default=0.5, gt=0.0, le=1.0)
    export_format: MeshFormat = Field(default="stl")


class MeshResponse(BaseModelResponse):
    mask_id: int
    vertex_count: int
    triangle_count: int
    volume_mm3: Optional[float] = None
    is_watertight: bool
    file_path: str
    meta_info: Optional[Dict[str, Any]] = None


class PrintabilityResponse(BaseModel):
    mesh_id: int
    is_watertight: bool
    winding_consistent: bool
    is_empty: bool
    volume_mm3: float
    area_mm2: float
    euler_number: int
    bounding_box_mm: list[float]
    ready_to_print: bool
    issues: list[str]
