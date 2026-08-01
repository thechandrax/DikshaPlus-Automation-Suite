# 📖 User Guide & Complete Automation Workflow

This document provides step-by-step instructions for launching, configuring, and operating **DIKSHA+ Automation Suite**.

---

## 🚀 1. Launching DIKSHA+ Automation Suite

### Method A: 1-Click Windows Batch Script (Recommended)
Double-click `diksha+.bat` in the project root directory:
```batch
diksha+.bat
```

### Method B: Command Prompt / PowerShell
Open Terminal or PowerShell in `C:\Users\thego\.gemini\antigravity\scratch\Diksha+ Automation Suite` and run:
```bash
python main.py
```

---

## 🔒 2. Security Access PIN Verification

Upon startup, DIKSHA+ verifies authorization via a 256-Bit Cryptographic SHA-256 PIN check:

```text
===================================================================
               LAUNCHING DIKSHA+ AUTOMATION SUITE
===================================================================

===================================================================
 🔒 DIKSHA+ SECURITY ACCESS VERIFICATION (256-BIT SHA-256)
===================================================================

[Security] Enter 6-digit Security PIN to unlock: ******
 ✔ [Security] 256-Bit Cryptographic PIN verified! Access granted.
```

### Key Security Features:
* **Default Security PIN**: `541563`
* **Salted SHA-256 Hash Verification**: `c72696e654fb1fdbd727a8b66e35bceb05a5a576e602252cbd927e4ff8116edf`
* **Masked Entry**: Asterisks (`*`) echo in real-time as digits are pressed.
* **Backspace Support**: Pressing <kbd>Backspace</kbd> live erases asterisks.
* **Circuit Breaker**: 3 failed PIN attempts automatically terminate execution.

---

## ⏸️ 3. Built-in Hotkey Live Pause & Resume

DIKSHA+ features an active background daemon thread (`msvcrt`) listening for keyboard shortcuts in the terminal window:

* **Press `P` or `Spacebar`**: Toggles **PAUSE / RESUME** in real-time.
* When paused, the log displays:
  ```text
  =================================================================
    ⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...
  =================================================================
  ```
* Pressing `P` or `Spacebar` again safely resumes Playwright execution without interrupting state!

---

## 👤 4. Account Selection Menu

After PIN verification, the system lists all registered student accounts:

```text
===================================================================
 ⚡ DIKSHA+ AUTOMATION SUITE
===================================================================

[Login] Registered accounts:
  [1] Gsgs Sdgr                : gexowo4534@candaba.com
  [2] Bgdh Hdfh                : borkej@smanthaai.online
  [3] Sujata Mondal            : 8617383566
  [4] Sumanta Halder           : 7044015007
  [5] Tasapur Rahaman          : 7908555852
-------------------------------------------------------------------
👉 Select user number (1-5) or type custom email/mobile:
```

---

## 🎓 5. Dashboard & Course Selection

Once logged in, the suite scans **Ongoing Courses** and **Finished Courses** tabs and displays the real-time progress dashboard:

```text
======================================================================
  🎓 DIKSHA+ ENROLLED COURSES (4 ONGOING • 0 FINISHED)
======================================================================

 ⚡ ONGOING COURSES:
  [01] NISHTHA FLN English                           [█░░░░░░░░░  12%] ⌛ Ongoing
  [02] Power of Audio in Education                   [█████████░  92%] ⌛ Ongoing
  [03] Online and Digital Education in the Len... [█████████░  92%] ⌛ Ongoing
  [04] কাৰ্যভিত্তিক গৱেষণা (Action Research)         [██░░░░░░░░  15%] ⌛ Ongoing

-----------------------------------------------------------------------
 👉 Select course number to automate (1-4) [Enter for 1]:
```

---

## ⚙️ 6. Activity Execution Pipeline

When a course is selected, DIKSHA+ executes each activity type automatically:

### A. Video Activities (`act_type="url"`)
* **Multi-Speed Acceleration**: Plays at 16x/4x speed during playback, then slows to 1.0x for the final 45 seconds to trigger server `ended` telemetry.
* **100% Checkmark Verification**: Waits 15 seconds for DIKSHA server checkmark confirmation.

### B. PDF Document Activities (`act_type="resource"`)
* **Page-Down Simulation**: Simulates `PageDown` keystrokes with 2.5s reading pacing per page.
* **End-of-Doc Scroll**: Auto-scrolls `.pdf-viewer` and `iframe` container elements to exact bottom.

### C. Formative Assessments & Quizzes (`act_type="quiz"`)
* **Question 1 Navigation Reset**: When opening or continuing an attempt ("Continue Assessment"), DIKSHA+ automatically detects Question 1 in the right-side Quiz Navigation panel (`#quiznavbutton1`), clicks it, and starts solving from Question 1!
* **Text Normalization**: `normalize_text()` converts Unicode curly apostrophes (`’`) to standard ASCII straight keyboard apostrophes (`'`).
* **AI Live Solver & Multi-Key Pool**: If a question is not in local JSON cache, Gemini AI solves it live with a 3s pacing delay.
* **4-Tier Radio Locator**: Targets `.answer > div.r0`, `.answer > div.r1`, and `preceding-sibling::input[@type='radio']` for 100% radio click precision.
* **Auto-Learning Storage**: Automatically saves solved Q&As to `data/courses/<course_name>.json` under module and subsection hierarchies.
* **Automatic Submission**: Executes final submission (`AUTOMATIC_FINAL_SUBMIT = True`).
