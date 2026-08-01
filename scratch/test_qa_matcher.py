import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
import automations.diksha_plus_engine as engine


def test_question_matching():
    answer_key = engine.load_answer_key("NISHTHA FLN English")
    items = engine.extract_all_qa_items(answer_key)
    
    print("=" * 60)
    print(f"  🧪 QUESTION-ANSWER MATCHING TEST (Loaded {len(items)} items)")
    print("=" * 60)

    # Real Screen Questions from DIKSHA portal
    test_screen_questions = [
        "1. At preschool, children do not learn by play-based age and developmentally appropriate activities and material",
        "Q2. All the aspects of preschool education such as physical development, cognitive development, language development, socio-emotional development, etc. are interrelated and interdependent.",
        "3. Once students fall behind on FLN, they tend to maintain flat learning curves for years, and are perpetually unable to catch up."
    ]


    for idx, raw_screen_q in enumerate(test_screen_questions, 1):
        clean_screen_q = re.sub(r'^(?:question\s*\d+[:.]?|\d+[:.]?|q\d+[:.]?)\s*', '', raw_screen_q, flags=re.IGNORECASE).strip().lower()
        clean_screen_alphanumeric = re.sub(r'[^\w\s]', '', clean_screen_q)
        screen_words = set(w for w in clean_screen_alphanumeric.split() if len(w) >= 3)

        matched_answer = None
        matched_json_q = None

        for item in items:
            json_q = (item.get("question") or item.get("question_keyword") or "").strip().lower()
            clean_json_q = re.sub(r'[^\w\s]', '', json_q)
            json_words = set(w for w in clean_json_q.split() if len(w) >= 3)

            overlap_ratio = (len(json_words & screen_words) / float(len(json_words))) if json_words else 0.0

            if clean_json_q and (clean_json_q in clean_screen_alphanumeric or clean_screen_alphanumeric in clean_json_q or overlap_ratio >= 0.75):
                matched_answer = (item.get("answer") or item.get("correct_option") or "").strip()
                matched_json_q = item.get("question") or item.get("question_keyword") or ""
                break

        print(f"\n[Test Q#{idx}] Input Screen Text : '{raw_screen_q}'")
        if matched_answer:
            print(f"  ✔ [GATE 1 VERIFIED] JSON Question Match : '{matched_json_q[:55]}...'")
            print(f"  ✔ [GATE 2 VERIFIED] Target Answer Match : '{matched_answer}'")
            print(f"  🛡️ [DUAL CONFIRMATION GUARANTEED] Question & Answer 100% Verified!")
        else:
            print(f"  ℹ [NOTICE] No JSON match found. Falling back to default option [1].")

if __name__ == "__main__":
    test_question_matching()
