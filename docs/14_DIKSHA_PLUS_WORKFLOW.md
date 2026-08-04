# ⚡ DIKSHA+ Automation Suite — Complete Workflow Documentation

> **Version:** Post-Fix (33 Bugs Resolved) | **Engine:** `diksha_plus_engine.py` | **Entry:** `main.py`

---

## 📋 Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Startup & Security Flow](#2-startup--security-flow)
3. [Login Flow](#3-login-flow)
4. [Course Selection Flow](#4-course-selection-flow)
5. [Module Processing Engine](#5-module-processing-engine)
6. [Per-Subsection 3-Attempt Retry System](#6-per-subsection-3-attempt-retry-system)
7. [Course Restart System (5 Restarts)](#7-course-restart-system-5-restarts)
8. [Video Activity Flow](#8-video-activity-flow)
9. [PDF Activity Flow](#9-pdf-activity-flow)
10. [Quiz / Assessment Flow](#10-quiz--assessment-flow)
11. [Feedback Activity Flow](#11-feedback-activity-flow)
12. [H5P Interactive Activity Flow](#12-h5p-interactive-activity-flow)
13. [Locked Item Handler](#13-locked-item-handler)
14. [AI Solver System](#14-ai-solver-system)
15. [Double Confirmation & Module Sync](#15-double-confirmation--module-sync)
16. [Key Timings Reference](#16-key-timings-reference)

---

## 1. System Architecture

```mermaid
graph TD
    A["diksha+.bat / python main.py"] --> B["main.py — CLI Entry Point"]
    B --> C["Security PIN Verification SHA-256"]
    C --> D["User Selection Menu"]
    D --> E["asyncio.run run_diksha_automation"]
    E --> F["Playwright Browser Launch Chromium"]
    F --> G["login_diksha()"]
    G --> H{Course URL provided?}
    H -->|--url flag| I["Direct Course URL Mode"]
    H -->|No URL| J["navigate_to_my_learning fetch_enrolled_courses"]
    J --> K["display_interactive_course_menu User picks 1-N"]
    K --> L["process_course_modules()"]
    I --> L
    L --> M["Module Accordion Engine Scan all sections"]
    M --> N["Per-Item 3-Attempt Retry Loop"]
    N --> O{Activity Type}
    O -->|url| P["process_video_activity"]
    O -->|resource| Q["process_pdf_activity"]
    O -->|quiz| R["process_quiz_assessment"]
    O -->|feedback| S["process_feedback_activity"]
    O -->|h5pactivity| T["process_h5p_activity"]
    P & Q & R & S & T --> U["is_item_100_percent_complete"]
    U -->|Verified| V["Next Subsection"]
    U -->|Failed| W{Attempt less than 3?}
    W -->|Yes| N
    W -->|No| X["_CourseRestartSignal raised"]
    X --> Y{Restart count less than 5?}
    Y -->|Yes| L
    Y -->|No| Z["Log and Move On"]
```

---

## 2. Startup & Security Flow

```mermaid
flowchart TD
    A["Run: python main.py"] --> B{AUTO_START == True?}
    B -->|False| C["STANDBY MODE time.sleep loop Railway Cloud Idle"]
    B -->|True| D{skip-pin or non-TTY?}
    D -->|Skip| F["User Selection Menu"]
    D -->|No| E["get_masked_pin Live asterisk masking"]
    E --> E2["SHA-256 of PIN + SALT vs stored hash"]
    E2 -->|Match| F
    E2 -->|Mismatch| G["sys.exit 1"]
    F --> H{Mode}
    H -->|--all-users| I["Batch all users in loop"]
    H -->|--user key| J["Single registered user"]
    H -->|--username + --password| K["Custom credential pair"]
    H -->|Interactive| L["display_interactive_user_menu"]
    I & J & K & L --> M["asyncio.run run_diksha_automation"]
```

### Example Log — Startup
```
===================================================================
 ⚡ DIKSHA+ AUTOMATION SUITE
===================================================================
[Login] Registered accounts:
  [1] Sumanta Halder           : 7044015007
  [2] Sujata Mondal            : 8617383566
  [3] Tasapur Rahaman          : 7908555852
-------------------------------------------------------------------
[Security] Enter 6-digit Security PIN to unlock: ******
✅ Security PIN verified. Access granted.
```

---

## 3. Login Flow

```mermaid
flowchart TD
    A["login_diksha(page, username, password)"] --> B["Navigate to AUTH_LOGIN_URL"]
    B --> C["Wait for login link and click"]
    C --> D["Fill username field"]
    D --> E["Fill password field XOR-decrypted at runtime"]
    E --> F["Click login button"]
    F --> G["Wait up to 90s for post-login redirect"]
    G --> H{URL changed away from login?}
    H -->|Yes| I["Login Success - Wait 10s"]
    H -->|No| J{Retry less than 3?}
    J -->|Yes| K["Wait 3s then retry login"]
    K --> F
    J -->|No| L["Login Failed - raise Exception"]
```

### Example Log — Login
```
[12:05:58] INFO  [LOGIN] Navigating to DIKSHA login page...
[12:06:01] INFO    --> Entering credentials for: Sumanta Halder (7044015007)
[12:06:03] INFO    --> Clicking LOGIN button...
[12:06:09] INFO    --> ✅ Login successful! Redirected to dashboard.
[12:06:09] INFO    --> Waiting 10s for dashboard to fully load...
```

---

## 4. Course Selection Flow

```mermaid
flowchart TD
    A["navigate_to_my_learning"] --> B["Click My Learning nav link"]
    B --> C["fetch_enrolled_courses"]
    C --> D["Scan Ongoing + Finished course cards"]
    D --> E["display_interactive_course_menu"]
    E --> F["Print table with progress bars"]
    F --> G["Select course number 1 to N"]
    G --> H{Input type}
    H -->|Number| I["Select that course"]
    H -->|Enter| J["Default Course 1"]
    H -->|SELECTED_USER env| K["Railway auto-select"]
    I & J & K --> L["Navigate to course URL"]
    L --> M["process_course_modules"]
```

### Example Log — Course Menu
```
===================================================================
  🎓 DIKSHA+ ENROLLED COURSES (1 ONGOING • 2 FINISHED)
===================================================================

 ⚡ ONGOING COURSES:
  [01] NISHTHA ECCE English           [████░░░░░░  40%] ⌛ Ongoing

 ✨ FINISHED COURSES:
  [02] Power of Audio in Education    [██████████ 100%] 🏆 Finished
  [03] NISHTHA FLN English            [██████████ 100%] 🏆 Finished

-------------------------------------------------------------------
 👉 Select course number to automate (1-3) [Enter for 1]: 1

[12:06:12] INFO  🚀 Starting Enrolled Course: [1] NISHTHA ECCE English
[12:06:12] INFO    --> Loaded answer key: data/courses/NISHTHA_ECCE_English.json
```

---

## 5. Module Processing Engine

```mermaid
flowchart TD
    A["process_course_modules()"] --> B["ensure_on_course_page navigate to course URL"]
    B --> C["Click Lessons tab Wait 5s for server hydration"]
    C --> D["ACCORDION ENGINE Scan all module headers"]
    D --> E{For each header}
    E --> F{Discussion / Navigation / Pinned?}
    F -->|Yes| G["SKIP SECTION move to next"]
    F -->|No| H{Certificate Section?}
    H -->|Yes| I["COURSE COMPLETED log and return"]
    H -->|No| J{Header already 100%?}
    J -->|Yes| K["SKIP MODULE already done"]
    J -->|No| L["Expand accordion Get distinct_btns"]
    L --> M["Print Subsection Checklist"]
    M --> N["Per-Item Execution Loop with 3-attempt retry"]
    N --> O["DOUBLE CONFIRMATION Module Sync 10 attempts"]
    O --> P{Synced?}
    P -->|Yes| Q["MODULE COMPLETED advance"]
    P -->|No| R["PAUSED Press ENTER to retry"]
    R --> L
```

### Example Log — Module Scan
```
[12:06:19] INFO  [ACCORDION ENGINE] Scanning course section accordions...
[12:06:19] INFO    --> [SKIP SECTION] 'Important Discussions (Pinned)' Skipping!
[12:06:19] INFO    --> [SKIP SECTION] 'Course Navigation' Skipping!

===================================
   DIKSHA COURSE STRUCTURE (6 MODULES DETECTED)
===================================
  [01] ⏳ Module 01: Introduction to ECCE      || 0%   || View
  [02] ✓  Module 02: Play and Development       || 100% || View
  [03] ⏳ Module 03: Play-based Activities      || 40%  || View

  📋 [SUBSECTION BREAKDOWN (31 ITEMS)]:
     [01/31] ✓  Introduction to ECCE            || 100% || View
     [08/31] ⏳ Use of Play-based Activities     || 0%   || View
     [13/31] ⏳ Play and Learning Material       || 0%   || View
```

---

## 6. Per-Subsection 3-Attempt Retry System

```mermaid
flowchart TD
    A["for j btn in distinct_btns"] --> B{Already 100% or in completed_items?}
    B -->|Yes| C["ALREADY DONE Skip next item"]
    B -->|No| D{Item Locked by DIKSHA?}
    D -->|Yes| E["LOCKED ITEM Re-execute prerequisite j-1 Reload page"]
    E --> F["LOCK RETRY continue outer while Rescan buttons"]
    D -->|No| G["item_success = False for item_attempt 1 to 3"]
    G --> H["SUBSECTION j/total Title Attempt X/3"]
    H --> I["Execute activity video pdf quiz feedback h5p"]
    I --> J["is_item_100_percent_complete check"]
    J -->|100%| K["ATTEMPT X/3 SUCCESS item_success = True break"]
    J -->|Not 100%| L{attempt less than 3?}
    L -->|Yes| M["ATTEMPT X/3 INCOMPLETE Retry in 5s"]
    M --> G
    L -->|No| N["ALL 3 ATTEMPTS EXHAUSTED raise _CourseRestartSignal"]
    I -->|Exception| O{attempt less than 3?}
    O -->|Yes| P["Retry in 5s"]
    P --> G
    O -->|No| Q["CRASH ALL 3 ATTEMPTS raise _CourseRestartSignal"]
    K --> R{item_success?}
    R -->|Yes| S["Add to completed_items Wait 4s next item"]
    R -->|No| T["Not added will be retried on course restart"]
```

### Example Log — Attempt 1 Success
```
===================================
 ▶ SUBSECTION [08/31]: 'Use of Play-based Activities' (Type: 'url') [Attempt 1/3]
===================================
[12:06:47] INFO    --> [CLICKED VIEW BUTTON] View button click sent — waiting 3s...
[12:06:50] INFO    --> [MODAL OPENED] Activity modal opened successfully on first click!
[12:06:57] INFO    --> Video playback started (Muted & 360p Low Resolution).
[12:06:59] INFO    --> Video Duration: 192 seconds (3m 12s)
[12:07:14] INFO    --> Dynamic Acceleration: Applying 10x Speed (Short Video < 5 min)...
[12:08:04] INFO    --> Clicking activity close button (x)...
[12:08:08] INFO    --> Server 100% checkmark confirmed!
[12:08:08] INFO  ✅ [ATTEMPT 1/3 SUCCESS] 'Use of Play-based Activities' verified 100% complete!
[12:08:08] INFO    --> DIKSHA Server sync buffer: waiting 4 seconds...
```

### Example Log — Attempt 1 Fail → Attempt 2 Success
```
===================================
 ▶ SUBSECTION [08/31]: 'Use of Play-based Activities' (Type: 'url') [Attempt 1/3]
===================================
[12:06:57] ERROR    [-] Attempt 1/3 execution notice: TimeoutError waiting for selector
[12:06:57] INFO    --> Retrying in 5s... (Attempt 2/3)

===================================
 ▶ SUBSECTION [08/31]: 'Use of Play-based Activities' (Type: 'url') [Attempt 2/3]
===================================
[12:07:05] INFO    --> Video Duration: 192 seconds
[12:07:58] INFO    --> Server 100% checkmark confirmed!
[12:07:58] INFO  ✅ [ATTEMPT 2/3 SUCCESS] Verified 100% complete!
```

### Example Log — All 3 Attempts Exhausted
```
===================================
 ▶ SUBSECTION [13/31]: 'Play and Learning Material' (Type: 'resource') [Attempt 3/3]
===================================
[12:15:30] WARNING   ⚠️ [ATTEMPT 3/3 INCOMPLETE] Not yet 100% on server.
[12:15:30] WARNING   ⚠️ [ALL 3 ATTEMPTS EXHAUSTED] 'Play and Learning Material' failed all 3 attempts.
                         Restarting course from beginning...
```

---

## 7. Course Restart System (5 Restarts)

```mermaid
flowchart TD
    A["_CourseRestartSignal raised item failed all 3 attempts"] --> B["Signal bubbles through for item_attempt for j btn while module_retry_pass for i header process_course_modules"]
    B --> C["Caught in run_diksha_automation for _cr in range 1 to 7"]
    C --> D{_cr less than 6 i.e. restart 1 to 5?}
    D -->|Yes| E["COURSE RESTART _cr/5 Log failed item page.goto course URL Wait 5s"]
    E --> F["Re-call process_course_modules Full fresh scan from top"]
    F --> G{CourseRestartSignal again?}
    G -->|Yes| C
    G -->|No| H["Course completed normally break restart loop"]
    D -->|No — 5 restarts done| I["COURSE RESTART LIMIT restarted 5 times moving on"]
```

### Example Log — Course Restart 1/5
```
[12:15:44] WARNING  ⚠️ [ALL 3 ATTEMPTS EXHAUSTED] 'Play and Learning Material' failed.
                        Restarting course from beginning...

===================================================================
 🔄 [COURSE RESTART 1/5] Item 'Play and Learning Material' failed all attempts.
     Restarting course from beginning...
===================================================================

[12:15:49] INFO  [COURSE MODULES] Checking for 'Lessons' tab...
[12:15:50] INFO    --> Waiting 5 seconds for DIKSHA server to hydrate modules...
[12:15:55] INFO  [ACCORDION ENGINE] Scanning course section accordions...
[12:15:55] INFO    --> [SKIP MODULE] 'Module 01' is ALREADY 100% COMPLETED. Skipping!
[12:15:55] INFO    --> [SKIP MODULE] 'Module 02' is ALREADY 100% COMPLETED. Skipping!

===================================
 ▶ SUBSECTION [13/31]: 'Play and Learning Material' (Type: 'resource') [Attempt 1/3]
===================================
[12:16:12] INFO  ✅ [ATTEMPT 1/3 SUCCESS] 'Play and Learning Material' verified 100% complete!
```

### Example Log — Restart Limit Hit
```
[12:45:00] ERROR  ❌ [COURSE RESTART LIMIT] Course restarted 5 times.
                     Item 'Play and Learning Material' still failing. Moving on.
```

---

## 8. Video Activity Flow

```mermaid
flowchart TD
    A["process_video_activity(page, view_button)"] --> B["open_activity_popup Click View Wait 3s"]
    B --> C{Modal opened?}
    C -->|Yes| D["MODAL OPENED First click success"]
    C -->|No| E["MODAL NOT DETECTED DOUBLE-TRIGGER Re-click by act_id Wait 3s"]
    D & E --> F["Scan all iframes for video element"]
    F --> G["Set Muted + 360p Low Resolution"]
    G --> H{Saved Progress greater than 0?}
    H -->|Yes| I["SAVED PROGRESS RESUMED Seek to position"]
    H -->|No| J["Start from beginning"]
    I & J --> K["15s Warm-up Buffer at 1.0x telemetry session init"]
    K --> L{Duration 5 min or more?}
    L -->|Yes| M["16x Speed Acceleration"]
    L -->|No| N["10x Speed Acceleration"]
    M & N --> O["45s Final Buffer at 1.0x natural ended event + 100% telemetry"]
    O --> P["close_activity_modal"]
    P --> Q["VIDEO CHECKMARK Wait 10-15s for server mark"]
    Q --> R["wait_for_server_checkmark"]
    R --> S["Server 100% checkmark confirmed!"]
```

### Example Log — Video
```
[12:06:46] INFO  [VIDEO ACTIVITY] Opening video module...
[12:06:47] INFO    --> [CLICKED VIEW BUTTON] View button click sent — waiting 3s...
[12:06:50] INFO    --> [MODAL OPENED] Activity modal opened successfully on first click!
[12:06:57] INFO    --> Video playback started (Muted & 360p Low Resolution preference set).
[12:06:59] INFO    --> Video Duration: 192 seconds (3m 12s)
[12:06:59] INFO    --> [SAVED PROGRESS RESUMED] Video already at 2% (5s / 192s)!
[12:06:59] INFO    --> 15s Warm-up Buffer: playing at 1.0x speed for session telemetry...
[12:07:14] INFO    --> Dynamic Acceleration: Applying 10x Speed (Short Video < 5 min)...
[12:07:29] INFO    --> 45s Final Buffer: slowing to 1.0x speed for natural ended event...
[12:08:04] INFO    --> Clicking activity close button (x)...
[12:08:08] INFO    --> [VIDEO CHECKMARK] Waiting 10s to 15s for video 100% checkmark...
[12:08:08] INFO    --> Server 100% checkmark confirmed!
```

### Example Log — Double-Trigger Popup
```
[12:06:47] INFO    --> [CLICKED VIEW BUTTON] View button click sent — waiting 3s...
[12:06:50] WARNING   --> [MODAL NOT DETECTED] Modal did not open after first click.
                         Attempting double-trigger fallback...
[12:06:50] INFO    --> [DOUBLE-TRIGGER POPUP] Re-clicking title link to force open popup modal...
[12:06:53] INFO    --> Video playback started (Muted & 360p Low Resolution).
```

---

## 9. PDF Activity Flow

```mermaid
flowchart TD
    A["process_pdf_activity(page, view_button)"] --> B["open_activity_popup Click View Wait 3s"]
    B --> C{Modal opened?}
    C -->|Yes| D["MODAL OPENED"]
    C -->|No| E["DOUBLE-TRIGGER POPUP"]
    D & E --> F["Wait MIN_PDF_READ_SECONDS 10s"]
    F --> G["Automated Page Flipping Simulate PageDown key presses 1 per 1.5s"]
    G --> H["End-of-Doc Scroll to exact bottom of PDF viewer"]
    H --> I["close_activity_modal"]
    I --> J["wait_for_server_checkmark"]
    J --> K["Server 100% checkmark confirmed!"]
```

### Example Log — PDF
```
[12:08:24] INFO  [PDF ACTIVITY] Opening PDF document resource...
[12:08:27] INFO    --> [CLICKED VIEW BUTTON] View button click sent — waiting 3s...
[12:08:30] INFO    --> [MODAL OPENED] Activity modal opened successfully on first click!
[12:08:39] INFO    --> Automated Page Flipping: simulating PageDown key presses...
[12:08:51] INFO    --> End-of-Doc Scroll: scrolling PDF viewer container to exact bottom...
[12:08:55] INFO    --> Clicking activity close button (x)...
[12:08:59] INFO    --> Server 100% checkmark confirmed!
```

---

## 10. Quiz / Assessment Flow

```mermaid
flowchart TD
    A["process_quiz_assessment(page, btn, answer_key)"] --> B["open_activity_popup"]
    B --> C["Close quiz banner if visible"]
    C --> D["Click Start Assessment button"]
    D --> E["For each question"]
    E --> F["Extract question text + answer options"]
    F --> G["lookup_answer_in_key check local JSON"]
    G --> H{Found in key?}
    H -->|Yes| I["Select matching answer option"]
    H -->|No| J["solve_question_with_ai Gemini + Groq"]
    J --> K{AI returned answer?}
    K -->|Yes| I
    K -->|No| L["Skip — no answer found"]
    I --> M["Click Next Question"]
    M --> N{More questions?}
    N -->|Yes| E
    N -->|No| O["Click Review and Submit"]
    O --> P{AUTOMATIC_FINAL_SUBMIT?}
    P -->|Yes| Q["Click Final Submit button"]
    P -->|No| R["Leave on Review page manual submission"]
    Q & R --> S["save_auto_learned_qa write to course JSON"]
    S --> T["Quiz Complete"]
```

### Example Log — Quiz with AI
```
[12:20:11] INFO  [QUIZ] Question 1/10: 'What is play-based learning?'
[12:20:11] INFO    --> Checking local answer key... Not found.
[12:20:11] INFO    --> Querying AI solver (Gemini → Groq)...
[12:20:13] INFO    🧠 [GEMINI AI SUCCESS] Key #1 -> 'Child-led exploration'
[12:20:13] INFO    --> Selected option [B]: 'Child-led exploration'
[12:20:13] INFO    --> Clicking Next Question...
...
[12:20:45] INFO    --> Clicking Review & Submit...
[12:20:48] INFO    --> Clicking Final Submit button...
[12:20:50] INFO    --> Quiz submitted! Server 100% checkmark confirmed!
```

---

## 11. Feedback Activity Flow

```mermaid
flowchart TD
    A["process_feedback_activity(page, btn, answer_key)"] --> B["open_activity_popup"]
    B --> C["Scan all feedback question containers"]
    C --> D{Question type}
    D -->|Radio MCQ| E["Select first available radio option or lookup in key"]
    D -->|Textarea| F["Type: The training is very helpful and informative."]
    E & F --> G["Next question"]
    G --> H{More questions?}
    H -->|Yes| D
    H -->|No| I["Click Submit Feedback button"]
    I --> J["Wait 6s for AJAX sync"]
    J --> K["wait_for_server_checkmark"]
    K --> L["Feedback Submitted"]
```

---

## 12. H5P Interactive Activity Flow

```mermaid
flowchart TD
    A["process_h5p_activity(page, btn, answer_key)"] --> B["open_activity_popup"]
    B --> C["Locate H5P iframe scan all frames"]
    C --> D["Click h5p-startbutton if visible"]
    D --> E["For each H5P question"]
    E --> F["Extract question + options from iframe"]
    F --> G["lookup or solve_question_with_ai"]
    G --> H["Click matching answer option"]
    H --> I["Click Check Answer button"]
    I --> J["Click Next Question button"]
    J --> K{More questions?}
    K -->|Yes| E
    K -->|No| L["Click Finish button"]
    L --> M["save_auto_learned_qa"]
    M --> N["H5P Complete"]
```

---

## 13. Locked Item Handler

```mermaid
flowchart TD
    A["is_item_locked_by_diksha returns True"] --> B["LOCKED ITEM DETECTED SUBSECTION j/total locked"]
    B --> C{j >= 2?}
    C -->|Yes| D["Get prev_btn = distinct_btns at j-2 Get prev_act_type"]
    D --> E["Re-execute prior prerequisite item j-1/total"]
    E --> F{prev_act_type}
    F -->|url| G["process_video_activity"]
    F -->|resource| H["process_pdf_activity"]
    F -->|h5pactivity| I["process_h5p_activity"]
    G & H & I --> J["page.reload Wait 5s ensure_on_course_page"]
    J --> K["lock_triggered = True break inner for loop"]
    K --> L{lock_triggered?}
    L -->|Yes| M{module_retry_pass > max + 3?}
    M -->|No| N["LOCK RETRY continue outer while Re-scan buttons on fresh page"]
    M -->|Yes| O["LOCK RETRY LIMIT proceed to sync check"]
    N --> P["Item now unlocked Execute normally"]
    C -->|No first item| Q["No prerequisite Reload page and retry"]
```

### Example Log — Locked Item
```
[12:08:22] INFO    --> [✓ ALREADY DONE] SUBSECTION [12/31]: 'Activities for Mathematical Thinking...' Skipping!
[12:08:24] WARNING   --> 🔒 [LOCKED ITEM DETECTED] SUBSECTION [13/31]: 'Play and Learning Material' locked.
[12:08:24] INFO    --> Re-triggering prior item & reloading page to hydrate DIKSHA server unlock...
[12:08:24] INFO    --> Re-executing prior prerequisite item [12/31]: 'Activities for Mathematical Thinking...'
[12:08:24] INFO  [PDF ACTIVITY] Opening PDF document resource...
[12:08:55] INFO    --> Server 100% checkmark confirmed!
[12:09:00] INFO  🔓 [LOCK RETRY] Prerequisite executed. Re-scanning 'Module 03' buttons...

===================================
 ▶ SUBSECTION [13/31]: 'Play and Learning Material' (Type: 'resource') [Attempt 1/3]
===================================
[12:09:02] INFO  [PDF ACTIVITY] Opening PDF document resource...
[12:09:35] INFO  ✅ [ATTEMPT 1/3 SUCCESS] 'Play and Learning Material' verified 100% complete!
```

---

## 14. AI Solver System

```mermaid
flowchart TD
    A["solve_question_with_ai(question, options)"] --> B["Build interleaved sequence Gemini1 Groq1 Gemini2 Groq2"]
    B --> C["For each provider and key"]
    C --> D{Provider}
    D -->|Gemini| E["asyncio.to_thread _try_gemini_key Models: gemini-2.0-flash then gemini-2.0-flash-lite then gemini-1.5-flash-latest"]
    D -->|Groq| F["asyncio.to_thread _try_groq_key Models: llama-3.3-70b then llama-3.1-70b then mixtral-8x7b"]
    E & F --> G{Answer returned?}
    G -->|Yes| H["Return answer string"]
    G -->|Rate limit 429 503| I["Try next key in sequence"]
    G -->|Auth fail 401 403| J["Break invalid key"]
    I --> C
    J --> C
    C -->|All keys exhausted| K["Stepped Backoff 30s then 45s then 60s wait"]
    K --> L["Retry all keys again"]
    L --> M{Answer?}
    M -->|Yes| H
    M -->|No| N["return None no answer found"]
```

> **Important:** All HTTP calls run in `asyncio.to_thread()` — the Playwright event loop is never blocked.

### Example Log — AI Solver
```
[12:10:11] INFO    --> Querying AI solver (Gemini Key #1 → gemini-2.0-flash)...
[12:10:13] INFO    🧠 [GEMINI AI SUCCESS] Key #1 -> 'Play-based learning'
[12:10:13] INFO    --> AI Answer selected: 'Play-based learning'

--- Rate Limited Example ---
[12:10:14] WARNING   ⏳ [GEMINI RATE LIMIT] Key #1 rate limited. Trying Groq Key #1...
[12:10:14] WARNING   ⏳ [GEMINI RATE LIMIT] Key #2 rate limited. Trying Groq Key #2...
[12:10:14] INFO    ⚡ [GROQ LPU SUCCESS] Key #1 -> 'Play-based learning'

--- Backoff Example ---
[12:10:30] WARNING   ⚠️ [AI INITIAL ATTEMPTS EXHAUSTED] Entering Stepped Backoff (30s→45s→60s)...
[12:11:00] INFO    ⏳ [AI RATE LIMIT BACKOFF 1/3] Waiting 30 seconds for API quota reset...
[12:11:30] INFO    🧠 [AI BACKOFF SUCCESS] Solved on Backoff #1 (30s) via Gemini Key #2
```

---

## 15. Double Confirmation & Module Sync

```mermaid
flowchart TD
    A["All subsections processed in this module pass"] --> B{lock_triggered?}
    B -->|Yes| C["LOCK RETRY continue outer while Rescan fresh buttons"]
    B -->|No| D["DOUBLE CONFIRMATION Verify 100% for Module Header"]
    D --> E["for sync_step in range 1 to 10"]
    E --> F["page.reload Wait 3s ensure_on_course_page"]
    F --> G["Re-expand accordion Get sync_btns"]
    G --> H["Execute any still-incomplete items single shot in sync"]
    H --> I["Check is_header_100_percent_complete OR all items checkmarked"]
    I -->|Pass| J["MODULE SYNC SUCCESS server_synced = True break"]
    I -->|Fail| K{sync_step less than 10?}
    K -->|Yes| L["SYNC WAIT Waiting 15s"]
    L --> E
    K -->|No| M["server_synced = False"]
    J --> N["MODULE COMPLETED Advance to next module"]
    M --> O["AUTOMATION PAUSED Press ENTER to retry module pass"]
    O --> P["User presses ENTER"]
    P --> C
```

### Example Log — Module Sync Success
```
[12:09:08] INFO    --> [DOUBLE CONFIRMATION] Verifying 100% for 'Module 03: Play-based Activities...'
[12:09:10] INFO
  ⏳ [MODULE SYNC 1/10] Reloading page & re-scanning subsections...
[12:09:18] INFO    ⏳ [SYNC WAIT] Attempt 1/10 incomplete. Waiting 15s for server sync...
[12:09:33] INFO
  ⏳ [MODULE SYNC 2/10] Reloading page & re-scanning subsections...
[12:09:41] INFO  ✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified on Attempt #2/10!
[12:09:41] INFO  🎓 [MODULE COMPLETED] 'Module 03: Play-based Activities' completed! Advancing...
```

### Example Log — Full Course Completion
```
===================================================================
 🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!
===================================================================
  ✔ User Profile : Sumanta Halder (7044015007)
  ✔ Course Title : NISHTHA ECCE English
  ✔ Certificate  : Download Certificate Available
  ✔ Status       : 100% Complete — All Modules & Assessments Done!
===================================================================
```

---

## 16. Key Timings Reference

| Phase | Duration | Source |
|---|---|---|
| Lessons tab hydration wait | **5s** | `wait_for_timeout(5000)` |
| Popup open wait after click | **3s** | `wait_for_timeout(3000)` |
| Video warm-up buffer | **15s @ 1.0x** | Hardcoded |
| Video acceleration | **10x** (< 5min) / **16x** (≥ 5min) | Engine logic |
| Video final buffer | **45s @ 1.0x** | Hardcoded |
| PDF minimum read time | **10s** | `MIN_PDF_READ_SECONDS` |
| Feedback AJAX sync wait | **6s** | `wait_for_timeout(6000)` |
| Post-item server sync buffer | **4s** | `wait_for_timeout(4000)` |
| Per-item retry wait | **5s** | `asyncio.sleep(5)` |
| Module sync retry interval | **15s** | `asyncio.sleep(15)` |
| Module sync max attempts | **10** | `range(1, 11)` |
| Per-item retry attempts | **3** | `range(1, 4)` |
| Course restart max attempts | **5** | `range(1, 7)` |
| AI solver backoff delays | **30s → 45s → 60s** | `backoff_delays` |
| Login post-redirect wait | **10s** | `POST_LOGIN_WAIT_SECONDS` |
| Login timeout | **90s** | `timeout=90000` |

---

## Key Files

| File | Role |
|---|---|
| `main.py` | CLI entry point, PIN verification, user selection menu, asyncio.run |
| `automations/diksha_plus_engine.py` | Core automation engine 3200+ lines all async |
| `config.py` | DOM selectors, credentials, API keys, timing constants |
| `utils/security.py` | SHA-256 PIN verification, XOR password encrypt/decrypt |
| `utils/logger.py` | Timestamped colored console logger |
| `data/courses/*.json` | Per-course answer key files auto-created on first run |
| `output/screenshots/` | Auto-saved screenshots on errors |
| `diksha+.bat` | Windows launcher script |

---

*Generated: 2026-08-04 | Engine: Post-33-Bug-Fix | Fixes: 33 across 5 files*
