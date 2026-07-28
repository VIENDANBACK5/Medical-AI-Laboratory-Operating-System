from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class ImplantRecord(BareBaseModel):
    __tablename__ = "implants"

    # Source segmentation mask the defect was reconstructed from.
    mask_id = Column(Integer, ForeignKey("masks.id", ondelete="CASCADE"), nullable=False)

    # Generation provenance
    plugin_name = Column(String, index=True, nullable=False)
    plugin_version = Column(String, nullable=False)
    method = Column(String, nullable=False)  # "mirroring", "generative", ...

    # Computational geometry properties of the generated implant mesh
    vertex_count = Column(Integer, nullable=False)
    triangle_count = Column(Integer, nullable=False)
    volume_mm3 = Column(Float, nullable=True)
    is_watertight = Column(Boolean, default=False)

    # Path to the generated implant mesh file on disk (relative)
    file_path = Column(String, nullable=False)

    # Parameters / labels used during generation
    meta_info = Column(JSON, nullable=True)

    # Relationships
    mask = relationship("Mask")
