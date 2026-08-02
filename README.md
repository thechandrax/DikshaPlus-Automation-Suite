# ⚡ DIKSHA+ AUTOMATION SUITE

An enterprise-grade, end-to-end automation engine for **DIKSHA / Moodle LMS Portals**. Features real-time **Gemini AI Multi-Key Live Solving**, **Stepped Backoff Retries (30s -> 45s -> 60s)**, **Total Server Stop Circuit Breaker**, **Feedback Form Auto-Filling Engine**, **Automatic Video Auto-Play & Stall Recovery Safeguard**, **HTML5 Video Element Screen Pause/Play Control**, **Clean Module -> Subsection JSON Architecture**, **Unicode Text Normalization**, **Hot-Key Live Pause/Resume**, **Question 1 Navigation Reset Protocol**, and complete **H5P, Formative Assessment & Feedback Form** automation.

---

## 🌟 Key Features

* **🧠 Gemini AI Multi-Key Pool Solver Engine**: When a quiz or feedback question is not found in your local answer key, the bot passes the question text + option choices to Gemini AI (`gemini-flash-latest` / `gemini-2.0-flash`), which solves the question live! With active 256-bit encrypted API keys in `config.py`, if Key #1 encounters rate limits (HTTP 429), the engine **instantly rotates to Key #2** without stopping!
* **⏳ Stepped Backoff Retry Protocol (30s -> 45s -> 60s)**: If initial AI solver attempts run out due to API quota limits:
  * **Retry #1**: Waits **30 seconds** for Gemini API quota reset $\rightarrow$ Retries AI solver across all keys/models!
  * **Retry #2**: If still rate-limited, waits **45 seconds** $\rightarrow$ Retries AI solver across all keys/models!
  * **Retry #3**: If still rate-limited, waits **60 seconds** $\rightarrow$ Retries AI solver across all keys/models!
* **⛔ Total Server Stop Circuit Breaker (0% Default Fallback)**:
  * Default Option [A] selection fallback is **completely removed**!
  * If after the 30s, 45s, and 60s backoff retries a question cannot be solved, DIKSHA+ cleanly closes browser context (`page.context.close()`) and stops all server automation processes safely.
* **📂 Clean Module -> Subsection JSON Architecture**: Course answer keys use the standard, clean hierarchy:
  * `modules` array $\rightarrow$ `subsections` array $\rightarrow$ `questions` array (`question`, `options`, `answer`).
