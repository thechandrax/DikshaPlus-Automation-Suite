# 📚 DIKSHA+ AUTOMATION SUITE — TECHNICAL DOCUMENTATION MASTER INDEX

Welcome to the official technical documentation repository for **DIKSHA+ Automation Suite**! Below is the complete master index listing all 13 technical guides in recommended reading order:

---

## 📑 Master Documentation Index

| # | Guide Name | Description |
| :--- | :--- | :--- |
| **01** | [**`01_USER_GUIDE.md`**](01_USER_GUIDE.md) | Getting Started, Security PIN `541563`, Account Selection, and Quick Start Guide. |
| **02** | [**`02_MANAGE_USERS_AND_SECURITY.md`**](02_MANAGE_USERS_AND_SECURITY.md) | Multi-User Credential Registry, 256-Bit SHA-256 Encryption, and Plain-Text Password Fallbacks. |
| **03** | [**`03_ANSWER_KEYS_AND_QUIZZES.md`**](03_ANSWER_KEYS_AND_QUIZZES.md) | Per-Course Answer Key JSON Storage, Dynamic Question Matching, and Auto-Learning Engine. |
| **04** | [**`04_AI_SOLVER_ENGINE_AND_API_KEYS.md`**](04_AI_SOLVER_ENGINE_AND_API_KEYS.md) | 10-Key Interleaved AI Pool (5 Gemini + 5 Groq), Rate-Limit Fallbacks, and Backoff Retries. |
| **05** | [**`05_RAILWAY_CLOUD_DEPLOYMENT.md`**](05_RAILWAY_CLOUD_DEPLOYMENT.md) | 24/7 Railway Cloud Server Deployment, Docker Engine Setup, and Background Container Controls. |
| **06** | [**`06_MODULE_EXECUTION_AND_RETRY_PROTOCOL.md`**](06_MODULE_EXECUTION_AND_RETRY_PROTOCOL.md) | 16x/10x Video Acceleration, 5-Attempt Sync Window, and Infinite User Pause & Resume System. |
| **07** | [**`07_DUAL_AI_SOLVER_AND_BACKOFF_LOGS_GUIDE.md`**](07_DUAL_AI_SOLVER_AND_BACKOFF_LOGS_GUIDE.md) | Mermaid Flowchart for 10-Key Interleaved Pool and Stepped Backoff Logs (30s ➔ 45s ➔ 60s). |
| **08** | [**`08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md`**](08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md) | Complete Android Termux & Ubuntu PRoot Setup, RealVNC GUI, Wake Lock, Timezone Config, & `git pull`. |
| **09** | [**`09_THREE_WAY_EXECUTION_ARCHITECTURE.md`**](09_THREE_WAY_EXECUTION_ARCHITECTURE.md) | 3-Way Core Architecture Matrix (Windows Desktop GUI vs. Railway Cloud vs. Termux VNC GUI). |
| **10** | [**`10_SYSTEM_REQUIREMENTS_AND_TROUBLESHOOTING.md`**](10_SYSTEM_REQUIREMENTS_AND_TROUBLESHOOTING.md) | Minimum System Specifications, Dependency Checklist, and Common Troubleshooting Solutions. |
| **11** | [**`11_COMPLETE_REAL_WORLD_TERMINAL_LOGS_EXAMPLE.md`**](11_COMPLETE_REAL_WORLD_TERMINAL_LOGS_EXAMPLE.md) | Real-World Terminal Output Logs from Startup to 100% Completion & Module Sync Re-Execution. |
| **12** | [**`12_AUTOMATION_STOP_CONDITIONS_AND_SAFEGUARDS.md`**](12_AUTOMATION_STOP_CONDITIONS_AND_SAFEGUARDS.md) | Comprehensive Guide on Victory Triggers, User Pause & Resume Prompts, and Zero-Crash Controls. |
| **13** | [**`13_CHANGELOG_AND_VERSION_HISTORY.md`**](13_CHANGELOG_AND_VERSION_HISTORY.md) | Complete Official Version History, Timestamps, Feature Breakdown, and GitHub Commit Logs. |

---

## ⚡ Quick 1-Word Commands (Termux Ubuntu PRoot)

| Command | Description |
| :--- | :--- |
| **`vnc`** | Kills stale VNC sessions & launches fresh VNC server on port `5901` (`:1`). |
| **`diksha`** | Enters project folder, sets `DISPLAY=:1`, and launches DIKSHA+ with visible GUI browser! |
| **`update`** | Enters project folder & downloads latest code updates from GitHub (`git pull`)! |
| **`exit`** | Exits Ubuntu PRoot (`root@localhost`) back to standard Termux (`~ $`). |
