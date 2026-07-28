"""Real bone segmentation plugin backed by TotalSegmentator.

This plugin wraps the pretrained `TotalSegmentator <https://github.com/wasserth/TotalSegmentator>`_
nnU-Net models and exposes them through the platform's :class:`IAIPlugin`
interface, so it is auto-discovered by :class:`AIEngineManager` exactly like the
mock plugin.

Design notes
------------
* Heavy imports (``totalsegmentator``, ``torch``) are performed lazily inside
  :meth:`initialize` / :meth:`predict`. ``__init__`` and :meth:`get_info` stay
  import-free so plugin discovery works even when the AI extras
  (``requirements-ai.txt``) are not installed -- the plugin simply fails at
  ``initialize()`` time with a clear message instead of crashing discovery.
* All array <-> file conversion goes through SimpleITK to stay consistent with
  the rest of the IO layer (numpy arrays are in z, y, x order; spacing is in
  array-axis order [dz, dy, dx] as documented on ``IAIPlugin.predict``).
* The output is a binary bone mask ({0: background, 1: bone}) built as the union
  of TotalSegmentator's skeletal ROIs. The downstream marching-cubes mesh
  pipeline binarizes the mask anyway, so a clean union keeps reconstruction
  simple and watertight.
"""

import os
import tempfile
from typing import List, Tuple

import numpy as np

from app.services.ai.base import IAIPlugin, ModelInfo


# Skeletal structures exposed by the TotalSegmentator "total" task that we treat
# as "bone" for reconstruction. Restricting inference to this subset via
# ``roi_subset`` is dramatically faster than segmenting all ~117 classes.
BONE_ROI_SUBSET: List[str] = [
    "skull",
    "vertebrae_C1", "vertebrae_C2", "vertebrae_C3", "vertebrae_C4",
    "vertebrae_C5", "vertebrae_C6", "vertebrae_C7",
    "vertebrae_T1", "vertebrae_T2", "vertebrae_T3", "vertebrae_T4",
    "vertebrae_T5", "vertebrae_T6", "vertebrae_T7", "vertebrae_T8",
    "vertebrae_T9", "vertebrae_T10", "vertebrae_T11", "vertebrae_T12",
    "vertebrae_L1", "vertebrae_L2", "vertebrae_L3", "vertebrae_L4", "vertebrae_L5",
    "sacrum",
    "hip_left", "hip_right",
    "femur_left", "femur_right",
    "humerus_left", "humerus_right",
    "scapula_left", "scapula_right",
    "clavicula_left", "clavicula_right",
    "rib_left_1", "rib_left_2", "rib_left_3", "rib_left_4", "rib_left_5", "rib_left_6",
    "rib_left_7", "rib_left_8", "rib_left_9", "rib_left_10", "rib_left_11", "rib_left_12",
    "rib_right_1", "rib_right_2", "rib_right_3", "rib_right_4", "rib_right_5", "rib_right_6",
    "rib_right_7", "rib_right_8", "rib_right_9", "rib_right_10", "rib_right_11", "rib_right_12",
    "sternum",
]


class TotalSegmentatorPlugin(IAIPlugin):
    def __init__(self) -> None:
        self._ready = False
        self._device = "cpu"
        # ``fast`` uses the 3mm low-res model: much quicker and CPU-friendly,
        # at the cost of some boundary detail. Toggle via env for GPU setups.
        self._fast = os.environ.get("TOTALSEG_FAST", "true").lower() == "true"

    def get_info(self) -> ModelInfo:
        return ModelInfo(
            name="totalsegmentator_bone",
            version="2.4.0",
            task_type="segmentation",
            labels={0: "background", 1: "bone"},
        )

    def initialize(self) -> None:
        """Verify the TotalSegmentator stack is importable and pick a device.

        Weights themselves are downloaded/cached lazily by TotalSegmentator on
        first ``predict`` call, so there is nothing to eagerly load here beyond
        confirming the dependency is present.
        """
        if self._ready:
            return
        try:
            import torch  # noqa: F401
            from totalsegmentator.python_api import totalsegmentator  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "TotalSegmentator is not installed. Install the AI extras with "
                "`pip install -r requirements-ai.txt` to enable this plugin."
            ) from exc

        try:
            import torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            self._device = "cpu"

        self._ready = True

    def predict(
        self, volume: np.ndarray, spacing: Tuple[float, float, float]
    ) -> np.ndarray:
        if not self._ready:
            self.initialize()

        if volume is None or volume.size == 0:
            raise ValueError("Input volume is empty or invalid.")

        import SimpleITK as sitk
        from totalsegmentator.python_api import totalsegmentator

        # 1. Wrap the numpy volume (z, y, x) into a SimpleITK image. sitk expects
        #    spacing in x, y, z order, so reverse the array-order [dz, dy, dx].
        image = sitk.GetImageFromArray(np.ascontiguousarray(volume))
        image.SetSpacing(tuple(float(s) for s in reversed(spacing)))

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, "input.nii.gz")
            output_path = os.path.join(tmp_dir, "segmentation.nii.gz")
            sitk.WriteImage(image, input_path)

            # 2. Run TotalSegmentator. ml=True writes a single multi-label volume
            #    in the input geometry; roi_subset limits work to bone ROIs.
            totalsegmentator(
                input=input_path,
                output=output_path,
                ml=True,
                fast=self._fast,
                roi_subset=BONE_ROI_SUBSET,
                device=self._device,
                quiet=True,
            )

            # 3. Read the multi-label result back in array order (z, y, x).
            seg_image = sitk.ReadImage(output_path)
            seg_array = sitk.GetArrayFromImage(seg_image)

        # 4. Collapse every non-zero skeletal label into a single binary bone
        #    mask matching the {0: background, 1: bone} contract in get_info().
        bone_mask = (seg_array > 0).astype(np.uint8)

        if bone_mask.shape != volume.shape:
            # Defensive: TotalSegmentator should preserve geometry, but guard
            # against silent axis/shape drift feeding the mesh pipeline.
            raise RuntimeError(
                f"Segmentation shape {bone_mask.shape} does not match input "
                f"volume shape {volume.shape}."
            )

        return bone_mask
