from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class MeshRecord(BareBaseModel):
    __tablename__ = "meshes"

    mask_id = Column(Integer, ForeignKey("masks.id", ondelete="CASCADE"), nullable=False)
    
    # Computational geometry properties
    vertex_count = Column(Integer, nullable=False)
    triangle_count = Column(Integer, nullable=False)
    volume_mm3 = Column(Float, nullable=True)
    is_watertight = Column(Boolean, default=False)
    
    # Path to the generated mesh file on disk (relative, e.g. storage/meshes/{uuid}.stl)
    file_path = Column(String, nullable=False)
    
    # Parameters used for generation (smoothing iterations, decimation ratio)
    meta_info = Column(JSON, nullable=True)

    # Relationships
    mask = relationship("Mask", back_populates="mesh")
