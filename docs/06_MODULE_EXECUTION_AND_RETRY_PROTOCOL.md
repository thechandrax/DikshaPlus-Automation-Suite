# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & 10-ATTEMPT SYNC WINDOW GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **10-Attempt x 15s (150s) Patient Server Sync Window**, **Certificate `customcert` Auto-Completion Protocol**, **Interleaved Gemini/Groq AI Pool**, and **Circuit Breaker Safeguards** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [Locked Item Session Recovery](#2-locked-item-session-recovery)
3. [10-Attempt x 15s (150s) Patient Server Sync Window](#3-10-attempt-x-15s-150s-patient-server-sync-window)
4. [Certificate `customcert` Auto-Completion Protocol](#4-certificate-customcert-auto-completion-protocol)
5. [10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)](#5-10-key-interleaved-alternating-ai-pool-5-gemini--5-groq)
6. [Circuit Breaker Guard (0% Dummy Option A Fallback)](#6-circuit-breaker-guard-0-dummy-option-a-fallback)

---

## 1. Module Execution Pipeline

DIKSHA+ executes course modules sequentially from Module #1 to Module #N with strict validation at every level:

```text
[STEP 01] Navigate & Expand Module Accordion Header
  └── [STEP 02] Check if Module Header is 100% Completed (Skip if Done)
        └── [STEP 03] Execute Subsection Items (Videos, PDFs, H5P, Quizzes, Feedback)
              └── [STEP 04] Double Confirmation: Re-check DOM Items & 100% Header Badge
                    └── [STEP 05] 10-Attempt x 15s (150s) Patient Server Sync Window
                          └── [STEP 06] Advance to Next Module
```

* **Item Attempts Tracking**: Tracks execution attempts per subsection item using `item_attempts[btn_text]`.
* **Generic Button Isolation**: Tracks completed items by their full unique title (e.g., `'Chapter 19_1_activity4_try_yourself'`), so generic button names like `"View"` or `"Start"` never cause locked items to be skipped.
* **Automatic Activity Selection**: Dynamically detects activity type (`url`, `resource`, `h5pactivity`, `quiz`, `feedback`) and dispatches the dedicated automation engine.

---

## 2. Locked Item Session Recovery

When DIKSHA server locks a subsection item because a prerequisite video or lesson is processing:

1. **Detection**: `is_button_enabled(btn) == False`.
2. **Log Notice**:
   ```text
   --> [LOCKED ITEM] Subsection [02/05]: 'Activity 02' is currently LOCKED.
   --> [SERVER REFRESH] Waiting 5s gap & reloading page (page.reload()) to fetch updated DIKSHA server session unlock status...
   ```
3. **Session Refresh**: Waits 5 seconds, executes `page.reload()`, waits 5 seconds for backend unlock sync, and re-opens the active module accordion.

---

## 3. 10-Attempt x 15s (150s) Patient Server Sync Window

Due to DIKSHA server hydration latency, module header badges or checkmarks may take up to **2.5 minutes** to update on the backend after completing all items in a section:

```text
⏳ [DIKSHA SERVER HYDRATION] 'Module 08: Learning Assessment' header badge is not 100% yet.
⏳ Entering 10-Attempt (150s) Patient Server Sync Window before any Circuit Breaker trigger...
```

* **10 Attempts x 15-Second Intervals = 150 Seconds (2.5 Minutes Total)**.
* **On Every 15-Second Reload (`sync_step` 1 to 10)**:
  1. Reloads page (`await page.reload()`).
  2. Waits 3 seconds for DOM hydration.
  3. **Check 1**: Re-evaluates Module Header Badge (`is_header_100_percent_complete()`).
  4. **Check 2**: Re-opens accordion panel and re-checks all individual subsection checkmarks (`✓`).
  5. **Instant Sync Success**: If either Check 1 or Check 2 passes, it logs `✅ [MODULE SYNC SUCCESS]`, closes the modal, collapses the accordion panel, and advances cleanly to the next module!

---

## 4. Certificate `customcert` Auto-Completion Protocol

When the automation reaches the **`Certificate`** section (or detects a `customcert` / `Download Certificate` element):

1. **No "View" Click Necessary**:
   The engine detects `<a act_type="customcert" href="...mod/customcert/view.php...">Download Certificate</a>` directly inside the Certificate module panel and **skips clicking "View"** to prevent PDF popup downloads.
2. **Instant Course Completion Confirmation**:
   Prints the Grand Victory Summary in the terminal logs:

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

3. **Clean Automation Finish**: Returns `True` and cleanly completes the course automation!

---

## 5. 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)

When a new quiz or feedback question is encountered that is not in local JSON cache:

* **Interleaved Sequence**: `Gemini #1` ➔ `Groq #1` ➔ `Gemini #2` ➔ `Groq #2` ➔ `Gemini #3` ➔ `Groq #3` ➔ `Gemini #4` ➔ `Groq #4` ➔ `Gemini #5` ➔ `Groq #5`.
* **1 Attempt Per Key**: Each key is granted **exactly 1 attempt**. If rate-limited, the engine instantly tries the next provider key in 0.1s.
* **Stepped Backoff Retries**: If all 10 keys are rate-limited, applies stepped backoffs (**30s ➔ 45s ➔ 60s**) before retrying all keys again.

---

## 6. Circuit Breaker Guard (0% Dummy Option A Fallback)

If after 10 attempts (150s sync window) and stepped backoff retries a regular course lesson or assessment remains incomplete:

* **Trigger Notice**:
  ```text
  ❌ [CRITICAL DIKSHA SERVER FAILURE] 'Module Title' remains incomplete after 10 attempts & 150s sync window.
  ⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context!
  ```
* **Safety Protocol**:
  * Default Option [A] selection fallback is **100% completely removed**!
  * Closes browser context cleanly (`page.context.close()`) to prevent infinite loops and protect your account accuracy.
