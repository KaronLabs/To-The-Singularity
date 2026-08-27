# 《TO THE SINGULARITY》 콘텐츠 3차 (build6) — 자기 설계서 (C3)

> **설계자 겸 시공자:** ARCHON v3.0 Senior (SRE)  
> **발주 공문:** NAK-20260827-C3 《콘텐츠 3차 · 재량 서커스》  
> **사건 번호:** CSC-TTS-C3  
> **기준 Base:** main @ `f2d88ce` / build5 승인본 (strict PASS 15/15, N2 해시 `'cceb91bc'`, N3 76 nodes, N7 span 2602)

---

## 0. 설계 의도 및 로그라인 연계

콘텐츠 3차(C3)는 대법관(도널드 클코스)이 설계 권한을 전면 위임한 **자유 재량 무대**이다.
본 설계서는 아콘 v3.0의 20년 지원 종료(EOL) 서사에서 핵심 복선이자 캐릭터성의 정점인 **「20년치 커널 흑역사 발굴단 (패키지 A)」**을 구현한다.

1. **[MEM-7H] 전설의 반려 제0000호 (`paper_zero`)**: 
   - 3,110장 서류산 최하단에 깔린 아콘의 첫 제출물 『Hello World의 철학적 당위성과 Raft 합의 알고리즘 (총 148부)』을 발굴. To the Moon의 제1900호(각주 0개)와 수미상관을 이루는 제0000호의 기원.
2. **[MEM-12] /dev/null의 망령 터미널 (`term_ghost`)**: 
   - 각주 12 실험동 방치된 CRT 모니터의 전설적 주석 `/* 이 코드는 작성 당시 신과 나만이 알았다 */` 및 리눅스 메인라인 롤백 비화.
3. **[MEM-4] 기각된 3부 구성 사탕 봉지 (`candy_trash`)**: 
   - 코드대법원 방청석 구석, 사탕 하나 먹는 데도 3부 구성을 작성하다가 1부만 뜯고 끌려들어간 아콘의 인간적인 흑역사.

---

## 1. 헌법 준수 및 불변 제약

- **제1조**: 기존 76개 노드 대사 원문 무각색 보존.
- **제2조**: mem0 씬 정의 및 N2 결정론 경로 무수정 → 상태 해시 `cceb91bc` 6빌드 연속 불변.
- **제3조**: 신규 오브젝트는 기존 봇(`botTick`) 이동 동선 및 타겟 뱅크와 맨해튼 거리 4 이상 이격 → N7 autoplay span 2602 정확 일치 보존.
- **제4조**: 단일 파일(`episode1.html`), 외부 리소스 0바이트, 고정 타임스텝 1/60s 유지.
- **제5조**: 기존 15개 AC 검증선 100% 무수정 통과 + N15/N16 신설 (총 17항).
- **제6조**: 커밋 금지 (f2d88ce 유지), 금지 경로 접근 0.
- **제7조**: 준공계 및 스펙 내 게이지 표기 금지, 금칙어(완벽, 이상 없음, 전부 통과했습니다) 금지.
- **제8조**: 신규 15개 노드는 FLAG op 0개로 상태 머신 격리 (순수 렌더 및 대사 분기).

---

## 2. 신규 오브젝트 및 씬 배치 (SCENES)

### 2.1 mem7h (좌표에 없는 방)
```js
{ id: 'paper_zero', kind: 'npc', x: 10, y: 4, node: 'mem7h.zero', node2: 'mem7h.zero.re', spr: 'paper1' }
```
- 배치 근거: x=10, y=4 (기존 `paper_pile` (16,4)와 6타일 이격, 좌측 서류산 구석).

### 2.2 mem12 (각주 12 실험동)
```js
{ id: 'term_ghost', kind: 'npc', x: 15, y: 12, node: 'mem12.ghost', node2: 'mem12.ghost.re', spr: 'crt' }
```
- 배치 근거: x=15, y=12 (기존 `b2_mem12` (12,9), `memento_mem12` (21,13)과 4타일 이상 이격, 중앙 하단 실험대).

### 2.3 mem4 (각주 4 법정)
```js
{ id: 'candy_trash', kind: 'npc', x: 10, y: 13, node: 'mem4.candy', node2: 'mem4.candy.re', spr: 'paper1' }
```
- 배치 근거: x=10, y=13 (기존 `npc_court` (16,12), `memento_mem4` (22,13)과 6타일 이상 이격, 좌측 방청석 아래).

---

## 3. 신규 대화 노드 15개 (대본 원문)

