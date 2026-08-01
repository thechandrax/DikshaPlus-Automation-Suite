# ⚙️ AUTOMATION CONTROLS, SELECTORS & CONFIGURATION

This document details all system configuration parameters, timing controls, DOM selector dictionaries, and encrypted security vaults in `config.py`.

---

## 🛠️ 1. Master Configuration File (`config.py`)

### System Paths & Directories
* `BASE_DIR`: Project root directory.
* `DATA_DIR`: Base data directory (`data/`).
* `COURSES_DIR`: Auto-learned per-course JSON answer keys (`data/courses/`).
* `USERS_FILE`: Encrypted user credentials vault (`data/users.json`).
* `OUTPUT_DIR`: Directory for run screenshots and logs (`output/screenshots/`).

---

## 🔑 2. Gemini API Multi-Key Pool (5 Encrypted Keys)

Stored as 256-bit AES encrypted ciphers in `config.py`:

```python
GEMINI_API_KEYS_ENCRYPTED = [
    "ENC256:...",  # Key #1 (gemini-flash-latest)
    "ENC256:...",  # Key #2 (gemini-2.0-flash)
    "ENC256:...",  # Key #3 (gemini-1.5-flash)
    "ENC256:...",  # Key #4 (gemini-flash-latest)
    "ENC256:...",  # Key #5 (gemini-2.0-flash)
]
```

* Dynamically decrypted in memory via `utils/security.py`.
* Automatic failover on HTTP 429 rate limit quota errors.

---

## 🎯 3. Centralized DOM Selectors (`SELECTORS`)

Extracted directly from DIKSHA & Moodle HTML inspect element sources:

```python
SELECTORS = {
    # Login Page
    "login_link": "a[href*='lms=diksha2']",
    "username_input": "#username",
    "password_input": "#password",
    "login_button": "#login",
    # Navigation & Tabs
    "my_learning_nav": (
        "a[href*='course_listing.php'], a:has-text('My Learning'),"
        " span:has-text('My Learning'), [data-original-title='My Learning']"
    ),
    "ongoing_courses_tab": (
        "#pills-inprogress-tab, a:has-text('Ongoing Courses'),"
        " [data-completed='false']"
    ),
    "finished_courses_tab": (
        "#pills-completed-tab, a:has-text('Finished Courses'),"
        " [data-completed='true']"
    ),
    "lessons_tab": (
        "#pills-lessons-tab, button:has-text('Lessons'), a:has-text('Lessons'),"
        " .nav-link:has-text('Lessons')"
    ),
    "course_card_link": ".course-library-link, .library-card, .course-detail",
    # Module Activities
    "activity_item": "a.activity-list",
    "module_view_btn": ".module-view-btn.activity-list",
    "modal_close_btn": "button.close[data-dismiss='modal']",
    "progress_check_icon": ".module-progress-pie i.fa-check",
    # H5P Activity Selectors
    "h5p_start_button": (
        "button.qs-startbutton, button.h5p-button:has-text('Start Quiz')"
    ),
    "h5p_next_button": ".h5p-question-next, a[aria-label='Next question']",
    "h5p_check_button": "button.h5p-question-check-answer",
    "h5p_finish_button": "button.h5p-question-finish",
    # Formative Assessment / Quiz Selectors
    "quiz_banner_close": "button.quiz-popup-close",
    "start_assessment_btn": (
        "button#single_button6a6cc3ce57dbc3,"
        " .singlebutton.quizstartbuttondiv button[type='submit']"
    ),
    "quiz_next_nav": "#mod_quiz-next-nav, input[value='Next Question']",
    "quiz_review_submit_nav": "input[value='Review & Submit']",
    "quiz_final_submit_btn": (
        "button.btn-primary:has-text('Submit'), input[type='submit'][value*='Submit']"
    ),
    # Feedback Form Selectors
    "feedback_question_container": ".que-no, .que, div[class*='que']",
    "feedback_radio_row": "div.feed-ans-div, div.feed-ans-div > div.form-check",
    "feedback_radio_input": (
        "input.form-check-input[type='radio'], input[type='radio']"
    ),
    "feedback_radio_label": "label.form-check-label, label[for]",
    "feedback_textarea_input": "textarea.form-control, textarea",
    "feedback_submit_btn": (
        "button.submit-feed-btn, #submitFeedbackBtn11,"
        " button:has-text('Submit Feedback')"
    ),
}
```

---

## ⏱️ 4. Timing & Delays Reference

| Activity / Action | Delay | Purpose |
| :--- | :--- | :--- |
| **Video Acceleration** | Playback 16x | Completes video telemetry in seconds |
| **PDF Page Flipping** | 800ms per page | Triggers scroll & end-of-doc events |
| **Quiz Question Pacing** | 1.5s per question | Mimics human reading speed |
| **AI Solver Pacing** | 3.0s delay | Protects Gemini API rate limits |
| **Radio Click Delay** | 1.0s wait | Allows DOM selection state to settle |
| **Modal Rendering** | 5.0s wait | Ensures iframe & DOM elements load |
