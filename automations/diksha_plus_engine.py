"""
DIKSHA / LMS End-to-End Automation Pipeline.
Full implementation of specifications from DIKSHA.docx:
- STEP 01/02: Login with credentials (#username, #password, #login)
- STEP 03/04: Navigation to 'My Learning' & Ongoing Courses
- STEP 05/06: Open Course & Module Activity Loop
- STEP 07: Video (act_type="url"), PDF (act_type="resource"),
          H5P Quizzes (act_type="h5pactivity"), Formative Assessments (act_type="quiz").
"""

import sys
import json
import asyncio
import re
import time
import urllib.request
import unicodedata
from pathlib import Path




# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import async_playwright
import config
from utils.logger import get_logger

import threading

logger = get_logger("DikshaEngine")

IS_PAUSED = False
KEYBOARD_LISTENER_STARTED = False

def start_keyboard_pause_listener():
    global KEYBOARD_LISTENER_STARTED
    if KEYBOARD_LISTENER_STARTED:
        return
    KEYBOARD_LISTENER_STARTED = True

    def listener():
        global IS_PAUSED
        while True:
            try:
                if sys.platform == "win32":
                    import msvcrt
                    if msvcrt.kbhit():
                        ch = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        if ch == 'p' or ch == ' ':
                            IS_PAUSED = not IS_PAUSED
                            if IS_PAUSED:
                                logger.info("\n" + "=" * 65)
                                logger.info("  ⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...")
                                logger.info("=" * 65 + "\n")
                            else:
                                logger.info("\n" + "=" * 65)
                                logger.info("  ▶️ [AUTOMATION RESUMED] Continuing DIKSHA execution...")
                                logger.info("=" * 65 + "\n")
                time.sleep(0.1)
            except Exception:
                time.sleep(0.5)

    t = threading.Thread(target=listener, daemon=True)
    t.start()

async def check_pause_status():
    global IS_PAUSED
    if IS_PAUSED:
        while IS_PAUSED:
            await asyncio.sleep(0.5)


def get_course_filename(course_title):
    """
    Generates a clean, full dynamic filename for course JSON files while
    preserving full Bengali, Hindi, Urdu, and Unicode course names cleanly.
    """
    c_name = (course_title or "course").strip()
    clean_fn = re.sub(r'[\/\\:\*\?"<>\|\n\r\t]+', '_', c_name)
    clean_fn = re.sub(r'[\s_]+', '_', clean_fn).strip('_')
    if not clean_fn:
        clean_fn = "course"
    return f"{clean_fn}.json"


def load_answer_key(course_title=None):
    """
    Loads course-specific answer key from data/courses/<course_name>.json.
    Auto-creates clean template JSON files per course matching official modules hierarchy.
    """
    courses_dir = config.DATA_DIR / "courses"
    courses_dir.mkdir(parents=True, exist_ok=True)

    if course_title:
        fn_name = get_course_filename(course_title)
        course_file = courses_dir / fn_name

        if not course_file.exists():
            for f_path in courses_dir.glob("*.json"):
                try:
                    with open(f_path, "r", encoding="utf-8") as f_check:
                        j_data = json.load(f_check)
                        if normalize_text(j_data.get("course_name", "")).lower() == normalize_text(course_title).lower():
                            course_file = f_path
                            break
                except Exception:
                    pass

        if course_file.exists():
            try:
                with open(course_file, "r", encoding="utf-8") as f:
                    logger.info(f"  --> Loaded course-specific answer key: data/courses/{course_file.name}")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not parse {course_file.name}: {e}")
        else:
            # Create a clean template JSON file for this course with official "modules" hierarchy
            template = {
                "course_name": course_title,
                "modules": []
            }
            try:
                with open(course_file, "w", encoding="utf-8") as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                logger.info(f"  --> Created clean answer key template file: data/courses/{course_file.name}")
            except Exception as ex:
                logger.warning(f"Notice creating template file: {ex}")




