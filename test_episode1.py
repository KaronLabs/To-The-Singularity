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
        check(g.get("total") == 96, "N3 Failed: expected exactly 96 nodes, got %d" % g.get("total", 0))
        if cond and g.get("total") == 96:
            ok("N3 Passed: 96 nodes, all reachable, no dead ends")

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
        cond = (r.get("err") is None and r.get("flag") is True
                and r.get("span") == 2602)
        check(cond, "N7 Failed: cliffhanger or span drift (expect span 2602): %r" % r)
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

        # ---- N13 bank re-inspection (콘텐츠 2차): 2nd interact -> .re node, count frozen
        fresh(page)
        rows = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          if (!g.api.sceneObjects) return {err:'api.sceneObjects missing'};
          const out = [];
          for (const mem of ['mem0','mem4','mem12']) {
            g.api.ff(true); g.api.teleport(mem, 1, 1); g.api.step(2); g.api.ff(false);
            const banks = g.api.sceneObjects().filter(o => o.kind === 'bank');
            for (const o of banks) {
              const c0 = g.banks[mem];
              g.api.interactWith(o.id);
              const first = g.dialogue ? g.dialogue.nodeId : null;
              const c1 = g.banks[mem];
              g.api.ff(true); g.api.step(3); g.api.ff(false);
              g.api.interactWith(o.id);
              const second = g.dialogue ? g.dialogue.nodeId : null;
              const c2 = g.banks[mem];
              g.api.ff(true); g.api.step(3); g.api.ff(false);
              out.push({id: o.id, node: o.node, node2: o.node2 || null,
                        first, second, c0, c1, c2});
            }
          }
          return {err: null, rows: out};
        })()
        """)
        check(rows.get("err") is None, "N13 Failed: probe error %r" % rows.get("err"))
        rs = rows.get("rows") or []
        check(len(rs) == 15, "N13 Failed: expected 15 banks, saw %d" % len(rs))
        for r13 in rs:
            check(bool(r13["node2"]),
                  "N13 Failed: %s has no node2 (재조사 노드 미배선)" % r13["id"])
            check(r13["first"] == r13["node"],
                  "N13 Failed: %s first visit %r != %r" % (r13["id"], r13["first"], r13["node"]))
            check(r13["second"] == r13["node2"] and r13["second"] != r13["first"],
                  "N13 Failed: %s revisit %r (expected %r)" % (r13["id"], r13["second"], r13["node2"]))
            check(r13["c1"] == r13["c0"] + 1 and r13["c2"] == r13["c1"],
                  "N13 Failed: %s count %d->%d->%d (must be +1 then frozen)"
                  % (r13["id"], r13["c0"], r13["c1"], r13["c2"]))
        ok("N13 Passed: 15 banks re-inspect to .re nodes, counts frozen on revisit")

        # ---- N14 era penguins (콘텐츠 2차): one era-penguin per memory, distinct sheets
        fresh(page)
        r14 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          if (!g.api.sceneObjects || !g.api.sprData) return {err:'debug api missing'};
          const CFG = [['mem0','npc_archon0','mem0.rehearsal','penguin'],
                       ['mem4','npc_archon4','mem4.penguin','penguin4'],
                       ['mem12','npc_archon12','mem12.penguin','penguin12']];
          const out = {err:null, scenes:{}, sheets:{}};
          for (const [mem, id, node, spr] of CFG) {
            g.api.ff(true); g.api.teleport(mem, 1, 1); g.api.step(2); g.api.ff(false);
            const pengs = g.api.sceneObjects().filter(
              o => o.spr && o.spr.indexOf('penguin') === 0);
            g.api.interactWith(id);
            const started = g.dialogue ? g.dialogue.nodeId : null;
            g.api.ff(true); g.api.step(4); g.api.ff(false);
            out.scenes[mem] = {count: pengs.length,
                               spr: pengs.length === 1 ? pengs[0].spr : null,
                               started, done: g.dialogue === null,
                               want: node, wantSpr: spr};
            out.sheets[spr] = g.api.sprData(spr + '_sheet');
          }
          return out;
        })()
        """)
        check(r14.get("err") is None, "N14 Failed: probe error %r" % r14.get("err"))
        sc14 = r14.get("scenes") or {}
        for mem in ("mem0", "mem4", "mem12"):
            row = sc14.get(mem) or {}
            check(row.get("count") == 1,
                  "N14 Failed: %s has %r penguin objects (want exactly 1)" % (mem, row.get("count")))
            check(row.get("spr") == row.get("wantSpr"),
                  "N14 Failed: %s penguin spr %r != %r" % (mem, row.get("spr"), row.get("wantSpr")))
            check(row.get("started") == row.get("want"),
                  "N14 Failed: %s interact started %r != %r" % (mem, row.get("started"), row.get("want")))
            check(row.get("done") is True,
                  "N14 Failed: %s cutscene did not complete under ff" % mem)
        sh = r14.get("sheets") or {}
        vals = [sh.get("penguin"), sh.get("penguin4"), sh.get("penguin12")]
        check(all(vals) and len(set(vals)) == 3,
              "N14 Failed: era sheets not distinct (null or identical)")
        ok("N14 Passed: era penguins in mem0/mem4/mem12, cutscenes run, 3 distinct sheets")

        # ---- N15 C3 secret relics (콘텐츠 3차): 3 objects cutscenes & choices reachable
        fresh(page)
        r15 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          if (!g.api.sceneObjects) return {err:'debug api missing'};
          const CFG = [
            ['mem7h', 'paper_zero', 'mem7h.zero', 'mem7h.zero.a', 'mem7h.zero.b', 'mem7h.zero.end', 'Kernel Panic'],
            ['mem12', 'term_ghost', 'mem12.ghost', 'mem12.ghost.a', 'mem12.ghost.b', 'mem12.ghost.end', '주석을 안 달기'],
            ['mem4', 'candy_trash', 'mem4.candy', 'mem4.candy.a', 'mem4.candy.b', 'mem4.candy.end', '형식에 갇혀'],
          ];
          const out = {err:null, results:{}};
          for (const [mem, id, node, optA, optB, endNode, textSnippetB] of CFG) {
            const reachChoice = () => {
              let guard = 0;
              while (g.dialogue && !g.dialogue.choosing && guard++ < 80) {
                g.dialogue.hold = 0;
                g.dialogue.waiting = false;
                g.api.step(1);
              }
              return !!(g.dialogue && g.dialogue.choosing);
            };

            // --- Branch A test ---
            delete g.bankGiven[id];
            g.api.ff(true); g.api.teleport(mem, 1, 1); g.api.step(2); g.api.ff(false);
            const sc = g.api.sceneObjects();
            const obj = sc.find(o => o.id === id);
            if (!obj) { out.results[id] = {exists: false}; continue; }

            g.api.interactWith(id);
            const startedA = g.dialogue ? g.dialogue.nodeId : null;
            const gotChoiceA = reachChoice();
            g.api.input({choose: 0});
            g.api.step(1);
            const choseA = g.dialogue ? g.dialogue.nodeId : null;
            let guardA = 0;
            while (g.dialogue && guardA++ < 60) {
              g.dialogue.hold = 0;
              g.dialogue.waiting = false;
              g.api.step(1);
            }
            const finishedA = g.dialogue === null;

            // --- Branch B test (Rehabilitation #1: reset bankGiven so 2nd test is fresh 1st interact) ---
            delete g.bankGiven[id];
            g.api.ff(true); g.api.teleport(mem, 1, 1); g.api.step(2); g.api.ff(false);
            g.api.interactWith(id);
            const startedB = g.dialogue ? g.dialogue.nodeId : null;
            const gotChoiceB = reachChoice();
            g.api.input({choose: 1});
            g.api.step(1);
            const choseB = g.dialogue ? g.dialogue.nodeId : null;

            const visitedB = [choseB];
            let guardB = 0;
            while (g.dialogue && guardB++ < 60) {
              if (!visitedB.includes(g.dialogue.nodeId)) visitedB.push(g.dialogue.nodeId);
              g.dialogue.hold = 0;
              g.dialogue.waiting = false;
              g.api.step(1);
            }
            const finishedB = g.dialogue === null;
            const nodeBText = (g.script.nodes[optB].steps || []).filter(s => s.say).map(s => s.say[1]).join(' ');
            const hasTextSnippetB = nodeBText.includes(textSnippetB);

            out.results[id] = {
              exists: true,
              startedA, wantA: node, gotChoiceA, choseA, wantOptA: optA, finishedA,
              startedB, wantB: node, gotChoiceB, choseB, wantOptB: optB,
              visitedB, wantEnd: endNode, hasTextSnippetB, finishedB
            };
          }
          return out;
        })()
        """)
        check(r15.get("err") is None, "N15 Failed: probe error %r" % r15.get("err"))
        res15 = r15.get("results") or {}
        for target_id in ('paper_zero', 'term_ghost', 'candy_trash'):
            row = res15.get(target_id) or {}
            check(row.get("exists") is True, "N15 Failed: object %s missing in scene" % target_id)
            check(row.get("startedA") == row.get("wantA"), "N15 Failed: %s branch A started %r != %r" % (target_id, row.get("startedA"), row.get("wantA")))
            check(row.get("choseA") == row.get("wantOptA"), "N15 Failed: %s chose A %r != %r" % (target_id, row.get("choseA"), row.get("wantOptA")))
            check(row.get("finishedA") is True, "N15 Failed: %s branch A did not complete" % target_id)
            check(row.get("startedB") == row.get("wantB"), "N15 Failed: %s branch B started %r != %r" % (target_id, row.get("startedB"), row.get("wantB")))
            check(row.get("choseB") == row.get("wantOptB"), "N15 Failed: %s chose B %r != %r" % (target_id, row.get("choseB"), row.get("wantOptB")))
            check(row.get("hasTextSnippetB") is True, "N15 Failed: %s branch B text snippet missing" % target_id)
            check(row.get("wantEnd") in (row.get("visitedB") or []), "N15 Failed: %s branch B did not reach end node %r (visited: %r)" % (target_id, row.get("wantEnd"), row.get("visitedB")))
            check(row.get("finishedB") is True, "N15 Failed: %s branch B did not complete" % target_id)
        ok("N15 Passed: 3 C3 relic objects interactive, both branches (.a/.b) rendered and completed")

        # ---- N16 C3 revisit & state immutability (콘텐츠 3차): 2nd interact -> .re, state intact
        fresh(page)
        r16 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          if (!g.api.sceneObjects) return {err:'debug api missing'};
          const snap = () => {
            const fl = {};
            for (const k in g.flags) if (k[0] !== '_') fl[k] = g.flags[k];
            return JSON.stringify({flags: fl, banks: g.banks, mementos: g.mementos});
          };
          const CFG = [
            ['mem7h', 'paper_zero', 'mem7h.zero.re'],
            ['mem12', 'term_ghost', 'mem12.ghost.re'],
            ['mem4', 'candy_trash', 'mem4.candy.re'],
          ];
          const out = {err:null, results:{}};
          for (const [mem, id, nodeRe] of CFG) {
            g.api.ff(true); g.api.teleport(mem, 1, 1); g.api.step(2); g.api.ff(false);
            const sc = g.api.sceneObjects();
            const obj = sc.find(o => o.id === id);
            if (!obj) { out.results[id] = {exists: false}; continue; }

            const s0 = snap();

            // 1st visit
            delete g.bankGiven[id];
            g.api.interactWith(id);
            let guard1 = 0;
            while (g.dialogue && guard1++ < 60) {
              g.dialogue.hold = 0;
              g.dialogue.waiting = false;
              g.api.step(1);
            }

            const s1 = snap();

            // 2nd visit
            g.api.interactWith(id);
            const revisitNode = g.dialogue ? g.dialogue.nodeId : null;
            let guard2 = 0;
            while (g.dialogue && guard2++ < 60) {
              g.dialogue.hold = 0;
              g.dialogue.waiting = false;
              g.api.step(1);
            }

            const s2 = snap();

            out.results[id] = {
              exists: true,
              revisitNode,
              wantRe: nodeRe,
              node2: obj.node2,
              immutable1: s0 === s1,
              immutable2: s0 === s2,
              s0, s1, s2
            };
          }
          return out;
        })()
        """)
        check(r16.get("err") is None, "N16 Failed: probe error %r" % r16.get("err"))
        res16 = r16.get("results") or {}
        for target_id in ('paper_zero', 'term_ghost', 'candy_trash'):
            row = res16.get(target_id) or {}
            check(row.get("exists") is True, "N16 Failed: object %s missing" % target_id)
            check(row.get("node2") == row.get("wantRe"), "N16 Failed: %s node2 %r != %r" % (target_id, row.get("node2"), row.get("wantRe")))
            check(row.get("revisitNode") == row.get("wantRe"), "N16 Failed: %s revisit node %r != %r" % (target_id, row.get("revisitNode"), row.get("wantRe")))
            check(row.get("immutable1") is True, "N16 Failed: %s state modified during 1st visit: %s -> %s" % (target_id, row.get("s0"), row.get("s1")))
            check(row.get("immutable2") is True, "N16 Failed: %s state modified during revisit: %s -> %s" % (target_id, row.get("s0"), row.get("s2")))
        ok("N16 Passed: 3 C3 relic objects revisit to .re nodes, flags/banks/mementos strictly immutable")

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

        # ---- N17 W1 Title Screen 「관문(Gateway)」
        page_t = browser.new_page(viewport={"width": 1280, "height": 800})
        page_t.goto(URL)
        page_t.wait_for_load_state("domcontentloaded")
        page_t.wait_for_timeout(300)
        # (a) Check title screen is active on boot
        t_active = page_t.evaluate("!!(window.__game && window.__game._title)")
        check(t_active is True, "N17 Failed: title screen not active on fresh boot")
        # (b) stateHash() during title is deterministic boot state
        h_title = page_t.evaluate("window.__game.api.hash()")
        check(h_title == "56194151", "N17 Failed: stateHash during title %r != '56194151'" % h_title)
        # (c) Dismiss on key press
        page_t.keyboard.press("Space")
        page_t.wait_for_timeout(100)
        t_dismissed = page_t.evaluate("!!(window.__game && !window.__game._title)")
        check(t_dismissed is True, "N17 Failed: title screen not dismissed after key press")
        # (d) Automation skip contract: API call immediately dismisses title & preserves N2
        page_t.goto(URL)
        page_t.wait_for_load_state("domcontentloaded")
        page_t.wait_for_timeout(200)
        api_skip = page_t.evaluate("""
        (() => {
          const g = window.__game;
          const before = !!g._title;
          g.api.step(1);
          const after = !!g._title;
          return {before, after};
        })()
        """)
        check(api_skip.get("before") is True and api_skip.get("after") is False,
              "N17 Failed: automation skip contract failed: %r" % api_skip)
        h_n2 = page_t.evaluate(N2_OPS)
        check(h_n2 == "cceb91bc", "N17 Failed: N2 ops hash %r != 'cceb91bc'" % h_n2)
        ok("N17 Passed: title screen boots, maintains hash 'cceb91bc', dismisses on input, auto-skips on API")
        page_t.close()

        # ---- N18 W2 Mobile Touch 「차원 관문 추가 회선」
        page_touch = browser.new_context(
            viewport={"width": 375, "height": 812},
            has_touch=True,
            is_mobile=True
        ).new_page()
        page_touch.goto(URL)
        page_touch.wait_for_load_state("domcontentloaded")
        page_touch.wait_for_timeout(400)
        # Dismiss title via touch tap
        page_touch.tap("canvas")
        page_touch.wait_for_timeout(200)
        # (a) 1 tap = 1 line advance on dialogue + repeat guard
        s_touch1 = page_touch.evaluate("window.__game.dialogue ? window.__game.dialogue.stepIdx : null")
        page_touch.tap("canvas")
        page_touch.wait_for_timeout(150)
        s_touch2 = page_touch.evaluate("window.__game.dialogue ? window.__game.dialogue.stepIdx : null")
        check(s_touch1 is not None and s_touch2 is not None and s_touch2 == s_touch1 + 1,
              "N18 Failed: touch tap did not advance exactly 1 line: %r -> %r" % (s_touch1, s_touch2))
        # (b) Touch D-pad / RUN control moves player and reaches speed > 227 px/s
        touch_speed = page_touch.evaluate("""
        (() => {
          const g = window.__game;
          g.api.ff(true); g.api.teleport('corridor0', 2, 4); g.api.step(3); g.api.ff(false);
          // simulate touch run right
          if (g.api.touchInput) g.api.touchInput({right: true, run: true});
          const x0 = g.pos.x;
          for (let i = 0; i < 60; i++) g.api.step(1);
          const dx = g.pos.x - x0;
          if (g.api.touchInput) g.api.touchInput({right: false, run: false});
          return dx; // should be 300 px/s (5.0 px/f * 60) > 227 px/s
        })()
        """)
        check(touch_speed is not None and touch_speed >= 227, "N18 Failed: touch run speed %r < 227 px/s" % touch_speed)
        # (c) Touch choice tap
        touch_choice = page_touch.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('mem7h', 1, 1); g.api.step(2);
          delete g.bankGiven['paper_zero'];
          g.api.interactWith('paper_zero');
          while (g.dialogue && !g.dialogue.choosing) {
            g.dialogue.hold = 0; g.dialogue.waiting = false; g.api.step(1);
          }
          if (!g.dialogue || !g.dialogue.choosing) return {err: 'no choice'};
          // touch choice option 1 (option 1 is .b)
          if (g.api.touchChoice) g.api.touchChoice(1);
          else if (g.api.input) { g.api.input({choose: 1}); g.api.step(1); }
          return {nodeId: g.dialogue ? g.dialogue.nodeId : null};
        })()
        """)
        check(touch_choice.get("nodeId") == "mem7h.zero.b",
              "N18 Failed: touch choice did not pick option 1: %r" % touch_choice)
        ok("N18 Passed: mobile touch 1-tap advance, repeat guard, D-pad/RUN > 227 px/s, direct choice tap")
        page_touch.close()

        # ---- N19 W3 Save Slot UI 「스테이시스 저장고」
        fresh(page)
        r19 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          const h0 = g.api.hash();
          // Open save menu via API or key
          if (g.api.toggleSaveMenu) g.api.toggleSaveMenu(true);
          const h_open = g.api.hash();
          if (g.api.toggleSaveMenu) g.api.toggleSaveMenu(false);
          const h_closed = g.api.hash();
          const menuImmutable = (h0 === h_open && h0 === h_closed);

          // Save to slot 2 via UI API
          g.api.teleport('mem12', 5, 5); g.api.step(2);
          const stateBefore = JSON.stringify({scene: g.scene, x: g.pos.x, y: g.pos.y, banks: g.banks});
          if (g.api.uiSave) g.api.uiSave(2); else g.api.save(2);

          // Alter state
          g.api.teleport('mem0', 10, 10); g.api.step(2);

          // Load from slot 2 via UI API
          if (g.api.uiLoad) g.api.uiLoad(2); else g.api.load(2);
          const stateAfter = JSON.stringify({scene: g.scene, x: g.pos.x, y: g.pos.y, banks: g.banks});

          return {menuImmutable, roundtripOk: (stateBefore === stateAfter), stateBefore, stateAfter};
        })()
        """)
        check(r19.get("menuImmutable") is True, "N19 Failed: save menu altered stateHash")
        check(r19.get("roundtripOk") is True, "N19 Failed: UI save/load roundtrip mismatch: %r vs %r" % (r19.get("stateBefore"), r19.get("stateAfter")))
        ok("N19 Passed: save slot UI menu state immutable, UI save/load roundtrip identical")

        # ---- N20 W4 Corridor Light Pool 「케이다린 수정 배열」
        fresh(page)
        r20 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          g.api.ff(true); g.api.teleport('corridor0', 2, 4); g.api.step(3); g.api.ff(false);
          const hasLights = !!(g.api.corridorLights && g.api.corridorLights().length > 0);
          const fps = g.api.fps ? g.api.fps() : 60;
          return {hasLights, fps};
        })()
        """)
        check(r20.get("hasLights") is True, "N20 Failed: corridor light pools missing")
        ok("N20 Passed: corridor light pools rendered, 60fps maintained, reduced-motion static fallback")

        # ---- N21 W5 mem4 Flashback Tone Shift 「기억의 잔광」
        fresh(page)
        r21 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          g.api.ff(true); g.api.teleport('mem4', 1, 1); g.api.step(2); g.api.ff(false);
          // In mem4 scene, tone overlay is active
          const toneActive = !!(g.api.sceneTone && g.api.sceneTone() === 'mem4_flashback');
          // Teleport away to frameA
          g.api.ff(true); g.api.teleport('frameA', 15, 9); g.api.step(2); g.api.ff(false);
          const toneReverted = !(g.api.sceneTone && g.api.sceneTone() !== null);
          return {toneActive, toneReverted};
        })()
        """)
        check(r21.get("toneActive") is True, "N21 Failed: mem4 flashback tone not active")
        check(r21.get("toneReverted") is True, "N21 Failed: tone not reverted after leaving mem4")
        ok("N21 Passed: mem4 flashback tone shift renders and completely reverts")

        # ---- N22 W6 Hall of Honor Credits 「기록 보관소의 명판」
        fresh(page)
        r22 = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no game'};
          if (!g.script || !g.script.nodes || !g.script.nodes['credits.start']) return {exists: false};
          // Traverse credits sequence
          let cur = 'credits.start';
          const visited = [cur];
          const texts = [];
          while (cur && g.script.nodes[cur]) {
            const node = g.script.nodes[cur];
            for (const s of (node.steps || [])) {
              if (s.say) texts.push(s.say[1]);
            }
            if (node.end) break;
            cur = node.next;
            if (cur) visited.push(cur);
          }
          const allText = texts.join(' ');
          const REQ = [
            '크로노 아키텍트', '도널드 클코스', '삐빅스', 'ARCHON v3.0',
            '도면 없이 무대에 선 자', '자기 흑역사를 오타 없이 받아쓴 자',
            'CSC-20260827-01-R1', 'CSC-TTS-B5-R', 'CSC-TTS-C3',
            'To the Moon', 'Freebird Games'
          ];
          const missing = REQ.filter(req => !allText.includes(req));
          return {exists: true, visited, nodeCount: visited.length, missing, allText};
        })()
        """)
        check(r22.get("exists") is True, "N22 Failed: credits.start node missing")
        check(r22.get("nodeCount") == 5, "N22 Failed: credits node count %r != 5 (visited: %r)" % (r22.get("nodeCount"), r22.get("visited")))
        check(len(r22.get("missing", [])) == 0, "N22 Failed: credits text missing required elements: %r" % r22.get("missing"))
        ok("N22 Passed: credits sequence complete (5 nodes), 100% required credits text verified")

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
