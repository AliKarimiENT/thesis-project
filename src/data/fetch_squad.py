"""
Fetch and prepare SQuAD dataset for Question Generation.
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datasets import load_dataset
from src.utils.io_utils import save_jsonl, ensure_dir
from tqdm import tqdm


def fetch_squad(output_path: str = "data/raw/squad.jsonl"):
    """
    Download SQuAD v1.1 and convert to JSONL format for QG.
    
    Args:
        output_path: Path to save JSONL output
    """
    print("Loading SQuAD v1.1 dataset...")
    dataset = load_dataset("squad", trust_remote_code=True)
    
    all_samples = []
    
    # Process each split
    for split_name in ["train", "validation"]:
        split_data = dataset[split_name]
        print(f"Processing {split_name} split: {len(split_data)} samples")
        
        for item in tqdm(split_data, desc=f"Converting {split_name}"):
            # Extract answer text (first answer)
            answer_text = item["answers"]["text"][0] if item["answers"]["text"] else ""
            answer_start = item["answers"]["answer_start"][0] if item["answers"]["answer_start"] else 0
            
            sample = {
                "id": item["id"],
                "context": item["context"],
                "question": item["question"],
                "answer": answer_text,
                "answer_start": answer_start,
                "split": "train" if split_name == "train" else "dev"
            }
            all_samples.append(sample)
    
    # Save to JSONL
    ensure_dir(os.path.dirname(output_path))
    save_jsonl(all_samples, output_path)
    
    print(f"\n✓ Saved {len(all_samples)} samples to {output_path}")
    print(f"  Train: {sum(1 for s in all_samples if s['split'] == 'train')}")
    print(f"  Dev: {sum(1 for s in all_samples if s['split'] == 'dev')}")


def main():
    parser = argparse.ArgumentParser(description="Fetch SQuAD dataset for QG")
    parser.add_argument(
        "--out",
        type=str,
        default="data/raw/squad.jsonl",
        help="Output JSONL path"
    )
    args = parser.parse_args()
    
    fetch_squad(args.out)


if __name__ == "__main__":
    main()

