import argparse

from sdk.experiment import Experiment


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MedAI-OS Standalone Research SDK CLI Interface"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="cli_experiment",
        help="Name identifier of the experiment."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="v1.0",
        help="Dataset version tag to query from server."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="MedSAM",
        choices=["MedSAM", "nnUNet", "TotalSegmentator"],
        help="Target AI model to train and evaluate."
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (simulated)."
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1e-4,
        help="Learning rate optimizer setting."
    )
    parser.add_argument(
        "--report",
        type=str,
        default="cli_report.md",
        help="File path to save the generated markdown report."
    )

    args = parser.parse_args()

    # Launch the Fluent API pipeline directly from parsed CLI arguments
    _ = (
        Experiment(args.name, dataset_version=args.dataset)
        .train(model_name=args.model, epochs=args.epochs, lr=args.lr)
        .evaluate()
        .visualize()
        .generate_report(args.report)
    )

    print("\n--- CLI Execution Finished ---")


if __name__ == "__main__":
    main()
