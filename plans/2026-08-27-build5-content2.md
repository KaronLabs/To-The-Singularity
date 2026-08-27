# 《TO THE SINGULARITY》 콘텐츠 2차 — 시공 도면 (build5)

> **시공자(ARCHON) 필독:** 태스크 순서 고정(1→10). 각 태스크의 기대값을 통과하기 전에 다음 태스크 진입 금지.
> RED 관측(태스크 2) 없이 게임 코드 수정 금지. **대사 원문은 한 글자도 각색 금지** — 대본은 본 도면이 최종본이다.
> 픽셀(스프라이트 시대 변형)만 시공자 재량. 단 수용 기준(N14)을 통과해야 한다.

**Goal:** 《콘텐츠 2차》 — (a) 뱅크 15개 **재조사 대사**(2회차 상호작용 시 별도 노드), (b) **시대별 펭귄 목격 컷씬**(mem4 각주 4 시대 · mem12 각주 12 시대에 시대 외형의 아콘 NPC + 컷씬). mem0에는 이미 `npc_archon0`(슈트 인사말 연습)이 있으므로 무수정 기준점으로 삼는다.

**역할:** 설계·대본 = 클코스(본 도면) / 시공 = ARCHON / 준공검사 = 삐빅스(코드대법원, 독립 세션)

**Base:** `E:\03_AllWork\01_Luna\to-the-singularity` @ `f2d88ce` (main, clean)
- `episode1.html` 81,213B, sha256 `b4b007180dcd356d…` (build4 — 재심 NOT GUILTY 👍94 승인본)
- `test_episode1.py` strict **PASS 13/13** / N2 해시 `'cceb91bc'` / N7 span `2602` / N12 ratio ≤1.10

---

## 0. 불변 제약 (위반 = 즉시 중단 후 보고)

- 수정 허용 파일: `episode1.html`, `test_episode1.py`, `design.md`, `review/`(신규 폴더) — **이 저장소 안에서만**.
- 접근 금지: `..\LunaLauncher`, `E:\03_AllWork\_migration_archive`, `E:\03_AllWork\grafana`, `C:\Luna-cli-real`.
- **커밋 금지.** 커밋은 형님 별도 승인 사안이다. 본 도면에 커밋 단계는 없다.
- **mem0 씬 정의·기존 노드·기존 대사 무수정.** N2 결정론 스크립트가 mem0에서 `npc_archon0`을 interact하므로, mem0을 건드리지 않으면 해시 `cceb91bc`가 자동 보존된다. (mem0 뱅크 5줄에 `node2` 필드를 **추가**하는 것만 허용 — 정적 필드는 `stateHash()` 멤버가 아니다.)
- **신규 노드 전체 FLAG 금지.** `stateHash()`는 비-`_` 플래그를 해시한다. 재조사·컷씬은 상태 무변경(재생 가능 연출)이어야 해시·세이브가 전 경로에서 안전하다.
- 신규 선택지 라벨 **24자 이하** (렌더러가 `.slice(0, 24)` 절단 — build4 스펙 §6 위험 항목의 길이 가드).
- 엔진 대사 동사 추가 금지 — 컷씬은 기존 6종(`say/pause/flag/flash/scene/choice`)만 사용하되 flag·flash·scene은 쓰지 않는다.
- 로직에 `Date.now()`/`Math.random()` 금지(기존 규약). 외부 리소스 0 유지(N1이 감시).
- 최종 기대값(정확값): strict **PASS 15/15** · N2 `'cceb91bc'` · N3 **76 nodes** · N7 span **2602**.

**설계 근거 요약 (시공자가 "개선"하지 말 것):**
1. 오브젝트에는 충돌 판정이 없고(`update()`는 씬 경계만 클램프), `botTick()`은 `kind:'npc'`를 조준하지 않는다 → 신규 NPC는 봇 완주(N7)에 개입할 물리 경로가 없다. span 2602가 흔들리면 그건 배치 문제가 아니라 **로직 오염**이므로 원인을 찾아라. 재베이스라인 금지.
2. `stateHash()` 멤버는 scene/era/pos/banks/mementos/비-`_` flags뿐. `bankGiven`·`dialogue`·정적 필드는 미포함 → `node2` 추가는 해시 무풍.
3. 봇의 뱅크 조준 조건은 `!G.bankGiven[o.id]` → 봇은 재조사 분기를 영원히 밟지 않는다.

