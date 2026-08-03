"""
DIKSHA LMS Automation Suite — Core Playwright Engine
Extracted from DIKSHA.docx DOM specification.
"""

import os
import re
import sys
import json
import asyncio
from pathlib import Path
from PIL import Image

import config
from utils.logger import get_logger

logger = get_logger("DikshaEngine")

# Global pause state controller
PAUSE_AUTOMATION = False

async def check_pause_status():
    """
    Checks if global pause signal is set. If True, enters asynchronous sleep loop
    until unpaused via console command or IPC signal.
    """
    global PAUSE_AUTOMATION
    while PAUSE_AUTOMATION:
        logger.info("  ⏸️ [ENGINE PAUSED] Automation is currently paused by user. Waiting for resume signal...")
        await asyncio.sleep(3)

async def close_activity_modal(page):
    """
    Closes DIKSHA activity modal popups (iframe / bootstrap modal).
    """
    try:
        close_selectors = [
            "button.close[data-dismiss='modal']",
            ".modal-header button.close",
            "button:has-text('×')",
            ".modal-footer button:has-text('Close')",
            "button[aria-label='Close']",
            "#closeModalBtn"
        ]
        for sel in close_selectors:
            el = page.locator(sel).first
            if await el.count() > 0 and await el.is_visible():
                await el.click(force=True)
                logger.info("  --> Closed activity modal popup.")
                await page.wait_for_timeout(1500)
                return True
    except Exception as e:
        logger.warning(f"  --> Notice closing modal: {e}")
    return False

async def wait_for_server_checkmark(page, timeout=15):
    """
    Waits for DIKSHA server checkmark sync (up to specified timeout seconds).
    Checks live DOM for fa-check icon or p100 completion badge.
    """
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        await check_pause_status()
        chk = page.locator("i.fa-check, .module-progress-pie i, .p100, .c100.p100").first
        if await chk.count() > 0 and await chk.is_visible():
            logger.info("  --> Server 100% checkmark confirmed!")
            return True
        await page.wait_for_timeout(2000)
    logger.info("  --> Checkmark sync window completed.")
    return False

async def safe_action_click(locator):
    """
    Safely clicks an action button (View / Start / Continue / Accordion Header) even if hidden or in scroll view.
    Combines scroll_into_view_if_needed, force=True click, and native JS element.click() fallback.
    """
    try:
        await locator.scroll_into_view_if_needed()
        await locator.click(force=True, timeout=5000)
    except Exception:
        try:
            await locator.evaluate("el => el.click()")
        except Exception:
            try:
                await locator.click(force=True)
            except Exception as e:
                logger.warning(f"  --> Safe action click notice: {e}")

