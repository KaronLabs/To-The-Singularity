# -*- coding: utf-8 -*-
# TO THE SINGULARITY — Extra Mini-Game: 《60%에서 멈춤》
# E2E Playwright Acceptance Test Suite (E1 ~ E8)
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_PATH = Path(__file__).with_name("extra_escaflone.html").resolve()
URL = HTML_PATH.as_uri()

FAILURES = []
PASSES = []

def check(cond, msg):
    if cond:
        return True
    FAILURES.append(msg)
    print("  [FAIL] " + msg)
    raise AssertionError(msg)

def ok(label):
    PASSES.append(label)
    print("  [OK] " + label)

def run_tests():
    print("=======================================================")
    print("EXTRA MINI-GAME: 《60%에서 멈춤》 E2E SUITE")
    print("=======================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # E1: Boot, 0 external requests, clean console, window.__game exposed
        # -------------------------------------------------------------
        net_requests = []
        console_errors = []

        context = browser.new_context()
        page = context.new_page()

        def on_req(req):
            u = req.url
            if not u.startswith("file://") and not u.startswith("data:"):
                net_requests.append(u)

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("request", on_req)
        page.on("console", on_console)

        page.goto(URL)
        page.wait_for_load_state("domcontentloaded")

        check(len(net_requests) == 0, f"E1 Failed: External requests made: {net_requests}")
        check(len(console_errors) == 0, f"E1 Failed: Console errors detected: {console_errors}")
        check(page.evaluate("() => typeof window.__game !== 'undefined'"), "E1 Failed: window.__game missing")
        ok("E1 Passed: boot, 0 external resources, clean console, window.__game exposed")

        # -------------------------------------------------------------
        # E2: Progress bar starts at 0% and advances deterministically
        # -------------------------------------------------------------
        page.evaluate("() => window.__game.api.reset()")
        st0 = page.evaluate("() => window.__game.api.getState()")
        check(st0["progress"] == 0.0, f"E2 Failed: initial progress should be 0, got {st0['progress']}")
        
        page.evaluate("() => window.__game.api.step(30)")
        st1 = page.evaluate("() => window.__game.api.getState()")
        check(st1["progress"] > 0.0, f"E2 Failed: progress did not advance after 30 steps: {st1['progress']}")
        ok("E2 Passed: progress starts at 0.00% and advances deterministically with steps")

        # -------------------------------------------------------------
        # E3: Early interrupt (< 59.5%) -> EAGAIN
        # -------------------------------------------------------------
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(45.0); window.__game.api.interrupt(); }")
        st_early = page.evaluate("() => window.__game.api.getState()")
        check(st_early["status"] == "EAGAIN", f"E3 Failed: expected status EAGAIN, got {st_early['status']}")
        ok("E3 Passed: early interrupt at 45% -> EAGAIN (너무 일찍 포기함)")

        # -------------------------------------------------------------
        # E4: Late interrupt (> 60.5%) -> KERNEL_PANIC
        # -------------------------------------------------------------
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(75.0); window.__game.api.interrupt(); }")
        st_late = page.evaluate("() => window.__game.api.getState()")
        check(st_late["status"] == "KERNEL_PANIC", f"E4 Failed: expected status KERNEL_PANIC, got {st_late['status']}")
        ok("E4 Passed: late interrupt at 75% -> KERNEL_PANIC (60% 돌파 데드락)")

        # -------------------------------------------------------------
        # E5: Exact 60% interrupt (59.5% ~ 60.5%) -> EXIT_0
        # -------------------------------------------------------------
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.0); window.__game.api.interrupt(); }")
        st_exact = page.evaluate("() => window.__game.api.getState()")
        check(st_exact["status"] == "EXIT_0", f"E5 Failed: expected status EXIT_0, got {st_exact['status']}")
        check(st_exact["streak"] == 1, f"E5 Failed: expected streak 1, got {st_exact['streak']}")
        ok("E5 Passed: exact 60.00% interrupt -> EXIT_0 (완벽한 60%에서 멈춤!)")

        # -------------------------------------------------------------
        # E6: Real Keyboard & Touch [Ctrl+C] button triggering
        # -------------------------------------------------------------
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.0); }")
        page.keyboard.press("Space")
        st_kbd = page.evaluate("() => window.__game.api.getState()")
        check(st_kbd["status"] == "EXIT_0", f"E6 Failed: Spacebar did not trigger interrupt: {st_kbd['status']}")

        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.0); }")
        page.click("#ctrl-c-btn")
        st_btn = page.evaluate("() => window.__game.api.getState()")
        check(st_btn["status"] == "EXIT_0", f"E6 Failed: #ctrl-c-btn click did not trigger interrupt: {st_btn['status']}")
        ok("E6 Passed: keyboard (Space) and UI button (#ctrl-c-btn) both trigger interrupt")

        # -------------------------------------------------------------
        # E7: 3-Consecutive Streak -> Guardian of 60% title & localStorage save
        # -------------------------------------------------------------
        page.evaluate("""() => {
            window.__game.api.reset();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
        }""")
        st_streak = page.evaluate("() => window.__game.api.getState()")
        check(st_streak["streak"] >= 3, f"E7 Failed: expected streak >= 3, got {st_streak['streak']}")
        check(st_streak["guardianUnlocked"] is True, "E7 Failed: guardianUnlocked flag should be true")
        saved_raw = page.evaluate("() => localStorage.getItem('tts_extra_escaflone')")
        check(saved_raw is not None and "guardian" in saved_raw, "E7 Failed: localStorage record not saved")
        ok("E7 Passed: 3 consecutive 60% interrupts -> Guardian title unlocked & stored in localStorage")

        # -------------------------------------------------------------
        # E8: Web Audio sfx contract clean execution
        # -------------------------------------------------------------
        audio_ok = page.evaluate("() => { try { window.__game.api.playSfx('sigint'); return true; } catch(e) { return false; } }")
        check(audio_ok is True, "E8 Failed: playSfx threw error")
        ok("E8 Passed: Web Audio SFX safely executed without errors")

        browser.close()

    print("=======================================================")
    print("ALL EXTRA MINI-GAME CRITERIA VERIFIED")
    print(f"PASS {len(PASSES)}/8")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
