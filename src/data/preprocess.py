"""
Preprocess datasets and add difficulty labels for controlled QG.
"""

import argparse
import sys
import os
import numpy as np
from collections import Counter
from typing import Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.io_utils import load_jsonl, save_jsonl, ensure_dir
from tqdm import tqdm


def compute_answer_length_score(answer: str) -> float:
    """
    Compute difficulty score based on answer length.
    Shorter answers are generally easier.
    
    Args:
        answer: Answer text
        
    Returns:
        Normalized score (0-1)
    """
    tokens = answer.split()
    # Normalize: 1 word = 0, 10+ words = 1
    return min(len(tokens) / 10.0, 1.0)


def compute_answer_rarity_score(answer: str, context: str) -> float:
    """
    Compute difficulty score based on answer rarity in context.
    Rarer answers (lower frequency) are harder.
    
    Args:
        answer: Answer text
        context: Context text
        
    Returns:
        Normalized score (0-1)
    """
    context_tokens = context.lower().split()
    answer_tokens = answer.lower().split()
    
    if not answer_tokens or not context_tokens:
        return 0.5
    
    # Count occurrences of answer tokens in context
    context_counter = Counter(context_tokens)
    
    # Average frequency of answer tokens
    frequencies = []
    for token in answer_tokens:
        freq = context_counter.get(token, 0)
        frequencies.append(freq)
    
    if not frequencies:
        return 0.5
    
    avg_freq = np.mean(frequencies)
    
    # Normalize: high frequency (5+) = 0 (easy), low frequency (1) = 1 (hard)
    # Using inverse: 1 / (freq + 1)
    rarity_score = 1.0 / (avg_freq + 1.0)
    
    # Scale to 0-1 range
    return min(rarity_score, 1.0)


def compute_context_complexity_score(context: str) -> float:
    """
    Compute difficulty score based on context complexity.
    Longer contexts with more complex vocabulary are harder.
    
    Args:
        context: Context text
        
    Returns:
        Normalized score (0-1)
    """
    sentences = context.split('.')
    num_sentences = len([s for s in sentences if s.strip()])
    
    tokens = context.split()
    num_tokens = len(tokens)
    
    # Average sentence length
    avg_sent_length = num_tokens / max(num_sentences, 1)
    
    # Vocabulary diversity (unique tokens / total tokens)
    vocab_diversity = len(set(tokens)) / max(num_tokens, 1)
    
    # Combine metrics
    # Longer sentences and higher vocab diversity = harder
    length_score = min(avg_sent_length / 30.0, 1.0)  # 30+ words per sentence = 1
    diversity_score = vocab_diversity  # Already 0-1
    
    complexity = (length_score + diversity_score) / 2.0
    return complexity


def compute_difficulty_score(sample: Dict) -> float:
    """
    Compute overall difficulty score for a sample using heuristics.
    
    Args:
        sample: Sample dictionary with 'context', 'answer', 'question'
        
    Returns:
        Difficulty score (0-1, higher = harder)
    """
    answer = sample.get('answer', '')
    context = sample.get('context', '')
    
    # Compute component scores
    answer_length = compute_answer_length_score(answer)
    answer_rarity = compute_answer_rarity_score(answer, context)
    context_complexity = compute_context_complexity_score(context)
    
    # Weighted combination
    weights = {
        'answer_length': 0.3,
        'answer_rarity': 0.4,
        'context_complexity': 0.3
    }
    
    difficulty = (
        weights['answer_length'] * answer_length +
        weights['answer_rarity'] * answer_rarity +
        weights['context_complexity'] * context_complexity
    )
    
    return difficulty


def assign_difficulty_labels(data: List[Dict]) -> List[Dict]:
    """
    Assign difficulty labels (easy/medium/hard) to dataset.
    
    Args:
        data: List of sample dictionaries
        
    Returns:
        Data with 'difficulty' and 'difficulty_score' fields added
    """
    print("Computing difficulty scores...")
    
    # Compute scores for all samples
    for sample in tqdm(data):
        sample['difficulty_score'] = compute_difficulty_score(sample)
    
    # Get score distribution
    scores = [s['difficulty_score'] for s in data]
    scores_sorted = sorted(scores)
    
    # Use percentiles for binning
    percentile_33 = np.percentile(scores_sorted, 33)
    percentile_67 = np.percentile(scores_sorted, 67)
    
    print(f"\nDifficulty score distribution:")
    print(f"  Min: {min(scores):.3f}")
    print(f"  33rd percentile: {percentile_33:.3f}")
    print(f"  Median: {np.median(scores):.3f}")
    print(f"  67th percentile: {percentile_67:.3f}")
    print(f"  Max: {max(scores):.3f}")
    
    # Assign labels
    for sample in data:
        score = sample['difficulty_score']
        if score < percentile_33:
            sample['difficulty'] = 'easy'
        elif score < percentile_67:
            sample['difficulty'] = 'medium'
        else:
            sample['difficulty'] = 'hard'
    
    # Print class distribution
    difficulty_counts = Counter([s['difficulty'] for s in data])
    print(f"\nDifficulty label distribution:")
    for label in ['easy', 'medium', 'hard']:
        count = difficulty_counts[label]
        pct = 100 * count / len(data)
        print(f"  {label.capitalize()}: {count} ({pct:.1f}%)")
    
    return data


def preprocess_dataset(input_path: str, output_path: str):
    """
    Load dataset, compute difficulty labels, and save.
    
    Args:
        input_path: Input JSONL file
        output_path: Output JSONL file with difficulty labels
    """
    print(f"Loading dataset from {input_path}...")
    data = load_jsonl(input_path)
    print(f"Loaded {len(data)} samples")
    
    # Add difficulty labels
    data = assign_difficulty_labels(data)
    
    # Save processed dataset
    ensure_dir(os.path.dirname(output_path))
    save_jsonl(data, output_path)
    
    print(f"\n✓ Saved {len(data)} samples to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Preprocess dataset and add difficulty labels")
    parser.add_argument("--in", dest="input", type=str, required=True, help="Input JSONL file")
    parser.add_argument("--out", type=str, required=True, help="Output JSONL file")
    args = parser.parse_args()
    
    preprocess_dataset(args.input, args.out)


if __name__ == "__main__":
    main()