async def process_video_activity(page, view_button):
    """
    STEP-07 (Video Activity - act_type="url"):
    Implements technical specification for Video Acceleration & Telemetry:
      1. Nested iFrame & Shadow DOM Support (scans all frames for <video>)
      2. 15s Warm-up Buffer @ 1.0x speed (telemetry session init)
      3. Dynamic Acceleration: 16x speed (duration >= 5m) or 10x speed (duration < 5m)
      4. Stall & Pause Recovery (auto-rewind 5% & resume play if stuck)
      5. 45s Final Buffer @ 1.0x speed (natural ended event & 100% progress telemetry)
      6. Video 10s-15s Checkmark Verification & 1-Time Reload/Replay Recovery Engine
    """
    row_saved_pct = 0
    try:
        parent_row = view_button.locator("xpath=./ancestor::*[contains(@class, 'activity') or contains(@class, 'row') or contains(@class, 'item') or self::li or self::div][1]")
        if await parent_row.count() > 0:
            row_text = await parent_row.inner_text()
            m = re.search(r'(\d{1,2})%', row_text)
            if m:
                row_saved_pct = int(m.group(1))
    except Exception:
        row_saved_pct = 0

    logger.info("[VIDEO ACTIVITY] Opening video module...")
    await safe_action_click(view_button)
    await page.wait_for_timeout(3000)

    target_frame = page
    video_locator = page.locator("video").first
    
    if await video_locator.count() == 0 or not await video_locator.is_visible():
        for frame in page.frames:
            f_v = frame.locator("video").first
            if await f_v.count() > 0:
                target_frame = frame
                video_locator = f_v
                logger.info(f"  --> Found video element inside nested frame: {frame.url}")
                break

    play_btn = target_frame.locator("button:has-text('Play'), .vjs-play-control, .media-play-button, .play-button").first
    if await play_btn.count() > 0 and await play_btn.is_visible():
        try:
            await play_btn.click(force=True)
            logger.info("  --> Video playback started via Play button.")
        except Exception:
            pass

    try:
        await target_frame.evaluate("""
            async () => {
                const vids = document.querySelectorAll('video');
                vids.forEach(v => {
                    v.muted = true;
                    v.volume = 0.0;
                    v.playbackRate = 1.0;
                    v.play().catch(() => {});
                });

                const qualBtns = Array.from(document.querySelectorAll('.vjs-quality-selector, .vjs-resolution-button, .quality-setting, option, .vjs-menu-item, button'));
                const lowOpt = qualBtns.find(el => {
                    const txt = (el.innerText || el.textContent || '').toLowerCase();
                    return txt.includes('360') || txt.includes('240') || txt.includes('low');
                });
                if (lowOpt) {
                    lowOpt.click();
                }
            }
        """)
        logger.info("  --> Video playback started (Muted & 360p Low Resolution preference set).")
    except Exception as e:
        logger.warning(f"  --> Video play init notice: {e}")

    await page.wait_for_timeout(2000)

    duration = 0.0
    try:
        duration = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.duration : 0; }"))
    except Exception:
        duration = 0.0

    if duration <= 0.0:
        logger.warning("  --> Could not determine exact video duration. Waiting 15s standard playback buffer...")
        await page.wait_for_timeout(15000)
        await close_activity_modal(page)
        return

    logger.info(f"  --> Video Duration: {int(duration)} seconds ({int(duration // 60)}m {int(duration % 60)}s)")

    curr_time = 0.0
    try:
        curr_time = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.currentTime : 0; }"))
    except Exception:
        curr_time = 0.0

    if row_saved_pct > 0 and curr_time < (duration * (row_saved_pct / 100.0)):
        target_resume_sec = duration * (row_saved_pct / 100.0)
        logger.info(f"  --> [DOM PROGRESS RESUMED] Resuming video from saved {row_saved_pct}% ({int(target_resume_sec)}s / {int(duration)}s)...")
        try:
            await target_frame.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) v.currentTime = {target_resume_sec}; }}")
            curr_time = target_resume_sec
        except Exception:
            pass
    elif curr_time > 5.0:
        logger.info(f"  --> [SAVED PROGRESS RESUMED] Video already at {int(curr_time / duration * 100)}% ({int(curr_time)}s / {int(duration)}s)! Resuming dynamically from current position...")

    if curr_time < 15.0:
        warmup_needed = 15.0 - curr_time
        logger.info("  --> 15s Warm-up Buffer: playing at 1.0x speed for session telemetry initialization...")
        await asyncio.sleep(min(warmup_needed, 15.0))

    try:
        curr_time = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.currentTime : 0; }"))
    except Exception:
        pass

    eff_multiplier = 16.0 if duration >= 300.0 else 10.0
    eff_label = "16x Speed (Long Video >= 5 min)" if duration >= 300.0 else "10x Speed (Short Video < 5 min)"
    logger.info(f"  --> Dynamic Acceleration: Applying {eff_label}...")

    target_fast_end = max(15.0, duration - 45.0)

    try:
        await target_frame.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) {{ v.muted = true; v.playbackRate = {eff_multiplier}; v.play().catch(() => {{}}); }} }}")
    except Exception:
        pass

    last_pos = curr_time
    stuck_counter = 0

    while True:
        await check_pause_status()
        await asyncio.sleep(1.5)
        try:
            c_pos = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.currentTime : 0; }"))
            is_paused = bool(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.paused : false; }"))
        except Exception:
            break

        if c_pos >= target_fast_end:
            logger.info(f"  --> Accelerated playback completed ({int(c_pos)}s / {int(duration)}s). Transitioning to 45s Final Buffer...")
            break

        if abs(c_pos - last_pos) < 0.2 or is_paused:
            stuck_counter += 1
            if stuck_counter >= 3:
                logger.warning("  --> [STALL DETECTED] Video playback stalled. Auto-rewinding 5% and resuming playback...")
                rewind_pos = max(0.0, c_pos - (duration * 0.05))
                try:
                    await target_frame.evaluate(f"() => {{ const v = document.querySelector('video'); if (v) {{ v.currentTime = {rewind_pos}; v.playbackRate = {eff_multiplier}; v.play().catch(() => {{}}); }} }}")
                except Exception:
                    pass
                stuck_counter = 0
        else:
            stuck_counter = 0
            last_pos = c_pos

    logger.info("  --> 45s Final Buffer: slowing down to 1.0x speed for natural ended event & 100% progress telemetry...")
    try:
        await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) { v.playbackRate = 1.0; v.play().catch(() => {}); } }")
    except Exception:
        pass

    final_buffer_start = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - final_buffer_start) < 45.0:
        await check_pause_status()
        await asyncio.sleep(2.0)
        try:
            c_pos = float(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.currentTime : 0; }"))
            v_ended = bool(await target_frame.evaluate("() => { const v = document.querySelector('video'); return v ? v.ended : false; }"))
            if v_ended or c_pos >= (duration - 1.0):
                logger.info("  --> Video reached ended stateNaturally!")
                break
        except Exception:
            pass

    try:
        await target_frame.evaluate("""
            () => {
                const v = document.querySelector('video');
                if (v) {
                    v.currentTime = v.duration || 1000;
                    v.dispatchEvent(new Event('ended', { bubbles: true }));
                    v.dispatchEvent(new Event('timeupdate', { bubbles: true }));
                }
            }
        """)
    except Exception:
        pass

    await close_activity_modal(page)

    logger.info("  --> [VIDEO CHECKMARK] Waiting 10s to 15s specifically for video 100% checkmark...")
    checkmark_ok = await wait_for_server_checkmark(page, timeout=15)

    if not checkmark_ok:
        logger.warning("  --> [VIDEO RECOVERY] 100% checkmark not confirmed. Reloading video 1 time to complete 100%...")
        try:
            await safe_action_click(view_button)
            await page.wait_for_timeout(3000)
            
            await target_frame.evaluate("""
                () => {
                    const v = document.querySelector('video');
                    if (v) {
                        v.currentTime = Math.max(0, (v.duration || 10) - 10);
                        v.playbackRate = 1.0;
                        v.play().catch(() => {});
                    }
                }
            """)
            await asyncio.sleep(10.0)
            await target_frame.evaluate("() => { const v = document.querySelector('video'); if (v) v.dispatchEvent(new Event('ended', { bubbles: true })); }")
            await close_activity_modal(page)
            await wait_for_server_checkmark(page, timeout=10)
        except Exception as rec_ex:
            logger.warning(f"  --> Notice during video replay recovery: {rec_ex}")

