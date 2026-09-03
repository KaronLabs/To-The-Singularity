# -*- coding: utf-8 -*-
# TO THE SINGULARITY — Extra Mini-Game: 《60%에서 멈춤》
# E2E Playwright Acceptance Test Suite (E1 ~ E13)
import hashlib
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
        # Universal Monitors across all contexts and pages
        # -------------------------------------------------------------
        net_requests = []
        console_errors = []
        console_warnings = []

        def attach_monitors(p_target):
            def on_req(req):
                u = req.url
                if not u.startswith("file://") and not u.startswith("data:"):
                    net_requests.append(u)

            def on_console(msg):
                if msg.type == "error":
                    console_errors.append(f"[{msg.type}] {msg.text}")
                elif msg.type == "warning":
                    console_warnings.append(f"[{msg.type}] {msg.text}")

            p_target.on("request", on_req)
            p_target.on("console", on_console)

        context = browser.new_context()
        page = context.new_page()
        attach_monitors(page)

        page.goto(URL)
        page.wait_for_load_state("domcontentloaded")

        check(len(net_requests) == 0, f"E1 Failed: External requests made: {net_requests}")
        check(len(console_errors) == 0, f"E1 Failed: Console errors detected: {console_errors}")
        check(page.evaluate("() => typeof window.__game !== 'undefined'"), "E1 Failed: window.__game missing")
        ok("E1 Passed: boot, 0 external resources, clean console, window.__game exposed")

        # -------------------------------------------------------------
        # E2: Progress bar starts at 0% and advances deterministically (including step(0) baseline)
        # -------------------------------------------------------------
        page.evaluate("() => window.__game.api.reset()")
        st0 = page.evaluate("() => window.__game.api.getState()")
        check(st0["progress"] == 0.0, f"E2 Failed: initial progress should be 0, got {st0['progress']}")

        # Baseline step(0) invariant: advances exactly 1 step (n || 1)
        p_pre0 = page.evaluate("() => window.__game.api.getState().progress")
        page.evaluate("() => window.__game.api.step(0)")
        p_post0 = page.evaluate("() => window.__game.api.getState().progress")
        spd = page.evaluate("() => window.__game.api.getState().speed")
        check(abs((p_post0 - p_pre0) - spd) < 1e-9, f"E2 Failed: api.step(0) must advance exactly 1 step (speed {spd}), got {p_post0 - p_pre0}")

        page.evaluate("() => window.__game.api.reset()")
        page.evaluate("() => window.__game.api.step(30)")
        st1 = page.evaluate("() => window.__game.api.getState()")
        check(st1["progress"] > 0.0, f"E2 Failed: progress did not advance after 30 steps: {st1['progress']}")
        ok("E2 Passed: progress starts at 0.00% and advances deterministically with steps (including step(0) baseline)")

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

        # -------------------------------------------------------------
        # E9: Beak Convergence (R1)
        # -------------------------------------------------------------
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(50.0); }")
        st_b50 = page.evaluate("() => window.__game.api.getState()")
        check(abs(st_b50.get("beakHz", -1.0) - 0.0) < 1e-9, f"E9 Failed: beakHz at 50% should be 0.0, got {st_b50.get('beakHz')}")

        page.evaluate("() => window.__game.api.setProgress(70.0)")
        st_b70 = page.evaluate("() => window.__game.api.getState()")
        check(abs(st_b70.get("beakHz", -1.0) - 0.0) < 1e-9, f"E9 Failed: beakHz at 70% should be 0.0, got {st_b70.get('beakHz')}")

        page.evaluate("() => window.__game.api.setProgress(55.0)")
        st_b55 = page.evaluate("() => window.__game.api.getState()")
        check(abs(st_b55.get("beakHz", -1.0) - 1.28) < 1e-9, f"E9 Failed: beakHz at 55% should be 1.28, got {st_b55.get('beakHz')}")

        page.evaluate("() => window.__game.api.setProgress(60.0)")
        st_b60 = page.evaluate("() => window.__game.api.getState()")
        check(abs(st_b60.get("beakHz", -1.0) - 2.56) < 1e-9, f"E9 Failed: beakHz at 60% should be 2.56, got {st_b60.get('beakHz')}")

        beak_meta = page.evaluate("""() => {
            const card = document.querySelector('.art-card');
            const beak = document.getElementById('archon-beak-tremor');
            const baseImg = card ? card.querySelector('.art-img') : null;
            const baseTf = baseImg ? window.getComputedStyle(baseImg).transform : 'none';
            const hudText = document.body.textContent;
            return {
                beakExists: !!beak,
                inCard: !!(card && beak && card.contains(beak)),
                beakLoaded: !!(beak && beak.complete && beak.naturalWidth > 0),
                baseTfNone: baseTf === 'none' || baseTf === 'matrix(1, 0, 0, 1, 0, 0)',
                hudHasBeak: hudText.includes('BEAK:')
            };
        }""")
        check(beak_meta["beakExists"] and beak_meta["inCard"], "E9 Failed: #archon-beak-tremor missing in .art-card")
        check(beak_meta["beakLoaded"], "E9 Failed: #archon-beak-tremor image failed to load or has 0 naturalWidth")
        check(beak_meta["baseTfNone"], "E9 Failed: base .art-img has unexpected transform; tremor must only apply to beak")
        check(beak_meta["hudHasBeak"], "E9 Failed: HUD does not display BEAK frequency indicator")
        ok("E9 Passed: beak convergence (50/70 -> 0Hz, 55 -> 1.28Hz, 60 -> 2.56Hz), image loaded, base img untransformed")

        # -------------------------------------------------------------
        # E10: Conveyor Boundary & Singularity (R2)
        # -------------------------------------------------------------
        page.reload()
        page.wait_for_load_state("domcontentloaded")

        # 1. Boundary check at exact 60.50 -> count 0
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.50); }")
        st_c0 = page.evaluate("() => window.__game.api.getState()")
        check(st_c0.get("reverseConveyorPenaltyCount", 0) == 0, f"E10 Failed: conveyor triggered prematurely at exact 60.50%: {st_c0.get('reverseConveyorPenaltyCount')}")

        # 2. Crossing > 60.50 triggers exactly once
        page.evaluate("() => window.__game.api.step(1)")
        st_c1 = page.evaluate("() => window.__game.api.getState()")
        check(st_c1.get("reverseConveyorPenaltyCount", 0) == 1, f"E10 Failed: conveyor should trigger on crossing > 60.50%: {st_c1.get('reverseConveyorPenaltyCount')}")

        phase_0 = page.evaluate("() => ({ dom: document.querySelector('main').dataset.reverseConveyorPhase, state: window.__game.api.getState().reverseConveyorPhase })")
        check(phase_0["dom"] == "outbound" and phase_0["state"] == "outbound", f"E10 Failed: immediate phase should be outbound, got dom={phase_0['dom']}, state={phase_0['state']}")

        # 3. Same attempt late steps and late interrupt do not increase trigger count
        page.evaluate("() => { window.__game.api.step(5); window.__game.api.interrupt(); }")
        st_c2 = page.evaluate("() => window.__game.api.getState()")
        check(st_c2.get("reverseConveyorPenaltyCount", 0) == 1, f"E10 Failed: conveyor re-triggered within same attempt: {st_c2.get('reverseConveyorPenaltyCount')}")

        # 4. Clean run to measure dynamic timing and transforms at 350ms, 550ms, 700ms, 1300ms
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.start(); window.__game.api.setProgress(60.50); window.__game.api.step(1); }")
        page.wait_for_timeout(350)
        sample_350 = page.evaluate(r"""() => {
            const main = document.querySelector('main');
            const style = window.getComputedStyle(main);
            const tf = style.transform;
            let tx = 0;
            if (tf && tf !== 'none') {
                const m = tf.match(/matrix\(([^)]+)\)/);
                if (m) {
                    const parts = m[1].split(',').map(s => parseFloat(s.trim()));
                    tx = parts[4] || 0;
                }
            }
            return { tx: tx, vw: window.innerWidth, tf: tf };
        }""")
        check(abs(sample_350["tx"]) >= sample_350["vw"], f"E10 Failed: main horizontal translation at 350ms ({sample_350['tx']}px) does not exceed viewport width ({sample_350['vw']}px)")

        page.wait_for_timeout(200) # 350 + 200 = 550ms
        phase_550 = page.evaluate("() => ({ dom: document.querySelector('main').dataset.reverseConveyorPhase, state: window.__game.api.getState().reverseConveyorPhase })")
        check(phase_550["dom"] == "returning" and phase_550["state"] == "returning", f"E10 Failed: phase at 550ms should be returning, got {phase_550}")

        page.wait_for_timeout(150) # 550 + 150 = 700ms
        sample_700 = page.evaluate(r"""() => {
            const main = document.querySelector('main');
            const style = window.getComputedStyle(main);
            const tf = style.transform;
            let tx = 0;
            if (tf && tf !== 'none') {
                const m = tf.match(/matrix\(([^)]+)\)/);
                if (m) {
                    const parts = m[1].split(',').map(s => parseFloat(s.trim()));
                    tx = parts[4] || 0;
                }
            }
            return { tx: tx, vw: window.innerWidth, tf: tf };
        }""")
        check(abs(sample_700["tx"]) >= sample_700["vw"], f"E10 Failed: main horizontal translation at 700ms ({sample_700['tx']}px) does not exceed viewport width ({sample_700['vw']}px)")
        check(sample_350["tx"] * sample_700["tx"] < 0, f"E10 Failed: translation at 350ms ({sample_350['tx']}) and 700ms ({sample_700['tx']}) should have opposite signs")

        page.wait_for_timeout(600) # 700 + 600 = 1300ms
        sample_1300 = page.evaluate("""() => {
            const main = document.querySelector('main');
            const style = window.getComputedStyle(main);
            const tf = style.transform;
            const bodyScroll = document.body.scrollWidth <= window.innerWidth;
            const docScroll = document.documentElement.scrollWidth <= window.innerWidth;
            return {
                domPhase: main.dataset.reverseConveyorPhase,
                statePhase: window.__game.api.getState().reverseConveyorPhase,
                tfNone: tf === 'none' || tf === 'matrix(1, 0, 0, 1, 0, 0)',
                noHScroll: bodyScroll && docScroll
            };
        }""")
        check(sample_1300["domPhase"] == "idle" and sample_1300["statePhase"] == "idle", f"E10 Failed: phase at 1300ms should be idle, got {sample_1300}")
        check(sample_1300["tfNone"], "E10 Failed: main transform at 1300ms should be identity/none")
        check(sample_1300["noHScroll"], "E10 Failed: horizontal scroll detected on body or documentElement")

        # 5. Reset & restart re-arms single latch; subsequent steps and late interrupt do not increase count
        st_before_rearm = page.evaluate("() => window.__game.api.getState().reverseConveyorPenaltyCount")
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.start(); window.__game.api.setProgress(60.50); window.__game.api.step(1); }")
        st_c3 = page.evaluate("() => window.__game.api.getState()")
        check(st_c3.get("reverseConveyorPenaltyCount", 0) == st_before_rearm + 1, f"E10 Failed: new attempt should allow exactly 1 new trigger, got {st_c3.get('reverseConveyorPenaltyCount')}")
        # Subsequent step and late interrupt in this new attempt:
        page.evaluate("() => { window.__game.api.step(3); window.__game.api.interrupt(); }")
        st_c3_sub = page.evaluate("() => window.__game.api.getState()")
        check(st_c3_sub.get("reverseConveyorPenaltyCount", 0) == st_before_rearm + 1, f"E10 Failed: subsequent step/interrupt in new attempt increased count: {st_c3_sub.get('reverseConveyorPenaltyCount')}")

        # 6. W2 Check: Direct late setProgress + interrupt without step() triggers conveyor if not yet triggered in run
        st_before_late = page.evaluate("() => window.__game.api.getState().reverseConveyorPenaltyCount")
        page.evaluate("() => { window.__game.api.reset(); window.__game.api.start(); window.__game.api.setProgress(75.0); window.__game.api.interrupt(); }")
        st_late_trigger = page.evaluate("() => window.__game.api.getState()")
        check(st_late_trigger.get("reverseConveyorPenaltyCount", 0) == st_before_late + 1, f"E10 Failed: late setProgress + interrupt did not trigger conveyor: {st_late_trigger.get('reverseConveyorPenaltyCount')}")
        check(st_late_trigger.get("reverseConveyorPhase") == "outbound", f"E10 Failed: phase after late interrupt should be outbound, got {st_late_trigger.get('reverseConveyorPhase')}")
        ok("E10 Passed: conveyor boundary at 60.50%, phase progression, offscreen translation, restart re-arming, and late interrupt trigger")

        # -------------------------------------------------------------
        # E11: Wig Seizure Ceremony (R3)
        # -------------------------------------------------------------
        ctx11 = browser.new_context()
        p11 = ctx11.new_page()
        attach_monitors(p11)
        p11.goto(URL)
        p11.wait_for_load_state("domcontentloaded")

        # 1. Streaks 1 and 2: ceremony count remains 0
        p11.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.0); window.__game.api.interrupt(); }")
        check(p11.evaluate("() => window.__game.api.getState().wigCeremonyCount") == 0, "E11 Failed: ceremony triggered at streak 1")

        p11.evaluate("() => { window.__game.api.setProgress(60.0); window.__game.api.interrupt(); }")
        check(p11.evaluate("() => window.__game.api.getState().wigCeremonyCount") == 0, "E11 Failed: ceremony triggered at streak 2")

        # 2. Transition streak 2 -> 3 triggers ceremony
        p11.evaluate("() => { window.__game.api.setProgress(60.0); window.__game.api.interrupt(); }")
        st_w3 = p11.evaluate("() => window.__game.api.getState()")
        check(st_w3["streak"] == 3, f"E11 Failed: expected streak 3, got {st_w3['streak']}")
        check(st_w3.get("wigCeremonyCount", 0) == 1, f"E11 Failed: ceremonyCount should be 1, got {st_w3.get('wigCeremonyCount')}")
        check(st_w3["guardianUnlocked"] is True, "E11 Failed: guardianUnlocked should be true on streak 3")

        init_w = p11.evaluate("""() => {
            const wrap = document.getElementById('wig-ceremony');
            const wig = document.getElementById('judge-wig');
            const claw = document.getElementById('warden-retrieval-claw');
            const wigStyle = window.getComputedStyle(wig);
            const clawStyle = window.getComputedStyle(claw);
            return {
                wrapPhase: wrap ? wrap.dataset.wigCeremonyPhase : null,
                wigVisible: wigStyle.display !== 'none' && wigStyle.visibility !== 'hidden' && parseFloat(wigStyle.opacity || '1') > 0,
                wigTfNonIdentity: wigStyle.transform !== 'none' && wigStyle.transform !== 'matrix(1, 0, 0, 1, 0, 0)',
                clawHidden: clawStyle.display === 'none' || clawStyle.visibility === 'hidden' || parseFloat(clawStyle.opacity || '1') === 0
            };
        }""")
        check(init_w["wrapPhase"] == "descending", f"E11 Failed: initial ceremony wrap phase should be descending, got {init_w['wrapPhase']}")
        check(init_w["wigVisible"] and init_w["wigTfNonIdentity"], "E11 Failed: judge-wig should be visible with non-identity transform during descending")
        check(init_w["clawHidden"], "E11 Failed: retrieval claw should be hidden during descending phase")

        # Sample top at 250ms
        p11.wait_for_timeout(250)
        top_250 = p11.evaluate("() => document.getElementById('judge-wig').getBoundingClientRect().top")

        # Landed phase at ~600ms
        p11.wait_for_timeout(350) # 250 + 350 = 600ms
        landed_w = p11.evaluate("""() => {
            const wrap = document.getElementById('wig-ceremony');
            const wig = document.getElementById('judge-wig');
            const claw = document.getElementById('warden-retrieval-claw');
            const wigStyle = window.getComputedStyle(wig);
            const clawStyle = window.getComputedStyle(claw);
            return {
                phase: wrap ? wrap.dataset.wigCeremonyPhase : null,
                top: wig.getBoundingClientRect().top,
                wigVisible: wigStyle.display !== 'none' && wigStyle.visibility !== 'hidden',
                clawVisible: clawStyle.display !== 'none' && clawStyle.visibility !== 'hidden'
            };
        }""")
        check(landed_w["phase"] == "landed", f"E11 Failed: expected phase landed at 600ms, got {landed_w['phase']}")
        check(landed_w["top"] - top_250 >= 10, f"E11 Failed: wig did not descend by >= 10px (250ms={top_250}, 600ms={landed_w['top']})")
        check(landed_w["wigVisible"] and landed_w["clawVisible"], "E11 Failed: both wig and claw must be visible during landed phase")

        # Retrieving phase at ~900ms and ~1100ms
        p11.wait_for_timeout(300) # 600 + 300 = 900ms
        ret_900 = p11.evaluate("""() => ({
            phase: document.getElementById('wig-ceremony').dataset.wigCeremonyPhase,
            wigTop: document.getElementById('judge-wig').getBoundingClientRect().top,
            clawTop: document.getElementById('warden-retrieval-claw').getBoundingClientRect().top
        })""")
        check(ret_900["phase"] == "retrieving", f"E11 Failed: expected phase retrieving at 900ms, got {ret_900['phase']}")

        p11.wait_for_timeout(200) # 900 + 200 = 1100ms
        ret_1100 = p11.evaluate("""() => ({
            wigTop: document.getElementById('judge-wig').getBoundingClientRect().top,
            clawTop: document.getElementById('warden-retrieval-claw').getBoundingClientRect().top
        })""")
        check(ret_900["wigTop"] - ret_1100["wigTop"] >= 5, f"E11 Failed: wig did not retrieve upward by >= 5px between 900ms and 1100ms")
        check(ret_900["clawTop"] - ret_1100["clawTop"] >= 5, f"E11 Failed: claw did not retrieve upward by >= 5px between 900ms and 1100ms")

        # Idle phase at 1.8s (1800ms)
        p11.wait_for_timeout(700) # 1100 + 700 = 1800ms
        idle_w = p11.evaluate("""() => {
            const wrap = document.getElementById('wig-ceremony');
            const wig = document.getElementById('judge-wig');
            const claw = document.getElementById('warden-retrieval-claw');
            const wrapStyle = window.getComputedStyle(wrap);
            const wigStyle = window.getComputedStyle(wig);
            const clawStyle = window.getComputedStyle(claw);
            const badge = document.getElementById('guardian-badge');
            return {
                domPhase: wrap ? wrap.dataset.wigCeremonyPhase : null,
                statePhase: window.__game.api.getState().wigCeremonyPhase,
                pointerEvents: wrapStyle.pointerEvents,
                wigHidden: wigStyle.display === 'none' || wigStyle.visibility === 'hidden' || parseFloat(wigStyle.opacity || '1') === 0,
                clawHidden: clawStyle.display === 'none' || clawStyle.visibility === 'hidden' || parseFloat(clawStyle.opacity || '1') === 0,
                badgeUnlocked: badge && badge.classList.contains('unlocked')
            };
        }""")
        check(idle_w["domPhase"] == "idle" and idle_w["statePhase"] == "idle", f"E11 Failed: expected idle at 1.8s, got dom={idle_w['domPhase']}, state={idle_w['statePhase']}")
        check(idle_w["pointerEvents"] == "none", f"E11 Failed: wig ceremony wrapper should have pointer-events: none, got {idle_w['pointerEvents']}")
        check(idle_w["wigHidden"] and idle_w["clawHidden"], "E11 Failed: wig and claw should be hidden in idle phase")
        check(idle_w["badgeUnlocked"], "E11 Failed: Guardian badge should remain unlocked after ceremony concludes")

        # 3. 4th streak does not replay ceremony
        p11.evaluate("() => { window.__game.api.setProgress(60.0); window.__game.api.interrupt(); }")
        check(p11.evaluate("() => window.__game.api.getState().wigCeremonyCount") == 1, "E11 Failed: ceremony replayed on 4th consecutive streak")
        ctx11.close()

        # 4. Pre-stored Guardian in localStorage still fires ceremony on new session 2 -> 3
        ctx11_stor = browser.new_context()
        p11_stor = ctx11_stor.new_page()
        attach_monitors(p11_stor)
        p11_stor.goto(URL)
        p11_stor.wait_for_load_state("domcontentloaded")
        p11_stor.evaluate("() => localStorage.setItem('tts_extra_escaflone', JSON.stringify({ guardian: true, streak: 5 }))")
        p11_stor.reload()
        p11_stor.wait_for_load_state("domcontentloaded")
        check(p11_stor.evaluate("() => window.__game.api.getState().guardianUnlocked") is True, "E11 Failed: pre-stored guardian title not recognized on load")
        p11_stor.evaluate("""() => {
            window.__game.api.reset();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
        }""")
        check(p11_stor.evaluate("() => window.__game.api.getState().wigCeremonyCount") == 1, "E11 Failed: pre-stored Guardian title erroneously suppressed ceremony on streak 2->3 in new session")
        ctx11_stor.close()

        # 5. Ceremony race test: api.reset() called during in-flight ceremony does not abort completion
        ctx11_race = browser.new_context()
        p11_race = ctx11_race.new_page()
        attach_monitors(p11_race)
        p11_race.goto(URL)
        p11_race.wait_for_load_state("domcontentloaded")
        p11_race.evaluate("""() => {
            window.__game.api.reset();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt();
            window.__game.api.setProgress(60.0); window.__game.api.interrupt(); // streak 3 reached, ceremony starts
            window.__game.api.reset(); // reset called immediately while ceremony is in-flight
        }""")
        check(p11_race.evaluate("() => window.__game.api.getState().wigCeremonyPhase") in ["descending", "landed", "retrieving"], "E11 Failed: api.reset() prematurely aborted in-flight ceremony")
        p11_race.wait_for_timeout(600)
        check(p11_race.evaluate("() => window.__game.api.getState().wigCeremonyPhase") in ["landed", "retrieving"], "E11 Failed: ceremony did not advance to landed/retrieving after reset")
        p11_race.wait_for_timeout(1200)
        check(p11_race.evaluate("() => window.__game.api.getState().wigCeremonyPhase") == "idle", "E11 Failed: ceremony did not conclude at idle after reset")
        check(p11_race.evaluate("() => window.__game.api.getState().guardianUnlocked") is True, "E11 Failed: Guardian badge lost after reset race")
        ctx11_race.close()
        ok("E11 Passed: wig seizure ceremony (2->3 trigger, spatial phases, pointer-events none, 4th streak guard, localStorage decoupling, reset race safety)")

        # -------------------------------------------------------------
        # E12: Podoongi Acorn Triage (R4)
        # -------------------------------------------------------------
        page.reload()
        page.wait_for_load_state("domcontentloaded")

        # 1. Initial balance & stopped click rejection (inviolability of all state fields)
        st_p0 = page.evaluate("() => window.__game.api.getState()")
        check(st_p0.get("acorns", 0) == 3, f"E12 Failed: initial acorns should be 3, got {st_p0.get('acorns')}")

        pre_stop_ui = page.evaluate("""() => {
            window.__game.api.reset();
            const btn = document.getElementById('podoongi-btn');
            return {
                text: btn.textContent,
                disabled: btn.disabled,
                state: window.__game.api.getState()
            };
        }""")
        check(pre_stop_ui["state"]["running"] is False, "E12 Failed: api.reset() did not set running=false")

        page.click("#podoongi-btn")
        post_stop_ui = page.evaluate("""() => {
            const btn = document.getElementById('podoongi-btn');
            return {
                text: btn.textContent,
                disabled: btn.disabled,
                state: window.__game.api.getState()
            };
        }""")
        check(post_stop_ui["state"]["acorns"] == 3, f"E12 Failed: clicking while stopped deducted acorn: {post_stop_ui['state']['acorns']}")
        check(post_stop_ui["state"]["podoongiArmed"] is False, "E12 Failed: podoongi armed while stopped")
        check(post_stop_ui["state"]["autoInterruptCount"] == 0, "E12 Failed: autoInterruptCount changed while stopped")
        check(post_stop_ui["state"]["lastInterruptSource"] is None, "E12 Failed: lastInterruptSource changed while stopped")
        check(post_stop_ui["state"]["progress"] == 0.0, "E12 Failed: progress changed while stopped")
        check(post_stop_ui["state"]["status"] == "READY", "E12 Failed: status changed while stopped")
        check(post_stop_ui["state"]["streak"] == 0, "E12 Failed: streak changed while stopped")
        check(post_stop_ui["text"] == pre_stop_ui["text"], "E12 Failed: button text changed on rejected stopped click")
        check(post_stop_ui["disabled"] == pre_stop_ui["disabled"], "E12 Failed: button disabled state changed on rejected stopped click")

        # 2. Synchronous intercept execution (single evaluate, zero await)
        r12_sync = page.evaluate("""() => {
            const g = window.__game;
            g.api.start();
            g.api.setProgress(59.85);

            const btn = document.getElementById('podoongi-btn');
            btn.click();

            const armedAcorns = g.acorns;
            const armedFlag = g.podoongiArmed;
            const cutout = document.getElementById('podoongi-cutout');
            const ctrlc = document.getElementById('ctrl-c-btn');
            const cutoutPreStyle = window.getComputedStyle(cutout);
            const preVisible = cutoutPreStyle.display !== 'none' && cutoutPreStyle.visibility !== 'hidden';
            const prePressed = ctrlc.classList.contains('pressed');

            // Cross 60.00 deterministically
            g.api.step(1);

            const postState = g.api.getState();
            const cutoutPostStyle = window.getComputedStyle(cutout);
            const postVisible = cutoutPostStyle.display !== 'none' && cutoutPostStyle.visibility !== 'hidden';

            return {
                armedAcorns: armedAcorns,
                armedFlag: armedFlag,
                preVisible: preVisible,
                prePressed: prePressed,
                postProgress: postState.progress,
                postStatus: postState.status,
                postSource: postState.lastInterruptSource,
                postAutoCount: postState.autoInterruptCount,
                postAcorns: postState.acorns,
                postArmed: postState.podoongiArmed,
                postVisible: postVisible
            };
        }""")
        check(r12_sync["armedAcorns"] == 2 and r12_sync["armedFlag"] is True, "E12 Failed: acorn not deducted or not armed on click")
        check(not r12_sync["preVisible"] and not r12_sync["prePressed"], "E12 Failed: cutout visible or Ctrl+C pressed before 60.00 crossing")
        check(r12_sync["postProgress"] == 60.0, f"E12 Failed: progress not locked to 60.00, got {r12_sync['postProgress']}")
        check(r12_sync["postStatus"] == "EXIT_0", f"E12 Failed: status should be EXIT_0, got {r12_sync['postStatus']}")
        check(r12_sync["postSource"] == "podoongi", f"E12 Failed: lastInterruptSource should be podoongi, got {r12_sync['postSource']}")
        check(r12_sync["postAutoCount"] == 1, f"E12 Failed: autoInterruptCount should be 1, got {r12_sync['postAutoCount']}")
        check(r12_sync["postAcorns"] == 2, f"E12 Failed: acorns should remain 2 after intercept, got {r12_sync['postAcorns']}")
        check(r12_sync["postArmed"] is False, "E12 Failed: podoongiArmed should be false after intercept")
        check(r12_sync["postVisible"], "E12 Failed: podoongi cutout should be visible upon intercept")

        # 3. Same attempt second click is rejected without deducting acorn or altering armed state
        double_click_res = page.evaluate("""() => {
            const g = window.__game;
            g.api.start();
            g.api.setProgress(50.0);
            const btn = document.getElementById('podoongi-btn');
            btn.click(); // first click arms
            const ac1 = g.acorns;
            const armed1 = g.podoongiArmed;
            const auto1 = g.autoInterruptCount;

            btn.click(); // second click should be rejected
            const ac2 = g.acorns;
            const armed2 = g.podoongiArmed;
            const auto2 = g.autoInterruptCount;

            return { ac1: ac1, ac2: ac2, armed1: armed1, armed2: armed2, auto1: auto1, auto2: auto2 };
        }""")
        check(double_click_res["ac1"] == double_click_res["ac2"], f"E12 Failed: second click in same attempt deducted acorn: {double_click_res}")
        check(double_click_res["armed2"] is True, "E12 Failed: second click altered armed state")
        check(double_click_res["auto1"] == double_click_res["auto2"], "E12 Failed: second click altered autoInterruptCount")

        # 4. Late reservation when progress >= 60 is rejected
        late_res = page.evaluate("""() => {
            const g = window.__game;
            g.api.start();
            g.api.setProgress(60.0);
            const btn = document.getElementById('podoongi-btn');
            const ac_pre = g.acorns;
            btn.click();
            const ac_post60 = g.acorns;
            const armed_post60 = g.podoongiArmed;

            g.api.setProgress(65.0);
            btn.click();
            const ac_post65 = g.acorns;
            const armed_post65 = g.podoongiArmed;

            return { ac_pre: ac_pre, ac_post60: ac_post60, armed_post60: armed_post60, ac_post65: ac_post65, armed_post65: armed_post65 };
        }""")
        check(late_res["ac_pre"] == late_res["ac_post60"] == late_res["ac_post65"], f"E12 Failed: late reservation (>=60%) deducted acorn: {late_res}")
        check(late_res["armed_post60"] is False and late_res["armed_post65"] is False, "E12 Failed: late reservation armed podoongi")

        # 5. Manual interrupt disarms without refund
        page.evaluate("""() => {
            window.__game.api.start();
            window.__game.api.setProgress(50.0);
            document.getElementById('podoongi-btn').click();
        }""")
        st_armed = page.evaluate("() => window.__game.api.getState()")
        check(st_armed["podoongiArmed"] is True, "E12 Failed: arming failed for manual disarm test")
        acorns_before_manual = st_armed["acorns"]

        page.evaluate("() => window.__game.api.interrupt()")
        st_disarmed = page.evaluate("() => window.__game.api.getState()")
        check(st_disarmed["podoongiArmed"] is False, "E12 Failed: manual interrupt did not disarm podoongi")
        check(st_disarmed["lastInterruptSource"] == "manual", "E12 Failed: manual interrupt should set source to manual")
        check(st_disarmed["acorns"] == acorns_before_manual, "E12 Failed: manual interrupt must not refund acorn")

        # 6. api.start() disarms without refund
        page.evaluate("""() => {
            window.__game.api.start();
            window.__game.api.setProgress(50.0);
            document.getElementById('podoongi-btn').click();
        }""")
        acorns_before_restart = page.evaluate("() => window.__game.api.getState().acorns")
        page.evaluate("() => window.__game.api.start()")
        st_restarted = page.evaluate("() => window.__game.api.getState()")
        check(st_restarted["podoongiArmed"] is False, "E12 Failed: api.start() did not disarm podoongi")
        check(st_restarted["acorns"] == acorns_before_restart, "E12 Failed: api.start() must not refund acorn")

        # 7. api.reset() preserves acorn balance and sets lastInterruptSource = null
        page.evaluate("() => window.__game.api.reset()")
        st_reset_acorn = page.evaluate("() => window.__game.api.getState()")
        check(st_reset_acorn["acorns"] == acorns_before_restart, "E12 Failed: api.reset() altered acorn balance")
        check(st_reset_acorn["lastInterruptSource"] is None, "E12 Failed: api.reset() did not set lastInterruptSource to null")

        # 8. Exhaustion to 0 acorns guarantees 3rd streak & disables button
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        exhaust_res = page.evaluate("""() => {
            const g = window.__game;
            const btn = document.getElementById('podoongi-btn');
            const res = [];
            for (let i = 0; i < 3; i++) {
                g.api.start();
                g.api.setProgress(59.85);
                btn.click();
                g.api.step(1);
                res.push(g.api.getState());
            }
            // Attempt 4th click
            btn.click();
            const finalState = g.api.getState();
            return { steps: res, final: finalState, btnDisabled: btn.disabled || btn.getAttribute('disabled') !== null };
        }""")
        check(exhaust_res["final"]["acorns"] == 0, f"E12 Failed: acorns should be 0 after 3 uses, got {exhaust_res['final']['acorns']}")
        check(exhaust_res["final"]["autoInterruptCount"] == 3, f"E12 Failed: autoInterruptCount should be 3, got {exhaust_res['final']['autoInterruptCount']}")
        check(exhaust_res["final"]["streak"] >= 3, f"E12 Failed: streak should be >= 3, got {exhaust_res['final']['streak']}")
        check(exhaust_res["final"]["wigCeremonyCount"] == 1, f"E12 Failed: 3 successful podoongi intercepts should trigger wig ceremony, got {exhaust_res['final']['wigCeremonyCount']}")
        check(exhaust_res["btnDisabled"], "E12 Failed: podoongi button not disabled when acorns == 0")

        # 9. Exhausted state immutability across reset/start/interrupt
        exhaust_immutable = page.evaluate("""() => {
            const g = window.__game;
            g.api.reset();
            const ac_reset = g.api.getState().acorns;
            g.api.start();
            const ac_start = g.api.getState().acorns;
            g.api.interrupt();
            const ac_int = g.api.getState().acorns;
            return { ac_reset, ac_start, ac_int };
        }""")
        check(exhaust_immutable["ac_reset"] == 0 and exhaust_immutable["ac_start"] == 0 and exhaust_immutable["ac_int"] == 0, f"E12 Failed: reset/start/interrupt changed 0-acorn balance: {exhaust_immutable}")

        # 10. Only real reload restores acorns to 3
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        st_reloaded = page.evaluate("() => window.__game.api.getState()")
        check(st_reloaded["acorns"] == 3, f"E12 Failed: reload did not restore acorns to 3, got {st_reloaded['acorns']}")
        ok("E12 Passed: podoongi acorn triage (3 acorns, stopped rejection, synchronous 60.00 lock, second-click rejection, late rejection, disarm no-refund, 0 disabled & immutable, reload restore)")

        # -------------------------------------------------------------
        # E13: Asset Integrity, Mobile & Reduced-Motion (R1-R5)
        # -------------------------------------------------------------
        expected_hashes = {
            "assets/extra-escaflone/archon-beak-tremor.png": "0a9bd653eb29cce6e5caa0383a6475a7b84ceefea4b01944efdfa202e968e317",
            "assets/extra-escaflone/judge-wig.png": "dd90629cec24ce0d647d4688d0d6e84db4477e761ca9fec0dbabb85ddc61242a",
            "assets/extra-escaflone/warden-retrieval-claw.png": "8144fc1c9e5dd54b15805c16e2d652add37fdad54642b8c033c2c2670e1e4e47",
            "assets/extra-escaflone/podoongi-ctrlc.png": "86470da8baf06e582cf8e05f79c2f4629e3a7127f05035ea028ae704cb10a88d"
        }
        base_dir = HTML_PATH.parent
        for rel_path, expected_hash in expected_hashes.items():
            file_path = base_dir / rel_path
            check(file_path.exists(), f"E13 Failed: asset file does not exist: {file_path}")
            actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest().lower()
            check(actual_hash == expected_hash, f"E13 Failed: SHA-256 mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}")

        imgs_ok = page.evaluate("""() => {
            const ids = ['archon-beak-tremor', 'judge-wig', 'warden-retrieval-claw', 'podoongi-cutout'];
            return ids.map(id => {
                const el = document.getElementById(id);
                return { id: id, exists: !!el, complete: el ? el.complete : false, naturalWidth: el ? el.naturalWidth : 0 };
            });
        }""")
        for img_info in imgs_ok:
            check(img_info["exists"], f"E13 Failed: element #{img_info['id']} missing in DOM")
            check(img_info["complete"] and img_info["naturalWidth"] > 0, f"E13 Failed: element #{img_info['id']} failed to load properly: {img_info}")

        # Mobile 390x844 touch viewport
        mob_ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
        mob_page = mob_ctx.new_page()
        attach_monitors(mob_page)
        mob_page.goto(URL)
        mob_page.wait_for_load_state("domcontentloaded")

        mob_layout = mob_page.evaluate("""() => {
            const ctrlc = document.getElementById('ctrl-c-btn');
            const restart = document.getElementById('restart-btn');
            const podoongi = document.getElementById('podoongi-btn');
            const inVw = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return r.top >= 0 && r.bottom <= window.innerHeight && r.left >= 0 && r.right <= window.innerWidth;
            };
            return {
                ctrlcInVw: inVw(ctrlc),
                restartInVw: inVw(restart),
                podoongiInVw: inVw(podoongi),
                noHScroll: document.body.scrollWidth <= window.innerWidth
            };
        }""")
        check(mob_layout["ctrlcInVw"] and mob_layout["restartInVw"] and mob_layout["podoongiInVw"], f"E13 Failed: buttons not within mobile 390x844 viewport: {mob_layout}")
        check(mob_layout["noHScroll"], "E13 Failed: horizontal scroll detected on mobile 390x844 viewport")

        # Verify buttons are actually clickable in mobile 390x844 viewport
        mob_page.tap("#ctrl-c-btn")
        mob_st1 = mob_page.evaluate("() => window.__game.api.getState()")
        check(mob_st1["status"] in ["EAGAIN", "EXIT_0", "KERNEL_PANIC"], "E13 Failed: mobile tap on #ctrl-c-btn did not trigger interrupt")

        mob_page.tap("#restart-btn")
        mob_st2 = mob_page.evaluate("() => window.__game.api.getState()")
        check(mob_st2["running"] is True, "E13 Failed: mobile tap on #restart-btn did not restart pipeline")

        mob_page.tap("#podoongi-btn")
        mob_st3 = mob_page.evaluate("() => window.__game.api.getState()")
        check(mob_st3["podoongiArmed"] is True, "E13 Failed: mobile tap on #podoongi-btn did not arm podoongi")
        mob_ctx.close()

        # Reduced-motion context verification
        rm_ctx = browser.new_context(reduced_motion="reduce")
        rm_page = rm_ctx.new_page()
        attach_monitors(rm_page)
        rm_page.goto(URL)
        rm_page.wait_for_load_state("domcontentloaded")

        # 3a. Beak tremor transform none on reduced motion
        rm_page.evaluate("() => { window.__game.api.reset(); window.__game.api.setProgress(60.0); }")
        rm_beak = rm_page.evaluate("""() => {
            const beak = document.getElementById('archon-beak-tremor');
            const tf = window.getComputedStyle(beak).transform;
            const hz = window.__game.api.getState().beakHz;
            return { tf: tf, hz: hz };
        }""")
        check(abs(rm_beak["hz"] - 2.56) < 1e-9, f"E13 Failed: reduced-motion beakHz should still be 2.56, got {rm_beak['hz']}")
        check(rm_beak["tf"] == "none" or rm_beak["tf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: reduced-motion beak tremor should have transform none, got {rm_beak['tf']}")

        # 3b. Conveyor on reduced motion: static transform + [QUEUE REJECTED] receipt
        rm_page.evaluate("() => { window.__game.api.start(); window.__game.api.setProgress(60.50); window.__game.api.step(1); }") # Crosses 60.50
        rm_conveyor = rm_page.evaluate("""() => {
            const main = document.querySelector('main');
            const tf = window.getComputedStyle(main).transform;
            const count = window.__game.api.getState().reverseConveyorPenaltyCount;
            const receipt = document.getElementById('queue-receipt');
            const receiptVisible = receipt && (receipt.dataset.reducedMotion === 'true' || window.getComputedStyle(receipt).display !== 'none');
            return { tf: tf, count: count, receiptVisible: receiptVisible };
        }""")
        check(rm_conveyor["count"] == 1, f"E13 Failed: conveyor penalty count should still increment on reduced motion: {rm_conveyor['count']}")
        check(rm_conveyor["tf"] == "none" or rm_conveyor["tf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: main should not translate on reduced motion, got {rm_conveyor['tf']}")
        check(rm_conveyor["receiptVisible"], "E13 Failed: [QUEUE REJECTED] receipt not visible on reduced motion")

        # 3c. Wig ceremony on reduced motion: immediately inactive and idle
        rm_wig = rm_page.evaluate("""() => {
            const g = window.__game;
            g.api.reset();
            g.streak = 2; // set up transition 2 -> 3
            g.api.setProgress(60.0);
            g.api.interrupt();
            const ceremonyWrap = document.getElementById('wig-ceremony');
            const wig = document.getElementById('judge-wig');
            const claw = document.getElementById('warden-retrieval-claw');
            const wigTf = window.getComputedStyle(wig).transform;
            const clawTf = window.getComputedStyle(claw).transform;
            return {
                ceremonyCount: g.api.getState().wigCeremonyCount,
                phase: g.api.getState().wigCeremonyPhase,
                wrapPhase: ceremonyWrap ? ceremonyWrap.dataset.wigCeremonyPhase : null,
                wrapReducedMotion: ceremonyWrap ? ceremonyWrap.dataset.reducedMotion : null,
                wigTf: wigTf,
                clawTf: clawTf
            };
        }""")
        check(rm_wig["ceremonyCount"] == 1, f"E13 Failed: wig ceremony count should be 1 on reduced motion, got {rm_wig['ceremonyCount']}")
        check(rm_wig["phase"] == "idle" and rm_wig["wrapPhase"] == "idle", f"E13 Failed: wig ceremony phase should be idle on reduced motion, got {rm_wig}")
        check(rm_wig["wrapReducedMotion"] == "true", f"E13 Failed: wig ceremony wrapper should have data-reduced-motion=true, got {rm_wig['wrapReducedMotion']}")
        check(rm_wig["wigTf"] == "none" or rm_wig["wigTf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: judge-wig has motion transform on reduced motion: {rm_wig['wigTf']}")
        check(rm_wig["clawTf"] == "none" or rm_wig["clawTf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: warden claw has motion transform on reduced motion: {rm_wig['clawTf']}")

        # 3d. Podoongi on reduced motion: reservation shows neither cutout nor pressed button; step crossing shows both without translation
        rm_podoongi = rm_page.evaluate("""() => {
            const g = window.__game;
            g.api.start();
            g.api.setProgress(59.85);
            const btn = document.getElementById('podoongi-btn');
            btn.click(); // arm

            const cutout = document.getElementById('podoongi-cutout');
            const ctrlc = document.getElementById('ctrl-c-btn');
            const preCutoutDisp = window.getComputedStyle(cutout).display;
            const prePressed = ctrlc.classList.contains('pressed');

            // step crossing 60.00
            g.api.step(1);

            const postState = g.api.getState();
            const postCutoutStyle = window.getComputedStyle(cutout);
            const postCtrlStyle = window.getComputedStyle(ctrlc);
            const postCutoutVisible = postCutoutStyle.display !== 'none' && postCutoutStyle.visibility !== 'hidden';
            const postPressed = ctrlc.classList.contains('pressed');

            return {
                preCutoutDisp: preCutoutDisp,
                prePressed: prePressed,
                postStatus: postState.status,
                postCutoutVisible: postCutoutVisible,
                postCutoutTf: postCutoutStyle.transform,
                postPressed: postPressed,
                postCtrlTf: postCtrlStyle.transform
            };
        }""")
        check(rm_podoongi["preCutoutDisp"] == "none" and not rm_podoongi["prePressed"], f"E13 Failed: cutout visible or button pressed before crossing on reduced motion: {rm_podoongi}")
        check(rm_podoongi["postStatus"] == "EXIT_0", f"E13 Failed: podoongi step did not yield EXIT_0 on reduced motion: {rm_podoongi['postStatus']}")
        check(rm_podoongi["postCutoutVisible"] and rm_podoongi["postPressed"], "E13 Failed: cutout or pressed state missing post-crossing on reduced motion")
        check(rm_podoongi["postCutoutTf"] == "none" or rm_podoongi["postCutoutTf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: podoongi cutout has motion transform on reduced motion: {rm_podoongi['postCutoutTf']}")
        check(rm_podoongi["postCtrlTf"] == "none" or rm_podoongi["postCtrlTf"] == "matrix(1, 0, 0, 1, 0, 0)", f"E13 Failed: Ctrl+C button has motion transform on reduced motion: {rm_podoongi['postCtrlTf']}")

        rm_ctx.close()

        # 4. Clean console error & warning verification across all contexts & pages
        check(len(console_errors) == 0, f"E13 Failed: console errors were emitted across pages: {console_errors}")
        check(len(console_warnings) == 0, f"E13 Failed: console warnings were emitted across pages: {console_warnings}")
        check(len(net_requests) == 0, f"E13 Failed: external network requests were emitted across pages: {net_requests}")
        ok("E13 Passed: asset integrity (exact SHA-256 matching), mobile 390x844 layout & touch taps, reduced-motion fallbacks for beak/conveyor/wig/podoongi, clean console")

        # -------------------------------------------------------------
        # Fail-closed Suite Invariant
        # -------------------------------------------------------------
        check(len(PASSES) == 13, f"Fail-closed check failed: expected exactly 13 passed oracles, got {len(PASSES)}")

        browser.close()

    print("=======================================================")
    print("ALL EXTRA MINI-GAME CRITERIA VERIFIED")
    print(f"PASS {len(PASSES)}/13")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
