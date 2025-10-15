#!/bin/bash
# Full pipeline for QG experiment: Data preparation → Training → Evaluation
# This script demonstrates the complete workflow from raw data to paper-ready results

set -e  # Exit on error

echo "=========================================="
echo "QG Experiment Full Pipeline"
echo "=========================================="

# Configuration
DATASET="squad"  # Change to "race" for RACE dataset
SEED=42

echo ""
echo "Step 1: Data Fetching"
echo "=========================================="

if [ "$DATASET" = "squad" ]; then
    python -m src.data.fetch_squad --out data/raw/squad.jsonl
    RAW_FILE="data/raw/squad.jsonl"
    INTERIM_FILE="data/interim/squad_small.jsonl"
    PROCESSED_FILE="data/processed/squad_small.qg_labeled.jsonl"
    CONFIG_BASELINE="src/config/exp_squad_small.yaml"
    CONFIG_CONTROLLED="src/config/exp_squad_small_controlled.yaml"
    DATASET_NAME="squad"
else
    python -m src.data.fetch_race --out data/raw/race.jsonl
    RAW_FILE="data/raw/race.jsonl"
    INTERIM_FILE="data/interim/race_small.jsonl"
    PROCESSED_FILE="data/processed/race_small.qg_labeled.jsonl"
    CONFIG_BASELINE="src/config/exp_race_small.yaml"
    CONFIG_CONTROLLED="src/config/exp_race_small_controlled.yaml"
    DATASET_NAME="race"
fi

echo ""
echo "Step 2: Create Small Subset"
echo "=========================================="
python -m src.data.make_subset \
    --in "$RAW_FILE" \
    --out "$INTERIM_FILE" \
    --train 1000 \
    --dev 200 \
    --test 200 \
    --seed "$SEED"

echo ""
echo "Step 3: Add Difficulty Labels"
echo "=========================================="
python -m src.data.preprocess \
    --in "$INTERIM_FILE" \
    --out "$PROCESSED_FILE"

echo ""
echo "Step 4: Train Baseline Model"
echo "=========================================="
python -m src.train.finetune_baseline --cfg "$CONFIG_BASELINE"

echo ""
echo "Step 5: Train Controlled Model"
echo "=========================================="
python -m src.train.finetune_controlled --cfg "$CONFIG_CONTROLLED"

echo ""
echo "Step 6: Generate Questions - Baseline"
echo "=========================================="
python -m src.generate.run_generate \
    --model "outputs/baseline_t5_small_${DATASET_NAME}_small" \
    --dataset "$PROCESSED_FILE" \
    --split test \
    --out "reports/tables/preds_baseline_${DATASET_NAME}.jsonl"

echo ""
echo "Step 7: Generate Questions - Controlled"
echo "=========================================="
python -m src.generate.run_generate \
    --model "outputs/controlled_t5_small_${DATASET_NAME}_small" \
    --dataset "$PROCESSED_FILE" \
    --split test \
    --out "reports/tables/preds_controlled_${DATASET_NAME}.jsonl"

echo ""
echo "Step 8: Compute BLEU/ROUGE Metrics"
echo "=========================================="
python -m src.eval.compute_bleu_rouge \
    --pred "reports/tables/preds_baseline_${DATASET_NAME}.jsonl" \
    --out "reports/tables/metrics_baseline_${DATASET_NAME}.json"

python -m src.eval.compute_bleu_rouge \
    --pred "reports/tables/preds_controlled_${DATASET_NAME}.jsonl" \
    --out "reports/tables/metrics_controlled_${DATASET_NAME}.json"

echo ""
echo "Step 9: Compute QA Answerability"
echo "=========================================="
python -m src.eval.qa_answerability \
    --dataset "$PROCESSED_FILE" \
    --pred "reports/tables/preds_baseline_${DATASET_NAME}.jsonl" \
    --out "reports/tables/qa_baseline_${DATASET_NAME}.json"

python -m src.eval.qa_answerability \
    --dataset "$PROCESSED_FILE" \
    --pred "reports/tables/preds_controlled_${DATASET_NAME}.jsonl" \
    --out "reports/tables/qa_controlled_${DATASET_NAME}.json"

echo ""
echo "Step 10: Create Human Evaluation Pack"
echo "=========================================="
python -m src.eval.human_pack \
    --dataset "$PROCESSED_FILE" \
    --predA "reports/tables/preds_baseline_${DATASET_NAME}.jsonl" \
    --predB "reports/tables/preds_controlled_${DATASET_NAME}.jsonl" \
    --n 120 \
    --out "reports/tables/human_eval_pack_${DATASET_NAME}.xlsx" \
    --seed 314

echo ""
echo "Step 11: Aggregate Results & Generate LaTeX"
echo "=========================================="
echo "Note: Human evaluation XLSX must be completed first."
echo "For now, running without human evaluation results..."

python -m src.eval.aggregate \
    --metricsA "reports/tables/metrics_baseline_${DATASET_NAME}.json" \
    --metricsB "reports/tables/metrics_controlled_${DATASET_NAME}.json" \
    --qaA "reports/tables/qa_baseline_${DATASET_NAME}.json" \
    --qaB "reports/tables/qa_controlled_${DATASET_NAME}.json" \
    --out_csv "reports/tables/comparison_${DATASET_NAME}.csv" \
    --out_fig "reports/figures/comparison_${DATASET_NAME}.png" \
    --emit_latex "paper/results_${DATASET_NAME}.tex"

echo ""
echo "=========================================="
echo "Pipeline Complete!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - Models: outputs/baseline_t5_small_${DATASET_NAME}_small/"
echo "  - Models: outputs/controlled_t5_small_${DATASET_NAME}_small/"
echo "  - Predictions: reports/tables/preds_*_${DATASET_NAME}.jsonl"
echo "  - Metrics: reports/tables/metrics_*_${DATASET_NAME}.json"
echo "  - QA Metrics: reports/tables/qa_*_${DATASET_NAME}.json"
echo "  - Human Eval Pack: reports/tables/human_eval_pack_${DATASET_NAME}.xlsx"
echo "  - Comparison CSV: reports/tables/comparison_${DATASET_NAME}.csv"
echo "  - Comparison Plot: reports/figures/comparison_${DATASET_NAME}.png"
echo "  - LaTeX Output: paper/results_${DATASET_NAME}.tex"
echo ""
echo "Next steps:"
echo "  1. Complete human evaluation in: reports/tables/human_eval_pack_${DATASET_NAME}.xlsx"
echo "  2. Re-run aggregation with --human flag"
echo "  3. Include paper/results_${DATASET_NAME}.tex in your LaTeX document"
echo ""

