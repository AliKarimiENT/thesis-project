#!/bin/bash
# Quick smoke test with tiny dataset (10 samples) for validation
# Use this to verify the pipeline works before running full experiments

set -e  # Exit on error

echo "=========================================="
echo "QG Experiment Smoke Test (10 samples)"
echo "=========================================="

SEED=42

echo ""
echo "Step 1: Fetch SQuAD"
echo "=========================================="
python -m src.data.fetch_squad --out data/raw/squad.jsonl

echo ""
echo "Step 2: Create Tiny Subset (10 samples)"
echo "=========================================="
python -m src.data.make_subset \
    --in data/raw/squad.jsonl \
    --out data/interim/squad_tiny.jsonl \
    --train 10 \
    --dev 5 \
    --test 5 \
    --seed "$SEED"

echo ""
echo "Step 3: Add Difficulty Labels"
echo "=========================================="
python -m src.data.preprocess \
    --in data/interim/squad_tiny.jsonl \
    --out data/processed/squad_tiny.qg_labeled.jsonl

echo ""
echo "Step 4: Test Model Loading (Baseline)"
echo "=========================================="
python -c "
from src.models.baseline_llm import BaselineQGModel
model = BaselineQGModel(model_name='t5-small', model_type='t5')
print('✓ Baseline model loaded successfully')
question = model.generate(
    context='The Eiffel Tower is in Paris.',
    answer='Paris',
    num_beams=2,
    max_length=32
)
print(f'Generated: {question}')
"

echo ""
echo "Step 5: Test Model Loading (Controlled)"
echo "=========================================="
python -c "
from src.models.controlled_qg import ControlledQGModel
model = ControlledQGModel(model_name='t5-small', model_type='t5')
print('✓ Controlled model loaded successfully')
question = model.generate(
    context='The Eiffel Tower is in Paris.',
    answer='Paris',
    difficulty='hard',
    num_beams=2,
    max_length=32
)
print(f'Generated: {question}')
"

echo ""
echo "Step 6: Test Data Loading"
echo "=========================================="
python -c "
from src.utils.io_utils import load_jsonl
data = load_jsonl('data/processed/squad_tiny.qg_labeled.jsonl')
print(f'✓ Loaded {len(data)} samples')
print(f'Sample fields: {list(data[0].keys())}')
if 'difficulty' in data[0]:
    print(f'✓ Difficulty labels present')
    diff_dist = {}
    for d in data:
        diff = d.get('difficulty', 'unknown')
        diff_dist[diff] = diff_dist.get(diff, 0) + 1
    print(f'Distribution: {diff_dist}')
"

echo ""
echo "Step 7: Test Metrics Computation"
echo "=========================================="
python -c "
from src.utils.metrics import compute_f1, compute_exact_match
tokens1 = ['what', 'is', 'the', 'capital']
tokens2 = ['the', 'capital', 'city']
f1 = compute_f1(tokens1, tokens2)
print(f'✓ F1 score: {f1:.3f}')
em = compute_exact_match('Paris', 'paris')
print(f'✓ Exact match: {em}')
"

echo ""
echo "=========================================="
echo "Smoke Test Complete!"
echo "=========================================="
echo ""
echo "All components loaded successfully."
echo "You can now run the full pipeline with:"
echo "  ./run_full_pipeline.sh"
echo ""
echo "Or train manually:"
echo "  python -m src.train.finetune_baseline --cfg src/config/exp_squad_small.yaml"
echo ""

