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
    "gexowo4534@candaba.com": "Gsgs Sdgr",
    "borkej@smanthaai.online": "Bgdh Hdfh",
    "8617383566": "Sujata Mondal",
    "7044015007": "Sumanta Halder",
    "7908555852": "Tasapur Rahaman",
}


USER_CREDENTIALS_ENCRYPTED = {
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "7908555852": "ENC256:S0R5KItAxBw=",
}

# Decrypt credentials dynamically in memory
USER_CREDENTIALS = {u: decrypt_password(p) for u, p in USER_CREDENTIALS_ENCRYPTED.items()}


# Per-Course Answer Keys Directory Path
COURSES_DIR = DATA_DIR / "courses"
COURSES_DIR.mkdir(parents=True, exist_ok=True)

# Browser Engine Launch Options
BROWSER_TYPE = "chromium"
HEADLESS = False           # Set to False to watch browser in action
SLOMO_MS = 500

# Automation Behavior Controls
MIN_VIDEO_WATCH_SECONDS = 30
MIN_PDF_READ_SECONDS = 10
SERVER_SYNC_TIMEOUT_SECONDS = 20
POST_LOGIN_WAIT_SECONDS = 10     # Time to wait for dashboard redirect after login button click
AUTOMATIC_FINAL_SUBMIT = True    # Set to True to automatically click final quiz submit

KEEP_BROWSER_OPEN = True         # Set to True to keep browser open after completion so it doesn't close!

# Gemini AI Live Solver Configuration (Set GEMINI_API_KEY environment variable)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
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
    "quiz_final_submit_btn": "button.btn-primary:has-text('Submit'), input[type='submit'][value*='Submit']"
}
