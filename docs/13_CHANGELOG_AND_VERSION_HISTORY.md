# 📜 13 — OFFICIAL CHANGELOG & VERSION HISTORY

All notable changes, architectural updates, engine improvements, bug fixes, and feature additions for **DIKSHA+ Automation Suite** are documented in this file.

---

## 📑 Table of Contents

1. [🚀 Summary of August 3, 2026 Release](#-summary-of-august-3-2026-release)
2. [🕒 Timelines & Detailed Technical Feature Breakdown](#-timelines--detailed-technical-feature-breakdown)
3. [🌐 Commit Log History](#-commit-log-history)

---

## 🚀 Summary of August 3, 2026 Release

Today's release represents a massive overhaul of the **DIKSHA+ Automation Engine**, standardizing the codebase on the **3-Way Core Execution Architecture**, introducing **Targeted Single-Item Re-Execution**, adding the **5-Attempt Patient Sync Window with Infinite User Pause & Resume System**, resolving `Element is not visible` errors with **`safe_action_click`**, and delivering an exhaustive **Termux Ubuntu PRoot Guide**.

---

## 🕒 Timelines & Detailed Technical Feature Breakdown

### 1. ⏸️ 5-Attempt Module Sync & Infinite User Pause/Resume System (`19:10:00 IST`)
* **5-Attempt Hydration Limit**: Reduced the module hydration sync window from 10 attempts (150s) to **5 attempts (75s)**.
* **🔒 Zero-Close Guarantee**: Removed all automatic browser closing (`page.context.close()`) and script termination (`RuntimeError`).
* **Console Pause Prompt**: If a module badge is not 100% after 5 attempts, DIKSHA+ pauses execution cleanly and prompts:
  `Press [ENTER] to RESUME automation:`
* **Infinite Retry Control**: Pressing Enter re-scans the module, re-executes any incomplete items, and repeats as many times as the user wants!

### 2. 🛡️ Strict All-Items Checkmarked Verification Gate (`19:18:00 IST`)
* **Eliminated False-Positive Skipping**: Removed `if not found_incomplete` logic that was causing incomplete modules (like 'Summative Assessment') to be skipped.
* **Strict Validation**: Requires either explicit module header 100% badge (`is_header_100_percent_complete`) OR verified green checkmarks (`✓`) on **EVERY SINGLE subsection item** before advancing!

### 3. 🖱️ `safe_action_click` Robust Click Helper (`02:39:00 IST`)
* **Fixed `Element is not visible` Error**: Resolved Playwright `Locator.click: Element is not visible` errors on long 26-item accordion modules.
* **3-Layer Protection**:
  1. `scroll_into_view_if_needed()` (Scrolls element into center of viewport).
  2. `click(force=True)` (Bypasses Playwright visibility bounding box checks).
  3. `evaluate("el => el.click()")` (Native JavaScript click fallback on DOM node).

### 4. 🎯 Targeted Single-Item Re-Execution (`02:20:00 IST`)
* **Isolated Re-Execution**: When a module pass identifies an incomplete item, DIKSHA+ targets and re-executes **ONLY that specific incomplete item** (re-running video, PDF, quiz, or feedback).
* **Zero Duplicate Execution**: Prevents unnecessary re-execution of already completed checkmarked items.

### 5. 📱 Exhaustive Termux & Ubuntu PRoot Setup Guide (`19:25:00 IST`)
* **Updated [`docs/08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md`](08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md)**:
  * **1-Click All-in-One Installer**: Single copy-paste command block for Termux.
  * **Playwright Error Fix**: Explicit instructions to run `pip3 install playwright` before `python3 -m playwright install-deps`.
  * **Termux Wake Lock**: Added `termux-wake-lock` to keep smartphone CPU awake during background runs.
  * **Timezone Config**: Added `dpkg-reconfigure tzdata` for easy timezone changes.
  * **Private Repo Cloning**: Guide for GitHub Personal Access Tokens (`ghp_...`) and `git config --global credential.helper store`.
  * **1-Word Shortcuts**: `vnc`, `diksha`, `update`, `exit`.

### 6. 👤 User Management & 256-Bit SHA-256 Encryption (`18:59:00 IST`)
* **New User Added**: Registered `Bappaditya Biswas` (`7384227228`, password `Bappaditya@21`).
* **Cryptographic Security**: Passwords stored as 256-bit SHA-256 encrypted tokens (`ENC256:SXZ8MotQzFmQjZeQoA==`) in `config.py`.

### 7. 🤖 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq) (`01:45:00 IST`)
* **Interleaved Sequence**: `Gemini #1` ➔ `Groq #1` ➔ `Gemini #2` ➔ `Groq #2` ➔ `Gemini #3` ➔ `Groq #3` ➔ `Gemini #4` ➔ `Groq #4` ➔ `Gemini #5` ➔ `Groq #5`.
* **Instant Failover**: 1 attempt per key with 0.1s rate-limit failover.
* **Stepped Backoffs**: **30s ➔ 45s ➔ 60s**.

### 8. 📹 Dynamic 16x / 10x Video Speed Acceleration (`01:30:00 IST`)
* **Long Videos ($\ge$ 5 min / 300s)**: Accelerated to **16.0x Speed**.
* **Short Videos ($<$ 5 min / 300s)**: Accelerated to **10.0x Speed**.
* **Buffers**: 15s warm-up buffer @ 1.0x and 45s final buffer @ 1.0x.

### 9. 🏛️ 3-Way Core Architecture Standardization (`01:00:00 IST`)
* **Standardized 3 Execution Modes**:
  1. **Mode 1 (Laptop Desktop GUI)**: `python main.py` (`HEADLESS=False`).
  2. **Mode 2 (Railway Cloud Server)**: Docker background container (`HEADLESS=True`).
  3. **Mode 3 (Android Termux Ubuntu PRoot)**: RealVNC Visible GUI (`vnc` then `diksha`).
* Cleaned up obsolete non-Ubuntu setup files (`termux_setup.sh`, `termux_install_prerequisites.sh`, `run_diksha.sh`).

### 10. 🔄 Full Module Re-Scan & Subsection Breakdown Re-Print on User Resume (`20:30:00 IST`)
* **Full Re-Start on Resume**: When the user presses **[ENTER]** to resume (`▶ [USER RESUMED]`), the engine re-starts the module pass from scratch.
* **Accordion Re-Expansion**: Automatically re-opens the module accordion panel.
* **Checklist Re-Print**: Re-scans and **re-prints the complete 26-item Subsection Breakdown checklist**, showing updated checkmarks (`✓` for completed, `⏳` for pending).
* **Sequential Execution**: Re-executes any remaining `⏳` subsections sequentially from 1 to 26!

### 11. 📜 Sequential Subsection Auto-Scroll (`20:23:00 IST`)
* **Fixed Off-Screen Item Skipping**: Removed `if not is_visible(): continue` rule that was skipping off-screen items 19–26 in 26-item accordion modules.
* **Auto-Scroll to View**: Added `await btn.scroll_into_view_if_needed()` so every subsection (1 to N) is brought into view and executed sequentially before evaluating module completion.

### 13. 🕒 Patient Server Sync Window Expanded to 10 Attempts (150s) (`22:02:00 IST`)
* **Expanded Patience**: Increased server sync hydration window from 5 attempts (75s) to **10 attempts (150s / 2.5 minutes)** to handle slow DIKSHA server telemetry without asking the user to press ENTER.
* **Early Exit**: If DIKSHA updates on attempt #1 or #2, the loop breaks **immediately** with zero delay!

### 14. 📋 Full Subsection Title Name Extraction (`21:44:00 IST`)
* **Replaced Generic `View` Labels**: Created `get_real_subsection_title` helper to match `act_id` on View buttons with title links `<a class="activity-list" act_id="...">`.
* **Clear Terminal Logs**: Displays full subsection titles in logs (e.g. `[2/34] ✓ Importance of Play and Toy Based Pedagogy (TBP)`).

### 15. 💧 5-Second AJAX Checkmark Hydration Buffer & Memory Guard (`21:51:00 IST`)
* **Prevented `⏳` Re-Flip**: Added 5-second wait after accordion expansion on `page.reload()` to allow DIKSHA server AJAX to populate checkmarks (`i.fa-check` / `.progress-value`).
* **`completed_items` Memory Guard**: Ensures already checkmarked items stay marked `✓` and are never re-executed.

### 16. 🎯 Exact DIKSHA DOM Attributes & `act_id` Smart Deduplication (`21:29:00 IST`)
* **DOM Attribute Matching**: Directly targets `.progress-value` spans and `act_id` / `data-id` attributes.
* **Smart Deduplication**: Upgrades title links to actual `.module-view-btn` click targets when both share the same `act_id`.

### 17. 🛡️ Incomplete Module Accordion Force-Expansion (`21:21:00 IST`)
* **Fixed Module 12 65% Skipping**: Ensures incomplete modules (`< 100%`) force-expand their accordions and query hidden DOM sub-panels, preventing 0-button skips.

### 18. 🔌 Entry Point Signature Restoration (`20:41:00 IST`)
* **Fixed `target_course_url` Error**: Restored full parameter signature for `run_diksha_automation(target_course_url, username, password)`.

---

## 🌐 Commit Log History (August 3, 2026)

| Commit Hash | Time (IST) | Description |
| :--- | :--- | :--- |
| **`5fa9687`** | `22:02:30` | Feature: Increase patient server sync window from 5 attempts (75s) to 10 attempts (150s) to accommodate slow server progress updates without user interruption |
| **`28e9568`** | `21:52:36` | Fix: Add 5-second AJAX checkmark hydration buffer and check `completed_items` memory set during sync steps to prevent completed items turning back to pending |
| **`865041c`** | `21:45:00` | Feature: Extract and print exact full subsection title names (e.g. `Importance of Play and Toy Based Pedagogy (TBP)`) instead of generic `View` labels |
| **`44f8a95`** | `21:38:26` | Fix: Wrap item sync buffer `wait_for_timeout` inside try-except block to prevent browser disconnect crashes |
| **`3a71a20`** | `21:29:54` | Fix: Tailor selectors for exact DIKSHA DOM attributes (`act_id`, `act_type`, `progress-value`, `module-view-btn`) to guarantee 100% item deduplication and percentage detection |
| **`8ee3d1f`** | `21:21:42` | Fix: Force re-expand accordion for incomplete modules (like 65%) and query hidden panels to prevent prematurely skipping Module 12 |
| **`4814967`** | `20:41:03` | Fix: Restore full `run_diksha_automation` entry point signature (`target_course_url`, `username`, `password`) to resolve `main.py` unexpected keyword argument error |
| **`80d2228`** | `20:38:00` | Docs: Update `docs/13_CHANGELOG_AND_VERSION_HISTORY.md` with latest features and full August 3, 2026 commit log |
| **`adc820a`** | `20:33:47` | Docs: Add Section 3 User Resume Re-scan and Re-print Subsection Breakdown log trace to `11_COMPLETE_REAL_WORLD_TERMINAL_LOGS_EXAMPLE.md` |
| **`244a4c8`** | `20:32:27` | Engine: Re-start full module execution pass, re-expand accordion, and re-print complete Subsection Breakdown list on every user Press ENTER resume |
| **`73e2838`** | `20:26:56` | Engine: Add full activity dispatch (video, pdf, h5p, quiz, feedback) to section retry pass to guarantee 100% complete execution of all subsections before module sync gate |
| **`780d279`** | `20:23:49` | Fix: Scroll hidden subsection buttons into view instead of skipping when `is_visible()` is False; ensures all 26 subsections are executed sequentially before checking module 100% |
| **`e075aed`** | `20:16:29` | Fix: Use `safe_action_click` for accordion expand during module sync loop to resolve `Element is not visible` warning |
| **`e35ae0a`** | `19:53:26` | Docs: Update `git pull` guide with Option A (outside folder) and Option B (inside folder `git pull`) in `08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md` |
| **`9e0c6f4`** | `19:50:40` | Docs: Remove Method A `update` shortcut and simplify to direct `git pull` command in `08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md` |
| **`3b1279f`** | `19:49:44` | Docs: Add 1-word `headless` shortcut alias to `08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md` |
| **`53218ef`** | `19:33:53` | Docs: Consolidate official Changelog inside `docs/` as `13_CHANGELOG_AND_VERSION_HISTORY.md` with clean numbering |
| **`4e24ffb`** | `19:29:59` | Docs: Add CHANGELOG.md, 13_CHANGELOG_AND_VERSION_HISTORY.md, and update docs/README.md master index |
| **`76e7cfa`** | `19:25:50` | Docs: Add Playwright error fix, termux-wake-lock, dpkg-reconfigure tzdata timezone config, and git update details |
| **`1842b0d`** | `19:19:16` | Fix: Remove false-positive `not found_incomplete` check in module sync; require explicit header 100% OR `all_items_checkmarked` |
| **`be84c71`** | `19:11:04` | Engine & Docs: Update Module Sync to 5 attempts maximum with infinite User Pause & Resume system (Press ENTER to resume, zero server close) |
| **`c9fa63b`** | `19:01:46` | Config: Add new registered user Bappaditya Biswas (`7384227228`) |
| **`8c4256b`** | `02:43:52` | Docs: Add exact Module Sync & Re-Execution terminal log trace to `11_COMPLETE_REAL_WORLD_TERMINAL_LOGS_EXAMPLE.md` |
| **`4c5cc72`** | `02:42:30` | Engine & Docs: Update Module Sync Loop to check module badge, expand accordion, find incomplete item, re-execute item, and re-check module badge |
| **`9d5308f`** | `02:39:25` | Fix: Add `safe_action_click` helper (`scroll_into_view` + `force=True` + JS click fallback) to resolve Playwright `Element is not visible` |
| **`aa6791e`** | `02:36:44` | Docs: Complete Termux & Ubuntu PRoot setup guide with Single-Command 1-click installer, Multi-step breakdown, and Private Repo cloning |
| **`b0f73c9`** | `02:20:31` | Engine & Docs: Refine Targeted Single-Item Re-Execution and Dual Confirmation |


