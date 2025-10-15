"""
Utilities for computing evaluation metrics.
"""

from typing import List, Dict, Tuple
import numpy as np
from collections import Counter


def compute_f1(pred_tokens: List[str], gold_tokens: List[str]) -> float:
    """
    Compute token-level F1 score between prediction and gold.
    
    Args:
        pred_tokens: List of predicted tokens
        gold_tokens: List of gold tokens
        
    Returns:
        F1 score (0-1)
    """
    if not pred_tokens or not gold_tokens:
        return 0.0
    
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())
    
    if num_common == 0:
        return 0.0
    
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    
    return f1


def compute_exact_match(pred: str, gold: str) -> bool:
    """
    Compute exact match between prediction and gold (case-insensitive, whitespace-normalized).
    
    Args:
        pred: Predicted string
        gold: Gold string
        
    Returns:
        True if exact match, False otherwise
    """
    pred_normalized = ' '.join(pred.lower().split())
    gold_normalized = ' '.join(gold.lower().split())
    return pred_normalized == gold_normalized


def compute_confidence_interval(scores: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Compute mean and confidence interval for a list of scores.
    
    Args:
        scores: List of numeric scores
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (mean, lower_bound, upper_bound)
    """
    if not scores:
        return 0.0, 0.0, 0.0
    
    scores_array = np.array(scores)
    mean = np.mean(scores_array)
    std_err = np.std(scores_array, ddof=1) / np.sqrt(len(scores_array))
    
    # Using normal approximation for CI
    z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
    margin = z_score * std_err
    
    return mean, mean - margin, mean + margin


def aggregate_metrics(metrics_list: List[Dict[str, float]]) -> Dict[str, Tuple[float, float, float]]:
    """
    Aggregate metrics from multiple samples with confidence intervals.
    
    Args:
        metrics_list: List of dictionaries containing metrics per sample
        
    Returns:
        Dictionary mapping metric names to (mean, lower_ci, upper_ci)
    """
    if not metrics_list:
        return {}
    
    # Collect all metric keys
    all_keys = set()
    for m in metrics_list:
        all_keys.update(m.keys())
    
    result = {}
    for key in all_keys:
        values = [m[key] for m in metrics_list if key in m]
        if values:
            result[key] = compute_confidence_interval(values)
    
    return result


def normalize_text(text: str) -> str:
    """
    Normalize text by lowercasing and removing extra whitespace.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    return ' '.join(text.lower().strip().split())


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length with ellipsis.
    
    Args:
        text: Input text
        max_length: Maximum character length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'