* **🛡️ Automatic Video Auto-Play & Network Stall Recovery Safeguard**: Continuously monitors the HTML5 video element every 1.5 seconds. If browser or server network lag causes the video stream to pause unexpectedly, DIKSHA+ automatically detects the stall and triggers `video.play()` to keep playback active!
* **⏸️ Built-in Hotkey Live Pause & Resume (Press `P` or `Spacebar`)**: Real-time terminal keyboard listener (`msvcrt`) lets you toggle **PAUSE / RESUME** instantly at any point! Automatically executes `video.pause()` on the HTML5 video element on screen to freeze video playback instantly, and `video.play()` upon resuming.
* **📝 Dedicated DIKSHA Feedback Form Popup Engine**: Automatically opens and completes course Feedback Forms (Module #8):
  * **Native JS Event Dispatcher**: Triggers DIKSHA's custom AJAX modal handler (`<a act_type="feedback" data-id="...">View</a>`) via native MouseEvents.
  * **Visible Modal Container Scoping**: Waits up to 10s for the Feedback popup modal (`.modal-dialog`, `.modal-content`) to become open and visible on screen.
  * **Dual-Pass JSON & AI Solver**: Matches feedback rating questions and open-text textarea questions against Course JSON answer keys or Gemini AI Live Solver!
  * **Textarea Open-Text Response Handling**: Extracts open-ended textarea questions (e.g. `"What aspects of the training could be improved?"`), strips leading numbers, and fills full paragraph answers into `<textarea class="form-control">`!
  * **Modal Submission**: Clicks the big brown `Submit Feedback` button (`button:has-text('Submit Feedback')`, `#submitFeedbackBtn11`).

* **🔀 Shuffled Option Resiliency**: Matches options on screen by **text content**, NOT hardcoded letters/positions! If Answer B moves to Option C on screen, DIKSHA+ matches the exact text and clicks Option C's radio button.
* **🤖 Smart Headless Auto-Detection**: Local computer runs default to visible desktop GUI (`HEADLESS = False`). Railway Cloud / Docker deployments automatically detect the container environment and switch to `HEADLESS = True` with zero configuration required!
* **🌐 2025/2026 Official Google API Auth Standard**: Fully compliant with [Google's official API Key specification](https://ai.google.dev/gemini-api/docs/api-key), sending mandatory `x-goog-api-key` headers and supporting encrypted key pools directly in `config.py`.
* **⏳ 3-Second Pacing Delay**: Features a smooth 3-second pacing delay before AI API calls to mimic human reading and prevent rate-limit quota exhaustion.
* **🎯 Question 1 Navigation Reset Protocol**: When starting or continuing an assessment ("Continue Assessment"), DIKSHA+ automatically detects Question 1 in the right-side Quiz Navigation panel (`#quiznavbutton1`), clicks it, and starts solving sequentially from Question 1!
* **🔤 Unicode Apostrophe & Text Normalization**: Automatically standardizes curly apostrophes (`’`, `\u2019`), curly quotes (`“`, `”`), dashes (`–`, `—`), and non-breaking spaces (`\u00a0`) to standard ASCII straight keyboard characters (`'`) in DOM parsing, JSON matching, and JSON auto-learning storage.
* **🎯 100% Exact Dual-Pass Radio Selection**:
  * **Gate 1**: 100% Question Text Match logged as `⚡ [VERIFIED JSON 100% MATCH QUESTION-03]`.
  * **Gate 2**: Exact 4-tier Moodle DOM Radio Input Locator (`.answer > div.r0`, `.answer > div.r1`, `div.feed-ans-div`, `preceding-sibling::input[@type='radio']`, `aria-labelledby`) ensuring 100% accurate radio button clicks.
* **💾 Smart Auto-Learning JSON Storage**: AI-solved answers are automatically saved to `data/courses/<course_name>.json` under clean module and subsection hierarchies (`module_no`, `module_name`, `subsection_no`, `subsection_name`, `questions`, `options`, `answer`).
  * **Quizzes**: Options formatted as `["[A] ...", "[B] ...", "[C] ...", "[D] ..."]` and answer as `"[B] ..."`.
  * **Feedback Forms**: Standard options `["Strongly Agree", "Agree", ...]` without letter tags.
* **📊 Professional Standardized Log Formatting**: Clean, standardized log tags:
  * `❓ [QUESTION-03]: <Full Question Text>`
  * `📋 [OPTIONS]: [A] ... [B] ... [C] ... [D] ...`
  * `🧠 [AI LIVE SUCCESS] Solved on Attempt 1/3 via Key #1 -> '...'`
  * `✍️ [TYPED FEEDBACK RESPONSE QUESTION-19]: '...'`
  * `🛡️ [AUTOPLAY SAFEGUARD] Video was paused. Auto-triggered video.play() to keep playback active.`
  * `💾 [AUTO-LEARNING SAVE] Saved to <course.json>: Module #8 ('Feedback Form') || Subsection #1 ('Feedback Form') -> Q: '...'`
* **⚡ Complete Activity Support**:
  * **Videos (`url`)**: Multi-speed playback acceleration (16x/4x/1x) with Auto-Play Safeguard & HTML5 screen pause.
  * **PDFs (`resource`)**: Automated page-down flipping and end-of-doc container scrolling.
  * **H5P Quizzes (`h5pactivity`)**: Full interactive quiz auto-solving with AI solver.
  * **Formative Assessments (`quiz`)**: Complete Moodle quiz automation with banner dismissal, Question 1 reset & final submission.
  * **Feedback Forms (`feedback`)**: Full rating selection, comment box typing & feedback submission.
* **🔒 256-Bit Cryptographic Security**: 
  * SHA-256 encrypted multi-user PIN lock (`541563`) and credential vault.
  * Gemini API Keys stored as 256-bit encrypted ciphers in `config.py` with dynamic in-memory decryption via `utils/security.py`. No plain text `.env` files required.
* **☁️ Railway Cloud Ready**: Fully containerized with root `Dockerfile`, `railway/` config, and 0-variable setup required.

---

## 📁 Repository Structure

```text
Diksha+ Automation Suite/
├── automations/
│   └── diksha_plus_engine.py      # Core Playwright automation, AI Solver, Stepped Backoffs & Circuit Breaker
├── config.py                      # System configuration, DOM SELECTORS, Headless Auto-Detection & Key Pool
├── data/
│   └── courses/                   # Auto-learning per-course JSON answer keys (Module -> Subsection hierarchy)
├── docs/                          # Detailed technical documentation
│   ├── README.md                  # Master documentation index
│   ├── 01_USER_GUIDE.md           # Operational guide, Keyboard Hotkeys & Auto-Play Safeguard
│   ├── 02_MANAGE_USERS_AND_SECURITY.md # Security & 256-bit PIN vault
│   ├── 03_ANSWER_KEYS_AND_QUIZZES.md  # AI Live Solver, Stepped Backoffs & Feedback Engine
│   ├── 04_AUTOMATION_CONTROLS_AND_CONFIG.md # Config, DOM Selectors & Headless Auto-Detection
│   └── 05_RAILWAY_DEPLOYMENT_GUIDE.md # Railway Cloud 1-Click Deployment Guide
├── output/
│   └── screenshots/               # Single official screenshot directory
├── utils/
│   ├── logger.py                  # Colorized engine logger
│   └── security.py                # 256-Bit cryptographic security engine
├── Dockerfile                     # Root Dockerfile for 1-click Railway Cloud build
├── railway.json                   # Railway Cloud deployment configuration
├── .dockerignore                  # Docker build ignore rules
├── main.py                        # CLI Menu launcher with 256-bit PIN lock
├── diksha+.bat                    # 1-Click Windows execution script
└── setup.bat                      # 1-Click environment installer

```

---

## 🚀 Quick Start (Local Run)

```bash
# 1. Clone repository
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
cd "Diksha+ Automation Suite"

# 2. Run Setup
setup.bat

# 3. Launch DIKSHA+
diksha+.bat
```

Default Security PIN: **`541563`**