def normalize_text(text):
    """
    Normalizes Unicode apostrophes (\u2019, '), quotes (\u201c, \u201d, "), dashes, and spaces to standard ASCII.
    Converts curly apostrophes ('Hon’ble') to standard straight keyboard apostrophes ('Hon\'ble').
    """
    if not text:
        return ""
    text = str(text)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201b", "'")
    text = text.replace("“", '"').replace("”", '"').replace("„", '"')
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("–", "-").replace("—", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00a0", " ")
    return re.sub(r'\s+', ' ', text).strip()

def extract_all_qa_items(answer_key):
    """
    Normalizes any JSON answer key structure (nested subsections, modules, flat answers/questions)
    into a unified list of question-answer dicts with normalized metadata.
    Strips leading option letter tags like [A], [B], b. from answer strings for 100% exact matching.
    """
    def clean_ans_str(val):
        val_str = str(val or "")
        stripped = re.sub(r'^\[[A-Z0-9]+\]\s*', '', val_str).strip()
        return normalize_text(stripped)

    qa_list = []
    if not isinstance(answer_key, dict):
        return qa_list

    # Schema 1: Top-level "subsections" array
    if "subsections" in answer_key and isinstance(answer_key["subsections"], list):
        for sub in answer_key["subsections"]:
            sub_no = sub.get("subsection_no")
            sub_name = sub.get("subsection_name")
            q_arr = sub.get("questions") or sub.get("answers") or []
            for item in q_arr:
                qa_list.append({
                    "module_no": sub.get("module_no") or answer_key.get("module_no"),
                    "module_name": sub.get("module_name") or answer_key.get("module_name"),
                    "subsection_no": sub_no,
                    "subsection_name": sub_name,
                    "question": normalize_text(item.get("question") or item.get("question_keyword") or ""),
                    "answer": clean_ans_str(item.get("answer") or item.get("correct_option") or ""),
                    "options": [normalize_text(o) for o in (item.get("options") or [])]
                })

    # Schema 2: Top-level "modules" array
    elif "modules" in answer_key and isinstance(answer_key["modules"], list):
        for mod in answer_key["modules"]:
            mod_no = mod.get("module_no")
            mod_name = mod.get("module_name")
            sub_arr = mod.get("subsections") or []
            for sub in sub_arr:
                sub_no = sub.get("subsection_no")
                sub_name = sub.get("subsection_name")
                q_arr = sub.get("questions") or sub.get("answers") or []
                for item in q_arr:
                    qa_list.append({
                        "module_no": mod_no,
                        "module_name": mod_name,
                        "subsection_no": sub_no,
                        "subsection_name": sub_name,
                        "question": normalize_text(item.get("question") or item.get("question_keyword") or ""),
                        "answer": clean_ans_str(item.get("answer") or item.get("correct_option") or ""),
                        "options": [normalize_text(o) for o in (item.get("options") or [])]
                    })

    # Schema 3: Flat "answers" or "questions" array
    else:
        q_arr = answer_key.get("answers") or answer_key.get("questions") or []
        for item in q_arr:
            qa_list.append({
                "module_no": item.get("module_no") or answer_key.get("module_no"),
                "module_name": item.get("module_name") or answer_key.get("module_name"),
                "subsection_no": item.get("subsection_no") or answer_key.get("subsection_no"),
                "subsection_name": item.get("subsection_name") or answer_key.get("subsection_name"),
                "question": normalize_text(item.get("question") or item.get("question_keyword") or ""),
                "answer": clean_ans_str(item.get("answer") or item.get("correct_option") or ""),
                "options": [normalize_text(o) for o in (item.get("options") or [])]
            })

    return qa_list


def save_auto_learned_qa(course_title, module_no, module_name, sub_no, sub_name, question_text, answer_text, option_texts=None, is_feedback=False):
    """
    Saves auto-learned question & answer sequentially under clean modules -> subsections hierarchy.
    """
    try:
        c_name = course_title or "unknown_course"
        fn_name = get_course_filename(c_name)
        course_key_file = config.COURSES_DIR / fn_name
        
        data_j = {}
        if course_key_file.exists():
            with open(course_key_file, "r", encoding="utf-8") as f:
                try:
                    data_j = json.load(f)
                except Exception:
                    data_j = {}


        data_j.pop("description", None)
        data_j.pop("answers", None)

        data_j["course_name"] = course_title or "Course"

        t_mod_no = int(module_no) if (module_no and str(module_no).isdigit()) else (module_no or 1)
        t_mod_name = module_name or "Module"

        t_sub_no = int(sub_no) if (sub_no and str(sub_no).isdigit()) else 1
        t_sub_name = sub_name or "Assessment"

        # Support clean "modules" hierarchy
        modules = data_j.get("modules")
        if not isinstance(modules, list):
            legacy_subs = data_j.pop("subsections", [])
            modules = []
            data_j["modules"] = modules
            if legacy_subs:
                m_dict = {}
                for s in legacy_subs:
                    mno = s.get("module_no") or t_mod_no
                    mname = s.get("module_name") or t_mod_name
                    if mno not in m_dict:
                        m_dict[mno] = {"module_no": mno, "module_name": mname, "subsections": []}
                    clean_s = {
                        "subsection_no": s.get("subsection_no", 1),
                        "subsection_name": s.get("subsection_name", "Assessment"),
                        "questions": s.get("questions", [])
                    }
                    m_dict[mno]["subsections"].append(clean_s)
                modules.extend(list(m_dict.values()))

        # Find or create target module
        target_mod = None
        for m in modules:
            if m.get("module_no") == t_mod_no or (m.get("module_name") or "").strip().lower() == t_mod_name.strip().lower():
                target_mod = m
                break

        if not target_mod:
            target_mod = {
                "module_no": t_mod_no,
                "module_name": t_mod_name,
                "subsections": []
            }
            modules.append(target_mod)

        # Find or create target subsection inside target module
        subsections = target_mod.get("subsections")
        if not isinstance(subsections, list):
            subsections = []
            target_mod["subsections"] = subsections

        target_sub = None
        for s in subsections:
            if s.get("subsection_no") == t_sub_no or (s.get("subsection_name") or "").strip().lower() == t_sub_name.strip().lower():
                target_sub = s
                break

        if not target_sub:
            target_sub = {
                "subsection_no": t_sub_no,
                "subsection_name": t_sub_name,
                "questions": []
            }
            subsections.append(target_sub)

        questions = target_sub.get("questions")
        if not isinstance(questions, list):
            questions = []
            target_sub["questions"] = questions

        norm_q = normalize_text(question_text)
        norm_a = normalize_text(answer_text)

        # Format options & answer based on Feedback Form vs Quiz context
        formatted_options = []
        formatted_answer = norm_a

        is_fb_context = is_feedback or "feedback" in (t_sub_name or "").lower()

        if is_fb_context:
            norm_q = re.sub(r'^\s*(?:\d+[\.\)]|Q\d+[\.\)]?|Question\s*\d+[\.\)]?)\s*', '', norm_q, flags=re.IGNORECASE).strip()

        if option_texts and isinstance(option_texts, list):
            if is_fb_context:
                formatted_options = [normalize_text(o) for o in option_texts]
                formatted_answer = norm_a
            else:

                matched_letter = ""
                clean_target = re.sub(r'[^\w\s]', '', norm_a.lower())

                for idx, opt_txt in enumerate(option_texts):
                    letter = chr(65 + idx) if idx < 26 else str(idx + 1)
                    clean_opt_txt = normalize_text(opt_txt)
                    formatted_options.append(f"[{letter}] {clean_opt_txt}")

                    clean_opt = re.sub(r'[^\w\s]', '', clean_opt_txt.lower())
                    if clean_target and clean_opt and (clean_target in clean_opt or clean_opt in clean_target):
                        matched_letter = letter

                if matched_letter:
                    raw_clean_a = re.sub(r'^\[[A-Z0-9]+\]\s*', '', norm_a)
                    formatted_answer = f"[{matched_letter}] {raw_clean_a}"

        clean_new_q = norm_q.lower()
        existing_qs = set(normalize_text(q.get("question") or "").lower() for q in questions)

        if clean_new_q not in existing_qs:
            q_entry = {
                "question": norm_q,
                "options": formatted_options,
                "answer": formatted_answer
            }
            questions.append(q_entry)
            with open(course_key_file, "w", encoding="utf-8") as f:
                json.dump(data_j, f, indent=2, ensure_ascii=False)
            logger.info(f"  💾 [AUTO-LEARNING SAVE] Saved to {course_key_file.name}: Module #{t_mod_no} ('{t_mod_name}') || Subsection #{t_sub_no} ('{t_sub_name}') -> Q: '{norm_q[:40]}...'")

    except Exception as ex:
        logger.warning(f"  --> Auto-learning save notice: {ex}")




def solve_question_with_ai(question_text, option_texts=None):
    """
    Uses Gemini AI API Multi-Key Pool FIRST (2 Attempts).
    If Gemini keys fail, uses Grok xAI API (2 Attempts) SECOND.
    If both fail, applies Stepped Backoff Protocol (30s -> 45s -> 60s).
    Returns None if all attempts fail, triggering strict Circuit Breaker Stop (never uses dummy Option A).
    """
    if not getattr(config, "AI_LIVE_SOLVER_ENABLED", True):
        return None

    options_formatted = "\n".join([f"{idx+1}. {opt}" for idx, opt in enumerate(option_texts or [])])
    prompt = f"""You are an expert AI teacher solving a quiz question for an educational course.

Question:
{question_text}

Option Choices:
{options_formatted if options_formatted else 'Select the correct factual answer.'}

INSTRUCTIONS:
Return ONLY the exact text of the correct option choice from the list above. Do NOT include option numbers (1, 2, 3), do NOT include explanations. Return ONLY the exact option text."""

    # 1. PRIORITY 1: Google Gemini AI Multi-Key Pool (2 ATTEMPTS)
    gemini_keys = getattr(config, "GEMINI_API_KEYS", [])
    if not gemini_keys and hasattr(config, "GEMINI_API_KEY") and config.GEMINI_API_KEY:
        gemini_keys = [config.GEMINI_API_KEY]

    models_to_try = ["gemini-2.0-flash", "gemini-flash-latest"]

    if gemini_keys:
        for gemini_attempt in range(1, 3):
            logger.info(f"  🧠 [GEMINI AI ATTEMPT {gemini_attempt}/2] Requesting solution via Gemini API...")
            for key_idx, api_key in enumerate(gemini_keys, 1):
                for model_name in models_to_try:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                        payload = json.dumps({
                            "contents": [{"parts": [{"text": prompt}]}]
                        }).encode('utf-8')
                        
                        headers = {
                            'Content-Type': 'application/json',
                            'x-goog-api-key': api_key
                        }

                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        
                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [GEMINI AI SUCCESS] Solved on Attempt {gemini_attempt}/2 via Key #{key_idx} ({model_name}) -> '{clean_ans}'")
                            return clean_ans
                    except urllib.error.HTTPError as http_err:
                        if http_err.code in (429, 503):
                            logger.warning(f"  ⏳ [GEMINI RATE LIMIT] Key #{key_idx} rate limited. Trying next key...")
                            time.sleep(1)
                            continue
                        elif http_err.code in (401, 403):
                            logger.error(f"  ❌ [GEMINI API ERROR {http_err.code}] Key #{key_idx} invalid.")
                            break
                    except Exception as ex:
                        logger.warning(f"  ⚠️ [GEMINI SOLVER NOTICE]: {ex}")
                        time.sleep(1)
                        break
            if gemini_attempt < 2:
                time.sleep(2)

    # 2. PRIORITY 2: Groq Cloud LPU API Key Pool (100% FREE - 14,400 RPD) (https://console.groq.com/)
    groq_keys = getattr(config, "GROQ_API_KEYS", [])
    if not groq_keys:
        single_groq = getattr(config, "GROQ_API_KEY", "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
        if single_groq:
            groq_keys = [single_groq]

    if groq_keys:
        for groq_attempt in range(1, 3):
            logger.info(f"  ⚡ [GROQ LPU ATTEMPT {groq_attempt}/2] Gemini keys exhausted. Requesting ultra-fast solution via Groq Cloud API...")
            for g_idx, groq_key in enumerate(groq_keys, 1):
                for model_name in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                    try:

                        url = "https://api.groq.com/openai/v1/chat/completions"
                        payload = json.dumps({
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are an expert AI teacher solving quiz questions for an educational course."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1
                        }).encode('utf-8')

                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {groq_key}',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                        }


                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [GROQ LPU SUCCESS] Solved on Attempt {groq_attempt}/2 via Groq ({model_name}) Key #{g_idx} -> '{clean_ans}'")
                            return clean_ans
                    except Exception as ex:
                        logger.warning(f"  ⚠️ [GROQ AI NOTICE] ({model_name} Key #{g_idx}): {ex}")
            if groq_attempt < 2:
                time.sleep(2)

    # 3. PRIORITY 3: xAI Grok API Key Pool Fallback (2 ATTEMPTS) (https://console.x.ai/)
    xai_keys = getattr(config, "XAI_API_KEYS", [])
    if not xai_keys:
        single_xai = getattr(config, "XAI_API_KEY", "").strip() or os.environ.get("XAI_API_KEY", "").strip()
        if single_xai:
            xai_keys = [single_xai]

    if xai_keys:
        for grok_attempt in range(1, 3):
            logger.info(f"  🤖 [GROK AI ATTEMPT {grok_attempt}/2] Gemini & Groq keys exhausted. Requesting solution via Grok xAI API...")
            for x_idx, xai_key in enumerate(xai_keys, 1):
                for model_name in ["grok-4.3", "grok-latest", "grok-4.20", "grok-code-fast", "grok-4.5"]:
                    try:
                        url = "https://api.x.ai/v1/chat/completions"
                        payload = json.dumps({
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are an expert AI teacher solving quiz questions for an educational course."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1
                        }).encode('utf-8')

                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {xai_key}'
                        }

                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [GROK AI SUCCESS] Solved on Attempt {grok_attempt}/2 via Grok ({model_name}) Key #{x_idx} -> '{clean_ans}'")
                            return clean_ans
                    except Exception as ex:
                        logger.warning(f"  ⚠️ [GROK AI NOTICE] ({model_name} Key #{x_idx}): {ex}")
            if grok_attempt < 2:
                time.sleep(2)



    # 3. STEPPED BACKOFF RETRY PROTOCOL: 30s -> 45s -> 60s
    logger.warning("  ⚠️ [AI INITIAL ATTEMPTS EXHAUSTED] Entering Stepped Backoff Retry Protocol (30s -> 45s -> 60s)...")
    backoff_delays = [30, 45, 60]
    for b_idx, delay_sec in enumerate(backoff_delays, 1):
        logger.warning(f"\n  ⏳ [AI RATE LIMIT BACKOFF {b_idx}/3] Waiting {delay_sec} seconds for API quota reset before Retry #{b_idx}...")
        time.sleep(delay_sec)

        # Retry ALL Gemini API Keys
        if gemini_keys:
            logger.info(f"  🧠 [BACKOFF RETRY #{b_idx}] Retrying ALL Gemini API Keys after {delay_sec}s delay...")
            for key_idx, api_key in enumerate(gemini_keys, 1):
                for model_name in models_to_try:
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
                        headers = {'Content-Type': 'application/json', 'x-goog-api-key': api_key}
                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [AI BACKOFF SUCCESS] Solved on Backoff #{b_idx} ({delay_sec}s) via Gemini ({model_name}) Key #{key_idx} -> '{clean_ans}'")
                            return clean_ans
                    except Exception:
                        pass

        # Retry ALL Groq LPU API Keys
        if groq_keys:
            logger.info(f"  ⚡ [BACKOFF RETRY #{b_idx}] Retrying ALL Groq LPU API Keys after {delay_sec}s delay...")
            for g_idx, groq_key in enumerate(groq_keys, 1):
                for model_name in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                    try:

                        url = "https://api.groq.com/openai/v1/chat/completions"
                        payload = json.dumps({
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are an expert AI teacher solving quiz questions for an educational course."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1
                        }).encode('utf-8')
                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {groq_key}',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                        }

                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [AI BACKOFF SUCCESS] Solved on Backoff #{b_idx} ({delay_sec}s) via Groq ({model_name}) Key #{g_idx} -> '{clean_ans}'")
                            return clean_ans
                    except Exception:
                        pass

        # Retry ALL Grok API Keys
        if xai_keys:
            logger.info(f"  🤖 [BACKOFF RETRY #{b_idx}] Retrying ALL Grok xAI API Keys after {delay_sec}s delay...")

            for x_idx, xai_key in enumerate(xai_keys, 1):
                for model_name in ["grok-4.3", "grok-latest", "grok-4.20", "grok-code-fast", "grok-4.5"]:
                    try:


                        url = "https://api.x.ai/v1/chat/completions"
                        payload = json.dumps({
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": "You are an expert AI teacher solving quiz questions for an educational course."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.1
                        }).encode('utf-8')
                        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {xai_key}'}
                        req = urllib.request.Request(url, data=payload, headers=headers)
                        res = urllib.request.urlopen(req, timeout=12)
                        resp_data = json.loads(res.read().decode('utf-8'))
                        ans_text = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                        if clean_ans:
                            logger.info(f"  🧠 [AI BACKOFF SUCCESS] Solved on Backoff #{b_idx} ({delay_sec}s) via Grok ({model_name}) Key #{x_idx} -> '{clean_ans}'")
                            return clean_ans
                    except Exception:
                        pass

    logger.error("  ❌ [AI BACKOFF RETRIES EXHAUSTED] AI Solver failed after 30s, 45s, and 60s backoff retries.")
    return None















async def login_diksha(page, username=None, password=None):
    """
    STEP-01 & STEP-02: Navigates to DIKSHA login page, handles landing page button,
    enters credentials, clicks LOGIN, and waits patiently for server authentication redirect.
    """
    user = username or next(iter(config.USER_CREDENTIALS.keys()), "")
    pwd = password or config.USER_CREDENTIALS.get(user, "")


    logger.info("[STEP 01] Navigating to DIKSHA Portal...")
    try:
        await page.goto(config.AUTH_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
    except Exception as e:
        logger.warning(f"  --> Initial page load notice: {e}. Retrying navigation...")
        try:
            await page.goto(config.AUTH_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
        except Exception:
            pass

    # Handle landing page "LOGIN with DIKSHA" button if present
    landing_btn = page.locator("a:has-text('LOGIN with DIKSHA'), button:has-text('LOGIN with DIKSHA'), a[href*='lms=diksha2'], a:has-text('Login')").first
    if await landing_btn.count() > 0 and await landing_btn.is_visible():
        logger.info("  --> Clicking 'LOGIN with DIKSHA' landing button...")
        await landing_btn.click(force=True)
        await page.wait_for_timeout(3000)

    logger.info("[STEP 02] Entering login credentials...")
    username_field = page.locator("#username, input[name='username']").first
    password_field = page.locator("#password, input[name='password']").first
    login_btn = page.locator("#kc-login, #login, input[type='submit'][value*='LOGIN'], input[value='LOGIN'], button:has-text('LOGIN'), button[type='submit']").first

    if await username_field.count() > 0 and await username_field.is_visible():
        if user:
            await username_field.fill(user)
            logger.info("  --> Username entered.")
        else:
            logger.warning("  --> Username is empty! Set DIKSHA_USERNAME in config or environment.")

        if pwd:
            await password_field.fill(pwd)
            logger.info("  --> Password entered.")
        else:
            logger.warning("  --> Password is empty! Set DIKSHA_PASSWORD in config or environment.")

        if user and pwd:
            logger.info("  --> Clicking LOGIN button & submitting Keycloak form...")
            try:
                await login_btn.click(force=True)
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            try:
                await password_field.press("Enter")
            except Exception:
                pass

            logger.info("  --> Waiting for DIKSHA server SSO authentication redirect (DIKSHA server slow mode)...")
            
            # Wait up to 60 seconds for slow DIKSHA server SSO redirect
            for sec in range(60):
                if "course_listing.php" in page.url or ("learning.diksha.gov.in" in page.url and "login.php" not in page.url):
                    logger.info(f"  --> Login redirect successful after {sec+1}s! (Current URL: {page.url})")
                    break
                await page.wait_for_timeout(1000)

            await page.wait_for_timeout(3000)
    else:
        logger.info("  --> Login form not visible or user already authenticated.")










async def navigate_to_my_learning(page):
    """
    STEP-03: Clicks 'My Learning' side navigation bar icon.
    """
    logger.info("[STEP 03] Navigating to 'My Learning'...")
    try:
        my_learning_link = page.locator("a[href*='course_listing.php'], a:has-text('My Learning'), span:has-text('My Learning'), [data-original-title='My Learning']").first
        if await my_learning_link.count() > 0 and await my_learning_link.is_visible():
            logger.info("  --> Clicking 'My Learning' sidebar button...")
            await my_learning_link.click(force=True)
            await page.wait_for_timeout(4000)
        else:
            if "course_listing.php" not in page.url:
                logger.info("  --> Opening My Learning course listing dashboard...")
                await page.goto("https://learning.diksha.gov.in/diksha/course_listing.php", wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
        logger.info(f"  --> Successfully opened 'My Learning' (Current URL: {page.url}).")
    except Exception as e:
        logger.warning(f"  --> Sidebar click notice: {e}")
        if "course_listing.php" not in page.url:
            await page.goto("https://learning.diksha.gov.in/diksha/course_listing.php", wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)





async def fetch_enrolled_courses(page):
    """
    STEP-04 & STEP-05: Fetches BOTH Ongoing Courses (#pills-inprogress-tab)
    and Finished Courses (#pills-completed-tab), extracting title, url, and % progress.
    """
    all_courses = []
    seen_urls = set()

    # 1. Fetch Ongoing Courses
    logger.info("[STEP 04] Selecting 'Ongoing Courses' tab...")
    ongoing_tab = page.locator("#pills-inprogress-tab, a:has-text('Ongoing Courses')").first
    if await ongoing_tab.count() > 0 and await ongoing_tab.is_visible():
        try:
            await ongoing_tab.click()
            await page.wait_for_timeout(2000)
        except Exception:
            pass

    # Wait up to 15 seconds for course card elements to hydrate on DIKSHA course_listing.php page
    cards = page.locator("#pills-inprogress .course-library-link, #pills-inprogress .library-card, .course-library-link, .library-card, a[href*='course.php']")
    for _ in range(15):
        if await cards.count() > 0:
            break
        await page.wait_for_timeout(1000)

    count = await cards.count()


    for i in range(count):
        card = cards.nth(i)
        title_text = f"Course #{i+1}"
        title_el = card.locator("h4, .title, bdi").first
        if await title_el.count() > 0:
            title_attr = await title_el.get_attribute("title") or await title_el.get_attribute("data-original-title") or ""
            inner_t = (await title_el.inner_text()).strip()
            raw_title = title_attr.strip() if (title_attr and len(title_attr.strip()) > len(inner_t)) else inner_t
            title_text = raw_title.replace("Course Title  :", "").replace("Course Title :", "").strip()

        href = await card.get_attribute("data-href")
        if not href:
            link_el = card.locator("a[href*='course.php']").first
            if await link_el.count() > 0:
                href = await link_el.get_attribute("href")

        if href and href not in seen_urls:
            seen_urls.add(href)
            progress_pct = 0
            
            # Extract Progress % from card inner text ("17% Completed") or style attribute ("width: 17%")
            try:
                card_text = (await card.inner_text()).strip()
                pct_match = re.search(r"(\d{1,3})\s*%\s*(?:Completed)?", card_text, re.IGNORECASE)
                if pct_match:
                    progress_pct = int(pct_match.group(1))
                else:
                    pbar = card.locator(".progress-bar").first
                    if await pbar.count() > 0:
                        style_attr = await pbar.get_attribute("style") or ""
                        m_style = re.search(r"width:\s*(\d{1,3})%", style_attr)
                        if m_style:
                            progress_pct = int(m_style.group(1))
            except Exception:
                pass

            full_url = href if href.startswith("http") else f"https://learning.diksha.gov.in/diksha/{href.lstrip('/')}"
            all_courses.append({
                "index": len(all_courses) + 1,
                "title": title_text,
                "url": full_url,
                "progress_pct": progress_pct,
                "status": "Ongoing",
                "icon": "⌛"
            })

    # 2. Fetch Finished Courses
    logger.info("[STEP 05] Selecting 'Finished Courses' tab...")
    finished_tab = page.locator("#pills-completed-tab, a:has-text('Finished Courses'), [data-completed='true']").first
    if await finished_tab.count() > 0 and await finished_tab.is_visible():
        try:
            await finished_tab.click()
            await page.wait_for_timeout(2000)
            
            f_cards = page.locator("#pills-completed .course-library-link, #pills-completed .library-card")
            f_count = await f_cards.count()
            if f_count == 0:
                f_cards = page.locator(".course-library-link, .library-card")
                f_count = await f_cards.count()

            for i in range(f_count):
                card = f_cards.nth(i)
                title_text = f"Finished Course #{i+1}"
                title_el = card.locator("h4, .title, bdi").first
                if await title_el.count() > 0:
                    title_attr = await title_el.get_attribute("title") or await title_el.get_attribute("data-original-title") or ""
                    inner_t = (await title_el.inner_text()).strip()
                    raw_title = title_attr.strip() if (title_attr and len(title_attr.strip()) > len(inner_t)) else inner_t
                    title_text = raw_title.replace("Course Title  :", "").replace("Course Title :", "").strip()

                href = await card.get_attribute("data-href")
                if not href:
                    link_el = card.locator("a[href*='course.php']").first
                    if await link_el.count() > 0:
                        href = await link_el.get_attribute("href")

                if href and href not in seen_urls:
                    seen_urls.add(href)
                    full_url = href if href.startswith("http") else f"https://learning.diksha.gov.in/diksha/{href.lstrip('/')}"
                    all_courses.append({
                        "index": len(all_courses) + 1,
                        "title": title_text,
                        "url": full_url,
                        "progress_pct": 100,
                        "status": "Finished",
                        "icon": "🏆"
                    })
        except Exception as ex:
            logger.warning(f"Notice fetching finished courses: {ex}")

    # 3. Switch browser view back to 'Ongoing Courses' tab
    logger.info("  --> Switching browser view back to 'Ongoing Courses' tab...")
    if await ongoing_tab.count() > 0 and await ongoing_tab.is_visible():
        try:
            await ongoing_tab.click()
            await page.wait_for_timeout(1000)
        except Exception:
            pass

    return all_courses


def get_real_terminal_columns(text):
    """
    Calculates true terminal display columns by ignoring non-spacing combining diacritic marks
    (like Bengali/Devanagari vowel signs), which attach to base consonants as a single visual glyph.
    """
    cols = 0
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ('Mn', 'Me', 'Cf'):
            continue
        cols += 1
    return cols


def get_real_terminal_columns(text):
    """
    Calculates true terminal display columns by ignoring non-spacing combining diacritic marks
    (like Bengali/Devanagari vowel signs), which attach to base consonants as a single visual glyph.
    """
    cols = 0
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ('Mn', 'Me', 'Cf'):
            continue
        cols += 1
    return cols


def pad_title_fixed(text, target_width=45):
    """
    Pads or truncates course titles to exact 45 real visual terminal columns,
    guaranteeing 100% straight vertical column alignment across Bengali, Urdu, Hindi, and English.
    """
    clean_t = text.strip()
    real_cols = get_real_terminal_columns(clean_t)
    
    if real_cols > target_width:
        res = ""
        curr_c = 0
        for ch in clean_t:
            cat = unicodedata.category(ch)
            if cat in ('Mn', 'Me', 'Cf'):
                res += ch
                continue
            if curr_c >= target_width - 3:
                break
            res += ch
            curr_c += 1
        rem_spaces = target_width - (curr_c + 3)
        return res + "..." + (" " * max(0, rem_spaces))
    else:
        rem_spaces = target_width - real_cols
        return clean_t + (" " * max(0, rem_spaces))









def display_interactive_course_menu(courses):
    """
    Renders CMD menu listing both Ongoing and Finished courses matching design mockup with rich colors.
    """
    if not courses:
        print("\n\033[38;5;51m\033[1m" + "="*67)
        print("  🎓 DIKSHA+ ENROLLED COURSES (0 COURSES FOUND)")
        print("="*67 + "\033[0m\n")
        return None

    ongoing_list = [c for c in courses if c['status'] == 'Ongoing']
    finished_list = [c for c in courses if c['status'] == 'Finished']

    print("\n\033[38;5;51m\033[1m" + "="*67)
    print(f"  🎓 DIKSHA+ ENROLLED COURSES ({len(ongoing_list)} ONGOING • {len(finished_list)} FINISHED)")
    print("="*67 + "\033[0m\n")

    if ongoing_list:
        print(" \033[38;5;82m\033[1m⚡ ONGOING COURSES:\033[0m")
        for c in ongoing_list:
            pct = c['progress_pct']
            filled = int(round(pct / 10))
            filled_str = "█" * filled
            empty_str = "░" * (10 - filled)
            bar = f"\033[38;5;46m[{filled_str}\033[38;5;238m{empty_str} \033[38;5;220m{pct:>3}%\033[38;5;46m]\033[0m"
            formatted_title = pad_title_fixed(c['title'], 45)
            print(f"  \033[38;5;220m[{c['index']:02d}]\033[0m \033[38;5;231m{formatted_title}\033[0m {bar} \033[38;5;214m{c['icon']} {c['status']}\033[0m")
        print()

    if finished_list:
        print(" \033[38;5;207m\033[1m✨ FINISHED COURSES:\033[0m")
        for c in finished_list:
            pct = c['progress_pct']
            filled_str = "█" * 10
            bar = f"\033[38;5;207m[{filled_str} \033[38;5;220m{pct:>3}%\033[38;5;207m]\033[0m"
            formatted_title = pad_title_fixed(c['title'], 45)
            print(f"  \033[38;5;220m[{c['index']:02d}]\033[0m \033[38;5;231m{formatted_title}\033[0m {bar} \033[38;5;220m{c['icon']} {c['status']}\033[0m")

        print()




    print("\033[38;5;240m-------------------------------------------------------------------\033[0m")

    import os
    env_course = os.getenv("SELECTED_COURSE", "").strip()

    if not sys.stdin.isatty():
        env_course = os.getenv("SELECTED_COURSE", "").strip()
        if env_course:
            clean_env_c = env_course.lower()
            if clean_env_c == "all":
                logger.info(f"  🎯 [RAILWAY COURSE SELECTION] SELECTED_COURSE='all' detected. Processing ALL {len(courses)} enrolled courses.")
                return courses
            elif env_course.isdigit():
                c_idx = int(env_course)
                if 1 <= c_idx <= len(courses):
                    logger.info(f"  🎯 [RAILWAY COURSE SELECTION] Selected Course #{c_idx}: '{courses[c_idx-1]['title']}'.")
                    return [courses[c_idx - 1]]
            else:
                # Match by course title keyword! (e.g. "Power of Audio", "audio", "NEP 2020", "NEP", "Action Research")
                matched_c = None
                for c in courses:
                    c_title = c.get("title", "")
                    if clean_env_c in c_title.lower() or c_title.lower() in clean_env_c:
                        matched_c = c
                        break

                if matched_c:
                    logger.info(f"  🎯 [RAILWAY COURSE SELECTION] Matched Course by Keyword '{env_course}': Course #{matched_c['index']} - '{matched_c['title']}'.")
                    return [matched_c]

        logger.warning("\n===================================================================\n ⏸️ [MANUAL COURSE CONFIGURATION REQUIRED ON RAILWAY]\n No SELECTED_COURSE variable configured in Railway Variables.\n Default auto-run selection is DISABLED per user preference.\n Please set SELECTED_COURSE in Railway Variables (e.g., 1, 2, 3, or all) to start.\n===================================================================\n")
        return None






    try:
        choice = input(f" \033[38;5;51m👉 Select course number to automate (1-{len(courses)}) [Enter for 1]: \033[0m").strip()
        if not choice:
            choice = "1"
        
        val = int(choice)
        if val == 0:
            return courses
        elif 1 <= val <= len(courses):
            return [courses[val - 1]]
        else:
            print("  [-] Invalid selection. Processing first course by default.")
            return [courses[0]]
    except Exception:
        print("  [-] Processing first course by default.")
        return [courses[0]]



async def close_activity_modal(page):
    """
    Closes activity modal using the spec close button: <button class="close" data-dismiss="modal">
    and ensures modal container backdrop is dismissed.
    """
    close_btns = page.locator("button.close[data-dismiss='modal'], button.close, [data-dismiss='modal']")
    if await close_btns.count() > 0:
        for i in range(await close_btns.count()):
            btn = close_btns.nth(i)
            if await btn.is_visible():
                logger.info("  --> Clicking activity close button (x)...")
                await btn.click(force=True)
                await page.wait_for_timeout(1500)
                break

    # Dismiss leftover modal backdrop / container if present
    try:
        popup = page.locator("#container-popup.show, .modal.show").first
        if await popup.count() > 0 and await popup.is_visible():
            handle = await popup.element_handle()
            if handle:
                await page.evaluate("el => el.style.display = 'none'", handle)
    except Exception:
        pass
    await page.wait_for_timeout(1500)


async def wait_for_server_checkmark(page, timeout=15):
    """
    Waits for server 100% checkmark pie icon: <i class="fas fa-check"></i>
    """
    logger.info("  --> Waiting for server 100% checkmark update...")
    start = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start) < timeout:
        check_icon = page.locator(config.SELECTORS["progress_check_icon"]).first
        if await check_icon.count() > 0 and await check_icon.is_visible():
            logger.info("  --> Server 100% checkmark confirmed!")
            return True
        await page.wait_for_timeout(2000)
    logger.info("  --> Checkmark sync window completed.")
    return False

async def process_video_activity(page, view_button):
    """
    STEP-07 (Video Activity - act_type="url"):
    Implements technical specification for Video Acceleration & Telemetry:
      1. Nested iFrame & Shadow DOM Support (scans all frames for <video>)
      2. 15s Warm-up Buffer @ 1.0x speed (telemetry session init)
      3. Dynamic Acceleration: 16x speed (duration >= 5m) or 10x speed (duration < 5m)
      4. Stall & Pause Recovery (auto-rewind 5% & resume play if stuck)
      5. 45s Final Buffer @ 1.0x speed (natural ended event & 100% progress telemetry)
      6. Video 10s-15s Checkmark Verification & 1-Time Reload/Replay Recovery Engine
    """
    # Check for saved progress percentage badge on DOM row (e.g. "55%")
    row_saved_pct = 0
    try:
        parent_row = view_button.locator("xpath=./ancestor::*[contains(@class, 'activity') or contains(@class, 'row') or contains(@class, 'item') or self::li or self::div][1]")
        if await parent_row.count() > 0:
            row_text = await parent_row.inner_text()
            import re
            m = re.search(r'(\d{1,2})%', row_text)
            if m:
                row_saved_pct = int(m.group(1))
    except Exception:
        row_saved_pct = 0

    logger.info("[VIDEO ACTIVITY] Opening video module...")
    await view_button.click(force=True)
    await page.wait_for_timeout(3000)

    # 1. Nested iFrame Support: Locate <video> across main page & all frames
    target_frame = page
    video_locator = page.locator("video").first
    
    if await video_locator.count() == 0 or not await video_locator.is_visible():
        for frame in page.frames:
            f_v = frame.locator("video").first
            if await f_v.count() > 0:
                target_frame = frame
                video_locator = f_v
                logger.info(f"  --> Found video element inside nested frame: {frame.url}")
                break

    # Play button click attempt
    play_btn = target_frame.locator("button:has-text('Play'), .vjs-play-control, .media-play-button, .play-button").first
    if await play_btn.count() > 0 and await play_btn.is_visible():
        try:
            await play_btn.click(force=True)
            logger.info("  --> Video playback started via Play button.")
        except Exception:
            pass

    # Ensure video plays muted via HTML5 Video API (preserving current video position)
    try:
        await target_frame.evaluate("""
            async () => {
                const vids = document.querySelectorAll('video');
                vids.forEach(v => {
                    v.muted = true;
                    v.volume = 0.0;
                    v.playbackRate = 1.0;
                    v.play().catch(() => {});
                });

                // Attempt to click 360p / 240p lower resolution option on Sunbird / VideoJS player UI
                const qualBtns = Array.from(document.querySelectorAll('.vjs-quality-selector, .vjs-resolution-button, .quality-setting, option, .vjs-menu-item, button'));
                const lowOpt = qualBtns.find(el => {
                    const txt = (el.innerText || el.textContent || '').toLowerCase();
                    return txt.includes('360') || txt.includes('240') || txt.includes('low');
                });
                if (lowOpt) {
                    lowOpt.click();
                }
            }
        """)
        logger.info("  --> Video playback started (Muted & 360p Low Resolution preference set).")
    except Exception as e:
        logger.warning(f"  --> Video play init notice: {e}")

    await page.wait_for_timeout(2000)

    # Get Video Duration
    duration = 0.0
    try:
        duration = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.duration : 0; }"))
    except Exception:
        duration = 0.0

    if duration and not (duration != duration):  # Check for valid float / NaN
        logger.info(f"  --> Video Duration: {int(duration)} seconds ({int(duration//60)}m {int(duration%60)}s)")

        # Check for saved progress (from DIKSHA DOM row badge e.g. 55% or HTML5 video currentTime)
        initial_time = 0.0
        try:
            initial_time = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.currentTime : 0; }"))
        except Exception:
            initial_time = 0.0

        if row_saved_pct > 0 and duration > 0:
            target_seek = (row_saved_pct / 100.0) * duration
            if initial_time < target_seek - 10:
                initial_time = target_seek
                await target_frame.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) {{ v.currentTime = {target_seek}; }} }}")
                logger.info(f"  --> [SAVED PROGRESS RESUMED] Detected {row_saved_pct}% saved progress badge on DIKSHA item row! Seeking video to {int(target_seek)}s / {int(duration)}s ({row_saved_pct}%) and resuming...")
            else:
                saved_pct = min(99, max(1, int((initial_time / duration) * 100)))
                logger.info(f"  --> [SAVED PROGRESS RESUMED] Video already at {saved_pct}% ({int(initial_time)}s / {int(duration)}s)! Resuming dynamically from current position...")
        elif initial_time > 1.0 and duration > 0:
            saved_pct = min(99, max(1, int((initial_time / duration) * 100)))
            logger.info(f"  --> [SAVED PROGRESS RESUMED] Video already at {saved_pct}% ({int(initial_time)}s / {int(duration)}s)! Resuming dynamically from current position...")



        # 2. ALWAYS 15s Warm-up Buffer @ 1.0x Speed (for telemetry initialization)
        logger.info("  --> 15s Warm-up Buffer: playing at 1.0x speed for session telemetry initialization...")
        await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.playbackRate = 1.0; if (v.paused) v.play(); } }")
        await asyncio.sleep(min(15, max(1, int(duration * 0.2))))

        # 3. Dynamic Playback Acceleration: 16x (>= 5 min) or 10x (< 5 min)
        if duration >= 300:
            speed = 16.0
            logger.info("  --> Dynamic Acceleration: Applying 16x Speed (Long Video >= 5 min)...")
        else:
            speed = 10.0
            logger.info("  --> Dynamic Acceleration: Applying 10x Speed (Short Video < 5 min)...")

        # Fast forward loop with Stall & Pause Recovery
        target_final_buffer_time = max(0, duration - 45)
        
        while True:
            await check_pause_status(page)
            cur_time = 0.0
            is_paused = False
            ready_state = 4
            
            try:
                state_info = await target_frame.evaluate("""
                    () => {
                        const v = document.querySelector('video');
                        return v ? { time: v.currentTime, paused: v.paused, readyState: v.readyState } : { time: 0, paused: true, readyState: 0 };
                    }
                """)
                cur_time = state_info.get("time", 0.0)
                is_paused = state_info.get("paused", False)
                ready_state = state_info.get("readyState", 4)
            except Exception:
                break

            if cur_time >= target_final_buffer_time or cur_time >= duration - 1:
                break

            # 4. Stall & Pause Recovery: Wait 10s for buffering window, then rewind 30s & adjust speed
            if is_paused or ready_state < 2:
                logger.warning("  --> [STALL RECOVERY] Video buffering/paused! Waiting 10s for DIKSHA server buffer...")
                await asyncio.sleep(10)
                
                # Re-verify if video resumed on its own after 10s buffering window
                try:
                    re_info = await target_frame.evaluate("""
                        () => {
                            const v = document.querySelector('video');
                            return v ? { paused: v.paused, readyState: v.readyState } : { paused: true, readyState: 0 };
                        }
                    """)
                    if re_info.get("paused", False) or re_info.get("readyState", 0) < 2:
                        logger.warning("  --> [STALL RECOVERY] Still buffering after 10s! Rewinding 30s back & resuming play()...")
                        await target_frame.evaluate("""
                            () => {
                                const v = document.querySelector('video');
                                if (v) {
                                    v.currentTime = Math.max(0, v.currentTime - 30);
                                    v.playbackRate = 4.0;
                                    v.play().catch(() => {});
                                }
                            }
                        """)
                except Exception:
                    pass

            else:

                # Set accelerated speed & advance
                await target_frame.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) {{ v.playbackRate = {speed}; if (v.paused) v.play(); }} }}")
                await asyncio.sleep(2)




        # 5. 45s Final Buffer @ 1.0x Speed with Auto-Play & Network Stall Recovery Safeguard
        logger.info("  --> 45s Final Buffer: slowing down to 1.0x speed for natural ended event & 100% progress telemetry...")
        await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.playbackRate = 1.0; if (v.paused) v.play(); } }")
        
        final_wait = min(45, max(10, int(duration - cur_time)))
        
        # Safeguard Loop: Periodically verifies video is playing, auto-resuming if paused by network/browser
        start_wait_t = time.time()
        while time.time() - start_wait_t < final_wait:
            await check_pause_status(page)
            try:
                v_st = await target_frame.evaluate("""
                    () => {
                        const v = document.querySelector('video');
                        if (!v) return { found: false };
                        if (v.paused && v.currentTime < v.duration) {
                            v.play().catch(() => {});
                        }
                        return { found: true, paused: v.paused, currentTime: v.currentTime };
                    }
                """)
                if v_st and v_st.get("found") and v_st.get("paused"):
                    logger.info("  🛡️ [AUTOPLAY SAFEGUARD] Video was paused. Auto-triggered video.play() to keep playback active.")
            except Exception:
                pass
            await asyncio.sleep(1.5)
        
        # Trigger natural ended event dispatch
        try:
            await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.dispatchEvent(new Event('ended')); } }")
        except Exception:
            pass
    else:
        # Fallback if duration is unavailable
        logger.info("  --> Video playback active (default watch duration)...")
        start_wait_t = time.time()
        while time.time() - start_wait_t < config.MIN_VIDEO_WATCH_SECONDS:
            await check_pause_status(page)
            try:
                await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v && v.paused) v.play().catch(() => {}); }")
            except Exception:
                pass
            await asyncio.sleep(1.5)

    # Close video modal
    await close_activity_modal(page)

    
    # 6. Video 10s-15s Checkmark Verification & 1-Time Reload/Replay Recovery Engine
    logger.info("  --> [VIDEO CHECKMARK] Waiting 10s to 15s specifically for video 100% checkmark...")
    checkmark_ok = await wait_for_server_checkmark(page, timeout=15)

    if not checkmark_ok:
        logger.warning("  --> [VIDEO RECOVERY] 100% checkmark not confirmed (partial progress like 45%/97% detected). Reloading video 1 time to complete 100%...")
        try:
            await view_button.click(force=True)
            await page.wait_for_timeout(3000)
            
            # Replay final 10 seconds at 1.0x speed and dispatch ended event
            await target_frame.evaluate("""
                async () => {
                    const v = document.querySelector('video');
                    if (v) {
                        v.currentTime = Math.max(0, v.duration - 10);
                        v.playbackRate = 1.0;
                        await v.play().catch(() => {});
                        v.dispatchEvent(new Event('ended'));
                    }
                }
            """)
            await asyncio.sleep(10)
            await close_activity_modal(page)
            logger.info("  --> Re-checking DIKSHA server for 100% video checkmark...")
            await wait_for_server_checkmark(page, timeout=15)
        except Exception as ex:
            logger.warning(f"  --> Video reload recovery notice: {ex}")

