# TABLES FOR WORD DOCUMENT (Copy-Paste Ready)

## Table 1: Automatic Evaluation Metrics

**Caption**: Comparison of automatic evaluation metrics between baseline and difficulty-controlled question generation models on SQuAD test set (n=200).

| Metric | Baseline | Controlled | Difference |
|--------|----------|------------|------------|
| BLEU | 9.57 | 9.16 | -4.3% |
| ROUGE-1 | 0.365 | 0.349 | -4.4% |
| ROUGE-2 | 0.156 | 0.150 | -3.8% |
| ROUGE-L | 0.318 | 0.303 | -4.7% |

**Note**: BLEU scores range from 0-100; ROUGE scores range from 0-1. Higher scores indicate better performance.

---

## Table 2: QA Answerability Metrics

**Caption**: Question answerability measured by a DistilBERT-SQuAD model's ability to correctly answer generated questions from context.

| Metric | Baseline | Controlled | Difference |
|--------|----------|------------|------------|
| Exact Match (EM) | 0.145 | 0.110 | -24.1% |
| F1 Score | 0.233 | 0.211 | -9.4% |

**Note**: EM and F1 scores range from 0-1. EM measures exact answer match; F1 measures token-level overlap. Higher scores indicate more answerable questions.

---

## Table 3: Question Length Statistics

**Caption**: Average question length (in words) for generated and reference questions.

| Question Type | Mean Length | Std. Deviation |
|---------------|-------------|----------------|
| Reference Questions | 10.2 | 3.5 |
| Baseline Generated | 13.7 | 6.3 |
| Controlled Generated | 14.8 | 6.6 |

**Note**: Generated questions tend to be longer than references. Controlled model produces slightly longer questions.

---

## Table 4: Difficulty Distribution in Test Set

**Caption**: Distribution of difficulty labels in the test set (n=200).

| Difficulty Level | Count | Percentage |
|------------------|-------|------------|
| Easy | 63 | 31.5% |
| Medium | 81 | 40.5% |
| Hard | 56 | 28.0% |

**Note**: Difficulty labels assigned using heuristic combining answer length, rarity, and context complexity.

---

## Table 5: Metrics by Difficulty Level (Baseline Model)

**Caption**: Baseline model performance broken down by difficulty level.

| Difficulty | Sample Count | Avg BLEU | Avg Question Length |
|------------|--------------|----------|---------------------|
| Easy | 63 | N/A* | 13.2 words |
| Medium | 81 | N/A* | 14.1 words |
| Hard | 56 | N/A* | 13.8 words |

*Note: BLEU is computed at corpus level, not per-sample.

---

## Table 6: Metrics by Difficulty Level (Controlled Model)

**Caption**: Controlled model performance broken down by difficulty level.

| Difficulty | Sample Count | Avg BLEU | Avg Question Length |
|------------|--------------|----------|---------------------|
| Easy | 63 | N/A* | 13.7 words |
| Medium | 81 | N/A* | 15.1 words |
| Hard | 56 | N/A* | 15.7 words |

**Note**: Controlled model shows progression in length with difficulty (13.7 → 15.1 → 15.7 words), suggesting some difficulty awareness.

---

## HOW TO INSERT TABLES IN WORD

1. Copy the table markdown above
2. In Word, use Insert → Table → Convert Text to Table
3. Or paste into a Word table manually
4. Format with Word's table styles for professional appearance
5. Add the caption above each table

**Alternative**: Use the CSV file `reports/tables/comparison_squad.csv` and insert as Excel table in Word.

---

## QUICK NUMBERS TO CITE IN TEXT

- Dataset size: **1,400 samples** (1,000 train / 200 dev / 200 test)
- Models compared: **2** (baseline T5-small, controlled T5-small)
- Difficulty tokens: **3** (<easy>, <medium>, <hard>)
- Test questions generated: **200 per model** (400 total)
- Training time: **~3 minutes per model** (CPU)
- Baseline BLEU: **9.57**
- Controlled BLEU: **9.16**
- Baseline ROUGE-L: **0.318**
- Controlled ROUGE-L: **0.303**
- QA F1 (baseline): **0.233**
- QA F1 (controlled): **0.211**
- Difficulty distribution: **33% easy, 34% medium, 33% hard**