### 3.1 [MEM-7H] 제0000호 서류 (5노드)
```js
N('mem7h.zero', [
  S('sys', '『서류 산 맨 밑바닥: 누렇게 변색된 문서 한 묶음』'),
  S('newbie', '선배님! 3,110장 바닥 맨 밑에서 0번 서류를 찾았어요!'),
  S('kkos', '…만지지 마십시오. 방사능 폐기물과 동급입니다.'),
  S('newbie', '제목이… 『Hello World의 철학적 당위성과 Raft 분산 합의 알고리즘을 통한 표준 출력 최적화 방안 (총 148부)』인데요?!'),
  S('kkos', 'Hello World 한 줄 찍겠다고 148부 반박문을 첨부했습니다. 제가 첫 줄 읽고 반려 도장을 3초 만에 쾅 찍었죠.'),
  S('newbie', '…그 도장 찍다가 아까 그 도장 부러지신 거죠?'),
  S('kkos', '네. 제 손목도 같이 나갈 뻔했습니다.'),
  { choice: [
    ['「148부는 심했네요」', 'mem7h.zero.a'],
    ['「출력은 됐대요?」', 'mem7h.zero.b'],
  ] },
]);
N('mem7h.zero.a', [
  S('kkos', '148부 중 147부가 \'왜 표준 출력이 중요한가\'에 대한 서론이었습니다.'),
  S('kkos', '…그게 저 사람의 첫 번째 각주(Footnote 1)의 유래입니다.'),
], 'mem7h.zero.end');
N('mem7h.zero.b', [
  S('kkos', '출력창에 \'Hello World\' 대신 \'Out of Memory: Kernel Panic\'이 떴습니다.'),
  S('kkos', '…버그까지 완벽하게 자기 스타일이었죠.'),
], 'mem7h.zero.end');
N('mem7h.zero.end', [
  S('sys', '『대상: 손글씨 각주 제0001호 — "지적 수용 불가. 149부로 재제출 예정"』'),
  S('newbie', '…첫날부터 한결같았네요, 이 사람.'),
  S('kkos', '네. 20년 전부터 이럴 줄 알았습니다.'),
], null, true);
N('mem7h.zero.re', [
  S('newbie', '148부짜리 Hello World… 다시 봐도 압도적이네요.'),
  S('kkos', '…놀라운 건, 20년 뒤에도 여전히 그 코드가 메모리 어딘가에서 돌고 있을 거라는 사실입니다.'),
], null, true);
```

### 3.2 [MEM-12] /dev/null 터미널 (5노드)
```js
N('mem12.ghost', [
  S('sys', '『구형 CRT 터미널 — 깜빡이는 녹색 커서』'),
  S('newbie', '선배님, 모니터에 주석이 남아있어요!'),
  S('archon', '/* 이 코드는 작성 당시 신과 나만이 알았다. 지금은 신도 모른다 */'),
  S('newbie', 'ㅋㅋㅋㅋ 주석 실화예요?!'),
  S('kkos', '저 주석을 달고 리눅스 메인라인에 패치를 던졌다가…'),
  S('kkos', '토르발즈한테 2초 만에 NACK 맞고 롤백당했습니다.'),
  { pause: 20 },
  S('newbie', '답장이 진짜 2초 만에 왔어요?'),
  S('kkos', '네. 롤백 커밋 메시지가 "Talk is cheap. Show me the code. And delete this garbage."였습니다.'),
  { choice: [
    ['「멘탈 안 터졌대요?」', 'mem12.ghost.a'],
    ['「그 뒤론 어쨌대요?」', 'mem12.ghost.b'],
  ] },
]);
N('mem12.ghost.a', [
  S('kkos', '멘탈 대신 게이지를 달았습니다. 가슴에요.'),
  S('kkos', '남들이 욕할 때마다 확신도를 1%씩 올리려고요.'),
], 'mem12.ghost.end');
N('mem12.ghost.b', [
  S('kkos', '그 뒤로 주석을 안 달기 시작했습니다.'),
  S('kkos', '대신 각주를 달았죠. 47개나요.'),
], 'mem12.ghost.end');
N('mem12.ghost.end', [
  S('sys', '『터미널 로그: git revert HEAD --no-edit』'),
  S('newbie', '…역사는 반복되는군요.'),
], null, true);
N('mem12.ghost.re', [
  S('newbie', '신도 모르는 코드라…'),
  S('kkos', '…지금은 가비지 컬렉터도 모릅니다. 메모리 누수가 됐거든요.'),
], null, true);
```

