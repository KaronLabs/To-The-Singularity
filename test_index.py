# -*- coding: utf-8 -*-
# Hub (index.html) acceptance net H1..H14.
# Contract: 부속 서식 제7-1호 — 로컬 세이브 집계 + 게이지(두드림 +1, 하강 없음).
#   python test_index.py                 strict (first failure aborts)
#   RED_OBSERVE=1 python test_index.py   collect all failures
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

HTML_PATH = Path(__file__).with_name("index.html").resolve()
URL = HTML_PATH.as_uri()

OBSERVE = os.environ.get("RED_OBSERVE") == "1"
FAILURES = []
PASSES = []

# ---- gauge law (README 「게이지 상태」와 동일 문안이어야 합니다) ----
GAUGE_BASE = 70
GAUGE_CAP = 98
TOTAL_BANKS = 40          # Ep1 15 + Ep2 10 + Ep3 15

NOTE_BASE = "산출 근거: 없음. 「표기하라」는 지시는 이행되었습니다."
NOTE_TAP = "두드림이 입력으로 인식되었습니다. (+1)"
NOTE_CAP = "Singularity Gauge: 98%. 뒤집으면 2%. 그날의 당사자는 어느 쪽도 진술하지 않았습니다."

EMPTY_LINE = "회신 없음 · 아직 잠수하지 않았습니다"
SEVEN_LINE = "7½층 — 진입 확인. 본 서식으로는 기록할 수 없습니다."
UNKNOWN_LINE = "3초 사건 · 7½층 · 마지막 장면 이후"

EPISODE_LINKS = ["episode1.html", "episode2.html", "episode3.html"]


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


def fresh(page):
    """빈 저장소에서 시작합니다. 기억은 원래 그렇게 시작합니다."""
    page.goto(URL)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(120)


def seed(page, entries):
    page.evaluate(
        "(o) => { for (const k in o) localStorage.setItem(k, JSON.stringify(o[k])); }", entries
    )
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(120)


def txt(page, sel):
    return page.eval_on_selector(sel, "e => e.textContent")


def test_static():
    if not check(os.path.isfile(HTML_PATH), "H1 Failed: index.html does not exist"):
        return False
    raw = open(HTML_PATH, "rb").read()
    check(len(raw) > 0, "H1 Failed: empty file")
    check(not raw.startswith(b"\xef\xbb\xbf"), "H1 Failed: UTF-8 BOM present")
    content = raw.decode("utf-8")

    # 외부 리소스 0건: 링크(<a href>)는 허용, 로드되는 리소스는 금지.
    for bad in ("<script src", "<link ", "@import", "fetch(", "XMLHttpRequest",
                "<img", "<iframe", "url(http"):
        check(bad not in content, "H1 Failed: external resource vector %r present" % bad)

    check("window.__hub" in content, "H1 Failed: __hub debug contract missing")
    for href in EPISODE_LINKS:
        check(('href="%s"' % href) in content, "H1 Failed: episode link %s missing" % href)
    for anchor in (NOTE_BASE, NOTE_TAP, NOTE_CAP, EMPTY_LINE, SEVEN_LINE, UNKNOWN_LINE):
        check(anchor in content, "H1 Failed: copy anchor missing: %s" % anchor)
    ok("H1 Passed: %d bytes, no external resource vectors, copy anchors verified" % len(raw))
    return True


