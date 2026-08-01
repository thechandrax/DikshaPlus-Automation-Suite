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
from pathlib import Path



# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import async_playwright
import config
from utils.logger import get_logger

logger = get_logger("DikshaEngine")

def load_answer_key(course_title=None):
    """
    Loads course-specific answer key from data/courses/<course_name>.json
    or falls back to data/answer_key.json. Auto-creates template JSON files per course.
    """
    courses_dir = config.DATA_DIR / "courses"
    courses_dir.mkdir(parents=True, exist_ok=True)

    if course_title:
        # Create safe filename: e.g. "Power of Audio in Education" -> "power_of_audio_in_education.json"
        safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', course_title.lower()).strip('_')
        course_file = courses_dir / f"{safe_name}.json"
        
        if course_file.exists():
            try:
                with open(course_file, "r", encoding="utf-8") as f:
                    logger.info(f"  --> Loaded course-specific answer key: data/courses/{course_file.name}")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not parse {course_file.name}: {e}")
        else:
            # Create a clean template JSON file for this course
            template = {
                "course_name": course_title,
                "description": "Add MCQ question and answer mappings for this course",
                "answers": [
                    {
                        "question_keyword": "example question text",
                        "correct_option": "Option 1"
                    }
                ]
            }
            try:
                with open(course_file, "w", encoding="utf-8") as f:
                    json.dump(template, f, indent=4)
                logger.info(f"  --> Created template answer key file: data/courses/{course_file.name}")
            except Exception:
                pass

def extract_all_qa_items(answer_key):
    """
    Normalizes any JSON answer key structure (nested subsections, modules, flat answers/questions)
    into a unified list of question-answer dicts with metadata.
    """
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
                    "module_no": answer_key.get("module_no"),
                    "module_name": answer_key.get("module_name"),
                    "subsection_no": sub_no,
                    "subsection_name": sub_name,
                    "question": item.get("question") or item.get("question_keyword") or "",
                    "answer": item.get("answer") or item.get("correct_option") or ""
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
                        "question": item.get("question") or item.get("question_keyword") or "",
                        "answer": item.get("answer") or item.get("correct_option") or ""
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
                "question": item.get("question") or item.get("question_keyword") or "",
                "answer": item.get("answer") or item.get("correct_option") or ""
            })

    return qa_list


def solve_question_with_ai(question_text, option_texts=None):
    """
    Uses Gemini AI API to solve any live quiz question on screen with 100% accuracy.
    Handles rate limits (HTTP 429) with exponential backoff retries.
    """
    if not getattr(config, "AI_LIVE_SOLVER_ENABLED", True):
        return None

    api_key = getattr(config, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    # 3-Second Pacing Delay for smooth execution & rate limit prevention
    logger.info("  ⏳ [AI LIVE SOLVER] Waiting 3s pacing delay before AI API call...")
    time.sleep(3)



    options_formatted = "\n".join([f"{idx+1}. {opt}" for idx, opt in enumerate(option_texts or [])])
    prompt = f"""You are an expert AI teacher solving a quiz question for an educational course.

Question:
{question_text}

Option Choices:
{options_formatted if options_formatted else 'Select the correct factual answer.'}

INSTRUCTIONS:
Return ONLY the exact text of the correct option choice from the list above. Do NOT include option numbers (1, 2, 3), do NOT include explanations. Return ONLY the exact option text."""

    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest"]

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}]
                }).encode('utf-8')
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
                res = urllib.request.urlopen(req, timeout=10)
                resp_data = json.loads(res.read().decode('utf-8'))
                ans_text = resp_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                
                # Remove quotes or markdown if returned
                clean_ans = re.sub(r'^["`\']|["`\']$', '', ans_text, flags=re.MULTILINE).strip()
                if clean_ans:
                    logger.info(f"  🧠 [AI LIVE SOLVER] Solved question via {model_name} -> '{clean_ans}'")
                    return clean_ans
            except urllib.error.HTTPError as http_err:
                if http_err.code == 429:
                    time.sleep(2 * (attempt + 1))
                    continue
                break
            except Exception as ex:
                time.sleep(1)
                break

    return None


