"""
Create stratified subsets from full datasets for rapid experimentation.
"""

import argparse
import sys
import os
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.io_utils import load_jsonl, save_jsonl, ensure_dir
from src.utils.seed import set_seed


def make_subset(
    input_path: str,
    output_path: str,
    train_size: int = 1000,
    dev_size: int = 200,
    test_size: int = 200,
    seed: int = 42
):
    """
    Create stratified subset from full dataset.
    
    Args:
        input_path: Input JSONL file
        output_path: Output JSONL file
        train_size: Number of training samples
        dev_size: Number of dev samples
        test_size: Number of test samples
        seed: Random seed
    """
    set_seed(seed)
    
    print(f"Loading dataset from {input_path}...")
    data = load_jsonl(input_path)
    
    # Split by original split
    train_data = [d for d in data if d['split'] == 'train']
    dev_data = [d for d in data if d['split'] == 'dev']
    test_data = [d for d in data if d['split'] == 'test']
    
    print(f"Original sizes: train={len(train_data)}, dev={len(dev_data)}, test={len(test_data)}")
    
    # Sample from each split
    subset = []
    
    if train_data and train_size > 0:
        sampled_train = random.sample(train_data, min(train_size, len(train_data)))
        for item in sampled_train:
            item['split'] = 'train'
        subset.extend(sampled_train)
        print(f"Sampled {len(sampled_train)} training samples")
    
    if dev_data and dev_size > 0:
        sampled_dev = random.sample(dev_data, min(dev_size, len(dev_data)))
        for item in sampled_dev:
            item['split'] = 'dev'
        subset.extend(sampled_dev)
        print(f"Sampled {len(sampled_dev)} dev samples")
    
    if test_data and test_size > 0:
        sampled_test = random.sample(test_data, min(test_size, len(test_data)))
        for item in sampled_test:
            item['split'] = 'test'
        subset.extend(sampled_test)
        print(f"Sampled {len(sampled_test)} test samples")
    elif dev_data and test_size > 0 and len(dev_data) > dev_size:
        # If no test split, take from dev
        remaining_dev = [d for d in dev_data if d not in subset]
        sampled_test = random.sample(remaining_dev, min(test_size, len(remaining_dev)))
        for item in sampled_test:
            item['split'] = 'test'
        subset.extend(sampled_test)
        print(f"Sampled {len(sampled_test)} test samples from dev split")
    
    # Save subset
    ensure_dir(os.path.dirname(output_path))
    save_jsonl(subset, output_path)
    
    print(f"\n✓ Saved {len(subset)} samples to {output_path}")
    for split_name in ['train', 'dev', 'test']:
        count = sum(1 for s in subset if s['split'] == split_name)
        if count > 0:
            print(f"  {split_name.capitalize()}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Create stratified subset from dataset")
    parser.add_argument("--in", dest="input", type=str, required=True, help="Input JSONL file")
    parser.add_argument("--out", type=str, required=True, help="Output JSONL file")
    parser.add_argument("--train", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--dev", type=int, default=200, help="Number of dev samples")
    parser.add_argument("--test", type=int, default=200, help="Number of test samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    make_subset(
        input_path=args.input,
        output_path=args.out,
        train_size=args.train,
        dev_size=args.dev,
        test_size=args.test,
        seed=args.seed
    )


if __name__ == "__main__":
    main()

