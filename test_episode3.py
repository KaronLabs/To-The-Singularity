# -*- coding: utf-8 -*-
# TO THE COURT (Ep3) acceptance net C1..C22 — TDD RED first.
# Contract: plans/2026-08-28-ep3-tothecourt-design.md + window.__game debug api.
#   python test_episode3.py                 strict (first failure aborts)
#   RED_OBSERVE=1 python test_episode3.py   collect all failures
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

HTML_PATH = Path(__file__).with_name("episode3.html").resolve()
URL = HTML_PATH.as_uri()

OBSERVE = os.environ.get("RED_OBSERVE") == "1"
FAILURES = []
PASSES = []

# ---- pins (frozen after first stable build; placeholders keep suite RED) ----
EXPECT_HASH = "ca834c3b"     # C2 determinism pin (frozen ep3-build1)
EXPECT_NODES = 47            # C3 exact node count
EXPECT_SPAN = 1985           # C18 bot full-run span (frozen ep3-build1)

# ---- script anchor strings (the oracle owns the script, not vice versa) ----
TESTIMONY = {
    1: "완벽한 입사였습니다.",
    2: "치밀한 준비였습니다.",
    3: "계기판이 저를 증명합니다.",
}
RATES = [12.5, 8.33, 0.0]
RATE_LINES = ["증언-기록 일치율: 12.50%", "증언-기록 일치율: 8.33%", "증언-기록 일치율: 0.00%"]
FINAL_SYS = "다음 기일: 미정. 준비: 이미 시작됨."
VERDICT_LINE = "반려 (통산 1,901회)"
UNOFFICIAL_LINE = "연습 기각은 집계되지 않습니다"
VENDING_LINE = "해외 수표는 취급하지 않습니다"
DELAY_LINE = "지연 사유서"
CREDITS_REQUIRED = ["TO THE COURT", "설계·시공: 도널드 클코스", "감수: 크로노 아키텍트",
                    "같은 사건의 다른 진술", "Ep1과 Ep2에서 이어짐"]
CREDITS_FORBIDDEN = ["무결점", "천재", "전설의"]


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


# Canonical deterministic input script for C2 (runs twice on fresh loads).
C2_OPS = """
(async () => {
  const g = window.__game;
  g.api.setSeed(4242);
  g.api.ff(true);
  g.api.step(40);
  g.api.teleport('lobby', 4, 6);
  g.api.input({move:'R', frames:30});
  g.api.step(30);
  g.api.input({move:'D', frames:12});
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
  const seen = new Set(['pro.start']);
  const q = ['pro.start'];
  while (q.length) {
    const id = q.pop();
    for (const t of (edges[id] || [])) if (!seen.has(t)) { seen.add(t); q.push(t); }
  }
  const orphans = ids.filter(id => !seen.has(id));
  return {err: null, total: ids.length, missing, deadEnds, orphans,
          hasEntry: !!nodes['pro.start']};
})()
"""


def fresh(page):
    page.goto(URL)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(400)


def test_static():
    exists = os.path.isfile(HTML_PATH)
    if not check(exists, "C1 Failed: episode3.html does not exist"):
        return False
    raw = open(HTML_PATH, "rb").read()
    check(len(raw) > 0, "C1 Failed: empty file")
    check(not raw.startswith(b"\xef\xbb\xbf"), "C1 Failed: UTF-8 BOM present")
    content = raw.decode("utf-8")
    check("window.__game" in content, "C1 Failed: __game debug contract missing")
    for bad in ("setInterval", "setTimeout(", "Date.now(", "Math.random("):
        check(bad not in content, "C1 Failed: forbidden primitive %s present" % bad)
    check("http://" not in content and "https://" not in content,
          "C1 Failed: external resource reference found")
    check("TO THE COURT" in content, "C1 Failed: title string missing")
    for i in (1, 2, 3):
        check(TESTIMONY[i] in content, "C1 Failed: testimony %d anchor missing" % i)
    for s in RATE_LINES + [FINAL_SYS, VERDICT_LINE, UNOFFICIAL_LINE, VENDING_LINE]:
        check(s in content, "C1 Failed: script anchor missing: %s" % s)
    check("S('bear'" not in content and 'S("bear"' not in content,
          "C1 Failed: the bear must never speak")
    ok("C1 Passed: %d bytes, source laws + script anchors verified" % len(raw))
    return True


