from typing import Tuple
import numpy as np

from app.services.ai.base import IAIPlugin, ModelInfo


class MockSegmentationPlugin(IAIPlugin):
    def get_info(self) -> ModelInfo:
        return ModelInfo(
            name="mock_bone_seg",
            version="1.0.0",
            task_type="segmentation",
            labels={0: "background", 1: "bone"}
        )

    def initialize(self) -> None:
        # Mock load weights
        pass

    def predict(self, volume: np.ndarray, spacing: Tuple[float, float, float]) -> np.ndarray:
        """
        Generates a clinically plausible mock bone mask by thresholding
        cortex density voxels from the CT volume.
        """
        if volume is None or volume.size == 0:
            raise ValueError("Input volume is empty or invalid.")

        # Detect if volume is normalized to [0.0, 1.0] or contains raw Hounsfield Units (HU)
        if volume.max() <= 1.01:
            # Assuming normalized volume, threshold at 0.45 (approx 250 HU in bone window)
            mask = (volume > 0.45).astype(np.uint8)
        else:
            # Raw HU values, threshold for cortical bone (> 250 HU)
            mask = (volume > 250.0).astype(np.uint8)

        # Zero out the outer border layer of voxels to ensure a closed surface
        # (and thus a watertight mesh) when reconstructed using marching cubes
        mask[0, :, :] = 0
        mask[-1, :, :] = 0
        mask[:, 0, :] = 0
        mask[:, -1, :] = 0
        mask[:, :, 0] = 0
        mask[:, :, -1] = 0

        return mask
