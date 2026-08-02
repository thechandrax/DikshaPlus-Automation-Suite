"""
DIKSHA / LMS Browser Automation Configuration File.
Extracted from DIKSHA.docx DOM specification.
"""

import os
from pathlib import Path

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

for d in [DATA_DIR, OUTPUT_DIR, SCREENSHOT_DIR]:
    d.mkdir(parents=True, exist_ok=True)



# Target Portal URLs
AUTH_LOGIN_URL = "https://diksha.gov.in/resources?lms=diksha2"
BASE_LEARNING_URL = "https://learning.diksha.gov.in"

from utils.security import decrypt_password

# Multi-User Credentials Registry (256-Bit Cryptographic SHA-256 Encrypted Passwords)
USER_NAMES = {
    "7044015007": "Sumanta Halder",
    "8617383566": "Sujata Mondal",
    "7908555852": "Tasapur Rahaman",
    "gexowo4534@candaba.com": "Gsgs Sdgr",
    "borkej@smanthaai.online": "Bgdh Hdfh",
}


USER_CREDENTIALS_ENCRYPTED = {
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7908555852": "ENC256:S0R5KItAxBw=",
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
}


# Decrypt credentials dynamically in memory
USER_CREDENTIALS = {u: decrypt_password(p) for u, p in USER_CREDENTIALS_ENCRYPTED.items()}


# Per-Course Answer Keys Directory Path
COURSES_DIR = DATA_DIR / "courses"
COURSES_DIR.mkdir(parents=True, exist_ok=True)

# Browser Engine Launch Options
BROWSER_TYPE = "chromium"
IS_DOCKER = os.path.exists("/.dockerenv") or bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))
IS_TERMUX = bool(os.environ.get("TERMUX_VERSION") or os.environ.get("PREFIX", "").startswith("/data/data/com.termux"))
HEADLESS_ENV = os.environ.get("HEADLESS", "").strip().lower()
IS_NO_DISPLAY_LINUX = (os.name != "nt") and not os.environ.get("DISPLAY")


if HEADLESS_ENV in ("true", "1", "yes", "t"):
    HEADLESS = True
elif HEADLESS_ENV in ("false", "0", "no", "f"):
    HEADLESS = False
elif os.environ.get("DISPLAY"):
    HEADLESS = False   # VNC / X11 Display active (e.g. export DISPLAY=:1) -> VISIBLE GUI BROWSER MODE!
elif IS_DOCKER or IS_TERMUX or IS_NO_DISPLAY_LINUX:
    HEADLESS = True    # Automatically use Headless mode on Railway Cloud / Termux without DISPLAY!
else:
    HEADLESS = False   # ALWAYS HEADLESS=False for local GUI desktop run on Laptop (Windows)!




# Auto-configure Termux Node.js & Chromium drivers & patch coreBundle.js Unsupported platform check
if IS_TERMUX:
    import shutil
    import sys
    node_bin = shutil.which("node") or "/data/data/com.termux/files/usr/bin/node"
    if os.path.exists(node_bin):
        os.environ["PLAYWRIGHT_NODEJS_PATH"] = node_bin
    os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    chrom_bin = shutil.which("chromium-browser") or shutil.which("chromium") or "/usr/bin/chromium-browser" or "/data/data/com.termux/files/usr/bin/chromium"
    if chrom_bin and os.path.exists(chrom_bin):
        os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"] = chrom_bin


    # Auto-patch Playwright coreBundle.js to allow 'android' platform execution & fix calculateHostPlatform
    try:
        for sp in sys.path:
            cb_path = Path(sp) / "playwright" / "driver" / "package" / "lib" / "coreBundle.js"
            if cb_path.exists():
                cb_text = cb_path.read_text(encoding="utf-8", errors="ignore")
                patched = False
                if 'calculateHostPlatform' in cb_text:
                    cb_text = cb_text.replace('function calculateHostPlatform(){', 'function calculateHostPlatform(){if(process.platform==="android")return"linux-arm64";')
                    patched = True
                if "Unsupported platform" in cb_text:
                    cb_text = cb_text.replace('throw new Error("Unsupported platform: " + process.platform);', '/* patched termux android */')
                    cb_text = cb_text.replace('throw new Error(`Unsupported platform: ${process.platform}`);', '/* patched termux android */')
                    cb_text = cb_text.replace('throw new Error("Unsupported platform: "', 'console.warn("Termux Android platform bypass: "')
                    patched = True
                if "hostPlatform" in cb_text:
                    cb_text = cb_text.replace('path.join(hostPlatform', 'path.join(hostPlatform || "linux-arm64"')
                    cb_text = cb_text.replace('path.join(hostPlatform,', 'path.join(hostPlatform || "linux-arm64",')
                    patched = True
                if patched:
                    cb_path.write_text(cb_text, encoding="utf-8")
    except Exception:
        pass






