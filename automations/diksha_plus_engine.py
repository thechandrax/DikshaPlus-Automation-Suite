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
import os
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
ACTIVE_COURSE_TITLE = ""

class _CourseRestartSignal(Exception):
    """
    Internal control-flow signal raised when a subsection fails all 3 attempts.
    Caught by run_diksha_automation to navigate back to the course URL and restart
    the entire course scan from scratch (up to 5 times total).
    """
    pass

async def check_pause_status(page=None):
    """Checks IS_PAUSED flag. If paused, waits in 5s intervals until resumed."""
    global IS_PAUSED
    while IS_PAUSED:
        await asyncio.sleep(5)





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
    global ACTIVE_COURSE_TITLE
    courses_dir = config.DATA_DIR / "courses"
    courses_dir.mkdir(parents=True, exist_ok=True)

    if course_title and course_title not in ("Course", "unknown_course", "Unknown Course"):
        ACTIVE_COURSE_TITLE = course_title


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
                return None
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

    return None  # No answer key found or created for this course title
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
    global ACTIVE_COURSE_TITLE
    try:
        # Resolve course_title using global memory if missing or generic
        valid_title = course_title
        if not valid_title or valid_title in ("Course", "unknown_course", "Unknown Course"):
            valid_title = ACTIVE_COURSE_TITLE

        # Search existing course JSON files in data/courses/
        courses_dir = config.COURSES_DIR
        course_key_file = None

        if valid_title:
            fn_name = get_course_filename(valid_title)
            course_key_file = courses_dir / fn_name

        if not course_key_file or not course_key_file.exists():
            # Check for non-unknown JSON files in data/courses/
            valid_files = [f for f in courses_dir.glob("*.json") if f.name != "unknown_course.json"]
            if valid_files:
                course_key_file = valid_files[0]
            elif valid_title:
                fn_name = get_course_filename(valid_title)
                course_key_file = courses_dir / fn_name
            else:
                course_key_file = courses_dir / "course.json"

        data_j = {}
        if course_key_file.exists():
            with open(course_key_file, "r", encoding="utf-8") as f:
                try:
                    data_j = json.load(f)
                except Exception:
                    data_j = {}

        data_j.pop("description", None)
        data_j.pop("answers", None)

        if valid_title and valid_title not in ("Course", "unknown_course", "Unknown Course"):
            data_j["course_name"] = valid_title
            ACTIVE_COURSE_TITLE = valid_title
        elif "course_name" not in data_j or data_j["course_name"] in ("Course", "unknown_course"):
            data_j["course_name"] = "Course"


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




