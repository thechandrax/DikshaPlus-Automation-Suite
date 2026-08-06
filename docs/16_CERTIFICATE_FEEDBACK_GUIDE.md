# 🎓 Certificate Section & Give Feedback — Complete Guide

> **Engine:** `diksha_plus_engine.py` | **Function:** `process_certificate_feedback()` | **Updated:** 2026-08-06

---

## Table of Contents
1. What is the Certificate Section
2. Two Scenarios — Normal vs Already Complete
3. How the Engine Detects Each Scenario
4. Give Feedback Popup Flow (7 Steps)
5. HTML Structure Reference
6. Step-by-Step Code Logic
7. Full Example Logs
8. Error Handling and Fallbacks
9. All Bugs Fixed (7 total)
10. Timings Reference

---

## 1. What is the Certificate Section

When all modules in a DIKSHA course are 100% complete, a Certificate section appears.
It contains:

- **Give Feedback** button — opens a rating + review popup
- **Download Certificate** button — direct link to the PDF certificate

The automation must:
1. Expand the certificate accordion panel (so the button is visible)
2. Submit the Give Feedback popup (emoji rating + review text)
3. Close the "Feedback Submitted Successfully" success modal
4. Log course completion
5. Never block completion if feedback fails for any reason

---

## 2. Two Scenarios — Normal vs Already Complete

### Scenario A — Course just completed (Normal path)
```
All modules done → Certificate section appears in accordion
→ Engine expands the accordion panel (Give Feedback inside)
→ Give Feedback button now visible → Engine clicks button
→ Modal opens → fills emoji + text → submits
→ "Feedback Submitted Successfully" modal appears → Engine closes it
```

### Scenario B — Course already 100% complete before run
```
Navigate to course → Click Lessons tab → Wait 5s
→ DIKSHA auto-pops the Give Feedback modal immediately
→ No module panel shown, no accordion sections visible
→ Engine detects open modal → fills → submits directly
→ "Feedback Submitted Successfully" modal appears → Engine closes it
→ No accordion scan needed
```

---

## 3. How the Engine Detects Each Scenario

### Scenario B — Early Detection
```
[COURSE MODULES] Checking for Lessons tab...
  --> Clicking Lessons tab button...
  --> Waiting 5 seconds for DIKSHA server to hydrate modules...

  [CHECK] Is .modal.show already visible on page?
    YES → [EARLY COMPLETION DETECTED] → submit feedback → close success modal → return True
    NO  → continue to accordion scan normally
```

### Scenario A — Certificate Section Detection
```
for each accordion header:
    is_cert_section = header title contains "certificate"?
    has_customcert_link = a[act_type=customcert] found in panel?
    if either is True:
        → Check aria-expanded on accordion toggle
        → If panel is collapsed: click toggle → wait 2.5s (panel opens)
        → If panel already expanded: skip click
        → Give Feedback button now visible inside expanded panel
        → submit feedback → close success modal → return True
```

---

## 4. Give Feedback Popup Flow (7 Steps)

### When modal_already_open=False (Scenario A):
```
Step 1: Expand certificate accordion panel (aria-expanded check)
         If collapsed: click toggle → wait 2.5s → panel renders
         If already expanded: skip

Step 2: Find .btn-wrap button:has-text(Give Feedback)  [real bound button]
         Fallback: any button:has-text(Give Feedback)
         If not found: log warning and return

Step 3: click(force=True) + JS removeAttribute(disabled) + MouseEvent dispatch
         Wait 3s → verify .modal.show is visible
         If not visible: log warning and return
         Wait 1.5s for modal animation to fully settle

Step 4: Click div.emoji-item[data-rating=5] (Excellent)
         Fallback: click last emoji-item if data-rating=5 not found
         Wait 0.5s

Step 5: Fill textarea[name=review] with review text
         Wait 0.5s

Step 6: Click #submitFeedbackBtn → Wait 5s for AJAX POST to DIKSHA server

Step 7: Wait 1.5s → Click a.close[data-dismiss=modal]
         Fallback: press Escape key
         Wait 1.5s for close animation
```