async def check_pause_status(page=None):
    global IS_PAUSED
    if IS_PAUSED:
        if page:
            try:
                await page.evaluate("() => { const v = document.querySelector('video'); if (v) v.pause(); }")
            except Exception:
                pass
        logger.info("\n" + "=" * 65 + "\n   ⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...\n" + "=" * 65 + "\n")
        while IS_PAUSED:
            await asyncio.sleep(0.2)
        logger.info("   ▶️ [AUTOMATION RESUMED] Continuing execution seamlessly...\n")
        if page:
            try:
                await page.evaluate("() => { const v = document.querySelector('video'); if (v) v.play(); }")
            except Exception:
                pass



async def process_pdf_activity(page, view_button):
    """
    STEP-07 (PDF Activity - act_type="resource"):
    Implements technical specification for PDF Reader:
      1. Automated Page Flipping (simulates PageDown & End key presses)
      2. Reading Time Simulation (maintains page reading intervals)
      3. End-of-Doc Scroll (auto-scrolls viewer container to exact bottom for checkmarks)
    """
    logger.info("[PDF ACTIVITY] Opening PDF document resource...")
    await view_button.click(force=True)
    await page.wait_for_timeout(3000)

    # 1. Automated Page Flipping & Reading Time Simulation
    logger.info("  --> Automated Page Flipping: simulating PageDown key presses...")
    for flip in range(4):
        await check_pause_status()
        await page.keyboard.press("PageDown")
        await page.wait_for_timeout(2500)

    # 3. End-of-Doc Scroll: Auto-scroll viewer container to exact bottom
    logger.info("  --> End-of-Doc Scroll: scrolling PDF viewer container to exact bottom...")
    await page.evaluate("""
        () => {
            const containers = document.querySelectorAll('.pdf-viewer, embed, iframe, .document-container, div[class*="pdf"], .modal-body, .card-body');
            containers.forEach(c => {
                if (c) c.scrollTop = c.scrollHeight;
            });
            window.scrollTo(0, document.body.scrollHeight);
        }
    """)
    await page.keyboard.press("End")
    await page.wait_for_timeout(3000)

    # Close modal and wait for server checkmark
    await close_activity_modal(page)
    await wait_for_server_checkmark(page)


