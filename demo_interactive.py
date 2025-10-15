#!/usr/bin/env python
"""
Interactive demo for Question Generation models.
Try out your trained models with custom inputs!
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.models.baseline_llm import BaselineQGModel
from src.models.controlled_qg import ControlledQGModel


def print_header():
    print("\n" + "="*60)
    print("🎓 QUESTION GENERATION - INTERACTIVE DEMO")
    print("="*60)
    print("\nThis demo lets you generate questions from custom inputs")
    print("using your trained models.")
    print()


def demo_baseline():
    """Demo baseline model."""
    print("\n" + "-"*60)
    print("📝 BASELINE MODEL DEMO")
    print("-"*60)
    
    # Load model
    print("\nLoading baseline model...")
    model = BaselineQGModel(
        model_name="outputs/baseline_t5_small_squad_small",
        model_type="t5"
    )
    model.from_pretrained("outputs/baseline_t5_small_squad_small")
    
    # Example 1
    print("\n✨ Example 1:")
    context1 = "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel, whose company designed and built the tower."
    answer1 = "Gustave Eiffel"
    
    print(f"Context: {context1}")
    print(f"Answer: {answer1}")
    
    question1 = model.generate(context1, answer1, num_beams=5, max_length=64)
    print(f"Generated Question: {question1}")
    
    # Example 2
    print("\n✨ Example 2:")
    context2 = "Python is a high-level, interpreted programming language. It was created by Guido van Rossum and first released in 1991."
    answer2 = "1991"
    
    print(f"Context: {context2}")
    print(f"Answer: {answer2}")
    
    question2 = model.generate(context2, answer2, num_beams=5, max_length=64)
    print(f"Generated Question: {question2}")
    
    return model


def demo_controlled():
    """Demo controlled model."""
    print("\n" + "-"*60)
    print("🎯 CONTROLLED MODEL DEMO")
    print("-"*60)
    
    # Load model
    print("\nLoading controlled model...")
    model = ControlledQGModel(
        model_name="outputs/controlled_t5_small_squad_small",
        model_type="t5"
    )
    model.from_pretrained("outputs/controlled_t5_small_squad_small")
    
    context = "Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed."
    answer = "artificial intelligence"
    
    print(f"\nContext: {context}")
    print(f"Answer: {answer}")
    print()
    
    # Generate at each difficulty level
    for difficulty in ['easy', 'medium', 'hard']:
        question = model.generate(
            context, answer,
            difficulty=difficulty,
            num_beams=5,
            max_length=64
        )
        print(f"  {difficulty.upper():6s}: {question}")
    
    return model


def interactive_mode(baseline_model, controlled_model):
    """Interactive mode for custom inputs."""
    print("\n" + "="*60)
    print("💬 INTERACTIVE MODE")
    print("="*60)
    print("\nEnter your own context and answer to generate questions!")
    print("Type 'quit' to exit.\n")
    
    while True:
        # Get context
        context = input("Context (or 'quit'): ").strip()
        if context.lower() == 'quit':
            break
        
        if not context:
            print("⚠️  Please enter a context.")
            continue
        
        # Get answer
        answer = input("Answer: ").strip()
        if not answer:
            print("⚠️  Please enter an answer.")
            continue
        
        print("\n" + "-"*60)
        print("Generating questions...")
        print("-"*60)
        
        # Generate with baseline
        try:
            baseline_q = baseline_model.generate(context, answer)
            print(f"\n📝 Baseline:   {baseline_q}")
        except Exception as e:
            print(f"\n⚠️  Baseline error: {e}")
        
        # Generate with controlled at each difficulty
        try:
            print(f"\n🎯 Controlled:")
            for diff in ['easy', 'medium', 'hard']:
                controlled_q = controlled_model.generate(context, answer, difficulty=diff)
                print(f"   {diff.capitalize():6s}: {controlled_q}")
        except Exception as e:
            print(f"\n⚠️  Controlled error: {e}")
        
        print("\n" + "-"*60 + "\n")


def main():
    print_header()
    
    # Check if models exist
    if not os.path.exists("outputs/baseline_t5_small_squad_small"):
        print("⚠️  Baseline model not found!")
        print("   Please train the model first:")
        print("   python -m src.train.finetune_baseline --cfg src/config/exp_squad_small.yaml")
        return
    
    if not os.path.exists("outputs/controlled_t5_small_squad_small"):
        print("⚠️  Controlled model not found!")
        print("   Please train the model first:")
        print("   python -m src.train.finetune_controlled --cfg src/config/exp_squad_small_controlled.yaml")
        return
    
    # Run demos
    baseline_model = demo_baseline()
    controlled_model = demo_controlled()
    
    # Interactive mode
    try:
        interactive_mode(baseline_model, controlled_model)
    except KeyboardInterrupt:
        print("\n\n👋 Exiting interactive mode...")
    
    print("\n✅ Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

