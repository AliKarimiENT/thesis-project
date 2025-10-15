"""
Evaluate question answerability using a QA model.
"""

import argparse
import sys
import os
from typing import List, Dict
import numpy as np
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import torch
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer

from src.utils.io_utils import load_jsonl, save_json, ensure_dir
from src.utils.metrics import compute_f1, compute_exact_match, normalize_text


def evaluate_answerability(
    dataset_path: str,
    pred_path: str,
    output_path: str,
    qa_model_name: str = "distilbert-base-cased-distilled-squad"
):
    """
    Evaluate answerability of generated questions using QA model.
    
    Args:
        dataset_path: Path to dataset JSONL (for context)
        pred_path: Path to predictions JSONL
        output_path: Path to save QA metrics
        qa_model_name: Name of QA model to use
    """
    print(f"Loading QA model: {qa_model_name}")
    device = 0 if torch.cuda.is_available() else -1
    
    qa_pipeline = pipeline(
        "question-answering",
        model=qa_model_name,
        tokenizer=qa_model_name,
        device=device
    )
    
    print(f"Loading predictions from {pred_path}")
    predictions = load_jsonl(pred_path)
    
    print(f"Evaluating answerability for {len(predictions)} questions...")
    
    results = []
    em_scores = []
    f1_scores = []
    
    for pred in tqdm(predictions):
        context = pred['context']
        pred_question = pred['pred_question']
        gold_answer = pred['answer']
        
        if not pred_question or not pred_question.strip():
            # Empty prediction
            results.append({
                'id': pred['id'],
                'em': 0,
                'f1': 0,
                'qa_answer': '',
                'gold_answer': gold_answer,
                'pred_question': pred_question
            })
            em_scores.append(0)
            f1_scores.append(0)
            continue
        
        try:
            # Run QA model
            qa_result = qa_pipeline(
                question=pred_question,
                context=context
            )
            qa_answer = qa_result['answer']
            
            # Compute EM and F1
            em = 1 if compute_exact_match(qa_answer, gold_answer) else 0
            
            # Token-level F1
            qa_tokens = normalize_text(qa_answer).split()
            gold_tokens = normalize_text(gold_answer).split()
            f1 = compute_f1(qa_tokens, gold_tokens)
            
            results.append({
                'id': pred['id'],
                'em': em,
                'f1': f1,
                'qa_answer': qa_answer,
                'gold_answer': gold_answer,
                'pred_question': pred_question,
                'qa_score': qa_result.get('score', 0.0)
            })
            
            em_scores.append(em)
            f1_scores.append(f1)
            
        except Exception as e:
            print(f"Error processing {pred['id']}: {e}")
            results.append({
                'id': pred['id'],
                'em': 0,
                'f1': 0,
                'qa_answer': '',
                'gold_answer': gold_answer,
                'pred_question': pred_question,
                'error': str(e)
            })
            em_scores.append(0)
            f1_scores.append(0)
    
    # Compute aggregate metrics
    metrics = {
        'num_samples': len(predictions),
        'em_mean': np.mean(em_scores),
        'em_std': np.std(em_scores),
        'f1_mean': np.mean(f1_scores),
        'f1_std': np.std(f1_scores),
        'per_sample': results
    }
    
    # Save metrics
    ensure_dir(os.path.dirname(output_path))
    save_json(metrics, output_path)
    
    print(f"\n✓ Saved QA metrics to {output_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("QA ANSWERABILITY SUMMARY")
    print("="*50)
    print(f"Exact Match (EM): {metrics['em_mean']:.4f} (±{metrics['em_std']:.4f})")
    print(f"F1 Score: {metrics['f1_mean']:.4f} (±{metrics['f1_std']:.4f})")
    print("="*50)
    
    # Save CSV summary
    csv_path = output_path.replace('.json', '_summary.csv')
    import csv
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['EM Mean', f"{metrics['em_mean']:.4f}"])
        writer.writerow(['EM Std', f"{metrics['em_std']:.4f}"])
        writer.writerow(['F1 Mean', f"{metrics['f1_mean']:.4f}"])
        writer.writerow(['F1 Std', f"{metrics['f1_std']:.4f}"])
    
    print(f"✓ Saved CSV summary to {csv_path}")
    
    # Show some examples
    print("\nExample QA results:")
    for i, result in enumerate(results[:3]):
        print(f"\n--- Example {i+1} ---")
        print(f"Question: {result['pred_question']}")
        print(f"Gold Answer: {result['gold_answer']}")
        print(f"QA Answer: {result['qa_answer']}")
        print(f"EM: {result['em']}, F1: {result['f1']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate question answerability using QA model")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to dataset JSONL"
    )
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
        help="Output path for QA metrics JSON"
    )
    parser.add_argument(
        "--qa_model",
        type=str,
        default="distilbert-base-cased-distilled-squad",
        help="QA model to use for evaluation"
    )
    
    args = parser.parse_args()
    
    evaluate_answerability(
        dataset_path=args.dataset,
        pred_path=args.pred,
        output_path=args.out,
        qa_model_name=args.qa_model
    )


if __name__ == "__main__":
    main()

