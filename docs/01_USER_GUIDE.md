# 📘 DIKSHA+ USER GUIDE & OPERATIONAL CONTROLS

Welcome to the official User Guide for **DIKSHA+ Automation Suite**. This document covers system launching, live keyboard controls, navigation reset protocols, Video Auto-Play Safeguard, and Feedback Form automation.

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

## 🎯 4. Question 1 Navigation Reset Protocol (`#quiznavbutton1`)

When DIKSHA+ clicks **"Continue Assessment"** or **"Start Assessment"**:
1. The bot waits 5 seconds for the assessment iframe to settle.
2. It executes DOM JS dismissal triggers for popup banners.
3. It detects the right-side Quiz Navigation panel (`#quiznavbutton1`).
4. It clicks **Question 1** button (`#quiznavbutton1`) to guarantee solving starts sequentially from Question 1!

---

## 📝 5. Feedback Form Automation Engine (Module #8)

DIKSHA+ includes native automation support for DIKSHA / Moodle Feedback Forms:

1. **Rating Selection**:
   * Inspects `.que-no`, `div.feed-ans-div`, and `input.form-check-input`.
   * Automatically selects your saved JSON rating (`Strongly Agree`, `Agree`, `Appropriate`, `Excellent`, `Yes`).
   * If not in JSON, Gemini AI selects the optimal positive rating choice.

2. **Comment Textbox Typing**:
   * Detects `<textarea.form-control>` and `<input type='text'>` fields inside open-ended questions.
   * Fills your exact custom comment string (e.g., *"Incorporating more hands-on practice activities..."*).

3. **Form Submission**:
   * Automatically clicks `Submit Feedback` (`button.submit-feed-btn`, `#submitFeedbackBtn11`).

---

## 🔀 6. Shuffled Option Handling

DIKSHA+ matches options on screen using **text content**, NOT hardcoded letters or position indices:
* If an answer text is `"Hon'ble Vice President of India"`, DIKSHA+ scans all screen option rows (`row_el`).
* If DIKSHA shuffles option choices so that `"Hon'ble Vice President of India"` moves from Option B to Option C, DIKSHA+ matches the text at Option C and clicks Option C's radio button.

---

## 💾 7. Smart Auto-Learning Storage

When Gemini AI solves a question live:
* **Quizzes**: Options array saved as `["[A] ...", "[B] ...", "[C] ...", "[D] ..."]` and answer as `"[B] ..."`.
* **Feedback Forms**: Options array saved as standard strings `["Strongly Agree", "Agree", ...]` without letters.
* Auto-saved to `data/courses/<course_name>.json` under full module & subsection structures.

---

## 📊 8. Standardized Log Tag Reference

| Log Tag | Description |
| :--- | :--- |
| `❓ [QUESTION-03]` | Full question text displayed on screen |
| `📋 [OPTIONS]` | Parsed option choices ([A], [B], [C], [D]) |
| `⚡ [VERIFIED JSON 100% MATCH QUESTION-03]` | Matched answer from cached JSON file (0.01s) |
| `🧠 [AI LIVE SUCCESS]` | Solved live via 5-key Gemini API pool |
| `✍️ [TYPED FEEDBACK RESPONSE QUESTION-19]` | Filled comment textbox in Feedback Form |
| `🛡️ [AUTOPLAY SAFEGUARD]` | Auto-triggered video.play() on stream pause |
| `🎯 [SELECTED OPTION B]` | Clicked radio input for matched answer |
| `💾 [AUTO-LEARNING SAVE]` | Auto-saved Q&A to course JSON |
| `⏸️ [ENGINE PAUSED]` | Automation paused via hotkey (HTML5 video paused) |
| `▶️ [ENGINE RESUMED]` | Automation resumed via hotkey (HTML5 video resumed) |
