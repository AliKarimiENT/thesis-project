# QG Experiment Quick Reference

Quick commands for common tasks in the QG experiment pipeline.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or use conda
conda env create -f environment.yml
conda activate qg-exp
```

## Data Preparation

### SQuAD Dataset

```bash
# Fetch full dataset
python -m src.data.fetch_squad --out data/raw/squad.jsonl

# Create small subset
python -m src.data.make_subset \
  --in data/raw/squad.jsonl \
  --out data/interim/squad_small.jsonl \
  --train 1000 --dev 200 --test 200 --seed 42

# Add difficulty labels
python -m src.data.preprocess \
  --in data/interim/squad_small.jsonl \
  --out data/processed/squad_small.qg_labeled.jsonl
```

### RACE Dataset

```bash
# Fetch full dataset
python -m src.data.fetch_race --out data/raw/race.jsonl

# Create small subset
python -m src.data.make_subset \
  --in data/raw/race.jsonl \
  --out data/interim/race_small.jsonl \
  --train 1000 --dev 200 --test 200 --seed 42

# Add difficulty labels
python -m src.data.preprocess \
  --in data/interim/race_small.jsonl \
  --out data/processed/race_small.qg_labeled.jsonl
```

## Training

### Baseline Models

```bash
# T5-small baseline on SQuAD
python -m src.train.finetune_baseline --cfg src/config/exp_squad_small.yaml

# T5-small baseline on RACE
python -m src.train.finetune_baseline --cfg src/config/exp_race_small.yaml
```

### Controlled Models

```bash
# T5-small controlled on SQuAD
python -m src.train.finetune_controlled --cfg src/config/exp_squad_small_controlled.yaml

# T5-small controlled on RACE
python -m src.train.finetune_controlled --cfg src/config/exp_race_small_controlled.yaml
```

### Custom Models

Edit config file to change model:

```yaml
model_name: facebook/bart-base  # or gpt2, t5-base, etc.
model_type: bart  # or gpt2, t5
```

## Generation

### Basic Generation

```bash
# Baseline model
python -m src.generate.run_generate \
  --model outputs/baseline_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --out reports/tables/preds_baseline.jsonl

# Controlled model (uses original difficulty labels)
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --out reports/tables/preds_controlled.jsonl
```

### Controlled Generation with Override

```bash
# Force all questions to be "hard"
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --difficulty hard \
  --out reports/tables/preds_hard.jsonl

# Force all questions to be "easy"
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --difficulty easy \
  --out reports/tables/preds_easy.jsonl
```

## Evaluation

### Automatic Metrics (BLEU/ROUGE)

```bash
python -m src.eval.compute_bleu_rouge \
  --pred reports/tables/preds_baseline.jsonl \
  --out reports/tables/metrics_baseline.json
```

### QA Answerability

```bash
python -m src.eval.qa_answerability \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --pred reports/tables/preds_baseline.jsonl \
  --out reports/tables/qa_baseline.json
```

### Human Evaluation Pack

```bash
python -m src.eval.human_pack \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --predA reports/tables/preds_baseline.jsonl \
  --predB reports/tables/preds_controlled.jsonl \
  --n 120 \
  --out reports/tables/human_eval_pack.xlsx \
  --seed 314
```

### Aggregate Results

```bash
# Without human evaluation
python -m src.eval.aggregate \
  --metricsA reports/tables/metrics_baseline.json \
  --metricsB reports/tables/metrics_controlled.json \
  --qaA reports/tables/qa_baseline.json \
  --qaB reports/tables/qa_controlled.json \
  --out_csv reports/tables/comparison.csv \
  --out_fig reports/figures/comparison.png \
  --emit_latex paper/results.tex

# With human evaluation (after completing XLSX)
python -m src.eval.aggregate \
  --metricsA reports/tables/metrics_baseline.json \
  --metricsB reports/tables/metrics_controlled.json \
  --qaA reports/tables/qa_baseline.json \
  --qaB reports/tables/qa_controlled.json \
  --human reports/tables/human_eval_results.xlsx \
  --out_csv reports/tables/comparison.csv \
  --out_fig reports/figures/comparison.png \
  --emit_latex paper/results.tex
