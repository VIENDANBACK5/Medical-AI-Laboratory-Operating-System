from abc import ABC, abstractmethod
from typing import Dict, Tuple

import numpy as np
from pydantic import BaseModel


class ImplantInfo(BaseModel):
    name: str
    version: str
    method: str            # "mirroring", "shape_completion", "generative", ...
    description: str


class IImplantPlugin(ABC):
    """Interface for AI implant recommendation / generation models.

    An implant plugin takes a segmented bone mask that contains a defect
    (missing region) and proposes the voxel geometry that would fill it -- the
    3D analogue of image inpainting. The platform meshes the returned voxel mask
    with the existing geometry pipeline and exports it as a printable implant.

    Swapping this plugin (mirroring -> diffusion / shape-completion network) is
    the primary research axis of the platform, mirroring the segmentation
    plugin system so new models drop in without touching the pipeline.
    """

    @abstractmethod
    def get_info(self) -> ImplantInfo:
        """Return the plugin's metadata and generation strategy."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Load any weights / resources needed for generation."""
        pass

    @abstractmethod
    def generate(
        self, bone_mask: np.ndarray, spacing: Tuple[float, float, float]
    ) -> np.ndarray:
        """Propose the implant that fills the defect in ``bone_mask``.

        Args:
            bone_mask: 3D binary numpy array [z, y, x] of the (defective) bone.
            spacing: Voxel size in mm in array-axis order [dz, dy, dx].

        Returns:
            3D binary numpy array [z, y, x] of the recommended implant region
            (1 = implant, 0 = background), same shape as ``bone_mask``.
        """
        pass