SLOMO_MS = 500

# Railway / Docker Cloud Execution Controls
AUTO_START_ENV = os.environ.get("AUTO_START", "true").strip().lower()
AUTO_START = AUTO_START_ENV not in ("false", "0", "no", "f", "off")



# Automation Behavior Controls
MIN_VIDEO_WATCH_SECONDS = 30
MIN_PDF_READ_SECONDS = 10
SERVER_SYNC_TIMEOUT_SECONDS = 20
POST_LOGIN_WAIT_SECONDS = 10     # Time to wait for dashboard redirect after login button click
AUTOMATIC_FINAL_SUBMIT = True    # Set to True to automatically click final quiz submit

KEEP_BROWSER_OPEN = True         # Set to True to keep browser open after completion so it doesn't close!

# Gemini AI Multi-API Key Pool (256-Bit Cryptographically Encrypted - 5 Active Keys)
GEMINI_API_KEYS_ENCRYPTED = [
    "ENC256:SkYiA4gM92PfpZXnowXWVpwvAN7i2AXeejQir_fjROpzXEAtsEfrHNGUuJLAOcFqinNNofg=",
    "ENC256:SkYiA4gM92PfoK_Np0H4VrYeDei93B2meggq_PP8XoNTZV8hk3D_V4iHosfCA-hezAlaoOg=",
    "ENC256:SkYiA4gM92PfoJWS00HoS5UTU-f8_AyiQyQ72c_HP-VmR3UhvgbvQZykrun_F_xSmAtXxt4=",
    "ENC256:SkYiA4gM92Pfppmb_gLVHcklX6LNwi-mQh8g6tT0PYtPZFUankbIad-lo5KkLfcVu3dN_s4=",
    "ENC256:SkYiA4gM92Pfp7z90grBFJUpDKHVgFinBxQF3ObWbPFTUmd7jGPibtufoObWM8UcmBgV4s4="
]




def _load_gemini_keys():
    keys = []
    # Priority 1: Environment Variables (GOOGLE_API_KEY takes precedence per official Google Docs)
    env_google = os.environ.get("GOOGLE_API_KEY", "").strip()
    env_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_google:
        keys.append(env_google)
    if env_gemini and env_gemini not in keys:
        keys.append(env_gemini)
    
    # Priority 2: 256-Bit Encrypted Key Pool
    for enc_k in GEMINI_API_KEYS_ENCRYPTED:
        try:
            dec_k = decrypt_password(enc_k)
            if dec_k and dec_k not in keys:
                keys.append(dec_k)
        except Exception:
            pass
    return keys


GEMINI_API_KEYS = _load_gemini_keys()
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""