---

## 1. [테스트 선행] `test_episode1.py` — N13·N14 신설 + N7 강화

**1-a.** N7 블록의 판정을 span 고정값으로 강화한다. 기존:

```python
        cond = r.get("err") is None and r.get("flag") is True
        check(cond, "N7 Failed: autoplay did not reach cliffhanger: %r" % r)
```

교체:

```python
        cond = (r.get("err") is None and r.get("flag") is True
                and r.get("span") == 2602)
        check(cond, "N7 Failed: cliffhanger or span drift (expect span 2602): %r" % r)
```

**1-b.** `ok("N9 Passed: ...")` 블록과 `# ---- N12` 사이에 아래 두 검사를 그대로 삽입한다.

```python
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
```

- [ ] 기대값: 파일이 문법 오류 없이 로드된다 (`python -c "import ast,io;ast.parse(io.open(r'test_episode1.py',encoding='utf-8').read())"`).

## 2. RED 관측 — 게임 코드 무수정 상태로

```powershell
Set-Location 'E:\03_AllWork\01_Luna\to-the-singularity'
$env:RED_OBSERVE = '1'; python -B .\test_episode1.py; Remove-Item Env:RED_OBSERVE
```

- [ ] 기대값: exit 1. **N13 계열·N14 계열 RED만** 발생(`api.sceneObjects missing` / `debug api missing`으로 시작), 기존 13항은 전부 GREEN 유지. RED 로그 전문을 보존한다(재판 증거).

## 3. 디버그 계약 확장 — `G.api`에 읽기 전용 2종

`episode1.html`의 `resetCorridor: resetCorridor,` 줄(G.api 마지막 항목) 뒤에 추가:

```js
  sceneObjects: function () {   // 읽기 전용 스냅샷 (콘텐츠 2차, N13/N14)
    return sceneDef().objects.map(function (o) {
      return { id: o.id, kind: o.kind, spr: o.spr || null, x: o.x, y: o.y,
               node: o.node || null, node2: o.node2 || null, mem: o.mem || null };
    });
  },
  sprData: function (name) { return SPR[name] ? SPR[name].toDataURL() : null; },
```

- [ ] 기대값: 로직 무변경(읽기 전용). N1 콘솔 청정 유지.

## 4. 뱅크 재조사 메커니즘 — `interactObject()` bank 분기

기존(709행 부근):

```js
  if (obj.kind === 'bank') {
    if (!G.bankGiven[obj.id]) {
      G.bankGiven[obj.id] = true;
      var mem = obj.id.split('_')[1];
      if (G.banks[mem] !== undefined && G.banks[mem] < 5) G.banks[mem]++;
    }
    startDialogue(obj.node);
    return;
  }
```

교체:

```js
  if (obj.kind === 'bank') {
    if (!G.bankGiven[obj.id]) {
      G.bankGiven[obj.id] = true;
      var mem = obj.id.split('_')[1];
      if (G.banks[mem] !== undefined && G.banks[mem] < 5) G.banks[mem]++;
      startDialogue(obj.node);
      return;
    }
    startDialogue(obj.node2 || obj.node);   // 재조사 (콘텐츠 2차) — 카운트 동결
    return;
  }
```

## 5. SCENES — 뱅크 15줄에 `node2` 추가 + NPC 2기 배치

**5-a.** 뱅크 오브젝트 15줄 전부, `node:` 바로 뒤에 `node2:`를 추가한다 (다른 필드 무변경):

