# 🛑 DIKSHA+ AUTOMATION SUITE — AUTOMATIC STOP CONDITIONS & SAFEGUARDS

This document provides a technical breakdown of **where, when, and why DIKSHA+ Automation Suite stops automatically**, detailing all victory completion triggers, security gates, Circuit Breaker safeguards, standby modes, and manual hotkeys.

---

## 📑 Summary Table of All Stop Conditions

| Stop Condition | Triggers When... | Action Taken | Result / Log Output |
| :--- | :--- | :--- | :--- |
| **1. Certificate Auto-Completion** | `<a act_type="customcert">` / `'Download Certificate'` detected in module. | Skips clicking View button. | Prints Grand Victory Banner & completes course cleanly (`True`). |
| **2. All Modules 100% Complete** | All module header badges reach 100% checkmarks (`✓`). | Completes all section processing. | Prints Grand Victory Banner & finishes execution cleanly. |
| **3. Security PIN Access Denied** | 3 invalid Security PIN attempts entered (`541563`). | Terminates Python process cleanly. | `⛔ [Security] Access Denied! Maximum security attempts exceeded.` (`sys.exit(1)`) |
| **4. AI Solver Circuit Breaker** | All 10 AI keys (5 Gemini + 5 Groq) & 30s/45s/60s backoffs fail. | Closes browser context cleanly (`page.context.close()`). | `⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes!` |
| **5. 10-Attempt Sync Circuit Breaker** | Module badge not 100% after 10 reloads & 150s (2.5m) sync window. | Closes browser context cleanly (`page.context.close()`). | `❌ [CRITICAL DIKSHA SERVER FAILURE] Module remains incomplete after 150s sync window.` |
| **6. Railway Cloud Standby Mode** | `AUTO_START=False` set in environment variables. | Enters infinite 1-hour standby loop. | `⏸️ [RAILWAY STANDBY MODE] Container standing by on Railway Cloud.` |
| **7. User Keyboard Interrupt** | User presses `Ctrl+C` or terminal hotkey. | Gracefully handles interrupt signal. | `Automation process interrupted by user.` |

---

## 🏆 1. Course Completion & Victory Triggers

### A. Certificate `customcert` Auto-Completion Protocol:
When DIKSHA+ reaches the final course section and detects `<a act_type="customcert">Download Certificate</a>`:
1. **No "View" Click**: Skips clicking the View button to prevent PDF popup downloads.
2. **Grand Victory Summary**: Logs full user details and course status in terminal:
   ```text
   ===================================================================
    🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!
   ===================================================================
     ✔ User Profile : Sumanta Halder (7044015007)
     ✔ Course Title : NISHTHA ECCE English
     ✔ Certificate  : Download Certificate Available
     ✔ Status       : 100% Complete — All Modules & Assessments Done!
   ===================================================================
   ```
3. **Clean Finish**: Returns `True` and completes automation cleanly.

### B. All Modules 100% Completed:
When all course module accordion headers report 100% progress badges, DIKSHA+ logs the victory summary, keeps the browser open (or finishes headless container mode), and exits cleanly.

---

## 🔒 2. Security PIN Clearance Gate

Access to DIKSHA+ is protected by a 256-bit SHA-256 cryptographic Security PIN lock (**`541563`**):
* If an incorrect PIN is entered 3 times consecutively, DIKSHA+ immediately logs:
  `⛔ [Security] Access Denied! Maximum security attempts exceeded.`
* Executes `sys.exit(1)` to lock unauthorized users out of the system.

---

## ⛔ 3. Circuit Breaker Safeguards (0% Option A Fallback)

To maintain 100% course accuracy and account integrity, dummy Option [A] fallback guessing has been **100% completely removed**.

### A. AI Live Solver Exhaustion Circuit Breaker:
* **Trigger**: If an assessment question cannot be solved after trying all **10 Interleaved AI Keys** (5 Gemini + 5 Groq) and **30s ➔ 45s ➔ 60s backoffs**:
* **Action**:
  1. Logs: `⛔ [CIRCUIT BREAKER TRIGGERED] Closing server context cleanly and stopping all automation processes!`
  2. Executes `await page.context.close()`.
  3. Raises `RuntimeError("AI_SOLVER_FAILED_SERVER_STUCK")` to safely stop execution without saving wrong answers.

### B. 10-Attempt x 15s (150s) Server Hydration Sync Circuit Breaker:
* **Trigger**: If DIKSHA server latency delays checkmark updates after 10 page reloads and 150 seconds (2.5 minutes total):
* **Action**:
  1. Logs: `❌ [CRITICAL DIKSHA SERVER FAILURE] Module remains incomplete after 10 attempts & 150s sync window.`
  2. Executes `await page.context.close()`.
  3. Stops automation cleanly to prevent infinite reload loops.

---

## ⏸️ 4. Railway Standby & Hotkey Controls

### A. Railway Cloud Standby Mode (`AUTO_START=False`):
* If `AUTO_START=False` is set in environment variables on Railway Cloud, DIKSHA+ enters a 1-hour sleep loop to keep the container online in standby mode.

### B. Live Terminal Pause Hotkey (**`P`** or **`Spacebar`**):
* Pressing **`P`** or **`Spacebar`** in terminal pauses browser automation and pauses HTML5 video playback. Pressing **`P`** again resumes execution.

### C. Manual Interrupt (`Ctrl+C`):
* Pressing `Ctrl+C` in the terminal triggers Python `KeyboardInterrupt`, logging `Automation process interrupted by user` and releasing system resources.
