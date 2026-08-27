# -*- coding: utf-8 -*-
# TO THE SINGULARITY Ep1 acceptance net (N1..N9) — TDD RED first.
# Contract: design.md section 6 (window.__game). Modes as in stairs suite:
#   python test_episode1.py                 strict (first failure aborts)
#   RED_OBSERVE=1 python test_episode1.py   collect all failures
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

HTML_PATH = Path(__file__).with_name("episode1.html").resolve()
URL = HTML_PATH.as_uri()

OBSERVE = os.environ.get("RED_OBSERVE") == "1"
FAILURES = []
PASSES = []


def check(cond, msg):
    if cond:
        return True
    if OBSERVE:
        FAILURES.append(msg)
        print("  [RED] " + msg)
        return False
    raise AssertionError(msg)


def ok(label):
    PASSES.append(label)
    print(label)


# Canonical deterministic input script for N2 (runs twice on fresh loads).
N2_OPS = """
(async () => {
  const g = window.__game;
  g.api.setSeed(4242);
  g.api.ff(true);
  g.api.teleport('mem0', 6, 6);
  g.api.input({move:'R', frames:30});
  g.api.step(30);
  g.api.input({move:'D', frames:18});
  g.api.step(18);
  g.api.input({interact:1});
  g.api.step(12);
  g.api.step(60);
  return g.api.hash();
})()
"""

GRAPH_WALK = """
(() => {
  const s = window.__game.script;
  if (!s || !s.nodes) return {err:'no script'};
  const nodes = s.nodes;
  const ids = Object.keys(nodes);
  const missing = [], deadEnds = [];
  const edges = {};
  for (const id of ids) {
    const n = nodes[id];
    const out = [];
    if (n.next) out.push(n.next);
    for (const st of (n.steps || [])) {
      if (st && st.choice) for (const c of st.choice) out.push(c[1]);
    }
    for (const t of out) if (!nodes[t]) missing.push(id + ' -> ' + t);
    if (!out.length && !n.end) deadEnds.push(id);
    edges[id] = out;
  }
  const seen = new Set(['frameA.start']);
  const q = ['frameA.start'];
  while (q.length) {
    const id = q.pop();
    for (const t of (edges[id] || [])) if (!seen.has(t)) { seen.add(t); q.push(t); }
  }
  const orphans = ids.filter(id => !seen.has(id));
  return {err: null, total: ids.length, missing, deadEnds, orphans,
          hasEntry: !!nodes['frameA.start']};
})()
"""


def fresh(page):
    page.goto(URL)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(400)


def test_static():
    exists = os.path.isfile(HTML_PATH)
    if not check(exists, "Static Failed: episode1.html does not exist"):
        return False
    raw = open(HTML_PATH, "rb").read()
    check(len(raw) > 0, "Static Failed: empty file")
    check(not raw.startswith(b"\xef\xbb\xbf"), "Static Failed: UTF-8 BOM present")
    content = raw.decode("utf-8")
    check("window.__game" in content, "Static Failed: __game debug contract missing")
    check("setInterval" not in content, "Static Failed: setInterval used (rAF/step only)")
    ok("Static Passed: %d bytes, contract token present" % len(raw))
    return True


