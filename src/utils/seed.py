"""
Utilities for setting random seeds for reproducibility.
"""

import random
import numpy as np
import torch


def set_seed(seed: int = 42):
    """
    Set random seeds for Python, NumPy, PyTorch, and Transformers.
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # For deterministic behavior (may reduce performance)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_seed_from_config(config: dict, default: int = 42) -> int:
    """
    Extract seed from config dictionary.
    
    Args:
        config: Configuration dictionary
        default: Default seed value if not found in config
        
    Returns:
        Seed value
    """
    return config.get('seed', default)

