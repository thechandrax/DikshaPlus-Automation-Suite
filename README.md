# ⚡ DIKSHA+ AUTOMATION SUITE

An enterprise-grade, end-to-end automation engine for **DIKSHA / Moodle LMS Portals**. Features real-time **Gemini AI Multi-Key Live Solving**, **Auto-Learning Smart JSON Caching**, **Unicode Text Normalization**, **Hot-Key Live Pause/Resume**, **Question 1 Navigation Reset Protocol**, and complete **H5P & Formative Assessment** automation.

---

## 🌟 Key Features

* **🧠 Gemini AI Multi-Key Pool Solver Engine**: When a quiz question is not found in your local answer key, the bot passes the question text + option choices to Gemini AI (`gemini-flash-latest` / `gemini-2.0-flash`), which solves the question live! If Key #1 encounters rate limits (HTTP 429), the engine **instantly rotates to Key #2** without stopping!
* **🌐 2025/2026 Official Google API Auth Standard**: Fully compliant with [Google's official API Key specification](https://ai.google.dev/gemini-api/docs/api-key), sending mandatory `x-goog-api-key` headers and supporting encrypted key pools directly in `config.py`.
* **⏳ 3-Second Pacing Delay**: Features a smooth 3-second pacing delay before AI API calls to mimic human reading and prevent rate-limit quota exhaustion.
* **🔁 3-Attempt AI Retry Protocol**: Runs up to 3 full solver retry rounds across models and keys before defaulting to Option A.
* **⏸️ Built-in Hotkey Pause & Resume (Press `P` or `Spacebar`)**: Real-time terminal keyboard listener (`msvcrt`) lets you toggle **PAUSE / RESUME** instantly at any point during automation!
* **🎯 Question 1 Navigation Reset Protocol**: When starting or continuing an assessment ("Continue Assessment"), DIKSHA+ automatically detects Question 1 in the right-side Quiz Navigation panel (`#quiznavbutton1`), clicks it, and starts solving sequentially from Question 1!
* **🔤 Unicode Apostrophe & Text Normalization**: Automatically standardizes curly apostrophes (`’`, `\u2019`), curly quotes (`“`, `”`), dashes (`–`, `—`), and non-breaking spaces (`\u00a0`) to standard ASCII straight keyboard characters (`'`) in DOM parsing, JSON matching, and JSON auto-learning storage.
* **🎯 100% Exact Dual-Pass Radio Selection**:
  * **Gate 1**: 100% Question Text Match logged as `⚡ [VERIFIED JSON 100% MATCH QUESTION-03]`.
  * **Gate 2**: Exact 4-tier Moodle DOM Radio Input Locator (`.answer > div.r0`, `.answer > div.r1`, `preceding-sibling::input[@type='radio']`, `aria-labelledby`) ensuring 100% accurate radio button clicks.
* **💾 Smart Auto-Learning JSON Storage**: AI-solved answers are automatically saved to `data/courses/<course_name>.json` under full module and subsection hierarchies (`module_no`, `module_name`, `subsection_no`, `subsection_name`, `questions`). Future runs use the cached answer in **0.01 seconds**!
* **📊 Professional Standardized Log Formatting**: Clean, standardized log tags:
  * `❓ [QUESTION-03]: <Full Question Text>`
  * `📋 [OPTIONS]: [A] ... [B] ... [C] ... [D] ...`
  * `🧠 [AI LIVE SUCCESS] Solved on Attempt 1/3 via Key #1 -> '...'`
  * `💾 [AUTO-LEARNING SAVE] Saved to <course.json>: Module #7 ('Assessment') || Subsection #1 ('Assessment') -> Q: '...'`
* **⚡ Complete Activity Support**:
  * **Videos (`url`)**: Multi-speed playback acceleration (16x/4x/1x) with telemetry checkmark verification.
  * **PDFs (`resource`)**: Automated page-down flipping and end-of-doc container scrolling.
  * **H5P Quizzes (`h5pactivity`)**: Full interactive quiz auto-solving with AI solver.
  * **Formative Assessments (`quiz`)**: Complete Moodle quiz automation with banner dismissal & automatic final submission.
* **🔒 256-Bit Cryptographic Security**: 
  * SHA-256 encrypted multi-user PIN lock (`541563`) and credential vault.
  * API Keys stored as 256-bit encrypted ciphers (`GEMINI_API_KEYS_ENCRYPTED = ["ENC256:...", "ENC256:..."]`) in `config.py` with dynamic in-memory decryption via `utils/security.py`. No plain text `.env` files required.
* **☁️ Railway Cloud Ready**: Fully containerized in `railway/` with Dockerfile and Automated Cron deployment options.

---

## 📁 Repository Structure

```text
Diksha+ Automation Suite/
├── automations/
│   └── diksha_plus_engine.py      # Core Playwright automation, AI Live Solver & Hotkey listener
├── config.py                      # System configuration & 256-bit encrypted API key pool
├── data/
│   └── courses/                   # Auto-learning per-course JSON answer keys
├── docs/                          # Detailed technical documentation
│   ├── README.md                  # Master documentation index
│   ├── 01_USER_GUIDE.md           # Operational guide & Keyboard Hotkeys
│   ├── 02_MANAGE_USERS_AND_SECURITY.md# Security & 256-bit PIN vault
│   ├── 03_ANSWER_KEYS_AND_QUIZZES.md  # AI Live Solver & Auto-Learning Storage
│   ├── 04_AUTOMATION_CONTROLS_AND_CONFIG.md# Config & Pacing Controls
│   └── 05_RAILWAY_DEPLOYMENT_GUIDE.md # Cloud Deployment Guide
├── output/
│   └── screenshots/               # Single official screenshot directory
├── railway/                       # Railway Cloud deployment files
│   ├── Dockerfile
│   ├── railway.json
│   └── .dockerignore
├── utils/
│   ├── logger.py                  # Colorized engine logger
│   └── security.py                # 256-Bit cryptographic security engine
├── main.py                        # CLI Menu launcher with 256-bit PIN lock
├── diksha+.bat                    # 1-Click Windows execution script
└── setup.bat                      # 1-Click environment installer
```

---

## 🚀 Quick Start (Local Run)

1. **Install Dependencies**:
   Double click `setup.bat` or run:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Gemini API Keys**:
   Gemini API Keys are pre-configured & 256-bit encrypted in `config.py`. You can also set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variables.

3. **Launch Automation**:
   Double click `diksha+.bat` or run:
   ```bash
   python main.py
   ```
   * Enter Security PIN: `541563`
   * Select registered account and start automation!

4. **Hotkey Live Controls**:
   * Press **`P`** or **`Spacebar`** in the terminal at any time to toggle **PAUSE / RESUME**.

---

## 📖 Documentation Directory

* 📄 [User Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/01_USER_GUIDE.md)
* 📄 [User & Security Management](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/02_MANAGE_USERS_AND_SECURITY.md)
* 📄 [Answer Keys & AI Live Solver Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/03_ANSWER_KEYS_AND_QUIZZES.md)
* 📄 [Automation Controls & Configuration](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/04_AUTOMATION_CONTROLS_AND_CONFIG.md)
* 📄 [Railway Cloud Deployment Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/05_RAILWAY_DEPLOYMENT_GUIDE.md)
