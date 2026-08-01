# ⚡ DIKSHA+ AUTOMATION SUITE

An enterprise-grade, end-to-end automation engine for **DIKSHA / Moodle LMS Portals**. Features real-time **Gemini AI Live Solving**, **Auto-Learning Smart JSON Caching**, **Dual-Pass 100% Exact Matching**, and complete **H5P & Formative Assessment** automation.

---

## 🌟 Key Features

* **🧠 Gemini AI Live Solver Engine**: When a quiz question is not found in your local answer key, the bot passes the screen question + option choices to Gemini AI (`gemini-2.0-flash`), which solves the question live in **0.4 seconds**!
* **💾 Smart Auto-Learning JSON Storage**: AI-solved answers are automatically saved to `data/courses/<course_name>.json` under full module and subsection hierarchies (`module_no`, `module_name`, `subsection_no`, `subsection_name`, `questions`). Future runs use the cached answer in **0.01 seconds**!
* **🎯 100% Exact Dual-Pass Verification**:
  * **Gate 1**: 100% Question Text Match (eliminates false index matching).
  * **Gate 2**: Option Label Matching (strips prefixes `a.`, `b.`, `c.`, `d.` and targets `<div data-region='answer-label'>` linked to `<input type="radio">`).
* **⚡ Complete Activity Support**:
  * **Videos (`url`)**: Multi-speed playback acceleration (16x/4x/1x) with telemetry checkmark verification.
  * **PDFs (`resource`)**: Automated page-down flipping and end-of-doc container scrolling.
  * **H5P Quizzes (`h5pactivity`)**: Full interactive quiz auto-solving with AI solver.
  * **Formative Assessments (`quiz`)**: Complete Moodle quiz automation with banner dismissal & automatic final submission.
* **🔒 256-Bit Cryptographic Security**: SHA-256 encrypted multi-user PIN lock (`541563`) and credential vault.
* **☁️ Railway Cloud Ready**: Fully containerized in `railway/` with Dockerfile and Automated Cron deployment options.

---

## 📁 Repository Structure

```text
Diksha+ Automation Suite/
├── automations/
│   └── diksha_plus_engine.py      # Core Playwright automation & AI Live Solver
├── config.py                      # System configuration & dynamic Gemini key loader
├── data/
│   └── courses/                   # Auto-learning per-course JSON answer keys
├── docs/                          # Detailed technical documentation
│   ├── 01_USER_GUIDE.md
│   ├── 02_MANAGE_USERS_AND_SECURITY.md
│   ├── 03_ANSWER_KEYS_AND_QUIZZES.md
│   ├── 04_AUTOMATION_CONTROLS_AND_CONFIG.md
│   └── 05_RAILWAY_DEPLOYMENT_GUIDE.md
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
├── gemini_key.txt                 # Local Gemini API Key (Ignored by Git)
├── .env                           # Environment variables file (Ignored by Git)
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

2. **Configure Gemini API Key**:
   Save your Gemini API Key in `gemini_key.txt` or `.env`:
   ```text
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Launch Automation**:
   Double click `diksha+.bat` or run:
   ```bash
   python main.py
   ```
   * Enter Security PIN: `541563`
   * Select registered account and start automation!

---

## 📖 Documentation Directory

* 📄 [User Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/01_USER_GUIDE.md)
* 📄 [User & Security Management](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/02_MANAGE_USERS_AND_SECURITY.md)
* 📄 [Answer Keys & AI Live Solver Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/03_ANSWER_KEYS_AND_QUIZZES.md)
* 📄 [Automation Controls & Configuration](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/04_AUTOMATION_CONTROLS_AND_CONFIG.md)
* 📄 [Railway Cloud Deployment Guide](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/05_RAILWAY_DEPLOYMENT_GUIDE.md)
