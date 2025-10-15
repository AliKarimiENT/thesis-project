"""
Difficulty-controlled Question Generation model.
Extends baseline with difficulty tokens (<easy>, <medium>, <hard>).
"""

import torch
from typing import Dict, Optional
from src.models.baseline_llm import BaselineQGModel


class ControlledQGModel(BaselineQGModel):
    """
    Controlled QG model with difficulty conditioning.
    Prepends difficulty tokens to input.
    """
    
    def __init__(
        self,
        model_name: str = "t5-small",
        model_type: str = "t5",
        device: str = None,
        add_difficulty_tokens: bool = True
    ):
        """
        Initialize controlled QG model.
        
        Args:
            model_name: Hugging Face model name/path
            model_type: Model type ('t5', 'bart', or 'gpt2')
            device: Device to load model on
            add_difficulty_tokens: Whether to add special difficulty tokens to vocabulary
        """
        super().__init__(model_name, model_type, device)
        
        self.difficulty_tokens = ["<easy>", "<medium>", "<hard>"]
        
        if add_difficulty_tokens:
            # Add special tokens to tokenizer
            num_added = self.tokenizer.add_special_tokens({
                'additional_special_tokens': self.difficulty_tokens
            })
            
            if num_added > 0:
                print(f"Added {num_added} difficulty tokens: {self.difficulty_tokens}")
                # Resize model embeddings to accommodate new tokens
                self.model.resize_token_embeddings(len(self.tokenizer))
            else:
                print("Difficulty tokens already in vocabulary")
    
    def format_input(
        self,
        context: str,
        answer: str,
        difficulty: str = "medium",
        **kwargs
    ) -> str:
        """
        Format input with difficulty token prepended.
        
        Args:
            context: Context passage
            answer: Answer span
            difficulty: Difficulty level ('easy', 'medium', or 'hard')
            
        Returns:
            Formatted input string with difficulty token
        """
        # Map difficulty to token
        difficulty_token = f"<{difficulty.lower()}>"
        
        if self.model_type in ["t5", "bart"]:
            # Seq2seq format with difficulty prepended
            return f"difficulty: {difficulty_token} context: {context} answer: {answer}"
        elif self.model_type == "gpt2":
            # Causal LM format
            return f"Difficulty: {difficulty_token}\nContext: {context}\nAnswer: {answer}\nQuestion:"
        else:
            # Default format
            return f"difficulty: {difficulty_token} context: {context} answer: {answer}"
    
    def generate(
        self,
        context: str,
        answer: str,
        difficulty: str = "medium",
        max_length: int = 64,
        num_beams: int = 5,
        no_repeat_ngram_size: int = 2,
        **gen_kwargs
    ) -> str:
        """
        Generate question with difficulty conditioning.
        
        Args:
            context: Context passage
            answer: Answer span
            difficulty: Target difficulty level
            max_length: Maximum generation length
            num_beams: Number of beams for beam search
            no_repeat_ngram_size: Prevent n-gram repetition
            **gen_kwargs: Additional generation arguments
            
        Returns:
            Generated question text
        """
        # Format input with difficulty token
        input_text = self.format_input(context, answer, difficulty=difficulty)
        inputs = self.tokenize_input(input_text, max_length=512)
        
        # Generate
        with torch.no_grad():
            if self.is_causal:
                # For causal models
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
                # Decode only new tokens
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
    
    def get_difficulty_token_ids(self) -> Dict[str, int]:
        """
        Get token IDs for difficulty tokens.
        
        Returns:
            Dictionary mapping difficulty levels to token IDs
        """
        token_ids = {}
        for diff in ["easy", "medium", "hard"]:
            token = f"<{diff}>"
            token_ids[diff] = self.tokenizer.convert_tokens_to_ids(token)
        return token_ids

