# 🧠 ANSWER KEYS, AI LIVE SOLVER & FEEDBACK FORM ENGINE

This document details the dual-pass solving pipeline, Gemini AI Multi-Key Pool integration, Stepped Backoff Retries, Total Server Stop Circuit Breaker, Feedback Form auto-filling, Unicode text normalization, and clean Module -> Subsection JSON storage.

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
       │     Gate 1.5: Query Gemini AI Multi-Key Pool
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

## 🔑 2. Gemini AI Multi-Key Pool & Stepped Backoff Retries

* **Key Encryption**: Gemini API keys are encrypted with 256-bit AES encryption in `config.py`:
  `GEMINI_API_KEYS_ENCRYPTED = ["ENC256:...", "ENC256:...", ...]`
* **Automatic Failover**: If Key #1 encounters HTTP 429 rate limits, DIKSHA+ rotates to Key #2, #3, etc.
* **Official Google Spec**: Sends mandatory `x-goog-api-key` header.
* **Stepped Backoff Retries**:
  * **Initial 3 Rounds**: Tries keys and models with 3s delays.
  * **Backoff Retry #1**: Waits **30 seconds** for API quota reset $\rightarrow$ Retries AI solver!
  * **Backoff Retry #2**: Waits **45 seconds** for API quota reset $\rightarrow$ Retries AI solver!
  * **Backoff Retry #3**: Waits **60 seconds** for API quota reset $\rightarrow$ Retries AI solver!
* **⛔ Total Server Stop Circuit Breaker**:
  * Default Option [A] fallback selection is **COMPLETELY REMOVED**!
  * If the question cannot be solved after 30s, 45s, 60s backoff retries, DIKSHA+ executes `await page.context.close()` and triggers a total server stop safely.

---

## 📂 3. Clean Module -> Subsection JSON Architecture

Course answer keys are organized in the clean standard hierarchy:

```json
{
  "course_name": "Power of Audio in Education",
  "modules": [
    {
      "module_no": 7,
      "module_name": "Assessment",
      "subsections": [
        {
          "subsection_no": 1,
          "subsection_name": "Assessment",
          "questions": [
            {
              "question": "How many community radio stations are there in India as of May 2025",
              "options": [
                "[A] 540",
                "[B] 100",
                "[C] 200",
                "[D] 300"
              ],
              "answer": "[A] 540"
            }
          ]
        }
      ]
    },
          ]
        }
      ]
    },
    {
      "module_no": 8,
      "module_name": "Feedback Form",
      "subsections": [
        {
          "subsection_no": 1,
          "subsection_name": "Feedback Form",
          "questions": [
            {
              "question": "The resources/materials provided during the training programme were useful and informative.",
              "options": [
                "Strongly Agree",
                "Agree",
                "Neutral",
                "Disagree",
                "Strongly Disagree"
              ],
              "answer": "Strongly Agree"
            },
            {
              "question": "Time provided to go through the training resources/materials?",
              "options": [
                "Too Long",
                "Appropriate",
                "Too Short"
              ],
              "answer": "Appropriate"
            },
            {
              "question": "What aspects of the training could be improved?",
              "options": [],
              "answer": "Incorporating more hands-on practice activities and allocating extra time for interactive Q&A sessions would make the training even more effective."
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 📝 4. Dedicated DIKSHA Feedback Form Popup Engine

DIKSHA+ features a **100% dedicated `process_feedback_activity()` engine** tailored specifically for DIKSHA Feedback Forms:

1. **Native JS Event Dispatcher**:
   * Fires a native JavaScript MouseEvent (`dispatchEvent(new MouseEvent('click'))`) on `<a act_type="feedback" data-id="...">View</a>` to trigger DIKSHA's custom AJAX popup handler.

2. **Visible Popup Modal Detection**:
   * Waits up to 10s for the Feedback popup modal container (`.modal-dialog`, `.modal-content`) to become **OPEN and VISIBLE on screen**.
   * Scopes option selection strictly to `input[type='radio']:visible` inside the visible modal.

3. **Dual Confirmation Guard for Ratings & Textareas**:
   * **Tier 1 (JSON Answer Key)**: Checks Course JSON (`data/courses/*.json`) under `Module #8 ("Feedback Form")` $\rightarrow$ `Subsection ("Feedback Form")`. Selects exact saved rating or fills exact textarea paragraph response from JSON!
   * **Tier 2 (AI Live Solver)**: If a new question is encountered, Gemini AI Live Solver generates the answer and auto-saves it to Course JSON.
   * **Tier 3 (Strict Circuit Breaker)**: 0% Option [A] / `Strongly Agree` fallback. Performs stepped backoffs (30s $\rightarrow$ 45s $\rightarrow$ 60s) and triggers Circuit Breaker if rate-limited.

4. **Textarea & Open-Text Response Handling**:
   * Extracts question text from preceding `.que-no` or wrapper (e.g., `"19. What aspects of the training could be improved?"`).
   * Strips leading numbers (`"19. "`) and fills full paragraph answers into `<textarea class="form-control">`!

5. **Modal Submission**:
   * Locates and clicks the big brown **Submit Feedback** button (`button:has-text('Submit Feedback')`, `#submitFeedbackBtn11`).
   * Confirms the **100% brown checkmark** update on the course dashboard!

