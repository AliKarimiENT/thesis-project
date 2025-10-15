# METHODOLOGY SECTION (Copy-Paste into Word)

## 3. Experimental Setup

### 3.1 Dataset

We conducted our experiments using the Stanford Question Answering Dataset (SQuAD v1.1) [Rajpurkar et al., 2016], which contains 100,000+ question-answer pairs on 500+ Wikipedia articles. To enable rapid experimentation and validation, we created a stratified subset consisting of:

- **Training set**: 1,000 samples
- **Validation set**: 200 samples  
- **Test set**: 200 samples

The subset was created using random stratified sampling with a fixed seed (42) to ensure reproducibility. Each sample consists of a context passage, an answer span, and a reference question.

### 3.2 Difficulty Labeling

To enable difficulty-controlled question generation, we assigned difficulty labels (easy, medium, hard) to each sample using a deterministic heuristic. The heuristic combines three components:

**1. Answer Length (30% weight)**  
Shorter answer spans typically indicate easier questions. We normalize answer length (in tokens) by dividing by 10, capping at 1.0.

**2. Answer Rarity (40% weight)**  
Questions about rare or infrequent words in the context tend to be harder. We compute the inverse document frequency (IDF-like) score by measuring the frequency of answer tokens within the context. Lower frequency indicates higher difficulty.

**3. Context Complexity (30% weight)**  
Longer, more complex contexts with diverse vocabulary indicate harder questions. We measure average sentence length and vocabulary diversity (unique tokens / total tokens).

The final difficulty score is a weighted combination of these three components, normalized to [0, 1]. We then bin samples into three classes using the 33rd and 67th percentiles:
- **Easy**: Score < 33rd percentile (462 samples, 33.0%)
- **Medium**: 33rd ≤ Score < 67th percentile (476 samples, 34.0%)
- **Hard**: Score ≥ 67th percentile (462 samples, 33.0%)

### 3.3 Models

We compare two question generation approaches:

**Baseline Model**  
A standard T5-small model (60M parameters) trained in a sequence-to-sequence fashion. Input format: `"context: [CONTEXT] answer: [ANSWER]"`. Output: the target question. This model has no explicit difficulty control.

**Difficulty-Controlled Model**  
The same T5-small architecture, but with three special difficulty tokens (`<easy>`, `<medium>`, `<hard>`) added to the vocabulary. Input format: `"difficulty: <LEVEL> context: [CONTEXT] answer: [ANSWER]"`. This allows explicit control over question difficulty at generation time.

Both models are initialized from the pre-trained `t5-small` checkpoint and fine-tuned on our SQuAD subset.

### 3.4 Training Configuration

Both models were trained with identical hyperparameters:
- **Optimizer**: AdamW
- **Learning rate**: 5e-5 with linear warmup (6% of steps)
- **Batch size**: 8 per device (with gradient accumulation: 2 steps)
- **Epochs**: 3
- **Max source length**: 512 tokens
- **Max target length**: 64 tokens
- **Beam search**: 5 beams for generation
- **Hardware**: CPU (MacBook Pro M-series)

Training took approximately 3 minutes per model on CPU.

### 3.5 Evaluation Metrics

We evaluate generated questions using both automatic and human evaluation:

**Automatic Metrics:**

1. **BLEU** (Bilingual Evaluation Understudy): Measures n-gram overlap between generated and reference questions using sacrebleu implementation. Reported as corpus-level score (0-100).

2. **ROUGE-1, ROUGE-2, ROUGE-L**: Measures unigram, bigram, and longest common subsequence overlap between generated and reference questions. Reported as F1-scores (0-1).

3. **QA Answerability**: We use a pre-trained DistilBERT-SQuAD model to answer the generated question given the context, then measure:
   - **Exact Match (EM)**: Whether the QA model's answer exactly matches the gold answer
   - **F1 Score**: Token-level F1 between QA answer and gold answer
   
   Higher scores indicate more answerable questions.

**Human Evaluation:**

We prepared an evaluation pack containing 120 randomly sampled question pairs (baseline vs. controlled), with A/B order randomized. Raters evaluate each question on five dimensions using a 5-point Likert scale:

1. **Fluency**: Grammatical correctness and naturalness
2. **Relevance**: How well the question relates to context and answer
3. **Answerability**: Whether the question can be answered from the context
4. **Educational Value**: Usefulness for learning/comprehension assessment
5. **Perceived Difficulty**: Subjective difficulty level

The evaluation pack is provided as an Excel spreadsheet with instructions and rubric included.

### 3.6 Implementation

All experiments were conducted using Python 3.13, PyTorch 2.8, and Hugging Face Transformers 4.57. The complete codebase, including data preprocessing, training, generation, and evaluation scripts, is available in our GitHub repository for reproducibility.

---

**COPY THE ABOVE INTO YOUR WORD DOCUMENT'S METHODOLOGY SECTION**

