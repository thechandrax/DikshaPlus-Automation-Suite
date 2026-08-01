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

## 👤 3. Account Selection Menu

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

### Input Options:
* **Select Registered Account**: Type `1`, `2`, `3`, `4`, or `5` and press <kbd>Enter</kbd>.
* **Custom Account**: Type any unregistered email or 10-digit mobile number, then enter the password when prompted.

---

## 🎓 4. Dashboard & Course Selection

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

* Enter the target course number (e.g. `1` or `2`) and press <kbd>Enter</kbd>.

---

## ⚙️ 5. Activity Execution Pipeline

When a course is selected, DIKSHA+ executes each activity type automatically:

### A. Video Activities (`act_type="url"`)
* **Multi-Speed Acceleration**: Plays at 16x/4x speed during playback, then slows to 1.0x for the final 45 seconds to trigger server `ended` telemetry.
* **100% Checkmark Verification**: Waits 15 seconds for DIKSHA server checkmark confirmation. If checkmark is not confirmed (e.g., partial 97%), performs 1-time reload/replay recovery.

### B. PDF Document Activities (`act_type="resource"`)
* **Page-Down Simulation**: Simulates `PageDown` keystrokes with 2.5s reading pacing per page.
* **End-of-Doc Scroll**: Auto-scrolls `.pdf-viewer` and `iframe` container elements to exact bottom and presses `End`.

### C. H5P Interactive Quizzes (`act_type="h5pactivity"`)
* Presses `Start Quiz`.
* Extracts H5P question text & options.
* Solves live via **Gemini AI API** (`gemini-2.0-flash`), clicks matching H5P radio option, and auto-saves to JSON cache.

### D. Formative Assessments / Quizzes (`act_type="quiz"`)
* Dismisses banner GIF popups (`button.quiz-popup-close`).
* Solves questions live via **Gemini AI API**, targets exact `<div data-region='answer-label'>` radio inputs, and auto-saves to JSON.
* Executes automatic final quiz submission (`AUTOMATIC_FINAL_SUBMIT = True`).
