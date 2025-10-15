"""
Fine-tune baseline QG model (without difficulty conditioning).
"""

import argparse
import sys
import os
from typing import Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import torch
from torch.utils.data import Dataset
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)

from src.utils.io_utils import load_jsonl, load_yaml, ensure_dir
from src.utils.seed import set_seed
from src.models.baseline_llm import BaselineQGModel


class QGDataset(Dataset):
    """Dataset for Question Generation."""
    
    def __init__(
        self,
        data: list,
        model: BaselineQGModel,
        max_source_length: int = 512,
        max_target_length: int = 64,
        split: str = "train"
    ):
        """
        Initialize QG dataset.
        
        Args:
            data: List of samples
            model: QG model with tokenizer
            max_source_length: Max source sequence length
            max_target_length: Max target sequence length
            split: Data split name
        """
        self.data = [d for d in data if d['split'] == split]
        self.model = model
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        
        print(f"Loaded {len(self.data)} {split} samples")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> Dict:
        sample = self.data[idx]
        
        # Format input
        input_text = self.model.format_input(
            context=sample['context'],
            answer=sample['answer']
        )
        
        # Tokenize input
        model_inputs = self.model.tokenizer(
            input_text,
            max_length=self.max_source_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Tokenize target
        labels = self.model.tokenizer(
            sample['question'],
            max_length=self.max_target_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )["input_ids"]
        
        # Replace padding with -100 for loss computation
        labels[labels == self.model.tokenizer.pad_token_id] = -100
        
        return {
            "input_ids": model_inputs["input_ids"].squeeze(),
            "attention_mask": model_inputs["attention_mask"].squeeze(),
            "labels": labels.squeeze()
        }


def train_baseline(config_path: str):
    """
    Train baseline QG model.
    
    Args:
        config_path: Path to YAML config file
    """
    # Load config
    print(f"Loading config from {config_path}")
    config = load_yaml(config_path)
    
    # Set seed
    set_seed(config['seed'])
    
    # Load data
    print(f"Loading dataset from {config['dataset_path']}")
    data = load_jsonl(config['dataset_path'])
    
    # Initialize model
    model = BaselineQGModel(
        model_name=config['model_name'],
        model_type=config['model_type']
    )
    
    # Create datasets
    train_dataset = QGDataset(
        data=data,
        model=model,
        max_source_length=config['max_source_length'],
        max_target_length=config['max_target_length'],
        split='train'
    )
    
    eval_dataset = QGDataset(
        data=data,
        model=model,
        max_source_length=config['max_source_length'],
        max_target_length=config['max_target_length'],
        split='dev'
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=config['output_dir'],
        num_train_epochs=config['num_train_epochs'],
        per_device_train_batch_size=config['train_batch_size'],
        per_device_eval_batch_size=config['eval_batch_size'],
        gradient_accumulation_steps=config['gradient_accumulation_steps'],
        learning_rate=config['learning_rate'],
        warmup_ratio=config['warmup_ratio'],
        weight_decay=config.get('weight_decay', 0.01),
        logging_steps=config.get('logging_steps', 100),
        save_steps=config['save_steps'],
        eval_steps=config['eval_steps'],
        evaluation_strategy="steps",
        save_strategy="steps",
        save_total_limit=config.get('save_total_limit', 2),
        load_best_model_at_end=config.get('load_best_model_at_end', True),
        metric_for_best_model=config.get('metric_for_best_model', 'eval_loss'),
        greater_is_better=config.get('greater_is_better', False),
        fp16=config.get('fp16', False),
        dataloader_num_workers=config.get('dataloader_num_workers', 4),
        report_to=["none"],  # Disable wandb/tensorboard by default
        seed=config['seed']
    )
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=model.tokenizer,
        model=model.model,
        padding=True
    )
    
    # Trainer
    trainer = Trainer(
        model=model.model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=model.tokenizer
    )
    
    # Train
    print("\n" + "="*50)
    print("Starting training...")
    print("="*50 + "\n")
    
    trainer.train()
    
    # Save final model
    print(f"\nSaving final model to {config['output_dir']}")
    model.model = trainer.model  # Update with trained model
    model.save_pretrained(config['output_dir'])
    
    # Save config
    import json
    config_save_path = os.path.join(config['output_dir'], 'train_config.json')
    with open(config_save_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✓ Training complete!")
    print(f"Model saved to: {config['output_dir']}")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune baseline QG model")
    parser.add_argument(
        "--cfg",
        type=str,
        required=True,
        help="Path to config YAML file"
    )
    args = parser.parse_args()
    
    train_baseline(args.cfg)


if __name__ == "__main__":
    main()

