"""
Compute BLEU and ROUGE metrics for generated questions.
"""

import argparse
import sys
import os
from typing import List, Dict
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.io_utils import load_jsonl, save_json, ensure_dir
import sacrebleu
from rouge_score import rouge_scorer


def compute_bleu(predictions: List[str], references: List[List[str]]) -> Dict:
    """
    Compute BLEU score using sacrebleu.
    
    Args:
        predictions: List of predicted strings
        references: List of lists of reference strings
        
    Returns:
        Dictionary with BLEU scores
    """
    # sacrebleu expects references as list of lists (one list per reference)
    # Transpose references for sacrebleu format
    refs_transposed = [[ref[i] for ref in references] for i in range(len(references[0]))]
    
    bleu = sacrebleu.corpus_bleu(predictions, refs_transposed)
    
    return {
        'bleu': bleu.score,
        'bleu_precisions': bleu.precisions,
        'bleu_bp': bleu.bp,
        'bleu_sys_len': bleu.sys_len,
        'bleu_ref_len': bleu.ref_len
    }


def compute_rouge(predictions: List[str], references: List[str]) -> Dict:
    """
    Compute ROUGE scores.
    
    Args:
        predictions: List of predicted strings
        references: List of reference strings
        
    Returns:
        Dictionary with ROUGE scores
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    scores = {
        'rouge1': [],
        'rouge2': [],
        'rougeL': []
    }
    
    for pred, ref in zip(predictions, references):
        score = scorer.score(ref, pred)
        scores['rouge1'].append(score['rouge1'].fmeasure)
        scores['rouge2'].append(score['rouge2'].fmeasure)
        scores['rougeL'].append(score['rougeL'].fmeasure)
    
    # Compute averages
    rouge_results = {
        'rouge1': np.mean(scores['rouge1']),
        'rouge1_std': np.std(scores['rouge1']),
        'rouge2': np.mean(scores['rouge2']),
        'rouge2_std': np.std(scores['rouge2']),
        'rougeL': np.mean(scores['rougeL']),
        'rougeL_std': np.std(scores['rougeL'])
    }
    
    return rouge_results


def compute_length_stats(predictions: List[str], references: List[str]) -> Dict:
    """
    Compute length statistics.
    
    Args:
        predictions: List of predicted strings
        references: List of reference strings
        
    Returns:
        Dictionary with length statistics
    """
    pred_lengths = [len(p.split()) for p in predictions]
    ref_lengths = [len(r.split()) for r in references]
    
    return {
        'pred_avg_length': np.mean(pred_lengths),
        'pred_std_length': np.std(pred_lengths),
        'ref_avg_length': np.mean(ref_lengths),
        'ref_std_length': np.std(ref_lengths),
        'length_diff': np.mean([abs(p - r) for p, r in zip(pred_lengths, ref_lengths)])
    }


def evaluate_predictions(pred_path: str, output_path: str):
    """
    Evaluate predictions using BLEU and ROUGE.
    
    Args:
        pred_path: Path to predictions JSONL
        output_path: Path to save metrics JSON
    """
    print(f"Loading predictions from {pred_path}")
    predictions = load_jsonl(pred_path)
    
    # Extract predictions and references
    pred_questions = [p['pred_question'] for p in predictions]
    ref_questions = [p['ref_question'] for p in predictions]
    
    print(f"Evaluating {len(predictions)} predictions...")
    
    # Compute BLEU
    print("Computing BLEU...")
    bleu_results = compute_bleu(pred_questions, [[ref] for ref in ref_questions])
    
    # Compute ROUGE
    print("Computing ROUGE...")
    rouge_results = compute_rouge(pred_questions, ref_questions)
    
    # Compute length stats
    print("Computing length statistics...")
    length_stats = compute_length_stats(pred_questions, ref_questions)
    
    # Combine all metrics
    metrics = {
        'num_samples': len(predictions),
        **bleu_results,
        **rouge_results,
        **length_stats
    }
    
    # Save metrics
    ensure_dir(os.path.dirname(output_path))
    save_json(metrics, output_path)
    
    print(f"\n✓ Saved metrics to {output_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("METRICS SUMMARY")
    print("="*50)
    print(f"BLEU: {metrics['bleu']:.2f}")
    print(f"ROUGE-1: {metrics['rouge1']:.4f} (±{metrics['rouge1_std']:.4f})")
    print(f"ROUGE-2: {metrics['rouge2']:.4f} (±{metrics['rouge2_std']:.4f})")
    print(f"ROUGE-L: {metrics['rougeL']:.4f} (±{metrics['rougeL_std']:.4f})")
    print(f"Avg pred length: {metrics['pred_avg_length']:.1f} words")
    print(f"Avg ref length: {metrics['ref_avg_length']:.1f} words")
    print("="*50)
    
    # Also save CSV summary
    csv_path = output_path.replace('.json', '_summary.csv')
    import csv
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['BLEU', f"{metrics['bleu']:.2f}"])
        writer.writerow(['ROUGE-1', f"{metrics['rouge1']:.4f}"])
        writer.writerow(['ROUGE-2', f"{metrics['rouge2']:.4f}"])
        writer.writerow(['ROUGE-L', f"{metrics['rougeL']:.4f}"])
        writer.writerow(['Pred Length', f"{metrics['pred_avg_length']:.1f}"])
        writer.writerow(['Ref Length', f"{metrics['ref_avg_length']:.1f}"])
    
    print(f"✓ Saved CSV summary to {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Compute BLEU and ROUGE metrics")
    parser.add_argument(
        "--pred",
        type=str,
        required=True,
        help="Path to predictions JSONL"
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output path for metrics JSON"
    )
    
    args = parser.parse_args()
    
    evaluate_predictions(args.pred, args.out)


if __name__ == "__main__":
    main()

