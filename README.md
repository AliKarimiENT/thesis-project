# Thesis Project

A research project implementing difficulty-controlled Question Generation (QG) for educational applications.

## Project Structure

```
thesis-project/
├── data/                    # Data directory
│   ├── raw/                # Raw data files (SQuAD, RACE)
│   ├── interim/            # Subsetted data
│   └── processed/          # Preprocessed with difficulty labels
├── notebooks/              # Jupyter notebooks
│   └── sample_preprocess.ipynb
├── reports/                # Generated reports
│   ├── figures/            # Plots and visualizations
│   └── tables/             # Predictions and metrics
├── paper/                  # LaTeX output for paper
│   ├── results.tex         # Auto-generated tables/figures
│   └── README.md
├── src/                    # Source code
│   ├── config/             # Experiment configurations
│   │   ├── exp_squad_small.yaml
│   │   ├── exp_race_small.yaml
│   │   └── exp_multi_model.yaml
│   ├── data/               # Data pipeline
│   │   ├── fetch_squad.py
│   │   ├── fetch_race.py
│   │   ├── make_subset.py
│   │   └── preprocess.py
│   ├── models/             # Model wrappers
│   │   ├── baseline_llm.py
│   │   └── controlled_qg.py
│   ├── train/              # Training scripts
│   │   ├── finetune_baseline.py
│   │   └── finetune_controlled.py
│   ├── generate/           # Generation pipeline
│   │   └── run_generate.py
│   ├── eval/               # Evaluation scripts
│   │   ├── compute_bleu_rouge.py
│   │   ├── qa_answerability.py
│   │   ├── human_pack.py
│   │   └── aggregate.py
│   └── utils/              # Utility functions
│       ├── io_utils.py
│       ├── seed.py
│       └── metrics.py
├── outputs/                # Trained models (created during training)
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment (alternative)
└── README.md              # This file
```

## Overview

This project implements and evaluates **difficulty-controlled Question Generation (QG)** for educational applications. We compare:
- **Baseline QG**: Standard seq2seq models (T5/BART/GPT-2) without difficulty control
- **Controlled QG**: Same models with difficulty tokens (`<easy>`, `<medium>`, `<hard>`)

**Key Features:**
- Support for multiple datasets (SQuAD, RACE)
- Multiple model architectures (T5, BART, GPT-2)
- Heuristic difficulty labeling (answer length, rarity, context complexity)
- Automatic evaluation (BLEU, ROUGE, QA answerability)
- Human evaluation framework
- LaTeX output for paper integration

## Setup

### Option 1: Virtual Environment (pip)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Conda Environment

```bash
# Create conda environment
conda env create -f environment.yml
conda activate qg-exp
```

## Quick Start

### 1. Data Preparation

```bash
# Fetch SQuAD dataset
python -m src.data.fetch_squad --out data/raw/squad.jsonl

# Fetch RACE dataset
python -m src.data.fetch_race --out data/raw/race.jsonl

# Create small subsets for rapid experimentation
python -m src.data.make_subset \
  --in data/raw/squad.jsonl \
  --out data/interim/squad_small.jsonl \
  --train 1000 --dev 200 --test 200 --seed 42

python -m src.data.make_subset \
  --in data/raw/race.jsonl \
  --out data/interim/race_small.jsonl \
  --train 1000 --dev 200 --test 200 --seed 42

# Add difficulty labels
python -m src.data.preprocess \
  --in data/interim/squad_small.jsonl \
  --out data/processed/squad_small.qg_labeled.jsonl

python -m src.data.preprocess \
  --in data/interim/race_small.jsonl \
  --out data/processed/race_small.qg_labeled.jsonl
```

### 2. Training

**Baseline Model (no difficulty control):**
```bash
python -m src.train.finetune_baseline --cfg src/config/exp_squad_small.yaml
```

**Controlled Model (with difficulty tokens):**
```bash
# First, update config to enable difficulty tokens
# Edit src/config/exp_squad_small.yaml: set use_difficulty_token: true
# and change output_dir to outputs/controlled_t5_small_squad

python -m src.train.finetune_controlled --cfg src/config/exp_squad_small.yaml
```

### 3. Generation

```bash
# Generate with baseline model
python -m src.generate.run_generate \
  --model outputs/baseline_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --out reports/tables/preds_baseline_squad.jsonl

# Generate with controlled model
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --out reports/tables/preds_controlled_squad.jsonl

# Optional: Override difficulty for controlled model
python -m src.generate.run_generate \
  --model outputs/controlled_t5_small_squad_small \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --split test \
  --difficulty hard \
  --out reports/tables/preds_controlled_hard.jsonl
```

### 4. Evaluation

**Automatic Metrics (BLEU/ROUGE):**
```bash
python -m src.eval.compute_bleu_rouge \
  --pred reports/tables/preds_baseline_squad.jsonl \
  --out reports/tables/metrics_baseline.json

python -m src.eval.compute_bleu_rouge \
  --pred reports/tables/preds_controlled_squad.jsonl \
  --out reports/tables/metrics_controlled.json
```

**QA Answerability:**
```bash
python -m src.eval.qa_answerability \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --pred reports/tables/preds_baseline_squad.jsonl \
  --out reports/tables/qa_baseline.json

python -m src.eval.qa_answerability \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --pred reports/tables/preds_controlled_squad.jsonl \
  --out reports/tables/qa_controlled.json
```

