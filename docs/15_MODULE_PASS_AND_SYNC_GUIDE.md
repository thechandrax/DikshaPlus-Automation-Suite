# 📘 DIKSHA+ Module Pass & Module Sync — Complete Guide

> **Engine:** `diksha_plus_engine.py` | **Updated:** 2026-08-05

---

## 📋 Table of Contents
1. [Overview — Two-Layer Completion System](#overview)
2. [Module Pass — Executing Items](#module-pass)
3. [Module Sync — Server Verification](#module-sync)
4. [How They Work Together](#together)
5. [Full Example Logs](#example-logs)
6. [Failure & Recovery Flow](#failure-recovery)
7. [Quick Reference Table](#quick-reference)
8. [Both Failures Trigger Course Restart](#both-trigger-restart)

---

## 1. Overview — Two-Layer Completion System

DIKSHA+ uses a **two-layer system** to guarantee every module reaches 100%:

```
LAYER 1: MODULE PASS   → "Do the work" (execute every PDF / Video / Quiz)
LAYER 2: MODULE SYNC   → "Confirm the server agrees it is 100% done"
```

Both layers must succeed before moving to the next module.
If either layer fails all its attempts → Full Course Restart triggered (up to 5 times).

---

## 2. Module Pass (`#1/3`, `#2/3`, `#3/3`)

### What it is
A full scan of all subsection items inside one module accordion.
The outer `while True` loop runs up to **3 passes** per module.

### When a new pass starts
| Trigger | Reason |
|---|---|
| Start of module processing | Always runs Pass #1 first |
| Locked item detected | `lock_triggered = True` → inner loop breaks → outer while `continue` → Pass #2 |
| Lock retry limit exceeded | Fell through to sync → sync failed → outer while continues → Pass #3 |

### What happens in each pass
```
Pass #1:  Scan all N items
          ├─ Item already 100%?   → [✓ ALREADY DONE] Skip
          ├─ Item locked?         → Re-execute prerequisite → reload → lock_triggered → break
          └─ Item incomplete?     → Execute (3 attempts per item)

Pass #2:  Re-scan all N items (on freshly reloaded page)
          ├─ Items done in Pass #1 → instantly skipped (in completed_items)
          ├─ Previously locked item → now unlocked → execute
          └─ Any remaining items  → execute

Pass #3:  Final re-scan (last chance)
          └─ Same as Pass #2 — if module still not done after this → Sync runs
```

### Log format
```
🔄 [RE-STARTING FULL MODULE PASS #2/3]
   Re-scanning 'Module 10: School Leadership...' & re-evaluating all subsections...
```

### Full Pass #1 → #2 example
```
📚 MODULE [10/10]: Module 10: School Leadership for Foundational Literacy and Numeracy

  🔄 [RE-STARTING FULL MODULE PASS #1/3] (first pass — no log shown for #1)
  📋 [SUBSECTION BREAKDOWN (23 ITEMS)]:
     [01/23] ✓ Introduction to School Leadership  || 100% || View
     [02/23] ✓ Role of Head Teacher               || 100% || View
     ...
     [17/23] ⏳ Activity 05: Try It Yourself       || 0%   || View
     [18/23] ⏳ Implementation of Foundational...  || 0%   || View

  ▶ SUBSECTION [17/23]: 'Activity 05: Try It Yourself' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100% complete!
  --> DIKSHA Server sync buffer: waiting 4 seconds...

  --> [✓ ALREADY DONE] SUBSECTION [17/23]: 'Activity 05: Try It Yourself' [Skipping!]
  --> 🔒 [LOCKED ITEM DETECTED] SUBSECTION [18/23]: 'Implementation of Foundational...'
       is locked by DIKSHA prerequisite rule.
  --> Re-executing prior prerequisite item [17/23]: 'Activity 05: Try It Yourself'...
  --> Server 100% checkmark confirmed!
  🔓 [LOCK RETRY] Prerequisite executed. Re-scanning buttons...

===================================================================
  🔄 [RE-STARTING FULL MODULE PASS #2/3]
     Re-scanning 'Module 10: School Leadership...' & re-evaluating all subsections...
===================================================================
  📋 [SUBSECTION BREAKDOWN (23 ITEMS)]:
     [01/23] ✓ Introduction to School Leadership  || 100% || View
     ...
     [17/23] ✓ Activity 05: Try It Yourself        || 100% || View
     [18/23] ⏳ Implementation of Foundational...   || 0%   || View  ← now unlocked!

  --> [✓ ALREADY DONE] SUBSECTION [01/23] ... [Skipping!]
  ...
  --> [✓ ALREADY DONE] SUBSECTION [17/23]: 'Activity 05...' [Skipping!]

  ▶ SUBSECTION [18/23]: 'Implementation of Foundational...' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100% complete!
  ...
  ▶ SUBSECTION [23/23]: 'Final Assessment' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100% complete!

  --> [DOUBLE CONFIRMATION] Verifying 100% for 'Module 10'...
```

---

## 3. Module Sync (`1/3`, `2/3`, `3/3`)

### What it is
After all items in a module pass have been executed, the engine checks whether
**DIKSHA's server-side module header** shows 100% complete.

This is separate from individual item completion — DIKSHA must aggregate all
item completions into the module-level percentage, which can take extra seconds.

### Why it is needed
```
Your browser (local):        DIKSHA server (remote):
────────────────────         ───────────────────────
Item 18 = ✅ done            Module header = still 97% ❌
Item 19 = ✅ done            (server database hasn't aggregated yet)
Item 20 = ✅ done
...
Item 23 = ✅ done
```

Even when every single item is verified 100%, DIKSHA's server may take
10–30 extra seconds to update the module-level completion percentage.
Module Sync gives it **3 chances × 15 seconds = up to 45 seconds** to catch up.

### What each sync attempt does
```
For each sync attempt (1, 2, 3):
  1. page.reload()                             ← fresh server data
  2. Wait 3s for page to settle
  3. ensure_on_course_page()                   ← verify still on course
  4. Re-expand accordion panel
  5. Re-scan all subsection buttons
  6. Print updated SUBSECTION BREAKDOWN list
  7. Re-execute any still-incomplete items     ← backup execution
  8. Check is_header_100_percent_complete()    ← module header check
     OR all individual items checkmarked?
  9. ✅ YES → MODULE SYNC SUCCESS → break
     ❌ NO  → wait 15s → next attempt
```

### Log format
```
⏳ [MODULE SYNC 1/3] Reloading page & re-scanning subsections...
⏳ [SYNC WAIT] Attempt 1/3 incomplete. Waiting 15s for server sync...

⏳ [MODULE SYNC 2/3] Reloading page & re-scanning subsections...
✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified on Attempt #2/3!
🎓 [MODULE COMPLETED] 'Module 10: School Leadership...' completed! Advancing...
```

### Success example
```
  --> [DOUBLE CONFIRMATION] Verifying 100% for 'Module 10: School Leadership...'

  ⏳ [MODULE SYNC 1/3] Reloading page & re-scanning subsections...
  📋 [SUBSECTION BREAKDOWN (23 ITEMS) - Attempt #1/3]:
     [01/23] ✓ Introduction to School Leadership  || 100% || View
     [02/23] ✓ Role of Head Teacher               || 100% || View
     ...
     [23/23] ✓ Final Assessment                   || 100% || View
  ⏳ [SYNC WAIT] Attempt 1/3 incomplete. Waiting 15s for server sync...

  ⏳ [MODULE SYNC 2/3] Reloading page & re-scanning subsections...
  📋 [SUBSECTION BREAKDOWN (23 ITEMS) - Attempt #2/3]:
     [01/23] ✓ ...  [23/23] ✓ ...  (all 23 done)
  ✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified on Attempt #2/3!
  🎓 [MODULE COMPLETED] 'Module 10: School Leadership...' completed! Advancing to next module...
```

### All 3 fail example → Course Restart
```
  ⏳ [MODULE SYNC 1/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 1/3 incomplete. Waiting 15s for server sync...

  ⏳ [MODULE SYNC 2/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 2/3 incomplete. Waiting 15s for server sync...

  ⏳ [MODULE SYNC 3/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 3/3 incomplete. Waiting 15s for server sync...

  ⚠️ [MODULE SYNC FAILED] 'Module 10: School Leadership...' not 100% after 3 sync attempts.
  🔄 Triggering full course restart to retry from the beginning...

===================================================================
  🔄 [COURSE RESTART 1/5] Item 'Module 10: School Leadership...' failed all attempts.
     Restarting course from beginning...
===================================================================
```

---

## 4. How They Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODULE PROCESSING FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODULE PASS #1/3                                               │
│  ├─ Scan 23 items                                               │
│  ├─ Execute incomplete items (3 attempts each)                  │
│  └─ Lock detected? → re-execute prerequisite → break loop       │
│              ↓ lock_triggered = True                            │
│  MODULE PASS #2/3    (outer while loop continues)               │
│  ├─ Re-scan 23 items on freshly reloaded page                   │
│  ├─ Skip already-done items instantly                           │
│  └─ Execute newly unlocked items                                │
│              ↓ all items done                                   │
│  ┌─────────────────────────────────────────┐                   │
│  │  MODULE SYNC 1/3                        │                   │
│  │  → reload → check module header 100%?   │                   │
│  │  ❌ NO → wait 15s                       │                   │
│  │  MODULE SYNC 2/3                        │                   │
│  │  → reload → check module header 100%?   │                   │
│  │  ❌ NO → wait 15s                       │                   │
│  │  MODULE SYNC 3/3                        │                   │
│  │  → reload → check module header 100%?   │                   │
│  │  ✅ YES → MODULE COMPLETED              │                   │
│  │  ❌ NO  → Course Restart (up to 5×)     │                   │
│  └─────────────────────────────────────────┘                   │
│              ↓ success                                          │
│  🎓 MODULE COMPLETED → next module                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Full Example Logs

### Scenario A — Clean run (Pass #1 + Sync #1 success)
```
📚 MODULE [02/10]: Module 02: Play and Development

  📋 [SUBSECTION BREAKDOWN (8 ITEMS)]:
     [01/08] ⏳ Introduction to Play               || 0%   || View
     [02/08] ⏳ Types of Play                      || 0%   || View
     [03/08] ⏳ Role of Teacher in Play            || 0%   || View
     [04/08] ⏳ Play-based Activity 01             || 0%   || View
     [05/08] ⏳ Play-based Activity 02             || 0%   || View
     [06/08] ⏳ Assessment                         || 0%   || View
     [07/08] ⏳ Feedback Form                      || 0%   || View
     [08/08] ⏳ Module Summary                     || 0%   || View

  ▶ SUBSECTION [01/08]: 'Introduction to Play' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100% complete!
  ...
  ▶ SUBSECTION [08/08]: 'Module Summary' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100% complete!

  --> [DOUBLE CONFIRMATION] Verifying 100% for 'Module 02: Play and Development'...

  ⏳ [MODULE SYNC 1/3] Reloading page & re-scanning subsections...
  ✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified on Attempt #1/3!
  🎓 [MODULE COMPLETED] 'Module 02: Play and Development' completed! Advancing to next module...
```

---

### Scenario B — Lock triggered (Pass #1 → Pass #2 → Sync success)
```
📚 MODULE [10/10]: Module 10: School Leadership...

  ▶ SUBSECTION [17/23]: 'Activity 05: Try It Yourself' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100%!

  --> 🔒 [LOCKED ITEM DETECTED] SUBSECTION [18/23]: 'Implementation...' is locked.
  --> Re-executing prior prerequisite item [17/23]...
  --> Server 100% checkmark confirmed!
  🔓 [LOCK RETRY] Prerequisite executed. Re-scanning buttons...

  🔄 [RE-STARTING FULL MODULE PASS #2/3]
  --> [✓ ALREADY DONE] SUBSECTION [01/23] ... [17/23] [Skipping!]

  ▶ SUBSECTION [18/23]: 'Implementation...' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100%!
  ...
  ▶ SUBSECTION [23/23]: 'Final Assessment' [Attempt 1/3]
  ✅ [ATTEMPT 1/3 SUCCESS] Verified 100%!

  ⏳ [MODULE SYNC 1/3] → ⏳ [SYNC WAIT] Attempt 1/3. Waiting 15s...
  ⏳ [MODULE SYNC 2/3]
  ✅ [MODULE SYNC SUCCESS] Verified on Attempt #2/3!
  🎓 [MODULE COMPLETED] Advancing to next module...
```

---

### Scenario C — All sync fails → Course Restart
```
  ⏳ [MODULE SYNC 1/3] → incomplete → wait 15s
  ⏳ [MODULE SYNC 2/3] → incomplete → wait 15s
  ⏳ [MODULE SYNC 3/3] → incomplete → wait 15s

  ⚠️ [MODULE SYNC FAILED] 'Module 03: Water Management...' not 100% after 3 sync attempts.
  🔄 Triggering full course restart to retry from the beginning...

  ===================================================================
  🔄 [COURSE RESTART 1/5] 'Module 03: Water Management...' failed.
     Restarting course from beginning...
  ===================================================================

  🚀 Starting Enrolled Course: [1] NISHTHA FLN English
  [COURSE MODULES] Checking for Lessons tab...
  --> [✓ SKIP MODULE] 'Module 01' is ALREADY 100% COMPLETED. [Skipping!]
  --> [✓ SKIP MODULE] 'Module 02' is ALREADY 100% COMPLETED. [Skipping!]
  📚 MODULE [03/10]: Module 03: Water Management...   ← retries from here
```

---

## 6. Failure & Recovery Flow

```
Item fails 3 attempts
        ↓
🔄 _CourseRestartSignal raised
        ↓
Course Restart 1/5 → restart from top

Module Sync fails 3/3
        ↓
🔄 _CourseRestartSignal raised
        ↓
Course Restart 1/5 → restart from top

Course Restart fails 5 times
        ↓
❌ [COURSE RESTART LIMIT] Moving on to next course
```

---

## 7. Quick Reference Table

| System | Attempts | Wait Between | On Success | On All Fail |
|---|---|---|---|---|
| Per-Item Retry | 3 | 5s | Next item | `_CourseRestartSignal` |
| Lock Retry | max+3 passes | page reload | Execute unlocked item | Proceed to sync |
| Module Pass | 3 | immediate | Run sync | Run sync on pass 3 |
| Module Sync | 3 | 15s | Next module | `_CourseRestartSignal` |
| Course Restart | 5 | navigate + 5s | Continue course | Log and move on |

---

### Key timings summary
```
Per-item retry wait    :  5s
Post-item server buffer:  4s
Module sync page reload:  3s
Module sync wait       : 15s  × 3 attempts = 45s max
Course restart nav wait:  5s
```

---
*Generated: 2026-08-05 | diksha_plus_engine.py*

---

## 8. Both Failures Trigger `[COURSE RESTART X/5]`

> **YES — both failure cases trigger the exact same course restart.**
> They both raise `_CourseRestartSignal` which is caught by the same restart loop.

---

### Case 1 — Per-Item fails all 3 attempts:

```python
# diksha_plus_engine.py (inside per-item retry loop)
logger.warning(f"  ⚠️ [ALL 3 ATTEMPTS EXHAUSTED] '{real_item_title}' failed all 3 attempts.")
raise _CourseRestartSignal(real_item_title)   # ← raises signal
```

**Log example:**
```
▶ SUBSECTION [18/23]: 'Implementation of Foundational Literacy...' [Attempt 1/3]
  --> [VIDEO CHECKMARK] Waiting exactly 10s...
  ⚠️ [ATTEMPT 1/3 INCOMPLETE] Not yet 100%. Retrying in 5s...

▶ SUBSECTION [18/23]: 'Implementation of Foundational Literacy...' [Attempt 2/3]
  ⚠️ [ATTEMPT 2/3 INCOMPLETE] Not yet 100%. Retrying in 5s...

▶ SUBSECTION [18/23]: 'Implementation of Foundational Literacy...' [Attempt 3/3]
  ⚠️ [ALL 3 ATTEMPTS EXHAUSTED] 'Implementation of Foundational Literacy...' failed all 3 attempts.
       Restarting course from beginning...
        ↓
🔄 [COURSE RESTART 1/5]
```

---

### Case 2 — Module Sync fails all 3 attempts:

```python
# diksha_plus_engine.py (after sync loop exhausted)
logger.warning(f"  ⚠️ [MODULE SYNC FAILED] '{header_title}' not 100% after 3 sync attempts.")
logger.warning(f"  🔄 Triggering full course restart to retry from the beginning...")
raise _CourseRestartSignal(header_title)      # ← raises same signal
```

**Log example:**
```
  ⏳ [MODULE SYNC 1/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 1/3 incomplete. Waiting 15s for server sync...

  ⏳ [MODULE SYNC 2/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 2/3 incomplete. Waiting 15s for server sync...

  ⏳ [MODULE SYNC 3/3] Reloading page & re-scanning subsections...
  ⏳ [SYNC WAIT] Attempt 3/3 incomplete. Waiting 15s for server sync...

  ⚠️ [MODULE SYNC FAILED] 'Module 03: Water Management...' not 100% after 3 sync attempts.
  🔄 Triggering full course restart to retry from the beginning...
        ↓
🔄 [COURSE RESTART 1/5]
```

---

### Both caught by the SAME restart loop:

```python
# in run_diksha_automation
for _cr in range(1, 7):   # up to 5 restarts
    try:
        await process_course_modules(...)
        break  # success — exit restart loop
    except _CourseRestartSignal as sig:
        if _cr < 6:
            logger.warning(f" 🔄 [COURSE RESTART {_cr}/5] Item '{sig}' failed.")
            await page.goto(course_url)   # go back to course start
        else:
            logger.error(f" ❌ [COURSE RESTART LIMIT] Restarted 5 times. Moving on.")
```

---

### What the restart log looks like — SAME for both cases:

```
===================================================================
🔄 [COURSE RESTART 1/5] Item 'Implementation of Foundational Literacy...' failed.
   Restarting course from beginning...
===================================================================

🚀 Starting Enrolled Course: [1] NISHTHA FLN English
  --> Clicking 'Lessons' tab button...
  --> Waiting 5 seconds for DIKSHA server to hydrate modules...
  [ACCORDION ENGINE] Scanning course section accordions...
  --> [✓ SKIP MODULE] 'Module 01' is ALREADY 100% COMPLETED. [Skipping!]
  --> [✓ SKIP MODULE] 'Module 02' is ALREADY 100% COMPLETED. [Skipping!]
  📚 MODULE [03/10]: Module 03: ...  ← picks up from here
```

> **Note:** The only difference between Case 1 and Case 2 in the restart log
> is the **name** shown in `[COURSE RESTART X/5]`:
> - Case 1 → shows the **item/subsection name** that failed
> - Case 2 → shows the **module name** that failed sync

---

### Comparison table:

| | Case 1: Item 3 Attempts Fail | Case 2: Sync 3 Attempts Fail |
|---|---|---|
| **Raised by** | Per-item retry loop | Module sync loop |
| **Signal** | `_CourseRestartSignal(item_title)` | `_CourseRestartSignal(module_title)` |
| **Caught by** | `run_diksha_automation` restart loop | Same loop |
| **Restart log** | `[COURSE RESTART X/5]` | `[COURSE RESTART X/5]` |
| **What restarts** | Entire course from top | Entire course from top |
| **Already-done modules** | Skipped automatically | Skipped automatically |
| **Max restarts** | 5 | 5 |

---
*Generated: 2026-08-05 | diksha_plus_engine.py*
