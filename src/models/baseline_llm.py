"""
Baseline LLM wrapper for Question Generation (T5, BART, GPT-2).
"""

import torch
from typing import Dict, List, Optional
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoTokenizer,
    T5ForConditionalGeneration,
    BartForConditionalGeneration,
    GPT2LMHeadModel
)


class BaselineQGModel:
    """
    Wrapper for baseline Question Generation models.
    Supports T5, BART (seq2seq), and GPT-2 (causal LM).
    """
    
    def __init__(
        self,
        model_name: str = "t5-small",
        model_type: str = "t5",
        device: str = None
    ):
        """
        Initialize model and tokenizer.
        
        Args:
            model_name: Hugging Face model name/path
            model_type: Model type ('t5', 'bart', or 'gpt2')
            device: Device to load model on (auto-detect if None)
        """
        self.model_name = model_name
        self.model_type = model_type.lower()
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"Loading {self.model_type} model: {model_name}")
        print(f"Device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model based on type
        if self.model_type == "t5":
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        elif self.model_type == "bart":
            self.model = BartForConditionalGeneration.from_pretrained(model_name)
        elif self.model_type == "gpt2":
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            # GPT-2 doesn't have pad token by default
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        else:
            # Generic loading
            try:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            except:
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        self.model.to(self.device)
        self.model.eval()
        
        self.is_causal = self.model_type == "gpt2"
    
    def format_input(self, context: str, answer: str, **kwargs) -> str:
        """
        Format input text for the model.
        
        Args:
            context: Context passage
            answer: Answer span
            
        Returns:
            Formatted input string
        """
        if self.model_type in ["t5", "bart"]:
            # Seq2seq format
            return f"context: {context} answer: {answer}"
        elif self.model_type == "gpt2":
            # Causal LM format
            return f"Context: {context}\nAnswer: {answer}\nQuestion:"
        else:
            # Default format
            return f"context: {context} answer: {answer}"
    
    def tokenize_input(
        self,
        input_text: str,
        max_length: int = 512,
        **kwargs
    ) -> Dict:
        """
        Tokenize input text.
        
        Args:
            input_text: Formatted input text
            max_length: Maximum sequence length
            
        Returns:
            Dictionary with input_ids, attention_mask
        """
        encoding = self.tokenizer(
            input_text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {k: v.to(self.device) for k, v in encoding.items()}
    
    def tokenize_target(
        self,
        target_text: str,
        max_length: int = 64,
        **kwargs
    ) -> Dict:
        """
        Tokenize target text (for training).
        
        Args:
            target_text: Target question text
            max_length: Maximum sequence length
            
        Returns:
            Dictionary with labels
        """
        encoding = self.tokenizer(
            target_text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        labels = encoding["input_ids"]
        # Replace padding token id with -100 for loss computation
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {"labels": labels.to(self.device)}
    
    def generate(
        self,
        context: str,
        answer: str,
        max_length: int = 64,
        num_beams: int = 5,
        no_repeat_ngram_size: int = 2,
        **gen_kwargs
    ) -> str:
        """
        Generate question given context and answer.
        
        Args:
            context: Context passage
            answer: Answer span
            max_length: Maximum generation length
            num_beams: Number of beams for beam search
            no_repeat_ngram_size: Prevent n-gram repetition
            **gen_kwargs: Additional generation arguments
            
        Returns:
            Generated question text
        """
        # Format and tokenize input
        input_text = self.format_input(context, answer)
        inputs = self.tokenize_input(input_text, max_length=512)
        
        # Generate
        with torch.no_grad():
            if self.is_causal:
                # For causal models, generate continuation
                outputs = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=max_length,
                    num_beams=num_beams,
                    no_repeat_ngram_size=no_repeat_ngram_size,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **gen_kwargs
                )
                # Decode only the new tokens (skip input)
                input_length = inputs["input_ids"].shape[1]
                generated_ids = outputs[:, input_length:]
            else:
                # For seq2seq models
                outputs = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=max_length,
                    num_beams=num_beams,
                    no_repeat_ngram_size=no_repeat_ngram_size,
                    **gen_kwargs
                )
                generated_ids = outputs
        
        # Decode
        question = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        return question.strip()
    
    def save_pretrained(self, output_dir: str):
        """
        Save model and tokenizer.
        
        Args:
            output_dir: Output directory
        """
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"Model saved to {output_dir}")
    
    def from_pretrained(self, model_path: str):
        """
        Load model from checkpoint.
        
        Args:
            model_path: Path to saved model
        """
        print(f"Loading model from {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        if self.is_causal:
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        
        self.model.to(self.device)
        self.model.eval()

