# 🛑 DIKSHA+ AUTOMATION — STOP CONDITIONS, SAFEGUARDS & USER PAUSE GUIDE

This document provides a comprehensive overview of **when automation stops automatically**, **when automation pauses for user input**, and **all safety mechanisms** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [🏆 VICTORY STOP CONDITIONS (Normal Automatic Completion)](#1--victory-stop-conditions-normal-automatic-completion)
2. [⏸️ USER PAUSE & RESUME CONDITIONS (No Server Close / No Exit)](#2-%EF%B8%8F-user-pause--resume-conditions-no-server-close--no-exit)
3. [🛡️ SECURITY & ACCESS PIN STOP CONDITIONS](#3-%EF%B8%8F-security--access-pin-stop-conditions)
4. [🤖 AI SOLVER & RATE-LIMIT BACKOFF SAFEGUARDS](#4--ai-solver--rate-limit-backoff-safeguards)
5. [📊 SUMMARY MATRIX OF ALL STOP & PAUSE CONDITIONS](#5--summary-matrix-of-all-stop--pause-conditions)

---

## 1. 🏆 VICTORY STOP CONDITIONS (Normal Automatic Completion)

The automation finishes cleanly and displays the **Grand Victory Summary** under the following conditions:

* **Trigger 1: 100% Course Completion**: All modules (Module #1 through Module #N) are verified 100% complete with green checkmarks.
* **Trigger 2: Certificate Target Reached**: Reaches `<a act_type="customcert">Download Certificate</a>` or `Certificate` accordion header.

---

## 2. ⏸️ USER PAUSE & RESUME CONDITIONS (No Server Close / No Exit)

Rather than closing the browser or crashing the program, DIKSHA+ **PAUSES** and keeps your browser & server session **100% ACTIVE** under the following conditions:

* **Trigger 1: 5 Sync Attempts Completed Without 100% Badge**:
  If after 5 page reload & item re-execution attempts (75 seconds) the DIKSHA server badge has not updated to 100%, DIKSHA+ pauses and prints:
  ```text
  ===================================================================
   ⏸️  [AUTOMATION PAUSED] 'Module Name' is not 100% complete after 5 attempts.
   🔒 BROWSER & SERVER SESSION REMAIN 100% ACTIVE (NOT CLOSED)!
   👉 Press [ENTER] key in console to RESUME automation & retry module...
  ===================================================================
  ```
  Pressing **[ENTER]** (or any key) immediately resumes the automation and retries the module pass! This process can be repeated as many times as the user wants!

* **Trigger 2: Item Locked After 4 Reload Attempts**:
  If a subsection item remains locked by DIKSHA server after 4 reloads, DIKSHA+ pauses and prompts the user to press **[ENTER]** to retry unlocking!

---

## 3. 🛡️ SECURITY & ACCESS PIN STOP CONDITIONS

* **Trigger 1: Incorrect Security PIN**: If an invalid Security PIN is entered at startup (Correct PIN: `541563`), access is denied and execution stops immediately.

---

## 4. 🤖 AI SOLVER & RATE-LIMIT BACKOFF SAFEGUARDS

* **10-Key Interleaved Alternating AI Pool**: 5 Gemini keys + 5 Groq keys (1 attempt per key, 0.1s instant failover).
* **Stepped Backoff Retries**: If all 10 keys are rate-limited, applies stepped backoffs (30s ➔ 45s ➔ 60s) before retrying.

---

## 5. 📊 SUMMARY MATRIX OF ALL STOP & PAUSE CONDITIONS

| Trigger Condition | Action Taken by DIKSHA+ | Browser Status | User Action Required |
| :--- | :--- | :--- | :--- |
| **All Modules 100% Done** | 🏆 Grand Victory Summary Printed | Kept Open (`KEEP_BROWSER_OPEN=True`) | None (Completed) |
| **Certificate Reached** | 🏆 Grand Victory Summary Printed | Kept Open | None (Completed) |
| **5 Sync Attempts Passed** | ⏸️ **SYSTEM PAUSED** | **100% ACTIVE (NOT CLOSED)** | Press **[ENTER]** in console to RESUME |
| **Item Locked > 4 Attempts** | ⏸️ **SYSTEM PAUSED** | **100% ACTIVE (NOT CLOSED)** | Press **[ENTER]** in console to RESUME |
| **Invalid Security PIN** | ⛔ Access Denied | Closed Immediately | Re-run script & enter PIN `541563` |