**Human Evaluation Pack:**
```bash
python -m src.eval.human_pack \
  --dataset data/processed/squad_small.qg_labeled.jsonl \
  --predA reports/tables/preds_baseline_squad.jsonl \
  --predB reports/tables/preds_controlled_squad.jsonl \
  --n 120 \
  --out reports/tables/human_eval_pack.xlsx \
  --seed 314
```

### 5. Aggregation & Visualization

```bash
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

## Configuration

### Model Configuration

Edit YAML files in `src/config/` to customize:
- `model_name`: e.g., `t5-small`, `facebook/bart-base`, `gpt2`
- `model_type`: `t5`, `bart`, or `gpt2`
- `use_difficulty_token`: `true` for controlled, `false` for baseline
- `train_batch_size`, `learning_rate`, `num_train_epochs`, etc.

### Difficulty Heuristic

The difficulty scoring in `src/data/preprocess.py` uses:
- **Answer length** (30% weight): Shorter answers = easier
- **Answer rarity** (40% weight): Rare words in context = harder
- **Context complexity** (30% weight): Longer sentences, diverse vocab = harder

Adjust weights in `compute_difficulty_score()` as needed.

## Supported Models

- **T5** (t5-small, t5-base): Text-to-text transformer (recommended)
- **BART** (facebook/bart-base, facebook/bart-large): Seq2seq model
- **GPT-2** (gpt2, gpt2-medium): Causal language model

## Dependencies

Core packages:
- `torch>=2.0.0`: Deep learning framework
- `transformers>=4.44`: Hugging Face models
- `datasets>=2.20`: Dataset loading
- `evaluate`, `rouge-score`, `sacrebleu`: Metrics
- `openpyxl`: Excel file handling
- `matplotlib`, `seaborn`: Visualization
- `pyyaml`: Configuration files

## Evaluation Metrics

### Automatic Metrics
- **BLEU**: N-gram overlap with reference questions
- **ROUGE-1/2/L**: Unigram/bigram/longest-common-subsequence overlap
- **EM (Exact Match)**: QA model's answer exactly matches gold answer
- **F1**: Token-level F1 between QA answer and gold answer

### Human Evaluation (1-5 Likert Scale)
- **Fluency**: Grammatical correctness and naturalness
- **Relevance**: How well question relates to context and answer
- **Answerability**: Can the question be answered from context?
- **Educational Value**: Usefulness for learning/assessment
- **Perceived Difficulty**: How hard is the question?

## Paper Integration

All results can be automatically exported to LaTeX format for your paper:

```bash
python -m src.eval.aggregate \
  --metricsA reports/tables/metrics_baseline.json \
  --metricsB reports/tables/metrics_controlled.json \
  --qaA reports/tables/qa_baseline.json \
  --qaB reports/tables/qa_controlled.json \
  --out_csv reports/tables/comparison.csv \
  --out_fig reports/figures/comparison.png \
  --emit_latex paper/results.tex
```

Then in your LaTeX document:
```latex
\input{paper/results.tex}
```

See `paper/README.md` for details.

## Troubleshooting

### Out of Memory (OOM)
- Reduce `train_batch_size` to 4 or 2
- Increase `gradient_accumulation_steps`
- Use a smaller model (e.g., `t5-small` instead of `t5-base`)
- Reduce `max_source_length` to 256

### Slow Training
- Enable `fp16: true` in config (requires GPU)
- Increase batch size if memory allows
- Use fewer training samples for initial testing

### Poor Generation Quality
- Check input formatting (context and answer properly separated)
- Increase `num_train_epochs`
- Try different `learning_rate` values
- Ensure difficulty labels are balanced

### Dataset Not Found
- Run data fetching scripts first
- Check file paths in config files
- Ensure `data/raw/`, `data/interim/`, and `data/processed/` directories exist

## Extending the Project

### Adding New Datasets
1. Create `fetch_<dataset>.py` in `src/data/`
2. Convert to JSONL format with fields: `id`, `context`, `question`, `answer`, `split`
3. Run `make_subset.py` and `preprocess.py`

### Adding New Models
1. Add model configuration to `src/config/exp_multi_model.yaml`
2. Ensure model is supported by Hugging Face `transformers`
3. Update `baseline_llm.py` if special handling needed

### Custom Difficulty Metrics
Edit `src/data/preprocess.py`:
- Modify `compute_difficulty_score()` function
- Add new component scores
- Adjust weights in weighted combination

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{qg-controlled,
  author = {Your Name},
  title = {Difficulty-Controlled Question Generation for Educational Applications},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/yourusername/thesis-project}
}
```

## Contributing

1. Create a feature branch from `paper-implementation`
2. Make your changes
3. Test your changes
4. Submit a pull request

## License

[Add your license information here]

## Acknowledgments

This project uses:
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [SQuAD Dataset](https://rajpurkar.github.io/SQuAD-explorer/)
- [RACE Dataset](https://www.cs.cmu.edu/~glai1/data/race/)
- [sacrebleu](https://github.com/mjpost/sacrebleu)
- [rouge-score](https://github.com/google-research/google-research/tree/master/rouge)