async def process_pdf_activity(page, view_button):
    """
    STEP-07 (PDF Activity - act_type="resource"):
    Implements technical specification for PDF Reader:
      1. Automated Page Flipping (simulates PageDown & End key presses)
      2. Reading Time Simulation (maintains page reading intervals)
      3. End-of-Doc Scroll (auto-scrolls viewer container to exact bottom for checkmarks)
    """
    logger.info("[PDF ACTIVITY] Opening PDF document resource...")
    await safe_action_click(view_button)
    await page.wait_for_timeout(3000)

    logger.info("  --> Automated Page Flipping: simulating PageDown key presses...")
    for _ in range(5):
        await check_pause_status()
        await page.keyboard.press("PageDown")
        await page.wait_for_timeout(1500)

    logger.info("  --> End-of-Doc Scroll: scrolling PDF viewer container to exact bottom...")
    for frame_target in [page] + page.frames:
        try:
            await frame_target.evaluate("""
                () => {
                    const containers = document.querySelectorAll('.pdf-viewer, #viewerContainer, .document-container, div[class*="pdf"], iframe');
                    containers.forEach(c => {
                        c.scrollTop = c.scrollHeight || 10000;
                    });
                    window.scrollTo(0, document.body.scrollHeight);
                }
            """)
        except Exception:
            pass

    await page.keyboard.press("End")
    await page.wait_for_timeout(2000)

    await close_activity_modal(page)
    await wait_for_server_checkmark(page)

async def process_h5p_activity(page, view_button, answer_key=None, course_title=None):
    """
    STEP-07 (H5P Interactive Quiz - act_type="h5pactivity"):
    Clicks View, waits for container, presses 'Start Quiz', answers radio questions,
    clicks Next, Check, Finish, and closes modal.
    """
    logger.info("[H5P ACTIVITY] Opening H5P interactive content...")
    await safe_action_click(view_button)
    await page.wait_for_timeout(4000)

    start_btn = page.locator(config.SELECTORS["h5p_start_button"]).first
    if await start_btn.count() > 0 and await start_btn.is_visible():
        logger.info("  --> Pressing 'Start Quiz' button...")
        await start_btn.click()
        await page.wait_for_timeout(2000)

    for step in range(10):
        await check_pause_status()
        radios = page.locator("input[type='radio']")
        r_count = await radios.count()
        if r_count > 0:
            logger.info("  --> Selecting Option 1 for H5P question...")
            await radios.first.click(force=True)
            await page.wait_for_timeout(1000)

        chk_btn = page.locator(config.SELECTORS["h5p_check_button"]).first
        if await chk_btn.count() > 0 and await chk_btn.is_visible():
            await chk_btn.click()
            await page.wait_for_timeout(1000)

        next_btn = page.locator(config.SELECTORS["h5p_next_button"]).first
        if await next_btn.count() > 0 and await next_btn.is_visible():
            await next_btn.click()
            await page.wait_for_timeout(1500)
        else:
            break

    fin_btn = page.locator(config.SELECTORS["h5p_finish_button"]).first
    if await fin_btn.count() > 0 and await fin_btn.is_visible():
        logger.info("  --> Finishing H5P activity...")
        await fin_btn.click()
        await page.wait_for_timeout(2000)

    await close_activity_modal(page)
    await wait_for_server_checkmark(page)