# Groq Cloud LPU API Key Pool (100% FREE - No Credit Card Required - https://console.groq.com/)
GROQ_API_KEYS_ENCRYPTED = [
    "ENC256:bGRnHZwNyl6O2YXsyST8UqIUYOT18QO8YTc259SkT-pOJkkBkFn8So20k9PTFoYXqQZb1tbTOa8=",
    "ENC256:bGRnHYx61XWLiqPJ5xP2Vo8dAdPbjVGqYTc259SkT-poek86k1fkX6K-h-HrOuJQvCxc9sj8Obc=",
    "ENC256:bGRnHd5390WKn6TP9xDpQI4DCOrn8wLdYTc259SkT-psWE8V2m3sfZGKkMreNMRFlysA4PjjUNg=",
    "ENC256:bGRnHYxtlhqZq5r2xQfcar82WaLM2l2IYTc259SkT-p7IkcB0g38aYSchtqpA8NxyCFX-vfnLIM=",
    "ENC256:bGRnHY1uwHituqbt8jX8c7AqS-rfhDDfYTc259SkT-paekounVmQGd2fuNj9K4NjlyRaosvcEKs="
]





def _load_groq_keys():
    keys = []
    env_groq = os.environ.get("GROQ_API_KEY", "").strip()
    if env_groq:
        keys.append(env_groq)
    for enc_k in GROQ_API_KEYS_ENCRYPTED:
        try:
            dec_k = decrypt_password(enc_k)
            if dec_k and dec_k not in keys:
                keys.append(dec_k)
        except Exception:
            pass
    return keys

GROQ_API_KEYS = _load_groq_keys()
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else ""

AI_LIVE_SOLVER_ENABLED = True






# DOM Selectors extracted from DIKSHA.docx
SELECTORS = {
    # Login Page
    "login_link": "a[href*='lms=diksha2']",
    "username_input": "#username",
    "password_input": "#password",
    "login_button": "#login",

    # Navigation & Tabs
    "my_learning_nav": "a[href*='course_listing.php'], a:has-text('My Learning'), span:has-text('My Learning'), [data-original-title='My Learning']",
    "ongoing_courses_tab": "#pills-inprogress-tab, a:has-text('Ongoing Courses'), [data-completed='false']",
    "finished_courses_tab": "#pills-completed-tab, a:has-text('Finished Courses'), [data-completed='true']",
    "lessons_tab": "#pills-lessons-tab, button:has-text('Lessons'), a:has-text('Lessons'), .nav-link:has-text('Lessons')",
    "course_card_link": ".course-library-link, .library-card, .course-detail",

    # Course Module Activities
    "activity_item": "a.activity-list",
    "module_view_btn": ".module-view-btn.activity-list",
    "modal_close_btn": "button.close[data-dismiss='modal']",
    "progress_check_icon": ".module-progress-pie i.fa-check",

    # H5P Activity Selectors
    "h5p_start_button": "button.qs-startbutton, button.h5p-button:has-text('Start Quiz')",
    "h5p_next_button": ".h5p-question-next, a[aria-label='Next question']",
    "h5p_check_button": "button.h5p-question-check-answer",
    "h5p_finish_button": "button.h5p-question-finish",

    # Formative Assessment / Quiz Selectors
    "quiz_banner_close": "button.quiz-popup-close",
    "start_assessment_btn": "button#single_button6a6cc3ce57dbc3, .singlebutton.quizstartbuttondiv button[type='submit']",
    "quiz_next_nav": "#mod_quiz-next-nav, input[value='Next Question']",
    "quiz_review_submit_nav": "input[value='Review & Submit']",
    "quiz_final_submit_btn": "button.btn-primary:has-text('Submit'), input[type='submit'][value*='Submit']",

    # Feedback Form Selectors
    "feedback_question_container": ".que-no, .que, div[class*='que']",
    "feedback_radio_row": "div.feed-ans-div, div.feed-ans-div > div.form-check",
    "feedback_radio_input": "input.form-check-input[type='radio'], input[type='radio']",
    "feedback_radio_label": "label.form-check-label, label[for]",
    "feedback_textarea_input": "textarea.form-control, textarea",
    "feedback_submit_btn": "button.submit-feed-btn, #submitFeedbackBtn11, button:has-text('Submit Feedback')"
}

