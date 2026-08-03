# 📜 DIKSHA+ AUTOMATION SUITE — OFFICIAL CHANGELOG & VERSION HISTORY

All notable changes, architectural updates, engine improvements, bug fixes, and feature additions for **DIKSHA+ Automation Suite** are documented in this file.

---

## 📅 [v2026.08.03] — 2026-08-03 (MAJOR SYSTEM UPGRADE & DOCUMENTATION RESTRUCTURE)

### 🚀 Summary of Today's Enhancements (August 3, 2026)

Today's release represents a massive overhaul of the **DIKSHA+ Automation Engine**, standardizing the codebase on the **3-Way Core Execution Architecture**, introducing **Targeted Single-Item Re-Execution**, adding the **5-Attempt Patient Sync Window with Infinite User Pause & Resume System**, resolving `Element is not visible` errors with **`safe_action_click`**, and delivering an exhaustive **Termux Ubuntu PRoot Guide**.

---

### 🕒 Detailed Timelines & Feature Breakdown

#### 1. ⏸️ 5-Attempt Module Sync & Infinite User Pause/Resume System (`19:10:00 IST`)
* **5-Attempt Hydration Limit**: Reduced the module hydration sync window from 10 attempts (150s) to **5 attempts (75s)**.
* **🔒 Zero-Close Guarantee**: Removed all automatic browser closing (`page.context.close()`) and script termination (`RuntimeError`).
* **Console Pause Prompt**: If a module badge is not 100% after 5 attempts, DIKSHA+ pauses execution cleanly and prompts:
  `Press [ENTER] to RESUME automation:`
* **Infinite Retry Control**: Pressing Enter re-scans the module, re-executes any incomplete items, and repeats as many times as the user wants!

#### 2. 🛡️ Strict All-Items Checkmarked Verification Gate (`19:18:00 IST`)
* **Eliminated False-Positive Skipping**: Removed `if not found_incomplete` logic that was causing incomplete modules (like 'Summative Assessment') to be skipped.
* **Strict Validation**: Requires either explicit module header 100% badge (`is_header_100_percent_complete`) OR verified green checkmarks (`✓`) on **EVERY SINGLE subsection item** before advancing!

#### 3. 🖱️ `safe_action_click` Robust Click Helper (`02:39:00 IST`)
* **Fixed `Element is not visible` Error**: Resolved Playwright `Locator.click: Element is not visible` errors on long 26-item accordion modules.
* **3-Layer Protection**:
  1. `scroll_into_view_if_needed()` (Scrolls element into center of viewport).
  2. `click(force=True)` (Bypasses Playwright visibility bounding box checks).
  3. `evaluate("el => el.click()")` (Native JavaScript click fallback on DOM node).

#### 4. 🎯 Targeted Single-Item Re-Execution (`02:20:00 IST`)
* **Isolated Re-Execution**: When a module pass identifies an incomplete item, DIKSHA+ targets and re-executes **ONLY that specific incomplete item** (re-running video, PDF, quiz, or feedback).
* **Zero Duplicate Execution**: Prevents unnecessary re-execution of already completed checkmarked items.

#### 5. 📱 Exhaustive Termux & Ubuntu PRoot Setup Guide (`19:25:00 IST`)
* **Updated [`docs/08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md`](docs/08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md)**:
  * **1-Click All-in-One Installer**: Single copy-paste command block for Termux.
  * **Playwright Error Fix**: Explicit instructions to run `pip3 install playwright` before `python3 -m playwright install-deps`.
  * **Termux Wake Lock**: Added `termux-wake-lock` to keep smartphone CPU awake during background runs.
  * **Timezone Config**: Added `dpkg-reconfigure tzdata` for easy timezone changes.
  * **Private Repo Cloning**: Guide for GitHub Personal Access Tokens (`ghp_...`) and `git config --global credential.helper store`.
  * **1-Word Shortcuts**: `vnc`, `diksha`, `update`, `exit`.

