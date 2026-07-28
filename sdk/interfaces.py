from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import numpy as np


class IDataset(ABC):
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the dataset version tag."""
        pass

    @abstractmethod
    def load_samples(self) -> List[Dict[str, Any]]:
        """Loads CT scans and their respective mask labels."""
        pass


class IModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the model model registration name."""
        pass

    @abstractmethod
    def train_epoch(self, dataloader: Any, lr: float) -> float:
        """Runs a training iteration and returns loss value."""
        pass

    @abstractmethod
    def predict(self, volume: np.ndarray) -> np.ndarray:
        """Runs validation inference on a volume."""
        pass


class ITracker(ABC):
    @abstractmethod
    def log_params(self, params: Dict[str, Any]) -> None:
        """Logs hyper-parameters of the experiment."""
        pass

    @abstractmethod
    def log_metrics(self, epoch: int, metrics: Dict[str, float]) -> None:
        """Logs metrics values for a given training epoch."""
        pass


class IVisualizer(ABC):
    @abstractmethod
    def plot_segmentation_slices(
        self, volume: np.ndarray, mask: np.ndarray, prediction: np.ndarray
    ) -> Any:
        """Generates axial/coronal/sagittal overlap segmentation plots."""
        pass


class IReportGenerator(ABC):
    @abstractmethod
    def export_summary(
        self,
        experiment_name: str,
        metrics: Dict[str, float],
        output_path: str
    ) -> None:
        """Generates a research paper-ready summary report (PDF/Markdown)."""
        pass
