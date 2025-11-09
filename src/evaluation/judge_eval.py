import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OpenAI api key is not set")

CLIENT = OpenAI(api_key=API_KEY)
JUDGE_MODEL = "gpt-5"
INPUT_CSV = "./results/generated_samples.csv"
OUTPUT_CSV = "./results/evaluation_results.csv"
SAMPLE_SIZE = 200 

QUESTION_TYPES = [
    "readingMatchingFeatures",
    "readingMultipleChoices",
    "readingShortAnswer",
    "readingTextCompletion",
    "readingTrueFalseNotGiven",
    "readingYesNoNotGiven"
]

def build_judge_prompt(passage, instruction, question, ref_type, intended_diff):
    instruction = str(instruction) if pd.notna(instruction) else "N/A"
    question = str(question) if pd.notna(question) else "N/A"
    
    prompt = f"""
    You are an expert evaluator for an IELTS Question Generation system. Your task is to 
    assess the quality of a generated question based on a given passage.
    Provide your evaluation in a strict JSON format.

    **Passage:**
    ---
    {passage[:2000]}
    ---

    **Generated Instruction:**
    ---
    {instruction}
    ---

    **Generated Question:**
    ---
    {question}
    ---

    **Reference (Ground Truth) Question Type:**
    {ref_type}

    **Intended Difficulty (from source):**
    {intended_diff}

    **EVALUATION CRITERIA:**

    1.  **Answerability (Score 0-10):** How answerable is the *Generated Question* using *only* the provided *Passage*?
        * 0: Impossible to answer or requires external knowledge.
        * 10: The answer is clearly and explicitly in the passage.

    2.  **Clarity (Score 0-10):** How clear, grammatically correct, and unambiguous 
        is the *Generated Question* (and its *Instruction*)?
        * 0: Incomprehensible or completely broken grammar.
        * 10: Perfectly clear, fluent, and well-formed.

    3.  **Relevance (Score 0-10):** How relevant is the *Generated Question* to the 
        main ideas of the *Passage*?
        * 0: Completely irrelevant or focused on a trivial detail.
        * 10: Directly addresses a key concept or important detail from the passage.

    4.  **Difficulty Assessment (Easy/Medium/Hard):** What is the *actual* difficulty 
        of answering this question based on the passage?
        Respond with ONLY one word: Easy, Medium, or Hard.

    5.  **Question Type Classification (String):** What is the *actual* question type 
        of the *Generated Instruction* and *Generated Question*? Choose *only* from this list:
        {json.dumps(QUESTION_TYPES)}
        Pay attention more to *Generated Instruction* column to classify the question type.
        
        ### Quick Guide to the Six Types
        - **readingMatchingFeatures** — *“Match the statements/features to options (people/researchers/years/…).”* Answers often letters; some options may be used more than once.
        - **readingMultipleChoices** — *“Choose the correct letter A–D / Which of the following…”* Standard multiple-choice with one best answer.
        - **readingShortAnswer** — WH-questions requiring a short phrase/word/number. Often with a word limit (e.g., “NO MORE THAN X WORDS AND/OR A NUMBER”). 
        - **readingTextCompletion** — Fill-in-the-gap in **text/sentences**. If the original instruction mentions a more specific format (summary/table/flow-chart), still classify as **readingTextCompletion** here (since the allowed list is limited to six types).
        - **readingTrueFalseNotGiven** — Verify statements against **facts** in the passage: **True / False / Not Given**.
        - **readingYesNoNotGiven** — Verify statements against **writer’s views/claims**: **Yes / No / Not Given**.

        **Disambiguation tips:**
        - If the instruction explicitly says “Match … to …” ⇒ `readingMatchingFeatures`.
        - If the instruction says “Choose the correct letter / Which of the following …” ⇒ `readingMultipleChoices`.
        - If it is a direct WH-question expecting a short phrase/number ⇒ `readingShortAnswer`.
        - If it says “Complete the text/sentences/gaps …” ⇒ `readingTextCompletion`.
        - **TFNG vs YNNG**: facts/information ⇒ `readingTrueFalseNotGiven`; writer’s views/claims ⇒ `readingYesNoNotGiven`.


    **OUTPUT (JSON Only):**
    Return *only* the JSON object, starting with {{ and ending with }}.
    {{
      "answerability_score": <int>,
      "clarity_score": <int>,
      "relevance_score": <int>,
      "judged_difficulty": "<Easy/Medium/Hard>",
      "judged_question_type": "<Type from list>"
    }}
    """
    return prompt

def get_evaluation(row):
    try:
        prompt = build_judge_prompt(
            row['reference_passage'],
            row['generated_instruction'],
            row['generated_question'],
            row['reference_question_type'],
            row['reference_difficulty']
        )
        
        response = CLIENT.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert IELTS evaluator. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result_json = response.choices[0].message.content
        result_dict = json.loads(result_json)
        
        if result_dict.get("judged_question_type") not in QUESTION_TYPES:
            result_dict["judged_question_type"] = "Other"
            
        return result_dict

    except Exception as e:
        print(f"Error processing row: {e}")
        return {
            "answerability_score": None,
            "clarity_score": None,
            "relevance_score": None,
            "judged_difficulty": None,
            "judged_question_type": None,
        }

def main():
    print(f"Loading input data from {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_CSV}' not found.")
        return

    if SAMPLE_SIZE > 0 and SAMPLE_SIZE < len(df):
        print(f"Processing a sample of {SAMPLE_SIZE} rows.")
        df_sample = df.sample(SAMPLE_SIZE, random_state=42).copy()
    else:
        print(f"Processing all {len(df)} rows.")
        df_sample = df.copy()

    evaluations = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_evaluation, row): index for index, row in df_sample.iterrows()}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Evaluating Generations"):
            index = futures[future]
            result = future.result()
            result['original_index'] = index 
            evaluations.append(result)

    eval_df = pd.DataFrame(evaluations)
    eval_df = eval_df.set_index('original_index')

    final_df = df_sample.join(eval_df)

    print("Adding comparison columns...")
    
    final_df['difficulty_match'] = final_df['reference_difficulty'] == final_df['judged_difficulty']
    
    final_df['type_match'] = final_df['reference_question_type'] == final_df['judged_question_type']
    
    final_df['avg_score'] = final_df[['answerability_score', 'clarity_score', 'relevance_score']].mean(axis=1)

    final_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n✅ Evaluation complete! Results saved to {OUTPUT_CSV}")
    
    print("\n--- Evaluation Summary ---")
    print(f"Average Score (0-10): {final_df['avg_score'].mean():.2f}")
    print(f"Difficulty Match Rate: {final_df['difficulty_match'].mean() * 100:.2f}%")
    print(f"Question Type Match Rate: {final_df['type_match'].mean() * 100:.2f}%")
    
    print("\nDistribution of Judged Difficulties:")
    print(final_df['judged_difficulty'].value_counts(normalize=True))
    
    print("\nDistribution of Judged Question Types:")
    print(final_df['judged_question_type'].value_counts(normalize=True))


if __name__ == "__main__":
    main()