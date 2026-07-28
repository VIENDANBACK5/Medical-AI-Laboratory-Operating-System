"""Baseline implant generator using contralateral mirroring.

This is the classic clinical baseline for reconstructing (near-)symmetric bone
defects such as cranial or pelvic gaps: the healthy side of the body is mirrored
across the mid-sagittal plane, and the part of the mirrored anatomy that is
missing on the defect side is proposed as the implant.

It runs on the segmentation voxel mask with pure numpy/scipy (no weights, fully
deterministic), so it always works and gives a sensible starting geometry that an
engineer -- or a future generative model swapped in behind the same
:class:`IImplantPlugin` interface -- can refine.
"""

import os
from typing import Tuple

import numpy as np

from app.services.implant.base import IImplantPlugin, ImplantInfo


class MirrorImplantPlugin(IImplantPlugin):
    def __init__(self) -> None:
        # Mid-sagittal reflection is along the x axis, which is the last axis of
        # the [z, y, x] mask. Overridable in case of non-standard orientation.
        self._mirror_axis = int(os.environ.get("IMPLANT_MIRROR_AXIS", "2"))

    def get_info(self) -> ImplantInfo:
        return ImplantInfo(
            name="mirror_implant",
            version="1.0.0",
            method="mirroring",
            description=(
                "Contralateral mid-sagittal mirroring baseline: fills a defect "
                "with the healthy side reflected across the body midline."
            ),
        )

    def initialize(self) -> None:
        # No weights to load for the geometric baseline.
        pass

    def generate(
        self, bone_mask: np.ndarray, spacing: Tuple[float, float, float]
    ) -> np.ndarray:
        from scipy import ndimage

        if bone_mask is None or bone_mask.size == 0:
            raise ValueError("Input bone mask is empty or invalid.")

        binary = (bone_mask > 0).astype(np.uint8)
        if binary.max() == 0:
            raise ValueError("Bone mask contains no positive voxels.")

        # 1. Reflect the anatomy across the mid-sagittal plane.
        mirrored = np.flip(binary, axis=self._mirror_axis)

        # 2. Candidate implant = present on the mirrored (healthy) side but
        #    absent on the patient's actual anatomy -> the missing region.
        candidate = ((mirrored == 1) & (binary == 0)).astype(np.uint8)

        # 3. Morphological closing bridges small gaps and yields a solid body.
        candidate = ndimage.binary_closing(candidate, iterations=2).astype(np.uint8)

        # 4. Remove noise from mirror misalignment: keep only the largest
        #    connected component (the actual defect), drop tiny speckles.
        labeled, num = ndimage.label(candidate)
        if num == 0:
            raise ValueError(
                "No defect region detected. The bone mask appears symmetric; "
                "mirroring found nothing to reconstruct."
            )
        sizes = ndimage.sum(np.ones_like(labeled), labeled, index=range(1, num + 1))
        largest_label = int(np.argmax(sizes)) + 1
        implant = (labeled == largest_label).astype(np.uint8)

        # 5. Zero the outer border so marching cubes yields a closed, watertight
        #    surface for the implant mesh.
        implant[0, :, :] = 0
        implant[-1, :, :] = 0
        implant[:, 0, :] = 0
        implant[:, -1, :] = 0
        implant[:, :, 0] = 0
        implant[:, :, -1] = 0

        if implant.max() == 0:
            raise ValueError("Generated implant region is empty after cleanup.")

        return implant