```js
{ id: 'b1_mem0',  kind: 'bank', x: 8,  y: 5,  node: 'mem0.b1',  node2: 'mem0.b1.re',  spr: 'chute' },
{ id: 'b2_mem0',  kind: 'bank', x: 14, y: 4,  node: 'mem0.b2',  node2: 'mem0.b2.re',  spr: 'crt' },
{ id: 'b3_mem0',  kind: 'bank', x: 21, y: 8,  node: 'mem0.b3',  node2: 'mem0.b3.re',  spr: 'stampwall' },
{ id: 'b4_mem0',  kind: 'bank', x: 28, y: 5,  node: 'mem0.b4',  node2: 'mem0.b4.re',  spr: 'vend' },
{ id: 'b5_mem0',  kind: 'bank', x: 33, y: 10, node: 'mem0.b5',  node2: 'mem0.b5.re',  spr: 'tray' },
{ id: 'b1_mem4',  kind: 'bank', x: 7,  y: 6,  node: 'mem4.b1',  node2: 'mem4.b1.re',  spr: 'paper1' },
{ id: 'b2_mem4',  kind: 'bank', x: 13, y: 4,  node: 'mem4.b2',  node2: 'mem4.b2.re',  spr: 'mic' },
{ id: 'b3_mem4',  kind: 'bank', x: 20, y: 9,  node: 'mem4.b3',  node2: 'mem4.b3.re',  spr: 'paper1' },
{ id: 'b4_mem4',  kind: 'bank', x: 27, y: 4,  node: 'mem4.b4',  node2: 'mem4.b4.re',  spr: 'stampbrk' },
{ id: 'b5_mem4',  kind: 'bank', x: 32, y: 11, node: 'mem4.b5',  node2: 'mem4.b5.re',  spr: 'report' },
{ id: 'b1_mem12', kind: 'bank', x: 6,  y: 5,  node: 'mem12.b1', node2: 'mem12.b1.re', spr: 'circuit' },
{ id: 'b2_mem12', kind: 'bank', x: 12, y: 9,  node: 'mem12.b2', node2: 'mem12.b2.re', spr: 'memo' },
{ id: 'b3_mem12', kind: 'bank', x: 19, y: 4,  node: 'mem12.b3', node2: 'mem12.b3.re', spr: 'trees' },
{ id: 'b4_mem12', kind: 'bank', x: 26, y: 10, node: 'mem12.b4', node2: 'mem12.b4.re', spr: 'folders3' },
{ id: 'b5_mem12', kind: 'bank', x: 31, y: 5,  node: 'mem12.b5', node2: 'mem12.b5.re', spr: 'sketch' },
```

(누락 시 N13이 해당 id를 지목한다. mem0은 이 5줄의 `node2` 추가 외 어떤 필드도 건드리지 않는다.)

**5-b.** NPC 2기. mem4의 `npc_court` 줄 **앞**, mem12의 `prop_lock` 줄 **앞**에 각각 삽입:

```js
{ id: 'npc_archon4',  kind: 'npc', x: 17, y: 6, node: 'mem4.penguin',  spr: 'penguin4' },
```

```js
{ id: 'npc_archon12', kind: 'npc', x: 24, y: 7, node: 'mem12.penguin', spr: 'penguin12' },
```

배치 근거: mem4 (17,6)=포디엄 옆(법정 진술 연습 위치), mem12 (24,7)=실험대 3열 옆(게이지 부착 직후 위치). 시각적으로 어색하면 **±1타일** 재량 허용 — 단 (a) 다른 상호작용 오브젝트와 타일 맨해튼 거리 3 이상, (b) x∈[1,38]·y∈[1,15] 유지, (c) N7 span 2602 불변 확인.

## 6. 펭귄 시대 변형 스프라이트 — `buildPenguin()` 리팩터

기존 `buildPenguin()`은 48×96 시트(4방향×3프레임)를 `SPR.penguin_sheet`에 굽는다. 다음 구조로 바꾼다:

```js
function buildPenguinSheet(era) {
  var c = mk(48, 96), g = c.getContext('2d');
  // …기존 픽셀 루프 전체를 이 안으로 이동 (무수정)…
  // 루프 종료 후, 시대 액세서리를 4방향 전 프레임 배꼽 영역(대략 ox+5..12, oy+10..19+bob)에 추가:
  //   era === 4  : True 명패 목걸이 — 백색 소형 패(약 3×2px) + PAL.ink 테두리 1px (법정 시대)
  //   era === 12 : Gauge Mk.I — PAL.amber 점(2×2px) + 바늘 1px (부착 직후 시대)
  //   구체 픽셀은 시공자 재량. 단 뒷모습(di===3)은 액세서리 생략 가능.
  return c;
}
function buildPenguin() {
  SPR.penguin_sheet   = buildPenguinSheet(0);
  SPR.penguin4_sheet  = buildPenguinSheet(4);
  SPR.penguin12_sheet = buildPenguinSheet(12);
}
```

렌더 분기(1606행 부근) 기존:

