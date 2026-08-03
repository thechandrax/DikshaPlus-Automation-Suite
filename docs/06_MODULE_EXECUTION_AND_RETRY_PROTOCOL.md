# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & 5-ATTEMPT USER RESUME WINDOW GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **Video Playback Automation Engine**, **Locked Item Recovery**, **5-Attempt Module Sync Window**, **Infinite User Pause & Resume System**, **Certificate `customcert` Auto-Completion Protocol**, **10-Key Interleaved Gemini/Groq AI Pool**, and **Circuit Breaker Safeguards** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [📹 Video Playback Automation Engine (16x / 10x Speed)](#2--video-playback-automation-engine-16x--10x-speed)
3. [Locked Item Session Recovery & User Pause](#3-locked-item-session-recovery--user-pause)
4. [🔄 5-Attempt Module Sync & Infinite User Pause/Resume Protocol](#4--5-attempt-module-sync--infinite-user-pauseresume-protocol)
5. [Certificate `customcert` Auto-Completion Protocol](#5-certificate-customcert-auto-completion-protocol)
6. [10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)](#6-10-key-interleaved-alternating-ai-pool-5-gemini--5-groq)
7. [Zero-Crash Safeguard (Infinite User Control)](#7-zero-crash-safeguard-infinite-user-control)

---

## 1. Module Execution Pipeline

DIKSHA+ executes course modules sequentially from Module #1 to Module #N with strict validation at every level:

```text
[STEP 01] Navigate & Expand Module Accordion Header
  └── [STEP 02] Check if Module Header is 100% Completed (Skip if Done)
        └── [STEP 03] Execute Subsection Items (Videos, PDFs, H5P, Quizzes, Feedback)
              └── [STEP 04] 🔄 5-Attempt Module Sync Window
                    └── [IF NOT 100%] ⏸️ AUTOMATION PAUSED (Wait for [ENTER] to Resume)
                          └── [STEP 05] Advance to Next Module when 100%
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

## 3. Locked Item Session Recovery & User Pause

When DIKSHA server locks a subsection item:
1. **Detection**: `is_button_enabled(btn) == False`.
2. **Session Refresh**: Waits 5s, executes `page.reload()`, re-opens accordion header, and re-checks unlock status.
3. **User Pause & Resume**: If still locked after 4 attempts, DIKSHA+ keeps the browser session 100% ACTIVE and prompts:
   `Press [ENTER] to RESUME & retry locked item:`

---

## 4. 🔄 5-Attempt Module Sync & Infinite User Pause/Resume Protocol

When verifying module completion at the end of a module:

```text
On Every Sync Reload Attempt (sync_step 1 to 5):

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
✅ Log SUCCESS &              Repeat Sync Loop (Attempts 1 to 5)
Advance to Next Module               │
                                     ▼
                      If NOT 100% after 5 Attempts:
                      ==============================================
                      ⏸️ AUTOMATION PAUSED (NO CLOSING / NO EXIT!)
                      👉 Press [ENTER] in console to RESUME
                      ==============================================
                                     │
                                     ▼
                      User presses Enter -> RE-EXECUTES MODULE!
                      Repeats as many times as the user wants!
```

### 🔑 Core Guarantees:
1. **5 Attempts Maximum Per Pass**: The patient sync window runs for **5 attempts (75 seconds)**.
2. **ZERO SERVER CLOSE**: Browser context and server session are **100% PRESERVED & KEPT ACTIVE**!
3. **Infinite User Pause & Resume**: If after 5 attempts the badge is not 100%, the console pauses with a banner. Pressing Enter (or any key) immediately resumes execution from where it left off!
4. **Repeat As Many Times As User Wants**: The user can press Enter to retry as many times as needed until 100% completion is achieved!

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

## 7. Zero-Crash Safeguard (Infinite User Control)

DIKSHA+ will **NEVER** close your browser or terminate your session due to server delays. You retain full interactive control to pause, inspect, and press Enter to resume automation at any time!