### When modal_already_open=True (Scenario B):
```
Steps 1-3 SKIPPED (button is hidden behind open modal overlay)

Step 4: Wait 1.5s for animation to fully settle
         Click div.emoji-item[data-rating=5] (Excellent)
         Wait 0.5s

Step 5: Fill textarea[name=review] with review text
         Wait 0.5s

Step 6: Click #submitFeedbackBtn → Wait 5s for AJAX POST to DIKSHA server

Step 7: Wait 1.5s → Click a.close[data-dismiss=modal]
         Fallback: Escape key → wait 1s
```

---

## 5. HTML Structure Reference

### Give Feedback Button (inside expanded certificate panel)
```html
<div class="btn-wrap mt-0">
    <button disabled>Give Feedback</button>  <!-- CORRECT: bound button -->
    <a act_type="customcert">Download Certificate</a>
</div>
```

### Feedback Popup Modal
```
Emoji ratings (data-rating 1 to 5):
  data-rating=5  Excellent  <-- engine selects this

Textarea: name="review" | id="submitFeedbackBtn"
```

### Success Modal (Feedback Submitted Successfully)
```html
<div class="modal-header">
    <h2 class="modal-title">Feedback Submitted Successfully</h2>
    <a type="button" class="close" data-dismiss="modal" aria-label="Close">
        <i class="icon-pre-cancel" aria-hidden="true"></i>
    </a>
</div>
```

Close button selectors used:
```
a.close[data-dismiss='modal'], a[aria-label='Close'],
button.close[data-dismiss='modal'], .modal-header a.close
```

### Review text (163 characters, limit 300):
```
"This course was very well-structured and informative. The content
 is highly relevant and practical for classroom teaching.
 I strongly recommend it to all teachers."
```

---

## 6. Step-by-Step Code Logic

### Accordion expansion + call (Scenario A)
```python
# BEFORE calling feedback: expand certificate panel
cert_toggle = header.locator("a[data-toggle='collapse'], ...").first
aria_exp = (await cert_toggle.get_attribute("aria-expanded") or "").lower()
if aria_exp != "true":
    await cert_toggle.click(force=True)
    await page.wait_for_timeout(2500)

await process_certificate_feedback(page)  # default modal_already_open=False
```

### Early detection (Scenario B)
```python
early_modal = page.locator(".modal.show, .modal.in, #feedbackModal, .feedback-modal").first
if await early_modal.count() > 0 and await early_modal.is_visible():
    await process_certificate_feedback(page, modal_already_open=True)
    return True
```

### Step 7 — Close success modal
```python
close_btn = page.locator(
    "a.close[data-dismiss='modal'], a[aria-label='Close'], "
    "button.close[data-dismiss='modal'], .modal-header a.close, .modal-header button.close"
).first
if await close_btn.count() > 0 and await close_btn.is_visible():
    await close_btn.click(force=True)
    await page.wait_for_timeout(1500)
else:
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(1000)
```

---

## 7. Full Example Logs

### Scenario A — Normal
```
🎓 [CERTIFICATE SECTION DETECTED] 'Certificate' reached!
  --> All course requirements 100% satisfied!
  --> [CERTIFICATE] Expanding accordion panel to reveal Give Feedback button...
  --> [CERTIFICATE FEEDBACK] Attempting to submit course feedback before certificate download...
  --> [CERTIFICATE FEEDBACK] Clicking 'Give Feedback' button...
  --> [CERTIFICATE FEEDBACK] Feedback modal opened successfully!
  --> [CERTIFICATE FEEDBACK] Selected 5-star rating emoji (Excellent)
  --> [CERTIFICATE FEEDBACK] Filled feedback textarea with positive review.
  --> [CERTIFICATE FEEDBACK] Clicking 'Submit Feedback'...
  --> [CERTIFICATE FEEDBACK] Feedback submitted successfully!
  --> [CERTIFICATE FEEDBACK] Closing 'Feedback Submitted Successfully' modal...
  --> [CERTIFICATE FEEDBACK] Success modal closed.

===================================================================
 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!
===================================================================
```

### Scenario B — Already complete
```
  --> [EARLY COMPLETION DETECTED] Course is already 100% complete!
  --> [EARLY COMPLETION] Give Feedback modal detected automatically by DIKSHA.
  --> [CERTIFICATE FEEDBACK] Modal already open - skipping button click...
  --> [CERTIFICATE FEEDBACK] Selected 5-star rating emoji (Excellent)
  --> [CERTIFICATE FEEDBACK] Filled feedback textarea with positive review.
  --> [CERTIFICATE FEEDBACK] Feedback submitted successfully!
  --> [CERTIFICATE FEEDBACK] Success modal closed.
===================================================================
 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!
===================================================================
```