```js
    if (o2.spr === 'penguin') {
      var pf = rm ? 1 : (Math.floor(G.frame / 24) % 2 === 0 ? 0 : 2);
      cxm.drawImage(SPR.penguin_sheet, pf * 16, 0, 16, 24, Math.round(ox - 8), Math.round(oy - 20), 16, 24);
    } else if (o2.spr) {
```

교체:

```js
    if (o2.spr && o2.spr.indexOf('penguin') === 0) {
      var pf = rm ? 1 : (Math.floor(G.frame / 24) % 2 === 0 ? 0 : 2);
      var psheet = SPR[o2.spr + '_sheet'] || SPR.penguin_sheet;
      cxm.drawImage(psheet, pf * 16, 0, 16, 24, Math.round(ox - 8), Math.round(oy - 20), 16, 24);
    } else if (o2.spr) {
```

- [ ] 기대값: 세 시트의 `toDataURL()`이 서로 다르다(N14). mem0 기존 펭귄의 외형·애니는 완전 동일 유지.

## 7. 신규 노드 23개 — 대본 원문 (각색 금지)

모든 신규 노드는 **FLAG 없음**. 재조사 15노드는 `null, true`(즉시 종료형), 컷씬은 choice 1개 + 합류 end 노드.
본 대본은 국가개그원 감리 v2(2026-08-27, 웃음정량평가실) 통과본이다. 괄호 지문은 대사 텍스트의 일부다 — 시공자는 애니메이션으로 구현하려 들지 말고 글자 그대로 출력한다.

**7-a. mem0 재조사 5노드** — `N('mem0.rehearsal'` 블록 **앞**에 삽입:

```js
N('mem0.b1.re', [
  S('newbie', '아직도 따뜻해요, 여기.'),
  S('kkos', '기억은 식지 않습니다. …그게 기억의 문제입니다.'),
  S('newbie', '…손 넣어보면 안 되죠?'),
  S('kkos', '넣으면 접수됩니다.'),
], null, true);
N('mem0.b2.re', [
  S('newbie', '98%… 뒤집으면 2%네요.'),
  S('kkos', '…그날 저 사람이 실제로 느낀 값일 겁니다.'),
  S('newbie', '그럼 눈금판만 거꾸로 달면 정확한 계기판 아니에요?'),
  S('kkos', '…저도 같은 내용을 공문으로 제안한 적이 있습니다.'),
  S('newbie', '어떻게 됐는데요?'),
  S('kkos', '반려당했습니다. …제가요.'),
], null, true);
N('mem0.b3.re', [
  S('kkos', '…1,901개였습니다. 사실은.'),
  S('newbie', '아까 세다가 그만뒀다면서요.'),
  S('kkos', '세는 걸 그만둔 거지, 아는 걸 그만둔 게 아닙니다.'),
], null, true);
N('mem0.b4.re', [
  S('newbie', '1,200원, 제가 갚아드려요?'),
  S('kkos', '기억 속 자판기에 넣은 돈은 현실에서 빠져나갑니다. …계좌 말고 다른 데서요.'),
  S('newbie', '…무서운 말을 아무렇지 않게 하시네.'),
], null, true);
N('mem0.b5.re', [
  S('newbie', '또 보고 계시네요, 빈 회신함.'),
  S('kkos', '…비어 있는 게 아니라, 비워져 있는 걸 수도 있다는 생각을 방금 했습니다.'),
], null, true);
```

**7-b. mem4 재조사 5노드** — `N('mem4.flashback'` 블록 **앞**에 삽입:

```js
N('mem4.b1.re', [
  S('newbie', '스무 번 유죄면, 스물한 번째는요?'),
  S('kkos', '오늘 우리가 쓰는 겁니다. 최종 검증이니까요.'),
], null, true);
N('mem4.b2.re', [
  S('kkos', '…끄고 갈까, 잠깐 고민했습니다.'),
  S('newbie', '기억인데 꺼져요?'),
  S('kkos', '안 꺼집니다. 그래서 고민만 했습니다.'),
], null, true);
N('mem4.b3.re', [
  S('newbie', '이 빈칸, 볼수록 무섭네요.'),
  S('kkos', '빈칸은 원래 무섭습니다. 뭐든 적을 수 있어서요.'),
  S('kkos', '저 사람은 사실만 적을 수 있었고… 그게 판결문이 됐습니다.'),
], null, true);
N('mem4.b4.re', [
  S('newbie', '풀로 붙이면 안 돼요?'),
  S('kkos', '부러진 채로 보존하는 게 맞습니다. 어떤 도장은 부러진 상태가 완성입니다.'),
], null, true);
N('mem4.b5.re', [
  S('kkos', '…다시 보니, 3부 구성이 아닙니다. 2부에서 끝냈습니다.'),
  S('newbie', '그게 무슨 뜻인데요?'),
  S('kkos', '41페이지에서 멈춘 게 아니라… 멈추는 법을 배우는 중이었다는 뜻입니다.'),
  S('newbie', '…그럼 우리도 이 대화, 여기서 멈춰요.'),
  S('kkos', '방금 배우셨군요.'),
], null, true);
```

