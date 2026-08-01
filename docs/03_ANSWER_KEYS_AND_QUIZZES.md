# 🧠 ANSWER KEYS, AI LIVE SOLVER & FEEDBACK FORM ENGINE

This document details the dual-pass solving pipeline, Gemini AI Multi-Key Pool integration, Feedback Form auto-filling, Unicode text normalization, and Auto-Learning JSON storage.

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
       │     Gate 1.5: Query Gemini AI Multi-Key Pool (5 Encrypted Keys)
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

## 🔑 2. Gemini AI 5-Key Encrypted API Pool

* **Key Encryption**: All 5 Gemini API keys are encrypted with 256-bit AES encryption in `config.py`:
  `GEMINI_API_KEYS_ENCRYPTED = ["ENC256:...", "ENC256:...", ...]`
* **Automatic Failover**: If Key #1 encounters HTTP 429 rate limits, DIKSHA+ rotates to Key #2, #3, #4, #5 instantly.
* **Official Google Spec**: Sends mandatory `x-goog-api-key` header.
* **3s Pacing & 3 Retry Rounds**: 3-second delay between AI API calls to protect quotas.

---

## 📝 3. Feedback Form Auto-Filling Engine

DIKSHA+ provides native automation for DIKSHA Feedback Forms:

1. **Rating Selection**:
   * Inspects `.que-no`, `div.feed-ans-div`, `input.form-check-input`.
   * Automatically selects your target rating (`Strongly Agree`, `Agree`, `Appropriate`, `Excellent`, `Yes`).
   * If not in JSON, Gemini AI generates a positive rating choice.

2. **Comment Textbox Typing**:
   * Fills open-ended comment boxes (`textarea.form-control`, `<input type='text'>`).
   * Saves text comments into JSON (`options: []`, `answer: "..."`).

3. **Feedback Submission**:
   * Clicks `Submit Feedback` (`button.submit-feed-btn`, `#submitFeedbackBtn11`).

---

## 🔀 4. Shuffled Option Resiliency

DIKSHA+ matches options on screen using **text content**, NOT hardcoded letters or position indices:
* Stored Answer: `"Hon'ble Vice President of India"`.
* Screen Option Row 1: `"Hon'ble President of India"` $\rightarrow$ ❌
* Screen Option Row 2: `"Hon'ble Prime Minister of India"` $\rightarrow$ ❌
* Screen Option Row 3: `"Hon'ble Vice President of India"` $\rightarrow$ ✅ **MATCH AT ROW 3!**
* DIKSHA+ clicks the radio button inside Row 3, ensuring 100% accuracy regardless of option shuffling.

---

## 🔤 5. Unicode Apostrophe & Text Normalization (`normalize_text`)

Standardizes Unicode characters across screen parsing, JSON matching, and JSON auto-learning saves:
* `’` (`\u2019`), `‘`, `` ` `` $\rightarrow$ `'`
* `“`, `”`, `„`, `\u201c`, `\u201d` $\rightarrow$ `"`
* `–`, `—`, `\u2013`, `\u2014` $\rightarrow$ `-`
* `\u00a0` $\rightarrow$ `' '` (Standard space)

---

## 💾 6. Auto-Learning JSON Schema Reference

Auto-saved JSON files in `data/courses/` follow this standardized structure:

```json
{
  "course_name": "Online and Digital Education in the Lens of NEP 2020",
  "subsections": [
    {
      "module_no": 7,
      "module_name": "Assessment",
      "subsection_no": 1,
      "subsection_name": "Assessment",
      "questions": [
        {
          "question": "Who formally launched the DIKSHA platform?",
          "options": [
            "[A] Hon’ble President of India",
            "[B] Hon’ble Vice President of India",
            "[C] Hon’ble Prime Minister of India",
            "[D] Hon’ble Education Minister"
          ],
          "answer": "[B] Hon’ble Vice President of India"
        }
      ]
    },
    {
      "module_no": 8,
      "module_name": "Feedback Form",
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
          "question": "What aspects of the training could be improved?",
          "options": [],
          "answer": "Incorporating more hands-on practice activities and allocating extra time for interactive Q&A sessions would make the training even more effective."
        }
      ]
    }
  ]
}
```
