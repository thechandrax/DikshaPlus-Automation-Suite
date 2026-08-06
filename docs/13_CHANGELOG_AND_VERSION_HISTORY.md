# 📜 13 — OFFICIAL CHANGELOG & VERSION HISTORY

All notable changes, architectural updates, engine improvements, bug fixes, and feature additions for **DIKSHA+ Automation Suite** are documented in this file.

---

## 📑 Table of Contents

1. [🚀 Summary of August 6, 2026 Release](#-summary-of-august-6-2026-release)
2. [🚀 Summary of August 4, 2026 Release](#-summary-of-august-4-2026-release)
3. [🚀 Summary of August 3, 2026 Release](#-summary-of-august-3-2026-release)
4. [🕒 Timelines & Detailed Technical Feature Breakdown](#-timelines--detailed-technical-feature-breakdown)
5. [🌐 Commit Log History](#-commit-log-history)

---

## 🚀 Summary of August 6, 2026 Release

Today's release delivers **6 critical bug fixes and new features** across the engine, main entry point, and course data:

* **Bug Fix — Certificate Accordion Not Expanded Before Feedback (Critical):** The certificate section handler called `process_certificate_feedback()` before expanding the accordion panel. The Give Feedback button inside the collapsed panel was invisible — `count() == 0` — causing silent feedback skip every time. Fixed by adding a dedicated `aria-expanded` check and `click(force=True)` panel expansion (2.5s wait) BEFORE calling the feedback function.
* **New — Step 7: Close "Feedback Submitted Successfully" Modal:** After AJAX submit, DIKSHA shows a success popup. Engine now automatically closes it using `a.close[data-dismiss='modal']` selector with `Escape` key fallback. Works in both Scenario A and Scenario B.
* **Bug Fix — open_activity_popup: `is_visible()` Caused Wrong Button Selection:** When resolving `li.action123 a[act_id='X']`, if the button was scrolled out of viewport, `is_visible()` returned `False` and fell back to the outer bare button (no event handler). This caused `[MODAL NOT DETECTED]` on every first click for PDF/Video activities. Fixed by removing the `is_visible()` check — `safe_action_click()` handles scroll automatically. First-click wait increased from 3s → 5s.
* **New — main.py: 3-Attempt Auto-Reconnect Session Loop:** Replaced plain `asyncio.run()` with a `for s_attempt in range(1, 4)` retry loop. Detects all Playwright disconnect errors (`connection closed`, `target closed`, `browser has been closed`, `websocket`, `pipe closed`). On disconnect: cleans stale `*Singleton*` Chrome lock files → sleeps 3s → restarts fresh Chrome session automatically. Non-browser errors break immediately (no retry).
* **Bug Fix — Module Sync Attempt Counter Label:** Subsection breakdown and re-execution log messages showed `/10` (old value) but the `for sync_step in range(1, 4)` loop only runs 3 times. Fixed both labels to correctly show `/3`.
* **Course JSON Data Merge:** Merged all answer key data from old `C:\UDISE [GM]\courses` into new `data\courses` folder. Copied 2 missing files (`Action_Research.json`, `Catch_the_Rain.json`). Deep-merged `NISHTHA_FLN_English.json` (7 missing modules + 3 subsections added, 13.8 KB → 300 KB) and `NISHTHA_ECCE_English.json` (3 missing modules added, 38.7 KB → 161.1 KB). Zero duplicates verified.

---

## 🚀 Summary of August 4, 2026 Release

Today's release delivers major reliability enhancements to **DIKSHA+ Automation Engine**:
* **Prerequisite Unlock Engine (`is_item_locked_by_diksha`)**: Auto-detects DIKSHA server prerequisite locks (`"Not available unless..."`), re-triggers prior incomplete items, and reloads the page to hydrate checkmarks so next buttons unlock immediately on screen.
* **Accordion Expansion Guard**: Ensures that page reloads during `sync_step` automatically re-expand collapsed module accordion panels (`Module 01: 72%`), rendering inner action buttons for instant completion.
* **Clean Log Output Standardization**:
  * 2-Digit Zero-Padding across all module and breakdown indexes (`[01/32]`, `[01/15]`).
  * 3-Tier Percentage Color Scheme (`100%` Neon Green, `1-99%` Electric Cyan, `0%` Amber Orange).
  * Single-Row Title Truncation (`...`) for titles > 52 characters.
  * Sleek `[Attempt 1/3]` subsection header format.
  * Single-Row `[✓ ALREADY DONE] SUBSECTION [02/26]: ... [Skipping!]` lines.
* **Keyboard Listener Clean Removal**: Removed redundant keyboard hotkey listener (`'P'` / Spacebar) with surgical precision, ensuring 100% hands-free background execution without accidental terminal pauses.
* **Exact Working Backup Logic Verified**: Validated bit-for-bit identity of core activity routines (`process_pdf_activity`, `process_video_activity`, `process_h5p_activity`, `process_quiz_assessment`, `process_feedback_activity`, `safe_action_click`, `close_activity_modal`) against August 3 working backup.

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

### 19. 🔢 2-Digit Zero-Padding Format Across All Modules & Log Indexes (`23:47:00 IST`)
* **Standardized 2-Digit Padding**: Module list indexes and subsection breakdown indexes now use 2-digit zero-padding (`[01/15]`, `[02/15]`, `[09/15]`, `[10/15]`, `[15/15]`).
* **Clean Alignment**: Ensures all breakdown lines align perfectly in terminal output.

### 20. 🎨 3-Tier Percentage Color System & Title Truncation (`23:32:00 IST`)
* **3-Tier Percentage Colors**:
  * **`100%`**: Vibrant Neon Green (`\033[38;5;82m`).
  * **`1-99%`**: Electric Cyan (`\033[38;5;51m`).
  * **`0%`**: Amber Red-Orange (`\033[38;5;208m`).
* **Title Truncation (`...`)**: Titles longer than 52 characters are truncated with `...` to guarantee 100% single-row lines without wrapping.

### 21. 🛡️ Strict Item Completion & Parent Class Filter (`23:22:00 IST`)
* **Eliminated False-Positive Skips**: Removed generic `[class*='completed']` matcher to prevent parent container CSS classes from falsely skipping transcript items.

## 🌐 Commit Log History (August 4, 2026)

| Commit Hash | Time (IST) | Description |
| :--- | :--- | :--- |
| **`53561dd`** | `01:35:41` | Feature: Cleanly remove keyboard pause listener while preserving 100% of all activity execution and course pipeline code |
| **`d817fb0`** | `01:18:13` | Fix: Add accordion expansion guard to sync_step so page reload re-expands collapsed module panels to click remaining items |
| **`8a45f3e`** | `01:13:46` | Docs: Save latest NISHTHA ECCE English course metadata and verified pipeline state |
| **`4c20d56`** | `01:08:03` | Fix: Re-trigger prior prerequisite item and reload page when a locked item is detected so DIKSHA unlocks next buttons immediately |
| **`0f9056a`** | `01:04:39` | Fix: Add is_item_locked_by_diksha helper to detect DIKSHA prerequisite rules ('Not available unless...') and skip locked items without scrolling down |
| **`74a8de5`** | `00:53:09` | Fix: Restore exact working safe_action_click and close_activity_modal implementation from user 03.08.26 backup folder |
| **`69e0e27`** | `00:48:53` | Fix: Restore clean human-like safe_action_click logic to trigger standard DOM mouse events like manual clicks |
| **`639a982`** | `00:41:47` | Fix: Add popup verification and parent row element click trigger to safe_action_click to guarantee PDF items open on screen |
| **`83cad94`** | `00:37:38` | Fix: Pre-click modal backdrop clearance and multi-dispatch fallback in safe_action_click to guarantee PDF/resource items open on click |
| **`39591ff`** | `00:36:05` | Fix: Multi-frame close button selector and native Bootstrap jQuery modal dismissal engine to resolve PDF modal close freezing |
| **`d3b93be`** | `00:30:03` | Fix: Add optional page=None parameter to check_pause_status to eliminate TypeError during video fast-forward playback loops |
| **`87fe41f`** | `00:27:21` | Feature: Format subsection log label as [Attempt 1/3] without # symbol as requested |
| **`ce05c69`** | `00:24:40` | Feature: Increase max module attempts to 3 and format subsection log label as [Attempt #1/3] as requested |
| **`dcf7683`** | `00:21:06` | Feature: Update subsection header log label from [Pass #1] to [Attempt #1] as requested |
| **`607bcbd`** | `00:00:38` | Feature: Format ALREADY DONE log lines on single row with title truncation (...), uppercase SUBSECTION, and bracketed [Skipping!] as requested |

## 🌐 Commit Log History (August 4, 2026)

| Commit Hash | Time (IST) | Description |
| :--- | :--- | :--- |
| **`659e5a7`** | `02:52:21` | Feature: Universal `open_activity_popup` for all View buttons (PDF, Video, H5P, Quiz, Feedback) with clean `[DOUBLE-TRIGGER POPUP]` log format |
| **`029ea37`** | `02:43:46` | Feature: Add `ensure_on_course_page` Automatic Dashboard Recovery Guard to re-navigate to course URL if Chrome lands on `dashboard.php` |
| **`92c8e44`** | `02:41:04` | Fix: Enhance `safe_action_click` with native JS bubble dispatch and add double-trigger title link fallback to guarantee assessment modal opens |
| **`aa8eb47`** | `02:36:31` | Docs: Add explicit `CLICKED VIEW BUTTON` log line to `process_quiz_assessment` to confirm View button click |
| **`101ca63`** | `02:34:41` | Fix: Restrict Final Submit JS fallback to quiz frames only to eliminate accidental redirects to `dashboard.php` |
| **`1d2056d`** | `02:30:17` | Feature: Enhance post-submission flow with Continue/Finish click, 5s server checkmark sync buffer, and modal dismissal before opening next section/module |
| **`1ae9181`** | `02:26:00` | Feature: Add 5-second popup pre-load buffer, instruction modal dismissal, and 5-second quiz iframe pre-load buffer to quiz assessment engine |

---

## 🌐 Commit Log History (August 3, 2026)



| Commit Hash | Time (IST) | Description |
| :--- | :--- | :--- |
| **`36c4dfa`** | `23:47:53` | Feature: Format course module list numbers with 2-digit zero-padding as [01/15], [02/15], [09/15], [10/15] as requested |
| **`42c9622`** | `23:45:15` | Fix: Remove trailing word boundary in percentage regex to guarantee 100% (Neon Green), 1-99% (Electric Cyan), and 0% (Amber Orange) color rendering |
| **`f1eea12`** | `23:33:07` | Feature: Add title truncation (...) for titles > 52 chars to enforce 100% single-row lines, and 3-tier percentage colors (100% Green, 1-99% Electric Cyan, 0% Amber Orange) |
| **`cb23fd3`** | `23:29:59` | Feature: Add vibrant Amber Red-Orange ANSI color highlighting for 0% percentage badges and Golden Hour colors for ⏳ icons in utils/logger.py |
| **`b09aeec`** | `23:35:16` | Feature: Format breakdown item numbers with 2-digit zero-padding as [01/32], [02/32], [09/32], [10/32] as requested |
| **`1639d33`** | `23:22:32` | Fix: Remove generic parent container class matching in is_item_100_percent_complete to eliminate false-positive skipping of Transcript items |
| **`bd5206d`** | `22:49:38` | Fix: Enhance get_real_subsection_title with 3-layer item row text extraction to ensure 100% of items display exact full title names |
| **`4b26eb1`** | `22:04:52` | Docs: Update docs/13_CHANGELOG_AND_VERSION_HISTORY.md with latest August 3, 2026 commits up to 5fa9687 |
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
## 🌐 Commit Log History (August 6, 2026)

| Commit Hash | Time (IST) | Description |
| :--- | :--- | :--- |
| **`901af56`** | `20:13:20` | Update: Set pre-click hydration buffer to 3s and format clean log line in open_activity_popup |
| **`0a26e74`** | `20:04:36` | Update: Set 5s polling interval and format exact log lines for open_activity_popup as requested |
| **`8378fb1`** | `20:08:52` | Feature: Add 5-second pre-click hydration buffer before clicking activity item title link or View button in open_activity_popup |
| **`967e45a`** | `19:45:13` | Feature: Add YouTube Weblinks Blocker, DOM Link Neutralizer, and Auto-Recovery Guard to prevent accidental external YouTube navigation on Weblinks resources |
| **`836d5c6`** | `19:23:55` | Fix: Simultaneously trigger both Item Title Link and View button on first click in open_activity_popup to guarantee 100% first-click modal opening |
| **`ee3d8e6`** | `19:20:14` | Feature: Perfect 5-Star Emoji Rating card selection ('Excellent' 😃) and clean logging for DIKSHA 'Share your Feedback' popup modal |
| **`37fece7`** | `19:14:47` | Feature: Enhance Feedback Rating Selector to dynamically support both 3-Star and 5-Star systems, Emoji cards, and Radio choices |
| **`cde504b`** | `19:02:20` | Update: Display exact model name in Gemini rate limit log warnings while preserving full multi-model retry sequence |
| **`2e15f4d`** | `18:57:52` | Fix: Break early on Gemini rate limit per key to eliminate duplicate log warning lines and switch immediately to Groq LPU API |
| **`e0f4208`** | `18:52:27` | Feature: Add Auto-Save Quality Guard in save_auto_learned_qa to reject saving questions with duplicate or near-identical options into JSON memory |
| **`2d1fbda`** | `18:50:17` | Data: Deep scan and delete 5 malformed questions with duplicate/near-identical options across NISHTHA ECCE and FLN course memory files |
| **`14ee3e8`** | `18:44:13` | Data: Organize, deduplicate, and sort all course JSON files in numerical module order (Module 01, 02, 03...) without UTF-8 BOM |
| **`1918f1d`** | `18:39:14` | Fix: Prioritize exact <li class='action123'> <a class='module-view-btn'> button element in get_section_action_buttons to ensure first-click success on View buttons |
| **`a5a8008`** | `18:36:20` | Feature: Add 500ms fast modal polling window and expanded PDF player selectors (.sunbird-pdf-player, #resource_iframe, etc.) to open_activity_popup |
| **`6e71674`** | `18:31:15` | Fix: Fully restore complete Dual-Scan Feedback Engine supporting both Automatic Popups and Manual 'Give Feedback' Button clicks with Emoji 5-Star Card Selection |

---



