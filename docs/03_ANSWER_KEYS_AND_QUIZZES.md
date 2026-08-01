# 📝 Answer Keys, AI Live Solver & Auto-Learning Guide

This guide details how per-course JSON answer keys work, how the **Gemini AI Multi-Key Live Solver** operates, and how **Smart Auto-Learning Sequential Storage** saves questions for **DIKSHA+ Automation Suite**.

---

## 📁 1. Per-Course JSON Registry (`data/courses/`)

Each course has its own JSON file inside `data/courses/<course_name>.json`:

* `data/courses/power_of_audio_in_education.json`
* `data/courses/online_and_digital_education_in_the_lens_of_nep_2020.json`
* `data/courses/ai_in_education_empowering_educators_for_a_future_ready_india.json`

If a course JSON file does not exist when the bot starts, the engine auto-creates a new course JSON file and populates it sequentially as AI solves questions!

---

## 🧠 2. Gemini AI Multi-Key Live Solver Engine

When DIKSHA displays a question during a Formative Assessment (`quiz`) or H5P Interactive Activity (`h5pactivity`):

1. **Step 1: Check Auto-Learning JSON Cache**:
   The engine searches all questions in the JSON file using 100% exact text matching.
   * **If Match Found**: Logged as `⚡ [VERIFIED JSON 100% MATCH Q-x]` and uses target answer in **0.01 seconds**!

2. **Step 2: Gemini AI Multi-Key Live Solving (If Question is NEW)**:
   If the screen question is not in the JSON key:
   * **3-Second Pacing Delay**: Features a smooth 3-second pacing delay to mimic human reading and prevent rate limit exhaustion.
   * **Multi-Key Failover Pool**: Evaluates `GEMINI_API_KEYS` in `config.py`. If `Key #1` hits HTTP 429 rate limit, the bot **instantly switches to Key #2**!
   * **2025/2026 Google API Standard**: Sends mandatory `x-goog-api-key` header to `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.
   * **Models Tested**: `gemini-flash-latest`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-1.5-flash`, `gemini-2.5-flash`.
   * **Radio Button Target Locator**: Engine targets exact `<div data-region='answer-label'>` linked to the radio input (`#q15158343:1_answer1`).

---

## 💾 3. Structured Sequential Auto-Learning Storage

Whenever Gemini AI solves a new question live, `save_auto_learned_qa()` automatically appends the question & answer to `data/courses/<course_name>.json` using a sequential hierarchical schema:

```json
{
  "course_name": "Power of Audio in Education",
  "module_no": 7,
  "module_name": "Assessment",
  "subsections": [
    {
      "subsection_no": 1,
      "subsection_name": "Assessment",
      "questions": [
        {
          "question": "How many community radio stations are there in India as of May 2025?",
          "answer": "500+"
        },
        {
          "question": "Why is audio well-suited for multitasking?",
          "answer": "It leaves visual attention free"
        }
      ]
    }
  ]
}
```

### Key Auto-Learning Features:
* **Preserves Module Metadata**: Captures exact `module_no`, `module_name`, `subsection_no`, and `subsection_name`.
* **Sequential Queue**: Appends new questions in the exact order they appear on screen.
* **Duplicate Prevention**: Automatically checks for existing questions before saving.

---

## 🎯 4. Dual-Pass 100% Exact Matching Architecture

* **Gate 1 (Question Verification)**:
  * 100% String Equality & 100% Word Set Equality.
  * Logged as `⚡ [VERIFIED JSON 100% MATCH Q-x]`.
* **Gate 2 (Option Label Verification)**:
  * Option Prefix Stripper (removes `a.`, `b.`, `c.`, `d.`, `1.`, `2.`, `3.`, `4.`).
  * Target Radio Locator (locates `div[data-region='answer-label']` linked via `aria-labelledby` to `<input type="radio">`).

