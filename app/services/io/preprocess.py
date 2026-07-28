from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np
import SimpleITK as sitk

from app.schemas.sche_volume import VolumeMetadataBase


class IVolumePreprocessor(ABC):
    @abstractmethod
    def resample_isotropic(
        self, array: np.ndarray, meta: VolumeMetadataBase, target_spacing: float = 1.0
    ) -> Tuple[np.ndarray, VolumeMetadataBase]:
        """Resamples the volume to target isotropic spacing (in mm)."""
        pass

    @abstractmethod
    def apply_window(self, array: np.ndarray, center: float, width: float) -> np.ndarray:
        """Applies a Hounsfield Unit (HU) window preset and scales intensities to [0, 1]."""
        pass


class VolumePreprocessor(IVolumePreprocessor):
    def resample_isotropic(
        self, array: np.ndarray, meta: VolumeMetadataBase, target_spacing: float = 1.0
    ) -> Tuple[np.ndarray, VolumeMetadataBase]:
        # Convert numpy array [z, y, x] back to SimpleITK Image
        image = sitk.GetImageFromArray(array)

        # Convert RAS metadata back to SimpleITK's native LPS space
        origin_lps = [-meta.origin[0], -meta.origin[1], meta.origin[2]]
        direction_lps = [
            -meta.direction[0], -meta.direction[1], -meta.direction[2],
            -meta.direction[3], -meta.direction[4], -meta.direction[5],
            meta.direction[6], meta.direction[7], meta.direction[8],
        ]

        image.SetSpacing(meta.spacing)
        image.SetOrigin(origin_lps)
        image.SetDirection(direction_lps)

        # Extract current image attributes
        original_spacing = image.GetSpacing()
        original_size = image.GetSize()

        # Compute new spatial attributes
        new_spacing = [target_spacing, target_spacing, target_spacing]
        new_size = [
            int(round(original_size[0] * original_spacing[0] / target_spacing)),
            int(round(original_size[1] * original_spacing[1] / target_spacing)),
            int(round(original_size[2] * original_spacing[2] / target_spacing)),
        ]

        # Configure SimpleITK Resampler
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetOutputSpacing(new_spacing)
        resampler.SetSize(new_size)
        resampler.SetOutputDirection(image.GetDirection())
        resampler.SetOutputOrigin(image.GetOrigin())
        resampler.SetTransform(sitk.Transform())
        
        # Set default background value to the minimum intensity to avoid border artifacts
        resampler.SetDefaultPixelValue(float(array.min()))

        resampled_image = resampler.Execute(image)
        resampled_array = sitk.GetArrayFromImage(resampled_image)

        # Convert resampled LPS coordinates back to RAS space for storage consistency
        new_origin_ras = [
            -resampled_image.GetOrigin()[0],
            -resampled_image.GetOrigin()[1],
            resampled_image.GetOrigin()[2],
        ]
        new_direction_ras = [
            -resampled_image.GetDirection()[0], -resampled_image.GetDirection()[1], -resampled_image.GetDirection()[2],
            -resampled_image.GetDirection()[3], -resampled_image.GetDirection()[4], -resampled_image.GetDirection()[5],
            resampled_image.GetDirection()[6], resampled_image.GetDirection()[7], resampled_image.GetDirection()[8],
        ]

        new_meta = VolumeMetadataBase(
            patient_id=meta.patient_id,
            study_instance_uid=meta.study_instance_uid,
            series_instance_uid=meta.series_instance_uid,
            spacing=new_spacing,
            dimensions=list(resampled_image.GetSize()),
            origin=new_origin_ras,
            direction=new_direction_ras,
            meta_info=meta.meta_info,
        )

        return resampled_array, new_meta

    def apply_window(self, array: np.ndarray, center: float, width: float) -> np.ndarray:
        min_val = center - (width / 2.0)
        max_val = center + (width / 2.0)

        # Clip values to the window limits
        windowed = np.clip(array, min_val, max_val)

        # Scale intensity windowed values to range [0.0, 1.0]
        windowed = (windowed - min_val) / width
        return windowed
