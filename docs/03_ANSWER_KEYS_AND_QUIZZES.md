# 🧠 ANSWER KEYS, AI LIVE SOLVER & FEEDBACK FORM ENGINE

This document details the dual-pass solving pipeline, 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq), Stepped Backoff Retries, Total Server Stop Circuit Breaker, Feedback Form auto-filling, Unicode text normalization, and clean Module -> Subsection JSON storage.

---

## 🎯 1. Dual-Pass Solving Architecture

When DIKSHA+ encounters any Quiz Question or Feedback Question:

```text
[ Question Displayed on Screen ]
               │
               ▼
   Gate 1: Check Local JSON Answer Key (data/courses/<course_name>.json)
               │
       ┌───────┴───────┐
  [ Match Found ]  [ No Match ]
       │               │
       │               ▼
       │     Gate 1.5: 10-Key Interleaved Gemini/Groq Pool (1 Attempt per Key)
       │               │
       │               ├─► Gemini #1 ➔ Groq #1 ➔ Gemini #2 ➔ Groq #2 ...
       │               │
       │               ├─► Stepped Backoffs (30s -> 45s -> 60s) if Rate Limited
       │               │
       │               ├─► ⛔ Circuit Breaker (Total Server Stop) if 0% Solved
       │               │
       │               ├─► Auto-Save New Q&A to Course JSON (Gate 3)
       │               │
       ▼               ▼
   Gate 2: 4-Tier DOM Radio Input Click / Textarea Fill
               │
               ▼
   Next Question / Submit Feedback
```

---

## 🔑 2. 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq)

* **256-Bit Encrypted Pool**: All 10 API keys (5 Gemini + 5 Groq) are encrypted with 256-bit SHA-256 encryption in `config.py` (`GEMINI_API_KEYS_ENCRYPTED` & `GROQ_API_KEYS_ENCRYPTED`).
* **Interleaved Sequence Protocol**:
  `Gemini #1` ➔ `Groq #1` ➔ `Gemini #2` ➔ `Groq #2` ➔ `Gemini #3` ➔ `Groq #3` ➔ `Gemini #4` ➔ `Groq #4` ➔ `Gemini #5` ➔ `Groq #5`.
* **1 Attempt Per Key**: Each key is granted **exactly 1 attempt**. If rate-limited, the engine instantly tries the next provider key in 0.1s.
* **Stepped Backoff Retries**:
  * **Retry #1**: Waits **30 seconds** for API quota reset ➔ Retries all keys across models!
  * **Retry #2**: Waits **45 seconds** for API quota reset ➔ Retries all keys across models!
  * **Retry #3**: Waits **60 seconds** for API quota reset ➔ Retries all keys across models!
* **⛔ Total Server Stop Circuit Breaker**: Default Option [A] fallback selection is **100% COMPLETELY REMOVED**! If all backoff retries fail, DIKSHA+ executes `await page.context.close()` and triggers a total server stop safely.

---

## 📂 3. Clean Module -> Subsection JSON Architecture

Per-course JSON answer keys (`data/courses/<course_name>.json`) use clean hierarchy:

```json
{
  "course_title": "NISHTHA FLN English",
  "modules": [
    {
      "module_no": 8,
      "module_name": "Module 08: Learning Assessment",
      "subsections": [
        {
          "subsection_no": 32,
          "subsection_name": "Formative Assessment 08",
          "questions": [
            {
              "question": "The 360-degree report card will include...",
              "options": [
                "[A] All aspects of the personality of a child.",
                "[B] The literacy and numeracy aspects.",
                "[C] Only the academic aspects.",
                "[D] The creative and psycho-social aspect."
              ],
              "answer": "The creative and psycho-social aspect."
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 📝 4. Feedback Form Auto-Filling & Comment Typing Engine

DIKSHA+ includes native automation support for DIKSHA / Moodle Feedback Forms:
1. **Rating Selection**: Inspects `.que-no`, `div.feed-ans-div`, and `input.form-check-input`, selecting your saved rating (`Strongly Agree`, `Agree`, `Appropriate`, `Excellent`, `Yes`).
2. **Comment Textbox Typing**: Detects `<textarea.form-control>` and `<input type='text'>` fields inside open-ended questions, filling full paragraph answers!
3. **Form Submission**: Automatically clicks `Submit Feedback` (`button.submit-feed-btn`, `#submitFeedbackBtn11`).
