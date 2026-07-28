from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Mask(BareBaseModel):
    __tablename__ = "masks"

    volume_id = Column(Integer, ForeignKey("volumes.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String, index=True, nullable=False)
    model_version = Column(String, nullable=False)
    
    # Path to the output segmentation mask array (.npy)
    file_path = Column(String, nullable=False)
    
    # Execution metrics
    inference_time_sec = Column(Float, nullable=True)
    vram_consumed_mb = Column(Float, nullable=True)
    
    # Dynamic research metadata (e.g. thresholds, labels dictionary)
    meta_info = Column(JSON, nullable=True)

    # Relationships
    volume = relationship("Volume", back_populates="masks")
    mesh = relationship("MeshRecord", uselist=False, back_populates="mask", cascade="all, delete-orphan")
