# 📝 Answer Keys & Quizzes Guide

This guide explains how per-course JSON answer keys work and how formative assessments/quizzes are automated in **DIKSHA+ Automation Suite**.

---

## 📁 1. Per-Course JSON Registry (`data/courses/`)

Each course has its own JSON file inside `data/courses/<course_name>.json`:

* `data/courses/power_of_audio_in_education.json`
* `data/courses/nishtha_fln_english.json`
* `data/courses/ai_in_education_empowering_educators_for_a_future_ready_india.json`
* `data/courses/action_research.json`
* `data/courses/nishtha_fln_urdu.json`

If a course does not have a JSON file yet, DIKSHA+ auto-creates a template file upon scanning!

---

## ✏️ 2. Universal Hierarchical Q&A Schema (`extract_all_qa_items`)

DIKSHA+ supports clean hierarchical module and subsection grouping parsed recursively by `extract_all_qa_items()` in [automations/diksha_plus_engine.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/automations/diksha_plus_engine.py):

```json
{
  "course_name": "NISHTHA FLN English",
  "module_no": 1,
  "module_name": "Module 01: Introduction to FLN Mission",
  "subsections": [
    {
      "subsection_no": 10,
      "subsection_name": "Activity 02: Check Your Understanding",
      "questions": [
        {
          "question": "At preschool, children do not learn by play-based age and developmentally appropriate activities and material",
          "answer": "False"
        },
        {
          "question": "Development of oral language, phonological awareness, print awareness, etc., are the components of physical development at the preschool stage.",
          "answer": "False"
        }
      ]
    },
    {
      "subsection_no": 25,
      "subsection_name": "Formative Assessment 01",
      "questions": [
        {
          "question": "NCERT, as a leading academic institution in the country...",
          "answer": "Foundational literacy and numeracy"
        }
      ]
    }
  ]
}
```

---

## 🤖 3. Assessment Automation & Fallbacks

DIKSHA+ automates quizzes with multi-layered fallback resilience:

1. **Button Selectors**: Supports `Start Assessment`, `Continue Assessment`, `Re-attempt Assessment`, and `.singlebutton.quizstartbuttondiv button`.
2. **Banner Cleanup**: Auto-dismisses overlay GIF popups (`button.quiz-popup-close`).
3. **Smart Matching**: Compares clean normalized question text against Q&A entries recursively extracted from JSON.
4. **Resilient Option Clicking**: Targets input radio buttons, label `for="id"` attributes, and direct text clicks.
5. **Fallback Choice**: If a question is not in the JSON answer key, it picks Option 1 to keep progress moving forward.
6. **Automatic Final Submit**: Executes JS fallback for `Final Submit` (`AUTOMATIC_FINAL_SUBMIT = True`).
