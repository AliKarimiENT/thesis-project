# ✅ QG Experiment - Local Execution Summary

**Date**: October 15, 2025  
**Status**: ✅ **RUNNING SUCCESSFULLY**  
**Process ID**: Check with `ps aux | grep run_full_pipeline`

---

## 🔧 Issues Fixed for Mac Compatibility

1. **Training Script API Update**
   - Changed `evaluation_strategy="steps"` → `eval_strategy="steps"`
   - Reason: Transformers 4.57.0 API change

2. **FP16 Disabled**
   - Changed `fp16: true` → `fp16: false`
   - Reason: Mac (MPS/CPU) doesn't support fp16 mixed precision

3. **DataLoader Workers**
   - Changed `dataloader_num_workers: 4` → `dataloader_num_workers: 0`
   - Reason: Python 3.13 + PyTorch multiprocessing issue on Mac

---

## 📊 Current Execution Status

**✅ Completed Steps:**
1. ✅ Fetched SQuAD dataset (98,169 samples)
2. ✅ Created subset (1000 train / 200 dev / 200 test)
3. ✅ Added difficulty labels (33% easy / 34% medium / 33% hard)

**⏳ In Progress:**
4. ⏳ Training baseline T5-small (~2.5 hours remaining)

**⏸️ Pending:**
5. ⏸️ Training controlled T5-small (~2.5 hours)
6. ⏸️ Generating questions (~15 mins)
7. ⏸️ Computing metrics (~15 mins)
8. ⏸️ Creating results & LaTeX (~5 mins)

**Estimated Total Time**: 5-6 hours

---

## 📦 Expected Outputs

When complete, you'll have:

### Models
- `outputs/baseline_t5_small_squad_small/` - Baseline QG model
- `outputs/controlled_t5_small_squad_small/` - Difficulty-controlled model

### Predictions
- `reports/tables/preds_baseline_squad.jsonl` - Generated questions (baseline)
- `reports/tables/preds_controlled_squad.jsonl` - Generated questions (controlled)

### Metrics
- `reports/tables/metrics_baseline_squad.json` - BLEU/ROUGE scores
- `reports/tables/metrics_controlled_squad.json` - BLEU/ROUGE scores
- `reports/tables/qa_baseline_squad.json` - QA answerability (EM/F1)
- `reports/tables/qa_controlled_squad.json` - QA answerability (EM/F1)

### Results
- `reports/tables/comparison_squad.csv` - Comparison table
- `reports/figures/comparison_squad.png` - Comparison plot
- `paper/results_squad.tex` - LaTeX tables/figures for paper
- `reports/tables/human_eval_pack_squad.xlsx` - Human evaluation template

---

## 📊 Monitor Progress

```bash
# Watch live output
tail -f pipeline_output.log

# Check last 30 lines
tail -30 pipeline_output.log

# Check if still running
ps aux | grep run_full_pipeline

# See training progress (look for percentage)
grep -E "%" pipeline_output.log | tail -10
```

---

## 🎯 After Completion

1. **Check results:**
   ```bash
   cat reports/tables/comparison_squad.csv
   open reports/figures/comparison_squad.png
   ```

2. **Use in paper:**
   ```latex
   \input{paper/results_squad.tex}
   ```

3. **Complete human evaluation:**
   - Open `reports/tables/human_eval_pack_squad.xlsx`
   - Rate 120 question pairs (5 dimensions each)
   - Save as `human_eval_results.xlsx`
   - Rerun aggregation to include human scores

---

## ⚠️ If Something Goes Wrong

**Pipeline stops unexpectedly:**
```bash
# Check last error
tail -50 pipeline_output.log

# Restart from where it stopped
source venv/bin/activate
./run_full_pipeline.sh
```

**Want to stop:**
```bash
# Find process ID
ps aux | grep run_full_pipeline

# Kill it
kill <PID>
```

---

## ✅ Success Criteria

The experiment is successful when:
- ✅ All 11 steps complete without errors
- ✅ Both models are trained and saved
- ✅ Predictions generated for 200 test samples
- ✅ Metrics computed (BLEU/ROUGE/EM/F1)
- ✅ LaTeX file generated for paper

**Current Status**: 🏃 Running - on track for success!

---

## 📝 Notes

- Training on CPU (MacBook Pro) takes ~5-6 hours
- GPU would be ~10x faster (~30-45 minutes)
- Google Colab (free GPU) is an alternative for faster execution
- All compatibility issues for Mac have been resolved
- Pipeline will continue even if you close the terminal

---

**Log File**: `pipeline_output.log`  
**Start Time**: Check file modification time  
**Expected Completion**: ~5-6 hours from start
