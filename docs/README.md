# ⚡ DIKSHA+ AUTOMATION SUITE — MASTER DOCUMENTATION

Welcome to the complete documentation hub for **DIKSHA+ Automation Suite**. Every guide, configuration detail, security protocol, and deployment instruction is included inside this `docs/` directory.

---

## 📑 Complete Documentation Files

1. 📖 **[01_USER_GUIDE.md](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/01_USER_GUIDE.md)**
   * 1-Click execution scripts (`diksha+.bat` and `setup.bat`).
   * Registered user selection menu (`main.py`).
   * Step-by-step course execution workflow (Login $\rightarrow$ My Learning $\rightarrow$ Ongoing Courses $\rightarrow$ Activity Loop).

2. 🔐 **[02_MANAGE_USERS_AND_SECURITY.md](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/02_MANAGE_USERS_AND_SECURITY.md)**
   * 256-Bit Cryptographic SHA-256 PIN Verification (`541563`).
   * User Credential Vault & in-memory dynamic decryption (`utils/security.py`).
   * Adding and managing registered student accounts safely.

3. 📝 **[03_ANSWER_KEYS_AND_QUIZZES.md](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/03_ANSWER_KEYS_AND_QUIZZES.md)**
   * **Gemini AI Live Solver Engine** (`gemini-2.0-flash`).
   * **Structured Sequential Auto-Learning Storage** (`module_no`, `module_name`, `subsection_no`, `subsection_name`, `questions`).
   * **Dual-Pass 100% Exact Matching** (Gate 1 question text equality & Gate 2 option label target locator).
   * Complete H5P & Formative Assessment activity automation.

4. ⚙️ **[04_AUTOMATION_CONTROLS_AND_CONFIG.md](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/04_AUTOMATION_CONTROLS_AND_CONFIG.md)**
   * Dynamic Gemini API key loading (`GEMINI_API_KEY`, `gemini_key.txt`, `.env`).
   * Screenshot directory configuration (`output/screenshots/`).
   * Playwright pacing controls (`SLOMO_MS`, `AUTOMATIC_FINAL_SUBMIT`, `KEEP_BROWSER_OPEN`).

5. ☁️ **[05_RAILWAY_DEPLOYMENT_GUIDE.md](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/docs/05_RAILWAY_DEPLOYMENT_GUIDE.md)**
   * Consolidated Railway Cloud folder structure (`railway/Dockerfile`, `railway/railway.json`, `railway/.dockerignore`).
   * Headless Playwright Docker container deployment instructions.

---

## 📁 Repository File Overview

```text
Diksha+ Automation Suite/
├── docs/                                  # Complete Master Documentation Folder
│   ├── README.md                          # Master documentation index & summary
│   ├── 01_USER_GUIDE.md                   # Full user operational guide
│   ├── 02_MANAGE_USERS_AND_SECURITY.md    # Security & User Management
│   ├── 03_ANSWER_KEYS_AND_QUIZZES.md      # AI Live Solver & Auto-Learning Storage
│   ├── 04_AUTOMATION_CONTROLS_AND_CONFIG.md# Config & Pacing Controls
│   └── 05_RAILWAY_DEPLOYMENT_GUIDE.md     # Cloud Deployment Guide
├── automations/
│   └── diksha_plus_engine.py              # Playwright Automation & AI Live Solver
├── config.py                              # Dynamic System Configuration
├── data/
│   └── courses/                           # Auto-learning Course Answer Keys
├── output/
│   └── screenshots/                       # Official Screenshot Directory
├── railway/                               # Consolidated Railway Deployment Files
│   ├── Dockerfile
│   ├── railway.json
│   └── .dockerignore
├── utils/
│   ├── logger.py                          # Colorized Console Logger
│   └── security.py                        # Cryptographic PIN & Vault Engine
├── main.py                                # CLI Menu Launcher
├── diksha+.bat                            # 1-Click Windows Batch Launcher
├── setup.bat                              # 1-Click Installer Script
├── gemini_key.txt                         # Local Gemini Key (Git Ignored)
└── .env                                   # Local Environment Variables (Git Ignored)
```
