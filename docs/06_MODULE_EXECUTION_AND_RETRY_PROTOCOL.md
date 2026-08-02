# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & 10-ATTEMPT SYNC WINDOW GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **Video Playback Automation Engine**, **Locked Item Recovery**, **Module-Level Reload ➔ Check ➔ Expand ➔ Re-Execute Incomplete Item Sync Protocol**, **Certificate `customcert` Auto-Completion Protocol**, **Interleaved Gemini/Groq AI Pool**, and **Circuit Breaker Safeguards** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [📹 Video Playback Automation Engine (16x / 10x Speed)](#2--video-playback-automation-engine-16x--10x-speed)
3. [Locked Item Session Recovery](#3-locked-item-session-recovery)
4. [🔄 Module-Level Reload ➔ Check ➔ Expand ➔ Re-Execute Incomplete Item Protocol](#4--module-level-reload--check--expand--re-execute-incomplete-item-protocol)
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
              └── [STEP 04] 🔄 Module-Level Reload ➔ Check ➔ Expand ➔ Re-Execute Incomplete Item Loop
                    └── [STEP 05] Advance to Next Module
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

## 4. 🔄 Module-Level Reload ➔ Check ➔ Expand ➔ Re-Execute Incomplete Item Protocol

When verifying module completion at the end of a module:

```text
On Every Sync Reload Attempt (sync_step 1 to 10):

  1. Reload Page (await page.reload())
              │
              ▼
  2. Step 1: Check Module Header Badge first. Is it 100%?
              │
       ┌──────┴──────┐
  [ YES ]          [ NO ]
       │              │
       ▼              ▼
✅ Log SUCCESS   3. Step 2: Expand Module Accordion Header (#collapse...)
& Advance        4. Step 3: Scan all subsection items inside module
                 5. Step 4: Find incomplete item (not showing 100% checkmark ✓)
                    🎯 RE-EXECUTE THAT INCOMPLETE ITEM IMMEDIATELY!
                      │
                      ▼
                 6. Step 5: Re-check Module Header Badge after completion!
                      │
       ┌──────────────┴──────────────┐
  [ YES ]                         [ NO ]
       │                             │
       ▼                             ▼
✅ Log SUCCESS &              Repeat Sync Loop (Attempt 2 to 10)
Advance to Next Module
```

### 🔑 Module Sync Loop Rules:
1. **Step 1: Check Module Badge First**: If Module Header Badge is `100%`, DIKSHA+ logs `✅ [MODULE SYNC SUCCESS]` and immediately advances to the next module!
2. **Step 2: Expand Accordion & Scan**: If NOT `100%`, DIKSHA+ expands the module accordion panel and re-scans all subsection items.
3. **Step 3: Find & Re-Execute Incomplete Item**: Identifies the exact item that is still incomplete (`not is_item_100_percent_complete(s_btn)`), re-launches it with `safe_action_click`, and executes the activity!
4. **Step 4: Re-Check Module Badge**: Immediately re-checks the Module Header Badge. Once 100%, advances cleanly!
5. **Step 5: Repeat Cycle**: Repeats this reload ➔ check ➔ expand ➔ re-execute ➔ re-check cycle up to **10 attempts maximum** before triggering Circuit Breaker safeguards.

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

If after 10 attempts (reload, check, expand, re-execute incomplete item window) and stepped backoff retries a lesson or assessment remains incomplete:
* Closes browser context cleanly (`page.context.close()`) to prevent infinite loops and protect your account accuracy.
