"""
Analysis utilities for QG experiment results.
"""

import json
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter


def load_predictions(pred_path: str) -> List[Dict]:
    """
    Load predictions from JSONL file.
    
    Args:
        pred_path: Path to predictions JSONL
        
    Returns:
        List of prediction dictionaries
    """
    predictions = []
    with open(pred_path, 'r') as f:
        for line in f:
            predictions.append(json.loads(line))
    return predictions


def analyze_difficulty_distribution(predictions: List[Dict]):
    """
    Analyze difficulty distribution in predictions.
    
    Args:
        predictions: List of prediction dictionaries
    """
    difficulties = [p.get('difficulty', 'unknown') for p in predictions]
    dist = Counter(difficulties)
    
    print("\n📊 Difficulty Distribution:")
    print("="*50)
    for diff in ['easy', 'medium', 'hard']:
        count = dist.get(diff, 0)
        pct = 100 * count / len(predictions) if predictions else 0
        print(f"  {diff.capitalize():8s}: {count:4d} ({pct:5.1f}%)")
    print("="*50)
    
    return dist


def analyze_question_lengths(predictions: List[Dict]):
    """
    Analyze question length distributions.
    
    Args:
        predictions: List of prediction dictionaries
    """
    pred_lengths = [len(p['pred_question'].split()) for p in predictions]
    ref_lengths = [len(p['ref_question'].split()) for p in predictions]
    
    print("\n📏 Question Length Analysis:")
    print("="*50)
    print(f"  Predicted Questions:")
    print(f"    Mean: {np.mean(pred_lengths):.1f} words")
    print(f"    Std:  {np.std(pred_lengths):.1f} words")
    print(f"    Min:  {np.min(pred_lengths)} words")
    print(f"    Max:  {np.max(pred_lengths)} words")
    print(f"\n  Reference Questions:")
    print(f"    Mean: {np.mean(ref_lengths):.1f} words")
    print(f"    Std:  {np.std(ref_lengths):.1f} words")
    print(f"    Min:  {np.min(ref_lengths)} words")
    print(f"    Max:  {np.max(ref_lengths)} words")
    print("="*50)
    
    return pred_lengths, ref_lengths


def analyze_by_difficulty(predictions: List[Dict], metrics_path: str = None):
    """
    Analyze metrics broken down by difficulty level.
    
    Args:
        predictions: List of prediction dictionaries
        metrics_path: Optional path to load full metrics
    """
    # Group by difficulty
    by_difficulty = {'easy': [], 'medium': [], 'hard': []}
    
    for p in predictions:
        diff = p.get('difficulty', 'medium')
        if diff in by_difficulty:
            by_difficulty[diff].append(p)
    
    print("\n📊 Breakdown by Difficulty:")
    print("="*50)
    for diff in ['easy', 'medium', 'hard']:
        items = by_difficulty[diff]
        if items:
            avg_pred_len = np.mean([len(p['pred_question'].split()) for p in items])
            avg_ref_len = np.mean([len(p['ref_question'].split()) for p in items])
            print(f"\n  {diff.capitalize()}:")
            print(f"    Count: {len(items)}")
            print(f"    Avg pred length: {avg_pred_len:.1f} words")
            print(f"    Avg ref length: {avg_ref_len:.1f} words")
    print("="*50)


def plot_length_distribution(
    pred_lengths: List[int],
    ref_lengths: List[int],
    output_path: str
):
    """
    Plot question length distributions.
    
    Args:
        pred_lengths: List of predicted question lengths
        ref_lengths: List of reference question lengths
        output_path: Path to save plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Predicted lengths
    axes[0].hist(pred_lengths, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    axes[0].axvline(np.mean(pred_lengths), color='red', linestyle='--', 
                    linewidth=2, label=f'Mean: {np.mean(pred_lengths):.1f}')
    axes[0].set_xlabel('Question Length (words)', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Predicted Questions', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Reference lengths
    axes[1].hist(ref_lengths, bins=20, alpha=0.7, color='coral', edgecolor='black')
    axes[1].axvline(np.mean(ref_lengths), color='red', linestyle='--',
                    linewidth=2, label=f'Mean: {np.mean(ref_lengths):.1f}')
    axes[1].set_xlabel('Question Length (words)', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Reference Questions', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved length distribution plot to {output_path}")


def create_detailed_report(
    baseline_preds_path: str,
    controlled_preds_path: str,
    output_path: str
):
    """
    Create detailed analysis report comparing both systems.
    
    Args:
        baseline_preds_path: Path to baseline predictions
        controlled_preds_path: Path to controlled predictions
        output_path: Path to save report
    """
    baseline = load_predictions(baseline_preds_path)
    controlled = load_predictions(controlled_preds_path)
    
    report = []
    report.append("="*60)
    report.append("QG EXPERIMENT - DETAILED ANALYSIS REPORT")
    report.append("="*60)
    report.append("")
    
    # Baseline analysis
    report.append("BASELINE MODEL")
    report.append("-"*60)
    report.append(f"Total predictions: {len(baseline)}")
    
    baseline_dist = Counter([p.get('difficulty', 'unknown') for p in baseline])
    for diff in ['easy', 'medium', 'hard']:
        count = baseline_dist.get(diff, 0)
        pct = 100 * count / len(baseline) if baseline else 0
        report.append(f"  {diff.capitalize()}: {count} ({pct:.1f}%)")
    
    baseline_lens = [len(p['pred_question'].split()) for p in baseline]
    report.append(f"Avg question length: {np.mean(baseline_lens):.1f} ± {np.std(baseline_lens):.1f} words")
    report.append("")
    
    # Controlled analysis
    report.append("CONTROLLED MODEL")
    report.append("-"*60)
    report.append(f"Total predictions: {len(controlled)}")
    
    controlled_dist = Counter([p.get('difficulty', 'unknown') for p in controlled])
    for diff in ['easy', 'medium', 'hard']:
        count = controlled_dist.get(diff, 0)
        pct = 100 * count / len(controlled) if controlled else 0
        report.append(f"  {diff.capitalize()}: {count} ({pct:.1f}%)")
    
    controlled_lens = [len(p['pred_question'].split()) for p in controlled]
    report.append(f"Avg question length: {np.mean(controlled_lens):.1f} ± {np.std(controlled_lens):.1f} words")
    report.append("")
    
    # Sample comparisons
    report.append("SAMPLE COMPARISONS (First 5)")
    report.append("-"*60)
    for i in range(min(5, len(baseline))):
        report.append(f"\nExample {i+1}:")
        report.append(f"  Context: {baseline[i]['context'][:80]}...")
        report.append(f"  Answer: {baseline[i]['answer']}")
        report.append(f"  Reference: {baseline[i]['ref_question']}")
        report.append(f"  Baseline: {baseline[i]['pred_question']}")
        report.append(f"  Controlled: {controlled[i]['pred_question']}")
        report.append(f"  Difficulty: {baseline[i].get('difficulty', 'N/A')}")
    
    report.append("")
    report.append("="*60)
    
    # Save report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"\n✓ Saved detailed report to {output_path}")
    
    # Also print to console
    print("\n" + '\n'.join(report))

