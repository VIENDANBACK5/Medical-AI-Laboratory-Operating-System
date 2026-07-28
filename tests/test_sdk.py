import os
import sys
import numpy as np
import pytest
from unittest.mock import patch

from sdk import Experiment, calculate_dice, calculate_hausdorff_distance
from sdk.cli import main as cli_main


def test_metrics_dice_calculation():
    # 1. Test identical arrays
    arr1 = np.ones((5, 5, 5), dtype=np.uint8)
    assert calculate_dice(arr1, arr1) == 1.0
    
    # 2. Test completely disjoint arrays
    arr_zeros = np.zeros((5, 5, 5), dtype=np.uint8)
    arr_ones = np.ones((5, 5, 5), dtype=np.uint8)
    assert calculate_dice(arr_zeros, arr_ones) == 0.0
    
    # 3. Test 50% overlap
    arr_half1 = np.zeros((4, 4, 4), dtype=np.uint8)
    arr_half1[0:2, :, :] = 1  # 32 active voxels
    
    arr_half2 = np.zeros((4, 4, 4), dtype=np.uint8)
    arr_half2[1:3, :, :] = 1  # 32 active voxels, overlaps at index 1 (16 voxels)
    
    # Intersect = 16. Total = 32 + 32 = 64. Dice = 2 * 16 / 64 = 0.5
    assert calculate_dice(arr_half1, arr_half2) == 0.5


def test_metrics_hausdorff_calculation():
    arr1 = np.ones((4, 4, 4), dtype=np.uint8)
    # Identical arrays should return 0.0 Hausdorff distance
    assert calculate_hausdorff_distance(arr1, arr1) == 0.0


def test_fluent_api_experiment_chaining():
    report_file = "test_run_report.md"
    if os.path.exists(report_file):
        os.remove(report_file)
        
    exp = Experiment(experiment_name="test_fluent_flow", dataset_version="v_test")
    
    # Verify state before training
    assert exp.is_trained is False
    assert exp.is_evaluated is False
    
    # Verify evaluation fails before training
    with pytest.raises(RuntimeError):
        exp.evaluate()

    # Execute training and evaluation
    exp.train(model_name="MedSAM", epochs=2, lr=1e-4).evaluate()
    
    assert exp.is_trained is True
    assert exp.is_evaluated is True
    assert "dice_score" in exp.metrics
    
    # Run compare, visualize, report
    exp.compare(baseline_metrics={"dice_score": 0.8}).visualize().generate_report(report_file)
    
    # Assert file generated
    assert os.path.exists(report_file)
    os.remove(report_file)


def test_sdk_cli_execution():
    report_file = "cli_test_report.md"
    if os.path.exists(report_file):
        os.remove(report_file)
        
    # Mock CLI arguments
    test_args = [
        "sdk.cli",
        "--name", "test_cli_run",
        "--dataset", "v_cli",
        "--model", "nnUNet",
        "--epochs", "1",
        "--lr", "1e-5",
        "--report", report_file
    ]
    
    with patch.object(sys, "argv", test_args):
        cli_main()
        
    # Assert that execution completed and report file was written
    assert os.path.exists(report_file)
    os.remove(report_file)
