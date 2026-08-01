import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
import automations.diksha_plus_engine as engine

print(f"Loaded Gemini Key: '{config.GEMINI_API_KEY[:8]}...'")

sample_course = "Test AI Auto Learning Course"
sample_q = "Which planet is known as the Red Planet?"
sample_opts = ["Earth", "Mars", "Jupiter", "Venus"]

print(f"\nSending question to AI Live Solver:\nQuestion: '{sample_q}'\nOptions: {sample_opts}")
solved_ans = engine.solve_question_with_ai(sample_q, sample_opts)
print(f"AI Live Solver Result: '{solved_ans}'")

if solved_ans:
    print("\nTesting Sequential Auto-Learning Storage...")
    engine.save_auto_learned_qa(
        course_title=sample_course,
        module_no=1,
        module_name="Solar System",
        sub_no=1,
        sub_name="Planets Assessment",
        question_text=sample_q,
        answer_text=solved_ans
    )
    
    key_file = config.COURSES_DIR / "test_ai_auto_learning_course.json"
    if key_file.exists():
        print(f"\nSUCCESS! File created: {key_file.name}")
        print("File Content:")
        print(key_file.read_text(encoding="utf-8"))
    else:
        print("FAILED: File was not created!")