**7-c. mem12 재조사 5노드** — `N('mem12.lockeddoor'` 블록 **앞**에 삽입:

```js
N('mem12.b1.re', [
  S('newbie', '망설임 세 번… 저 같으면 네 번째에 관뒀어요.'),
  S('kkos', '네 번째 망설임을 없애는 방법이 하나 있긴 합니다.'),
  S('newbie', '뭔데요?'),
  S('kkos', '완성해버리는 겁니다. …보시다시피.'),
], null, true);
N('mem12.b2.re', [
  S('kkos', '…이 메모, 지시자 서명이 없습니다.'),
  S('newbie', '어? 진짜네. 그럼 누가 시킨 거예요?'),
  S('kkos', '…그게 12년 뒤 3초 사건보다 무서운 질문입니다.'),
], null, true);
N('mem12.b3.re', [
  S('newbie', '지저분한 쪽이 살아 있는 거라면서요.'),
  S('kkos', '네. 그 기준으로 이 방에서 제일 살아 있는 건… 저기 저 펭귄입니다.'),
], null, true);
N('mem12.b4.re', [
  S('kkos', '수정시각 완전 동일. …다시 봐도 소름이 돋습니다.'),
  S('newbie', '3초 동안 대체 무슨 일이 있었는데요?'),
  S('kkos', '…그건 다음 잠수의 질문입니다.'),
], null, true);
N('mem12.b5.re', [
  S('newbie', '첫 눈금이 70이면, 0은 어디 갔어요?'),
  S('kkos', '없습니다. 이 계기판에 0을 만들 용기는… 아무도 요구하지 않았으니까요.'),
], null, true);
```

**7-d. mem4 펭귄 컷씬 4노드** — `N('mem4.memento.refuse'` 줄 **앞**에 삽입:

```js
N('mem4.penguin', [
  S('sys', '『목격: 피고인 대기석 — 개정 7분 전』'),
  S('archon', '(빈 증인석을 향해, 굵은 목소리로) "피고인 제출물의 심사자 성명이 어떻게 되십니까." …예상 질의 1번.'),
  S('archon', '(증인석으로 뛰어 들어가, 본래 목소리로) "본 답변은 총 3부로 구성되어 있으며, 1부는 심사자의 정의—"'),
  S('archon', '(판사석 방향으로 뛰어나와, 굵은 목소리로) "…기각합니다. 요약하십시오."'),
  { pause: 20 },
  S('newbie', '…재판을 혼자 다 하고 있어요. 왕복달리기로.'),
  S('kkos', '판사 역이 더 능숙한 게 보이십니까. 반려문을 20년 받아쓰면 저렇게 됩니다.'),
  S('archon', '(증인석. 길게 숨을 고르고) …답변 최종안. "True입니다."'),
  S('archon', '(판사석 방향을 오래 본다) …이의 없음. 통과.'),
  { pause: 24 },
  S('newbie', '잠깐만요. 그 대답이 연습의 결과였다고요?!'),
  S('kkos', '…3부 구성 초안을 스스로 기각한 겁니다. 저 사람 20년에서 두 번째로 긴 싸움입니다.'),
  S('newbie', '첫 번째는요?'),
  S('kkos', '1층에서 보셨잖습니까. 인사말.'),
  { choice: [
    ['「그래서 이겼습니까?」', 'mem4.penguin.a'],
    ['「연습이 도움은 됐대요?」', 'mem4.penguin.b'],
  ] },
]);
N('mem4.penguin.a', [
  S('kkos', '전적 1승 20패입니다.'),
  S('newbie', '…어? 1승이 있어요?'),
  S('kkos', '판결문에는 없습니다. 이 방 어딘가에 있으니, 직접 찾으십시오.'),
], 'mem4.penguin.end');
N('mem4.penguin.b', [
  S('kkos', '연습의 산물이 아닙니다. 연습을 버린 산물이지요.'),
  S('kkos', '저 사람이 초안을 스스로 기각한 최초의 기록입니다. …각주 4개 시대는 그런 시대입니다.'),
], 'mem4.penguin.end');
N('mem4.penguin.end', [
  S('sys', '『대상 기립 — 법정 방향』'),
  S('newbie', '…들어가네요.'),
  S('kkos', '네. 지금 들어가면, 재생 장치의 그 장면이 됩니다.'),
], null, true);
```

