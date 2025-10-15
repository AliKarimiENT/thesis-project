"""
Aggregate all metrics, create comparison plots, and generate LaTeX output.
"""

import argparse
import sys
import os
from typing import Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.io_utils import load_json, ensure_dir


def load_human_eval(human_path: str) -> Optional[Dict]:
    """
    Load human evaluation results from XLSX.
    
    Args:
        human_path: Path to completed human eval XLSX
        
    Returns:
        Dictionary with human metrics or None if file doesn't exist
    """
    if not os.path.exists(human_path):
        print(f"Warning: Human eval file not found: {human_path}")
        return None
    
    try:
        df = pd.read_excel(human_path, sheet_name='Evaluation')
        
        # Compute means for each dimension
        dimensions = ['fluency', 'relevance', 'answerability', 'edu_value', 'perceived_diff']
        
        results = {
            'system_A': {},
            'system_B': {}
        }
        
        for dim in dimensions:
            col_A = f'{dim}_A'
            col_B = f'{dim}_B'
            
            if col_A in df.columns and col_B in df.columns:
                # Filter out empty ratings
                scores_A = pd.to_numeric(df[col_A], errors='coerce').dropna()
                scores_B = pd.to_numeric(df[col_B], errors='coerce').dropna()
                
                if len(scores_A) > 0:
                    results['system_A'][dim] = {
                        'mean': float(np.mean(scores_A)),
                        'std': float(np.std(scores_A))
                    }
                
                if len(scores_B) > 0:
                    results['system_B'][dim] = {
                        'mean': float(np.mean(scores_B)),
                        'std': float(np.std(scores_B))
                    }
        
        return results
    
    except Exception as e:
        print(f"Error loading human eval: {e}")
        return None


def create_comparison_table(
    metricsA: Dict,
    metricsB: Dict,
    qaA: Dict,
    qaB: Dict,
    human: Optional[Dict],
    output_csv: str
):
    """
    Create comparison table CSV.
    
    Args:
        metricsA: Metrics for system A
        metricsB: Metrics for system B
        qaA: QA metrics for system A
        qaB: QA metrics for system B
        human: Human evaluation results
        output_csv: Output CSV path
    """
    rows = []
    
    # Automatic metrics
    rows.append(['Metric', 'System A (Baseline)', 'System B (Controlled)'])
    rows.append(['--- Automatic Metrics ---', '', ''])
    rows.append(['BLEU', f"{metricsA['bleu']:.2f}", f"{metricsB['bleu']:.2f}"])
    rows.append(['ROUGE-1', f"{metricsA['rouge1']:.4f}", f"{metricsB['rouge1']:.4f}"])
    rows.append(['ROUGE-2', f"{metricsA['rouge2']:.4f}", f"{metricsB['rouge2']:.4f}"])
    rows.append(['ROUGE-L', f"{metricsA['rougeL']:.4f}", f"{metricsB['rougeL']:.4f}"])
    rows.append(['--- QA Answerability ---', '', ''])
    rows.append(['EM', f"{qaA['em_mean']:.4f}", f"{qaB['em_mean']:.4f}"])
    rows.append(['F1', f"{qaA['f1_mean']:.4f}", f"{qaB['f1_mean']:.4f}"])
    
    # Human metrics if available
    if human:
        rows.append(['--- Human Evaluation ---', '', ''])
        dimensions = ['fluency', 'relevance', 'answerability', 'edu_value', 'perceived_diff']
        for dim in dimensions:
            if dim in human['system_A'] and dim in human['system_B']:
                val_A = human['system_A'][dim]
                val_B = human['system_B'][dim]
                rows.append([
                    dim.replace('_', ' ').title(),
                    f"{val_A['mean']:.2f} (±{val_A['std']:.2f})",
                    f"{val_B['mean']:.2f} (±{val_B['std']:.2f})"
                ])
    
    # Write CSV
    import csv
    ensure_dir(os.path.dirname(output_csv))
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"✓ Saved comparison table to {output_csv}")