---

## 8. Error Handling and Fallbacks

| Failure Point | Fallback Action |
|---|---|
| Certificate panel collapsed | click toggle → 2.5s wait → panel opens |
| Panel expand fails | Warning logged — feedback still attempted |
| .btn-wrap button not found | Falls back to any button:has-text(Give Feedback) |
| Both buttons not found | Logs warning and returns — completion proceeds |
| click(force=True) fails | JS dispatch with removeAttribute(disabled) fires next |
| Modal does not open | Logs warning and returns — completion proceeds |
| data-rating=5 not found | Clicks last emoji-item (highest available) |
| No emojis found | Step skipped — submit still fires |
| Textarea not found | Step skipped — submit still fires |
| Submit button not found | Logs warning — completion banner still shows |
| Success modal close btn not found | Escape key pressed as fallback |
| Any unhandled exception | Outer try/except logs warning — never blocks completion |

---

## 9. All Bugs Fixed

### Bug 1 — Dual Give Feedback button
```
Problem: DIKSHA renders two identical buttons. .first picks outer unbound button.
Fix:     Prefer .btn-wrap button:has-text(Give Feedback) — the real bound button.
```

### Bug 2 — Modal already open path tried to click hidden button
```
Problem: Scenario B modal open covers page. Button hidden → count()==0 → return.
Fix:     Added modal_already_open=True parameter — skips button-click steps.
```

### Bug 3 — No modal animation wait
```
Problem: Emoji clicked immediately after modal opens → click missed (animating).
Fix:     1.5s wait after modal opens before emoji click.
```

### Bug 4 — Broad modal selector
```
Problem: [id*='feedback'] matched error labels → false positives.
Fix:     Only .modal.show, .modal.in, #feedbackModal, .feedback-modal used.
```

### Bug 5 — No gap between steps
```
Problem: Steps fired instantly → race conditions on slow networks.
Fix:     0.5s wait between emoji→textarea, textarea→submit.
```

### Bug 6 — Certificate accordion panel not expanded before feedback call (2026-08-06)
```
Problem: Certificate section detected → process_certificate_feedback() called immediately.
         Panel still COLLAPSED → Give Feedback button invisible → count()==0.
         "Give Feedback button not found. Skipping." — silent skip every time.

Root cause: Panel expansion is inside while True module loop (below cert check).
            Certificate path bypasses that loop — panel never expanded.

Fix:     Added dedicated accordion expansion block BEFORE calling feedback.
         Checks aria-expanded. If not "true": click toggle → wait 2.5s → open.
```

### Bug 7 — open_activity_popup: is_visible() fallback to wrong button (2026-08-06)
```
Problem: li.action123 a[act_id='X'] found but scrolled out of viewport.
         is_visible() = False → fallback to outer bare button (no handler).
         Bare button click → no modal → [MODAL NOT DETECTED] every first try.

Fix:     Removed is_visible() check. count() > 0 is sufficient.
         safe_action_click() calls scroll_into_view_if_needed() automatically.
         Also: increased first-click wait from 3s → 5s for PDF loading time.
```

---

## 10. Timings Reference

| Phase | Wait | Reason |
|---|---|---|
| Certificate panel expand | 2.5s | Bootstrap collapse animation |
| After clicking Give Feedback (Scenario A) | 3s | Modal open animation |
| After modal confirmed open / already open | 1.5s | Animation settled — emoji items rendered |
| After emoji click | 0.5s | Selection registered before textarea fill |
| After textarea fill | 0.5s | Input settled before submit click |
| After Submit Feedback click | 5s | AJAX POST to DIKSHA server completes |
| Before closing success modal | 1.5s | "Feedback Submitted" modal renders |
| After success modal close click | 1.5s | Modal close animation completes |

**Total time for feedback flow:**
- Scenario A (panel collapsed + button click): ~15–17 seconds
- Scenario A (panel already expanded): ~13–14 seconds
- Scenario B (modal already open): ~10–11 seconds

---

*Updated: 2026-08-06 | diksha_plus_engine.py — process_certificate_feedback(page, modal_already_open=False)*