async def process_h5p_activity(page, view_button, answer_key, course_title=None):
    """
    STEP-07 (H5P Interactive Quiz - act_type="h5pactivity"):
    Clicks View, waits for container, presses 'Start Quiz', answers radio questions,
    clicks Next, Check, Finish, and closes modal.
    """
    logger.info("[H5P ACTIVITY] Opening H5P interactive content...")
    await view_button.click()
    await page.wait_for_timeout(4000)

    start_btn = page.locator(config.SELECTORS["h5p_start_button"]).first
    if await start_btn.count() > 0 and await start_btn.is_visible():
        logger.info("  --> Pressing 'Start Quiz' button...")
        await start_btn.click()
        await page.wait_for_timeout(2000)

    # Radio button option selection loop with Smart Auto-Learning AI Cache & Live Solver
    answers_list = extract_all_qa_items(answer_key)
    for question_step in range(15):
        await check_pause_status()
        h5p_frame = page
        for f in page.frames:
            try:
                if await f.locator(".h5p-question-text, .h5p-content, .h5p-question-introduction").count() > 0:
                    h5p_frame = f
                    break
            except Exception:
                pass

        q_text_screen = ""
        try:
            q_elem = h5p_frame.locator(".h5p-question-introduction, .h5p-question-text, .h5p-task-description").first
            if await q_elem.count() > 0 and await q_elem.is_visible():
                raw_q = (await q_elem.inner_text()).strip()
                q_text_screen = re.sub(r'^(?:question\s*\d+[:.]?|\d+[:.]?)\s*', '', raw_q, flags=re.IGNORECASE).strip()
        except Exception:
            pass

        option_elements = h5p_frame.locator(".h5p-answer, .h5p-radio-button, label.h5p-joubelui-button, .h5p-alternative-container")
        opt_count = await option_elements.count()
        screen_opts = []
        for o_idx in range(opt_count):
            try:
                raw_o = await option_elements.nth(o_idx).inner_text()
                c_opt = re.sub(r'^(?:[a-d][.)]|option\s*[a-d][:.]?|\d+[.)])\s*', '', raw_o, flags=re.IGNORECASE).strip()
                if c_opt:
                    screen_opts.append(c_opt)
            except Exception:
                pass

        if q_text_screen:
            logger.info("\n" + "  " + "-" * 75)
            logger.info(f"  ❓ [Q-{question_step + 1} FULL QUESTION]: {q_text_screen}")
            if screen_opts:
                logger.info("  📋 [OPTION CHOICES]:")
                for idx, opt_text in enumerate(screen_opts):
                    letter = chr(65 + idx) if idx < 26 else str(idx + 1)
                    logger.info(f"     [{letter}] {opt_text}")

        matched_answer_text = None

        # 1. Check Auto-Learning JSON Cache
        if q_text_screen and answers_list:
            clean_screen_q = re.sub(r'[^\w\s]', '', q_text_screen.lower())
            screen_words = set(w for w in clean_screen_q.split() if len(w) >= 3) if clean_screen_q else set()
            for item in answers_list:
                json_q = (item.get("question") or item.get("question_keyword") or "").strip().lower()
                clean_json_q = re.sub(r'[^\w\s]', '', json_q)
                json_words = set(w for w in clean_json_q.split() if len(w) >= 3)
                if clean_json_q and clean_screen_q and (clean_json_q == clean_screen_q or (json_words and screen_words and json_words == screen_words)):
                    matched_answer_text = (item.get("answer") or item.get("correct_option") or "").strip()
                    logger.info(f"  ⚡ [H5P VERIFIED JSON 100% MATCH Q-{question_step + 1}] Target Answer: '{matched_answer_text}'")
                    break

        # 2. AI Live Solver Fallback
        if not matched_answer_text and q_text_screen:
            ai_solved = solve_question_with_ai(q_text_screen, screen_opts)
            if ai_solved:
                matched_answer_text = ai_solved
                logger.info(f"  🧠 [H5P AI LIVE SOLVER Q-{question_step + 1}] Solved: '{matched_answer_text}'")
                save_auto_learned_qa(course_title, 1, "H5P Interactive Quiz", 1, "H5P Interactive Quiz", q_text_screen, ai_solved)

        # Click matching option or fallback to first radio
        selected = False
        if matched_answer_text and opt_count > 0:
            clean_target = re.sub(r'[^\w\s]', '', matched_answer_text.lower())
            for o_idx in range(opt_count):
                try:
                    opt_el = option_elements.nth(o_idx)
                    opt_txt = await opt_el.inner_text()
                    clean_opt = re.sub(r'[^\w\s]', '', opt_txt.lower())
                    if clean_target in clean_opt or clean_opt in clean_target:
                        await opt_el.click(force=True)
                        selected = True
                        opt_let = chr(65 + o_idx) if o_idx < 26 else str(o_idx + 1)
                        logger.info(f"  🎯 [SELECTED OPTION {opt_let}] Selected Radio Button [{opt_let}] for Answer: '{matched_answer_text}'.")
                        logger.info("  " + "-" * 75 + "\n")
                        break
                except Exception:
                    pass


        if not selected:
            radios = h5p_frame.locator("input[type='radio'], .h5p-joubelui-button, .h5p-radio-button")
            if await radios.count() > 0:
                first_radio = radios.first
                if await first_radio.is_visible():
                    await first_radio.click(force=True)
                    logger.info(f"  --> Selected default H5P answer option for question {question_step + 1}.")

        await page.wait_for_timeout(1000)
        next_btn = h5p_frame.locator(config.SELECTORS["h5p_next_button"]).first
        if await next_btn.count() > 0 and await next_btn.is_visible():
            await next_btn.click(force=True)
            await page.wait_for_timeout(1500)
        else:
            break


    # Click Check and Finish
    check_btn = page.locator(config.SELECTORS["h5p_check_button"]).first
    if await check_btn.count() > 0 and await check_btn.is_visible():
        logger.info("  --> Clicking 'Check' answer button...")
        await check_btn.click()
        await page.wait_for_timeout(1500)

    finish_btn = page.locator(config.SELECTORS["h5p_finish_button"]).first
    if await finish_btn.count() > 0 and await finish_btn.is_visible():
        logger.info("  --> Clicking 'Finish' button...")
        await finish_btn.click()
        await page.wait_for_timeout(1500)

    await close_activity_modal(page)