```

## Automated Pipelines

### Full Pipeline

```bash
# Edit the script to choose dataset (squad or race)
# Then run:
./run_full_pipeline.sh
```

### Smoke Test

```bash
# Quick test with 10 samples
./smoke_test.sh
```

## Common Workflows

### Experiment 1: Compare T5, BART, GPT-2

```bash
# Train all three architectures
for model in t5-small facebook/bart-base gpt2; do
  # Update config with model
  # Train baseline
  # Train controlled
  # Generate
  # Evaluate
done
```

### Experiment 2: Difficulty Ablation

```bash
# Generate questions at each difficulty level
for diff in easy medium hard; do
  python -m src.generate.run_generate \
    --model outputs/controlled_t5_small_squad_small \
    --dataset data/processed/squad_small.qg_labeled.jsonl \
    --split test \
    --difficulty $diff \
    --out reports/tables/preds_${diff}.jsonl
  
  # Evaluate
  python -m src.eval.compute_bleu_rouge \
    --pred reports/tables/preds_${diff}.jsonl \
    --out reports/tables/metrics_${diff}.json
done
```

### Experiment 3: Cross-Dataset Evaluation

```bash
# Train on SQuAD, test on RACE
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/race_small.qg_labeled.jsonl \
  --split test \
  --out reports/tables/preds_squad_on_race.jsonl
```

## Debugging

### Check Data

```bash
# Inspect JSONL file
python -c "
from src.utils.io_utils import load_jsonl
data = load_jsonl('data/processed/squad_small.qg_labeled.jsonl')
print(f'Total samples: {len(data)}')
print(f'Fields: {list(data[0].keys())}')
print(f'Example: {data[0]}')
"
```

### Check Model

```bash
# Test model loading
python -c "
from src.models.baseline_llm import BaselineQGModel
model = BaselineQGModel('t5-small', 't5')
q = model.generate('Paris is the capital of France.', 'Paris')
print(f'Generated: {q}')
"
```

### Check Config

```bash
# Load and print config
python -c "
from src.utils.io_utils import load_yaml
import json
config = load_yaml('src/config/exp_squad_small.yaml')
print(json.dumps(config, indent=2))
"
```

## File Locations

### Input Data
- Raw: `data/raw/*.jsonl`
- Interim: `data/interim/*_small.jsonl`
- Processed: `data/processed/*_labeled.jsonl`

### Models
- Trained models: `outputs/*/`
- Checkpoints: `outputs/*/checkpoint-*/`

### Results
- Predictions: `reports/tables/preds_*.jsonl`
- Metrics: `reports/tables/metrics_*.json`
- QA Metrics: `reports/tables/qa_*.json`
- Human Eval: `reports/tables/human_eval_*.xlsx`
- Plots: `reports/figures/*.png`
- LaTeX: `paper/results*.tex`

## Configuration Files

- Baseline SQuAD: `src/config/exp_squad_small.yaml`
- Controlled SQuAD: `src/config/exp_squad_small_controlled.yaml`
- Baseline RACE: `src/config/exp_race_small.yaml`
- Controlled RACE: `src/config/exp_race_small_controlled.yaml`
- Multi-model: `src/config/exp_multi_model.yaml`

## Key Parameters

### Training
- `train_batch_size`: Batch size per device (default: 8)
- `num_train_epochs`: Number of epochs (default: 3)
- `learning_rate`: Learning rate (default: 5e-5)
- `fp16`: Use mixed precision (default: true)

### Generation
- `num_beams`: Beam search width (default: 5)
- `max_length`: Max tokens to generate (default: 64)
- `no_repeat_ngram_size`: Prevent n-gram repetition (default: 2)

### Data
- `max_source_length`: Max input tokens (default: 512)
- `max_target_length`: Max output tokens (default: 64)

## Tips

1. **Start small**: Use smoke test first
2. **Monitor GPU**: Use `nvidia-smi` to check usage
3. **Check logs**: Training logs in `outputs/*/`
4. **Save often**: Models auto-save every 500 steps
5. **Use fp16**: Speeds up training on GPU
6. **Batch accumulation**: If OOM, increase `gradient_accumulation_steps`

