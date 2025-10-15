#!/usr/bin/env python
"""
Comprehensive validation script for QG experiment.
Tests all components and verifies outputs.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(__file__))

from pathlib import Path


def print_section(title):
    """Print section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def check_file_exists(path, description):
    """Check if file exists and show size."""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    if exists and os.path.isfile(path):
        size = os.path.getsize(path)
        if size > 1e9:
            size_str = f"{size/1e9:.2f} GB"
        elif size > 1e6:
            size_str = f"{size/1e6:.2f} MB"
        elif size > 1e3:
            size_str = f"{size/1e3:.2f} KB"
        else:
            size_str = f"{size} B"
        print(f"{status} {description}: {size_str}")
    elif exists and os.path.isdir(path):
        print(f"{status} {description}: (directory)")
    else:
        print(f"{status} {description}: MISSING")
    return exists


def validate_json_file(path, expected_keys=None):
    """Validate JSON file structure."""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        if expected_keys:
            missing = [k for k in expected_keys if k not in data]
            if missing:
                print(f"    ⚠️  Missing keys: {missing}")
                return False
        print(f"    ✓ Valid JSON with {len(data)} keys")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def validate_jsonl_file(path, min_samples=0):
    """Validate JSONL file."""
    try:
        with open(path, 'r') as f:
            samples = [json.loads(line) for line in f]
        if len(samples) < min_samples:
            print(f"    ⚠️  Only {len(samples)} samples (expected >= {min_samples})")
            return False
        print(f"    ✓ {len(samples)} samples")
        if samples:
            print(f"    ✓ Fields: {list(samples[0].keys())[:5]}...")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "     🔍 COMPREHENSIVE QG EXPERIMENT VALIDATION 🔍".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    total_checks = 0
    passed_checks = 0
    
    # 1. Check source code
    print_section("1. SOURCE CODE")
    files_to_check = [
        ("src/data/fetch_squad.py", "SQuAD fetcher"),
        ("src/data/fetch_race.py", "RACE fetcher"),
        ("src/data/make_subset.py", "Subset creator"),
        ("src/data/preprocess.py", "Preprocessor"),
        ("src/models/baseline_llm.py", "Baseline model"),
        ("src/models/controlled_qg.py", "Controlled model"),
        ("src/train/finetune_baseline.py", "Baseline trainer"),
        ("src/train/finetune_controlled.py", "Controlled trainer"),
        ("src/generate/run_generate.py", "Generator"),
        ("src/eval/compute_bleu_rouge.py", "BLEU/ROUGE eval"),
        ("src/eval/qa_answerability.py", "QA eval"),
        ("src/eval/human_pack.py", "Human eval pack"),
        ("src/eval/aggregate.py", "Aggregator"),
    ]
    
    for path, desc in files_to_check:
        total_checks += 1
        if check_file_exists(path, desc):
            passed_checks += 1
    
    # 2. Check configurations
    print_section("2. CONFIGURATION FILES")
    config_files = [
        ("src/config/exp_squad_small.yaml", "SQuAD baseline config"),
        ("src/config/exp_squad_small_controlled.yaml", "SQuAD controlled config"),
        ("src/config/exp_race_small.yaml", "RACE baseline config"),
        ("src/config/exp_race_small_controlled.yaml", "RACE controlled config"),
        ("src/config/exp_multi_model.yaml", "Multi-model config"),
    ]
    
    for path, desc in config_files:
        total_checks += 1
        if check_file_exists(path, desc):
            passed_checks += 1
    
    # 3. Check data files
    print_section("3. DATA FILES")
    data_files = [
        ("data/raw/squad.jsonl", "SQuAD raw", 90000),
        ("data/interim/squad_small.jsonl", "SQuAD subset", 1000),
        ("data/processed/squad_small.qg_labeled.jsonl", "SQuAD labeled", 1000),
    ]
    
    for path, desc, *min_samples in data_files:
        total_checks += 1
        if check_file_exists(path, desc):
            if min_samples:
                validate_jsonl_file(path, min_samples[0])
            passed_checks += 1
    
    # 4. Check trained models
    print_section("4. TRAINED MODELS")
    model_files = [
        ("outputs/baseline_t5_small_squad_small/model.safetensors", "Baseline model weights"),
        ("outputs/baseline_t5_small_squad_small/config.json", "Baseline config"),
        ("outputs/controlled_t5_small_squad_small/model.safetensors", "Controlled model weights"),
        ("outputs/controlled_t5_small_squad_small/config.json", "Controlled config"),
    ]
    
    for path, desc in model_files:
        total_checks += 1
        if check_file_exists(path, desc):
            passed_checks += 1
    
    # 5. Check predictions
    print_section("5. GENERATED PREDICTIONS")
    pred_files = [
        ("reports/tables/preds_baseline_squad.jsonl", "Baseline predictions", 200),
        ("reports/tables/preds_controlled_squad.jsonl", "Controlled predictions", 200),
    ]
    
    for path, desc, min_samples in pred_files:
        total_checks += 1
        if check_file_exists(path, desc):
            validate_jsonl_file(path, min_samples)
            passed_checks += 1
    
    # 6. Check metrics
    print_section("6. EVALUATION METRICS")
    metric_files = [
        ("reports/tables/metrics_baseline_squad.json", "Baseline BLEU/ROUGE", ['bleu', 'rouge1']),
        ("reports/tables/metrics_controlled_squad.json", "Controlled BLEU/ROUGE", ['bleu', 'rouge1']),
        ("reports/tables/qa_baseline_squad.json", "Baseline QA metrics", ['em_mean', 'f1_mean']),
        ("reports/tables/qa_controlled_squad.json", "Controlled QA metrics", ['em_mean', 'f1_mean']),
    ]
    
    for path, desc, *keys in metric_files:
        total_checks += 1
        if check_file_exists(path, desc):
            if keys:
                validate_json_file(path, keys[0])
            passed_checks += 1
    
    # 7. Check results
    print_section("7. FINAL RESULTS")
    result_files = [
        ("reports/tables/comparison_squad.csv", "Comparison table"),
        ("reports/figures/comparison_squad.png", "Comparison plot"),
        ("paper/results_squad.tex", "LaTeX output"),
        ("reports/tables/human_eval_pack_squad.xlsx", "Human eval pack"),
    ]
    
    for path, desc in result_files:
        total_checks += 1
        if check_file_exists(path, desc):
            passed_checks += 1
    
    # 8. Check documentation
    print_section("8. DOCUMENTATION")
    doc_files = [
        ("README.md", "Main README"),
        ("QUICK_REFERENCE.md", "Quick reference"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
        ("PLAN_CHECKLIST.md", "Plan checklist"),
        ("EXPERIMENT_COMPLETE.md", "Experiment complete doc"),
        ("paper/README.md", "Paper README"),
    ]
    
    for path, desc in doc_files:
        total_checks += 1
        if check_file_exists(path, desc):
            passed_checks += 1
    
    # 9. Test imports
    print_section("9. PYTHON IMPORTS")
    test_imports = [
        ("src.utils.seed", "Seed utilities"),
        ("src.utils.metrics", "Metrics utilities"),
        ("src.utils.io_utils", "I/O utilities"),
        ("src.utils.analysis", "Analysis utilities"),
        ("src.models.baseline_llm", "Baseline model"),
        ("src.models.controlled_qg", "Controlled model"),
    ]
    
    for module_name, desc in test_imports:
        total_checks += 1
        try:
            __import__(module_name)
            print(f"✅ {desc}: Import successful")
            passed_checks += 1
        except Exception as e:
            print(f"❌ {desc}: {e}")
    
    # Final summary
    print_section("VALIDATION SUMMARY")
    print(f"\n  Total Checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    print(f"  Failed: {total_checks - passed_checks}")
    print(f"  Success Rate: {100 * passed_checks / total_checks:.1f}%")
    
    if passed_checks == total_checks:
        print("\n  🎉 ALL CHECKS PASSED! 🎉")
        print("  ✅ Your QG experiment is fully operational!")
    else:
        print(f"\n  ⚠️  {total_checks - passed_checks} checks failed")
        print("  Please review the errors above")
    
    print("\n" + "="*60 + "\n")
    
    return passed_checks == total_checks


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