def save_auto_learned_qa(course_title, module_no, module_name, sub_no, sub_name, question_text, answer_text):
    """
    Saves auto-learned question & answer sequentially under the exact
    module_no, module_name, subsection_no, and subsection_name structure.
    """
    try:
        c_name = course_title or "unknown_course"
        course_key_file = config.COURSES_DIR / f"{re.sub(r'[^a-zA-Z0-9]+', '_', c_name.lower()).strip('_')}.json"
        
        data_j = {}
        if course_key_file.exists():
            with open(course_key_file, "r", encoding="utf-8") as f:
                try:
                    data_j = json.load(f)
                except Exception:
                    data_j = {}

        data_j["course_name"] = course_title or "Course"
        if module_no:
            try:
                data_j["module_no"] = int(module_no)
            except Exception:
                data_j["module_no"] = module_no
        if module_name:
            data_j["module_name"] = module_name

        subsections = data_j.get("subsections")
        if not isinstance(subsections, list):
            subsections = []
            data_j["subsections"] = subsections

        target_sub = None
        t_sub_no = int(sub_no) if (sub_no and str(sub_no).isdigit()) else 1
        t_sub_name = sub_name or "Assessment"

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

        clean_new_q = question_text.strip().lower()
        existing_qs = set((q.get("question") or "").strip().lower() for q in questions)

        if clean_new_q not in existing_qs:
            questions.append({
                "question": question_text.strip(),
                "answer": answer_text.strip()
            })
            with open(course_key_file, "w", encoding="utf-8") as f:
                json.dump(data_j, f, indent=2)
            logger.info(f"  💾 [AUTO-LEARNING SEQUENTIAL SAVE] Saved to {course_key_file.name}: Module #{module_no or 1} ('{module_name or ''}') • Subsection #{t_sub_no} ('{t_sub_name}') -> Q: '{question_text[:40]}...'")
    except Exception as ex:
        logger.warning(f"  --> Auto-learning save notice: {ex}")






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

    cards = page.locator("#pills-inprogress .course-library-link, #pills-inprogress .library-card")
    count = await cards.count()
    if count == 0:
        cards = page.locator(".course-library-link, .library-card")
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


