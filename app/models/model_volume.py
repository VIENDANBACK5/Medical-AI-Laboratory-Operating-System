import json
from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY

from app.models.model_base import BareBaseModel


class CompatibleArray(TypeDecorator):
    """
    A database-agnostic array type.
    Uses PostgreSQL's native ARRAY type when running on Postgres,
    and falls back to JSON representation on SQLite (for testing and local dev).
    Handles serialization/deserialization for non-Postgres engines.
    """
    impl = JSON

    def __init__(self, item_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(self.item_type))
        else:
            return dialect.type_descriptor(JSON)

    def process_bind_param(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if dialect.name != "postgresql" and value is not None:
            if isinstance(value, str):
                return json.loads(value)
            return value
        return value


class Volume(BareBaseModel):
    __tablename__ = "volumes"

    patient_id = Column(String, index=True, nullable=True)
    study_instance_uid = Column(String, index=True, nullable=True)
    series_instance_uid = Column(String, unique=True, index=True, nullable=True)
    
    # Spatial mapping parameters (RAS coordinate space representation)
    spacing = Column(CompatibleArray(Float), nullable=False)       # Voxel size in mm: [dx, dy, dz]
    dimensions = Column(CompatibleArray(Integer), nullable=False)  # Voxel dimensions: [x, y, z]
    origin = Column(CompatibleArray(Float), nullable=False)      # Voxel matrix origin: [ox, oy, oz]
    direction = Column(CompatibleArray(Float), nullable=False)   # Coordinate system direction cosines (flat 3x3)

    # Voxel data storage details
    file_path = Column(String, nullable=False)           # Path to the resampled isotropic RAS numpy file (.npy)
    original_file_path = Column(String, nullable=True)   # Path to original upload (ZIP archive or .nii.gz)
    
    # Dynamic/Extensible research metadata dump (e.g. KVp, SliceThickness, EchoTime)
    meta_info = Column(JSON, nullable=True)

    # Relationships
    masks = relationship("Mask", back_populates="volume", cascade="all, delete-orphan")
