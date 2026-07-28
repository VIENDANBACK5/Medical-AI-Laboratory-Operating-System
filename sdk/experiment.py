import os
import time
from typing import Dict, Any, Optional
import numpy as np

from sdk.dataset import MedAIDataset
from sdk.model import MODEL_REGISTRY, MedAIModel
from sdk.metrics import MetricEvaluator


class Experiment:
    def __init__(self, experiment_name: str, dataset_version: str = "v1.0"):
        self.name = experiment_name
        self.dataset_version = dataset_version
        self.dataset = MedAIDataset(version_tag=dataset_version)
        self.model: Optional[MedAIModel] = None
        
        # Hyperparameters
        self.epochs = 0
        self.learning_rate = 0.0
        
        # State tracking
        self.is_trained = False
        self.is_evaluated = False
        self.metrics: Dict[str, float] = {}

    def train(self, model_name: str, epochs: int = 5, lr: float = 1e-4) -> "Experiment":
        """
        [Fluent API] Trains the selected AI model on the versioned dataset.
        """
        print(f"\n--- Starting Experiment: {self.name} ---")
        
        # Fetch from model registry
        if model_name in MODEL_REGISTRY:
            self.model = MODEL_REGISTRY[model_name]()
        else:
            self.model = MedAIModel(model_name)

        self.epochs = epochs
        self.learning_rate = lr

        # Download and load sample paths
        self.dataset.download().load_samples()
        
        print(f"Initializing {self.model.name}...")
        self.model.load_weights("pretrained_backbone.pth")
        
        # Train epochs
        for epoch in range(1, epochs + 1):
            loss = self.model.train_epoch(None, lr=lr)
            print(f"Epoch {epoch}/{epochs} - Training loss: {loss:.4f}")
            time.sleep(0.1)  # Simulate processing duration
            
        self.is_trained = True
        print(f"Training completed for '{self.model.name}'.")
        return self

    def evaluate(self) -> "Experiment":
        """
        [Fluent API] Evaluates the trained model on validation sets and computes scores.
        """
        if not self.is_trained or not self.model:
            raise RuntimeError("Evaluation failed: Model must be trained before evaluation.")

        print("\n--- Evaluating Model ---")
        # Build synthetic true volume and simulate inference prediction
        np.random.seed(42)
        dummy_volume = np.random.rand(16, 16, 16)
        dummy_ground_truth = (dummy_volume > 0.4).astype(np.uint8)
        
        start_time = time.time()
        dummy_prediction = self.model.predict(dummy_volume)
        eval_duration = time.time() - start_time
        
        # Calculate metric scores
        evaluator = MetricEvaluator()
        self.metrics = evaluator.evaluate(dummy_ground_truth, dummy_prediction, eval_duration)
        
        print("Computed metrics:")
        for k, v in self.metrics.items():
            print(f"  {k}: {v:.4f}")
            
        self.is_evaluated = True
        return self

    def compare(self, baseline_metrics: Dict[str, float]) -> "Experiment":
        """
        [Fluent API] Compares the current experiment results against a baseline.
        """
        if not self.is_evaluated:
            raise RuntimeError("Comparison failed: Experiment must be evaluated first.")

        print(f"\n--- Comparison: {self.name} vs. Baseline ---")
        print(f"{'Metric':<30} | {'Current':<12} | {'Baseline':<12} | {'Delta':<12}")
        print("-" * 75)
        for metric, current_val in self.metrics.items():
            baseline_val = baseline_metrics.get(metric, 0.0)
            delta = current_val - baseline_val
            # Higher is better for Dice/FPS, lower is better for HD/time
            print(f"{metric:<30} | {current_val:<12.4f} | {baseline_val:<12.4f} | {delta:<+12.4f}")
        return self

    def visualize(self) -> "Experiment":
        """
        [Fluent API] Generates axial slice plots of the segmentation predictions.
        """
        if not self.is_evaluated:
            raise RuntimeError("Visualization failed: Experiment must be evaluated first.")

        print("\n--- Generating Visualization Slices ---")
        # Print an ASCII representation of the center slice mask for CLI view
        print("Voxel slice matrix preview (Active region '*'):")
        preview = [
            "".join(["*" if i % 3 == 0 else "." for i in range(16)])
            for _ in range(6)
        ]
        for line in preview:
            print(f"  {line}")
        return self

    def generate_report(self, output_path: str = "experiment_report.md") -> "Experiment":
        """
        [Fluent API] Exports a Markdown report detailing hyperparameters and results.
        """
        if not self.is_evaluated:
            raise RuntimeError("Report generation failed: Experiment must be evaluated first.")

        print(f"\nWriting evaluation report to '{output_path}'...")
        with open(output_path, "w") as f:
            f.write(f"# MedAI-OS Research Report: {self.name}\n\n")
            f.write(f"- **AI Model**: {self.model.name} (v{self.model.version})\n")
            f.write(f"- **Dataset Version**: {self.dataset_version}\n")
            f.write(f"- **Training Epochs**: {self.epochs}\n")
            f.write(f"- **Learning Rate**: {self.learning_rate}\n\n")
            f.write("## Performance Metrics\n\n")
            f.write(f"| Metric | Score |\n")
            f.write(f"| :--- | :--- |\n")
            for k, v in self.metrics.items():
                f.write(f"| {k} | {v:.4f} |\n")
            f.write(f"\n*Report compiled on {time.strftime('%Y-%m-%d %H:%M:%S')}*")
            
        print("Report saved successfully.")
        return self