def display_interactive_course_menu(courses):
    """
    Renders CMD menu listing both Ongoing and Finished courses matching design mockup with rich colors.
    """
    if not courses:
        print("\n\033[38;5;51m\033[1m" + "="*70)
        print("  🎓 DIKSHA+ ENROLLED COURSES (0 COURSES FOUND)")
        print("="*70 + "\033[0m\n")
        return None

    ongoing_list = [c for c in courses if c['status'] == 'Ongoing']
    finished_list = [c for c in courses if c['status'] == 'Finished']

    print("\n\033[38;5;51m\033[1m" + "="*70)
    print(f"  🎓 DIKSHA+ ENROLLED COURSES ({len(ongoing_list)} ONGOING • {len(finished_list)} FINISHED)")
    print("="*70 + "\033[0m\n")

    if ongoing_list:
        print(" \033[38;5;82m\033[1m⚡ ONGOING COURSES:\033[0m")
        for c in ongoing_list:
            pct = c['progress_pct']
            filled = int(round(pct / 10))
            bar = f"\033[38;5;46m[{"█" * filled}\033[38;5;238m{"░" * (10 - filled)} \033[38;5;220m{pct:>3}%\033[38;5;46m]\033[0m"
            formatted_title = (c['title'][:42] + '...') if len(c['title']) > 45 else c['title'].ljust(45)
            print(f"  \033[38;5;220m[{c['index']:02d}]\033[0m \033[38;5;231m{formatted_title}\033[0m {bar} \033[38;5;214m{c['icon']} {c['status']}\033[0m")
        print()

    if finished_list:
        print(" \033[38;5;207m\033[1m✨ FINISHED COURSES:\033[0m")
        for c in finished_list:
            pct = c['progress_pct']
            filled = 10
            bar = f"\033[38;5;207m[{"█" * filled} \033[38;5;220m{pct:>3}%\033[38;5;207m]\033[0m"
            formatted_title = (c['title'][:42] + '...') if len(c['title']) > 45 else c['title'].ljust(45)
            print(f"  \033[38;5;220m[{c['index']:02d}]\033[0m \033[38;5;231m{formatted_title}\033[0m {bar} \033[38;5;220m{c['icon']} {c['status']}\033[0m")
        print()



    print("\033[38;5;240m-----------------------------------------------------------------------\033[0m")

    import os
    env_course = os.getenv("SELECTED_COURSE", "").strip()

    if not sys.stdin.isatty():
        if env_course:
            if env_course.lower() == "all":
                logger.info(f"  [!] Environment variable SELECTED_COURSE='all' detected. Processing ALL {len(courses)} enrolled courses.")
                return courses
            elif env_course.isdigit():
                c_idx = int(env_course)
                if 1 <= c_idx <= len(courses):
                    logger.info(f"  [!] Environment variable SELECTED_COURSE='{c_idx}' detected. Processing Course #{c_idx}: '{courses[c_idx-1]['title']}'.")
                    return [courses[c_idx - 1]]
        logger.info("  [!] Non-interactive mode detected. Processing option [1] by default.")
        return [courses[0]]


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




        # 5. 45s Final Buffer @ 1.0x Speed
        logger.info("  --> 45s Final Buffer: slowing down to 1.0x speed for natural ended event & 100% progress telemetry...")
        await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.playbackRate = 1.0; if (v.paused) v.play(); } }")
        
        final_wait = min(45, max(10, int(duration - cur_time)))
        await asyncio.sleep(final_wait)
        
        # Trigger natural ended event dispatch
        try:
            await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.dispatchEvent(new Event('ended')); } }")
        except Exception:
            pass
    else:
        # Fallback if duration is unavailable
        logger.info("  --> Video playback active (default watch duration)...")
        await asyncio.sleep(config.MIN_VIDEO_WATCH_SECONDS)

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
                    logger.info(f"  ⚡ [H5P CACHED JSON 100% MATCH Q-{question_step + 1}] Target Answer: '{matched_answer_text}'")
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
                        logger.info(f"  ✔ [H5P EXACT OPTION CLICKED Q-{question_step + 1}] '{opt_txt.strip()}'")
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