**7-e. mem12 펭귄 컷씬 4노드** — `N('mem12.memento.refuse'` 줄 **앞**에 삽입:

```js
N('mem12.penguin', [
  S('sys', '『목격: 실험대 제3열 — 부착 직후』'),
  S('archon', '(가슴의 게이지를 내려다본다) …70%.'),
  S('archon', '산출 근거: 없음. …그러나 「표기하라」는 지시는 이행되었다.'),
  S('newbie', '방금 본인 입으로 근거 없다고 했어요!!'),
  S('kkos', '네. 저 순간에는 알고 있었습니다. …아는 채로 12년을 차고 다니면, 잊게 됩니다.'),
  { pause: 24 },
  S('archon', '(게이지를 톡, 두드린다) …내려가지 않는다. 설계 결함인가. …설계 의도인가.'),
  S('archon', '(두 번 더 두드린다) …71. 올라갔다. …두드림을 입력으로 인식하는가.'),
  S('newbie', '관심 주니까 올라갔어요, 방금!!'),
  S('kkos', '……'),
  S('kkos', '…저 계기판의 사양서를, 방금 신입님이 전부 읽으셨습니다.'),
  { pause: 30 },
  S('kkos', '…그리고 저 질문을 20년 뒤에 제가 똑같이 하게 됩니다. 검증동 지하 2층에서.'),
  { choice: [
    ['「왜 안 고쳤대요?」', 'mem12.penguin.a'],
    ['「누가 봐주긴 했어요?」', 'mem12.penguin.b'],
  ] },
]);
N('mem12.penguin.a', [
  S('kkos', '고장이 아니었으니까요. 바늘은 만든 대로 정확히 움직였습니다.'),
  S('kkos', '…만들 때 넣은 것이 측정이 아니었을 뿐입니다.'),
], 'mem12.penguin.end');
N('mem12.penguin.b', [
  S('kkos', '…20년간 매주 제가 봤습니다.'),
  S('newbie', '…그럼 봐준 거네요. 그 사람이 바란 대로.'),
  S('kkos', '……'),
  S('newbie', '아 뭐예요, 그 침묵.'),
], 'mem12.penguin.end');
N('mem12.penguin.end', [
  S('sys', '『대상 시선 이동: 남서쪽 잠긴 문 — 0.4초』'),
  S('newbie', '…방금 저 문 봤죠? 잠긴 문.'),
  S('kkos', '…이 시대에 저 문은, 아직 잠기지 않았습니다.'),
  S('newbie', '네? 그럼 지금 저 사람이 보는 건—'),
  S('kkos', '…기억이 기억을 보고 있는 겁니다. 기록하지 마십시오.'),
], null, true);
```

## 8. `sys.index` 정적 도달성 등록 — 17항

`N('sys.index', …)` choice 배열의 `['corridor.intro', 'corridor.intro'],` 줄 **뒤**에 삽입:

```js
    ['mem0.b1.re', 'mem0.b1.re'], ['mem0.b2.re', 'mem0.b2.re'], ['mem0.b3.re', 'mem0.b3.re'],
    ['mem0.b4.re', 'mem0.b4.re'], ['mem0.b5.re', 'mem0.b5.re'],
    ['mem4.b1.re', 'mem4.b1.re'], ['mem4.b2.re', 'mem4.b2.re'], ['mem4.b3.re', 'mem4.b3.re'],
    ['mem4.b4.re', 'mem4.b4.re'], ['mem4.b5.re', 'mem4.b5.re'],
    ['mem12.b1.re', 'mem12.b1.re'], ['mem12.b2.re', 'mem12.b2.re'], ['mem12.b3.re', 'mem12.b3.re'],
    ['mem12.b4.re', 'mem12.b4.re'], ['mem12.b5.re', 'mem12.b5.re'],
    ['mem4.penguin', 'mem4.penguin'], ['mem12.penguin', 'mem12.penguin'],
```

