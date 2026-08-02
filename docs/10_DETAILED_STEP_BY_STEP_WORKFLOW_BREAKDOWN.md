# 🛠️ DIKSHA+ AUTOMATION SUITE — DETAILED STEP-BY-STEP WORKFLOW BREAKDOWN

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

```text
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                      DIKSHA+ AUTOMATION ENGINE (v2026)                          │
 └────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ 🔐 1. AUTHENTICATION & LOGIN GATEWAY   │
                      │  • Keycloak SSO Auth Redirect         │
                      │  • 256-Bit SHA-256 Multi-User Vault   │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ 📚 2. COURSE STRUCTURE & MEMORY LOCK  │
                      │  • Detects Course & Modules Count     │
                      │  • Locks ACTIVE_COURSE_TITLE in Mem   │
                      │  • Prints Subsection Checklist (✓/⏳) │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ ⚡ 3. SUBSECTION EXECUTION ENGINE      │
                      │  • Videos: Fast Watch & Auto-Play     │
                      │  • PDFs: PageDown & End Scroll        │
                      │  • H5P / Feedback: Auto Rating & Type │
                      │  • Assessments: Quiz Reset & Submit   │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ 🧠 4. DUAL-PASS SOLVING PIPELINE       │
                      │  • Pass 1: Local Course JSON Cache    │
                      │  • Pass 2: 8-Key AI Pool (5 Gem/3 Gro)│
                      │  • 0% Option A Fallback Guarantee     │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ ⏳ 5. 15s RELOAD SYNC & GATE GUARD    │
                      │  • Every 15s: Reload & Re-expand      │
                      │  • Checks: Subsections ✓ OR Header % │
                      │  • 2-Min Patient Server Hydration Window│
                      │  • Cleanly closes modal & accordion   │
                      └───────────────────┬───────────────────┘
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ 💾 6. AUTO-LEARNING & RE-USE          │
                      │  • Saves new Q&As to Course JSON      │
                      │  • Locks titles in completed_items    │
                      │  • Advances cleanly to Next Module 🚀 │
                      └───────────────────────────────────────┘
```

---

## 🛠️ EXHAUSTIVE STEP-BY-STEP TECHNICAL BREAKDOWN

### 1️⃣ STEP 1: SECURITY CLEARANCE & AUTHENTICATION (`login_diksha`)
* **SHA-256 Security PIN**: Validates user access PIN (`541563`) before initializing engine parameters.
* **Encrypted Vault Decryption**: Dynamically decrypts 256-bit AES/SHA-256 encrypted account passwords in memory (`utils/security.py`).
* **Keycloak SSO Authentication**: Navigates to `AUTH_LOGIN_URL`, fills username and password, submits Keycloak form, and waits up to 60s for server SSO redirect to `course_listing.php`.

### 2️⃣ STEP 2: COURSE HYDRATION & MEMORY LOCK (`process_course_modules`)
* **Course Title Resolution**: Extracts official course title and sets `global ACTIVE_COURSE_TITLE`. This memory lock guarantees all modules save into the exact same course JSON file (`data/courses/<course_name>.json`).
* **Module Structure Scan**: Locates main module accordion headers, deduplicates singular/plural titles, and prints a live **Subsection Breakdown Checklist**:
  ```text
  📋 [SUBSECTION BREAKDOWN (10 ITEMS)]:
     [1/10] ✓ কাৰ্যভিত্তিক গৱেষণাৰ প্ৰক্ৰিয়া
     [2/10] ⏳ কার্যভিত্তিক গৱেষণাৰ পদক্ষেপ : তথ্যৰ সংগ্ৰহ
  ```

### 3️⃣ STEP 3: SUBSECTION ACTIVITY ENGINE
* **📹 Videos (`act_type="url"`)**: Sets muted 360p resolution, accelerates playback, dispatches HTML5 `ended` events, and verifies 100% checkmarks.
* **📄 PDFs (`act_type="resource"`)**: Simulates `PageDown` page flipping, auto-scrolls PDF viewer container to exact bottom, and verifies checkmarks.
* **✍️ Feedback Forms (`is_feedback=True`)**: Auto-fills rating choices, types full paragraph answers for open-ended textareas, and submits feedback modal.
* **📝 Formative Assessments (`act_type="quiz"`)**: Dismisses inner GIF popup banners, auto-resets navigation to Question 1 (`#quiznavbutton1`), solves questions sequentially, and executes Final Submit on the Summary page.

### 4️⃣ STEP 4: DUAL-PASS SOLVING PIPELINE (`solve_question_with_ai`)
* **Pass 1 (Local JSON Cache)**: Matches exact question text against `data/courses/<course_name>.json` (`⚡ [VERIFIED JSON 100% MATCH]`).
* **Pass 2 (8-Key Multi-AI Pool)**: Rotates across **5 Gemini API Keys + 3 Groq Cloud LPU Keys** (1 attempt per key).
* **Stepped Backoff Protocol**: If rate limited, applies 30s $\rightarrow$ 45s $\rightarrow$ 60s backoff retries. **0% Option A fallback guarantee**.

### 5️⃣ STEP 5: 15-SECOND RELOAD SYNC & GATE GUARD
When a module finishes, DIKSHA+ enters a **Patient 15-Second Sync Loop**:
1. Reloads page (`page.reload()`).
2. Re-expands target module accordion (`click_target`).
3. Re-queries fresh DOM locators to unlock subsequent items immediately.
4. Verifies BOTH:
   - Are **ALL individual subsections checkmarked (`✓`)**?
   - **OR** did Module Header badge update to 100%?
5. **Clean Close**: Closes activity modal (`close_activity_modal`) and collapses module accordion before advancing to the next module!

### 6️⃣ STEP 6: AUTO-LEARNING & PERSISTENCE (`save_auto_learned_qa`)
* Newly solved Q&As are automatically appended to `data/courses/<course_name>.json` under clean `modules` $\rightarrow$ `subsections` hierarchy.
* Item titles are added to `completed_items` memory to prevent any re-execution loop.

---

## 🌐 4-WAY DEPLOYMENT ARCHITECTURE

| Mode | Platform | Environment Flags | Interface | Laptop Code Status |
| :--- | :--- | :--- | :--- | :--- |
| **Mode 1** | 💻 **Local Laptop** | `HEADLESS=False` | Visible GUI Window | **100% Preserved** ✅ |
| **Mode 2** | ☁️ **Railway Server** | `HEADLESS=True` | Background Container | **100% Preserved** ✅ |
| **Mode 3** | 📱 **Railway Mobile** | `HEADLESS=True` | Smartphone Web Browser | **0% Battery Drain** 🔋 |
| **Mode 4** | 📲 **Termux App** | `IS_TERMUX=True` | Android Native Terminal | **100% Supported** ✅ |