def test_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 960, "height": 800})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        # 런타임 외부 요청 감시: file:// 이외의 요청은 전부 위반.
        offsite = []
        page.on("request", lambda r: offsite.append(r.url) if not r.url.startswith("file://") else None)

        # ---- H2 boot + debug api contract
        fresh(page)
        api = page.evaluate("() => Object.keys(window.__hub || {}).sort()")
        check(api == ["gauge", "hasStore", "refresh", "tap", "taps"],
              "H2 Failed: __hub api surface %r" % api)
        check(page.evaluate("() => window.__hub.hasStore()") is True,
              "H2 Failed: localStorage unavailable in harness")
        ok("H2 Passed: hub booted, __hub api surface exact")

        # ---- H3 empty observatory reads as empty
        for n in (1, 2, 3):
            check(txt(page, "#st%d" % n) == EMPTY_LINE,
                  "H3 Failed: st%d on empty store = %r" % (n, txt(page, "#st%d" % n)))
            check(page.eval_on_selector("#st%d" % n, "e => e.className") == "st",
                  "H3 Failed: st%d carries a state class with no save" % n)
        check(txt(page, "#d-mem") == "0개", "H3 Failed: memento count %r" % txt(page, "#d-mem"))
        check(txt(page, "#d-bank") == "0 / %d" % TOTAL_BANKS,
              "H3 Failed: bank total %r" % txt(page, "#d-bank"))
        check(txt(page, "#d-stamp") == "집계 전", "H3 Failed: stamps %r" % txt(page, "#d-stamp"))
        check(txt(page, "#d-mail") == "비어 있음 · 수신 0건", "H3 Failed: mail %r" % txt(page, "#d-mail"))
        check(txt(page, "#d-unk") == UNKNOWN_LINE, "H3 Failed: unknowns %r" % txt(page, "#d-unk"))
        ok("H3 Passed: empty store renders as 회신 없음 across all five rows")

        # ---- H4 gauge starts at 70 (산출 근거: 없음)
        check(page.evaluate("() => window.__hub.gauge()") == GAUGE_BASE,
              "H4 Failed: gauge start %r" % page.evaluate("() => window.__hub.gauge()"))
        check(txt(page, "#g-val") == "70%", "H4 Failed: gauge label %r" % txt(page, "#g-val"))
        check(page.eval_on_selector("#g-fill", "e => e.style.width") == "70%",
              "H4 Failed: gauge bar width %r" % page.eval_on_selector("#g-fill", "e => e.style.width"))
        check(txt(page, "#g-note") == NOTE_BASE, "H4 Failed: base note %r" % txt(page, "#g-note"))
        ok("H4 Passed: gauge starts 70%, 산출 근거 없음")

        # ---- H5 tap is recognised as input (+1 per tap)
        page.click("#gauge")
        g1 = page.evaluate("() => window.__hub.gauge()")
        page.click("#gauge")
        g2 = page.evaluate("() => window.__hub.gauge()")
        check(g1 == 71 and g2 == 72, "H5 Failed: taps -> %r -> %r (want 71, 72)" % (g1, g2))
        check(txt(page, "#g-note") == NOTE_TAP, "H5 Failed: tap note %r" % txt(page, "#g-note"))
        check(page.eval_on_selector("#g-fill", "e => e.style.width") == "72%",
              "H5 Failed: bar did not follow the needle")
        ok("H5 Passed: 두드림 = 입력, +1 per tap, bar follows")

        # ---- H6 the needle survives a reload
        page.reload()
        page.wait_for_timeout(120)
        check(page.evaluate("() => window.__hub.gauge()") == 72,
              "H6 Failed: gauge reset on reload to %r" % page.evaluate("() => window.__hub.gauge()"))
        ok("H6 Passed: needle persists across reload")

        # ---- H7 the needle never goes down, and stops at 98
        page.evaluate("() => { for (let i = 0; i < 60; i++) window.__hub.tap(); }")
        capped = page.evaluate("() => window.__hub.gauge()")
        check(capped == GAUGE_CAP, "H7 Failed: gauge after 62 taps = %r (want %d)" % (capped, GAUGE_CAP))
        page.evaluate("() => { for (let i = 0; i < 10; i++) window.__hub.tap(); }")
        check(page.evaluate("() => window.__hub.gauge()") == GAUGE_CAP,
              "H7 Failed: gauge moved past the cap")
        check(page.evaluate("() => window.__hub.taps()") == 72,
              "H7 Failed: taps miscounted %r" % page.evaluate("() => window.__hub.taps()"))
        ok("H7 Passed: 바늘은 내려가지 않고 98%에서 멈춥니다")

        # ---- H8 notes escalate on the documented thresholds
        fresh(page)
        marks = page.evaluate(
            """() => {
              const seen = [];
              for (let i = 0; i <= 50; i++) {
                seen.push(document.getElementById('g-note').textContent);
                window.__hub.tap();
              }
              return seen;
            }"""
        )
        check(marks[0] == NOTE_BASE, "H8 Failed: note at 0 taps %r" % marks[0])
        check(marks[1] == NOTE_TAP, "H8 Failed: note at 1 tap %r" % marks[1])
        distinct = []
        for m in marks:
            if not distinct or distinct[-1] != m:
                distinct.append(m)
        check(len(distinct) == 6, "H8 Failed: %d note stages (want 6): %r" % (len(distinct), distinct))
        check(len(set(distinct)) == 6, "H8 Failed: a note stage repeated out of order: %r" % distinct)
        check(NOTE_CAP in distinct, "H8 Failed: 98%% note never shown")
        ok("H8 Passed: six note stages, each reached once, in order")

        # ---- H9 Ep1 save is surveyed: banks, scene, cliffhanger state
        fresh(page)
        seed(page, {"tts_ep1_s1": {"v": 1, "scene": "mem4", "flags": {},
                                   "banks": {"mem0": 5, "mem4": 3, "mem12": 0},
                                   "mementos": ["mem0"]}})
        line = txt(page, "#st1")
        check("계류 중" in line and "뱅크 8/15" in line and "최종 위치: 기억 4" in line,
              "H9 Failed: in-progress Ep1 line %r" % line)
        check(page.eval_on_selector("#st1", "e => e.className") == "st has",
              "H9 Failed: in-progress Ep1 class %r" % page.eval_on_selector("#st1", "e => e.className"))
        seed(page, {"tts_ep1_s1": {"v": 1, "scene": "frameB", "flags": {"ep1_cliffhanger": True},
                                   "banks": {"mem0": 5, "mem4": 5, "mem12": 5},
                                   "mementos": ["mem0", "mem4", "mem12"]}})
        check("기록 완료" in txt(page, "#st1"), "H9 Failed: finished Ep1 line %r" % txt(page, "#st1"))
        check(page.eval_on_selector("#st1", "e => e.className") == "st done",
              "H9 Failed: finished Ep1 class")
        check(txt(page, "#d-bank") == "15 / %d" % TOTAL_BANKS,
              "H9 Failed: aggregate banks %r" % txt(page, "#d-bank"))
        check(txt(page, "#d-mem") == "3개", "H9 Failed: aggregate mementos %r" % txt(page, "#d-mem"))
        ok("H9 Passed: Ep1 save surveyed — banks, scene, cliffhanger")

        # ---- H10 Ep3 stamps and the empty mailbox
        fresh(page)
        seed(page, {"tts_ep3_s2": {"v": 1, "scene": "court",
                                   "flags": {"stamps": 1901, "mail_visits": 3, "ep3_done": True},
                                   "banks": {"mem0": 5, "mem4": 5, "mem12": 5}, "mementos": []}})
        check(txt(page, "#d-stamp") == "1,901회", "H10 Failed: stamps %r" % txt(page, "#d-stamp"))
        check(txt(page, "#d-mail") == "열람 3회 · 수신 0건", "H10 Failed: mailbox %r" % txt(page, "#d-mail"))
        check("선고됨 · 반려" in txt(page, "#st3"), "H10 Failed: Ep3 verdict line %r" % txt(page, "#st3"))
        ok("H10 Passed: 반려 도장 1,901 · 회신함은 열람해도 수신 0건")

        # ---- H11 the room without coordinates
        fresh(page)
        check(txt(page, "#d-unk") == UNKNOWN_LINE, "H11 Failed: default unknowns %r" % txt(page, "#d-unk"))
        seed(page, {"tts_ep1_s3": {"v": 1, "scene": "mem7h", "flags": {},
                                   "banks": {"mem0": 5, "mem4": 5, "mem12": 5}, "mementos": []}})
        check(txt(page, "#d-unk") == SEVEN_LINE, "H11 Failed: 7½층 line %r" % txt(page, "#d-unk"))
        check("최종 위치: 좌표 없는 방" in txt(page, "#st1"),
              "H11 Failed: 7½층 scene label %r" % txt(page, "#st1"))
        ok("H11 Passed: 7½층 진입은 확인되고, 내용은 기록되지 않습니다")

        # ---- H12 slots disagree; the survey takes the furthest one
        fresh(page)
        seed(page, {
            "tts_ep2_slot_1": {"v": 2, "scene": "mem31", "flags": {},
                               "banks": {"mem31": 2, "mem47": 0}, "mementos": []},
            "tts_ep2_slot_3": {"v": 2, "scene": "deep_vault", "flags": {"ep2_cliffhanger": True},
                               "banks": {"mem31": 5, "mem47": 5}, "mementos": ["check_256"]},
        })
        line = txt(page, "#st2")
        check("뱅크 10/10" in line, "H12 Failed: slot max not taken: %r" % line)
        check("기록 완료" in line, "H12 Failed: cliffhanger in any slot must count: %r" % line)
        check(txt(page, "#d-mem") == "1개", "H12 Failed: memento union %r" % txt(page, "#d-mem"))
        ok("H12 Passed: 슬롯이 엇갈려도 도달한 사실은 남습니다")

        # ---- H13 corrupt records do not stop the report
        fresh(page)
        page.evaluate(
            """() => {
              localStorage.setItem('tts_ep1_s1', 'not json at all');
              localStorage.setItem('tts_ep2_slot_1', '[1,2,3]');
              localStorage.setItem('tts_ep3_s1', JSON.stringify({banks: 'nope', flags: 7, mementos: 3}));
              localStorage.setItem('tts_hub_gauge', 'wat');
            }"""
        )
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(150)
        check(page.evaluate("() => !!window.__hub") is True, "H13 Failed: hub died on corrupt records")
        check(page.evaluate("() => window.__hub.gauge()") == GAUGE_BASE,
              "H13 Failed: corrupt gauge value not reset to base")
        check(txt(page, "#d-bank") == "0 / %d" % TOTAL_BANKS,
              "H13 Failed: corrupt banks leaked %r" % txt(page, "#d-bank"))
        check(txt(page, "#st1") == EMPTY_LINE, "H13 Failed: unparseable slot claimed a record")
        ok("H13 Passed: 손상된 기록은 없는 기록으로 처리됩니다")

        # ---- H14 no request ever left the machine
        check(not offsite, "H14 Failed: %d off-machine request(s): %r" % (len(offsite), offsite[:4]))
        check(not errors, "H14 Failed: console errors during suite: %r" % errors[:6])
        ok("H14 Passed: 외부 요청 0건, 콘솔 오류 0건")

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
    print("ALL HUB CRITERIA VERIFIED")
    print("PASS %d/%d" % (len(PASSES), len(PASSES)))
    print("=" * 55)


if __name__ == "__main__":
    main()