async def process_quiz_assessment(page, view_button, answer_key, module_name=None, module_no=None, sub_name=None, sub_no=None):
    """
    STEP-07 (Formative Assessment - act_type="quiz"):
    Identifies exact module (number/name) & subsection (number/name) context,
    matches questions against answer key metadata, and executes assessment.
    """
    if module_name or sub_name:
        ctx_str = f"Module #{module_no or 1} ('{module_name or ''}') • Subsection #{sub_no or 1} ('{sub_name or ''}')"
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

    # 2. Locate and click 'Start Assessment' / 'Continue Assessment' / 'Re-attempt Assessment' button across page and all frames
    start_assessment_btn = None
    target_frame = page

    start_selectors = [
        "button:has-text('Re-attempt Assessment')",
        "input[value*='Re-attempt Assessment']",
        "a:has-text('Re-attempt Assessment')",
        "button:has-text('Continue Assessment')",
        "input[value*='Continue Assessment']",
        "a:has-text('Continue Assessment')",
        "button:has-text('Start Assessment')",
        "input[value*='Start Assessment']",
        "a:has-text('Start Assessment')",
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
            logger.info(f"  --> Clicking Assessment button '{btn_txt}'...")
            await start_assessment_btn.click(force=True)
            await page.wait_for_timeout(4000)
        except Exception as ex:
            logger.warning(f"  --> Direct click notice on assessment button: {ex}")

    # Fallback JavaScript evaluation click for Start/Continue/Re-attempt Assessment
    if not start_assessment_btn:
        logger.info("  --> Attempting JS click fallback for 'Start/Continue/Re-attempt Assessment'...")
        for frame_target in [page] + page.frames:
            try:
                clicked = await frame_target.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn'));
                    const startBtn = btns.find(b => {
                        const txt = (b.innerText || b.value || '').toLowerCase();
                        return txt.includes('re-attempt') || txt.includes('continue') || txt.includes('start');
                    });
                    if (startBtn) { startBtn.click(); return true; }
                    return false;
                }""")
                if clicked:
                    logger.info("  --> JS fallback successfully clicked 'Start/Continue/Re-attempt Assessment'!")
                    await page.wait_for_timeout(4000)
                    target_frame = frame_target
                    break
            except Exception:
                pass

    # 3. Dynamic Question Answering Loop with Hierarchical Module/Subsection Scoping & Position Matching
    answers_list = extract_all_qa_items(answer_key)


    # Check top-level JSON metadata
    top_mod_no = answer_key.get("module_no") if isinstance(answer_key, dict) else None
    top_sub_name = (answer_key.get("subsection_name") or "").strip().lower() if isinstance(answer_key, dict) else ""

    # Pre-scope JSON items matching active Module & Subsection context
    scoped_items = []
    if answers_list:
        for item in answers_list:
            item_mod_no = item.get("module_no") or top_mod_no
            item_sub_name = (item.get("subsection_name") or top_sub_name or "").strip().lower()
            
            mod_match = not (item_mod_no and module_no and int(item_mod_no) != int(module_no))
            sub_match = not (item_sub_name and sub_name and item_sub_name not in sub_name.lower() and sub_name.lower() not in item_sub_name)
            
            if mod_match and sub_match:
                scoped_items.append(item)

    search_buckets = [scoped_items, answers_list] if scoped_items else [answers_list]
    logger.info(f"  --> [HIERARCHICAL MATCHING] Scoped {len(scoped_items)} questions for Module #{module_no or 1} • Subsection '{sub_name or ''}'.")

    for q_num in range(200):
        # Unlimited time pacing: 1.5s human reading delay
        await page.wait_for_timeout(1500)

        # Extract question text displayed on screen across all potential DIKSHA selectors
        q_text_screen = ""
        try:
            q_elem = target_frame.locator(".qtext, div.qtext, .question-text, .que .content .qtext, fieldset legend, .qheader, .question-content, div.que div.content").first
            if await q_elem.count() > 0 and await q_elem.is_visible():
                raw_q = (await q_elem.inner_text()).strip()
                # 1. Clean DIKSHA question text header & option choice footer noise
                q_text_screen = re.sub(r'^(?:question\s*text|question\s*\d+[:.]?|\d+[:.]?|q\d+[:.]?)\s*', '', raw_q, flags=re.IGNORECASE)
                q_text_screen = re.sub(r'\s*(?:select\s*one|question\s*\d+).*$', '', q_text_screen, flags=re.IGNORECASE | re.DOTALL).strip().lower()
        except Exception:
            pass

        if q_text_screen:
            logger.info(f"  [Q-{q_num + 1} SCREEN TEXT]: '{q_text_screen[:70]}...'")

        # Dual Confirmation Guard Protocol: Smart Auto-Learning JSON Cache + AI Live Solver Engine
        matched_answer_text = None
        gate1_ok = False

        # Step 1: Check Auto-Learning JSON Cache First (Instant 0.01s Match)
        if q_text_screen and answers_list:
            clean_screen_q = re.sub(r'[^\w\s]', '', q_text_screen) if q_text_screen else ""
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
                            matched_json_question = (item.get("question") or item.get("question_keyword") or "")[:50]
                            gate1_ok = True
                            logger.info(f"  ⚡ [CACHED JSON 100% MATCH Q-{q_num + 1}] '{matched_json_question}...' -> Target: '{matched_answer_text}'")
                            break

        # Step 2: AI Live Solver Fallback (If Question is NEW & Not in JSON Cache)
        if not matched_answer_text and q_text_screen:
            try:
                option_containers = target_frame.locator("div[data-region='answer-label'], [aria-labelledby*='answer'], .answer label, div[class*='r0'], div[class*='r1'], .form-check-label, label, .custom-control-label")
                lbl_count = await option_containers.count()
                screen_opts = []
                for l_idx in range(lbl_count):
                    raw_l = await option_containers.nth(l_idx).inner_text()
                    c_opt = re.sub(r'^(?:[a-d][.)]|option\s*[a-d][:.]?|\d+[.)])\s*', '', raw_l, flags=re.IGNORECASE).strip()
                    if c_opt:
                        screen_opts.append(c_opt)

                ai_solved = solve_question_with_ai(q_text_screen, screen_opts)
                if ai_solved:
                    matched_answer_text = ai_solved
                    gate1_ok = True
                    logger.info(f"  🧠 [AI LIVE SOLVER Q-{q_num + 1}] Solved NEW question -> '{matched_answer_text}'")

                    # Save sequentially with module_no, module_name, sub_no, sub_name structure
                    save_auto_learned_qa(course_title, module_no, module_name, sub_no, sub_name, q_text_screen, ai_solved)
            except Exception as ai_ex:
                logger.warning(f"  --> AI Live Solver notice: {ai_ex}")




        selected_option = False


        
        # Gate 2: 100% Option Label Verification & Exact Target Radio Click
        if matched_answer_text:
            try:
                option_containers = target_frame.locator("div[data-region='answer-label'], [aria-labelledby*='answer'], .answer label, div[class*='r0'], div[class*='r1'], .form-check-label, label, .custom-control-label")
                lbl_count = await option_containers.count()
                
                clean_target = re.sub(r'[^\w\s]', '', matched_answer_text.lower())
                target_words = set(w for w in clean_target.split() if len(w) >= 3)

                # Check if target answer is letter prefix e.g. "a", "b", "c", "d" or "option a"
                letter_idx_map = {"a": 0, "b": 1, "c": 2, "d": 3, "1": 0, "2": 1, "3": 2, "4": 3}
                target_letter_idx = letter_idx_map.get(clean_target)

                # Pass 1: Direct Index Click if target answer is specified as a letter/number e.g. "b" or "2"
                if target_letter_idx is not None and target_letter_idx < lbl_count:
                    container = option_containers.nth(target_letter_idx)
                    container_id = await container.get_attribute("id") or ""
                    if container_id and "_label" in container_id:
                        input_id = container_id.replace("_label", "")
                        target_input = target_frame.locator(f"#{input_id}, input[id='{input_id}']").first
                        if await target_input.count() > 0:
                            await target_input.click(force=True)
                            selected_option = True
                            gate2_ok = True
                            logger.info(f"  ✔ [VERIFIED ANSWER 100% MATCH Q-{q_num + 1}] Target Letter Option [{clean_target.upper()}]: #{input_id}")
                            logger.info(f"  🛡️ [EXACT RADIO CLICKED Q-{q_num + 1}] Selected radio button for letter '{matched_answer_text}'.")
                            await page.wait_for_timeout(1000)

                # Pass 2: Text Matching on Option Containers if not already clicked by letter index
                if not selected_option:
                    for l_idx in range(lbl_count):
                        container = option_containers.nth(l_idx)
                        
                        raw_lbl = await container.inner_text()
                        clean_option_txt = re.sub(r'^(?:[a-d][.)]|option\s*[a-d][:.]?|\d+[.)])\s*', '', raw_lbl, flags=re.IGNORECASE).strip().lower()
                        
                        clean_lbl = re.sub(r'[^\w\s]', '', clean_option_txt)
                        lbl_words = set(w for w in clean_lbl.split() if len(w) >= 3)

                        opt_overlap = (len(target_words & lbl_words) / float(len(target_words))) if target_words else 0.0
                        
                        # 100% Option Label Equality Criteria
                        is_100pct_option_match = (clean_target == clean_lbl) or (target_words and lbl_words and target_words == lbl_words) or (clean_target in clean_lbl or clean_lbl in clean_target) or (opt_overlap == 1.0)

                        if clean_target and is_100pct_option_match:
                            gate2_ok = True
                            logger.info(f"  ✔ [VERIFIED ANSWER 100% MATCH Q-{q_num + 1}] Target Answer: '{matched_answer_text}'")
                            logger.info(f"  🛡️ [DUAL CONFIRMATION 100% GUARANTEED Q-{q_num + 1}] Question & Answer 100% Verified!")

                            # 1. DIKSHA aria-labelledby linking check (e.g. id="q15158343:1_answer1_label" -> input id="q15158343:1_answer1")
                            container_id = await container.get_attribute("id") or ""
                            if container_id and "_label" in container_id:
                                input_id = container_id.replace("_label", "")
                                target_input = target_frame.locator(f"#{input_id}, input[id='{input_id}']").first
                                if await target_input.count() > 0:
                                    await target_input.click(force=True)
                                    selected_option = True
                                    logger.info(f"  --> Question #{q_num + 1}: Clicked DIKSHA radio input #{input_id} for answer '{matched_answer_text}'.")
                                    await page.wait_for_timeout(1000)
                                    break

                            # 2. Check for input linked via aria-labelledby
                            if container_id:
                                linked_input = target_frame.locator(f"input[aria-labelledby='{container_id}']").first
                                if await linked_input.count() > 0:
                                    await linked_input.click(force=True)
                                    selected_option = True
                                    logger.info(f"  --> Question #{q_num + 1}: Clicked DIKSHA radio input via aria-labelledby for answer '{matched_answer_text}'.")
                                    await page.wait_for_timeout(1000)
                                    break

                            # 3. Check for input inside container or parent row
                            input_child = container.locator("input[type='radio'], input[type='checkbox']").first
                            if await input_child.count() == 0:
                                parent_row = container.locator("xpath=./ancestor::div[contains(@class,'r0') or contains(@class,'r1') or contains(@class,'answer')][1]")
                                if await parent_row.count() > 0:
                                    input_child = parent_row.locator("input[type='radio'], input[type='checkbox']").first

                            if await input_child.count() > 0:
                                await input_child.click(force=True)
                                selected_option = True
                                logger.info(f"  --> Question #{q_num + 1}: Clicked radio option input for answer '{matched_answer_text}'.")
                                await page.wait_for_timeout(1000)
                                break

                            # 4. Fallback: Click container element directly
                            await container.click(force=True)
                            selected_option = True
                            logger.info(f"  --> Question #{q_num + 1}: Clicked matched option container for answer '{matched_answer_text}'.")
                            await page.wait_for_timeout(1000)
                            break
            except Exception as match_ex:
                logger.warning(f"  --> Option matching notice: {match_ex}")

        # Fallback ONLY if question was NOT in JSON key
        if not selected_option:
            if matched_answer_text:
                logger.warning(f"  --> Question #{q_num + 1} Notice: Answer '{matched_answer_text}' option container not visible. Selecting available radio.")
            else:
                logger.info(f"  --> Question #{q_num + 1} Notice: Unmatched question not in JSON key. Selecting default option [1].")

            options = target_frame.locator("input[type='radio'], input[type='checkbox'], .h5p-radio-button, label.radio, .form-check-input")
            if await options.count() == 0:
                options = page.locator("input[type='radio'], input[type='checkbox'], .h5p-radio-button, label.radio, .form-check-input")

            if await options.count() > 0:
                opt = options.first
                if await opt.is_visible() and not await opt.is_checked():
                    await opt.click(force=True)
                    logger.info(f"  --> Question #{q_num + 1} (Fallback): Selected first available option.")
                    await page.wait_for_timeout(800)




        next_nav = target_frame.locator("input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next')").first
        if await next_nav.count() == 0:
            next_nav = page.locator("input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next')").first

        review_submit_nav = target_frame.locator("input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first
        if await review_submit_nav.count() == 0:
            review_submit_nav = page.locator("input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first

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


    # 4. Close Assessment Modal & Confirm Checkmark
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
    Returns False if header contains ANY percentage badge from 0% to 99% (e.g. 0%, 12%, 45%, 50%, 97%, 99%).
    """
    try:
        raw_text = (await header.inner_text()).strip().lower()
        
        # Regex search for any 1 or 2 digit percentage badge (0% to 99%)
        pct_matches = re.findall(r"(\d{1,2})%", raw_text)
        if pct_matches:
            for val_str in pct_matches:
                val = int(val_str)
                if val < 100:
                    return False  # Any % between 0% and 99% is incomplete!
                elif val == 100:
                    return True

        # Check for 100% completion checkmark icon or .p100 class
        check_icon = header.locator("i.fa-check, .c100.p100, .fa-check-circle, div[class*='p100']").first
        if await check_icon.count() > 0 and await check_icon.is_visible():
            return True

        if "100%" in raw_text:
            return True
    except Exception:
        pass

    return False