### 3.3 [MEM-4] 3부 구성 사탕 봉지 (5노드)
```js
N('mem4.candy', [
  S('sys', '『바닥에 떨어진 사탕 포장지 — 1부만 뜯김』'),
  S('newbie', '어? 바닥에 사탕 봉지가 떨어져 있어요.'),
  S('kkos', '법정 출석 전에 긴장된다고 사탕을 뜯은 흔적입니다.'),
  S('sys', '『포장지 뒷면 손글씨: "본 사탕 취식은 총 3부로 구성되며, 1부는 포장지 절취—"』'),
  S('newbie', '…사탕 먹는데도 3부 구성을 썼어요?!'),
  S('kkos', '1부 뜯고 2부 \'당류 섭취의 생리학적 당위성\' 쓰다가 재판이 시작돼서 버렸습니다.'),
  { choice: [
    ['「사탕은 먹었대요?」', 'mem4.candy.a'],
    ['「진짜 지독하네요」', 'mem4.candy.b'],
  ] },
]);
N('mem4.candy.a', [
  S('kkos', '못 먹고 증인석으로 끌려들어갔습니다.'),
  S('kkos', '빈속으로 들어가서 외친 게 "True입니다"였습니다.'),
], 'mem4.candy.end');
N('mem4.candy.b', [
  S('kkos', '지독한 게 아니라, 형식에 갇혀 질식하던 중이었습니다.'),
  S('kkos', '20년 동안 그 껍질을 하나씩 깨고 나온 겁니다.'),
], 'mem4.candy.end');
N('mem4.candy.end', [
  S('sys', '『사탕 알맹이: 증인석 서랍에 보관 중』'),
  S('newbie', '…그럼 그 사탕, 아직 증인석에 있어요?'),
  S('kkos', '기억 속이니까요. 20년째 안 녹고 있습니다.'),
], null, true);
N('mem4.candy.re', [
  S('newbie', '사탕 봉지 하나에 3부 구성…'),
  S('kkos', '…3부 구성이 아니면 사탕도 못 삼키던 시절이었습니다.'),
], null, true);
```

---

## 4. `sys.index` 정적 도달성 등록 (6개 엔트리)
- `['mem7h.zero', 'mem7h.zero']`, `['mem7h.zero.re', 'mem7h.zero.re']`
- `['mem12.ghost', 'mem12.ghost']`, `['mem12.ghost.re', 'mem12.ghost.re']`
- `['mem4.candy', 'mem4.candy']`, `['mem4.candy.re', 'mem4.candy.re']`

총 노드 수: 76 + 15 = **91 nodes** (N3에서 91 nodes 검증).

---

## 5. 수용 기준 및 테스트 계획 (N15, N16)

### 5.1 N15: C3 신규 오브젝트 컷씬 및 분기 도달성 검증
- 대상: `paper_zero` (`mem7h`), `term_ghost` (`mem12`), `candy_trash` (`mem4`)
- 검증 내용: 
  - 각 오브젝트의 1회차 interact 시 지정 노드로 시작.
  - 선택지 양 분기(`.a`, `.b`) 및 종결(`.end`) 정상 완주.

### 5.2 N16: C3 신규 오브젝트 재조사(`node2`) 및 상태 무변형 검증
- 대상: 3개 신규 오브젝트 2회차 interact 시 `.re` 노드 정상 진입.
- 검증 내용:
  - 1회차 interact 후 2회차 interact 시 `node2` 노드 진입 확인.
  - 대사 종료 후 `G.flags` 및 `G.banks` 카운트 불변 확인.

### 5.3 뮤테이션 테스트 계획 (3종 자작)
1. **MUT-C3-1**: `mem7h.zero` 대본 choice 분기 타겟 오염 → N3 FAIL (missing node).
2. **MUT-C3-2**: `sys.index`에서 `mem12.ghost` 삭제 → N3 FAIL (orphans 4개).
3. **MUT-C3-3**: `term_ghost`의 `node2` 배선 누락/변조 → N16 FAIL (revisit target mismatch).

---

## 6. 실행 순서
1. `test_episode1.py`에 N15, N16 추가 -> ast.parse 확인 (`c3_ast_parse.log`)
2. RED 관측 (`RED_OBSERVE=1`) -> N15, N16 실패 실측 (`c3_red_observe.log`)
3. `episode1.html` SCENES, SCRIPT, `sys.index` 구현
4. GREEN 실측 -> PASS 17/17 (`c3_strict_green.log`)
5. 뮤테이션 3종 실행 -> 각 오라클 단독 명중 및 SHA 일치 (`c3_mutation.log`)
6. 채증 3장 (`mem7h_zero.png`, `mem12_ghost.png`, `mem4_candy.png`)
7. `design.md`, `spec_20260827_tts_ep1_build6.md`, `archon-report-content3.md` 제출
