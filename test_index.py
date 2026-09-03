# -*- coding: utf-8 -*-
# TO THE SINGULARITY — Portal (index.html) E2E Test Suite (P1 ~ P8)
# Strict TDD Acceptance Suite
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_PATH = Path(__file__).with_name("index.html").resolve()
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
    print("PORTAL (index.html) E2E PLAYWRIGHT SUITE")
    print("=======================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # P1: Boot, 0 external network requests, clean console
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

        check(len(net_requests) == 0, f"P1 Failed: External requests made: {net_requests}")
        check(len(console_errors) == 0, f"P1 Failed: Console errors detected: {console_errors}")
        check(page.evaluate("() => typeof window.__portal !== 'undefined'"), "P1 Failed: window.__portal telemetry missing")
        ok("P1 Passed: boot, 0 external resources, clean console, window.__portal exposed")

        # -------------------------------------------------------------
        # P2: Default state (empty localStorage) -> Gauge 70.00%, seals unearned
        # -------------------------------------------------------------
        state = page.evaluate("() => window.__portal.getState()")
        check(state["gauge"] == 70.0, f"P2 Failed: expected initial gauge 70.0, got {state['gauge']}")
        check(state["seals"]["ep1"] is False, "P2 Failed: ep1 seal should be false initially")
        check(state["seals"]["ep2"] is False, "P2 Failed: ep2 seal should be false initially")
        check(state["seals"]["ep3"] is False, "P2 Failed: ep3 seal should be false initially")
        ok("P2 Passed: empty localStorage -> Gauge 70.00%, all 3 seals unearned")

        # -------------------------------------------------------------
        # P3: Ep1 save injection -> Ep1 seal active, Gauge 80.00%
        # -------------------------------------------------------------
        page.evaluate("""() => {
            localStorage.setItem('tts_ep1_s1', JSON.stringify({
                v: 1, scene: 'mem7h', flags: { ep1_cliffhanger: true }
            }));
            window.__portal.refresh();
        }""")
        state = page.evaluate("() => window.__portal.getState()")
        check(state["seals"]["ep1"] is True, "P3 Failed: ep1 seal not activated upon ep1 save")
        check(state["gauge"] == 80.0, f"P3 Failed: expected gauge 80.0, got {state['gauge']}")
        ok("P3 Passed: Ep1 save -> Ep1 seal active, Gauge 80.00%")

        # -------------------------------------------------------------
        # P4: Ep2 save injection ($2.56 check) -> Ep2 seal active, Gauge 90.00%
        # -------------------------------------------------------------
        page.evaluate("""() => {
            localStorage.setItem('tts_ep2_slot_1', JSON.stringify({
                v: 2, mementos: ['check_256'], flags: { ep2_cliffhanger: true }
            }));
            window.__portal.refresh();
        }""")
        state = page.evaluate("() => window.__portal.getState()")
        check(state["seals"]["ep2"] is True, "P4 Failed: ep2 seal not activated upon $2.56 check save")
        check(state["gauge"] == 90.0, f"P4 Failed: expected gauge 90.0, got {state['gauge']}")
        ok("P4 Passed: Ep2 save ($2.56 check) -> Ep2 seal active, Gauge 90.00%")

        # -------------------------------------------------------------
        # P5: Ep3 save injection (1 victory verdict) -> Ep3 seal active, Gauge 100.00%
        # -------------------------------------------------------------
        page.evaluate("""() => {
            localStorage.setItem('tts_ep3_s1', JSON.stringify({
                v: 1, flags: { ep3_done: true, ep3_verdict: true }
            }));
            window.__portal.refresh();
        }""")
        state = page.evaluate("() => window.__portal.getState()")
        check(state["seals"]["ep3"] is True, "P5 Failed: ep3 seal not activated upon 1 victory save")
        check(state["gauge"] == 100.0, f"P5 Failed: expected gauge 100.0, got {state['gauge']}")
        check(state["achieved"] is True, "P5 Failed: singularity achieved banner not triggered")
        ok("P5 Passed: Ep3 save -> Ep3 seal active, Gauge 100.00% (Singularity Achieved!)")

        # -------------------------------------------------------------
        # P6: Gauge tap/click -> Jiggle reaction & tap record counter
        # -------------------------------------------------------------
        initial_taps = page.evaluate("() => window.__portal.getState().tapCount")
        page.click("#gauge-container")
        after_taps = page.evaluate("() => window.__portal.getState().tapCount")
        check(after_taps == initial_taps + 1, f"P6 Failed: tap count expected {initial_taps + 1}, got {after_taps}")
        check(page.evaluate("() => window.__portal.isJiggling()"), "P6 Failed: gauge jiggle flag not set on click")
        ok("P6 Passed: gauge click -> tap registered, needle jiggle triggered")

        # -------------------------------------------------------------
        # P7: Jukebox play/pause button state transition & AudioContext activation
        # -------------------------------------------------------------
        jb_state = page.evaluate("() => window.__portal.getJukeboxState()")
        check(jb_state["playing"] is False, "P7 Failed: jukebox should be stopped initially")
        page.click("#jb-play-btn")
        jb_state_after = page.evaluate("() => window.__portal.getJukeboxState()")
        check(jb_state_after["playing"] is True, "P7 Failed: jukebox not playing after play button click")
        check(jb_state_after["ctxState"] in ["running", "suspended"], f"P7 Failed: unexpected ctxState {jb_state_after['ctxState']}")
        page.click("#jb-play-btn")
        check(page.evaluate("() => window.__portal.getJukeboxState().playing") is False, "P7 Failed: jukebox not paused after second click")
        ok("P7 Passed: jukebox play/pause button toggles state and initializes AudioContext")

        # -------------------------------------------------------------
        # P8: Footnote slider updates active voices & footnote label
        # -------------------------------------------------------------
        for fn, expected_label in [
            (0, "각주 0개 · 뮤직박스 단선율"),
            (4, "각주 4개 · 베이스 보강"),
            (12, "각주 12개 · 아르페지오 편곡"),
            (31, "각주 31개 · 하프시코드 앙상블"),
            (47, "각주 47개 · 파이프오르간 풀 코랄")
        ]:
            page.evaluate(f"() => window.__portal.setFootnotes({fn})")
            jb_cur = page.evaluate("() => window.__portal.getJukeboxState()")
            check(jb_cur["footnotes"] == fn, f"P8 Failed: expected footnote {fn}, got {jb_cur['footnotes']}")
            check(expected_label in jb_cur["label"], f"P8 Failed: expected label '{expected_label}', got '{jb_cur['label']}'")

        ok("P8 Passed: footnote slider modulation across 0, 4, 12, 31, 47 accurately shifts voices and labels")

        browser.close()

    print("=======================================================")
    print("ALL PORTAL CRITERIA VERIFIED")
    print(f"PASS {len(PASSES)}/8")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
