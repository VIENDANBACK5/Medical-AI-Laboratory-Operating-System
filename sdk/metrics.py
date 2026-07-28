from typing import Dict
import numpy as np


def calculate_dice(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes the Dice Similarity Coefficient between two 3D arrays.
    
    Formula: Dice = (2 * |A intersect B|) / (|A| + |B|)
    """
    # Flatten the volumetric arrays
    y_true_f = y_true.astype(bool)
    y_pred_f = y_pred.astype(bool)
    
    intersection = np.sum(y_true_f & y_pred_f)
    total_elements = np.sum(y_true_f) + np.sum(y_pred_f)
    
    if total_elements == 0:
        return 1.0
        
    return float(2.0 * intersection / total_elements)


def calculate_hausdorff_distance(y_true: np.ndarray, y_pred: np.ndarray, spacing: tuple = (1.0, 1.0, 1.0)) -> float:
    """
    Computes a mock Hausdorff Distance (HD95) representing surface edge alignment.
    In production, this uses scipy.spatial.distance.directed_hausdorff or monai.metrics.
    """
    # Mocking HD calculation for quick SDK testing
    if np.array_equal(y_true, y_pred):
        return 0.0
    # Simulate based on differences
    diff_ratio = np.sum(y_true != y_pred) / y_true.size
    return float(diff_ratio * 10.0 * spacing[0])


class MetricEvaluator:
    def __init__(self):
        self.scores: Dict[str, float] = {}

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, duration_sec: float) -> Dict[str, float]:
        """Runs the complete metrics calculation suite."""
        self.scores = {
            "dice_score": calculate_dice(y_true, y_pred),
            "hausdorff_distance_mm": calculate_hausdorff_distance(y_true, y_pred),
            "inference_time_sec": duration_sec,
            "fps": float(y_true.shape[0] / duration_sec) if duration_sec > 0 else 0.0,
        }
        return self.scores