async def process_quiz_assessment(page, view_button, answer_key, module_name=None, module_no=None, sub_name=None, sub_no=None, course_title=None):

    """
    STEP-07 (Formative Assessment - act_type="quiz"):
    Identifies exact module (number/name) & subsection (number/name) context,
    matches questions against answer key metadata, and executes assessment.
    """
    if module_name or sub_name:
        ctx_str = f"Module #{module_no or 1} ('{module_name or ''}') || Subsection #{sub_no or 1} ('{sub_name or ''}')"
        logger.info(f"[FORMATIVE ASSESSMENT] Opening Assessment for {ctx_str}...")
    else:

        logger.info("[FORMATIVE ASSESSMENT] Opening Assessment...")

    await view_button.click(force=True)
    logger.info("  --> Waiting 5 seconds for DIKSHA assessment modal & banner popup to render...")
    await page.wait_for_timeout(5000)

    # 1. Close inner "Stay Calm" banner popup across main page and all frames
    closed_banner = False
    for frame_target in [page] + page.frames:
        try:
            banner_close = frame_target.locator("button.quiz-popup-close, .quiz-popup-close, button[class*='quiz-popup-close']").first
            if await banner_close.count() > 0 and await banner_close.is_visible():
                logger.info("  --> Closing 'Stay Calm' inner GIF banner popup (button.quiz-popup-close)...")
                await banner_close.click(force=True)
                closed_banner = True
                await page.wait_for_timeout(2000)
                break
        except Exception:
            pass

    # Backup DOM JavaScript cleanup if Playwright locator didn't close it
    if not closed_banner:
        logger.info("  --> Executing DOM JS trigger for inner quiz popup banner...")
        for frame_target in [page] + page.frames:
            try:
                await frame_target.evaluate("""() => {
                    const btn = document.querySelector('.quiz-popup-close, button[class*="quiz-popup-close"], button.quiz-popup-close');
                    if (btn) { btn.click(); return true; }
                    const wrapper = document.querySelector('.quiz-popup-wrapper, .quiz-popup-glass');
                    if (wrapper) { wrapper.remove(); return true; }
                    return false;
                }""")
            except Exception:
                pass
        await page.wait_for_timeout(2000)

    # 2. Locate and click 'Start Assessment' / 'Continue Assessment' / 'Answer the questions' button across page and all frames
    start_assessment_btn = None
    target_frame = page

    start_selectors = [
        "a:has-text('Answer the questions')",
        "button:has-text('Answer the questions')",
        "input[value*='Answer the questions']",
        "a:has-text('Complete Feedback')",
        "button:has-text('Complete Feedback')",
        "button.submit-feed-btn",
        "#submitFeedbackBtn11",
        "button:has-text('Re-attempt Assessment')",
        "input[value*='Re-attempt Assessment']",
        "a:has-text('Re-attempt Assessment')",
        "button:has-text('Continue Assessment')",
        "input[value*='Continue Assessment']",
        "a:has-text('Continue Assessment')",
        "button:has-text('Start Assessment')",
        "input[value*='Start Assessment']",
        "a:has-text('Start Assessment')",
        "a[href*='complete.php']",
        "a[href*='feedback']",
        ".singlebutton.quizstartbuttondiv button",
        ".singlebutton.quizstartbuttondiv input",
        ".singlebutton button",
        ".singlebutton input",
        "button:has-text('Re-attempt')",
        "button:has-text('Continue')",
        "button:has-text('Start')",
        "#start-assessment",
        "form[action*='startattempt.php'] button",
        "form[action*='startattempt.php'] input",
        "form[action*='attempt.php'] button",
        "form[action*='attempt.php'] input",
        "button[type='submit']:has-text('Re-attempt')",
        "button[type='submit']:has-text('Continue')",
        "button[type='submit']:has-text('Start')",
        "input[type='submit'][value*='Re-attempt']",
        "input[type='submit'][value*='Continue']",
        "input[type='submit'][value*='Start']"
    ]

    for frame_target in [page] + page.frames:
        for sel in start_selectors:
            try:
                btn_cand = frame_target.locator(sel).first
                if await btn_cand.count() > 0 and await btn_cand.is_visible():
                    start_assessment_btn = btn_cand
                    target_frame = frame_target
                    break
            except Exception:
                pass
        if start_assessment_btn:
            break

    if start_assessment_btn:
        try:
            btn_txt = (await start_assessment_btn.inner_text()).strip() or (await start_assessment_btn.get_attribute("value") or "").strip()
            logger.info(f"  --> Clicking Assessment/Feedback launch button '{btn_txt}'...")
            await start_assessment_btn.click(force=True)
            await page.wait_for_timeout(4000)
        except Exception as ex:
            logger.warning(f"  --> Direct click notice on assessment button: {ex}")

    # Fallback JavaScript evaluation click for Start/Continue/Re-attempt/Answer Questions
    if not start_assessment_btn:
        logger.info("  --> Attempting JS click fallback for 'Start/Continue/Answer the questions'...")
        for frame_target in [page] + page.frames:
            try:
                clicked = await frame_target.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn, a'));
                    const startBtn = btns.find(b => {
                        const txt = (b.innerText || b.value || '').toLowerCase();
                        return txt.includes('answer the questions') || txt.includes('complete feedback') || txt.includes('re-attempt') || txt.includes('continue') || txt.includes('start');
                    });
                    if (startBtn) { startBtn.click(); return true; }
                    return false;
                }""")
                if clicked:
                    logger.info("  --> JS fallback successfully clicked launch button!")
                    await page.wait_for_timeout(4000)
                    target_frame = frame_target
                    break
            except Exception:
                pass

    # 3. Dynamic Question Answering Loop with Hierarchical Module/Subsection Scoping & Position Matching
    answers_list = extract_all_qa_items(answer_key)


    # Normalize sub_name if it is generic like 'View' or 'Start'
    effective_sub_name = sub_name or ""
    if effective_sub_name.strip().lower() in ("view", "start", "continue", "open"):
        if "feedback" in (module_name or "").lower() or str(module_no) == "8":
            effective_sub_name = "Feedback Form"

    # Pre-scope JSON items matching active Module & Subsection context
    scoped_items = []
    if answers_list:
        for item in answers_list:
            item_mod_no = item.get("module_no") or top_mod_no
            item_sub_name = (item.get("subsection_name") or top_sub_name or "").strip().lower()
            
            mod_match = not (item_mod_no and module_no and int(item_mod_no) != int(module_no))
            sub_match = not (item_sub_name and effective_sub_name and item_sub_name not in effective_sub_name.lower() and effective_sub_name.lower() not in item_sub_name)
            
            if "feedback" in (effective_sub_name or "").lower() or "feedback" in (module_name or "").lower() or str(module_no) == "8":
                sub_match = True

            if mod_match and sub_match:
                scoped_items.append(item)

    search_buckets = [scoped_items, answers_list] if scoped_items else [answers_list]
    logger.info(f"  --> [HIERARCHICAL MATCHING] Scoped {len(scoped_items)} questions for Module #{module_no or 1} || Subsection '{effective_sub_name}'.")



    # 2.5 Navigation Reset Protocol: Click Question 1 in Right-Side Quiz Navigation panel (#quiznavbutton1)
    try:
        q1_btn = target_frame.locator("#quiznavbutton1, a#quiznavbutton1, .qn_buttons a[data-quiz-page='0']").first
        if await q1_btn.count() == 0:
            q1_btn = page.locator("#quiznavbutton1, a#quiznavbutton1, .qn_buttons a[data-quiz-page='0']").first

        if await q1_btn.count() > 0 and await q1_btn.is_visible():
            logger.info("  🎯 [QUIZ NAV RESET] Found Question 1 button (#quiznavbutton1). Clicking to start quiz from Question 1!")
            await q1_btn.click(force=True)
            await page.wait_for_timeout(2000)
    except Exception as q1_ex:
        logger.warning(f"  --> Question 1 navigation reset notice: {q1_ex}")

    for q_num in range(200):

        # Unlimited time pacing: 1.5s human reading delay
        await page.wait_for_timeout(1500)

        # Extract question text & option choices displayed on screen
        await check_pause_status()
        q_text_screen = ""
        screen_opts = []
        parsed_option_elements = []

        screen_q_label = f"{q_num + 1}"
        try:
            qno_el = target_frame.locator(".qno, .questionnumber, .question-number, h3.no, h4.no, .qheader h3, .qheader h4").first
            if await qno_el.count() > 0 and await qno_el.is_visible():
                raw_qno = (await qno_el.inner_text()).strip()
                if raw_qno:
                    screen_q_label = raw_qno
        except Exception:
            pass

        num_m = re.search(r'\d+', screen_q_label)
        if num_m:
            q_tag = f"QUESTION-{int(num_m.group()):02d}"
        else:
            q_tag = f"QUESTION-{q_num + 1:02d}"

        try:
            q_elem = target_frame.locator(".que-no, .qtext, div.qtext, .question-text, .que .content .qtext, fieldset legend, .qheader, .question-content, div.que div.content").first
            if await q_elem.count() > 0 and await q_elem.is_visible():
                raw_q = (await q_elem.inner_text()).strip()
                q_text_screen = re.sub(r'^(?:question\s*text|question\s*\d+[:.]?|\d+[:.]?|q\d+[:.]?)\s*', '', raw_q, flags=re.IGNORECASE)
                q_text_screen = normalize_text(re.sub(r'\s*(?:select\s*one|question\s*\d+).*$', '', q_text_screen, flags=re.IGNORECASE | re.DOTALL).strip())

            # Select unique option rows cleanly (.answer > div.r0 / div.r1 / div.feed-ans-div)
            option_rows = target_frame.locator(".answer > div.r0, .answer > div.r1, .answer > div, .que .content .answer > div, div.feed-ans-div, div.feed-ans-div > div.form-check")
            row_count = await option_rows.count()

            if row_count == 0:
                option_rows = target_frame.locator("div.r0, div.r1, div[data-region='answer-label'], .feed-ans-div .form-check")
                row_count = await option_rows.count()



            for r_idx in range(row_count):
                row_el = option_rows.nth(r_idx)
                raw_text = (await row_el.inner_text()).strip()
                clean_text = normalize_text(re.sub(r'^(?:[a-d][.)]|option\s*[a-d][:.]?|\d+[.)])\s*', '', raw_text, flags=re.IGNORECASE).strip())

                clean_lower = clean_text.lower()

                ignore_list = ["clear selection", "maximum marks"]
                if not ("feedback" in (module_name or "").lower() or "feedback" in (effective_sub_name or "").lower()):
                    ignore_list.append("give feedback")
                if any(ignore_kw in clean_lower for ignore_kw in ignore_list):
                    continue


                if clean_text and clean_text not in screen_opts:
                    screen_opts.append(clean_text)
                    parsed_option_elements.append((clean_text, row_el))
        except Exception:
            pass

        if q_text_screen:
            logger.info("\n" + "  " + "-" * 75)
            logger.info(f"  ❓ [{q_tag}]: {q_text_screen}")
            if screen_opts:
                logger.info("  📋 [OPTIONS]:")
                for idx, opt_text in enumerate(screen_opts):
                    letter = chr(65 + idx) if idx < 26 else str(idx + 1)
                    logger.info(f"     [{letter}] {opt_text}")

        # Dual Confirmation Guard Protocol: Smart Auto-Learning JSON Cache + AI Live Solver Engine
        matched_answer_text = None
        gate1_ok = False

        # Step 1: Check Auto-Learning JSON Cache First (Instant 0.01s Match)
        if q_text_screen and answers_list:
            clean_screen_q = re.sub(r'[^\w\s]', '', q_text_screen.lower())
            screen_words = set(w for w in clean_screen_q.split() if len(w) >= 3) if clean_screen_q else set()

            for bucket in search_buckets:
                if matched_answer_text:
                    break

                if clean_screen_q:
                    for item in bucket:
                        json_q = (item.get("question") or item.get("question_keyword") or "").strip().lower()
                        clean_json_q = re.sub(r'[^\w\s]', '', json_q)
                        json_words = set(w for w in clean_json_q.split() if len(w) >= 3)
                        
                        common_words = json_words & screen_words
                        json_coverage = (len(common_words) / float(len(json_words))) if json_words else 0.0
                        screen_coverage = (len(common_words) / float(len(screen_words))) if screen_words else 0.0

                        is_100pct_match = False
                        if clean_json_q and clean_screen_q:
                            if clean_json_q == clean_screen_q or (json_words and screen_words and json_words == screen_words):
                                is_100pct_match = True
                            elif (clean_json_q in clean_screen_q or clean_screen_q in clean_json_q) and json_coverage == 1.0 and screen_coverage >= 0.85:
                                is_100pct_match = True

                        if is_100pct_match:
                            matched_answer_text = (item.get("answer") or item.get("correct_option") or "").strip()
                            gate1_ok = True
                            logger.info(f"  ⚡ [VERIFIED JSON 100% MATCH {q_tag}] Target Answer: '{matched_answer_text}'")
                            break

        # Step 2: AI Live Solver Fallback (If Question is NEW & Not in JSON Cache)
        if not matched_answer_text and q_text_screen:
            try:
                ai_solved = solve_question_with_ai(q_text_screen, screen_opts)
                if ai_solved:
                    matched_answer_text = ai_solved
                    gate1_ok = True
                    logger.info(f"  🧠 [AI LIVE {q_tag}] Solved NEW question -> '{matched_answer_text}'")
                    save_auto_learned_qa(course_title, module_no, module_name, sub_no, sub_name, q_text_screen, ai_solved, option_texts=screen_opts, is_feedback=("feedback" in (sub_name or "").lower()))

            except Exception as ai_ex:
                logger.warning(f"  --> AI Live Solver notice: {ai_ex}")

        selected_option = False
        
        # Gate 2: Exact Target Radio Input Click
        if matched_answer_text and parsed_option_elements:
            try:
                clean_target = re.sub(r'[^\w\s]', '', matched_answer_text.lower())
                target_words = set(w for w in clean_target.split() if len(w) >= 3)

                for idx, (opt_txt, row_el) in enumerate(parsed_option_elements):
                    clean_opt = re.sub(r'[^\w\s]', '', opt_txt.lower())
                    opt_words = set(w for w in clean_opt.split() if len(w) >= 3)
                    opt_overlap = (len(target_words & opt_words) / float(len(target_words))) if target_words else 0.0
                    
                    is_match = (clean_target == clean_opt) or (target_words and opt_words and target_words == opt_words) or (clean_target in clean_opt or clean_opt in clean_target) or (opt_overlap == 1.0)

                    if is_match:
                        opt_let = chr(65 + idx) if idx < 26 else str(idx + 1)
                        logger.info(f"  ✔ [VERIFIED ANSWER MATCH {q_tag}] Target Answer: '{matched_answer_text}'")


                        # 1. Try finding radio/checkbox inside THIS specific option row
                        radio_input = row_el.locator("input[type='radio'], input[type='checkbox']").first
                        if await radio_input.count() > 0:
                            await radio_input.click(force=True)
                            selected_option = True
                        else:
                            # 2. Try preceding sibling input (Moodle DOM structure: <input> followed by <div id="..._label">)
                            prec_radio = row_el.locator("xpath=preceding-sibling::input[@type='radio' or @type='checkbox'][1]").first
                            if await prec_radio.count() > 0:
                                await prec_radio.click(force=True)
                                selected_option = True

                        if not selected_option:
                            # 3. Try aria-labelledby or id.replace('_label', '') match (Moodle DOM standard)
                            row_id = await row_el.get_attribute("id") or ""
                            if row_id:
                                input_id = row_id.replace("_label", "")
                                linked_input = target_frame.locator(f"#{input_id}, input[id='{input_id}'], input[aria-labelledby='{row_id}']").first
                                if await linked_input.count() > 0:
                                    await linked_input.click(force=True)
                                    selected_option = True

                        if not selected_option:
                            # 4. Direct click on option row element as fallback
                            await row_el.click(force=True)
                            selected_option = True


                        if selected_option:
                            logger.info(f"  🎯 [SELECTED OPTION {opt_let}] Selected Radio Button [{opt_let}] for Answer: '{matched_answer_text}'.")
                            logger.info("  " + "-" * 75 + "\n")
                            await page.wait_for_timeout(1000)
                            break

            except Exception as match_ex:
                logger.warning(f"  --> Option matching notice: {match_ex}")

        # Gate 2.5: Text / Comment Box Input Filling (For Feedback Forms or Open Text Questions)
        if matched_answer_text and not selected_option:
            try:
                textarea_el = target_frame.locator("textarea, input[type='text']:not([class*='search']), .form-control:not([type='hidden'])").first
                if await textarea_el.count() > 0 and await textarea_el.is_visible():
                    await textarea_el.fill(matched_answer_text)
                    selected_option = True
                    logger.info(f"  ✍️ [TYPED FEEDBACK RESPONSE {q_tag}]: '{matched_answer_text}'")
                    logger.info("  " + "-" * 75 + "\n")
                    await page.wait_for_timeout(1000)
            except Exception as text_ex:
                logger.warning(f"  --> Text response filling notice: {text_ex}")

        if not selected_option:
            logger.error(f"\n❌ [CRITICAL AI SOLVER EXHAUSTED {q_tag}] Could not solve Question '{q_text_screen[:45]}...' after 2 Gemini attempts, 2 Grok attempts, and 30s, 45s, 60s backoff retries.")
            logger.error("⛔ [CIRCUIT BREAKER TRIGGERED] Closing server context cleanly and stopping all automation processes!\n")
            try:
                await page.context.close()
            except Exception:
                pass
            raise RuntimeError(f"AI_SOLVER_FAILED_SERVER_STUCK: Question '{q_text_screen[:45]}...' could not be solved without 100% accuracy.")




        next_nav = target_frame.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next'), button:has-text('Submit Feedback'), input[value*='Submit Feedback'], button:has-text('Submit'), input[value*='Submit']").first
        if await next_nav.count() == 0:
            next_nav = page.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next'), button:has-text('Submit Feedback'), input[value*='Submit Feedback'], button:has-text('Submit'), input[value*='Submit']").first


        review_submit_nav = target_frame.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first
        if await review_submit_nav.count() == 0:
            review_submit_nav = page.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first


        if await next_nav.count() > 0 and await next_nav.is_visible():
            await next_nav.click(force=True)
            await page.wait_for_timeout(1500)
        elif await review_submit_nav.count() > 0 and await review_submit_nav.is_visible():
            logger.info(f"  --> Reached end of question set (Total Questions: {q_num + 1})! Submitting assessment...")
            await review_submit_nav.click(force=True)
            await page.wait_for_timeout(2500)
            break
        else:
            break


    if config.AUTOMATIC_FINAL_SUBMIT:
        logger.info("  --> Searching for Final Submit button (Summary of Attempt page)...")
        await page.wait_for_timeout(2000)

        final_selectors = [
            "input[value='Final Submit']",
            "input[value*='Final Submit']",
            "button:has-text('Final Submit')",
            "input[value*='Submit all']",
            "button:has-text('Submit all')",
            "input[type='submit'][value*='Submit']",
            "button.btn-primary:has-text('Submit')",
            "button:has-text('Finish')",
            ".singlebutton input",
            ".singlebutton button"
        ]

        final_submit = None
        for frame_target in [target_frame, page] + page.frames:
            for sel in final_selectors:
                try:
                    cand = frame_target.locator(sel).first
                    if await cand.count() > 0 and await cand.is_visible():
                        final_submit = cand
                        break
                except Exception:
                    pass
            if final_submit:
                break

        if final_submit:
            logger.info("  --> Executing Final Assessment Submit...")
            try:
                await final_submit.click(force=True)
                await page.wait_for_timeout(3000)
            except Exception as ex:
                logger.warning(f"  --> Notice clicking Final Submit: {ex}")
        else:
            logger.info("  --> Executing JS fallback for Final Submit...")
            for frame_target in [target_frame, page] + page.frames:
                try:
                    clicked = await frame_target.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
                        const fBtn = btns.find(b => (b.innerText || b.value || '').toLowerCase().includes('submit'));
                        if (fBtn) { fBtn.click(); return true; }
                        return false;
                    }""")
                    if clicked:
                        logger.info("  --> JS fallback executed Final Submit!")
                        await page.wait_for_timeout(3000)
                        break
                except Exception:
                    pass


    # 4. Post-Submission 'Continue' button click (Returns to course page to hydrate 100% checkmark)
    for frame_target in [target_frame, page] + page.frames:
        try:
            post_cont = frame_target.locator("a:has-text('Continue'), button:has-text('Continue'), input[value*='Continue']").first
            if await post_cont.count() > 0 and await post_cont.is_visible():
                logger.info("  --> Clicking post-submission 'Continue' button to trigger 100% checkmark sync...")
                await post_cont.click(force=True)
                await page.wait_for_timeout(3000)
                break
        except Exception:
            pass

    # 5. Close Activity Modal & Confirm Checkmark
    await close_activity_modal(page)
    await wait_for_server_checkmark(page)


