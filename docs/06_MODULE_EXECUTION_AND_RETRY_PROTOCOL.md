# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & 10-ATTEMPT SYNC WINDOW GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **Video Playback Automation Engine**, **Locked Item Recovery**, **10-Attempt Sync & Re-Execution Protocol**, **Certificate `customcert` Auto-Completion Protocol**, **Interleaved Gemini/Groq AI Pool**, and **Circuit Breaker Safeguards** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [📹 Video Playback Automation Engine (16x / 10x Speed)](#2--video-playback-automation-engine-16x--10x-speed)
3. [Locked Item Session Recovery](#3-locked-item-session-recovery)
4. [🔄 10-Attempt Reload, Check & Re-Execution Sync Protocol](#4--10-attempt-reload-check--re-execution-sync-protocol)
5. [Certificate `customcert` Auto-Completion Protocol](#5-certificate-customcert-auto-completion-protocol)
6. [10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)](#6-10-key-interleaved-alternating-ai-pool-5-gemini--5-groq)
7. [Circuit Breaker Guard (0% Dummy Option A Fallback)](#7-circuit-breaker-guard-0-dummy-option-a-fallback)

---

## 1. Module Execution Pipeline

DIKSHA+ executes course modules sequentially from Module #1 to Module #N with strict validation at every level:

```text
[STEP 01] Navigate & Expand Module Accordion Header
  └── [STEP 02] Check if Module Header is 100% Completed (Skip if Done)
        └── [STEP 03] Execute Subsection Items (Videos, PDFs, H5P, Quizzes, Feedback)
              └── [STEP 04] Double Confirmation: Re-check DOM Items & 100% Header Badge
                    └── [STEP 05] 🔄 10-Attempt Reload, Check & Re-Execution Sync Window
                          └── [STEP 06] Advance to Next Module
```

---

## 2. 📹 Video Playback Automation Engine (16x / 10x Speed)

When DIKSHA+ opens a video lesson (`act_type == "url"` or HTML5 `<video>` element):
* **15s Warm-up Buffer (@ 1.0x Speed)**: Initial telemetry initialization.
* **🚀 16x Speed Acceleration (Long Videos $\ge$ 5 min / 300s)**: `video.playbackRate = 16.0`.
* **⚡ 10x Speed Acceleration (Short Videos $<$ 5 min / 300s)**: `video.playbackRate = 10.0`.
* **45s Final Buffer (@ 1.0x Speed)**: Natural telemetry ended event dispatch.
* **🛡️ Autoplay Safeguard**: Monitors `<video>` every 1.5s; auto-triggers `video.play()` if paused.

---

## 3. Locked Item Session Recovery

When DIKSHA server locks a subsection item because a prerequisite video or lesson is processing:
1. **Detection**: `is_button_enabled(btn) == False`.
2. **Session Refresh**: Waits 5s, executes `page.reload()`, re-opens accordion header, and re-checks unlock status.

---

## 4. 🔄 10-Attempt Reload, Check & Re-Execution Sync Protocol

When a module or subsection item requires progress verification:

```text
On Every Reload Attempt (sync_step 1 to 10):

  1. Reload Page (await page.reload()) & Re-expand Accordion Panel
              │
              ▼
  2. Check 1: Is Module Header Badge 100% OR Item Checkmarked (✓)?
              │
       ┌──────┴──────┐
  [ YES ]          [ NO ]
       │              │
       ▼              ▼
✅ Log SUCCESS   3. Check 2: Item still incomplete?
& Advance        🔄 RE-EXECUTE Activity (Re-run Video/PDF/Quiz/Feedback)!
                      │
                      ▼
                 4. Re-check Checkmark (✓) immediately after re-execution!
                      │
       ┌──────────────┴──────────────┐
  [ YES ]                         [ NO ]
       │                             │
       ▼                             ▼
✅ Log SUCCESS                Repeat Reload & Re-execution Loop
& Advance                     (Attempts 2 to 10)
```

### 🔑 Workflow Logic:
1. **Step 1: Reload & Re-Expand**: Executes `await page.reload()` and re-opens the target module accordion header.
2. **Step 2: Check Module Header Badge & Subsection Checkmark (`✓`)**: Evaluates if `is_header_100_percent_complete()` or `is_item_100_percent_complete()` passes.
3. **Step 3: Auto Re-Execution**: If the subsection item is **NOT** checkmarked `✓` yet, DIKSHA+ **automatically re-launches and re-executes that exact activity** (re-running video stream, scrolling PDF, or answering quiz/feedback)!
4. **Step 4: Post Re-Execution Verification**: Immediately re-verifies checkmark status. If complete, logs `✅ [RE-EXECUTION SUCCESS]` and advances cleanly!
5. **Step 5: Repeat Loop**: Repeats this reload, check, and re-execution cycle up to **10 attempts maximum** before triggering Circuit Breaker safeguards.

---

## 5. Certificate `customcert` Auto-Completion Protocol

When the automation reaches the **`Certificate`** section (or detects a `customcert` / `Download Certificate` element):
1. **No "View" Click Necessary**: Detects `<a act_type="customcert">Download Certificate</a>` and skips clicking "View" to prevent PDF popup downloads.
2. **Instant Course Completion Confirmation**: Prints the Grand Victory Summary and cleanly completes execution!

---

## 6. 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)

* **Interleaved Sequence**: `Gemini #1` ➔ `Groq #1` ➔ `Gemini #2` ➔ `Groq #2` ➔ `Gemini #3` ➔ `Groq #3` ➔ `Gemini #4` ➔ `Groq #4` ➔ `Gemini #5` ➔ `Groq #5`.
* **1 Attempt Per Key**: 0.1s instant failover if rate-limited.
* **Stepped Backoff Retries**: **30s ➔ 45s ➔ 60s**.

---

## 7. Circuit Breaker Guard (0% Dummy Option A Fallback)

If after 10 attempts (reload, check, and re-execution window) and stepped backoff retries a lesson or assessment remains incomplete:
* Closes browser context cleanly (`page.context.close()`) to prevent infinite loops and protect your account accuracy.