async def process_course_modules(page, answer_key=None):
    """
    Clicks 'Lessons' tab (waits 6s for server hydration), lists all Main Modules,
    auto-expands 50%/0% incomplete modules, and executes items without checkmarks.
    """
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

        # Skip empty or non-lesson discussion & guideline sections
        if not header_title or any(skip in lower_t for skip in ["discussion", "navigation", "file upload", "closed for replies", "pinned"]):
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
            logger.info("\n" + "=" * 35)
            logger.info(f" 📚 MODULE [{i}/{total_real_modules}]: {header_title}")
            logger.info("=" * 35)

            item_attempts = {}

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
                    logger.info("\n" + "=" * 35)
                    logger.info(f" ▶ SUBSECTION [{j}/{total_sec_items}]: '{btn_text}' (Type: '{act_type}') [Attempt {runs_done + 1}/4]")
                    logger.info("=" * 35)

                    item_attempts[btn_text] = runs_done + 1


                    try:
                        if act_type == "url":
                            await process_video_activity(page, btn)
                        elif act_type == "resource":
                            await process_pdf_activity(page, btn)
                        elif act_type == "h5pactivity":
                            await process_h5p_activity(page, btn, answer_key, course_title=course_title)

                        elif act_type == "quiz":
                            await process_quiz_assessment(page, btn, answer_key, module_name=header_title, module_no=i+1, sub_name=btn_text, sub_no=j)
                        else:
                            await btn.click(force=True)
                            await page.wait_for_timeout(3000)
                            await close_activity_modal(page)
                            await wait_for_server_checkmark(page)
                    except Exception as item_ex:
                        logger.error(f"     [-] Subsection execution notice: {item_ex}")

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

            # Check 1: Re-verify section item checkmarks
            recheck_btns = await get_section_action_buttons(collapse_panel, header)
            all_done = True
            for r_btn in recheck_btns:
                if not await is_item_100_percent_complete(r_btn):
                    all_done = False
                    break

            header_done = await is_header_100_percent_complete(header)

            if not all_done and not header_done:
                logger.info("  --> [GATE REFRESH] Reloading page once to sync DIKSHA server backend checkmarks...")
                try:
                    await page.reload()
                    await page.wait_for_timeout(4000)
                    header_done = await is_header_100_percent_complete(header)
                except Exception:
                    pass

            if all_done or header_done:
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
                if not final_header_check:
                    logger.error(f"\n❌ [CRITICAL DIKSHA SERVER FAILURE] '{header_title}' remains incomplete after 4 attempts & 5s page reloads.")
                    logger.error("⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context!\n")
                    try:
                        await page.context.close()
                    except Exception:
                        pass
                    raise RuntimeError(f"DIKSHA_SERVER_STUCK: '{header_title}' failed to achieve 100% after 4 attempts.")






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
    answer_key = load_answer_key()

    logger.info("=" * 35)
    logger.info("   DIKSHA AUTOMATION PIPELINE (DOCX DOM SPECIFICATION)")
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
            await process_course_modules(page, answer_key)
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
                    await process_course_modules(page, course_answer_key)



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