#### 6. 👤 User Management & 256-Bit SHA-256 Encryption (`18:59:00 IST`)
* **New User Added**: Registered `Bappaditya Biswas` (`7384227228`, password `Bappaditya@21`).
* **Cryptographic Security**: Passwords stored as 256-bit SHA-256 encrypted tokens (`ENC256:SXZ8MotQzFmQjZeQoA==`) in `config.py`.

#### 7. 🤖 10-Key Interleaved Alternating AI Pool (5 Gemini + 5 Groq) (`01:45:00 IST`)
* **Interleaved Sequence**: `Gemini #1` ➔ `Groq #1` ➔ `Gemini #2` ➔ `Groq #2` ➔ `Gemini #3` ➔ `Groq #3` ➔ `Gemini #4` ➔ `Groq #4` ➔ `Gemini #5` ➔ `Groq #5`.
* **Instant Failover**: 1 attempt per key with 0.1s rate-limit failover.
* **Stepped Backoffs**: **30s ➔ 45s ➔ 60s**.

#### 8. 📹 Dynamic 16x / 10x Video Speed Acceleration (`01:30:00 IST`)
* **Long Videos ($\ge$ 5 min / 300s)**: Accelerated to **16.0x Speed**.
* **Short Videos ($<$ 5 min / 300s)**: Accelerated to **10.0x Speed**.
* **Buffers**: 15s warm-up buffer @ 1.0x and 45s final buffer @ 1.0x.

#### 9. 🏛️ 3-Way Core Architecture Standardization (`01:00:00 IST`)
* **Standardized 3 Execution Modes**:
  1. **Mode 1 (Laptop Desktop GUI)**: `python main.py` (`HEADLESS=False`).
  2. **Mode 2 (Railway Cloud Server)**: Docker background container (`HEADLESS=True`).
  3. **Mode 3 (Android Termux Ubuntu PRoot)**: RealVNC Visible GUI (`vnc` then `diksha`).
* Cleaned up obsolete non-Ubuntu setup files (`termux_setup.sh`, `termux_install_prerequisites.sh`, `run_diksha.sh`).

---

### 🌐 Commit Log History (August 3, 2026)

| Commit Hash | Time (IST) | Commit Message / Description |
| :--- | :--- | :--- |
| **`76e7cfa`** | `19:25:50` | Docs: Add Playwright error fix, termux-wake-lock, dpkg-reconfigure tzdata timezone config, and git update details to `08_MOBILE_EXECUTION_TERMUX_UBUNTU_GUIDE.md` |
| **`1842b0d`** | `19:19:16` | Fix: Remove false-positive `not found_incomplete` check in module sync; require explicit header 100% OR `all_items_checkmarked` to prevent skipping incomplete modules |
| **`be84c71`** | `19:11:04` | Engine & Docs: Update Module Sync to 5 attempts maximum with infinite User Pause & Resume system (Press ENTER to resume, zero server close) |
| **`c9fa63b`** | `19:01:46` | Config: Add new registered user Bappaditya Biswas (`7384227228`) |
| **`8c4256b`** | `02:43:52` | Docs: Add exact Module Sync & Re-Execution terminal log trace to `11_COMPLETE_REAL_WORLD_TERMINAL_LOGS_EXAMPLE.md` |
| **`4c5cc72`** | `02:42:30` | Engine & Docs: Update Module Sync Loop to check module badge, expand accordion, find incomplete item, re-execute item, and re-check module badge |
| **`9d5308f`** | `02:39:25` | Fix: Add `safe_action_click` helper (`scroll_into_view` + `force=True` + JS click fallback) to resolve Playwright `Element is not visible` on items in long accordion panels |
| **`aa6791e`** | `02:36:44` | Docs: Complete Termux & Ubuntu PRoot setup guide with Single-Command 1-click installer, Multi-step breakdown, and Private Repo cloning |
| **`b0f73c9`** | `02:20:31` | Engine & Docs: Refine Targeted Single-Item Re-Execution and Dual Confirmation (Item checkmark + Module 100% badge) |
