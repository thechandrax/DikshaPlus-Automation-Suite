# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & STEPPED BACKOFF GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **Locked Item Recovery**, **Double Confirmation Gate Guard**, **Certificate Handling**, and the **Stepped Backoff Retry Protocol (30s ➔ 45s ➔ 60s)** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [Locked Item Session Recovery](#2-locked-item-session-recovery)
3. [Double Confirmation & Gate Refresh](#3-double-confirmation--gate-refresh)
4. [Certificate Section Handling](#4-certificate-section-handling)
5. [Circuit Breaker Guard](#5-circuit-breaker-guard)
6. [Stepped Backoff Retry Protocol (30s ➔ 45s ➔ 60s)](#6-stepped-backoff-retry-protocol-30s--45s--60s)
7. [Continuous Execution Fallback](#7-continuous-execution-fallback)

---

## 1. Module Execution Pipeline

DIKSHA+ executes course modules sequentially from Module #1 to Module #N with strict validation at every level:

```text
[STEP 01] Navigate & Expand Module Header
  └── [STEP 02] Check if Module is 100% Completed (Skip if Done)
        └── [STEP 03] Execute Subsection Items (Videos, PDFs, H5P, Quizzes, Feedback)
              └── [STEP 04] Double Confirmation Gate Check
                    └── [STEP 05] Advance to Next Module
```

* **Item Attempts Tracking**: Tracks execution attempts per subsection item using `item_attempts[btn_text]`.
* **Automatic Activity Selection**: Dynamically detects activity type (`url`, `resource`, `h5pactivity`, `quiz`, `feedback`) and dispatches the correct dedicated automation engine.

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

## 3. Double Confirmation & Gate Refresh

After completing all subsection activities in a module, DIKSHA+ verifies completion:

* **Check 1**: Re-scans all individual item checkmarks in the DOM (`is_item_100_percent_complete()`).
* **Check 2**: Re-scans the main module header percentage badge (`is_header_100_percent_complete()`).
* **Backend Sync Refresh**: If the badge is not 100% yet due to DIKSHA server latency:
  ```text
  --> [GATE REFRESH] Reloading page once to sync DIKSHA server backend checkmarks...
  ```
  Executes `page.reload()` once and re-checks completion before advancing.

---

## 4. Certificate Section Handling

Post-course reward download pages (`'Certificate'`, `'Download Certificate'`):

* **Automatic Skip**: Recognized as optional reward download links rather than interactive lesson activities.
* **Clean Log**:
  ```text
  🎓 [CERTIFICATE SECTION] 'Certificate' reached end of course. Course completed successfully!
  ```
* **No Error Thrown**: Finishes execution cleanly without triggering server stuck errors.

---

## 5. Circuit Breaker Guard

If after 4 attempts and page reloads a regular course lesson or assessment remains incomplete:

* **Trigger Notice**:
  ```text
  ❌ [CRITICAL DIKSHA SERVER FAILURE] 'Module Title' remains incomplete after 4 attempts & 5s page reloads.
  ⛔ [CIRCUIT BREAKER TRIGGERED] Stopping all automation processes and closing server context!
  ```
* **Safety Protocol**: Closes browser context cleanly (`page.context.close()`) to prevent infinite loops and protect your account.

---

## 6. Stepped Backoff Retry Protocol (30s ➔ 45s ➔ 60s)

When solving new quiz or feedback questions live via Gemini AI API:

```mermaid
flowchart TD
    A[New Question Encountered] --> B{In JSON Answer Key?}
    B -- Yes 0.01s --> C[Click Exact Answer]
    B -- No --> D[Call Gemini AI Live Solver]
    D --> E[Try Key Pool #1, #2, #3]
    E -- Success --> F[Save to JSON & Click Answer]
    E -- All Keys Rate Limited HTTP 429 --> G[Stepped Backoff Protocol]
    
    G --> H[⏳ Backoff #1: Wait 30s for Quota Reset]
    H --> I{Solved?}
    I -- Yes --> F
    I -- No --> J[⏳ Backoff #2: Wait 45s for Quota Reset]
    J --> K{Solved?}
    K -- Yes --> F
    K -- No --> L[⏳ Backoff #3: Wait 60s for Quota Reset]
    L --> M{Solved?}
    M -- Yes --> F
    M -- No --> N[Continuous Execution Fallback]
```

### ⏳ Backoff Delays Table:

| Retry Pass | Delay | Action |
| :--- | :--- | :--- |
| **Initial Pool** | 0s (3s pacing) | Rotates across all 256-bit encrypted API keys & models (`gemini-2.0-flash`, `gemini-flash-latest`). |
| **Backoff #1** | **30 Seconds** | Waits 30s for Google API quota reset $\rightarrow$ Retries AI solver across all keys. |
| **Backoff #2** | **45 Seconds** | Waits 45s for Google API quota reset $\rightarrow$ Retries AI solver across all keys. |
| **Backoff #3** | **60 Seconds** | Waits 60s for Google API quota reset $\rightarrow$ Retries AI solver across all keys. |

---

## 7. Continuous Execution Fallback

If after 30s, 45s, and 60s backoff retries the AI API is still rate-limited:

* **Quizzes / Assessments**: Selects **Option A** (`QUIZ AI RATE LIMIT FALLBACK`) so the quiz **continues running smoothly on Railway Cloud without crashing or stopping**.
* **Feedback Forms**: Selects positive rating response (**'Strongly Agree'**) so feedback form submits cleanly.