def create_comparison_plot(
    metricsA: Dict,
    metricsB: Dict,
    qaA: Dict,
    qaB: Dict,
    output_fig: str
):
    """
    Create bar plot comparing systems.
    
    Args:
        metricsA: Metrics for system A
        metricsB: Metrics for system B
        qaA: QA metrics for system A
        qaB: QA metrics for system B
        output_fig: Output figure path
    """
    # Prepare data
    metrics_names = ['BLEU', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'EM', 'F1']
    
    # Normalize BLEU to 0-1 scale for visualization
    baseline_scores = [
        metricsA['bleu'] / 100,
        metricsA['rouge1'],
        metricsA['rouge2'],
        metricsA['rougeL'],
        qaA['em_mean'],
        qaA['f1_mean']
    ]
    
    controlled_scores = [
        metricsB['bleu'] / 100,
        metricsB['rouge1'],
        metricsB['rouge2'],
        metricsB['rougeL'],
        qaB['em_mean'],
        qaB['f1_mean']
    ]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline_scores, width, label='Baseline', color='steelblue', alpha=0.8)
    bars2 = ax.bar(x + width/2, controlled_scores, width, label='Controlled', color='coral', alpha=0.8)
    
    ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Question Generation: Baseline vs. Difficulty-Controlled', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1)
    
    # Add value labels on bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=8)
    
    add_labels(bars1)
    add_labels(bars2)
    
    plt.tight_layout()
    
    ensure_dir(os.path.dirname(output_fig))
    plt.savefig(output_fig, dpi=300, bbox_inches='tight')
    print(f"✓ Saved comparison plot to {output_fig}")
    plt.close()


def generate_latex(
    metricsA: Dict,
    metricsB: Dict,
    qaA: Dict,
    qaB: Dict,
    human: Optional[Dict],
    fig_path: str,
    output_tex: str
):
    """
    Generate LaTeX tables and figure code.
    
    Args:
        metricsA: Metrics for system A
        metricsB: Metrics for system B
        qaA: QA metrics for system A
        qaB: QA metrics for system B
        human: Human evaluation results
        fig_path: Path to comparison figure
        output_tex: Output LaTeX file path
    """
    latex_content = []
    
    # Automatic metrics table
    latex_content.append("% Automatic Metrics Table")
    latex_content.append("\\begin{table}[ht]")
    latex_content.append("\\centering")
    latex_content.append("\\caption{Automatic Evaluation Metrics}")
    latex_content.append("\\label{tab:automatic-metrics}")
    latex_content.append("\\begin{tabular}{lcc}")
    latex_content.append("\\toprule")
    latex_content.append("\\textbf{Metric} & \\textbf{Baseline} & \\textbf{Controlled} \\\\")
    latex_content.append("\\midrule")
    latex_content.append(f"BLEU & {metricsA['bleu']:.2f} & {metricsB['bleu']:.2f} \\\\")
    latex_content.append(f"ROUGE-1 & {metricsA['rouge1']:.3f} & {metricsB['rouge1']:.3f} \\\\")
    latex_content.append(f"ROUGE-2 & {metricsA['rouge2']:.3f} & {metricsB['rouge2']:.3f} \\\\")
    latex_content.append(f"ROUGE-L & {metricsA['rougeL']:.3f} & {metricsB['rougeL']:.3f} \\\\")
    latex_content.append("\\bottomrule")
    latex_content.append("\\end{tabular}")
    latex_content.append("\\end{table}")
    latex_content.append("")
    
    # QA answerability table
    latex_content.append("% QA Answerability Table")
    latex_content.append("\\begin{table}[ht]")
    latex_content.append("\\centering")
    latex_content.append("\\caption{QA Answerability Metrics}")
    latex_content.append("\\label{tab:qa-metrics}")
    latex_content.append("\\begin{tabular}{lcc}")
    latex_content.append("\\toprule")
    latex_content.append("\\textbf{Metric} & \\textbf{Baseline} & \\textbf{Controlled} \\\\")
    latex_content.append("\\midrule")
    latex_content.append(f"Exact Match (EM) & {qaA['em_mean']:.3f} & {qaB['em_mean']:.3f} \\\\")
    latex_content.append(f"F1 Score & {qaA['f1_mean']:.3f} & {qaB['f1_mean']:.3f} \\\\")
    latex_content.append("\\bottomrule")
    latex_content.append("\\end{tabular}")
    latex_content.append("\\end{table}")
    latex_content.append("")
    
    # Human evaluation table (if available)
    if human:
        latex_content.append("% Human Evaluation Table")
        latex_content.append("\\begin{table}[ht]")
        latex_content.append("\\centering")
        latex_content.append("\\caption{Human Evaluation Results (1-5 Likert Scale)}")
        latex_content.append("\\label{tab:human-eval}")
        latex_content.append("\\begin{tabular}{lcc}")
        latex_content.append("\\toprule")
        latex_content.append("\\textbf{Dimension} & \\textbf{Baseline} & \\textbf{Controlled} \\\\")
        latex_content.append("\\midrule")
        
        dim_labels = {
            'fluency': 'Fluency',
            'relevance': 'Relevance',
            'answerability': 'Answerability',
            'edu_value': 'Educational Value',
            'perceived_diff': 'Perceived Difficulty'
        }
        
        for dim, label in dim_labels.items():
            if dim in human['system_A'] and dim in human['system_B']:
                val_A = human['system_A'][dim]
                val_B = human['system_B'][dim]
                latex_content.append(
                    f"{label} & {val_A['mean']:.2f} $\\pm$ {val_A['std']:.2f} & "
                    f"{val_B['mean']:.2f} $\\pm$ {val_B['std']:.2f} \\\\"
                )
        
        latex_content.append("\\bottomrule")
        latex_content.append("\\end{tabular}")
        latex_content.append("\\end{table}")
        latex_content.append("")
    
    # Figure
    latex_content.append("% Comparison Figure")
    latex_content.append("\\begin{figure}[ht]")
    latex_content.append("\\centering")
    # Use relative path from paper directory
    fig_basename = os.path.basename(fig_path)
    latex_content.append(f"\\includegraphics[width=0.8\\textwidth]{{../reports/figures/{fig_basename}}}")
    latex_content.append("\\caption{Comparison of baseline and difficulty-controlled question generation systems.}")
    latex_content.append("\\label{fig:comparison}")
    latex_content.append("\\end{figure}")
    latex_content.append("")
    
    # Write to file
    ensure_dir(os.path.dirname(output_tex))
    with open(output_tex, 'w') as f:
        f.write('\n'.join(latex_content))
    
    print(f"✓ Saved LaTeX output to {output_tex}")


