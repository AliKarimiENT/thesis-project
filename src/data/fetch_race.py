"""
Fetch and prepare RACE dataset for Question Generation.
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datasets import load_dataset
from src.utils.io_utils import save_jsonl, ensure_dir
from tqdm import tqdm


def fetch_race(output_path: str = "data/raw/race.jsonl"):
    """
    Download RACE dataset and convert to JSONL format for QG.
    RACE is a multiple-choice reading comprehension dataset.
    We extract the correct answer option as the answer text.
    
    Args:
        output_path: Path to save JSONL output
    """
    print("Loading RACE dataset...")
    try:
        dataset = load_dataset("race", "all", trust_remote_code=True)
    except Exception as e:
        print(f"Error loading RACE dataset: {e}")
        print("Trying alternative loading method...")
        dataset = load_dataset("ehovy/race", "all", trust_remote_code=True)
    
    all_samples = []
    
    # Process each split
    for split_name in ["train", "validation", "test"]:
        if split_name not in dataset:
            print(f"Warning: {split_name} split not found in dataset")
            continue
            
        split_data = dataset[split_name]
        print(f"Processing {split_name} split: {len(split_data)} samples")
        
        for idx, item in enumerate(tqdm(split_data, desc=f"Converting {split_name}")):
            # RACE has 4 options (A, B, C, D) and an answer key
            answer_idx = ord(item["answer"]) - ord('A')  # Convert 'A' -> 0, 'B' -> 1, etc.
            
            # Get the correct answer text
            if 0 <= answer_idx < len(item["options"]):
                answer_text = item["options"][answer_idx]
            else:
                answer_text = item["options"][0]  # Fallback
            
            # Create unique ID
            sample_id = f"race_{split_name}_{idx}"
            
            sample = {
                "id": sample_id,
                "context": item["article"],
                "question": item["question"],
                "answer": answer_text,
                "answer_start": -1,  # Not available in RACE
                "options": item["options"],
                "correct_option": item["answer"],
                "split": "train" if split_name == "train" else ("dev" if split_name == "validation" else "test")
            }
            all_samples.append(sample)
    
    # Save to JSONL
    ensure_dir(os.path.dirname(output_path))
    save_jsonl(all_samples, output_path)
    
    print(f"\n✓ Saved {len(all_samples)} samples to {output_path}")
    for split_name in ["train", "dev", "test"]:
        count = sum(1 for s in all_samples if s['split'] == split_name)
        if count > 0:
            print(f"  {split_name.capitalize()}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Fetch RACE dataset for QG")
    parser.add_argument(
        "--out",
        type=str,
        default="data/raw/race.jsonl",
        help="Output JSONL path"
    )
    args = parser.parse_args()
    
    fetch_race(args.out)


if __name__ == "__main__":
    main()

