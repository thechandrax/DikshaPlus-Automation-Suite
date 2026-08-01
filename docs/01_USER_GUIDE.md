# 📘 DIKSHA+ USER GUIDE & OPERATIONAL CONTROLS

Welcome to the official User Guide for **DIKSHA+ Automation Suite**. This document covers system launching, live keyboard controls, navigation reset protocols, Video Auto-Play Safeguard, Stepped Backoff Retries, Total Server Stop Circuit Breaker, and Feedback Form automation.

---

## 🔑 1. Security Authentication & PIN Lock

Access to DIKSHA+ is protected by a 256-bit SHA-256 cryptographic security PIN lock:
* **Default Master Security PIN**: `541563`

When running `main.py` or double-clicking `diksha+.bat`, enter `541563` to authenticate.

---

## 🎮 2. Live Keyboard Hotkey Controls & Screen Video Pause

DIKSHA+ includes an asynchronous keyboard listener (`msvcrt`) running in a non-blocking background thread:

* **Toggle Pause / Resume**: Press **`P`** or **`Spacebar`** in the terminal at any time!
  * **When Paused**: The engine freezes browser execution instantly, executes `video.pause()` on any playing HTML5 video element on screen, and logs `⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...`
  * **When Resumed**: The engine executes `video.play()` to resume video playback and continues automation immediately, logging `▶️ [AUTOMATION RESUMED] Continuing DIKSHA execution...`

---

## 🛡️ 3. Automatic Video Auto-Play & Network Stall Recovery Safeguard

DIKSHA+ includes an automatic stop-and-play safeguard for video streams:
* Periodically checks the HTML5 video element every **1.5 seconds**.
* If DIKSHA server lag or browser autoplay restrictions pause the video, DIKSHA+ automatically detects the stall and triggers `video.play()`!
* Logs: `🛡️ [AUTOPLAY SAFEGUARD] Video was paused. Auto-triggered video.play() to keep playback active.`

---

## ⌛ 4. Stepped Backoff Retry & Total Server Stop Protocol

If initial Gemini AI solver attempts run out due to API quota limits:
* **Retry #1**: Waits **30 seconds** for Gemini API quota reset $\rightarrow$ Retries AI solver across all keys/models!
* **Retry #2**: If still rate-limited, waits **45 seconds** $\rightarrow$ Retries AI solver across all keys/models!
* **Retry #3**: If still rate-limited, waits **60 seconds** $\rightarrow$ Retries AI solver across all keys/models!
* **⛔ Total Server Stop Circuit Breaker**:
  * Default Option [A] fallback selection is **COMPLETELY REMOVED**!
  * If the question cannot be solved after 30s, 45s, 60s backoff retries, DIKSHA+ executes `await page.context.close()` and triggers a total server stop safely.

---

## 🎯 5. Question 1 Navigation Reset Protocol (`#quiznavbutton1`)

When DIKSHA+ clicks **"Continue Assessment"** or **"Start Assessment"**:
1. The bot waits 5 seconds for the assessment iframe to settle.
2. It executes DOM JS dismissal triggers for popup banners.
3. It detects the right-side Quiz Navigation panel (`#quiznavbutton1`).
4. It clicks **Question 1** button (`#quiznavbutton1`) to guarantee solving starts sequentially from Question 1!

---

## 📝 6. Feedback Form Automation Engine (Module #8)

DIKSHA+ includes native automation support for DIKSHA / Moodle Feedback Forms:

1. **Rating Selection**:
   * Inspects `.que-no`, `div.feed-ans-div`, and `input.form-check-input`.
   * Automatically selects your saved JSON rating (`Strongly Agree`, `Agree`, `Appropriate`, `Excellent`, `Yes`).
   * If not in JSON, Gemini AI selects the optimal positive rating choice.

2. **Comment Textbox Typing**:
   * Detects `<textarea.form-control>` and `<input type='text'>` fields inside open-ended questions.
   * Fills your exact custom comment string.

3. **Form Submission**:
   * Automatically clicks `Submit Feedback` (`button.submit-feed-btn`, `#submitFeedbackBtn11`).