def aggregate_all(
    metricsA_path: str,
    metricsB_path: str,
    qaA_path: str,
    qaB_path: str,
    human_path: Optional[str],
    out_csv: str,
    out_fig: str,
    emit_latex: Optional[str]
):
    """
    Aggregate all metrics and create outputs.
    
    Args:
        metricsA_path: Path to system A metrics JSON
        metricsB_path: Path to system B metrics JSON
        qaA_path: Path to system A QA metrics JSON
        qaB_path: Path to system B QA metrics JSON
        human_path: Path to human eval XLSX (optional)
        out_csv: Output CSV path
        out_fig: Output figure path
        emit_latex: Output LaTeX path (optional)
    """
    print("Loading metrics...")
    metricsA = load_json(metricsA_path)
    metricsB = load_json(metricsB_path)
    qaA = load_json(qaA_path)
    qaB = load_json(qaB_path)
    
    human = None
    if human_path:
        human = load_human_eval(human_path)
    
    print("\nCreating comparison table...")
    create_comparison_table(metricsA, metricsB, qaA, qaB, human, out_csv)
    
    print("\nCreating comparison plot...")
    create_comparison_plot(metricsA, metricsB, qaA, qaB, out_fig)
    
    if emit_latex:
        print("\nGenerating LaTeX output...")
        generate_latex(metricsA, metricsB, qaA, qaB, human, out_fig, emit_latex)
    
    print("\n" + "="*50)
    print("AGGREGATION COMPLETE")
    print("="*50)
    print(f"CSV: {out_csv}")
    print(f"Figure: {out_fig}")
    if emit_latex:
        print(f"LaTeX: {emit_latex}")
    print("="*50)


def main():
    parser = argparse.ArgumentParser(description="Aggregate metrics and create outputs")
    parser.add_argument("--metricsA", type=str, required=True, help="System A metrics JSON")
    parser.add_argument("--metricsB", type=str, required=True, help="System B metrics JSON")
    parser.add_argument("--qaA", type=str, required=True, help="System A QA metrics JSON")
    parser.add_argument("--qaB", type=str, required=True, help="System B QA metrics JSON")
    parser.add_argument("--human", type=str, default=None, help="Human eval XLSX")
    parser.add_argument("--out_csv", type=str, required=True, help="Output CSV path")
    parser.add_argument("--out_fig", type=str, required=True, help="Output figure path")
    parser.add_argument("--emit_latex", type=str, default=None, help="Output LaTeX path")
    
    args = parser.parse_args()
    
    # Generate default figure path with date if not absolute
    if args.out_fig and 'YYYYMMDD' in args.out_fig:
        date_str = datetime.now().strftime('%Y%m%d')
        args.out_fig = args.out_fig.replace('YYYYMMDD', date_str)
    
    aggregate_all(
        metricsA_path=args.metricsA,
        metricsB_path=args.metricsB,
        qaA_path=args.qaA,
        qaB_path=args.qaB,
        human_path=args.human,
        out_csv=args.out_csv,
        out_fig=args.out_fig,
        emit_latex=args.emit_latex
    )


if __name__ == "__main__":
    main()

