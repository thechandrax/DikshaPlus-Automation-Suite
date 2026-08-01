# ⚙️ Automation Controls & Configuration Guide

This document details all customizable timing parameters, video playback architecture, stall recovery controls, engine module structure, and exit procedures for **DIKSHA+ Automation Suite**.

---

## 🎥 1. Complete Video Playback Architecture (`process_video_activity`)

Located in [automations/diksha_plus_engine.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/automations/diksha_plus_engine.py):

The video automation pipeline follows a strict 8-step lifecycle:

| Step | Stage | Behavior |
| :--- | :--- | :--- |
| **1** | **Dynamic Saved Progress Resume** | Inspects `currentTime`. If video was previously watched to any progress from **1% to 99%**, it logs `[SAVED PROGRESS RESUMED] Video already at X%!` and resumes dynamically from that position instead of rewinding to zero. |
| **2** | **Mandatory 15s Warm-up** | Plays the first 15 seconds at **1.0x normal speed** to ensure session telemetry & progress registration with DIKSHA servers. |
| **3** | **Dynamic Acceleration** | Applies **16.0x speed** for long videos ($\ge$ 5 min) or **10.0x speed** for short videos (< 5 min). |
| **4** | **10s Stall Window** | If buffering or paused (`readyState < 2`), waits 10 seconds for DIKSHA server buffer recovery. |
| **5** | **30s Fixed Rewind** | If still buffering after 10s, rewinds **exactly 30 seconds back** (`currentTime - 30`) and lowers playback to 4.0x speed. |
| **6** | **45s Final Buffer** | Slows down to **1.0x speed** for the final 45 seconds to naturally dispatch the `ended` event & log 100% progress telemetry. |
| **7** | **15s Checkmark Sync** | Closes video modal and waits 15 seconds for DIKSHA server 100% brown checkmark update. |
| **8** | **5s Refresh & Circuit Breaker** | If locked after 2 attempts, waits 5s and reloads page (`page.reload()`). If incomplete after 4 total attempts, triggers **Circuit Breaker** and exits cleanly. |

---

## 🎛️ 2. Configuration Settings (`config.py`)

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

## 🛑 3. How to Safely Close / Exit Automation

If you need to stop or close the automation while running:

### Method A: Keyboard Interrupt (CMD Terminal)
Press <kbd>Ctrl</kbd> + <kbd>C</kbd> in the CMD window. DIKSHA+ will catch the exit signal and close the Playwright browser cleanly.

### Method B: Close Terminal Window
Click the **`X`** button on the top right corner of the CMD window to terminate execution.