def test_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        # ---- N1 boot
        fresh(page)
        ver = page.evaluate("window.__game ? window.__game.version : null")
        check(ver == "ep1", "N1 Failed: __game.version = %r" % ver)
        has_canvas = page.evaluate("!!document.querySelector('canvas')")
        check(has_canvas, "N1 Failed: no canvas")
        res = page.evaluate("performance.getEntriesByType('resource').length")
        check(res == 0, "N1 Failed: resource entries %d != 0" % res)
        check(not errors, "N1 Failed: console/page errors: %r" % errors[:3])
        ok("N1 Passed: boot, canvas, resources 0, console clean")

        # ---- N10 dialogue must NOT auto-advance; one keypress = one line
        # (regression for the reported double-advance bug)
        page.wait_for_timeout(700)   # let the first line's typewriter finish
        s1 = page.evaluate("window.__game.dialogue ? [window.__game.dialogue.nodeId, window.__game.dialogue.stepIdx] : null")
        page.wait_for_timeout(1500)
        s2 = page.evaluate("window.__game.dialogue ? [window.__game.dialogue.nodeId, window.__game.dialogue.stepIdx] : null")
        check(s1 is not None and s1 == s2,
              "N10 Failed: dialogue advanced by itself: %r -> %r" % (s1, s2))
        # render-level oracle (court order CSC-20260827-01 / rehab #1):
        # the string actually drawn on canvas must be the script's current say.
        says = page.evaluate(
            "window.__game.script.nodes['frameA.start'].steps"
            ".filter(s => s.say).map(s => s.say[1])")
        r1 = page.evaluate("window.__game._drawn ? window.__game._drawn.text : null")
        check(r1 == says[0],
              "N10 Failed: first RENDERED line %r != script first say %r" % (r1, says[0]))
        page.keyboard.press("e")
        page.wait_for_timeout(600)
        s3 = page.evaluate("[window.__game.dialogue.nodeId, window.__game.dialogue.stepIdx]")
        check(s3 != s2, "N10 Failed: keypress did not advance dialogue: %r" % (s3,))
        r2 = page.evaluate("window.__game._drawn ? window.__game._drawn.text : null")
        check(r2 == says[1],
              "N10 Failed: after 1 press rendered %r != script second say %r" % (r2, says[1]))
        page.wait_for_timeout(900)
        s4 = page.evaluate("[window.__game.dialogue.nodeId, window.__game.dialogue.stepIdx]")
        check(s3 == s4, "N10 Failed: drift after keypress: %r -> %r" % (s3, s4))
        r3 = page.evaluate("window.__game._drawn ? window.__game._drawn.text : null")
        check(r2 == r3, "N10 Failed: rendered line drifted with no input: %r -> %r" % (r2, r3))
        ok("N10 Passed: no auto-advance; 1 press = 1 line (state AND rendered string)")

        # ---- N11 choices must wait for human input; both branches reachable
        def reach_choice():
            fresh(page)
            for _ in range(60):
                page.keyboard.press("e")
                page.wait_for_timeout(70)
                if page.evaluate(
                        "!!(window.__game.dialogue && window.__game.dialogue.choosing)"):
                    return True
            return False

        got = reach_choice()
        check(got, "N11 Failed: choosing state never appeared on the human path "
                   "(choice auto-picks without input)")
        if got:
            node0 = page.evaluate("window.__game.dialogue.nodeId")
            page.wait_for_timeout(900)
            still = page.evaluate(
                "window.__game.dialogue && window.__game.dialogue.choosing"
                " ? window.__game.dialogue.nodeId : null")
            check(still == node0,
                  "N11 Failed: choice did not hold for input: %r -> %r" % (node0, still))
            ui = page.evaluate("window.__game._drawnChoices")
            check(bool(ui) and len(ui.get("labels", [])) == 2 and ui.get("sel") == 0,
                  "N11 Failed: choice UI not rendered: %r" % (ui,))
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(80)
            sel = page.evaluate("window.__game.dialogue.choosing.sel")
            check(sel == 1, "N11 Failed: ArrowDown did not move selection: %r" % (sel,))
            page.keyboard.press("e")
            page.wait_for_timeout(150)
            nb = page.evaluate("window.__game.dialogue ? window.__game.dialogue.nodeId : null")
            check(nb == "frameA.contract.b",
                  "N11 Failed: confirm did not branch to option 1: %r" % (nb,))
            got_a = reach_choice()
            check(got_a, "N11 Failed: could not re-reach choice for branch 0")
            if got_a:
                page.keyboard.press("e")
                page.wait_for_timeout(150)
                na = page.evaluate(
                    "window.__game.dialogue ? window.__game.dialogue.nodeId : null")
                check(na == "frameA.contract.a",
                      "N11 Failed: default confirm did not branch to option 0: %r" % (na,))
                ok("N11 Passed: choice waits for input; E -> .a, ArrowDown+E -> .b; UI rendered")

        # ---- N2 determinism (two fresh runs, same seed+ops -> same hash)
        h1 = page.evaluate(N2_OPS) if ver == "ep1" else None
        fresh(page)
        h2 = page.evaluate(N2_OPS) if ver == "ep1" else None
        check(h1 is not None and h1 == h2, "N2 Failed: hashes differ %r vs %r" % (h1, h2))
        ok("N2 Passed: deterministic hash %r" % h1)

        # ---- N3 dialogue graph integrity
        g = page.evaluate(GRAPH_WALK)
        cond = (g.get("err") is None and g.get("hasEntry")
                and not g.get("missing") and not g.get("deadEnds") and not g.get("orphans"))
        check(cond, "N3 Failed: graph broken: %r" % {k: g.get(k) for k in
              ("err", "hasEntry", "missing", "deadEnds", "orphans")})
        if cond:
            ok("N3 Passed: %d nodes, all reachable, no dead ends" % g.get("total", 0))

        # ---- N4 progression invariants
        fresh(page)
        r = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          g.api.ff(true);
          g.api.teleport('mem0', 0, 0);
          g.api.interactWith('memento_mem0');
          g.api.step(30);
          const early = g.mementos.slice();
          for (let i = 0; i < 4; i++) g.api.grantBank('mem0');
          g.api.interactWith('memento_mem0');
          g.api.step(30);
          const atFour = { mementos: g.mementos.slice(), puzzleOpen: !!g.puzzle };
          g.api.grantBank('mem0');
          g.api.interactWith('memento_mem0');
          g.api.step(30);
          g.api.solvePuzzle();
          g.api.step(30);
          const late = g.mementos.slice();
          const diveEarlyBlocked = !g.api.canDive('mem0_to_mem4_without');
          return {err:null, early, atFour, late, banks:g.banks.mem0};
        })()
        """)
        four = r.get("atFour") or {}
        cond = (r.get("err") is None and r.get("early") == []
                and four.get("mementos") == [] and four.get("puzzleOpen") is False
                and "mem0" in (r.get("late") or []))
        check(cond, "N4 Failed: invariants: %r" % r)
        if cond:
            ok("N4 Passed: memento locked at 0/5 and 4/5, opens at 5/5 (banks=%s)" % r.get("banks"))

        # ---- N5 crowbar corridor (comply / speed / still)
        outcomes = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          const run = (profile) => {
            g.api.ff(true);
            g.api.teleport('corridor0', 2, 4);
            g.api.resetCorridor();
            if (profile === 'walk') { g.api.input({move:'R', frames:600}); g.api.step(600); }
            if (profile === 'run')  { g.api.input({move:'R', frames:600, run:true}); g.api.step(600); }
            if (profile === 'still'){ g.api.step(600); }
            return !!g.flags.corridor_pass;
          };
          return {err:null, walk: run('walk'), run: run('run'), still: run('still')};
        })()
        """)
        cond = (outcomes.get("err") is None and outcomes.get("walk") is True
                and outcomes.get("run") is False and outcomes.get("still") is False)
        check(cond, "N5 Failed: corridor outcomes %r" % outcomes)
        if cond:
            ok("N5 Passed: crowbar walk=pass, run=fail, still=fail")

        # ---- N6 save/load roundtrip
        r = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          g.api.teleport('mem0', 9, 9);
          g.flags.testmark = 7;
          g.api.save(1);
          const h1 = g.api.hash();
          g.api.teleport('frameA', 1, 1);
          g.flags.testmark = 99;
          g.api.load(1);
          const h2 = g.api.hash();
          return {err:null, h1, h2};
        })()
        """)
        cond = r.get("err") is None and r.get("h1") == r.get("h2")
        check(cond, "N6 Failed: save/load hash %r" % r)
        if cond:
            ok("N6 Passed: save/load roundtrip identical")

        # ---- N7 autoplay bot completes Ep1
        fresh(page)
        r = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          g.api.setSeed(7);
          g.api.ff(true);
          const f0 = g.frame;   // frames before this point depend on wall-clock boot time
          const done = g.api.autoplay(240000);
          return {err:null, done, flag: !!g.flags.ep1_cliffhanger, frame: g.frame, span: g.frame - f0};
        })()
        """)
        cond = r.get("err") is None and r.get("flag") is True
        check(cond, "N7 Failed: autoplay did not reach cliffhanger: %r" % r)
        if cond:
            ok("N7 Passed: bot reached ep1_cliffhanger, deterministic span %s frames (total %s)"
               % (r.get("span"), r.get("frame")))

        # ---- N8 fps floor in heaviest scene (real-time render)
        page.evaluate("window.__game && window.__game.api.teleport('mem7h', 4, 4)")
        page.wait_for_timeout(2300)
        fps = page.evaluate("window.__game ? window.__game.api.fps() : 0")
        check(fps >= 30, "N8 Failed: fps %.1f < 30 in mem7h" % (fps or 0))
        ok("N8 Passed: fps = %.0f in heaviest scene" % (fps or 0))

        # ---- N9 reduced motion
        page.emulate_media(reduced_motion="reduce")
        fresh(page)
        rm = page.evaluate("window.__game ? window.__game.flags.reducedMotion === true : null")
        check(rm is True, "N9 Failed: flags.reducedMotion = %r" % rm)
        if rm is True:
            ok("N9 Passed: reduced-motion honored")
        page.emulate_media(reduced_motion="no-preference")

        # ---- N12 fixed-timestep contract: speed must not follow display refresh
        RAF_MOCK = """
        window.__rafQ = [];
        window.__vt = 0;
        window.requestAnimationFrame = function (cb) {
          window.__rafQ.push(cb); return window.__rafQ.length;
        };
        window.__pump = function (ms, n) {
          for (var i = 0; i < n; i++) {
            window.__vt += ms;
            var q = window.__rafQ; window.__rafQ = [];
            for (var j = 0; j < q.length; j++) q[j](window.__vt);
          }
        };
        """
        page2 = browser.new_page(viewport={"width": 1280, "height": 800})
        page2.add_init_script(RAF_MOCK)

        def rate_probe(hz):
            page2.goto(URL)
            page2.wait_for_load_state("domcontentloaded")
            return page2.evaluate("""
              (hz) => {
                const g = window.__game;
                g.api.ff(true);
                g.api.teleport('mem0', 1, 6);
                g.api.step(3);            // burn the onEnter dialogue under ff
                g.api.ff(false);
                g.api.input({move:'R', frames: 400});
                const x0 = g.pos.x, f0 = g.frame;
                window.__pump(1000 / hz, hz);   // exactly one simulated second
                return {dx: g.pos.x - x0, df: g.frame - f0};
              }
            """, hz)

        r60 = rate_probe(60)
        r120 = rate_probe(120)
        ratio = (r120["dx"] / r60["dx"]) if r60["dx"] else 999.0
        check(abs(ratio - 1.0) <= 0.10,
              "N12 Failed: speed follows refresh rate: 60Hz %r vs 120Hz %r (ratio %.2f)"
              % (r60, r120, ratio))
        burst = page2.evaluate(
            "(() => { const g = window.__game; const f0 = g.frame;"
            " window.__pump(3000, 1); return g.frame - f0; })()")
        check(burst <= 5, "N12 Failed: catch-up not capped: %d updates for one 3000ms tick" % burst)
        if abs(ratio - 1.0) <= 0.10 and burst <= 5:
            ok("N12 Passed: 60Hz vs 120Hz travel %spx vs %spx (ratio %.3f), catch-up capped at %d"
               % (r60["dx"], r120["dx"], ratio, burst))
        page2.close()

        browser.close()


if __name__ == "__main__":
    if test_static():
        test_e2e()
    print()
    print("=======================================================")
    if OBSERVE:
        print("OBSERVE MODE: %d passed, %d RED" % (len(PASSES), len(FAILURES)))
        for f in FAILURES:
            print("  RED:", f)
        sys.exit(1 if FAILURES else 0)
    print("ALL Ep1 CRITERIA VERIFIED")
    print("PASS %d/%d" % (len(PASSES), len(PASSES)))
    print("=======================================================")
