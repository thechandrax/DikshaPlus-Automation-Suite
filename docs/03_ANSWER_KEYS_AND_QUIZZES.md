# 📝 Answer Keys, AI Live Solver & Auto-Learning Guide

This guide details how per-course JSON answer keys work, how the **Gemini AI Live Solver** operates, and how **Smart Auto-Learning Sequential Storage** saves questions for **DIKSHA+ Automation Suite**.

---

## 📁 1. Per-Course JSON Registry (`data/courses/`)

Each course has its own JSON file inside `data/courses/<course_name>.json`:

* `data/courses/power_of_audio_in_education.json`
* `data/courses/nishtha_fln_english.json`
* `data/courses/ai_in_education_empowering_educators_for_a_future_ready_india.json`

If a course JSON file does not exist when the bot starts, the engine auto-creates a new course JSON file and populates it sequentially as AI solves questions!

---

## 🧠 2. Gemini AI Live Solver Engine

When DIKSHA displays a question during a Formative Assessment or H5P Interactive Quiz:

1. **Step 1: Check Auto-Learning JSON Cache**:
   The engine searches all questions in the JSON file using 100% exact text matching.
   * **If Match Found**: Uses the cached target answer in **0.01 seconds**!

2. **Step 2: Gemini AI Live Solving (If Question is NEW)**:
   If the screen question is not in the JSON key, the bot passes the question text + 4 option choices to Gemini AI (`gemini-2.0-flash`).
   * **Response Time**: ~0.4 seconds.
   * **Execution**: AI selects the correct option choice text.
   * **Radio Button Click**: Engine targets the exact `<div data-region='answer-label'>` linked to the radio input (`#q15158343:1_answer1`).

---

## 💾 3. Structured Sequential Auto-Learning Storage

Whenever Gemini AI solves a new question live, the bot automatically saves the question & answer to `data/courses/<course_name>.json` using a sequential hierarchical schema:

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
  * No false index matching (`[VERIFIED INDEX 100% MATCH]` log clutter eliminated).
* **Gate 2 (Option Label Verification)**:
  * Option Prefix Stripper (removes `a.`, `b.`, `c.`, `d.`, `1.`, `2.`, `3.`, `4.`).
  * Target Radio Locator (locates `div[data-region='answer-label']` linked via `aria-labelledby` to `<input type="radio">`).