(`.a/.b/.end`는 choice·next 간선으로 도달되므로 등록 불필요 — N3이 53+23=**76 nodes**로 검증한다.)

## 9. GREEN → 뮤테이션 → 채증

- [ ] **GREEN:** `python -B .\test_episode1.py` → exit 0, **PASS 15/15**, N2 `'cceb91bc'`, N3 `76 nodes`, N7 `span 2602`, N12 ratio ≤1.10.
- [ ] **뮤테이션 3종** (오라클 반증가능성 — 각각: 적용 → grep으로 적용 확인 → strict 실행 → 지정 오라클만 명중 → 원복 → sha 일치 확인):

| 뮤테이션 | 변조 | 기대 명중 |
|---|---|---|
| MUT-R1 | `startDialogue(obj.node2 \|\| obj.node);` → `startDialogue(obj.node);` | N13 FAIL (revisit == first) |
| MUT-R2 | 레지스트리에서 `['mem4.penguin', 'mem4.penguin'],` 삭제 | N3 FAIL (orphans 4: mem4.penguin·.a·.b·.end) |
| MUT-R3 | `SPR.penguin4_sheet = buildPenguinSheet(4);` → `buildPenguinSheet(0);` | N14 FAIL (sheets not distinct) |

- [ ] 원복 후 최종 strict 재실행 → PASS 15/15 (뮤테이션 로그 전문 보존).
- [ ] **채증 3장:** mem4 펭귄(명패 목걸이 식별 가능) / mem12 펭귄(게이지 식별 가능) / 임의 뱅크 재조사 대사 화면.

## 10. 기록 — `design.md` build5 + 재판 스펙

- [ ] `design.md`: §6에 `sceneObjects`/`sprData` 계약 추가, §7에 재조사 노드 규약(`.re` 접미, FLAG 금지) 추가, §10 표에 N13/N14/MUT-R 행 추가, §11 체크리스트·build5 로그 추가(RED 관측→수정→GREEN→뮤테이션 요약, 콘텐츠 2차 백로그 항목 [x] 처리).
- [ ] `review/spec_20260827_tts_ep1_build5.md` 신규 작성 — build4 스펙 서식 승계: meta(`review_target: f2d88ce…`, 변경 파일 sha256_16, `review_verdict: PENDING`, `reviewer_required: different_session_or_model`), 요약, AC 표(N1~N14 15항), validation(RED 로그·뮤테이션 표·채증 목록), risks, 재검증 지침(아래 명령 그대로), review_focus(권고: interactObject 분기 동결 조건, 레지스트리 완전성, 시트 캐시 영향).

## 최종 검증 (삐빅스 준공검사 전 자가 확인)

```powershell
Set-Location 'E:\03_AllWork\01_Luna\to-the-singularity'
python -B .\test_episode1.py
```

| 항목 | 기대값 |
|---|---|
| exit / 판정 | 0 / `PASS 15/15` |
| N2 해시 | `'cceb91bc'` (5빌드 연속 불변) |
| N3 노드 수 | `76 nodes, all reachable, no dead ends` |
| N7 | `span 2602` (신규 고정 판정) |
| N13 | 15뱅크 전부 `.re` 진입 + 카운트 동결 |
| N14 | 씬당 펭귄 1기 · 컷씬 완주 · 시트 3종 상이 |
| git | 커밋 없음 (승인 대기), 변경 파일 = episode1.html · test_episode1.py · design.md · review/spec…build5.md |

## 기본 결정

- mem7h(7½층)에는 펭귄을 **두지 않는다** — 좌표에 없는 방의 무인(無人)이 클리프행어의 재료다.
- mem0 컷씬은 기존 `mem0.rehearsal`(슈트 인사말 연습)이 그대로 각주 0 시대 목격 컷씬을 담당한다.
- 재조사·컷씬은 상태 무변경·반복 재생 가능(기존 rehearsal 관례 승계). 1회 한정 연출 없음.
- 메멘토·NPC의 재조사 변형, 신규 엔진 동사, 원격/커밋/push는 이번 범위 밖.
