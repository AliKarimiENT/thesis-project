# Paper LaTeX Integration

This directory contains auto-generated LaTeX code from the QG experiment results.

## Files

- `results.tex` - Auto-generated LaTeX tables and figures (created by `src/eval/aggregate.py`)

## Usage

To include the results in your LaTeX paper:

```latex
\documentclass{article}
\usepackage{booktabs}  % For table formatting
\usepackage{graphicx}  % For figures

\begin{document}

% Include the results
\input{paper/results.tex}

\end{document}
```

## Tables Generated

1. **Table: Automatic Metrics** (`tab:automatic-metrics`)
   - BLEU, ROUGE-1, ROUGE-2, ROUGE-L scores
   - Comparison between baseline and controlled systems

2. **Table: QA Answerability** (`tab:qa-metrics`)
   - Exact Match (EM) and F1 scores
   - Measures how well generated questions can be answered

3. **Table: Human Evaluation** (`tab:human-eval`)
   - Fluency, Relevance, Answerability, Educational Value, Perceived Difficulty
   - 1-5 Likert scale ratings with mean ± std

## Figures Generated

1. **Figure: Comparison Plot** (`fig:comparison`)
   - Bar chart comparing all automatic metrics
   - Located in `reports/figures/`

## Regenerating Results

To regenerate the LaTeX output after running new experiments:

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

## LaTeX Requirements

Make sure your LaTeX document includes:

```latex
\usepackage{booktabs}   % For \toprule, \midrule, \bottomrule
\usepackage{graphicx}   % For \includegraphics
```

## References

You can reference the tables and figures in your text:

```latex
Table~\ref{tab:automatic-metrics} shows the automatic evaluation results.
The QA answerability metrics in Table~\ref{tab:qa-metrics} indicate...
Figure~\ref{fig:comparison} illustrates the overall comparison.
```

