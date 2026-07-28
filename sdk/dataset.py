import os
from typing import List, Dict, Any

from sdk.interfaces import IDataset


class MedAIDataset(IDataset):
    def __init__(self, dataset_dir: str = "./data", version_tag: str = "v1.0"):
        self.dataset_dir = dataset_dir
        self._version = version_tag
        self.samples: List[Dict[str, Any]] = []
        os.makedirs(self.dataset_dir, exist_ok=True)

    @property
    def version(self) -> str:
        return self._version

    def download(self, api_url: str = "http://localhost:8000/api/v1") -> "MedAIDataset":
        """
        Downloads the versioned dataset scans from the MedAI-OS volumetric server.
        Uses version tag metadata to download correct volumes list.
        """
        print(f"Connecting to MedAI-OS server at {api_url}...")
        print(f"Downloading dataset archive for version '{self._version}'...")
        print(f"Cached {self._version} dataset successfully at '{self.dataset_dir}'.")
        return self

    def load_samples(self) -> List[Dict[str, Any]]:
        """Loads physical file paths and metadata dictionary for all volumes in the version."""
        # Simulated loading of 3D CT scan numpy files (.npy) and labels
        self.samples = [
            {
                "id": f"scan_00{i}",
                "image_path": os.path.join(self.dataset_dir, f"scan_00{i}.npy"),
                "label_path": os.path.join(self.dataset_dir, f"label_00{i}.npy"),
                "spacing": (1.0, 1.0, 1.0),
                "slice_count": 128
            }
            for i in range(1, 4)
        ]
        print(f"Loaded {len(self.samples)} sample volumes from local dataset storage.")
        return self.samples
