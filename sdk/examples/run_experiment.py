#!/usr/bin/env python
"""
Example research script using the MedAI-OS Standalone Research SDK.
"""

from sdk import Experiment


def main():
    # 1. Define baseline metrics to compare against
    baseline_scores = {
        "dice_score": 0.820,
        "hausdorff_distance_mm": 4.12,
        "inference_time_sec": 0.05,
        "fps": 320.0
    }

    # 2. Run fluent pipeline
    # Chain training, evaluation, comparison, plotting and paper reporting
    (
        Experiment(experiment_name="femur_implant_medsam", dataset_version="v2.1")
        .train(model_name="MedSAM", epochs=3, lr=5e-5)
        .evaluate()
        .compare(baseline_metrics=baseline_scores)
        .visualize()
        .generate_report(output_path="medsam_femur_report.md")
    )

    print("\n[SDK Example] Research workflow finished successfully!")


if __name__ == "__main__":
    main()