async def process_feedback_activity(page, view_button, answer_key=None, module_name="", module_no=None, sub_name="", sub_no=None, course_title=""):
    """
    Dedicated DIKSHA Popup Feedback Form Engine.
    Matches exact DIKSHA Feedback Form popup modal:
    1. Clicks brown 'View' button to open Feedback Form popup modal.
    2. Selects 'Strongly Agree' / Option 1 for all radio questions inside the modal.
    3. Clicks the brown 'Submit Feedback' button at the bottom of the modal.
    4. Confirms 100% checkmark update!
    """
    ctx_str = f"Module #{module_no or 8} ('{module_name or 'Feedback Form'}') || Subsection #{sub_no or 1} ('{sub_name or 'Feedback Form'}')"
    logger.info(f"\n" + "=" * 50)
    logger.info(f" 📝 [FEEDBACK FORM MODAL] Opening Feedback Form for {ctx_str}...")
    logger.info("=" * 50)

    # 1. Click the brown 'View' button to open the Feedback Form popup modal
    try:
        view_id = await view_button.get_attribute("data-id") or ""
        await view_button.scroll_into_view_if_needed()
        await view_button.click(force=True)

        # JS Event Dispatcher Backup Click to ensure DIKSHA AJAX handler triggers
        for frame_target in [page] + page.frames:
            try:
                await frame_target.evaluate("""(vid) => {
                    const btn = document.querySelector(`a[data-id="${vid}"]`) || document.querySelector('a.activity-feedback');
                    if (btn) {
                        btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        btn.click();
                        return true;
                    }
                    return false;
                }""", view_id)
            except Exception:
                pass

        logger.info("  --> Clicked Feedback View button. Waiting 3s for Feedback Form popup modal to render...")

        await page.wait_for_timeout(3000)
    except Exception as ex:
        logger.warning(f"  --> Direct click notice on Feedback View button: {ex}")

    # 2. Wait up to 10s for the Feedback popup modal container to become VISIBLE on screen
    modal_container = None
    target_frame = page
    for frame_target in [page] + page.frames:
        try:
            modal_cand = frame_target.locator(".modal-dialog, .modal-content, .modal-body, div[class*='modal']:has-text('Feedback'), div[class*='modal']:has-text('Submit')").first
            if await modal_cand.count() > 0 and await modal_cand.is_visible():
                modal_container = modal_cand
                target_frame = frame_target
                logger.info("  --> Feedback popup modal is OPEN and VISIBLE on screen!")
                break
        except Exception:
            pass

    # 3. Process Feedback Questions using JSON Answer Key + AI Fallback Engine
    answers_list = extract_all_qa_items(answer_key)
    target_scope = modal_container if modal_container else target_frame

    try:
        radios = target_scope.locator("input[type='radio']:visible, input[type='checkbox']:visible")
        r_count = await radios.count()
        
        # Fallback to all radios inside target_scope if :visible filter is strict
        if r_count == 0:
            radios = target_scope.locator("input[type='radio'], input[type='checkbox']")
            r_count = await radios.count()

        if r_count > 0:
            # Group radio elements by question input name attribute
            radio_groups = {}
            for idx in range(r_count):
                r_el = radios.nth(idx)
                try:
                    r_name = await r_el.get_attribute("name") or f"q_idx_{idx}"
                    if r_name not in radio_groups:
                        radio_groups[r_name] = []
                    radio_groups[r_name].append(r_el)
                except Exception:
                    pass

            logger.info(f"  --> Found {len(radio_groups)} Rating Questions in Feedback Modal. Matching against JSON Answer Key / AI Solver...")


            q_counter = 1
            for group_name, group_radios in radio_groups.items():
                # Extract question number and clean question text from DOM
                q_text_dom = ""
                dom_q_num = None
                try:
                    que_el = group_radios[0].locator("xpath=ancestor::*[contains(@class,'que') or contains(@class,'form-group') or contains(@class,'row') or contains(@class,'card')][1]/descendant::*[contains(@class,'que-no') or contains(@class,'qtext') or contains(@class,'question-text') or self::h4 or self::h5 or self::legend][1]").first
                    if await que_el.count() == 0:
                        que_el = group_radios[0].locator("xpath=preceding-sibling::*[contains(@class,'que-no') or contains(@class,'qtext')][1]").first
                    if await que_el.count() > 0:
                        q_text_dom = (await que_el.inner_text()).strip()
                except Exception:
                    pass

                # If specific header not found, fallback to parent inner_text
                if not q_text_dom:
                    try:
                        parent_wrapper = group_radios[0].locator("xpath=ancestor::*[contains(@class,'que') or contains(@class,'form-group') or contains(@class,'row') or contains(@class,'card')][1]").first
                        if await parent_wrapper.count() > 0:
                            q_text_dom = (await parent_wrapper.inner_text()).strip()
                    except Exception:
                        pass

                # Parse exact DOM question number (e.g., "1.", "18.", "Q19")
                if q_text_dom:
                    num_match = re.search(r'^\s*(\d+)[\.\)]', q_text_dom)
                    if num_match:
                        dom_q_num = int(num_match.group(1))

                # Set tag based on real DOM question number if available
                if dom_q_num:
                    q_tag = f"FEEDBACK-Q{dom_q_num:02d}"
                else:
                    q_tag = f"FEEDBACK-Q{q_counter:02d}"
                q_counter += 1

                # Strip leading numbers ("1. ", "2. ", "Q1: ")
                clean_q_dom = re.sub(r'^\s*(?:\d+[\.\)]|Q\d+[\.\)]?|Question\s*\d+[\.\)]?)\s*', '', q_text_dom, flags=re.IGNORECASE).strip() if q_text_dom else ""


                # 1. Check JSON Answer Key first!
                matched_target_text = None
                if answers_list and clean_q_dom:
                    norm_clean_q = normalize_text(clean_q_dom)
                    for item in answers_list:
                        json_q = normalize_text(item.get("question", ""))
                        if json_q and (norm_clean_q in json_q or json_q in norm_clean_q):
                            matched_target_text = item.get("answer", "")
                            logger.info(f"  🎯 [JSON ANSWER KEY MATCH {q_tag}]: Found exact answer in JSON: '{matched_target_text}'")
                            break

                # 2. If NOT found in JSON, call AI Live Solver!
                if not matched_target_text and clean_q_dom and len(clean_q_dom) > 10:
                    try:
                        ai_ans, _ = await solve_question_with_ai(clean_q_dom, ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"])
                        if ai_ans:
                            matched_target_text = ai_ans
                            logger.info(f"  🤖 [AI LIVE SOLVER MATCH {q_tag}]: AI selected answer: '{matched_target_text}'")
                            # Auto-save learned Feedback Q&A into Course JSON
                            save_auto_learned_qa(
                                course_title=course_title,
                                module_no=module_no or 8,
                                module_name=module_name or "Feedback Form",
                                sub_no=sub_no or 1,
                                sub_name=sub_name or "Feedback Form",
                                question_text=clean_q_dom,
                                answer_text=matched_target_text,
                                option_texts=["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
                                is_feedback=True
                            )
                    except Exception:
                        pass

                # 3. Select target option in DOM
                clicked_option = False
                if matched_target_text:
                    for r_el in group_radios:
                        try:
                            r_id = await r_el.get_attribute("id") or ""
                            label_el = target_scope.locator(f"label[for='{r_id}']").first if r_id else None
                            opt_txt = (await label_el.inner_text()).strip() if label_el and await label_el.count() > 0 else ""
                            
                            if opt_txt and (normalize_text(matched_target_text) in normalize_text(opt_txt) or normalize_text(opt_txt) in normalize_text(matched_target_text)):
                                await r_el.click(force=True)
                                clicked_option = True
                                await page.wait_for_timeout(200)
                                break
                        except Exception:
                            pass

                # Fallback: Click first rating option ('Strongly Agree') for feedback survey so form completes cleanly
                if not clicked_option and group_radios:
                    try:
                        await group_radios[0].click(force=True)
                        await page.wait_for_timeout(200)
                        logger.info(f"  👍 [FEEDBACK SURVEY RATING {q_tag}]: Selected positive rating response ('Strongly Agree').")
                    except Exception:
                        pass



        # Process all Textarea / Comment / Text Response Questions in Feedback Form
        textareas = target_scope.locator("textarea, input[type='text']:not([class*='search']):not([id*='search'])")
        t_count = await textareas.count()
        if t_count > 0:
            logger.info(f"  --> Found {t_count} Textarea/Comment Questions in Feedback Form. Matching against JSON / AI...")

            for idx in range(t_count):
                try:
                    ta_el = textareas.nth(idx)
                    if await ta_el.is_visible():
                        # 1. Extract question text from preceding div.que-no
                        ta_q_text = ""
                        try:
                            parent_wrap = ta_el.locator("xpath=ancestor::*[contains(@class,'feed-ans-div') or contains(@class,'que') or contains(@class,'form-group') or contains(@class,'row')][1]/preceding-sibling::div[contains(@class,'que-no')][1]").first
                            if await parent_wrap.count() == 0:
                                parent_wrap = ta_el.locator("xpath=preceding-sibling::div[contains(@class,'que-no')][1]").first
                            if await parent_wrap.count() == 0:
                                parent_wrap = ta_el.locator("xpath=ancestor::*[contains(@class,'que') or contains(@class,'form-group') or contains(@class,'card')][1]").first
                            if await parent_wrap.count() > 0:
                                ta_q_text = (await parent_wrap.inner_text()).strip()
                        except Exception:
                            pass

                        clean_ta_q = re.sub(r'^\s*(?:\d+[\.\)]|Q\d+[\.\)]?|Question\s*\d+[\.\)]?)\s*', '', ta_q_text, flags=re.IGNORECASE).strip()
                        
                        # Parse exact question number (e.g. 19, 20, 21)
                        ta_q_num = None
                        if ta_q_text:
                            ta_num_m = re.search(r'^\s*(\d+)[\.\)]', ta_q_text)
                            if ta_num_m:
                                ta_q_num = int(ta_num_m.group(1))

                        ta_tag = f"Q{ta_q_num:02d}" if ta_q_num else f"Q{idx+19}"

                        # 2. Check JSON Answer Key first!
                        matched_ta_ans = None
                        if answers_list and clean_ta_q:
                            for item in answers_list:
                                json_q = normalize_text(item.get("question", ""))
                                if json_q and (normalize_text(clean_ta_q) in json_q or json_q in normalize_text(clean_ta_q)):
                                    matched_ta_ans = item.get("answer", "")
                                    logger.info(f"  🎯 [JSON TEXTAREA MATCH {ta_tag}]: Found exact answer in JSON: '{matched_ta_ans[:50]}...'")
                                    break

                        # 3. If NOT found in JSON, call AI Live Solver for Textarea Question!
                        if not matched_ta_ans and clean_ta_q and len(clean_ta_q) > 10:
                            try:
                                ai_ans, _ = await solve_question_with_ai(clean_ta_q, [])
                                if ai_ans:
                                    matched_ta_ans = ai_ans
                                    logger.info(f"  🤖 [AI TEXTAREA SOLVER {ta_tag}]: AI generated response: '{matched_ta_ans[:50]}...'")
                            except Exception:
                                pass

                        # Fallback default comment text
                        if not matched_ta_ans:
                            matched_ta_ans = "Overall, it was a highly informative and well-executed training program."

                        await ta_el.fill(matched_ta_ans)
                        logger.info(f"  ✍️ [FILLED FEEDBACK TEXTAREA {ta_tag}]: '{matched_ta_ans[:50]}...'")


                        # Auto-save learned Textarea Response into Course JSON
                        if clean_ta_q and matched_ta_ans:
                            save_auto_learned_qa(
                                course_title=course_title,
                                module_no=module_no or 8,
                                module_name=module_name or "Feedback Form",
                                sub_no=sub_no or 1,
                                sub_name=sub_name or "Feedback Form",
                                question_text=clean_ta_q,
                                answer_text=matched_ta_ans,
                                option_texts=[],
                                is_feedback=True
                            )
                except Exception as ta_ex:
                    logger.warning(f"  --> Textarea filling notice: {ta_ex}")
    except Exception as f_ex:
        logger.warning(f"  --> Feedback modal processing notice: {f_ex}")




    # 3. Click the brown 'Submit Feedback' button at the bottom of the modal
    logger.info("  --> Searching for brown 'Submit Feedback' button...")
    submitted = False
    for frame_target in [page] + page.frames:
        try:
            sub_btn = frame_target.locator("#submitFeedbackBtn11, button.submit-feed-btn, button:has-text('Submit Feedback'), input[value*='Submit Feedback'], button:has-text('Submit'), input[type='submit'][value*='Submit']").first
            if await sub_btn.count() > 0 and await sub_btn.is_visible():
                logger.info("  🎯 [SUBMIT FEEDBACK] Clicking brown 'Submit Feedback' button...")
                await sub_btn.scroll_into_view_if_needed()
                await sub_btn.click(force=True)
                
                # Dispatch native DOM MouseEvent to guarantee DIKSHA AJAX submit handler executes
                await frame_target.evaluate("""() => {
                    const btn = document.querySelector('#submitFeedbackBtn11') || document.querySelector('button.submit-feed-btn');
                    if (btn) {
                        btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        btn.click();
                        return true;
                    }
                    return false;
                }""")
                
                submitted = True
                logger.info("  --> Submitted Feedback Form! Waiting 6s for DIKSHA server AJAX sync...")
                await page.wait_for_timeout(6000)
                break
        except Exception:
            pass

    # Fallback JS Submit click
    if not submitted:
        for frame_target in [page] + page.frames:
            try:
                clicked = await frame_target.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"], a.btn'));
                    const sub = btns.find(b => {
                        const txt = (b.innerText || b.value || '').toLowerCase();
                        const id = (b.id || '').toLowerCase();
                        const cls = (b.className || '').toLowerCase();
                        return txt.includes('submit feedback') || id.includes('submitfeedback') || cls.includes('submit-feed') || txt.includes('submit');
                    });
                    if (sub) { 
                        sub.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        sub.click(); 
                        return true; 
                    }
                    return false;
                }""")
                if clicked:
                    logger.info("  🎯 [SUBMIT FEEDBACK] JS fallback successfully clicked 'Submit Feedback' button!")
                    await page.wait_for_timeout(6000)
                    break
            except Exception:
                pass

    # 4. Handle Modal Close / Thank-You Screen Dismissal
    for frame_target in [page] + page.frames:
        try:
            cls_btn = frame_target.locator("button.close, .modal-header .close, button[data-dismiss='modal'], button:has-text('Close'), a:has-text('Close'), .modal-footer button:has-text('OK'), .modal-footer button:has-text('Close')").first
            if await cls_btn.count() > 0 and await cls_btn.is_visible():
                logger.info("  --> Clicking Modal Close / Thank-You screen button...")
                await cls_btn.click(force=True)
                await page.wait_for_timeout(2000)
                break
        except Exception:
            pass

    # 5. Check for modal close & confirm 100% checkmark update
    await close_activity_modal(page)
    await wait_for_server_checkmark(page)








async def get_section_action_buttons(collapse_panel, header):
    """
    Returns unique, deduplicated action buttons inside a module collapse panel.
    Ensures exactly 1 button per activity row (e.g. 2 items = 2 distinct buttons).
    """
    if collapse_panel and await collapse_panel.count() > 0:
        btns = collapse_panel.locator(".btn.module-view-btn, a.activity-list, button:has-text('View'), a:has-text('View')")
    else:
        btns = header.locator("xpath=following-sibling::div[1]").locator(".btn.module-view-btn, a.activity-list")
    
    raw_count = await btns.count()
    distinct_btns = []
    seen_row_keys = set()

    for idx in range(raw_count):
        b = btns.nth(idx)
        if await b.is_visible():
            try:
                row = b.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list')][1]").first
                row_key = (await row.inner_text()).strip() if await row.count() > 0 else (await b.inner_text()).strip()
                clean_key = ' '.join(row_key.split())
                if clean_key not in seen_row_keys:
                    seen_row_keys.add(clean_key)
                    distinct_btns.append(b)
            except Exception:
                distinct_btns.append(b)
    return distinct_btns

async def is_button_enabled(btn):

    """
    Determines if a View button is active/unlocked on DIKSHA.
    Returns False if button is disabled, greyed out, or locked ("not available unless...").
    """
    try:
        is_dis = await btn.get_attribute("disabled")
        aria_dis = await btn.get_attribute("aria-disabled")
        btn_class = (await btn.get_attribute("class") or "").split()
        
        if is_dis is not None or aria_dis == "true" or "disabled" in btn_class or "btn-disabled" in btn_class or "not-available" in btn_class:
            return False

        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list')][1]").first
        if await row.count() > 0:
            row_text = (await row.inner_text()).strip().lower()
            if "not available unless" in row_text:
                return False
    except Exception:
        pass
    return True

async def is_item_100_percent_complete(btn):

    """
    Determines if a subsection item row on DIKSHA is 100% complete.
    Item is complete ONLY IF it contains a visible checkmark (i.fa-check, brown check circle)
    and does NOT contain an incomplete percentage badge ('0%', '50%', etc.).
    """
    try:
        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list') or contains(@class,'card-body') or contains(@class,'activity')][1]").first
        if await row.count() > 0:
            row_text = (await row.inner_text()).strip().lower()
            
            # If item row explicitly shows an incomplete percentage badge (0%, 50%, etc.)
            pct_matches = re.findall(r"(\d{1,2})%", row_text)
            if pct_matches:
                for val_str in pct_matches:
                    val = int(val_str)
                    if val < 100:
                        return False  # Incomplete item!
                    elif val == 100:
                        return True

            # Check for visible brown checkmark icon or .p100 class on the item row
            check_icon = row.locator("i.fa-check, .fa-check, .fa-check-circle, .c100.p100, div[class*='p100']").first
            if await check_icon.count() > 0 and await check_icon.is_visible():
                return True
    except Exception:
        pass

    return False

async def is_header_100_percent_complete(header):
    """
    Determines if a module header is 100% completed on DIKSHA.
    Returns False if header contains ANY percentage badge from 0% to 99% (e.g. 0%, 13%, 26%, 50%, 97%, 99%).
    Returns True ONLY IF 100% badge/checkmark is present AND no incomplete percentage is present.
    """
    try:
        raw_text = (await header.inner_text()).strip().lower()
        
        # Regex search for any percentage badge (0% to 99%)
        pct_matches = re.findall(r"(\d{1,2})%", raw_text)
        if pct_matches:
            for val_str in pct_matches:
                val = int(val_str)
                if val < 100:
                    return False  # Incomplete percentage detected!

        # Check element class attributes for incomplete circle badges (e.g. p0, p13, p26, p50)
        classes = (await header.get_attribute("class") or "").split()
        for cl in classes:
            if cl.startswith("p") and cl[1:].isdigit():
                if int(cl[1:]) < 100:
                    return False

        # If 100% explicitly in text or p100 class
        if "100%" in raw_text:
            return True

        # Check for 100% completion checkmark icon or .p100 class strictly on the header level
        check_icon = header.locator("i.fa-check, .c100.p100, div[class*='p100']").first
        if await check_icon.count() > 0 and await check_icon.is_visible():
            return True
    except Exception:
        pass

    return False


async def process_course_modules(page, answer_key=None, course_title="Unknown Course"):
    """
    Clicks 'Lessons' tab (waits 6s for server hydration), lists all Main Modules,
    auto-expands 50%/0% incomplete modules, and executes items without checkmarks.
    """
    if not course_title or course_title == "Unknown Course":
        try:
            h_el = page.locator(".course-title, .page-title, .course-header h1, h1").first
            if await h_el.count() > 0 and await h_el.is_visible():
                extracted_t = (await h_el.inner_text()).strip()
                if extracted_t:
                    course_title = extracted_t
        except Exception:
            pass

    logger.info("[COURSE MODULES] Checking for 'Lessons' tab...")
    try:
        lessons_tab = page.locator(config.SELECTORS["lessons_tab"]).first
        if await lessons_tab.count() > 0 and await lessons_tab.is_visible():
            logger.info("  --> Clicking 'Lessons' tab button...")
            await lessons_tab.click(force=True)
            logger.info("  --> Waiting 6 seconds for DIKSHA server to hydrate modules and auto-expand active incomplete section...")
            await page.wait_for_timeout(6000)
    except Exception as e:
        logger.warning(f"  --> Lessons tab click notice: {e}")


    logger.info("[ACCORDION ENGINE] Scanning course section accordions...")
    
    # Locate all primary module accordion headers
    headers_raw = page.locator(
        ".courses_modules_header, #accordion .card-header, .courses_modules_div .card-header, "
        ".accordion .card-header, .panel-heading"
    )
    header_count = await headers_raw.count()

    if header_count == 0:
        headers_raw = page.locator("h5, h6, .card-header, [data-toggle='collapse']")
        header_count = await headers_raw.count()

    main_modules = []
    seen_normalized_titles = set()

    for i in range(header_count):
        header = headers_raw.nth(i)
        header_title = f"Module #{i+1}"
        try:
            raw = (await header.inner_text()).strip()
            if raw:
                header_title = raw.split('\n')[0].strip()
        except Exception:
            pass

        lower_t = header_title.lower().strip()
        normalized_t = lower_t.rstrip('s')

        # Skip empty or non-lesson discussion, guideline, & certificate sections
        if not header_title or any(skip in lower_t for skip in ["discussion", "navigation", "file upload", "closed for replies", "pinned", "certificate", "download certificate"]):
            logger.info(f"  --> [SKIP SECTION] '{header_title}' is a Certificate / Reward section. Skipping!")
            continue


        # Deduplicate identical / singular-plural titles (e.g. Assessment vs Assessments)
        if normalized_t not in seen_normalized_titles:
            seen_normalized_titles.add(normalized_t)
            main_modules.append((header, header_title))

    total_real_modules = len(main_modules)

    if total_real_modules > 0:
        # 1. Print Clean Course Module Structure Summary
        logger.info("\n" + "=" * 35)
        logger.info(f"   DIKSHA COURSE STRUCTURE ({total_real_modules} MODULES DETECTED)")
        logger.info("=" * 35)
        
        for idx, (hdr, title) in enumerate(main_modules, 1):
            logger.info(f"  [{idx}/{total_real_modules}] {title}")

        logger.info("=" * 35 + "\n")

        # 2. Sequential Execution Loop per Module with Smart Skipping & Auto-Expand
        for i, (header, header_title) in enumerate(main_modules, 1):
            await check_pause_status()
            logger.info("\n" + "=" * 35)
            logger.info(f" 📚 MODULE [{i}/{total_real_modules}]: {header_title}")
            logger.info("=" * 35)


            item_attempts = {}
            completed_items = set()

            # Check if Module header is ALREADY 100% complete

            if await is_header_100_percent_complete(header):
                logger.info(f"  --> [SKIP MODULE] '{header_title}' is ALREADY 100% COMPLETED. Skipping!")
                continue

            # Locate the exact clickable <a> toggle element or header
            click_target = header.locator("a[data-toggle='collapse'], a[href*='collapse'], a[aria-controls*='collapse']").first
            if await click_target.count() == 0:
                click_target = header

            # Extract collapse target ID (e.g. href="#collapse8450" -> collapse8450)
            collapse_id = ""
            try:
                href = await click_target.get_attribute("href") or await click_target.get_attribute("data-target") or await click_target.get_attribute("aria-controls") or ""
                data_id = await click_target.get_attribute("data-id") or ""
                collapse_id = href.replace("#", "").strip()
                if not collapse_id and data_id:
                    collapse_id = f"collapse{data_id}"
            except Exception:
                pass

            # Determine expansion state using class, aria-expanded, and collapse panel visibility
            is_collapsed = True
            try:
                link_class = (await click_target.get_attribute("class") or "").split()
                aria_exp = (await click_target.get_attribute("aria-expanded") or "").lower()
                
                if "collapsed" in link_class or aria_exp == "false":
                    is_collapsed = True
                elif aria_exp == "true":
                    is_collapsed = False

                if collapse_id and await page.locator(f"#{collapse_id}").count() > 0:
                    panel = page.locator(f"#{collapse_id}").first
                    p_class = (await panel.get_attribute("class") or "").split()
                    if ("in" in p_class or "show" in p_class) and await panel.is_visible():
                        is_collapsed = False
            except Exception:
                pass

            # If module is collapsed, click the <a> link to expand it
            if is_collapsed:
                logger.info(f"  --> [INCOMPLETE MODULE] Expanding accordion for '{header_title}'...")
                try:
                    await click_target.scroll_into_view_if_needed()
                    await click_target.click(force=True)
                    await page.wait_for_timeout(2500)
                except Exception as ex:
                    logger.warning(f"  --> Notice expanding header '{header_title}': {ex}")

            # Scope View buttons strictly to THIS specific collapse panel (#collapse8450 or .modules_full_accordian_div)
            collapse_panel = None
            if collapse_id and await page.locator(f"#{collapse_id}").count() > 0:
                collapse_panel = page.locator(f"#{collapse_id}").first
            else:
                parent_div = header.locator("xpath=ancestor::*[contains(@class,'modules_full_accordian_div') or contains(@class,'panel') or contains(@class,'card')][1]").first
                if await parent_div.count() > 0:
                    collapse_panel = parent_div.locator(".panel-collapse, .collapse, .card-body").first

            # Dynamic Execution Loop: Re-scans section buttons after each item completes to handle sequential unlocks
            for pass_num in range(3):
                distinct_btns = await get_section_action_buttons(collapse_panel, header)
                total_sec_items = len(distinct_btns)

                if total_sec_items == 0:
                    if pass_num == 0:
                        logger.info("     [-] No action buttons inside this section. Moving to next...")
                    break

                processed_any = False

                for j, btn in enumerate(distinct_btns, 1):
                    await check_pause_status()
                    if not await btn.is_visible():
                        continue


                    btn_text = (await btn.inner_text()).strip()

                    # Smart Subsection Item Skipping: check if item row has 100% brown checkmark
                    if await is_item_100_percent_complete(btn):
                        logger.info(f"  --> [✓ ALREADY DONE] Subsection [{j}/{total_sec_items}]: '{btn_text}' is 100% complete. Skipping!")
                        continue

                    # Strict Attempt & Page Reload Circuit Breaker Protocol
                    runs_done = item_attempts.get(btn_text, 0)
                    
                    if runs_done >= 4:
                        logger.error(f"\n❌ [CRITICAL DIKSHA SERVER FAILURE] Subsection item '{btn_text}' failed to unlock/complete after 4 attempts & 5s page refreshes.")
                        logger.error("⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context cleanly!\n")
                        try:
                            await page.context.close()
                        except Exception:
                            pass
                        raise RuntimeError(f"DIKSHA_SERVER_STUCK: '{btn_text}' did not complete after 4 attempts.")

                    if runs_done == 2:
                        logger.warning(f"  --> [ATTEMPT 2 FAILED] Subsection '{btn_text}' not unlocked yet. Waiting 5s gap & reloading page (page.reload())...")
                        await asyncio.sleep(5)
                        try:
                            await page.reload()
                            await asyncio.sleep(5)
                            if await click_target.count() > 0:
                                await click_target.click(force=True)
                                await page.wait_for_timeout(2500)
                        except Exception:
                            pass

                    # Check if item is locked / disabled by DIKSHA server
                    if not await is_button_enabled(btn):
                        logger.info(f"  --> [LOCKED ITEM] Subsection [{j}/{total_sec_items}]: '{btn_text}' is currently LOCKED.")
                        logger.info("  --> [SERVER REFRESH] Waiting 5s gap & reloading page (page.reload()) to fetch updated DIKSHA server session unlock status...")
                        await asyncio.sleep(5)
                        try:
                            await page.reload()
                            await asyncio.sleep(5)
                            if await click_target.count() > 0:
                                await click_target.click(force=True)
                                await page.wait_for_timeout(2500)
                        except Exception:
                            pass

                        if not await is_button_enabled(btn):
                            if runs_done >= 3:
                                logger.error(f"\n❌ [CRITICAL DIKSHA SERVER FAILURE] Subsection item '{btn_text}' remains locked after 4 attempts.")
                                logger.error("⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context!\n")
                                try:
                                    await page.context.close()
                                except Exception:
                                    pass
                                raise RuntimeError(f"DIKSHA_SERVER_LOCKED_STUCK: '{btn_text}' locked after 4 attempts.")
                            logger.info(f"  --> [SKIP LOCKED] Subsection [{j}/{total_sec_items}]: '{btn_text}' remains locked. Will re-evaluate on next pass...")
                            continue

                    act_type = await btn.get_attribute("act_type") or "resource"
                    
                    # Extract real item title if button text is generic like 'View'
                    real_item_title = btn_text
                    if btn_text.lower() in ("view", "start", "open", "continue"):
                        try:
                            row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'card-body')][1]").first
                            if await row.count() > 0:
                                title_el = row.locator("h4, h5, .title, .activity-title, bdi, strong, .name").first
                                if await title_el.count() > 0:
                                    extracted_t = (await title_el.inner_text()).strip()
                                    if extracted_t and extracted_t.lower() not in ("view", "start"):
                                        real_item_title = extracted_t
                        except Exception:
                            pass

                    logger.info("\n" + "=" * 35)
                    logger.info(f" ▶ SUBSECTION [{j}/{total_sec_items}]: '{real_item_title}' (Type: '{act_type}') [Attempt {runs_done + 1}/4]")
                    logger.info("=" * 35)

                    item_attempts[btn_text] = runs_done + 1

                    try:
                        await btn.scroll_into_view_if_needed()
                        await page.wait_for_timeout(300)
                    except Exception:
                        pass

                    is_feedback = (
                        act_type in ("feedback", "survey", "choice") or 
                        "feedback" in act_type.lower() or 
                        "feedback" in header_title.lower() or 
                        "feedback" in real_item_title.lower() or 
                        "survey" in real_item_title.lower()
                    )

                    is_quiz = act_type == "quiz" or "assessment" in real_item_title.lower() or "quiz" in act_type.lower()

                    try:
                        if act_type == "url":
                            await process_video_activity(page, btn)
                        elif act_type == "resource":
                            await process_pdf_activity(page, btn)
                        elif act_type == "h5pactivity":
                            await process_h5p_activity(page, btn, answer_key, course_title=course_title)
                        elif is_feedback:
                            await process_feedback_activity(page, btn, answer_key, module_name=header_title, module_no=i, sub_name=real_item_title, sub_no=j, course_title=course_title)
                        elif is_quiz:
                            await process_quiz_assessment(page, btn, answer_key, module_name=header_title, module_no=i, sub_name=real_item_title, sub_no=j, course_title=course_title)
                        else:
                            try:
                                await btn.scroll_into_view_if_needed()
                            except Exception:
                                pass
                            await btn.click(force=True)
                            await page.wait_for_timeout(3000)
                            await close_activity_modal(page)
                            await wait_for_server_checkmark(page)

                    except Exception as item_ex:
                        logger.error(f"     [-] Subsection execution notice: {item_ex}")



                    completed_items.add(btn_text)
                    completed_items.add(real_item_title)
                    processed_any = True

                    # DIKSHA Server unlock sync delay between subsections
                    logger.info("  --> DIKSHA Server sync buffer: waiting 4 seconds for next item unlock...")
                    await page.wait_for_timeout(4000)

                # If no new items were executed in this pass, all section items are complete or skipped!
                if not processed_any:
                    break

            # DOUBLE CONFIRMATION & STRICT 100% COMPLETION GATE GUARD
            logger.info(f"  --> [DOUBLE CONFIRMATION] Verifying 100% completion for '{header_title}'...")
            await page.wait_for_timeout(3000)

            # Check 1: Re-verify section item checkmarks strictly from live DOM
            recheck_btns = await get_section_action_buttons(collapse_panel, header)
            all_done = True
            for r_btn in recheck_btns:
                if not await is_item_100_percent_complete(r_btn):
                    all_done = False
                    break

            header_done = await is_header_100_percent_complete(header)

            if not all_done or not header_done:
                logger.info("  --> [GATE REFRESH] Reloading page once to sync DIKSHA server backend checkmarks...")
                try:
                    await page.reload()
                    await page.wait_for_timeout(5000)
                    recheck_btns = await get_section_action_buttons(collapse_panel, header)
                    all_done = True
                    for r_btn in recheck_btns:
                        if not await is_item_100_percent_complete(r_btn):
                            all_done = False
                            break
                    header_done = await is_header_100_percent_complete(header)
                except Exception:
                    pass

            if (all_done and header_done) or (not recheck_btns and any(skip_kw in header_title.lower() for skip_kw in ["certificate", "download"])):
                logger.info(f"  --> [CONFIRMED 1/2] Section activities in '{header_title}' verified 100% complete!")
                logger.info(f"  --> [CONFIRMED 2/2] DIKSHA Server 100% completion badge verified! Moving to next module...\n")

            else:
                logger.warning(f"  --> [GATE WARNING] '{header_title}' is NOT 100% completed yet!")
                logger.info(f"  --> Retrying section execution to achieve 100% checkmark before advancing...")
                # Re-try active item in this section if not yet 100% done
                for retry_pass in range(2):
                    r_btns = await get_section_action_buttons(collapse_panel, header)
                    for r_idx, r_btn in enumerate(r_btns, start=1):
                        r_btn_text = (await r_btn.inner_text()).strip()
                        r_runs = item_attempts.get(r_btn_text, 0)
                        if r_runs >= 4:
                            continue

                        if not await is_item_100_percent_complete(r_btn) and await is_button_enabled(r_btn):
                            r_act_type = await r_btn.get_attribute("act_type") or "resource"
                            logger.info(f"  ▶ Retrying Subsection item (Type: '{r_act_type}') [Attempt {r_runs + 1}/4]...")
                            item_attempts[r_btn_text] = r_runs + 1
                            if r_act_type == "quiz":
                                await process_quiz_assessment(page, r_btn, answer_key, module_name=header_title, module_no=i+1, sub_name=r_btn_text, sub_no=r_idx)
                            elif r_act_type == "h5pactivity":
                                await process_h5p_activity(page, r_btn, answer_key)
                            elif r_act_type == "url":
                                await process_video_activity(page, r_btn)
                            elif r_act_type == "resource":
                                await process_pdf_activity(page, r_btn)

                # Final Circuit Breaker Gate Check
                final_header_check = await is_header_100_percent_complete(header)
                if not final_header_check and not any(skip_kw in header_title.lower() for skip_kw in ["certificate", "download"]):
                    logger.error(f"\n❌ [CRITICAL DIKSHA SERVER FAILURE] '{header_title}' remains incomplete after 4 attempts & 5s page reloads.")
                    logger.error("⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context!\n")
                    try:
                        await page.context.close()
                    except Exception:
                        pass
                    raise RuntimeError(f"DIKSHA_SERVER_STUCK: '{header_title}' failed to achieve 100% after 4 attempts.")
                elif any(skip_kw in header_title.lower() for skip_kw in ["certificate", "download"]):
                    logger.info(f"  🎓 [CERTIFICATE SECTION] '{header_title}' reached end of course. Course completed successfully!")







    else:
        logger.info("  --> No explicit accordion headers found. Processing direct View buttons...")
        view_btns = page.locator(".btn.module-view-btn, a.activity-list, button:has-text('View'), a:has-text('View')")
        btn_count = await view_btns.count()
        logger.info(f"Found {btn_count} direct view button(s).")
        for j in range(btn_count):
            btn = view_btns.nth(j)
            if await btn.is_visible():
                await process_pdf_activity(page, btn)



async def run_diksha_automation(target_course_url=None, username=None, password=None, mode="all"):
    """
    Main entry point for executing full DIKSHA automation pipeline.
    """
    start_keyboard_pause_listener()
    answer_key = load_answer_key()

    logger.info("   DIKSHA AUTOMATION PIPELINE")
    logger.info("  💡 [HOTKEY ENABLED] Press 'P' or 'Spacebar' in terminal to PAUSE / RESUME!")
    logger.info("=" * 35)





    async with async_playwright() as p:
        browser_launcher = getattr(p, config.BROWSER_TYPE)
        browser = await browser_launcher.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOMO_MS,
            args=["--start-maximized", "--mute-audio", "--no-sandbox", "--disable-setuid-sandbox"]
        )


        context = await browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()


        # Step 1 & 2: Login
        await login_diksha(page, username, password)

        # Direct course URL or navigate via My Learning
        if target_course_url:
            logger.info(f"Opening target course URL: {target_course_url}")
            await page.goto(target_course_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            t_title = "Target Course"
            try:
                h_el = page.locator(".course-title, .page-title, .course-header h1, h1").first
                if await h_el.count() > 0 and await h_el.is_visible():
                    t_title = (await h_el.inner_text()).strip()
            except Exception:
                pass
            
            c_key = load_answer_key(t_title)
            await process_course_modules(page, c_key, course_title=t_title)
        else:
            await navigate_to_my_learning(page)
            enrolled_courses = await fetch_enrolled_courses(page)
            
            selected_courses = display_interactive_course_menu(enrolled_courses)
            
            if selected_courses:
                for c in selected_courses:
                    await page.goto(c['url'], wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    # 100% Future-Proof Title Verification: Extract exact full heading from DIKSHA course page
                    try:
                        h_el = page.locator(".course-title, .page-title, .course-header h1, h1").first
                        if await h_el.count() > 0 and await h_el.is_visible():
                            page_full_title = (await h_el.inner_text()).strip()
                            if page_full_title and len(page_full_title) >= len(c['title']):
                                c['title'] = page_full_title
                    except Exception:
                        pass

                    logger.info(f"🚀 Starting Enrolled Course: [{c['index']}] {c['title']}")
                    course_answer_key = load_answer_key(c['title'])
                    
                    # Run activity modules for this course
                    await process_course_modules(page, course_answer_key, course_title=c['title'])




        # Screenshot completion milestone (with timeout safety for external fonts)
        screenshot_path = config.SCREENSHOT_DIR / "diksha_pipeline_executed.png"
        try:
            await page.screenshot(path=str(screenshot_path), timeout=5000)
            logger.info(f"Pipeline executed successfully. Screenshot saved to {screenshot_path.name}")
        except Exception as e:
            logger.info(f"Pipeline executed successfully. (Screenshot notice: {e})")

        if config.KEEP_BROWSER_OPEN and not config.HEADLESS:
            logger.info("==========================================================")
            logger.info("  [KEEP-OPEN] Chrome browser is kept OPEN for your inspection!")
            logger.info("  Close the browser window or press Ctrl+C in console when finished.")
            logger.info("==========================================================")
            try:
                while True:
                    await asyncio.sleep(10)
            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("Closing browser...")
        else:
            await page.wait_for_timeout(3000)
            await browser.close()



