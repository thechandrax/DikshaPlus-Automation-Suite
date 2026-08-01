# ⚙️ AUTOMATION CONTROLS, SELECTORS & CONFIGURATION

This document details all system configuration parameters, timing controls, DOM selector dictionaries, Headless auto-detection, and encrypted security vaults in `config.py`.

---

## 🛠️ 1. Master Configuration File (`config.py`)

### System Paths & Directories
* `BASE_DIR`: Project root directory.
* `DATA_DIR`: Base data directory (`data/`).
* `COURSES_DIR`: Auto-learned per-course JSON answer keys (`data/courses/`).
* `USERS_FILE`: Encrypted user credentials vault (`data/users.json`).
* `OUTPUT_DIR`: Directory for run screenshots and logs (`output/screenshots/`).

---

## 🤖 2. Smart Headless Auto-Detection

`config.py` automatically detects whether the automation is running on a local desktop computer or inside a cloud Docker container (such as Railway Cloud):

```python
# Browser Engine Launch Options
BROWSER_TYPE = "chromium"
IS_DOCKER = os.path.exists("/.dockerenv") or bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))
HEADLESS_ENV = os.environ.get("HEADLESS", "").strip().lower()

if HEADLESS_ENV in ("true", "1", "yes", "t"):
    HEADLESS = True
elif HEADLESS_ENV in ("false", "0", "no", "f"):
    HEADLESS = False
elif IS_DOCKER:
    HEADLESS = True    # Automatically use Headless mode on Railway Cloud / Docker!
else:
    HEADLESS = False   # Default to False for local GUI desktop run
```

---

## 🔑 3. Gemini API Multi-Key Pool

Stored as 256-bit AES encrypted ciphers in `config.py`:

```python
GEMINI_API_KEYS_ENCRYPTED = [
    "ENC256:...",  # Key #1
    "ENC256:...",  # Key #2
    "ENC256:...",  # Key #3
]
```

* Dynamically decrypted in memory via `utils/security.py`.
* Automatic failover on HTTP 429 rate limit quota errors.

---

## 🎯 4. Centralized DOM Selectors (`SELECTORS`)

Extracted directly from DIKSHA & Moodle HTML inspect element sources:

```python
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
    # Course Cards
    "course_card": ".course-card, .card, [data-course-id]",
    "course_title": ".course-title, .card-title, h5, h6",
    "course_progress": ".progress-bar, .progress-percentage, [data-progress]",
    "start_course_btn": "a:has-text('Start Learning'), a:has-text('Continue Learning'), a:has-text('Join Course'), .btn-start-course",
    # Feedback Form Selectors
    "feedback_q_num": ".que-no, .qtext, div.qtext, .question-text",
    "feedback_ans_row": "div.feed-ans-div, div.form-check",
    "feedback_radio": "input.form-check-input[type='radio'], input[type='radio']",
    "feedback_comment": "textarea.form-control, textarea, input[type='text']:not([class*='search'])",
    "feedback_submit_btn": "button.submit-feed-btn, #submitFeedbackBtn11, button:has-text('Submit Feedback'), input[value*='Submit Feedback']"
}
```
