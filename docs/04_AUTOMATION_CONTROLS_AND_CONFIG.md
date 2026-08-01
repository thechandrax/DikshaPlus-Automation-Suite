# ⚙️ Automation Controls & Configuration Guide

This document details all customizable timing parameters, video buffering recovery settings, engine module structure, and exit procedures for **DIKSHA+ Automation Suite**.

---

## 🎛️ 1. Configuration Settings (`config.py`)

You can tune all automation behaviors inside [config.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py):

```python
# ----------------------------------------------------------------------
# Automation & Timeout Settings
# ----------------------------------------------------------------------
PAGE_TIMEOUT_MS = 60000              # Page navigation timeout (60 seconds)
SELECTOR_TIMEOUT_MS = 15000          # Element waiting timeout (15 seconds)

# ----------------------------------------------------------------------
# Pacing & Delay Controls (Seconds)
# ----------------------------------------------------------------------
MIN_VIDEO_WATCH_SECONDS = 3          # Fast video completion buffer (seconds)
MIN_PDF_READ_SECONDS = 3             # Fast document reading buffer (seconds)
POST_LOGIN_WAIT_SECONDS = 5          # DIKSHA SSO server redirect wait
INTER_ACTIVITY_DELAY = 1.0           # Delay between sub-items (seconds)
SERVER_SYNC_TIMEOUT_SECONDS = 30     # 100% completion badge sync wait

# ----------------------------------------------------------------------
# Quiz & Assessment Controls
# ----------------------------------------------------------------------
AUTOMATIC_FINAL_SUBMIT = True        # Auto-submit quiz after last question

# ----------------------------------------------------------------------
# Browser Launch Options
# ----------------------------------------------------------------------
HEADLESS = False                     # Set to True for hidden browser mode
SLOMO_MS = 200                       # Slow-motion delay for smooth watching
```

---

## 🎥 2. Video Buffering & 3% Auto-Rewind Engine (`process_video_activity`)

Located in [automations/diksha_plus_engine.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/automations/diksha_plus_engine.py):

* **Buffering Detection**: When video buffering/stall (`readyState < 2` or `is_paused`) is detected, DIKSHA+ waits **8 seconds** for natural network buffer recovery.
* **Auto-Rewind 3%**: If still buffering after 8 seconds, it automatically rewinds **3% back** (`duration * 0.03`) and calls `.play()` to unfreeze video playback smoothly without console spam.

---

## 🛑 3. How to Safely Close / Exit Automation

If you need to stop or close the automation while running:

### Method A: Keyboard Interrupt (CMD Terminal)
Press <kbd>Ctrl</kbd> + <kbd>C</kbd> in the CMD window. DIKSHA+ will catch the exit signal and close the Playwright browser cleanly.

### Method B: Close Terminal Window
Click the **`X`** button on the top right corner of the CMD window to terminate execution.
