# 📝 Answer Keys, AI Live Solver & Auto-Learning Guide

This guide details how per-course JSON answer keys work, how the **Gemini AI Multi-Key Live Solver** operates, how **Unicode Text Normalization** prevents string mismatches, and how **Smart Auto-Learning Storage** saves questions for **DIKSHA+ Automation Suite**.

---

## 📁 1. Per-Course JSON Registry (`data/courses/`)

Each course has its own JSON file inside `data/courses/<course_name>.json`:

* `data/courses/power_of_audio_in_education.json`
* `data/courses/online_and_digital_education_in_the_lens_of_nep_2020.json`
* `data/courses/nishtha_fln_english.json`

Initial course JSON files template automatically with zero hardcoded modules/subsections (`{"course_name": "...", "subsections": []}`). When automation executes a module, `save_auto_learned_qa()` dynamically extracts `module_no`, `module_name`, `subsection_no`, and `subsection_name` live from DIKSHA portal screen during execution!

---

## 🔤 2. Unicode Apostrophe & Text Normalization (`normalize_text`)

To eliminate mismatches caused by website font variations (e.g. `Hon’ble` vs `Hon'ble`):

* `normalize_text()` pipeline converts curly apostrophes (`’`, `\u2019`, `‘`, `\u2018`, `` ` ``) $\rightarrow$ standard straight keyboard apostrophe `'`.
* Converts curly double quotes (`“`, `”`, `\u201c`, `\u201d`) $\rightarrow$ standard double quote `"`.
* Converts en/em dashes (`–`, `—`, `\u2013`, `\u2014`) $\rightarrow$ standard hyphen `-`.
* Standardizes non-breaking spaces (`\u00a0`) and multi-spaces $\rightarrow$ single space.
* Applied across **DOM Screen Extraction**, **JSON Matching**, and **Auto-Learning JSON File Saves**.

---

## 🧠 3. Gemini AI Multi-Key Live Solver Engine

When DIKSHA displays a question during a Formative Assessment (`quiz`) or H5P Interactive Activity (`h5pactivity`):

1. **Step 1: Check Auto-Learning JSON Cache**:
   The engine searches all questions in the JSON file using 100% exact text matching.
   * **If Match Found**: Logged as `⚡ [VERIFIED JSON 100% MATCH QUESTION-03]` and uses target answer in **0.01 seconds**!

2. **Step 2: Gemini AI Multi-Key Live Solving (If Question is NEW)**:
   If the screen question is not in the JSON key:
   * **3-Second Pacing Delay**: Features a smooth 3-second pacing delay before AI API calls.
   * **3-Attempt Retry Protocol**: Runs up to 3 full solver retry rounds across keys before defaulting to Option A.
   * **Multi-Key Failover Pool**: Evaluates encrypted `GEMINI_API_KEYS_ENCRYPTED` in `config.py`. If `Key #1` hits HTTP 429 rate limit, the bot **instantly switches to Key #2**!
   * **2025/2026 Google API Standard**: Sends mandatory `x-goog-api-key` header to `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.

---

## 🎯 4. 4-Tier DOM Radio Locator & Question 1 Reset

* **Question 1 Navigation Reset**:
  When starting or continuing an attempt ("Continue Assessment"), DIKSHA+ automatically detects Question 1 in the right-side Quiz Navigation panel (`#quiznavbutton1`), clicks it, and starts solving sequentially from Question 1!

* **4-Tier Radio Button Locator**:
  1. `row_el.locator("input[type='radio']").first` (direct child radio inside `.answer > div.r0`, `.answer > div.r1`).
  2. `row_el.locator("xpath=preceding-sibling::input[@type='radio'][1]")` (preceding sibling radio).
  3. `target_frame.locator("input[aria-labelledby='...']")` (aria-labelledby linked radio).
  4. `row_el.click(force=True)` (direct row click fallback).

---

## 📊 5. Standardized Log Format Specification

```text
---------------------------------------------------------------------------
❓ [QUESTION-03]: Who formally launched the DIKSHA platform?
📋 [OPTIONS]:
   [A] Hon'ble President of India
   [B] Hon'ble Vice President of India
   [C] Hon'ble Prime Minister of India
   [D] Hon'ble Education Minister
⏳ [AI LIVE] Waiting 3s pacing delay before AI API call...
🧠 [AI ATTEMPT 1/3] Requesting AI solution...
🧠 [AI LIVE SUCCESS] Solved on Attempt 1/3 via Key #1 -> 'Hon'ble Vice President of India'
🧠 [AI LIVE QUESTION-03] Solved NEW question -> 'Hon'ble Vice President of India'
💾 [AUTO-LEARNING SAVE] Saved to online_and_digital_education_in_the_lens_of_nep_2020.json: Module #7 ('Assessment') || Subsection #1 ('Assessment') -> Q: 'Who formally launched the DIKSHA platfor...'
✔ [VERIFIED ANSWER MATCH QUESTION-03] Target Answer: 'Hon'ble Vice President of India'
🎯 [SELECTED OPTION B] Selected Radio Button [B] for Answer: 'Hon'ble Vice President of India'.
---------------------------------------------------------------------------
```
