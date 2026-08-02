# 📘 DIKSHA+ USER GUIDE & OPERATIONAL CONTROLS

Welcome to the official User Guide for **DIKSHA+ Automation Suite**. This document covers system launching, live keyboard controls, live asterisk PIN masking, 1-word shortcuts, 10-attempt sync windows, Certificate customcert auto-completion, and Feedback Form automation.

---

## 🔑 1. Security Authentication & Live Asterisk (`*`) PIN Masking

Access to DIKSHA+ is protected by a 256-bit SHA-256 cryptographic security PIN lock:
* **Default Master Security PIN**: `541563`
* **Live Asterisk (`*`) Echo**: As you type each digit (`5`, `4`, `1`, `5`, `6`, `3`) on Windows CMD, Linux, or Termux, asterisks `******` appear live on screen! Backspace erases characters live.

---

## ⚡ 2. 1-Word Shortcuts in Termux (Ubuntu PRoot)

* **`vnc`**: Kills old VNC server & starts fresh VNC server on port `5901` (`:1`).
* **`diksha`**: Auto-enters project directory, sets `DISPLAY=:1`, and launches DIKSHA+ with visible GUI browser!
* **`exit`**: Exits Ubuntu PRoot (`root@localhost`) back to Termux (`~ $`).

---

## 🎮 3. Live Keyboard Hotkey Controls & Screen Video Pause

DIKSHA+ includes an asynchronous keyboard listener (`msvcrt`) running in a non-blocking background thread:

* **Toggle Pause / Resume**: Press **`P`** or **`Spacebar`** in the terminal at any time!
  * **When Paused**: The engine freezes browser execution instantly, executes `video.pause()` on any playing HTML5 video element on screen, and logs `⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...`
  * **When Resumed**: The engine executes `video.play()` to resume video playback and continues automation immediately, logging `▶️ [AUTOMATION RESUMED] Continuing DIKSHA execution...`

---

## 🛡️ 4. Automatic Video Auto-Play & Network Stall Recovery Safeguard

DIKSHA+ includes an automatic stop-and-play safeguard for video streams:
* Periodically checks the HTML5 video element every **1.5 seconds**.
* If DIKSHA server lag or browser autoplay restrictions pause the video, DIKSHA+ automatically detects the stall and triggers `video.play()`!
* Logs: `🛡️ [AUTOPLAY SAFEGUARD] Video was paused. Auto-triggered video.play() to keep playback active.`

---

## ⏳ 5. 10-Attempt x 15s (150s) Patient Server Sync Window

Due to DIKSHA server hydration latency, module header badges or checkmarks may take up to **2.5 minutes** to update on the backend after completing all items in a section:
* **10 Attempts x 15-Second Intervals = 150 Seconds (2.5 Minutes Total)**.
* On every 15-second reload, DIKSHA+ re-checks header badges and individual subsection checkmarks (`✓`). Once 100% complete, it closes the modal, collapses the accordion panel, and advances cleanly.

---

## 🎓 6. Certificate `customcert` Auto-Completion Protocol

When the automation reaches the **`Certificate`** section (or detects a `customcert` / `Download Certificate` element):
* **No "View" Click Necessary**: Detects `<a act_type="customcert" href="...">Download Certificate</a>` and **skips clicking "View"** to prevent PDF popup downloads.
* **Instant Course Completion Confirmation**: Prints the Grand Victory Summary with the user's name and mobile/email ID, then cleanly completes execution!

---

## 🎯 7. Question 1 Navigation Reset Protocol (`#quiznavbutton1`)

When DIKSHA+ clicks **"Continue Assessment"** or **"Start Assessment"**:
1. The bot waits 5 seconds for the assessment iframe to settle.
2. It executes DOM JS dismissal triggers for popup banners.
3. It detects the right-side Quiz Navigation panel (`#quiznavbutton1`).
4. It clicks **Question 1** button (`#quiznavbutton1`) to guarantee solving starts sequentially from Question 1!

---

## 📝 8. Feedback Form Automation Engine (Module #8)

DIKSHA+ includes native automation support for DIKSHA / Moodle Feedback Forms:
1. **Rating Selection**: Inspects `.que-no`, `div.feed-ans-div`, and `input.form-check-input`, selecting your saved rating (`Strongly Agree`, `Agree`, `Appropriate`, `Excellent`, `Yes`).
2. **Comment Textbox Typing**: Detects `<textarea.form-control>` and `<input type='text'>` fields inside open-ended questions, filling full paragraph answers!
3. **Form Submission**: Automatically clicks `Submit Feedback` (`button.submit-feed-btn`, `#submitFeedbackBtn11`).
