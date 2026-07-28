from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np
from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    version: str
    task_type: str          # "segmentation", "detection", "registration", "implant"
    labels: Dict[int, str]  # e.g., {0: "background", 1: "femur", 2: "tibia"}


class IAIPlugin(ABC):
    @abstractmethod
    def get_info(self) -> ModelInfo:
        """Returns capabilities, metadata, and labels of this model."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Loads model weights, compiles model graph, and allocates VRAM/RAM."""
        pass

    @abstractmethod
    def predict(self, volume: np.ndarray, spacing: Tuple[float, float, float]) -> np.ndarray:
        """
        Runs inference on the resampled isotropic voxel volume array.
        
        Args:
            volume: 3D numpy array in RAS space [depth, height, width] (z, y, x)
            spacing: Voxel size in mm in array-axis order [dz, dy, dx], matching
                the volume axes above.

        Returns:
            3D numpy array [depth, height, width] containing predicted labels/segmentations.
        """
        pass
