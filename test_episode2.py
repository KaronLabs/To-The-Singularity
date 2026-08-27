"""
Episode 2 E2E & Static Test Suite (test_episode2.py) — build2 (klkos rehab)
Oracles: Static + M1 ~ M22
Contract: episode2.html, window.__game, window.__game.api
Harness law: RED_OBSERVE=1 collects all failures (exit 1 if any);
strict mode aborts on first failure (exit 1). Banner prints computed count only on success.
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HTML_PATH = Path(__file__).with_name("episode2.html").resolve()
URL = HTML_PATH.as_uri()

RED_OBSERVE = os.environ.get("RED_OBSERVE") == "1"
failures = []
passed = [0]

def check(cond, msg):
    if not cond:
        if RED_OBSERVE:
            print("RED OBSERVE:", msg)
            failures.append(msg)
        else:
            raise AssertionError(msg)

def ok(msg):
    passed[0] += 1
    print("  [OK]", msg)

def test_static():
    print("--- Static Contract Inspection ---")
    if not HTML_PATH.exists():
        check(False, "Static Failed: episode2.html not found")
        return False
    content = HTML_PATH.read_text(encoding="utf-8")
    size = len(content.encode("utf-8"))
    check(size > 20000, "Static Failed: episode2.html too small (%d bytes)" % size)
    check("window.__game" in content, "Static Failed: window.__game contract missing")
    check("solveTubePuzzle" in content, "Static Failed: solveTubePuzzle API missing")
    check("setTimeout" not in content, "Static Failed: setTimeout found (determinism law)")
    check("Date.now" not in content, "Static Failed: Date.now found (determinism law)")
    check("Math.random" not in content, "Static Failed: Math.random found (determinism law)")
    ok("Static Passed: %d bytes, Ep2 contracts present, no timer/random primitives" % size)
    return True

def test_e2e():
    print("\n--- Starting Episode 2 E2E Playwright Suite ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        def fresh(pg):
            pg.goto(URL)
            pg.wait_for_load_state("domcontentloaded")
            pg.wait_for_timeout(200)

        # ---- M1 Boot & Canvas
        fresh(page)
        r1 = page.evaluate("""
        (() => {
          const g = window.__game;
          if (!g) return {err: 'no __game'};
          const cv = document.getElementById('stage');
          const res = performance.getEntriesByType('resource').length;
          return {ok: true, scene: g.scene, res, hasCanvas: !!cv};
        })()""")
        check(r1.get("ok") is True, "M1 Failed: game not booted")
        check(r1.get("hasCanvas") is True, "M1 Failed: canvas #stage missing")
        check(r1.get("res") == 0, "M1 Failed: external resources loaded (%r)" % r1.get("res"))
        check(len(console_errors) == 0, "M1 Failed: console errors: %r" % console_errors)
        ok("M1 Passed: boot, canvas, 0 external resources, clean console")

        # ---- M2 Deterministic Hash (pinned)
        fresh(page)
        r2 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.setSeed(1337); g.api.teleport('roof12', 10, 12); g.api.step(60);
          const h1 = g.api.hash();
          g.api.setSeed(1337); g.api.teleport('roof12', 10, 12); g.api.step(60);
          const h2 = g.api.hash();
          return {h1, h2, match: (h1 === h2 && !!h1 && h1 === '926f420b')};
        })()""")
        check(r2.get("match") is True, "M2 Failed: non-deterministic or mismatched hash: %r vs %r" % (r2.get("h1"), r2.get("h2")))
        ok("M2 Passed: deterministic hash '%s' (pinned)" % r2.get("h1"))

        # ---- M3 Script graph integrity: exact count, reachable, real dead-end check
        fresh(page)
        r3 = page.evaluate("""
        (() => {
          const g = window.__game, nodes = g.script.nodes;
          const keys = Object.keys(nodes);
          const ENGINE_EDGES = { 'tube_hub.puzzle.open': 'tube_hub.puzzle.cleared' };
          const roots = ['sys.index', 'roof12.start'];
          for (const sc of ['roof12','tube_hub','mem31','mem47','deep_vault']) {
            g.api.teleport(sc, 1, 1);
            for (const o of (g.sceneDef().objects || [])) {
              if (o.node) roots.push(o.node);
              if (o.node2) roots.push(o.node2);
            }
          }
          const seen = {}, q = roots.slice();
          while (q.length) {
            const cur = q.shift();
            if (!cur || seen[cur] || !nodes[cur]) continue;
            seen[cur] = true;
            const n = nodes[cur];
            if (n.next) q.push(n.next);
            if (ENGINE_EDGES[cur]) q.push(ENGINE_EDGES[cur]);
            for (const s of (n.steps || [])) if (s.choice) for (const c of s.choice) if (c[1]) q.push(c[1]);
          }
          const orphans = keys.filter(k => !seen[k]);
          const deadEnds = keys.filter(k => {
            const n = nodes[k];
            if (n.end === true || n.next) return false;
            return !(n.steps || []).some(s => !!s.choice);
          });
          return {total: keys.length, orphans, deadEnds};
        })()""")
        check(r3.get("total") == 82, "M3 Failed: node count %r != 82" % r3.get("total"))
        check(len(r3.get("orphans", ['x'])) == 0, "M3 Failed: orphan nodes: %r" % r3.get("orphans"))
        check(len(r3.get("deadEnds", ['x'])) == 0, "M3 Failed: dead-end nodes (no end/next/choice): %r" % r3.get("deadEnds"))
        ok("M3 Passed: 82 nodes, all reachable, 0 computed dead ends")

        # ---- M4 Ep1 Save Migration (REAL Ep1 key format tts_ep1_s{n})
        fresh(page)
        r4 = page.evaluate("""
        (() => {
          localStorage.clear();
          const g = window.__game;
          g.api.checkEp1Migration();
          const negBefore = !!g.flags.ep1_veteran;
          localStorage.setItem('tts_ep1_s2', JSON.stringify({
            scene: 'frameB', pos: {x: 10, y: 10},
            flags: {ep1_cliffhanger: true}, banks: {mem0: 5, mem4: 5, mem12: 5},
            mementos: ['memento_mem0','memento_mem4','memento_mem12'], era: 7
          }));
          g.api.checkEp1Migration();
          const pos = !!g.flags.ep1_veteran;
          localStorage.clear();
          return {negBefore, pos};
        })()""")
        check(r4.get("negBefore") is False, "M4 Failed: veteran flag set without any Ep1 save (vacuous grant)")
        check(r4.get("pos") is True, "M4 Failed: real-key (tts_ep1_s2) Ep1 cliffhanger save not detected")
        ok("M4 Passed: Ep1 migration reads real tts_ep1_s{n} keys; negative case clean")

        # ---- M5 Rooftop wind particles (real list) & movement
        fresh(page)
        r5 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('roof12', 5, 8); g.api.step(3);
          const wRoof = g.api.windParticles ? g.api.windParticles().length : -1;
          const x0 = g.pos.x;
          g.api.touchInput({right: true}); g.api.step(30); g.api.touchInput({right: false});
          const dx = g.pos.x - x0;
          g.api.teleport('tube_hub', 5, 8); g.api.step(3);
          const wHub = g.api.windParticles ? g.api.windParticles().length : -1;
          return {wRoof, wHub, dx};
        })()""")
        check(r5.get("wRoof", 0) > 0, "M5 Failed: no wind particles on roof12")
        check(r5.get("wHub", 1) == 0, "M5 Failed: wind particles leaked into tube_hub (%r)" % r5.get("wHub"))
        check(r5.get("dx", 0) > 2, "M5 Failed: movement delta %r <= 2 tiles" % r5.get("dx"))
        ok("M5 Passed: wind particle list real (roof %d / hub 0), movement dx=%.1f tiles" % (r5.get("wRoof"), r5.get("dx")))

        # ---- M6 Puzzle FSM: scramble -> DEADLOCK exactly; rotate resets to IDLE
        fresh(page)
        r6 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('tube_hub', 15, 10); g.api.step(2);
          g.api.openTubePuzzle();
          g.api.scrambleTubePuzzle();
          g.api.dispatchCapsule();
          const afterBad = g.api.tubePuzzleState().status;
          g.api.rotateValve(0, 0);
          const afterRot = g.api.tubePuzzleState().status;
          return {afterBad, afterRot};
        })()""")
        check(r6.get("afterBad") == "DEADLOCK", "M6 Failed: scrambled dispatch status %r != DEADLOCK" % r6.get("afterBad"))
        check(r6.get("afterRot") == "IDLE", "M6 Failed: rotate did not reset status to IDLE (%r)" % r6.get("afterRot"))
        ok("M6 Passed: FSM deadlock on scrambled grid, rotate resets to IDLE")

        # ---- M7 Puzzle: IN-GAME opening via console dialogue + BFS solve + delivery gates story
        fresh(page)
        r7 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('tube_hub', 15, 10); g.api.step(2);
          g.api.interactWith('console_tube');
          g.api.ff(true); g.api.step(5); g.api.ff(false);
          const choosing = !!(g.dialogue && g.dialogue.choosing);
          g.api.input({choose: 0});
          g.api.ff(true); g.api.step(4); g.api.ff(false);
          const opened = g.api.tubePuzzleState().active;
          const clearedBefore = !!g.flags.puzzle_tube_cleared;
          const solved = g.api.solveTubePuzzle();
          g.api.dispatchCapsule();
          const st = g.api.tubePuzzleState().status;
          g.api.step(30);
          const closed = !g.api.tubePuzzleState().active;
          const node = g.dialogue ? g.dialogue.nodeId : null;
          return {choosing, opened, clearedBefore, solved, st, closed, node,
                  cleared: !!g.flags.puzzle_tube_cleared};
        })()""")
        check(r7.get("choosing") is True, "M7 Failed: console dialogue did not reach choice")
        check(r7.get("opened") is True, "M7 Failed: puzzle did NOT open from in-game console path")
        check(r7.get("clearedBefore") is False, "M7 Failed: story cleared flag before puzzle was played")
        check(r7.get("solved") is True, "M7 Failed: BFS solver found no valid rotation assignment")
        check(r7.get("st") == "DELIVERED", "M7 Failed: dispatch after solve gave %r" % r7.get("st"))
        check(r7.get("closed") is True and r7.get("node") == "tube_hub.puzzle.cleared",
              "M7 Failed: delivery did not close overlay into cleared dialogue (node=%r)" % r7.get("node"))
        check(r7.get("cleared") is True, "M7 Failed: puzzle_tube_cleared flag not set on delivery")
        ok("M7 Passed: in-game puzzle opening, BFS solve, DELIVERED gates cleared dialogue + flag")

        # ---- M8 Era 31 objects & harpsichord voice
        fresh(page)
        r8 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('mem31', 10, 10); g.api.step(3);
          const ids = g.sceneDef().objects.map(o => o.id);
          return {hasPatch: ids.includes('patch_panel_31'), hasArchon: ids.includes('npc_archon31'),
                  voice: g.api.activeAudioVoice()};
        })()""")
        check(r8.get("hasPatch") is True, "M8 Failed: patch_panel_31 missing in mem31")
        check(r8.get("hasArchon") is True, "M8 Failed: npc_archon31 missing in mem31")
        check(r8.get("voice") == "harpsichord", "M8 Failed: harpsichord voice not active in Era 31 (%r)" % r8.get("voice"))
        ok("M8 Passed: Era 31 patch room objects and harpsichord voice")

        # ---- M9 Era 47 objects & pipe organ voice
        fresh(page)
        r9 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('mem47', 10, 10); g.api.step(3);
          const ids = g.sceneDef().objects.map(o => o.id);
          return {hasOutlet: ids.includes('chute_outlet_47'), hasArchon: ids.includes('npc_archon47'),
                  voice: g.api.activeAudioVoice()};
        })()""")
        check(r9.get("hasOutlet") is True, "M9 Failed: chute_outlet_47 missing in mem47")
        check(r9.get("hasArchon") is True, "M9 Failed: npc_archon47 missing in mem47")
        check(r9.get("voice") == "pipe_organ", "M9 Failed: pipe organ voice not active in Era 47 (%r)" % r9.get("voice"))
        ok("M9 Passed: Era 47 deep bedrock objects and pipe organ voice")

        # ---- M10 Bibix debate: wrong answer loops, correct answer grants check_256
        fresh(page)
        r10 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('deep_vault', 15, 10); g.api.step(2);
          g.api.interactWith('hologram_bibix');
          g.api.step(3);
          const choosing1 = !!(g.dialogue && g.dialogue.choosing);
          g.api.input({choose: 0});
          g.api.ff(true); g.api.step(4); g.api.ff(false);
          const afterWrongChoosing = !!(g.dialogue && g.dialogue.choosing);
          const noCheckYet = !(g.mementos.includes('check_256'));
          g.api.input({choose: 1});
          g.api.step(5);
          const hasCheck = g.mementos.includes('check_256');
          return {choosing1, afterWrongChoosing, noCheckYet, hasCheck};
        })()""")
        check(r10.get("choosing1") is True, "M10 Failed: debate did not present choices")
        check(r10.get("afterWrongChoosing") is True, "M10 Failed: wrong answer did not loop back to debate")
        check(r10.get("noCheckYet") is True, "M10 Failed: check granted on WRONG answer")
        check(r10.get("hasCheck") is True, "M10 Failed: $2.56 check not granted on correct answer")
        ok("M10 Passed: debate loops on wrong answer, $2.56 check on correct answer only")

        # ---- M11 Dialogue 1-press = 1-line (real dialogue, real text)
        fresh(page)
        r11 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('roof12', 4, 6); g.api.step(2);
          g.api.interactWith('vending_roof');
          g.api.step(2);
          const t1 = g._drawn ? g._drawn.text : '';
          g.api.step(20);
          const t2 = g._drawn ? g._drawn.text : '';
          g.api.input({interact: 1}); g.api.step(2);
          const t3 = g._drawn ? g._drawn.text : '';
          g.api.ff(true); g.api.step(10); g.api.ff(false);
          const ended = g.dialogue === null;
          g.api.interactWith('vending_roof'); g.api.step(2);
          const revisit = g.dialogue ? g.dialogue.nodeId : null;
          return {t1, t2, t3, ended, revisit};
        })()""")
        check(len(r11.get("t1", "")) > 0, "M11 Failed: no dialogue text drawn after interact")
        check(r11.get("t1") == r11.get("t2"), "M11 Failed: dialogue auto-advanced without input")
        check(r11.get("t1") != r11.get("t3"), "M11 Failed: input did not advance dialogue line")
        check(r11.get("ended") is True, "M11 Failed: dialogue did not terminate under ff")
        check(r11.get("revisit") == "roof12.vending.re", "M11 Failed: second interact gave %r, not the .re revisit node" % r11.get("revisit"))
        ok("M11 Passed: 1-press 1-line held/advanced; revisit routes to .re node")

        # ---- M12 Choice waits and renders labels
        fresh(page)
        r12 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('deep_vault', 15, 10); g.api.step(2);
          g.api.interactWith('hologram_bibix');
          g.api.step(10);
          return {choosing: !!(g.dialogue && g.dialogue.choosing),
                  labels: g._drawnChoices ? g._drawnChoices.labels.length : 0};
        })()""")
        check(r12.get("choosing") is True, "M12 Failed: dialogue did not stop in choosing mode")
        check(r12.get("labels") == 3, "M12 Failed: %r choice labels rendered (want 3)" % r12.get("labels"))
        ok("M12 Passed: choice waits for explicit input, 3 labels rendered")

        # ---- M13 Fixed timestep refresh independence (WITH movement, accumulator-driven)
        fresh(page)
        r13 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('roof12', 2, 8); g.api.step(2);
          g.api.touchInput({right: true});
          let t = 1000.0;
          window.__gameLoop(t);
          for (let i = 0; i < 60; i++) { t += 16.667; window.__gameLoop(t); }
          const d60 = g.pos.x - 2;
          g.api.teleport('roof12', 2, 8);
          for (let i = 0; i < 120; i++) { t += 8.333; window.__gameLoop(t); }
          const d120 = g.pos.x - 2;
          g.api.touchInput({right: false});
          return {d60, d120, ratio: d120 / (d60 || 1)};
        })()""")
        check(r13.get("d60", 0) > 1.5, "M13 Failed: vacuous test — no movement measured (d60=%r)" % r13.get("d60"))
        check(abs(r13.get("ratio", 9) - 1.0) <= 0.06, "M13 Failed: 60Hz vs 120Hz ratio %r drifted" % r13.get("ratio"))
        ok("M13 Passed: real movement %.1f vs %.1f tiles, ratio %.3f" % (r13.get("d60"), r13.get("d120"), r13.get("ratio")))

        # ---- M14 Save/Load full-hash roundtrip
        fresh(page)
        r14 = page.evaluate("""
        (() => {
          const g = window.__game;
          localStorage.clear();
          g.api.teleport('mem31', 6, 7); g.api.step(2);
          g.api.save(2);
          const h0 = g.api.hash();
          g.api.teleport('roof12', 3, 3); g.api.step(2);
          g.flags.puzzle_tube_cleared = true;
          const moved = g.api.hash() !== h0;
          const okLoad = g.api.load(2);
          return {moved, okLoad, match: g.api.hash() === h0, scene: g.scene};
        })()""")
        check(r14.get("moved") is True, "M14 Failed: state hash did not change after perturbation (vacuous)")
        check(r14.get("okLoad") is True, "M14 Failed: load(2) returned false")
        check(r14.get("match") is True and r14.get("scene") == "mem31", "M14 Failed: full-hash roundtrip mismatch")
        ok("M14 Passed: save/load full state-hash roundtrip identical")

        # ---- M15 REAL mobile touch: D-pad, RUN, tap-advance (TouchEvent on has_touch context)
        mctx = browser.new_context(viewport={"width": 375, "height": 812}, has_touch=True, is_mobile=True)
        mpg = mctx.new_page()
        mpg.goto(URL)
        mpg.wait_for_load_state("domcontentloaded")
        mpg.wait_for_timeout(300)
        r15 = mpg.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.step(1);
          g.api.teleport('roof12', 4, 8); g.api.step(2);
          const cv = document.getElementById('stage');
          const r = cv.getBoundingClientRect();
          const at = (mx, my, type) => {
            const cx = r.left + mx * r.width / 480, cy = r.top + my * r.height / 270;
            const t = new Touch({identifier: 1, target: cv, clientX: cx, clientY: cy});
            const ev = new TouchEvent(type, {touches: type === 'touchend' ? [] : [t],
                                             changedTouches: [t], bubbles: true, cancelable: true});
            cv.dispatchEvent(ev);
          };
          const wait = ms => new Promise(res => setTimeout(res, ms));
          const x0 = g.pos.x;
          at(58, 232, 'touchstart'); await wait(400); at(58, 232, 'touchend');
          const walked = g.pos.x - x0;
          at(100, 253, 'touchstart'); at(100, 253, 'touchend');
          const runOn = g.api.touchState ? g.api.touchState().run : null;
          const x1 = g.pos.x;
          at(58, 232, 'touchstart'); await wait(400); at(58, 232, 'touchend');
          const ran = g.pos.x - x1;
          g.api.interactWith('vending_roof'); g.api.step(30); // let the typewriter finish the line
          const s0 = g.dialogue ? g.dialogue.stepIdx : -9;
          at(240, 120, 'touchstart'); at(240, 120, 'touchend');
          g.api.step(2);
          const s1 = g.dialogue ? g.dialogue.stepIdx : -9;
          return {walked, ran, runOn, s0, s1};
        })()""")
        mctx.close()
        check(r15.get("walked", 0) > 1.0, "M15 Failed: real D-pad touch moved %r tiles" % r15.get("walked"))
        check(r15.get("runOn") is True, "M15 Failed: RUN toggle did not engage on real touch")
        check(r15.get("ran", 0) > r15.get("walked", 99) * 1.5, "M15 Failed: RUN speed %r not > 1.5x walk %r" % (r15.get("ran"), r15.get("walked")))
        check(r15.get("s1") == r15.get("s0", -9) + 1, "M15 Failed: real tap did not advance dialogue by exactly 1 (%r -> %r)" % (r15.get("s0"), r15.get("s1")))
        ok("M15 Passed: REAL touch D-pad %.1ft, RUN x%.1f, tap-advance +1" % (r15.get("walked"), r15.get("ran") / max(r15.get("walked"), 0.001)))

        # ---- M16 Autoplay bot: real traversal (walk + interact + puzzle), honest span
        fresh(page)
        r16 = page.evaluate("""
        (() => {
          const g = window.__game;
          const r = g.api.autoplay(6000);
          return {reached: !!g.flags.ep2_cliffhanger, span: r.span, scene: g.scene,
                  puzzleCleared: !!g.flags.puzzle_tube_cleared};
        })()""")
        check(r16.get("reached") is True, "M16 Failed: bot did not reach ep2_cliffhanger")
        check(r16.get("span", 0) >= 60, "M16 Failed: span %r < 60 — bot is not actually traversing" % r16.get("span"))
        check(r16.get("scene") == "deep_vault", "M16 Failed: bot ended in %r, not deep_vault" % r16.get("scene"))
        check(r16.get("puzzleCleared") is True, "M16 Failed: bot bypassed the tube puzzle")
        ok("M16 Passed: autoplay bot walked/interacted/solved puzzle to ep2_cliffhanger (span %r frames)" % r16.get("span"))

        # ---- M17 fps instrument responds to fed frame timing (kills hardcoded gauges)
        fresh(page)
        r17 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('deep_vault', 15, 10); g.api.step(2);
          let t = 5000.0;
          window.__gameLoop(t);
          for (let i = 0; i < 61; i++) { t += 16.667; window.__gameLoop(t); }
          const f60 = g.api.fps();
          for (let i = 0; i < 41; i++) { t += 33.333; window.__gameLoop(t); }
          const f30 = g.api.fps();
          return {f60, f30};
        })()""")
        check(55 <= r17.get("f60", 0) <= 62, "M17 Failed: fed 60Hz but instrument reads %r" % r17.get("f60"))
        check(25 <= r17.get("f30", 0) <= 35, "M17 Failed: fed 30Hz but instrument reads %r (hardcoded gauge?)" % r17.get("f30"))
        ok("M17 Passed: fps instrument measures reality (60Hz->%r, 30Hz->%r)" % (r17.get("f60"), r17.get("f30")))

        # ---- M18 Reduced motion: flag honored AND particles actually stop
        fresh(page)
        page.emulate_media(reduced_motion="reduce")
        r18 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('roof12', 10, 10); g.api.step(2);
          return {reduced: !!g.flags.reducedMotion, particles: g.api.windParticles ? g.api.windParticles().length : -1};
        })()""")
        page.emulate_media(reduced_motion="no-preference")
        check(r18.get("reduced") is True, "M18 Failed: reducedMotion flag not honored")
        check(r18.get("particles", 1) == 0, "M18 Failed: %r particles still emitted under reduced motion" % r18.get("particles"))
        ok("M18 Passed: reduced-motion flag set and particle emission is zero")

        # ---- M19 Credits: 5 nodes, required text, no self-awarded medals
        fresh(page)
        r19 = page.evaluate("""
        (() => {
          const g = window.__game;
          if (!g.script.nodes['credits.start']) return {exists: false};
          let cur = 'credits.start', count = 0;
          const texts = [];
          while (cur && g.script.nodes[cur]) {
            count++;
            const node = g.script.nodes[cur];
            for (const s of (node.steps || [])) if (s.say) texts.push(s.say[1]);
            if (node.end) break;
            cur = node.next;
          }
          const allText = texts.join(' ');
          const REQ = ['크로노 아키텍트', '도널드 클코스', 'ARCHON', '각주 47개와 4차원 서류 슈트', 'To the Moon'];
          return {exists: true, count, missing: REQ.filter(q => !allText.includes(q)),
                  selfAward: allText.includes('명예의 전당 훈장')};
        })()""")
        check(r19.get("exists") is True, "M19 Failed: credits.start missing")
        check(r19.get("count") == 5, "M19 Failed: credits chain %r nodes != 5" % r19.get("count"))
        check(len(r19.get("missing", ['x'])) == 0, "M19 Failed: credits missing required text: %r" % r19.get("missing"))
        check(r19.get("selfAward") is False, "M19 Failed: self-awarded medals present in credits")
        ok("M19 Passed: credits 5 nodes, required text present, no self-awarded medals")

        # ---- M20 Automation skip contract (title AND modal UI)
        fresh(page)
        r20 = page.evaluate("""
        (() => {
          const g = window.__game;
          const titleBefore = g._title;
          g._saveMenu = true;
          g.api.step(1);
          return {titleBefore, titleAfter: g._title, menuAfter: g._saveMenu};
        })()""")
        check(r20.get("titleBefore") is True, "M20 Failed: title not active on fresh boot")
        check(r20.get("titleAfter") is False, "M20 Failed: API call did not auto-skip title")
        check(r20.get("menuAfter") is False, "M20 Failed: API call did not auto-dismiss save menu (art.9)")
        ok("M20 Passed: automation skip contract dismisses title and modal UI")

        # ---- M21 Save menu UI: REAL keyboard save/load path
        fresh(page)
        page.evaluate("localStorage.clear(); window.__game.api.step(1);")
        page.evaluate("(() => { const g = window.__game; g.api.teleport('mem47', 10, 10); g.api.step(2); })()")
        page.keyboard.press('m'); page.wait_for_timeout(80)
        m_open = page.evaluate("window.__game._saveMenu")
        page.keyboard.press('ArrowDown'); page.wait_for_timeout(60)
        sel = page.evaluate("window.__game._saveSel")
        page.keyboard.press('Enter'); page.wait_for_timeout(80)
        slot2 = page.evaluate("!!localStorage.getItem('tts_ep2_slot_2')")
        page.keyboard.press('Escape'); page.wait_for_timeout(60)
        m_closed = page.evaluate("!window.__game._saveMenu")
        page.evaluate("(() => { const g = window.__game; g.api.teleport('roof12', 3, 3); g.api.step(2); })()")
        page.keyboard.press('m'); page.wait_for_timeout(60)
        page.keyboard.press('l'); page.wait_for_timeout(100)
        r21 = page.evaluate("({scene: window.__game.scene, x: window.__game.pos.x, menu: window.__game._saveMenu})")
        check(m_open is True, "M21 Failed: M key did not open save menu")
        check(sel == 2, "M21 Failed: ArrowDown did not select slot 2 (sel=%r)" % sel)
        check(slot2 is True, "M21 Failed: Enter did not save to slot 2 via UI")
        check(m_closed is True, "M21 Failed: Escape did not close menu")
        check(r21.get("scene") == "mem47" and abs(r21.get("x", 0) - 10) < 1, "M21 Failed: L did not load slot state (%r)" % r21)
        ok("M21 Passed: real-key save menu — navigate, save, close, load all functional")

        # ---- M22 Play-reachability: every node reachable through actual gameplay edges
        fresh(page)
        r22 = page.evaluate("""
        (() => {
          const g = window.__game, nodes = g.script.nodes;
          const TRANSITIONS = {
            'roof12.to_hub': 'tube_hub.start',
            'tube_hub.to_mem31': 'mem31.start',
            'mem31.to_mem47': 'mem47.start',
            'mem47.to_deep_vault': 'deep_vault.start',
            'tube_hub.puzzle.open': 'tube_hub.puzzle.cleared'
          };
          const roots = ['roof12.start'];
          for (const sc of ['roof12','tube_hub','mem31','mem47','deep_vault']) {
            g.api.teleport(sc, 1, 1);
            for (const o of (g.sceneDef().objects || [])) {
              if (o.node) roots.push(o.node);
              if (o.node2) roots.push(o.node2);
            }
          }
          const seen = {}, q = roots.slice();
          while (q.length) {
            const cur = q.shift();
            if (!cur || seen[cur] || !nodes[cur]) continue;
            seen[cur] = true;
            const n = nodes[cur];
            if (n.next) q.push(n.next);
            if (TRANSITIONS[cur]) q.push(TRANSITIONS[cur]);
            for (const s of (n.steps || [])) if (s.choice) for (const c of s.choice) if (c[1]) q.push(c[1]);
          }
          const dead = Object.keys(nodes).filter(k => !seen[k] && k !== 'sys.index');
          return {dead, reachable: Object.keys(seen).length};
        })()""")
        check(len(r22.get("dead", ['x'])) == 0,
              "M22 Failed: %d nodes unreachable in actual play: %r" % (len(r22.get("dead", [])), r22.get("dead")))
        ok("M22 Passed: all %d content nodes reachable through real gameplay" % r22.get("reachable", 0))

        check(len(console_errors) == 0, "PostSuite Failed: console errors during suite: %r" % console_errors)
        browser.close()

if __name__ == "__main__":
    ok_static = test_static()
    if ok_static:
        try:
            test_e2e()
        except AssertionError as e:
            print("\nFAILED:", e)
            sys.exit(1)
    if failures:
        print("\n" + "=" * 55)
        print("RED FAILURES: %d collected" % len(failures))
        print("=" * 55)
        sys.exit(1)
    print("\n" + "=" * 55)
    print("ALL Ep2 CRITERIA VERIFIED")
    print("PASS %d/%d" % (passed[0], passed[0]))
    print("=" * 55)
    sys.exit(0)
