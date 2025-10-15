#!/usr/bin/env python
"""
Analyze QG experiment results in detail.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.utils.analysis import (
    load_predictions,
    analyze_difficulty_distribution,
    analyze_question_lengths,
    analyze_by_difficulty,
    plot_length_distribution,
    create_detailed_report
)
from src.utils.io_utils import load_json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Analyze QG experiment results")
    parser.add_argument(
        "--baseline",
        type=str,
        default="reports/tables/preds_baseline_squad.jsonl",
        help="Path to baseline predictions"
    )
    parser.add_argument(
        "--controlled",
        type=str,
        default="reports/tables/preds_controlled_squad.jsonl",
        help="Path to controlled predictions"
    )
    parser.add_argument(
        "--report",
        type=str,
        default="reports/ANALYSIS_REPORT.txt",
        help="Output path for detailed report"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("QG EXPERIMENT - DETAILED ANALYSIS")
    print("="*60)
    
    # Load predictions
    print("\n📥 Loading predictions...")
    baseline_preds = load_predictions(args.baseline)
    controlled_preds = load_predictions(args.controlled)
    
    print(f"✓ Loaded {len(baseline_preds)} baseline predictions")
    print(f"✓ Loaded {len(controlled_preds)} controlled predictions")
    
    # Analyze baseline
    print("\n" + "="*60)
    print("BASELINE MODEL ANALYSIS")
    print("="*60)
    analyze_difficulty_distribution(baseline_preds)
    pred_lens_b, ref_lens_b = analyze_question_lengths(baseline_preds)
    analyze_by_difficulty(baseline_preds)
    
    # Analyze controlled
    print("\n" + "="*60)
    print("CONTROLLED MODEL ANALYSIS")
    print("="*60)
    analyze_difficulty_distribution(controlled_preds)
    pred_lens_c, ref_lens_c = analyze_question_lengths(controlled_preds)
    analyze_by_difficulty(controlled_preds)
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    plot_length_distribution(
        pred_lens_b,
        ref_lens_b,
        "reports/figures/baseline_lengths.png"
    )
    plot_length_distribution(
        pred_lens_c,
        ref_lens_c,
        "reports/figures/controlled_lengths.png"
    )
    
    # Create detailed report
    print("\n📝 Creating detailed report...")
    create_detailed_report(args.baseline, args.controlled, args.report)
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - {args.report}")
    print(f"  - reports/figures/baseline_lengths.png")
    print(f"  - reports/figures/controlled_lengths.png")
    print()


if __name__ == "__main__":
    main()

