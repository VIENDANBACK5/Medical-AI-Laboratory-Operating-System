from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.schemas.sche_base import BaseModelResponse


class VolumeMetadataBase(BaseModel):
    patient_id: Optional[str] = None
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    spacing: List[float]       # [dx, dy, dz] in mm
    dimensions: List[int]      # [x, y, z] in voxels
    origin: List[float]        # [ox, oy, oz] in mm
    direction: List[float]     # flat 3x3 direction cosine matrix
    meta_info: Optional[Dict[str, Any]] = None


class VolumeResponse(BaseModelResponse):
    patient_id: Optional[str] = None
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    spacing: List[float]
    dimensions: List[int]
    origin: List[float]
    direction: List[float]
    file_path: str
    original_file_path: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None
