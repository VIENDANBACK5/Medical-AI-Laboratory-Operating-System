from typing import Any
import numpy as np

from sdk.interfaces import IModel


class MedAIModel(IModel):
    def __init__(self, model_name: str, version: str = "1.0.0"):
        self._name = model_name
        self.version = version
        self.weights_loaded = False

    @property
    def name(self) -> str:
        return self._name

    def load_weights(self, weights_path: str) -> "MedAIModel":
        """Loads weight files into the model graph."""
        print(f"Loading weights for '{self._name}' from {weights_path}...")
        self.weights_loaded = True
        return self

    def train_epoch(self, dataloader: Any, lr: float = 1e-4) -> float:
        """Executes a single backpropagation epoch and returns dummy loss."""
        if not self.weights_loaded:
            print("Warning: Training model with uninitialized weights.")
        
        # Mocking optimization backward loop
        loss = 0.456 / (lr * 1000)
        return float(loss)

    def predict(self, volume: np.ndarray) -> np.ndarray:
        """Runs the validation forward pass."""
        if volume is None:
            raise ValueError("Inference failed: Volume is empty.")
            
        print(f"Running inference with model '{self._name}' version '{self.version}'...")
        # Generates a mock segmentation mask array
        prediction = (volume > 0.5).astype(np.uint8)
        return prediction


# Central Model Registry for hot-swapping
MODEL_REGISTRY = {
    "MedSAM": lambda: MedAIModel("MedSAM", "2.0.0"),
    "nnUNet": lambda: MedAIModel("nnUNet", "1.2.0"),
    "TotalSegmentator": lambda: MedAIModel("TotalSegmentator", "3.0.0"),
}
