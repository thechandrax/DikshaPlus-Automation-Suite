# ⚙️ MODULE EXECUTION, RETRY PROTOCOL & 10-ATTEMPT SYNC WINDOW GUIDE

This document provides a comprehensive technical reference for the **Module Execution Pipeline**, **Video Playback Automation Engine**, **Locked Item Recovery**, **Targeted Single-Item Re-Execution & Dual Confirmation Sync Protocol**, **Certificate `customcert` Auto-Completion Protocol**, **Interleaved Gemini/Groq AI Pool**, and **Circuit Breaker Safeguards** in **DIKSHA+ Automation Suite**.

---

## 📑 Table of Contents

1. [Module Execution Pipeline](#1-module-execution-pipeline)
2. [📹 Video Playback Automation Engine (16x / 10x Speed)](#2--video-playback-automation-engine-16x--10x-speed)
3. [Locked Item Session Recovery](#3-locked-item-session-recovery)
4. [🎯 Targeted Single-Item Re-Execution & Dual Confirmation Sync Protocol](#4--targeted-single-item-re-execution--dual-confirmation-sync-protocol)
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
              └── [STEP 04] 🎯 Targeted Single-Item Re-Execution & Dual Confirmation
                    └── [STEP 05] 10-Attempt Patient Server Sync Window
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

## 4. 🎯 Targeted Single-Item Re-Execution & Dual Confirmation Sync Protocol

When verifying completion for an incomplete subsection item:

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
✅ Log SUCCESS   3. Target ONLY the Single Incomplete Item!
& Advance        🎯 RE-EXECUTE THAT SPECIFIC ITEM ONLY (Re-run Video/PDF/Quiz/Feedback)!
                      │
                      ▼
                 4. 🛡️ DUAL CONFIRMATION GATE:
                    ├─► Check 4A: Is Item itself checkmarked (✓)?
                    └─► Check 4B: Is Module Header Badge 100%?
                      │
       ┌──────────────┴──────────────┐
  [ YES ]                         [ NO ]
       │                             │
       ▼                             ▼
✅ Log SUCCESS &              Repeat Targeted Loop
Advance to Next Item          (Attempts 2 to 10)
```

### 🔑 Targeted Re-Execution & Dual Confirmation Rules:
1. **Targeted Execution ONLY**: DIKSHA+ **never re-runs completed items**. It isolates and re-executes **ONLY the single specific item** that is still incomplete!
2. **🛡️ Dual Confirmation Gate**: Immediately after re-executing the targeted item, DIKSHA+ re-checks **BOTH**:
   * **Check 4A**: Did the specific item display a green checkmark (`✓`)?
   * **Check 4B**: Did the main Module Header Badge update to `100%`?
3. **Instant Victory Exit**: If either Check 4A or Check 4B passes, DIKSHA+ logs `✅ [DUAL CONFIRMATION SUCCESS]`, locks the item in memory, and advances cleanly to the next item!

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

If after 10 attempts (targeted re-execution and Dual Confirmation window) and stepped backoff retries a lesson or assessment remains incomplete:
* Closes browser context cleanly (`page.context.close()`) to prevent infinite loops and protect your account accuracy.