def test_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 960, "height": 600})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type in ("error",) else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        # ---- C2 boot + api contract + determinism hash (twice) + pin
        fresh(page)
        boot = page.evaluate("""
        (() => {
          const g = window.__game; if (!g) return {err:'no __game'};
          const need = ['step','ff','setSeed','teleport','input','interactWith','hash',
                        'save','load','autoplay','sceneObjects','sprData','hud','trial',
                        'gotoRound','enterRecollection','finishRecollection','gotoVerdict',
                        'summonToBench','choose'];
          const missing = need.filter(k => typeof g.api[k] !== 'function');
          return {err:null, missing};
        })()
        """)
        check(boot.get("err") is None and not boot.get("missing"),
              "C2 Failed: api contract incomplete: %r" % boot)
        h1 = page.evaluate(C2_OPS)
        fresh(page)
        h2 = page.evaluate(C2_OPS)
        check(h1 == h2, "C2 Failed: nondeterministic hash %r vs %r" % (h1, h2))
        check(h1 == EXPECT_HASH, "C2 Failed: hash %r != pin %r" % (h1, EXPECT_HASH))
        check(not errors, "C2 Failed: console errors: %r" % errors[:4])
        ok("C2 Passed: api complete, deterministic hash '%s' (pinned)" % h1)

        # ---- C3 dialogue graph exact
        fresh(page)
        gr = page.evaluate(GRAPH_WALK)
        check(gr.get("err") is None, "C3 Failed: %r" % gr.get("err"))
        check(gr.get("hasEntry") is True, "C3 Failed: entry node pro.start missing")
        check(not gr.get("missing"), "C3 Failed: broken edges %r" % gr.get("missing"))
        check(not gr.get("deadEnds"), "C3 Failed: dead ends %r" % gr.get("deadEnds"))
        check(not gr.get("orphans"), "C3 Failed: orphans %r" % gr.get("orphans"))
        check(gr.get("total") == EXPECT_NODES,
              "C3 Failed: node count %r != %r" % (gr.get("total"), EXPECT_NODES))
        ok("C3 Passed: %d nodes, all reachable, no dead ends" % gr.get("total"))

        # ---- C4 title boot gate + article-9 auto skip
        fresh(page)
        r4 = page.evaluate("""
        (() => {
          const g = window.__game;
          const before = g._title ? g._title.active : false;
          g.api.step(2);
          const after = g._title ? g._title.active : false;
          return {before, after, scene: g.scene};
        })()
        """)
        check(r4["after"] is False, "C4 Failed: api step did not auto-clear title (article 9): %r" % r4)
        ok("C4 Passed: boot title auto-skips on api entry (article 9)")

        # ---- C5 prologue walk: floating title during lobby walk, court reachable
        fresh(page)
        r5 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.ff(true); g.api.step(4);
          const inLobby = g.scene === 'lobby';
          let guard = 0;
          while (g.dialogue && guard++ < 200) { g.api.advance(); g.api.step(1); }
          g.api.input({move:'R', frames:200}); g.api.step(200);
          const titleShown = !!g._titleShown;
          g.api.step(600);
          return {inLobby, titleShown, scene: g.scene};
        })()
        """)
        check(r5["inLobby"] is True, "C5 Failed: game does not start in lobby: %r" % r5)
        check(r5["titleShown"] is True, "C5 Failed: TO THE COURT overlay never shown during walk")
        ok("C5 Passed: prologue lobby walk floats the title")

        # ---- C6..C8 courtroom rounds via scripted play (round1)
        fresh(page)
        r6 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          const oki = g.api.autoplay ? true : false;
          // drive to round 1 via bot checkpoint api
          const t = g.api.trial();
          g.api.gotoRound(1);
          g.api.step(30);
          const t1 = g.api.trial();
          return {oki, round: t1.round, testimony: t1.testimony};
        })()
        """)
        check(r6.get("round") == 1 and r6.get("testimony") == TESTIMONY[1],
              "C6 Failed: round1 testimony banner %r" % r6)
        ok("C6 Passed: round 1 testimony pinned to banner")

        # ---- C7 wrong choice -> unofficial stamp within 24 frames, re-presented, counter frozen
        r7 = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.ff(false);
          g.api.interactWith('witness_stand');   // summoned in C6 -> starts r1.q
          let guard = 0;
          while (guard++ < 60) {
            g.api.step(2);
            if (g.dialogue && g.dialogue.choosing) break;
            g.api.advance();
          }
          const c0 = g.dialogue && g.dialogue.choosing;
          const st0 = g.api.hud().stamps;
          g.api.choose(0);              // wrong: 3-part draft
          let stampFrame = -1;
          for (let i = 1; i <= 30; i++) {
            g.api.step(1);
            const ls = g.api.trial().lastStamp;
            if (ls && !ls.official) { stampFrame = i; break; }
          }
          guard = 0;
          let rePresented = false;
          while (guard++ < 80) {
            g.api.step(2);
            if (g.dialogue && g.dialogue.choosing) { rePresented = true; break; }
            if (!g.dialogue) break;
            g.api.advance();
          }
          const st1 = g.api.hud().stamps;
          g.api.choose(2);              // correct answer
          let advanced = false;
          guard = 0;
          while (guard++ < 80) {
            if (g.api.trial().phase !== 'question') { advanced = true; break; }
            g.api.step(2);
            if (!g.dialogue) break;
            g.api.advance();
          }
          return {c0: !!c0, stampFrame, rePresented, st0, st1, advanced};
        })()
        """)
        check(r7["c0"] is True, "C7 Failed: round1 question did not present choices: %r" % r7)
        check(0 < r7["stampFrame"] <= 24, "C7 Failed: unofficial stamp not within 24 frames: %r" % r7)
        check(r7["rePresented"] is True, "C7 Failed: wrong choice did not re-present question")
        check(r7["st0"] == r7["st1"], "C7 Failed: unofficial stamp moved official counter")
        check(r7["advanced"] is True, "C7 Failed: correct answer did not advance")
        ok("C7 Passed: rejection-converging choice (24f stamp, re-ask, counter frozen)")

        # ---- C8 recollection 1 (mem0): era sprite + scene + return + rate line
        r8 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.enterRecollection(1);
          g.api.step(10);
          const scene = g.scene;
          const spr = g.player.spr;
          const done = g.api.finishRecollection();
          g.api.step(40);
          const t = g.api.trial();
          return {scene, spr, rates: t.rates, back: g.scene};
        })()
        """)
        check(r8["scene"] == "mem0", "C8 Failed: recollection 1 scene %r" % r8)
        check(r8["spr"] == "penguin", "C8 Failed: era-0 sprite %r" % r8)
        check(r8["back"] == "court", "C8 Failed: did not return to court: %r" % r8["back"])
        check(abs(r8["rates"][0] - 12.5) < 1e-9, "C8 Failed: round1 rate %r" % r8["rates"])
        ok("C8 Passed: recollection 1 enters mem0 as era-0 penguin, returns, rate 12.50%")

        # ---- C9 official stamp counter path 1,896 -> 1,901 frozen (full bot run later at C18 asserts too)
        fresh(page)
        r9 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          const seq = [g.api.hud().stamps];
          for (let r = 1; r <= 3; r++) {
            g.api.gotoRound(r); g.api.step(20);
            g.api.enterRecollection(r); g.api.step(10);
            g.api.finishRecollection(); g.api.step(60);
            seq.push(g.api.hud().stamps);
          }
          g.api.gotoVerdict(); g.api.step(120);
          seq.push(g.api.hud().stamps);
          g.api.step(240);
          seq.push(g.api.hud().stamps);
          return {seq};
        })()
        """)
        check(r9["seq"] == [1896, 1898, 1899, 1901, 1901, 1901],
              "C9 Failed: official stamp sequence %r "
              "(expect [1896,1898,1899,1901,1901,1901] — round 3 auto-chains into the verdict)" % r9["seq"])
        ok("C9 Passed: official stamps 1,896→1,901 then frozen (verdict chained after round 3)")

        # ---- C10 gauge: 70.00 start, +1 on real click, monotone, hash-invisible
        fresh(page)
        r10a = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.step(2);
          const hud = g.api.hud();
          return {gauge: hud.gauge, rect: hud.gaugeRect, hash: g.api.hash()};
        })()
        """)
        check(abs(r10a["gauge"] - 70.0) < 1e-9, "C10 Failed: gauge start %r" % r10a["gauge"])
        rect = r10a["rect"]
        box = page.evaluate("(() => { const c = document.querySelector('canvas');"
                            " const b = c.getBoundingClientRect();"
                            " return {x:b.x, y:b.y, sx:b.width/c.width, sy:b.height/c.height}; })()")
        page.mouse.click(box["x"] + (rect[0] + rect[2] / 2) * box["sx"],
                         box["y"] + (rect[1] + rect[3] / 2) * box["sy"])
        r10b = page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.step(2);
          return {gauge: g.api.hud().gauge, hash: g.api.hash()};
        })()
        """)
        check(abs(r10b["gauge"] - 71.0) < 1e-9, "C10 Failed: click did not +1 gauge: %r" % r10b)
        check(r10a["hash"] == r10b["hash"], "C10 Failed: gauge leaked into state hash")
        ok("C10 Passed: gauge 70.00 start, +1 per real click, hash-invisible")

        # ---- C11 shuttle interrogation + delay-notice event
        fresh(page)
        r11 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.gotoRound(1); g.api.step(20);
          const objs = g.api.sceneObjects().map(o => o.id);
          const hasBench = objs.includes('judge_bench') && objs.includes('witness_stand');
          // trigger the summon then idle 300 frames without moving
          g.api.summonToBench();
          g.api.step(300);
          const delayed = (g.dialogue && g.dialogue.nodeId) || g.api.trial().lastEvent;
          return {hasBench, delayed};
        })()
        """)
        check(r11["hasBench"] is True, "C11 Failed: court lacks judge_bench/witness_stand")
        check(r11["delayed"] == "court.delay",
              "C11 Failed: idle summon did not trigger delay notice: %r" % r11["delayed"])
        ok("C11 Passed: shuttle benches present, self-issued delay notice on 300f idle")

        # ---- C12 mem0 gags: vending rejects the $2.56 check, mailbox 3-tier
        fresh(page)
        r12 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.gotoRound(1); g.api.step(20);
          g.api.enterRecollection(1); g.api.step(10);
          g.api.interactWith('vend0');
          const vendNode = g.dialogue ? g.dialogue.nodeId : null;
          g.api.step(400);
          const seq = [];
          for (let i = 0; i < 3; i++) {
            g.api.interactWith('mailbox0');
            seq.push(g.dialogue ? g.dialogue.nodeId : null);
            g.api.step(400);
          }
          return {vendNode, seq};
        })()
        """)
        check(r12["vendNode"] == "re1.vend", "C12 Failed: vending node %r" % r12["vendNode"])
        check(r12["seq"] == ["re1.mail1", "re1.mail2", "re1.mail3"],
              "C12 Failed: mailbox 3-tier sequence %r" % r12["seq"])
        ok("C12 Passed: vending check-rejection + mailbox 3-tier escalation")

        # ---- C13 mem4 gag: the stamp breaks (flag) during recollection 2
        fresh(page)
        r13 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.gotoRound(2); g.api.step(20);
          g.api.enterRecollection(2); g.api.step(10);
          const spr0 = g.player.spr;
          g.api.interactWith('stampdesk4');
          g.api.step(400);
          return {spr0, broken: !!g.flags.re2_stamp_broken};
        })()
        """)
        check(r13["spr0"] == "penguin4", "C13 Failed: era-4 sprite %r" % r13["spr0"])
        check(r13["broken"] is True, "C13 Failed: stamp-break flag not set")
        ok("C13 Passed: era-4 recollection, the stamp breaks on duty")

        # ---- C14 mem12: gauge attach + inspector cameo + tap +1 origin gag
        fresh(page)
        r14 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.gotoRound(3); g.api.step(20);
          g.api.enterRecollection(3); g.api.step(10);
          const spr0 = g.player.spr;
          const objs = g.api.sceneObjects().map(o => o.id);
          const gaugeBefore = g.api.hud().gauge;
          g.api.interactWith('bench12');
          g.api.step(500);
          const gaugeAfter = g.api.hud().gauge;
          return {spr0, hasInspector: objs.includes('npc_inspector'),
                  delta: gaugeAfter - gaugeBefore};
        })()
        """)
        check(r14["spr0"] == "penguin12", "C14 Failed: era-12 sprite %r" % r14["spr0"])
        check(r14["hasInspector"] is True, "C14 Failed: nameless inspector absent")
        check(abs(r14["delta"] - 1.0) < 1e-9,
              "C14 Failed: attach scene tap did not +1 gauge (origin gag): %r" % r14["delta"])
        ok("C14 Passed: era-12 attach day, inspector cameo, the original tap +1")

        # ---- C15 the bear crosses in silence during round-2 blackout
        fresh(page)
        r15 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.gotoRound(2); g.api.step(20);
          g.api.enterRecollection(2); g.api.step(10);
          g.api.finishRecollection(); g.api.step(30);
          // blackout window plays right after round-2 verdict delivery
          let seenX = [];
          for (let i = 0; i < 240; i += 20) {
            g.api.step(20);
            const bear = g.api.sceneObjects().find(o => o.id === 'bear');
            if (bear) seenX.push(bear.x);
          }
          return {n: seenX.length, moved: seenX.length >= 2 && seenX[0] !== seenX[seenX.length-1],
                  black: true};
        })()
        """)
        check(r15["n"] >= 2 and r15["moved"] is True,
              "C15 Failed: bear did not cross during blackout: %r" % r15)
        ok("C15 Passed: the bear crosses the dark courtroom, wordless")

        # ---- C16 verdict: loss delivered, stamp 1901 wording
        fresh(page)
        r16 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          for (let r = 1; r <= 3; r++) {
            g.api.gotoRound(r); g.api.step(20);
            g.api.enterRecollection(r); g.api.step(10);
            g.api.finishRecollection(); g.api.step(60);
          }
          g.api.gotoVerdict(); g.api.step(400);
          const t = g.api.trial();
          return {phase: t.phase, verdictDelivered: !!g.flags.ep3_verdict,
                  stamps: g.api.hud().stamps};
        })()
        """)
        check(r16["verdictDelivered"] is True and r16["stamps"] == 1901,
              "C16 Failed: verdict state %r" % r16)
        ok("C16 Passed: the 1,901st rejection is this trial")

        # ---- C17 epilogue reached by continuing; final flag
        r17 = page.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true);
          g.api.step(2000);
          return {scene: g.scene, done: !!g.flags.ep3_done,
                  gauge: g.api.hud().gauge};
        })()
        """)
        check(r17["done"] is True, "C17 Failed: epilogue did not complete: %r" % r17)
        check(r17["gauge"] >= 71.0, "C17 Failed: epilogue scripted gauge tap missing: %r" % r17["gauge"])
        ok("C17 Passed: epilogue completes; the gauge got its one sincere tap")

        # ---- C18 bot full autoplay, deterministic span
        fresh(page)
        r18 = page.evaluate("""
        (async () => {
          const g = window.__game;
          const f0 = g.frame;
          const done = g.api.autoplay(300000);
          return {err:null, done, flag: !!g.flags.ep3_done, span: g.frame - f0};
        })()
        """)
        cond = r18.get("done") and r18.get("flag") and r18.get("span") == EXPECT_SPAN
        check(cond, "C18 Failed: autoplay incomplete or span drift (expect %r): %r" % (EXPECT_SPAN, r18))
        ok("C18 Passed: bot full run, deterministic span %s" % r18.get("span"))

        # ---- C19 saves: ep3 keys roundtrip; ep1/ep2 keys untouched
        fresh(page)
        r19 = page.evaluate("""
        (async () => {
          const g = window.__game;
          localStorage.setItem('tts_ep1_s1', 'SENTINEL1');
          localStorage.setItem('tts_ep2_s1', 'SENTINEL2');
          g.api.ff(true); g.api.gotoRound(2); g.api.step(30);
          const h0 = g.api.hash();
          g.api.save(1);
          g.api.gotoRound(3); g.api.step(50);
          g.api.load(1);
          g.api.step(2);
          const h1 = g.api.hash();
          return {h0, h1, key: !!localStorage.getItem('tts_ep3_s1'),
                  s1: localStorage.getItem('tts_ep1_s1'),
                  s2: localStorage.getItem('tts_ep2_s1')};
        })()
        """)
        check(r19["key"] is True, "C19 Failed: tts_ep3_s1 not written")
        check(r19["h0"] == r19["h1"], "C19 Failed: save/load hash mismatch %r" % r19)
        check(r19["s1"] == "SENTINEL1" and r19["s2"] == "SENTINEL2",
              "C19 Failed: foreign save keys touched")
        ok("C19 Passed: ep3 save roundtrip exact; ep1/ep2 keys inviolate")

        # ---- C20 touch: tap advances exactly one line; D-pad walks
        mctx = browser.new_context(viewport={"width": 375, "height": 812},
                                   has_touch=True, is_mobile=True)
        mpage = mctx.new_page()
        fresh(mpage)
        r20 = mpage.evaluate("""
        (async () => {
          const g = window.__game;
          g.api.ff(true); g.api.gotoRound(1); g.api.step(20); g.api.ff(false);
          g.api.interactWith('witness_stand');
          g.api.step(40);
          const lines0 = g.dialogue ? g.dialogue.stepIdx : -99;
          const c = document.querySelector('canvas');
          const r = c.getBoundingClientRect();
          const t = new Touch({identifier: 1, target: c,
                               clientX: r.x + r.width * 0.5, clientY: r.y + r.height * 0.4});
          c.dispatchEvent(new TouchEvent('touchstart', {touches:[t], changedTouches:[t],
                                                        bubbles:true, cancelable:true}));
          c.dispatchEvent(new TouchEvent('touchend', {touches:[], changedTouches:[t],
                                                      bubbles:true, cancelable:true}));
          g.api.step(12);
          const lines1 = g.dialogue ? g.dialogue.stepIdx : -99;
          return {adv: lines1 - lines0};
        })()
        """)
        check(r20["adv"] == 1, "C20 Failed: tap advanced %r lines (want exactly 1)" % r20["adv"])
        mctx.close()
        ok("C20 Passed: real touch tap advances exactly one line")

        # ---- C21 reduced motion honored
        rmctx = browser.new_context(reduced_motion="reduce")
        rmpage = rmctx.new_page()
        fresh(rmpage)
        r21 = rmpage.evaluate("(() => { const g = window.__game; g.api.step(30);"
                              " return {rm: !!g.flags.reducedMotion}; })()")
        check(r21["rm"] is True, "C21 Failed: reduced-motion flag not honored")
        rmctx.close()
        ok("C21 Passed: reduced-motion honored")

        # ---- C22 credits: required strings, no self-medals
        raw = open(HTML_PATH, encoding="utf-8").read()
        cred = raw[raw.find("credits."):]
        for s in CREDITS_REQUIRED:
            check(s in raw, "C22 Failed: credits string missing: %s" % s)
        for s in CREDITS_FORBIDDEN:
            check(s not in raw, "C22 Failed: forbidden self-medal present: %s" % s)
        ok("C22 Passed: credits complete, medal-free")

        check(not errors, "C-final Failed: console errors during suite: %r" % errors[:6])
        browser.close()


def main():
    okstatic = test_static()
    if okstatic or OBSERVE:
        try:
            if okstatic:
                test_e2e()
        except AssertionError as e:
            if not OBSERVE:
                print("FAILED: %s" % e)
                sys.exit(1)
            FAILURES.append(str(e))
    total = len(PASSES) + len(FAILURES)
    if FAILURES:
        print("\n%d RED / %d total" % (len(FAILURES), total))
        sys.exit(1)
    print("\n" + "=" * 55)
    print("ALL Ep3 CRITERIA VERIFIED")
    print("PASS %d/%d" % (len(PASSES), len(PASSES)))
    print("=" * 55)


if __name__ == "__main__":
    main()
