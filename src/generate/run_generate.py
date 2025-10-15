"""
Generate questions using trained QG models.
"""

import argparse
import sys
import os
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.io_utils import load_jsonl, save_jsonl, ensure_dir, load_json
from src.models.baseline_llm import BaselineQGModel
from src.models.controlled_qg import ControlledQGModel


def generate_questions(
    model_path: str,
    dataset_path: str,
    output_path: str,
    split: str = "test",
    difficulty_override: str = None,
    max_length: int = 64,
    num_beams: int = 5,
    batch_size: int = 1  # Set to 1 for simplicity
):
    """
    Generate questions for a dataset split.
    
    Args:
        model_path: Path to trained model
        dataset_path: Path to dataset JSONL
        output_path: Path to save predictions
        split: Data split to generate for
        difficulty_override: Override difficulty level (for controlled models)
        max_length: Max generation length
        num_beams: Number of beams for beam search
        batch_size: Batch size for generation
    """
    print(f"Loading dataset from {dataset_path}")
    data = load_jsonl(dataset_path)
    split_data = [d for d in data if d['split'] == split]
    print(f"Found {len(split_data)} {split} samples")
    
    # Detect if model is controlled
    config_path = os.path.join(model_path, 'train_config.json')
    is_controlled = False
    model_type = 't5'
    
    if os.path.exists(config_path):
        config = load_json(config_path)
        is_controlled = config.get('use_difficulty_token', False)
        model_type = config.get('model_type', 't5')
        print(f"Loaded model config: type={model_type}, controlled={is_controlled}")
    
    # Load model
    print(f"Loading model from {model_path}")
    if is_controlled:
        model = ControlledQGModel(
            model_name=model_path,
            model_type=model_type
        )
        model.from_pretrained(model_path)
    else:
        model = BaselineQGModel(
            model_name=model_path,
            model_type=model_type
        )
        model.from_pretrained(model_path)
    
    print("Generating questions...")
    predictions = []
    
    for sample in tqdm(split_data):
        context = sample['context']
        answer = sample['answer']
        ref_question = sample['question']
        difficulty = sample.get('difficulty', 'medium')
        
        # Override difficulty if specified
        if difficulty_override:
            difficulty = difficulty_override
        
        # Generate question
        try:
            if is_controlled:
                pred_question = model.generate(
                    context=context,
                    answer=answer,
                    difficulty=difficulty,
                    max_length=max_length,
                    num_beams=num_beams
                )
            else:
                pred_question = model.generate(
                    context=context,
                    answer=answer,
                    max_length=max_length,
                    num_beams=num_beams
                )
        except Exception as e:
            print(f"Error generating for sample {sample['id']}: {e}")
            pred_question = ""
        
        predictions.append({
            'id': sample['id'],
            'context': context,
            'answer': answer,
            'ref_question': ref_question,
            'pred_question': pred_question,
            'difficulty': difficulty
        })
    
    # Save predictions
    ensure_dir(os.path.dirname(output_path))
    save_jsonl(predictions, output_path)
    
    print(f"\n✓ Saved {len(predictions)} predictions to {output_path}")
    
    # Show some examples
    print("\nExample predictions:")
    for i, pred in enumerate(predictions[:3]):
        print(f"\n--- Example {i+1} ---")
        print(f"Context: {pred['context'][:100]}...")
        print(f"Answer: {pred['answer']}")
        print(f"Reference: {pred['ref_question']}")
        print(f"Predicted: {pred['pred_question']}")
        print(f"Difficulty: {pred['difficulty']}")


def main():
    parser = argparse.ArgumentParser(description="Generate questions using trained model")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to trained model directory"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to dataset JSONL"
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output path for predictions"
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        help="Data split to generate for"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default=None,
        choices=['easy', 'medium', 'hard'],
        help="Override difficulty level (for controlled models)"
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=64,
        help="Max generation length"
    )
    parser.add_argument(
        "--num_beams",
        type=int,
        default=5,
        help="Number of beams for beam search"
    )
    
    args = parser.parse_args()
    
    generate_questions(
        model_path=args.model,
        dataset_path=args.dataset,
        output_path=args.out,
        split=args.split,
        difficulty_override=args.difficulty,
        max_length=args.max_length,
        num_beams=args.num_beams
    )


if __name__ == "__main__":
    main()