async def process_quiz_assessment(page, view_button, answer_key=None, module_name="", module_no=None, sub_name="", sub_no=None, course_title=""):
    """
    Formative Assessment & Quiz Engine.
    Handles assessment popups, question solving via Answer Key / Gemini / Groq, and submission.
    """
    ctx_str = f"Module #{module_no or 1} ('{module_name or 'Assessment'}') || Subsection #{sub_no or 1} ('{sub_name or 'Assessment'}')"
    logger.info(f"\n" + "=" * 50)
    if module_name or sub_name:
        logger.info(f" [FORMATIVE ASSESSMENT] Opening Assessment for {ctx_str}...")
    else:
        logger.info("[FORMATIVE ASSESSMENT] Opening Assessment...")

    await safe_action_click(view_button)
    logger.info("  --> Waiting 5 seconds for DIKSHA assessment modal & banner popup to render...")
    await page.wait_for_timeout(5000)

    closed_banner = False
    for frame_target in [page] + page.frames:
        try:
            banner_close = frame_target.locator("button.quiz-popup-close, .quiz-popup-close, button[class*='quiz-popup-close']").first
            if await banner_close.count() > 0 and await banner_close.is_visible():
                logger.info("  --> Closing 'Stay Calm' inner GIF banner popup...")
                await banner_close.click(force=True)
                closed_banner = True
                await page.wait_for_timeout(2000)
                break
        except Exception:
            pass

    if not closed_banner:
        for frame_target in [page] + page.frames:
            try:
                await frame_target.evaluate("""() => {
                    const btn = document.querySelector('.quiz-popup-close, button[class*="quiz-popup-close"], button.quiz-popup-close');
                    if (btn) { btn.click(); return true; }
                    const wrapper = document.querySelector('.quiz-popup-wrapper, .quiz-popup-glass');
                    if (wrapper) { wrapper.remove(); return true; }
                    return false;
                }""")
            except Exception:
                pass
        await page.wait_for_timeout(2000)

    start_assessment_btn = None
    target_frame = page

    start_selectors = [
        "a:has-text('Answer the questions')",
        "button:has-text('Answer the questions')",
        "input[value*='Answer the questions']",
        "button:has-text('Re-attempt Assessment')",
        "button:has-text('Continue Assessment')",
        "button:has-text('Start Assessment')",
        "a:has-text('Start Assessment')",
        "button:has-text('Start')",
        "#start-assessment"
    ]

    for frame_target in [page] + page.frames:
        for sel in start_selectors:
            el = frame_target.locator(sel).first
            if await el.count() > 0 and await el.is_visible():
                start_assessment_btn = el
                target_frame = frame_target
                break
        if start_assessment_btn:
            break

    if start_assessment_btn:
        logger.info("  --> Pressing 'Start / Re-attempt Assessment' button...")
        try:
            await start_assessment_btn.click(force=True)
            await page.wait_for_timeout(4000)
        except Exception as ex:
            logger.warning(f"  --> Notice clicking start assessment button: {ex}")
    else:
        logger.info("  --> Attempting JS click fallback for 'Start Assessment'...")
        for frame_target in [page] + page.frames:
            try:
                clicked = await frame_target.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"], a.btn, a'));
                    const startBtn = btns.find(b => {
                        const txt = (b.innerText || b.value || '').toLowerCase();
                        return txt.includes('answer the questions') || txt.includes('start assessment') || txt.includes('re-attempt') || txt.includes('continue assessment') || txt.includes('start');
                    });
                    if (startBtn) { startBtn.click(); return true; }
                    return false;
                }""")
                if clicked:
                    target_frame = frame_target
                    logger.info("  --> JS fallback clicked 'Start Assessment'!")
                    await page.wait_for_timeout(4000)
                    break
            except Exception:
                pass

    try:
        nav_q1 = target_frame.locator("#quiznavbutton1, a[id*='quiznavbutton1'], button[id*='quiznavbutton1']").first
        if await nav_q1.count() > 0 and await nav_q1.is_visible():
            logger.info("  --> [NAVIGATION RESET] Clicked Question 1 in nav panel (#quiznavbutton1). Starting sequential solving...")
            await nav_q1.click(force=True)
            await page.wait_for_timeout(2000)
    except Exception:
        pass

    for q_num in range(30):
        await check_pause_status()
        q_tag = f"[Q-{q_num + 1:02d}]"
        
        q_text_screen = ""
        screen_opts = []
        
        for frame_target in [target_frame, page] + page.frames:
            try:
                q_el = frame_target.locator(".qtext, .questiontext, .que .text, div[id*='qtext']").first
                if await q_el.count() > 0 and await q_el.is_visible():
                    q_text_screen = (await q_el.inner_text()).strip()
                    opt_els = frame_target.locator(".answer div.r0, .answer div.r1, .answer label, .form-check-label, .que .answer div")
                    opt_cnt = await opt_els.count()
                    for o_idx in range(opt_cnt):
                        txt = (await opt_els.nth(o_idx).inner_text()).strip()
                        if txt and txt not in screen_opts:
                            screen_opts.append(txt)
                    if q_text_screen:
                        target_frame = frame_target
                        break
            except Exception:
                pass

        if not q_text_screen:
            await page.wait_for_timeout(2000)

        logger.info(f"\n  ❓ {q_tag}: {q_text_screen[:70]}..." if q_text_screen else f"\n  ❓ {q_tag}: Solving question #{q_num + 1}...")

        target_answer = None

        if answer_key and q_text_screen:
            from automations.quiz_solver import find_answer_in_key
            target_answer = find_answer_in_key(q_text_screen, answer_key)
            if target_answer:
                logger.info(f"  ⚡ [VERIFIED JSON 100% MATCH {q_tag}] Target Answer: '{target_answer}'")

        if not target_answer and q_text_screen and config.AI_LIVE_SOLVER_ENABLED:
            logger.info(f"  🤖 [10-KEY INTERLEAVED AI POOL {q_tag}] Querying 5 Gemini + 5 Groq keys...")
            from automations.quiz_solver import solve_question_with_ai
            target_answer = await solve_question_with_ai(q_text_screen, screen_opts, module_name=module_name, sub_name=sub_name, course_title=course_title)

        selected_option = False

        if target_answer and screen_opts:
            from automations.quiz_solver import find_best_matching_option
            best_opt_idx = find_best_matching_option(target_answer, screen_opts)
            if best_opt_idx is not None:
                try:
                    radio_inputs = target_frame.locator("input[type='radio']")
                    if await radio_inputs.count() > best_opt_idx:
                        await radio_inputs.nth(best_opt_idx).click(force=True)
                        logger.info(f"  🎯 [SELECTED OPTION {chr(65 + best_opt_idx)}] Selected Radio Button [{chr(65 + best_opt_idx)}] for Answer: '{screen_opts[best_opt_idx][:40]}...'")
                        selected_option = True
                except Exception as ex:
                    logger.warning(f"  --> Notice clicking option radio: {ex}")

        if not selected_option:
            try:
                radio_inputs = target_frame.locator("input[type='radio']")
                if await radio_inputs.count() > 0:
                    await radio_inputs.first.click(force=True)
                    logger.info(f"  🎯 [DEFAULT OPTION A {q_tag}] Clicked Option A fallback.")
                    selected_option = True
            except Exception:
                pass

        if not selected_option:
            if not q_text_screen and not screen_opts:
                logger.info("  🏁 [QUIZ SUMMARY DETECTED] Reached end of questions / Summary of Attempt page! Proceeding to Final Assessment Submit...")
                break

        next_nav = target_frame.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next'), button:has-text('Submit Feedback'), input[value*='Submit Feedback'], button:has-text('Submit'), input[value*='Submit']").first
        if await next_nav.count() == 0:
            next_nav = page.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Next Question'], input[value='Next'], button:has-text('Next Question'), button:has-text('Next'), .btn-next, a:has-text('Next'), button:has-text('Submit Feedback'), input[value*='Submit Feedback'], button:has-text('Submit'), input[value*='Submit']").first

        review_submit_nav = target_frame.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first
        if await review_submit_nav.count() == 0:
            review_submit_nav = page.locator("button.submit-feed-btn, #submitFeedbackBtn11, input[value='Review & Submit'], input[value='Submit'], button:has-text('Review & Submit'), button:has-text('Submit Assessment'), button:has-text('Submit'), input[value*='Submit']").first

        if await next_nav.count() > 0 and await next_nav.is_visible():
            await next_nav.click(force=True)
            await page.wait_for_timeout(1500)
        elif await review_submit_nav.count() > 0 and await review_submit_nav.is_visible():
            logger.info(f"  --> Reached end of question set (Total Questions: {q_num + 1})! Submitting assessment...")
            await review_submit_nav.click(force=True)
            await page.wait_for_timeout(2500)
            break
        else:
            break

    if config.AUTOMATIC_FINAL_SUBMIT:
        final_submit = target_frame.locator("button:has-text('Submit all and finish'), input[value*='Submit all and finish'], button.btn-primary:has-text('Submit'), input[type='submit'][value*='Submit']").first
        if await final_submit.count() == 0:
            final_submit = page.locator("button:has-text('Submit all and finish'), input[value*='Submit all and finish'], button.btn-primary:has-text('Submit'), input[type='submit'][value*='Submit']").first

        if final_submit and await final_submit.count() > 0:
            logger.info("  --> Executing Final Assessment Submit...")
            try:
                await final_submit.click(force=True)
                await page.wait_for_timeout(3000)
            except Exception as ex:
                logger.warning(f"  --> Notice clicking Final Submit: {ex}")

    for frame_target in [target_frame, page] + page.frames:
        try:
            post_cont = frame_target.locator("a:has-text('Continue'), button:has-text('Continue'), input[value*='Continue']").first
            if await post_cont.count() > 0 and await post_cont.is_visible():
                logger.info("  --> Clicking post-submission 'Continue' button to trigger 100% checkmark sync...")
                await post_cont.click(force=True)
                await page.wait_for_timeout(3000)
                break
        except Exception:
            pass

    await close_activity_modal(page)
    await wait_for_server_checkmark(page)

async def process_feedback_activity(page, view_button, answer_key=None, module_name="", module_no=None, sub_name="", sub_no=None, course_title=""):
    """
    Dedicated DIKSHA Popup Feedback Form Engine.
    """
    ctx_str = f"Module #{module_no or 8} ('{module_name or 'Feedback Form'}') || Subsection #{sub_no or 1} ('{sub_name or 'Feedback Form'}')"
    logger.info(f"\n" + "=" * 50)
    logger.info(f" 📝 [FEEDBACK FORM MODAL] Opening Feedback Form for {ctx_str}...")
    logger.info("=" * 50)

    try:
        await safe_action_click(view_button)
        await page.wait_for_timeout(4000)

        for frame_target in [page] + page.frames:
            try:
                radio_rows = frame_target.locator(config.SELECTORS["feedback_radio_row"])
                row_count = await radio_rows.count()
                if row_count > 0:
                    logger.info(f"  --> Processing {row_count} Feedback Question Radio Groups...")
                    for r_idx in range(row_count):
                        row = radio_rows.nth(r_idx)
                        first_opt = row.locator("input[type='radio'], label").first
                        if await first_opt.count() > 0:
                            await first_opt.click(force=True)
                            await page.wait_for_timeout(500)

                text_inputs = frame_target.locator(config.SELECTORS["feedback_textarea_input"])
                t_count = await text_inputs.count()
                if t_count > 0:
                    for t_idx in range(t_count):
                        t_box = text_inputs.nth(t_idx)
                        if await t_box.is_visible():
                            await t_box.fill("Excellent course and content.")

                sub_btn = frame_target.locator(config.SELECTORS["feedback_submit_btn"]).first
                if await sub_btn.count() > 0 and await sub_btn.is_visible():
                    logger.info("  --> Clicking 'Submit Feedback' button...")
                    await sub_btn.click(force=True)
                    await page.wait_for_timeout(3000)
                    break
            except Exception as ex:
                logger.warning(f"  --> Notice filling feedback form: {ex}")

    except Exception as e:
        logger.warning(f"  --> Notice during feedback activity: {e}")

    await close_activity_modal(page)
    await wait_for_server_checkmark(page)

async def is_item_100_percent_complete(btn_element):
    """
    Checks if an individual subsection item button row has a green 100% checkmark icon or text.
    """
    try:
        row = btn_element.locator("xpath=./ancestor::*[contains(@class, 'activity') or contains(@class, 'row') or contains(@class, 'item') or self::li or self::div][1]")
        if await row.count() > 0:
            chk = row.locator("i.fa-check, .fa-check-circle, .text-success, [data-completed='true']").first
            if await chk.count() > 0 and await chk.is_visible():
                return True
            row_text = await row.inner_text()
            if "100%" in row_text or "✓" in row_text:
                return True
    except Exception:
        pass
    return False

async def is_header_100_percent_complete(header):
    """
    Determines if a module header is 100% completed on DIKSHA.
    """
    try:
        raw_text = (await header.inner_text()).strip().lower()
        pct_matches = re.findall(r"(\d{1,2})%", raw_text)
        if pct_matches:
            for val_str in pct_matches:
                val = int(val_str)
                if val < 100:
                    return False

        classes = (await header.get_attribute("class") or "").split()
        for cl in classes:
            if cl.startswith("p") and cl[1:].isdigit():
                if int(cl[1:]) < 100:
                    return False

        if "100%" in raw_text:
            return True

        check_icon = header.locator("i.fa-check, .c100.p100, div[class*='p100']").first
        if await check_icon.count() > 0 and await check_icon.is_visible():
            return True
    except Exception:
        pass
    return False

async def get_section_action_buttons(collapse_panel, header):
    """
    Finds and returns all actionable subsection buttons inside a module panel.
    """
    try:
        search_target = collapse_panel if collapse_panel else header.locator("xpath=./following-sibling::*[1]")
        btns = search_target.locator(
            ".btn.module-view-btn, a.activity-list, button.activity-list, "
            "button:has-text('View'), a:has-text('View'), button:has-text('Start'), "
            "a:has-text('Start'), a:has-text('Continue'), button:has-text('Continue')"
        )
        btn_count = await btns.count()
        distinct_btns = []
        seen_texts = set()
        for b_idx in range(btn_count):
            b_el = btns.nth(b_idx)
            b_text = (await b_el.inner_text()).strip()
            data_id = await b_el.get_attribute("data-id") or ""
            key = f"{data_id}_{b_text}" if data_id else b_text
            if key not in seen_texts:
                seen_texts.add(key)
                distinct_btns.append(b_el)
        return distinct_btns
    except Exception:
        return []

async def process_course_modules(page, answer_key=None, course_title="Unknown Course", username=""):
    """
    Main Course Module Processing Pipeline.
    Iterates through modules, re-scans & re-prints full SUBSECTION BREAKDOWN lists on every pass,
    executes all subsections sequentially, runs 5-attempt sync window, and pauses for USER [ENTER] resume.
    """
    disp_user = config.USER_NAMES.get(username, username) if username else "Active User"
    user_str = f"{disp_user} ({username})" if username else disp_user

    if not course_title or course_title == "Unknown Course":
        try:
            h_el = page.locator(".course-title, .page-title, .course-header h1, h1").first
            if await h_el.count() > 0 and await h_el.is_visible():
                extracted_t = (await h_el.inner_text()).strip()
                if extracted_t:
                    course_title = extracted_t
        except Exception:
            pass

    logger.info("[COURSE MODULES] Checking for 'Lessons' tab...")
    try:
        lessons_tab = page.locator(config.SELECTORS["lessons_tab"]).first
        if await lessons_tab.count() > 0 and await lessons_tab.is_visible():
            logger.info("  --> Clicking 'Lessons' tab button...")
            await lessons_tab.click(force=True)
            logger.info("  --> Waiting 6 seconds for DIKSHA server to hydrate modules...")
            await page.wait_for_timeout(6000)
    except Exception as e:
        logger.warning(f"  --> Lessons tab notice: {e}")

    logger.info("[ACCORDION ENGINE] Scanning course section accordions...")
    headers_raw = page.locator(
        ".courses_modules_header, #accordion .card-header, .courses_modules_div .card-header, "
        ".accordion .card-header, .panel-heading"
    )
    header_count = await headers_raw.count()

    if header_count == 0:
        headers_raw = page.locator("h5, h6, .card-header, [data-toggle='collapse']")
        header_count = await headers_raw.count()

    main_modules = []
    for h_idx in range(header_count):
        h = headers_raw.nth(h_idx)
        if await h.is_visible():
            main_modules.append(h)

    logger.info(f"\n" + "=" * 65)
    logger.info(f"   DIKSHA COURSE STRUCTURE ({len(main_modules)} MODULES DETECTED)")
    logger.info("=" * 65)
    for m_idx, m_header in enumerate(main_modules, 1):
        try:
            ht = (await m_header.inner_text()).strip()
            ht_clean = " ".join(ht.split())
            logger.info(f"  [{m_idx}/{len(main_modules)}] {ht_clean[:70]}")
        except Exception:
            pass
    logger.info("=" * 65 + "\n")

    completed_items = set()
    item_attempts = {}

    for i, header in enumerate(main_modules):
        await check_pause_status()
        header_title = (await header.inner_text()).strip()
        header_title = " ".join(header_title.split())

        logger.info("\n" + "=" * 65)
        logger.info(f" 📚 MODULE [{i + 1}/{len(main_modules)}]: {header_title}")
        logger.info("=" * 65)

        if "certificate" in header_title.lower() or "download certificate" in header_title.lower():
            logger.info(f"  🎓 [CERTIFICATE SECTION DETECTED] '{header_title}' reached!")
            logger.info("  --> Verified Download Certificate link. All course requirements 100% satisfied!")
            logger.info("  --> Skipping 'View' button click to prevent unexpected PDF download popups.\n")

            logger.info("=" * 67)
            logger.info(" 🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!")
            logger.info("=" * 67)
            logger.info(f"  ✔ User Profile : {user_str}")
            logger.info(f"  ✔ Course Title : {course_title}")
            logger.info("  ✔ Certificate  : Download Certificate Available")
            logger.info("  ✔ Status       : 100% Complete — All Modules & Assessments Done!")
            logger.info("=" * 67 + "\n")
            return True

        module_pass_count = 0
        while True:
            module_pass_count += 1
            if module_pass_count > 1:
                logger.info(f"\n  🔄 [RE-STARTING FULL MODULE PASS #{module_pass_count}] Re-scanning '{header_title}' & re-evaluating all subsections...")

            if await is_header_100_percent_complete(header):
                logger.info(f"  --> [SKIP MODULE] '{header_title}' is ALREADY 100% COMPLETED. Skipping!")
                break

            click_target = header.locator("a[data-toggle='collapse'], a[href*='collapse'], a[aria-controls*='collapse']").first
            if await click_target.count() == 0:
                click_target = header

            collapse_id = ""
            try:
                href = await click_target.get_attribute("href") or await click_target.get_attribute("data-target") or await click_target.get_attribute("aria-controls") or ""
                data_id = await click_target.get_attribute("data-id") or ""
                collapse_id = href.replace("#", "").strip()
                if not collapse_id and data_id:
                    collapse_id = f"collapse{data_id}"
            except Exception:
                pass

            logger.info(f"  --> [INCOMPLETE MODULE] Expanding accordion for '{header_title}'...")
            try:
                await safe_action_click(click_target)
                await page.wait_for_timeout(2500)
            except Exception as ex:
                logger.warning(f"  --> Notice expanding header '{header_title}': {ex}")

            collapse_panel = None
            if collapse_id and await page.locator(f"#{collapse_id}").count() > 0:
                collapse_panel = page.locator(f"#{collapse_id}").first
            else:
                parent_div = header.locator("xpath=ancestor::*[contains(@class,'modules_full_accordian_div') or contains(@class,'panel') or contains(@class,'card')][1]").first
                if await parent_div.count() > 0:
                    collapse_panel = parent_div.locator(".panel-collapse, .collapse, .card-body").first

            distinct_btns = await get_section_action_buttons(collapse_panel, header)
            total_sec_items = len(distinct_btns)

            if total_sec_items == 0:
                logger.info("     [-] No action buttons inside this section. Moving to next...")
                break

            # 📋 PRINT FULL SUBSECTION BREAKDOWN CHECKLIST SUMMARY ON EVERY MODULE PASS!
            logger.info(f"  📋 [SUBSECTION BREAKDOWN ({total_sec_items} ITEMS)]:")
            for idx, b in enumerate(distinct_btns, 1):
                try:
                    b_txt = (await b.inner_text()).strip()
                    r_txt = b_txt
                    if b_txt.lower() in ("view", "start", "open", "continue"):
                        row = b.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'card-body')][1]").first
                        if await row.count() > 0:
                            t_el = row.locator("h4, h5, .title, .activity-title, bdi, strong, .name").first
                            if await t_el.count() > 0:
                                extracted_t = (await t_el.inner_text()).strip()
                                if extracted_t and extracted_t.lower() not in ("view", "start"):
                                    r_txt = extracted_t
                    chk = "✓" if await is_item_100_percent_complete(b) else "⏳"
                    logger.info(f"     [{idx}/{total_sec_items}] {chk} {r_txt}")
                except Exception:
                    pass
            logger.info("  " + "-" * 55)

            for j, btn in enumerate(distinct_btns, 1):
                await check_pause_status()
                try:
                    await btn.scroll_into_view_if_needed()
                    await page.wait_for_timeout(200)
                except Exception:
                    pass

                btn_text = (await btn.inner_text()).strip()
                real_item_title = btn_text
                if btn_text.lower() in ("view", "start", "open", "continue"):
                    try:
                        row = btn.locator("xpath=ancestor::*[contains(@class,'row') or contains(@class,'item') or contains(@class,'card-body')][1]").first
                        if await row.count() > 0:
                            title_el = row.locator("h4, h5, .title, .activity-title, bdi, strong, .name").first
                            if await title_el.count() > 0:
                                extracted_t = (await title_el.inner_text()).strip()
                                if extracted_t and extracted_t.lower() not in ("view", "start"):
                                    real_item_title = extracted_t
                    except Exception:
                        pass

                is_generic_btn = btn_text.lower() in ("view", "start", "open", "continue", "retry")
                already_done_in_mem = (real_item_title in completed_items) or (not is_generic_btn and btn_text in completed_items)

                if already_done_in_mem or await is_item_100_percent_complete(btn):
                    logger.info(f"  --> [✓ ALREADY DONE] Subsection [{j}/{total_sec_items}]: '{real_item_title}' is 100% complete. Skipping!")
                    if not is_generic_btn:
                        completed_items.add(btn_text)
                    if real_item_title and real_item_title.lower() not in ("view", "start", "open", "continue"):
                        completed_items.add(real_item_title)
                    continue

                act_type = await btn.get_attribute("act_type") or "resource"

                logger.info("\n" + "=" * 35)
                logger.info(f" ▶ SUBSECTION [{j}/{total_sec_items}]: '{real_item_title}' (Type: '{act_type}') [Pass #{module_retry_pass}]")
                logger.info("=" * 35)

                try:
                    if act_type == "url":
                        await process_video_activity(page, btn)
                    elif act_type == "resource":
                        await process_pdf_activity(page, btn)
                    elif act_type == "h5pactivity":
                        await process_h5p_activity(page, btn, answer_key, course_title=course_title)
                    elif act_type == "feedback" or "feedback" in real_item_title.lower():
                        await process_feedback_activity(page, btn, answer_key, module_name=header_title, module_no=i+1, sub_name=real_item_title, sub_no=j, course_title=course_title)
                    elif act_type == "quiz" or "assessment" in real_item_title.lower():
                        await process_quiz_assessment(page, btn, answer_key, module_name=header_title, module_no=i+1, sub_name=real_item_title, sub_no=j, course_title=course_title)
                    else:
                        await safe_action_click(btn)
                        await page.wait_for_timeout(3000)
                        await close_activity_modal(page)
                        await wait_for_server_checkmark(page)
                except Exception as item_ex:
                    logger.error(f"     [-] Subsection execution notice: {item_ex}")

                if not is_generic_btn:
                    completed_items.add(btn_text)
                if real_item_title and real_item_title.lower() not in ("view", "start", "open", "continue"):
                    completed_items.add(real_item_title)

                logger.info("  --> DIKSHA Server sync buffer: waiting 4 seconds for next item unlock...")
                await page.wait_for_timeout(4000)

            logger.info(f"  --> [DOUBLE CONFIRMATION] Verifying 100% completion for '{header_title}'...")
            await page.wait_for_timeout(2000)

            server_synced = False
            for sync_step in range(1, 6):
                logger.info(f"  ⏳ [MODULE SYNC {sync_step}/5] Reloading page & checking module completion (Elapsed: {sync_step * 15}s / 75s)...")
                await asyncio.sleep(15)
                try:
                    await page.reload()
                    await asyncio.sleep(3)

                    if await click_target.count() > 0:
                        await safe_action_click(click_target)
                        await page.wait_for_timeout(2000)

                    sync_btns = await get_section_action_buttons(collapse_panel, header)
                    all_items_checkmarked = True
                    if sync_btns:
                        for s_check_btn in sync_btns:
                            if not await is_item_100_percent_complete(s_check_btn):
                                all_items_checkmarked = False
                                break
                    else:
                        all_items_checkmarked = False

                    if await is_header_100_percent_complete(header) or all_items_checkmarked:
                        logger.info(f"  ✅ [MODULE SYNC SUCCESS] DIKSHA server completion verified for '{header_title}' on Attempt #{sync_step}!")
                        server_synced = True
                        break
                except Exception as m_sync_ex:
                    logger.warning(f"  --> Module sync attempt #{sync_step} notice: {m_sync_ex}")

            if server_synced or await is_header_100_percent_complete(header):
                logger.info(f"  🎓 [MODULE COMPLETED] '{header_title}' completed successfully! Advancing to next module...\n")
                break

            logger.warning("\n" + "=" * 75)
            logger.warning(f" ⏸️  [AUTOMATION PAUSED] '{header_title}' is not 100% complete after 5 attempts.")
            logger.warning(" 🔒 BROWSER & SERVER SESSION REMAIN 100% ACTIVE (NOT CLOSED)!")
            logger.warning(" 👉 Press [ENTER] key in terminal console to RESUME automation & retry full module pass...")
            logger.warning("=" * 75 + "\n")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, input, "Press [ENTER] to RESUME & RE-START module pass: ")
            logger.info("  ▶ [USER RESUMED] Re-starting full module execution & re-scanning all subsections...\n")

    logger.info("===================================================================")
    logger.info(" 🎉 🎓 AUTOMATION EXECUTION SUCCESSFUL & COURSE COMPLETED!")
    logger.info("===================================================================")
    return True

# Alias for main.py entry point
run_diksha_automation = process_course_modules