async def solve_question_with_ai(question_text, option_texts=None):
    """
    Async AI solver: Gemini Multi-Key Pool → Groq LPU Fallback → Stepped Backoff.
    Uses asyncio.sleep (non-blocking) to avoid freezing the Playwright event loop.
    Returns None if all attempts fail — never guesses or uses a dummy answer.
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

    # 1. Load Gemini & Groq API Key Pools
    gemini_keys = getattr(config, "GEMINI_API_KEYS", [])
    if not gemini_keys and hasattr(config, "GEMINI_API_KEY") and config.GEMINI_API_KEY:
        gemini_keys = [config.GEMINI_API_KEY]

    groq_keys = getattr(config, "GROQ_API_KEYS", [])
    if not groq_keys:
        single_groq = getattr(config, "GROQ_API_KEY", "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
        if single_groq:
            groq_keys = [single_groq]

    def _try_gemini_key(key_idx, api_key):
        models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest"]
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
                    logger.info(f"\n  🧠 [GEMINI AI SUCCESS] Key #{key_idx} -> '{clean_ans}'")
                    return clean_ans

            except urllib.error.HTTPError as http_err:
                if http_err.code in (429, 503):
                    logger.warning(f"  ⏳ [GEMINI RATE LIMIT] Key #{key_idx} rate limited. Trying next key in sequence...")
                elif http_err.code in (401, 403):
                    logger.error(f"  ❌ [GEMINI API ERROR {http_err.code}] Key #{key_idx} invalid.")
                    break
            except Exception as ex:
                logger.warning(f"  ⚠️ [GEMINI SOLVER NOTICE] Key #{key_idx}: {ex}")
        return None

    def _try_groq_key(g_idx, groq_key):
        for model_name in ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]:
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
                    logger.info(f"\n  ⚡ [GROQ LPU SUCCESS] Key #{g_idx} -> '{clean_ans}'")
                    return clean_ans
            except Exception as ex:
                logger.warning(f"  ⚠️ [GROQ AI NOTICE] ({model_name} Key #{g_idx}): {ex}")
        return None

    # Build Interleaved Alternating Sequence: Gemini #1 -> Groq #1 -> Gemini #2 -> Groq #2 ...
    interleaved_sequence = []
    max_len = max(len(gemini_keys), len(groq_keys))
    for i in range(max_len):
        if i < len(gemini_keys):
            interleaved_sequence.append(("gemini", i + 1, gemini_keys[i]))
        if i < len(groq_keys):
            interleaved_sequence.append(("groq", i + 1, groq_keys[i]))

    for provider, k_idx, k_val in interleaved_sequence:

        if provider == "gemini":
            sol = await asyncio.to_thread(_try_gemini_key, k_idx, k_val)
            if sol:
                return sol
        elif provider == "groq":
            sol = await asyncio.to_thread(_try_groq_key, k_idx, k_val)
            if sol:
                return sol

    # 3. STEPPED BACKOFF RETRY PROTOCOL: 30s -> 45s -> 60s
    logger.warning("  ⚠️ [AI INITIAL ATTEMPTS EXHAUSTED] Entering Stepped Backoff Retry Protocol (30s -> 45s -> 60s)...")
    backoff_delays = [30, 45, 60]
    for b_idx, delay_sec in enumerate(backoff_delays, 1):
        logger.warning(f"\n  ⏳ [AI RATE LIMIT BACKOFF {b_idx}/3] Waiting {delay_sec} seconds for API quota reset before Retry #{b_idx}...")
        await asyncio.sleep(delay_sec)
        for provider, k_idx, k_val in interleaved_sequence:
            if provider == "gemini":
                sol = await asyncio.to_thread(_try_gemini_key, k_idx, k_val)
                if sol:
                    logger.info(f"  🧠 [AI BACKOFF SUCCESS] Solved on Backoff #{b_idx} ({delay_sec}s) via Gemini Key #{k_idx} -> '{sol}'")
                    return sol
            elif provider == "groq":
                sol = await asyncio.to_thread(_try_groq_key, k_idx, k_val)
                if sol:
                    logger.info(f"  ⚡ [AI BACKOFF SUCCESS] Solved on Backoff #{b_idx} ({delay_sec}s) via Groq Key #{k_idx} -> '{sol}'")
                    return sol

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
        logger.warning(f"  --> Initial page load notice: {e}. Retrying navigation in 3s...")
        await asyncio.sleep(3)
        try:
            await page.goto(config.AUTH_LOGIN_URL, wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_timeout(3000)
        except Exception as e2:
            logger.error(f"  --> Navigation retry also failed: {e2}. Proceeding with caution.")

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




async def process_certificate_feedback(page, modal_already_open=False):
    """
    Handles the Certificate section 'Give Feedback' popup flow:
      modal_already_open=False (default): Clicks Give Feedback button, waits for modal, then submits.
      modal_already_open=True:            Modal is already visible (DIKSHA auto-opened it on course load).
                                          Skips button-click steps — goes straight to emoji + submit.
      Steps (when modal_already_open=False):
        1. Clicks 'Give Feedback' button (force=True, JS dispatch — bypasses disabled state)
        2. Waits for feedback modal popup to open
      Steps (always):
        3. Selects the best emoji rating (data-rating='5' — 5 stars = Excellent)
        4. Fills the optional textarea with a positive feedback message
        5. Clicks 'Submit Feedback' (#submitFeedbackBtn)
        6. Waits 5s for AJAX submission to complete
    If any step fails, logs a warning and continues — feedback failure never blocks course completion.
    """
    logger.info("  --> [CERTIFICATE FEEDBACK] Attempting to submit course feedback before certificate download...")
    try:
        if modal_already_open:
            # Modal is already visible — DIKSHA auto-opened it on course load.
            # Skip button-click and modal-verify steps entirely.
            logger.info("  --> [CERTIFICATE FEEDBACK] Modal already open — skipping button click, proceeding to rating...")
            await page.wait_for_timeout(1500)  # Ensure animation is fully settled
        else:
            # Step 1: Locate the CORRECT Give Feedback button
            # DIKSHA renders two buttons — prefer the one inside .btn-wrap (the real bound button)
            feedback_btn = page.locator(".btn-wrap button:has-text('Give Feedback')").first
            if await feedback_btn.count() == 0:
                # Fallback to any Give Feedback button on the page
                feedback_btn = page.locator("button:has-text('Give Feedback')").first
            if await feedback_btn.count() == 0:
                logger.warning("  --> [CERTIFICATE FEEDBACK] 'Give Feedback' button not found. Skipping feedback step.")
                return

            logger.info("  --> [CERTIFICATE FEEDBACK] Clicking 'Give Feedback' button...")
            try:
                await feedback_btn.click(force=True)
            except Exception:
                pass
            # JS dispatch as fallback — removes disabled attribute and fires click event
            try:
                await feedback_btn.evaluate("""el => {
                    el.removeAttribute('disabled');
                    el.click();
                    const ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
                    el.dispatchEvent(ev);
                }""")
            except Exception:
                pass
            await page.wait_for_timeout(3000)

            # Step 2: Verify feedback modal opened (tight selector — no broad [id*='feedback'])
            modal = page.locator(".modal.show, .modal.in, #feedbackModal, .feedback-modal").first
            if await modal.count() == 0 or not await modal.is_visible():
                logger.warning("  --> [CERTIFICATE FEEDBACK] Feedback modal did not open. Skipping feedback step.")
                return
            logger.info("  --> [CERTIFICATE FEEDBACK] Feedback modal opened successfully!")
            # Wait 1.5s for modal animation to complete before clicking emoji
            await page.wait_for_timeout(1500)

        # Step 3: Select best emoji rating (5 stars — data-rating='5' = Excellent)
        try:
            best_emoji = page.locator("div.emoji-item[data-rating='5']").first
            if await best_emoji.count() > 0:
                await best_emoji.click(force=True)
                logger.info("  --> [CERTIFICATE FEEDBACK] Selected 5-star rating emoji ⭐⭐⭐⭐⭐ (Excellent)")
            else:
                # Fallback: click last emoji-item (highest available)
                all_emojis = page.locator("div.emoji-item.rating-input")
                cnt = await all_emojis.count()
                if cnt > 0:
                    await all_emojis.nth(cnt - 1).click(force=True)
                    logger.info(f"  --> [CERTIFICATE FEEDBACK] Selected highest available rating (emoji #{cnt})")
        except Exception as e:
            logger.warning(f"  --> [CERTIFICATE FEEDBACK] Emoji rating notice: {e}")

        await page.wait_for_timeout(500)

        # Step 4: Fill optional feedback textarea
        try:
            textarea = page.locator("textarea[name='review'], textarea.form-control").first
            if await textarea.count() > 0:
                await textarea.fill("This course was very well-structured and informative. The content is highly relevant and practical for classroom teaching. I strongly recommend it to all teachers.")
                logger.info("  --> [CERTIFICATE FEEDBACK] Filled feedback textarea with positive review.")
        except Exception as e:
            logger.warning(f"  --> [CERTIFICATE FEEDBACK] Textarea fill notice: {e}")

        await page.wait_for_timeout(500)

        # Step 5: Click Submit Feedback button
        try:
            submit_btn = page.locator("#submitFeedbackBtn, button:has-text('Submit Feedback')").first
            if await submit_btn.count() > 0:
                logger.info("  --> [CERTIFICATE FEEDBACK] Clicking 'Submit Feedback'...")
                await submit_btn.click(force=True)
                await page.wait_for_timeout(5000)
                logger.info("  --> [CERTIFICATE FEEDBACK] ✅ Feedback submitted successfully!")
            else:
                logger.warning("  --> [CERTIFICATE FEEDBACK] Submit button not found.")
        except Exception as e:
            logger.warning(f"  --> [CERTIFICATE FEEDBACK] Submit notice: {e}")

        # Step 6: Close the 'Feedback Submitted Successfully' success modal
        # DIKSHA shows a success popup after submit — must be closed to resume automation
        try:
            await page.wait_for_timeout(1500)  # Let success modal fully render
            close_btn = page.locator(
                "a.close[data-dismiss='modal'], "
                "a[aria-label='Close'], "
                "button.close[data-dismiss='modal'], "
                ".modal-header a.close, "
                ".modal-header button.close"
            ).first
            if await close_btn.count() > 0 and await close_btn.is_visible():
                logger.info("  --> [CERTIFICATE FEEDBACK] Closing 'Feedback Submitted Successfully' modal...")
                await close_btn.click(force=True)
                await page.wait_for_timeout(1500)  # Wait for modal close animation
                logger.info("  --> [CERTIFICATE FEEDBACK] Success modal closed. ✓")
            else:
                # Fallback: press Escape key to close any open modal
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
                logger.info("  --> [CERTIFICATE FEEDBACK] Success modal closed via Escape key. ✓")
        except Exception as e:
            logger.warning(f"  --> [CERTIFICATE FEEDBACK] Modal close notice: {e}")

    except Exception as ex:
        logger.warning(f"  --> [CERTIFICATE FEEDBACK] Feedback flow notice: {ex}. Continuing to course completion...")




async def wait_for_server_checkmark(page, timeout=15, item_btn=None):
    """
    Waits for server 100% checkmark pie icon: <i class="fas fa-check"></i>
    If item_btn is provided, also verifies the specific item row is 100% before
    logging confirmed — avoids false positives from other completed items on page.
    """
    logger.info("  --> Waiting for server 100% checkmark update...")
    start = asyncio.get_running_loop().time()
    false_positive_logged = False  # Ensures the false-positive warning logs only once
    while (asyncio.get_running_loop().time() - start) < timeout:
        check_icon = page.locator(config.SELECTORS["progress_check_icon"]).first
        if await check_icon.count() > 0 and await check_icon.is_visible():
            # Page-level icon found — now verify it belongs to THIS specific item
            if item_btn is not None:
                item_confirmed = await is_item_100_percent_complete(item_btn)
                if item_confirmed:
                    logger.info("  --> Server 100% checkmark confirmed! (item-specific verified)")
                    return True
                else:
                    # False positive — checkmark is from a different completed item on the page
                    # Log only once, then poll silently until timeout
                    if not false_positive_logged:
                        logger.warning("  --> [FALSE POSITIVE] Page checkmark belongs to another item. Polling until this item reaches 100%...")
                        false_positive_logged = True
            else:
                logger.info("  --> Server 100% checkmark confirmed!")
                return True
        await page.wait_for_timeout(2000)
    logger.info("  --> Checkmark sync window completed.")
    return False


async def safe_action_click(locator):
    """
    Safely clicks an action button (View / Start / Continue) even if hidden or in scroll view.
    Combines scroll_into_view_if_needed, force=True click, native JS parent <a> bubble dispatch, and fallback.
    """
    try:
        await locator.scroll_into_view_if_needed()
    except Exception:
        pass

    try:
        await locator.click(force=True, timeout=3000)
    except Exception:
        pass

    # Native JS Event Bubble Dispatcher (targets parent <a> or <button> if clicked on inner text node)
    try:
        await locator.evaluate("""el => {
            const target = el.closest('a') || el.closest('button') || el;
            if (target) {
                target.click();
                const ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window });
                target.dispatchEvent(ev);
            }
        }""")
    except Exception as e:
        logger.warning(f"  --> Safe action click notice: {e}")


async def open_activity_popup(page, view_button):
    """
    Universally opens any activity modal popup (PDF, Video, H5P, Quiz, Feedback).
    Uses safe_action_click, waits 3s, and applies double-trigger fallback if modal did not open.
    Logs clean message without raw ID attribute:
    '--> [DOUBLE-TRIGGER POPUP] Re-clicking title link to force open popup modal...'
    """
    # Resolve the CORRECT clickable button — DIKSHA renders two identical <a> elements
    # with the same act_id: one bare outer anchor (unbound) and one inside li.action123 (real button).
    # Always prefer the li.action123 version for the first click.
    actual_btn = view_button
    try:
        act_id_pre = await view_button.get_attribute("act_id") or await view_button.get_attribute("data-id") or ""
        if act_id_pre:
            correct_btn = page.locator(f"li.action123 a[act_id='{act_id_pre}'], li.action123 a[data-id='{act_id_pre}']").first
            if await correct_btn.count() > 0:
                # Use li.action123 button regardless of viewport visibility
                # safe_action_click() handles scroll_into_view automatically
                actual_btn = correct_btn
    except Exception:
        actual_btn = view_button  # Fallback to original if resolution fails

    await safe_action_click(actual_btn)
    logger.info("  --> [CLICKED VIEW BUTTON] View button click sent — waiting 5s for modal to open...")
    await page.wait_for_timeout(5000)

    try:
        modal_chk = page.locator(".modal.show, .modal.in, .quiz-popup-wrapper, #instructionModal, iframe, .pdf-viewer, #pdf-container").first
        if await modal_chk.count() > 0 and await modal_chk.is_visible():
            logger.info("  --> [MODAL OPENED] Activity modal opened successfully on first click!")
        else:
            logger.warning("  --> [MODAL NOT DETECTED] Modal did not open after first click. Attempting double-trigger fallback...")
            act_id = await view_button.get_attribute("act_id") or await view_button.get_attribute("data-id") or ""
            if act_id:
                # Prefer li.action123 version in double-trigger too
                t_link = page.locator(f"li.action123 a[act_id='{act_id}'], li.action123 a[data-id='{act_id}'], a[act_id='{act_id}'], a[data-id='{act_id}']").first
                if await t_link.count() > 0 and await t_link.is_visible():
                    logger.info("  --> [DOUBLE-TRIGGER POPUP] Re-clicking title link to force open popup modal...")
                    await safe_action_click(t_link)
                    await page.wait_for_timeout(3000)
                else:
                    logger.warning("  --> [DOUBLE-TRIGGER] No title link found by act_id. Proceeding anyway.")
            else:
                logger.warning("  --> [DOUBLE-TRIGGER] No act_id attribute found on view button. Proceeding anyway.")
    except Exception as d_ex:
        logger.warning(f"  --> Double-trigger popup notice: {d_ex}")








async def process_video_activity(page, view_button):

    """
    STEP-07 (Video Activity - act_type="url"):
    Implements technical specification for Video Acceleration & Telemetry:
      1. Nested iFrame & Shadow DOM Support (scans all frames for <video>)
      2. 15s Warm-up Buffer @ 1.0x speed (telemetry session init)
      3. Dynamic Acceleration: 16x speed (duration >= 5m) or 6x speed (duration < 5m)
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
            m = re.search(r'(\d{1,2})%', row_text)
            if m:
                row_saved_pct = int(m.group(1))
    except Exception:
        row_saved_pct = 0

    logger.info("[VIDEO ACTIVITY] Opening video module...")
    await open_activity_popup(page, view_button)
    await page.wait_for_timeout(2000)

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

        # 3. Dynamic Playback Acceleration: 16x (>= 5 min) or 6x (< 5 min)
        if duration >= 300:
            speed = 16.0
            logger.info("  --> Dynamic Acceleration: Applying 16x Speed (Long Video >= 5 min)...")
        else:
            speed = 6.0
            logger.info("  --> Dynamic Acceleration: Applying 6x Speed (Short Video < 5 min)...")

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

    # 5s settling buffer — allows DIKSHA server to register the natural 'ended' event before modal closes
    logger.info("  --> Waiting 5s settling buffer before closing — allowing server to register 100% telemetry...")
    await asyncio.sleep(5)

    # Close video modal
    await close_activity_modal(page)

    # 6. Video 10s Checkmark Verification & 1-Time Reload/Replay Recovery Engine
    logger.info("  --> [VIDEO CHECKMARK] Waiting exactly 10s for video 100% checkmark...")
    checkmark_ok = await wait_for_server_checkmark(page, timeout=10, item_btn=view_button)

    if not checkmark_ok:
        logger.warning("  --> [VIDEO RECOVERY] 100% checkmark not confirmed. Reopening video to replay final 10s...")
        try:
            # Re-open the video modal via the original view button
            await view_button.click(force=True)
            await page.wait_for_timeout(3000)

            # Re-resolve a fresh frame reference — target_frame may be stale after modal close
            live_frame = page
            for frame in page.frames:
                f_v = frame.locator("video").first
                if await f_v.count() > 0:
                    live_frame = frame
                    break

            # Replay final 10 seconds at 1.0x speed and dispatch ended event on the live frame
            await live_frame.evaluate("""
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


async def process_pdf_activity(page, view_button):
    """
    STEP-07 (PDF Activity - act_type="resource"):
    Implements technical specification for PDF Reader:
      1. Automated Page Flipping (simulates PageDown & End key presses)
      2. Reading Time Simulation (maintains page reading intervals)
      3. End-of-Doc Scroll (auto-scrolls viewer container to exact bottom for checkmarks)
    """
    logger.info("[PDF ACTIVITY] Opening PDF document resource...")
    await open_activity_popup(page, view_button)
    await page.wait_for_timeout(2000)



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
    await safe_action_click(view_button)
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
            ai_solved = await solve_question_with_ai(q_text_screen, screen_opts)
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

    await open_activity_popup(page, view_button)
    logger.info("  --> Waiting 5 seconds for DIKSHA assessment modal & banner popup to render...")
    await page.wait_for_timeout(2000)



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

    # 1. Wait 5s for quiz instruction popup banner to appear on screen after clicking View
    logger.info("  ⏳ [POPUP PRE-LOAD] Waiting 5 seconds for quiz instruction popup banner to render...")
    await page.wait_for_timeout(5000)

    # Dismiss any instruction / announcement popup modal if present
    try:
        for frame_target in [page] + page.frames:
            popup_close = frame_target.locator(".modal.show button.close, .modal.in .close, #instructionModal .close, .popup-banner .close-btn, button:has-text('Close'), button:has-text('OK'), a.close").first
            if await popup_close.count() > 0 and await popup_close.is_visible():
                logger.info("  --> [DISMISS POPUP] Closing instruction popup modal...")
                await popup_close.click(force=True)
                await page.wait_for_timeout(2000)
                break
    except Exception as pop_ex:
        logger.warning(f"  --> Instruction popup dismiss notice: {pop_ex}")

    # 2. Locate and click 'Start Assessment' / 'Continue Assessment' / 'Answer the questions' button
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
            logger.info("  ⏳ [QUIZ IFRAME PRE-LOAD BUFFER] Waiting 5 seconds for question #1 to render...")
            await page.wait_for_timeout(5000)
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
                    logger.info("  ⏳ [QUIZ IFRAME PRE-LOAD BUFFER] Waiting 5 seconds for question #1 to render...")
                    await page.wait_for_timeout(5000)
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
            item_mod_no = item.get("module_no") or module_no
            item_sub_name = (item.get("subsection_name") or sub_name or "").strip().lower()
            
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
            q_elem = None
            for frame_t in [target_frame, page] + page.frames:
                cand_q = frame_t.locator(".que-no, .qtext, div.qtext, .question-text, .que .content .qtext, fieldset legend, .qheader, .question-content, div.que div.content").first
                if await cand_q.count() > 0 and await cand_q.is_visible():
                    q_elem = cand_q
                    target_frame = frame_t
                    break

            if q_elem and await q_elem.count() > 0:
                raw_q = (await q_elem.inner_text()).strip()
                q_text_screen = re.sub(r'^(?:question\s*text|question\s*\d+[:.]?|\d+[:.]?|q\d+[:.]?)\s*', '', raw_q, flags=re.IGNORECASE)
                q_text_screen = normalize_text(re.sub(r'\s*(?:select\s*one|question\s*\d+).*$', '', q_text_screen, flags=re.IGNORECASE | re.DOTALL).strip())

            # Select unique option rows cleanly (.answer > div.r0 / div.r1 / div.feed-ans-div)
            option_rows = target_frame.locator(".answer > div.r0, .answer > div.r1, .answer > div, .que .content .answer > div, div.feed-ans-div, div.feed-ans-div > div.form-check")
            row_count = await option_rows.count()

            if row_count == 0:
                option_rows = target_frame.locator("div.r0, div.r1, div[data-region='answer-label'], .feed-ans-div .form-check, .answer label, .options label")
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
                ai_solved = await solve_question_with_ai(q_text_screen, screen_opts)
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

        # Gate 2.5: Text / Short Answer / Blank / Feedback Input Filling
        if matched_answer_text and not selected_option:
            try:
                text_input_found = False
                for frame_target in [target_frame, page] + page.frames:
                    text_locs = frame_target.locator("textarea, input[type='text']:not([class*='search']), input.shortanswer, input[name*='answer'], input[id*='answer'], .form-control:not([type='hidden']), div[contenteditable='true']")
                    count = await text_locs.count()
                    for t_idx in range(count):
                        t_el = text_locs.nth(t_idx)
                        if await t_el.is_visible():
                            try:
                                await t_el.fill(matched_answer_text)
                            except Exception:
                                await t_el.evaluate("(el, val) => { el.innerText = val; el.value = val; }", matched_answer_text)
                            selected_option = True
                            text_input_found = True
                            logger.info(f"  ✍️ [TYPED TEXT ANSWER {q_tag}]: '{matched_answer_text}'")
                            logger.info("  " + "-" * 75 + "\n")
                            await page.wait_for_timeout(1000)
                            break
                    if text_input_found:
                        break
            except Exception as text_ex:
                logger.warning(f"  --> Text response filling notice: {text_ex}")

        # Fallback for Informative / Continuation slides without choices or when AI answer is provided for text question
        if not selected_option and matched_answer_text and not screen_opts:
            selected_option = True
            logger.info(f"  ℹ️ [INFORMATIVE / CONTINUATION QUESTION {q_tag}] Auto-advancing with AI solution: '{matched_answer_text}'")
            logger.info("  " + "-" * 75 + "\n")

        if not selected_option:
            if not q_text_screen and not screen_opts:
                logger.info("  🏁 [QUIZ SUMMARY DETECTED] Reached end of questions / Summary of Attempt page! Proceeding to Final Assessment Submit...")
                break
            else:
                logger.error(f"\n❌ [CRITICAL AI SOLVER EXHAUSTED {q_tag}] Could not solve Question '{q_text_screen[:45]}...' after 5 Gemini keys, 3 Grok keys, and 30s, 45s, 60s backoff retries.")
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
                logger.info("  ⏳ [POST-SUBMIT BUFFER] Waiting 5 seconds for DIKSHA server score telemetry & checkmark processing...")
                await page.wait_for_timeout(5000)
            except Exception as ex:
                logger.warning(f"  --> Notice clicking Final Submit: {ex}")
        else:
            if "dashboard.php" not in page.url and "my-learning" not in page.url:
                logger.info("  --> Executing JS fallback for Final Submit (quiz frames)...")
                for frame_target in [target_frame] + page.frames:
                    if frame_target != page:
                        try:
                            clicked = await frame_target.evaluate("""() => {
                                const btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
                                const fBtn = btns.find(b => {
                                    const txt = (b.innerText || b.value || '').toLowerCase();
                                    return txt.includes('submit all') || txt.includes('final submit') || (txt.includes('submit') && !txt.includes('dashboard'));
                                });
                                if (fBtn) { fBtn.click(); return true; }
                                return false;
                            }""")
                            if clicked:
                                logger.info("  --> JS fallback executed Final Submit inside quiz frame!")
                                logger.info("  ⏳ [POST-SUBMIT BUFFER] Waiting 5 seconds for DIKSHA server score telemetry & checkmark processing...")
                                await page.wait_for_timeout(5000)
                                break
                        except Exception:
                            pass




    # 4. Post-Submission 'Continue' / 'Finish' / 'Back to Course' button click
    for frame_target in [target_frame, page] + page.frames:
        try:
            post_cont = frame_target.locator("a:has-text('Continue'), button:has-text('Continue'), input[value*='Continue'], a:has-text('Finish'), button:has-text('Finish'), a:has-text('Back to Course'), button:has-text('Back to Course'), input[value*='Finish']").first
            if await post_cont.count() > 0 and await post_cont.is_visible():
                p_txt = (await post_cont.inner_text()).strip() or "Continue"
                logger.info(f"  --> Clicking post-submission '{p_txt}' button to return to course page...")
                await post_cont.click(force=True)
                await page.wait_for_timeout(3000)
                break
        except Exception:
            pass

    # 5. Close Activity Modal & Wait 5s for DIKSHA Server Checkmark Sync
    await close_activity_modal(page)
    logger.info("  ⏳ [SERVER SYNC BUFFER] Waiting 5 seconds for DIKSHA server checkmark & next subsection unlock...")
    await page.wait_for_timeout(5000)
    await wait_for_server_checkmark(page, timeout=15)



async def process_certificate_feedback(page, view_button=None, answer_key=None, module_name=None, module_no=None, sub_name=None, sub_no=None, course_title=None):
    """
    STEP-07 (Feedback Form Activity):
    Dual-Scan Auto-Popup Engine:
      1. First checks if 'Share your Feedback' modal is ALREADY OPEN on screen (auto-popped by DIKSHA server).
      2. If NOT open, clicks brown 'Give Feedback' / 'View' button or searches page for feedback triggers.
      3. Selects 'Excellent' (5 Stars) / 'Strongly Agree' for all emoji/rating questions inside modal.
      4. Fills Textarea / Comment responses via JSON / AI.
      5. Clicks the brown 'Submit Feedback' button at the bottom of the modal.
      6. Confirms 100% checkmark update!
    """
    ctx_str = f"Module #{module_no or 8} ('{module_name or 'Feedback Form'}') || Subsection #{sub_no or 1} ('{sub_name or 'Feedback Form'}')"
    logger.info(f"\n" + "=" * 50)
    logger.info(f" 📝 [FEEDBACK FORM MODAL] Processing Feedback Form for {ctx_str}...")
    logger.info("=" * 50)

    # 1. First, check if Feedback Modal is ALREADY OPEN & VISIBLE on screen (DIKSHA Auto-Popup)
    modal_container = None
    target_frame = page
    for frame_target in [page] + page.frames:
        try:
            modal_cand = frame_target.locator(".modal-dialog, .modal-content, .modal-body, div[class*='modal']:has-text('Feedback'), div[class*='modal']:has-text('Share your Feedback'), div[class*='modal']:has-text('Submit Feedback')").first
            if await modal_cand.count() > 0 and await modal_cand.is_visible():
                modal_container = modal_cand
                target_frame = frame_target
                logger.info("  🎯 [AUTO-POPUP DETECTED] 'Share your Feedback' modal is ALREADY OPEN and VISIBLE on screen!")
                break
        except Exception:
            pass

    # 2. If modal is NOT open, click view_button or search for 'Give Feedback' button on page
    if not modal_container:
        fb_btn = view_button
        if not fb_btn or await fb_btn.count() == 0 or not await fb_btn.is_visible():
            for frame_t in [page] + page.frames:
                try:
                    cand_btn = frame_t.locator("button:has-text('Give Feedback'), a:has-text('Give Feedback'), button:has-text('Feedback'), a:has-text('Feedback'), a.activity-feedback, a.module-view-btn").first
                    if await cand_btn.count() > 0 and await cand_btn.is_visible():
                        fb_btn = cand_btn
                        break
                except Exception:
                    pass

        if fb_btn and await fb_btn.count() > 0:
            try:
                view_id = await fb_btn.get_attribute("data-id") or await fb_btn.get_attribute("act_id") or ""
                logger.info("  --> [FEEDBACK BUTTON CLICK] Clicking 'Give Feedback' button...")
                await safe_action_click(fb_btn)

                # JS Event Dispatcher Backup Click
                for frame_target in [page] + page.frames:
                    try:
                        await frame_target.evaluate("""(vid) => {
                            const btn = document.querySelector(`a[data-id="${vid}"]`) || document.querySelector('a.activity-feedback') || Array.from(document.querySelectorAll('a, button')).find(b => (b.innerText||'').toLowerCase().includes('feedback'));
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

        # Re-check for visible modal container after click
        for frame_target in [page] + page.frames:
            try:
                modal_cand = frame_target.locator(".modal-dialog, .modal-content, .modal-body, div[class*='modal']:has-text('Feedback'), div[class*='modal']:has-text('Share your Feedback'), div[class*='modal']:has-text('Submit Feedback')").first
                if await modal_cand.count() > 0 and await modal_cand.is_visible():
                    modal_container = modal_cand
                    target_frame = frame_target
                    logger.info("  --> Feedback popup modal is NOW OPEN and VISIBLE on screen!")
                    break
            except Exception:
                pass

    target_scope = modal_container if modal_container else target_frame

    # 3. Handle Emoji Star Rating Cards inside 'Share your Feedback' Modal
    try:
        exc_card = target_scope.locator("div:has-text('Excellent'), label:has-text('Excellent'), span:has-text('Excellent'), img[alt*='Excellent'], .rating-card:has-text('Excellent'), .star-rating:last-child").first
        if await exc_card.count() > 0 and await exc_card.is_visible():
            logger.info("  ⭐ [EMOJI RATING]: Selected 'Excellent' (5 Stars) rating response!")
            await exc_card.click(force=True)
            await page.wait_for_timeout(400)
        else:
            good_card = target_scope.locator("div:has-text('Good'), label:has-text('Good'), span:has-text('Good')").first
            if await good_card.count() > 0 and await good_card.is_visible():
                logger.info("  ⭐ [EMOJI RATING]: Selected 'Good' rating response!")
                await good_card.click(force=True)
                await page.wait_for_timeout(400)
    except Exception as r_ex:
        logger.warning(f"  --> Emoji rating card selection notice: {r_ex}")


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
                        ai_ans = await solve_question_with_ai(clean_q_dom, ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"])
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
                                ai_ans = await solve_question_with_ai(clean_ta_q, [])
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
    Returns unique, deduplicated action buttons inside a module collapse panel or card.
    Deduplicates title links vs View buttons using act_id and data-id attributes.
    Always prioritizes actual .module-view-btn elements over title links.
    """
    btns = None
    if collapse_panel and await collapse_panel.count() > 0:
        btns = collapse_panel.locator("a.module-view-btn, button.module-view-btn, .btn.module-view-btn, a[act_type], a[act_id], a.activity-list, button:has-text('View'), a:has-text('View'), button:has-text('Start'), a:has-text('Start'), button:has-text('Continue'), a:has-text('Continue')")
    
    if not btns or await btns.count() == 0:
        parent_card = header.locator("xpath=ancestor::*[contains(@class,'card') or contains(@class,'panel') or contains(@class,'modules_full_accordian_div')][1]").first
        if await parent_card.count() > 0:
            btns = parent_card.locator("a.module-view-btn, button.module-view-btn, .btn.module-view-btn, a[act_type], a[act_id], a.activity-list, button:has-text('View'), a:has-text('View')")
        else:
            btns = header.locator("xpath=following-sibling::div[1]").locator("a.module-view-btn, .btn, a[act_id], a")

    raw_count = await btns.count()
    id_map = {}
    fallback_btns = []

    for idx in range(raw_count):
        b = btns.nth(idx)
        try:
            act_id = await b.get_attribute("act_id") or await b.get_attribute("data-id") or ""
            b_class = await b.get_attribute("class") or ""
            is_real_view_btn = "module-view-btn" in b_class or "btn" in b_class or "view" in (await b.inner_text()).lower()

            if act_id:
                if act_id not in id_map:
                    id_map[act_id] = b
                elif is_real_view_btn:
                    id_map[act_id] = b  # Upgrade to real View button if previous match was title link
            else:
                row = b.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list') or contains(@class,'card-body')][1]").first
                row_key = (await row.inner_text()).strip() if await row.count() > 0 else (await b.inner_text()).strip()
                clean_key = ' '.join(row_key.split())
                if clean_key:
                    fallback_btns.append((clean_key, b))
        except Exception:
            fallback_btns.append(("", b))

    distinct_btns = list(id_map.values())
    seen_keys = set()
    for key, b in fallback_btns:
        if not key or key not in seen_keys:
            if key:
                seen_keys.add(key)
            distinct_btns.append(b)

    return distinct_btns


def sanitize_title_string(txt):
    if not txt:
        return ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    clean_lines = []
    for l in lines:
        l_lower = l.lower()
        if l_lower not in ("view", "start", "open", "continue", "retry") and not l_lower.startswith("0%") and not l_lower.startswith("100%"):
            clean_lines.append(l)
    if clean_lines:
        res = " ".join(clean_lines)
        res = re.sub(r"\s*(?:0%|100%|\d{1,3}%|View|Start|Continue)\s*$", "", res, flags=re.IGNORECASE).strip()
        return res
    return ""


async def get_real_subsection_title(page, btn):
    """
    Extracts full subsection title text from DIKSHA activity row or title link.
    Guarantees 100% real title extraction for all items as clean single-line strings.
    """
    try:
        act_id = await btn.get_attribute("act_id") or await btn.get_attribute("data-id") or ""
        if act_id:
            t_elements = page.locator(f"[act_id='{act_id}'], [data-id='{act_id}']")
            count = await t_elements.count()
            for idx in range(count):
                el = t_elements.nth(idx)
                txt = (await el.inner_text()).strip()
                if txt and txt.lower() not in ("view", "start", "open", "continue", "retry"):
                    clean_t = sanitize_title_string(txt)
                    if clean_t and len(clean_t) > 2:
                        return clean_t

        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list') or contains(@class,'card-body') or contains(@class,'activity') or contains(@class,'panel')][1]").first
        if await row.count() > 0:
            title_nodes = await row.locator("a.activity-list:not(.module-view-btn), .title, .activity-title, h4, h5, bdi, strong, .name, td, p, span, div.col-md-9, div.col-8, div.col-9, div.col-10").all()
            for t_el in title_nodes:
                txt = (await t_el.inner_text()).strip()
                clean_t = sanitize_title_string(txt)
                clean_lower = clean_t.lower()
                if clean_t and clean_lower not in ("view", "start", "open", "continue", "retry") and len(clean_t) > 3:
                    if not clean_lower.startswith("view") and not clean_lower.startswith("0%") and not clean_lower.startswith("100%"):
                        return clean_t

            row_raw = (await row.inner_text()).strip()
            clean_row = sanitize_title_string(row_raw)
            if clean_row and len(clean_row) > 3:
                return clean_row
    except Exception:
        pass

    try:
        raw_b = (await btn.inner_text()).strip()
        clean_b = sanitize_title_string(raw_b)
        if clean_b and clean_b.lower() not in ("view", "start", "open", "continue"):
            return clean_b
    except Exception:
        pass

    act_t = await btn.get_attribute("act_type") or "Resource"
    return f"{act_t.capitalize()} Activity"




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
    Checks progress-value spans (0%, 65%, 100%) and explicit checkmark icons.
    Strictly avoids false positives from parent container CSS classes.
    """
    try:
        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list') or contains(@class,'card-body') or contains(@class,'activity')][1]").first
        if await row.count() > 0:
            row_text = (await row.inner_text()).strip().lower()
            
            # 1. Explicit incomplete percentage badge check (0%, 50%, 65%, etc.)
            pct_matches = re.findall(r"(\d{1,3})%", row_text)
            if pct_matches:
                for val_str in pct_matches:
                    val = int(val_str)
                    if val < 100:
                        return False  # Incomplete item!
                    elif val == 100:
                        return True

            # 2. DIKSHA specific .progress-value check
            p_val_el = row.locator(".progress-value, span:has-text('%')").first
            if await p_val_el.count() > 0:
                p_txt = (await p_val_el.inner_text()).strip().lower()
                if "100%" in p_txt:
                    return True
                # Use word-boundary match to avoid '10%' matching inside '100%'
                elif re.search(r'\b([0-9]|[1-9][0-9])%', p_txt):
                    return False

            # 3. Explicit checkmark icons on the item row itself
            check_selectors = [
                "i.fa-check", ".fa-check-circle", ".fa-check-square",
                "i.completed-icon", "span.completed-icon",
                ".badge-success", "img[src*='check']", "img[src*='complete']", "svg[class*='check']"
            ]
            for sel in check_selectors:
                chk = row.locator(sel).first
                if await chk.count() > 0 and await chk.is_visible():
                    return True
    except Exception:
        pass

    return False


async def is_item_locked_by_diksha(btn):
    """
    Checks if an item row on DIKSHA is currently locked/disabled due to sequential prerequisite rules.
    (e.g., 'Not available unless the activity Assignment is completed.')
    """
    try:
        if await btn.is_disabled():
            return True
        b_class = (await btn.get_attribute("class") or "").lower()
        if "disabled" in b_class or "not-allowed" in b_class:
            return True

        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'list') or contains(@class,'card-body') or contains(@class,'activity') or self::li or self::div][1]").first
        if await row.count() > 0:
            row_text = (await row.inner_text()).strip().lower()
            if "not available unless" in row_text:
                return True
    except Exception:
        pass
    return False




async def is_header_100_percent_complete(header):
    """
    Determines if a module header is 100% completed on DIKSHA.
    Checks .progress-value (65% = False, 100% = True) and circle badges.
    """
    try:
        raw_text = (await header.inner_text()).strip().lower()
        
        # Check .progress-value element text explicitly
        prog_el = header.locator(".progress-value, span:has-text('%')").first
        if await prog_el.count() > 0:
            prog_txt = (await prog_el.inner_text()).strip().lower()
            m = re.search(r"(\d{1,3})%", prog_txt)
            if m:
                val = int(m.group(1))
                if val < 100:
                    return False  # 65%, 0%, etc -> Incomplete!
                elif val == 100:
                    return True

        # General regex search for any percentage badge (0% to 99%)
        pct_matches = re.findall(r"(\d{1,2})%", raw_text)
        if pct_matches:
            for val_str in pct_matches:
                val = int(val_str)
                if val < 100:
                    return False  # Incomplete percentage detected!

        # Check element class attributes for incomplete circle badges (e.g. p0, p13, p26, p50, p65)
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



async def ensure_on_course_page(page, target_course_url=None):
    """
    Checks if page redirected to dashboard.php or my-learning.
    If so, automatically re-navigates to the active course URL, clicks 'Lessons' tab, and resumes execution seamlessly!
    """
    try:
        curr_url = page.url.lower()
        if "dashboard.php" in curr_url or "my-learning" in curr_url:
            logger.warning("\n" + "=" * 70)
            logger.warning(" ⚠️  [AUTOMATIC DASHBOARD RECOVERY] Detected redirect to dashboard.php!")
            if target_course_url:
                logger.warning(f" 🚀 Re-navigating to active course URL: {target_course_url}")
                await page.goto(target_course_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                lessons_tab = page.locator(config.SELECTORS["lessons_tab"]).first
                if await lessons_tab.count() > 0 and await lessons_tab.is_visible():
                    await lessons_tab.click(force=True)
                    await page.wait_for_timeout(4000)
                logger.warning(" ✅ Successfully recovered to course page! Resuming module pass...")
            logger.warning("=" * 70 + "\n")
            return True
    except Exception as ex:
        logger.warning(f"  --> Dashboard recovery check notice: {ex}")
    return False


async def process_course_modules(page, answer_key=None, course_title="Unknown Course", username="", target_course_url=None):
    """
    Clicks 'Lessons' tab (waits 6s for server hydration), lists all Main Modules,
    auto-expands 50%/0% incomplete modules, and executes items without checkmarks.
    """
    disp_user = config.USER_NAMES.get(username, username) if username else "Active User"
    user_str = f"{disp_user} ({username})" if username else disp_user
    
    if not target_course_url:
        # Fallback: snapshot current URL — caller should always pass the explicit course URL
        target_course_url = page.url

    await ensure_on_course_page(page, target_course_url)



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
            logger.info("  --> Waiting 5 seconds for DIKSHA server to hydrate modules and auto-expand active incomplete section...")
            await page.wait_for_timeout(5000)
    except Exception as e:
        logger.warning(f"  --> Lessons tab click notice: {e}")

    # ── EARLY COMPLETION DETECTION ────────────────────────────────────────────
    # Some courses are already 100% complete — DIKSHA auto-pops the Give Feedback
    # modal immediately after the Lessons tab loads (no module scan needed).
    # Detect and handle this before the accordion engine runs.
    try:
        early_modal = page.locator(".modal.show, .modal.in, #feedbackModal, .feedback-modal").first
        if await early_modal.count() > 0 and await early_modal.is_visible():
            logger.info("  --> [EARLY COMPLETION DETECTED] Course is already 100% complete!")
            logger.info("  --> [EARLY COMPLETION] Give Feedback modal detected automatically by DIKSHA.")
            # Pass modal_already_open=True — skip button-click steps (modal is already visible)
            await process_certificate_feedback(page, modal_already_open=True)
            logger.info("=" * 67)
            logger.info(" 🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!")
            logger.info("=" * 67)
            logger.info(f"  ✔ User Profile : {user_str}")
            logger.info(f"  ✔ Course Title : {course_title}")
            logger.info("  ✔ Certificate  : Download Certificate Available")
            logger.info("  ✔ Status       : 100% Complete — Already Finished Before This Run!")
            logger.info("=" * 67 + "\n")
            return True
    except Exception as early_ex:
        logger.warning(f"  --> Early completion check notice: {early_ex}")
    # ─────────────────────────────────────────────────────────────────────────

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

        # Skip empty or non-lesson discussion, guideline, & navigation sections (Keep Certificate section for completion check)
        if not header_title or any(skip in lower_t for skip in ["discussion", "navigation", "file upload", "closed for replies", "pinned"]):
            logger.info(f"  --> [SKIP SECTION] '{header_title}' is a Discussion / Navigation section. Skipping!")
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
            logger.info(f"  [{idx:02d}/{total_real_modules:02d}] {title}")

        logger.info("=" * 35 + "\n")

        # 2. Sequential Execution Loop per Module with Smart Skipping & Auto-Expand
        for i, (header, header_title) in enumerate(main_modules, 1):
            await check_pause_status()
            logger.info("\n" + "=" * 35)
            logger.info(f" 📚 MODULE [{i:02d}/{total_real_modules:02d}]: {header_title}")
            logger.info("=" * 35)


            item_attempts = {}
            completed_items = set()
            distinct_btns = []
            all_items_completed_in_memory = False


            # Certificate Section / Customcert Download Link Protocol (Scoped strictly to Certificate module header / panel)
            is_cert_section = any(kw in header_title.lower() for kw in ["certificate", "customcert", "download certificate"])
            cert_el = header.locator("a[act_type='customcert'], a[href*='customcert'], a:has-text('Download Certificate')").first
            has_customcert_link = await cert_el.count() > 0

            if is_cert_section or has_customcert_link:
                logger.info(f"  🎓 [CERTIFICATE SECTION DETECTED] '{header_title}' reached!")
                logger.info("  --> All course requirements 100% satisfied!")

                # Expand the Certificate accordion panel FIRST before calling feedback
                # (Give Feedback button is inside the panel — invisible if panel is collapsed)
                try:
                    cert_toggle = header.locator("a[data-toggle='collapse'], a[href*='collapse'], a[aria-controls*='collapse']").first
                    if await cert_toggle.count() == 0:
                        cert_toggle = header
                    aria_exp = (await cert_toggle.get_attribute("aria-expanded") or "").lower()
                    if aria_exp != "true":
                        logger.info("  --> [CERTIFICATE] Expanding accordion panel to reveal Give Feedback button...")
                        await cert_toggle.scroll_into_view_if_needed()
                        await cert_toggle.click(force=True)
                        await page.wait_for_timeout(2500)
                    else:
                        logger.info("  --> [CERTIFICATE] Accordion panel already expanded.")
                except Exception as cert_expand_ex:
                    logger.warning(f"  --> [CERTIFICATE] Panel expand notice: {cert_expand_ex}")

                # Submit Give Feedback popup before logging course completion
                await process_certificate_feedback(page)

                logger.info("=" * 67)
                logger.info(" 🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!")
                logger.info("=" * 67)
                logger.info(f"  ✔ User Profile : {user_str}")
                logger.info(f"  ✔ Course Title : {course_title}")
                logger.info("  ✔ Certificate  : Download Certificate Available")
                logger.info("  ✔ Status       : 100% Complete — All Modules & Assessments Done!")
                logger.info("=" * 67 + "\n")
                return True


            max_module_attempts = 3
            module_retry_pass = 0
            while True:
                module_retry_pass += 1
                if module_retry_pass > 1:
                    logger.info(f"\n  🔄 [RE-STARTING FULL MODULE PASS #{module_retry_pass}/{max_module_attempts}] Re-scanning '{header_title}' & re-evaluating all subsections...")

                # Check if Module header is ALREADY 100% complete
                if await is_header_100_percent_complete(header):
                    logger.info(f"  --> [✓ SKIP MODULE] '{header_title}' is ALREADY 100% COMPLETED. [Skipping!]")

                    break

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
                distinct_btns = await get_section_action_buttons(collapse_panel, header)
                total_sec_items = len(distinct_btns)

                if total_sec_items == 0 and not await is_header_100_percent_complete(header):
                    logger.info(f"  --> [RE-EXPANDING ACCORDION] Re-clicking header for '{header_title}' to render inner action buttons...")
                    try:
                        await safe_action_click(click_target)
                        await page.wait_for_timeout(3000)
                        distinct_btns = await get_section_action_buttons(collapse_panel, header)
                        total_sec_items = len(distinct_btns)
                    except Exception as ex:
                        logger.warning(f"  --> Notice re-expanding accordion '{header_title}': {ex}")

                if total_sec_items == 0:
                    logger.info("     [-] No action buttons inside this section. Moving to next...")
                    break


                # 📋 PRINT FULL SUBSECTION BREAKDOWN CHECKLIST SUMMARY ON EVERY MODULE PASS!
                logger.info(f"  📋 [SUBSECTION BREAKDOWN ({total_sec_items} ITEMS)]:")
                for idx, b in enumerate(distinct_btns, 1):
                    try:
                        r_txt = await get_real_subsection_title(page, b)
                        b_txt = (await b.inner_text()).strip()
                        is_done = (r_txt in completed_items) or (b_txt in completed_items) or await is_item_100_percent_complete(b)
                        chk = "✓" if is_done else "⏳"
                        pct = "100%" if is_done else "0%"
                        act_lbl = b_txt if b_txt and b_txt.lower() in ("view", "start", "open", "continue", "retry") else "View"
                        act_lbl = act_lbl.capitalize()
                        t_disp = r_txt[:49].strip() + "..." if len(r_txt) > 52 else r_txt
                        logger.info(f"     [{idx:02d}/{total_sec_items:02d}] {chk} {t_disp} || {pct} || {act_lbl}")
                    except Exception:
                        pass
                logger.info("  " + "-" * 55)

                lock_triggered = False  # Flag: set True when a locked item triggers prerequisite re-execution
                for j, btn in enumerate(distinct_btns, 1):
                    await check_pause_status()
                    try:
                        await btn.scroll_into_view_if_needed()
                        await page.wait_for_timeout(200)
                    except Exception:
                        pass

                    btn_text = (await btn.inner_text()).strip()
                    real_item_title = await get_real_subsection_title(page, btn)

                    is_generic_btn = btn_text.lower() in ("view", "start", "open", "continue", "retry")
                    already_done_in_mem = (real_item_title in completed_items) or (not is_generic_btn and btn_text in completed_items)

                    if already_done_in_mem or await is_item_100_percent_complete(btn):
                        disp_t = real_item_title[:42].strip() + "..." if len(real_item_title) > 45 else real_item_title
                        logger.info(f"  --> [✓ ALREADY DONE] SUBSECTION [{j:02d}/{total_sec_items:02d}]: '{disp_t}' is 100% complete. [Skipping!]")
                        if not is_generic_btn:
                            completed_items.add(btn_text)
                        if real_item_title and real_item_title.lower() not in ("view", "start", "open", "continue"):
                            completed_items.add(real_item_title)
                        continue

                    # 🔒 Check if item is locked by DIKSHA prerequisite rule (e.g. 'Not available unless...')
                    if await is_item_locked_by_diksha(btn):
                        disp_t = real_item_title[:42].strip() + "..." if len(real_item_title) > 45 else real_item_title
                        logger.warning(f"  --> 🔒 [LOCKED ITEM DETECTED] SUBSECTION [{j:02d}/{total_sec_items:02d}]: '{disp_t}' is locked by DIKSHA prerequisite rule.")
                        logger.info("  --> Re-triggering prior item & reloading page to hydrate DIKSHA server unlock...")
                        
                        # Re-execute prior prerequisite item if available
                        if j >= 2:
                            try:
                                prev_btn = distinct_btns[j - 2]
                                prev_title = await get_real_subsection_title(page, prev_btn)
                                prev_act_type = await prev_btn.get_attribute("act_type") or "resource"
                                logger.info(f"  --> Re-executing prior prerequisite item [{j-1:02d}/{total_sec_items:02d}]: '{prev_title}' to unlock current item...")
                                if prev_act_type == "url":
                                    await process_video_activity(page, prev_btn)
                                elif prev_act_type == "resource":
                                    await process_pdf_activity(page, prev_btn)
                                elif prev_act_type == "h5pactivity":
                                    await process_h5p_activity(page, prev_btn, answer_key, course_title=course_title)
                            except Exception as ex:
                                logger.warning(f"  --> Notice re-triggering prior item: {ex}")

                        try:
                            await page.reload()
                            await page.wait_for_timeout(5000)
                            await ensure_on_course_page(page, target_course_url)
                        except Exception:
                            pass
                        lock_triggered = True
                        break  # Exit for loop — outer while will re-scan freshly reloaded page




                    act_type = await btn.get_attribute("act_type") or "resource"

                    # ── Per-Subsection 3-Attempt Retry Loop ──────────────────────────────────
                    item_success = False
                    for item_attempt in range(1, 4):
                        logger.info("\n" + "=" * 35)
                        logger.info(f" ▶ SUBSECTION [{j:02d}/{total_sec_items:02d}]: '{real_item_title}' (Type: '{act_type}') [Attempt {item_attempt}/3]")
                        logger.info("=" * 35)

                        try:
                            if act_type == "url":
                                await process_video_activity(page, btn)
                            elif act_type == "resource":
                                await process_pdf_activity(page, btn)
                            elif act_type == "h5pactivity":
                                await process_h5p_activity(page, btn, answer_key, course_title=course_title)
                            elif act_type == "feedback" or "feedback" in real_item_title.lower():
                                await process_feedback_activity(page, btn, answer_key, module_name=header_title, module_no=i, sub_name=real_item_title, sub_no=j, course_title=course_title)
                            elif act_type == "quiz" or "assessment" in real_item_title.lower():
                                await process_quiz_assessment(page, btn, answer_key, module_name=header_title, module_no=i, sub_name=real_item_title, sub_no=j, course_title=course_title)
                            else:
                                await btn.click(force=True)
                                await page.wait_for_timeout(3000)
                                await close_activity_modal(page)
                                await wait_for_server_checkmark(page, item_btn=btn)

                            # Verify actual success via 100% checkmark — only mark done if truly complete
                            if await is_item_100_percent_complete(btn):
                                logger.info(f"  ✅ [ATTEMPT {item_attempt}/3 SUCCESS] '{real_item_title}' verified 100% complete!")
                                item_success = True
                                break
                            else:
                                if item_attempt < 3:
                                    logger.warning(f"  ⚠️ [ATTEMPT {item_attempt}/3 INCOMPLETE] '{real_item_title}' not yet 100% on server. Retrying in 5s...")
                                    await asyncio.sleep(5)
                                else:
                                    logger.warning(f"  ⚠️ [ALL 3 ATTEMPTS EXHAUSTED] '{real_item_title}' failed all 3 attempts. Restarting course from beginning...")
                                    raise _CourseRestartSignal(real_item_title)

                        except _CourseRestartSignal:
                            raise  # Let it bubble up to process_course_modules restart handler
                        except Exception as item_ex:
                            logger.error(f"     [-] Attempt {item_attempt}/3 execution notice: {item_ex}")
                            if item_attempt < 3:
                                logger.info(f"  --> Retrying in 5s... (Attempt {item_attempt + 1}/3)")
                                await asyncio.sleep(5)
                            else:
                                logger.warning(f"  ⚠️ [CRASH ALL 3 ATTEMPTS] '{real_item_title}' crashed all 3 times. Restarting course from beginning...")
                                raise _CourseRestartSignal(real_item_title)

                    # Only add to completed_items if genuinely verified successful
                    if item_success:
                        if not is_generic_btn:
                            completed_items.add(btn_text)
                        if real_item_title and real_item_title.lower() not in ("view", "start", "open", "continue"):
                            completed_items.add(real_item_title)

                    logger.info("  --> DIKSHA Server sync buffer: waiting 4 seconds for next item unlock...")
                    try:
                        await page.wait_for_timeout(4000)
                    except Exception:
                        pass


                # If a lock was triggered, restart the while loop to re-scan items on the freshly reloaded page
                # The reloaded page should now show item 13 as unlocked and ready to execute
                if lock_triggered:
                    if module_retry_pass > max_module_attempts + 3:
                        logger.warning(f"  ⚠️ [LOCK RETRY LIMIT] Exceeded max lock retries for '{header_title}'. Proceeding to sync check.")
                    else:
                        logger.info(f"  🔓 [LOCK RETRY] Prerequisite executed. Re-scanning '{header_title}' buttons to execute newly unlocked item...")
                        continue  # Restart outer while loop — re-scans all buttons on fresh page

                # DOUBLE CONFIRMATION & STRICT 100% COMPLETION GATE GUARD
                logger.info(f"  --> [DOUBLE CONFIRMATION] Verifying 100% completion for '{header_title}'...")
                try:
                    await page.wait_for_timeout(2000)
                except Exception:
                    pass


                server_synced = False
                for sync_step in range(1, 4):
                    logger.info(f"\n  ⏳ [MODULE SYNC {sync_step}/3] Reloading page & re-scanning subsections...")
                    try:
                        await page.reload()
                        await page.wait_for_timeout(3000)
                        await ensure_on_course_page(page, target_course_url)


                        # Step 1: Re-expand accordion panel ONLY if collapsed
                        click_target = header.locator("a[data-toggle='collapse'], a[href*='collapse'], a[aria-controls*='collapse']").first
                        if await click_target.count() == 0:
                            click_target = header

                        is_collapsed = True
                        try:
                            link_class = (await click_target.get_attribute("class") or "").split()
                            aria_exp = (await click_target.get_attribute("aria-expanded") or "").lower()
                            if "collapsed" in link_class or aria_exp == "false":
                                is_collapsed = True
                            elif aria_exp == "true":
                                is_collapsed = False
                        except Exception:
                            is_collapsed = True

                        if is_collapsed and await click_target.count() > 0:
                            logger.info(f"  --> [EXPANDING ACCORDION] Expanding accordion panel for '{header_title}'...")
                            await safe_action_click(click_target)
                            await page.wait_for_timeout(3000)


                        collapse_panel = None
                        if collapse_id and await page.locator(f"#{collapse_id}").count() > 0:
                            collapse_panel = page.locator(f"#{collapse_id}").first
                        else:
                            parent_div = header.locator("xpath=ancestor::*[contains(@class,'modules_full_accordian_div') or contains(@class,'panel') or contains(@class,'card')][1]").first
                            if await parent_div.count() > 0:
                                collapse_panel = parent_div.locator(".panel-collapse, .collapse, .card-body").first

                        # Step 2: Re-scan and re-print SUBSECTION BREAKDOWN list on Attempt #sync_step
                        sync_btns = await get_section_action_buttons(collapse_panel, header)
                        if sync_btns:
                            logger.info(f"  📋 [SUBSECTION BREAKDOWN ({len(sync_btns)} ITEMS) - Sync Attempt #{sync_step}/3]:")
                            for idx, b in enumerate(sync_btns, 1):
                                try:
                                    b_txt = (await b.inner_text()).strip()
                                    r_txt = await get_real_subsection_title(page, b)
                                    is_done = (r_txt in completed_items) or (b_txt in completed_items) or await is_item_100_percent_complete(b)
                                    chk = "✓" if is_done else "⏳"
                                    pct = "100%" if is_done else "0%"
                                    act_lbl = b_txt if b_txt and b_txt.lower() in ("view", "start", "open", "continue", "retry") else "View"
                                    act_lbl = act_lbl.capitalize()
                                    t_disp = r_txt[:49].strip() + "..." if len(r_txt) > 52 else r_txt
                                    logger.info(f"     [{idx:02d}/{len(sync_btns):02d}] {chk} {t_disp} || {pct} || {act_lbl}")
                                except Exception:
                                    pass
                            logger.info("  " + "-" * 55)




                        # Step 3: Find any incomplete subsection item and re-execute it right now!
                        if sync_btns:
                            for s_idx, s_btn in enumerate(sync_btns, 1):
                                try:
                                    await s_btn.scroll_into_view_if_needed()
                                    await page.wait_for_timeout(200)
                                except Exception:
                                    pass

                                s_btn_text = (await s_btn.inner_text()).strip()
                                s_item_title = await get_real_subsection_title(page, s_btn)
                                is_gen_b = s_btn_text.lower() in ("view", "start", "open", "continue", "retry")
                                is_item_done = (s_item_title in completed_items) or (not is_gen_b and s_btn_text in completed_items) or await is_item_100_percent_complete(s_btn)

                                if not is_item_done:
                                    # NOTE: A locked item here is theoretically IMPOSSIBLE with the new system.
                                    # The main loop resolves all locks via lock_triggered+continue BEFORE reaching sync.
                                    # If this fires it indicates a DIKSHA server-side race condition — log it as ERROR.
                                    if await is_item_locked_by_diksha(s_btn):
                                        logger.error(f"  ❌ [UNEXPECTED LOCK IN SYNC] Item [{s_idx:02d}/{len(sync_btns):02d}]: '{s_item_title}' is locked during sync — this should not happen. Triggering course restart...")
                                        raise _CourseRestartSignal(s_item_title)

                                    logger.info(f"  🔄 [SYNC RE-EXECUTION Attempt #{sync_step}/3] Found incomplete item [{s_idx:02d}/{len(sync_btns):02d}]: '{s_item_title}'. Executing item now...")

                                    s_act_type = await s_btn.get_attribute("act_type") or "resource"
                                    if s_act_type == "url":
                                        await process_video_activity(page, s_btn)
                                    elif s_act_type == "resource":
                                        await process_pdf_activity(page, s_btn)
                                    elif s_act_type == "h5pactivity":
                                        await process_h5p_activity(page, s_btn, answer_key, course_title=course_title)
                                    elif s_act_type == "feedback" or "feedback" in s_item_title.lower():
                                        await process_feedback_activity(page, s_btn, answer_key, module_name=header_title, module_no=i, sub_name=s_item_title, sub_no=s_idx, course_title=course_title)
                                    elif s_act_type == "quiz" or "assessment" in s_item_title.lower():
                                        await process_quiz_assessment(page, s_btn, answer_key, module_name=header_title, module_no=i, sub_name=s_item_title, sub_no=s_idx, course_title=course_title)


                                    if not is_gen_b:
                                        completed_items.add(s_btn_text)
                                    if s_item_title and s_item_title.lower() not in ("view", "start", "open", "continue"):
                                        completed_items.add(s_item_title)


                        # Step 4: Strict verification - check if Header is 100% OR all items checkmarked
                        sync_btns = await get_section_action_buttons(collapse_panel, header)
                        all_items_checkmarked = True
                        if sync_btns:
                            for s_check_btn in sync_btns:
                                if not await is_item_100_percent_complete(s_check_btn):
                                    all_items_checkmarked = False
                                    break
                        else:
                            all_items_checkmarked = False

                        if await is_header_100_percent_complete(header) or all_items_checkmarked:
                            logger.info(f"  ✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified for '{header_title}' on Attempt #{sync_step}/3!")
                            server_synced = True
                            break
                        # Not done yet — wait 15s for DIKSHA server to register progress before next attempt
                        logger.info(f"  ⏳ [SYNC WAIT] Attempt {sync_step}/3 incomplete. Waiting 15s for server sync...")
                        await asyncio.sleep(15)
                    except _CourseRestartSignal:
                        raise  # Never swallow the course restart signal
                    except Exception as m_sync_ex:
                        logger.warning(f"  --> Module sync attempt #{sync_step} notice: {m_sync_ex}")
                        await asyncio.sleep(15)


                if server_synced or await is_header_100_percent_complete(header):
                    logger.info(f"  🎓 [MODULE COMPLETED] '{header_title}' completed successfully! Advancing to next module...\n")
                    break

                # Both sync attempts failed — restart the entire course from the beginning
                logger.warning(f"  ⚠️ [MODULE SYNC FAILED] '{header_title}' not 100% after 3 sync attempts.")
                logger.warning(f"  🔄 Triggering full course restart to retry from the beginning...")
                raise _CourseRestartSignal(header_title)

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

    logger.info("   DIKSHA AUTOMATION PIPELINE")
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
            for _cr in range(1, 7):  # Up to 5 full course restarts if an item fails all 3 attempts
                try:
                    await process_course_modules(page, c_key, course_title=t_title, username=username, target_course_url=target_course_url)
                    break  # Completed normally
                except _CourseRestartSignal as sig:
                    if _cr < 6:
                        logger.warning(f"\n{'=' * 67}")
                        logger.warning(f" 🔄 [COURSE RESTART {_cr}/5] Item '{sig}' failed all attempts. Restarting course from beginning...")
                        logger.warning(f"{'=' * 67}")
                        try:
                            await page.goto(target_course_url, wait_until="domcontentloaded", timeout=60000)
                            await page.wait_for_timeout(5000)
                        except Exception:
                            pass
                    else:
                        logger.error(f"  ❌ [COURSE RESTART LIMIT] Course restarted 5 times. Item '{sig}' still failing. Moving on.")
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
                    for _cr in range(1, 7):  # Up to 5 full course restarts if an item fails all 3 attempts
                        try:
                            await process_course_modules(page, course_answer_key, course_title=c['title'], username=username, target_course_url=c['url'])
                            break  # Completed normally
                        except _CourseRestartSignal as sig:
                            if _cr < 6:
                                logger.warning(f"\n{'=' * 67}")
                                logger.warning(f" 🔄 [COURSE RESTART {_cr}/5] Item '{sig}' failed all attempts. Restarting course from beginning...")
                                logger.warning(f"{'=' * 67}")
                                try:
                                    await page.goto(c['url'], wait_until="domcontentloaded", timeout=60000)
                                    await page.wait_for_timeout(5000)
                                except Exception:
                                    pass
                            else:
                                logger.error(f"  ❌ [COURSE RESTART LIMIT] Course restarted 5 times. Item '{sig}' still failing. Moving on.")




        # Screenshot completion milestone (with timeout safety for external fonts)
        screenshot_path = config.SCREENSHOT_DIR / "diksha_pipeline_executed.png"
        try:
            await page.screenshot(path=str(screenshot_path), timeout=5000)
            logger.info("Pipeline executed successfully.")
        except Exception:
            logger.info("Pipeline executed successfully.")


        if config.KEEP_BROWSER_OPEN and not config.HEADLESS:
            logger.info("=" * 67)
            logger.info("  [KEEP-OPEN] Chrome browser is kept OPEN for your inspection!")
            logger.info("  Close the browser window or press Ctrl+C in console when finished.")
            logger.info("=" * 67)

            try:
                while True:
                    await asyncio.sleep(10)
            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("Closing browser...")
        else:
            await page.wait_for_timeout(3000)
            await browser.close()



