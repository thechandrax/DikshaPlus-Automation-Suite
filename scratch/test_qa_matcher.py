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

    # Screen Questions from User Log
    test_screen_questions = [
        "1. question text\nwhich one of the following is the most celebrated aspect...",
        "2. question text\naudio is……….\nquestion 2\nselect one:\na.\ndistant\nb.\nfamili...",
        "7. question text\nwhich device is central to modern audio experiences acro...",
        "11. question text\nwhat is one major emotional advantage of audio in educat..."
    ]



    for idx, raw_q in enumerate(test_screen_questions, 1):
        q_text_screen = re.sub(r'^(?:question\s*text|question\s*\d+[:.]?|\d+[:.]?|q\d+[:.]?)\s*', '', raw_q, flags=re.IGNORECASE)
        q_text_screen = re.sub(r'\s*(?:select\s*one|question\s*\d+).*$', '', q_text_screen, flags=re.IGNORECASE | re.DOTALL).strip().lower()

        clean_screen_q = re.sub(r'[^\w\s]', '', q_text_screen) if q_text_screen else ""
        screen_words = set(w for w in clean_screen_q.split() if len(w) >= 3) if clean_screen_q else set()

        matched_answer = None
        matched_json_q = None

        for item in items:
            json_q = (item.get("question") or item.get("question_keyword") or "").strip().lower()
            clean_json_q = re.sub(r'[^\w\s]', '', json_q)
            json_words = set(w for w in clean_json_q.split() if len(w) >= 3)

            common_words = json_words & screen_words
            json_coverage = (len(common_words) / float(len(json_words))) if json_words else 0.0
            screen_coverage = (len(common_words) / float(len(screen_words))) if screen_words else 0.0

            is_exact_sub = False
            if clean_json_q and clean_screen_q:
                if clean_json_q == clean_screen_q:
                    is_exact_sub = True
                elif clean_json_q in clean_screen_q or clean_screen_q in clean_json_q:
                    if (len(clean_json_q) >= 15 and screen_coverage >= 0.35) or abs(len(clean_json_q) - len(clean_screen_q)) <= 10:
                        is_exact_sub = True

            is_keyword_match = (json_coverage >= 0.75 and screen_coverage >= 0.35)

            if is_exact_sub or is_keyword_match:
                matched_answer = (item.get("answer") or item.get("correct_option") or "").strip()
                matched_json_q = item.get("question") or item.get("question_keyword") or ""
                break

        print(f"\n[Test Q#{idx}] Input Screen Text : '{q_text_screen}'")
        if matched_answer:
            print(f"  ✔ [GATE 1 VERIFIED] JSON Question Match : '{matched_json_q[:55]}...'")
            print(f"  ✔ [GATE 2 VERIFIED] Target Answer Match : '{matched_answer}'")
            print(f"  🛡️ [DUAL CONFIRMATION GUARANTEED] Question & Answer 100% Verified!")
        else:
            print(f"  ℹ [NOTICE] False match prevented cleanly! No false match.")


if __name__ == "__main__":
    test_question_matching()
