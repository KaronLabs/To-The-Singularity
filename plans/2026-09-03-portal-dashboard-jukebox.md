# [포털 개편] index.html 3부작 통합 관측 대시보드 & 절차적 주크박스 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `index.html`을 단순한 텍스트 링크 목록에서 3부작(Ep1/Ep2/Ep3)의 `localStorage` 세이브 슬롯을 실시간 집계하는 **「종합 관측 계측기」** 및 각주 슬라이더 기반 **「Web Audio 절차적 주크박스」**가 통합된 반응형 느와르 포털로 업그레이드한다.

**Architecture:** 
- 외부 리소스 요청 0건(Zero Network Requests) 원칙을 100% 사수하며 순수 HTML5/CSS/Vanilla JS/Web Audio API로 단일 파일 `index.html`에 구현.
- `episode1.html`, `episode2.html`, `episode3.html` 및 관련 테스트 스위트 3종(N1~N22, M1~M22, C1~C23)은 단 1바이트도 수정하지 않고 영구 보존(Zero-Regression).
- 신규 E2E 테스트 스위트 `test_index.py`를 작성하여 정적 계약, 로컬스토리지 연동, 계측기 게이지 진동, 주크박스 오디오 슬라이더 상태 전이를 엄격히 검증.

**Tech Stack:** HTML5, CSS3 Custom Properties & CRT scanlines, Vanilla JavaScript (ES5/ES6 호환), Web Audio API (Oscillator/Gain/BiquadFilter), Python Playwright E2E.

**Spec:** 사용자 요구사항 (2026-09-03)
- `localStorage` 3부작 키 실시간 스캔: `tts_ep1_s1..3`, `tts_ep2_slot_1..3`, `tts_ep3_s1..3`
- 종합 인장 3종:
  - Ep1: `[7½층 도달: 각주 47개 답장 발견]` (`flags.ep1_cliffhanger` 또는 `scene === 'mem7h'`)
  - Ep2: `[삐빅스 수표 $2.56 보유]` (`mementos.includes('check_256')`)
  - Ep3: `[반려 1,901호 판결: 통산 1승 달성]` (`flags.ep3_done` 또는 `flags.ep3_verdict`)
- Total Singularity Gauge: 70% (0개) → 80% (1개) → 90% (2개) → 100% (3개 올클리어) 아날로그 바늘 & 클릭/터치 반응
- 테이프 데크 주크박스: 각주 슬라이더(0 → 4 → 12 → 31 → 47)로 실시간 악기 모핑 (뮤직박스 → 베이스 → 아르페지오 → 하프시코드 → 파이프오르간/첼로 풀 앙상블)

## Global Constraints
- `episode1.html`, `episode2.html`, `episode3.html`을 절대 수정하지 않는다. (Ep1 SHA: `727a298aad1ed210`, Ep2 SHA: `6b786661b8b2dd14`, Ep3 SHA: `439edc2fd839c613`)
- `index.html` 내 외부 스크립트, 웹폰트, 외부 CDN, 이미지 파일 로드 0건 유지.
- 오디오는 브라우저 사용자 제스처 정책을 준수하여 첫 클릭/터치 시 기동.
- 모든 기능은 모바일 터치 및 데스크톱 브라우저 환경에서 동등 작동.

---

### Task 1: 테스트 하네스 `test_index.py` 선행 구축 (RED Phase)

**Files:**
- Create: `test_index.py`

**Interfaces:**
- Consumes: `index.html` DOM 및 `window.__portal` 디버그/텔레메트리 객체
- Produces: 8개 테스트 오라클 (P1 ~ P8)
  - P1: 외부 네트워크 리소스 0건, 콘솔 에러 0건 부팅
  - P2: `localStorage`가 비어있을 때 기본 게이지 70.00% 및 3개 인장 미도달 상태 렌더
  - P3: Ep1 세이브 주입 시 Ep1 인장 활성화 및 게이지 80.00% 갱신
  - P4: Ep2 세이브($2.56 수표) 주입 시 Ep2 인장 활성화 및 게이지 90.00% 갱신
  - P5: Ep3 세이브(1승 판결) 주입 시 Ep3 인장 활성화 및 게이지 100.00% (특이점 돌파) 갱신
  - P6: 게이지 두드림(클릭/터치) 시 텔레메트리 반응 및 일시적 떨림(jiggle) 플래그
  - P7: 주크박스 재생/정지 버튼 상태 전이 및 Web Audio 가동
  - P8: 각주 슬라이더 조절(0, 4, 12, 31, 47) 시 주크박스 활성 음색(voices) 레이어 수 및 악기 편성 갱신

- [ ] **Step 1: Write the failing test suite `test_index.py`**
  Playwright 동기 스크립트로 `index.html`을 띄우고 가상 `localStorage` 데이터를 주입하여 P1~P8 단언을 수행하는 테스트 코드 작성.

- [ ] **Step 2: Run test to verify it fails (RED)**
  `python -B test_index.py` 실행하여 현재의 정적 `index.html`에 대시보드와 주크박스가 없으므로 FAIL 관측.

- [ ] **Step 3: Commit RED test suite**
  `git add test_index.py` 및 커밋.

---

### Task 2: `localStorage` 3부작 관측 엔진 & 인장 UI 구현 (GREEN Phase 1)

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: 브라우저 `localStorage`
- Produces: `scanTrilogySaves()`, `window.__portal.state`, 인장 배지 3기 및 에피소드 카드 상태 표시

- [ ] **Step 1: Write `scanTrilogySaves()` 함수 및 상태 구조체**
  - Ep1: `tts_ep1_s1`, `tts_ep1_s2`, `tts_ep1_s3` 순회 파싱 → `flags.ep1_cliffhanger` 또는 `scene === 'mem7h'` 감지
  - Ep2: `tts_ep2_slot_1`, `tts_ep2_slot_2`, `tts_ep2_slot_3` 순회 파싱 → `mementos.includes('check_256')` 감지
  - Ep3: `tts_ep3_s1`, `tts_ep3_s2`, `tts_ep3_s3` 순회 파싱 → `flags.ep3_done` 또는 `flags.ep3_verdict` 감지
- [ ] **Step 2: 인장 3기 배지 및 동적 카드 상태 UI 마크업/스타일링**
  - 카드 내에 `[관측 대기 중]` ➔ `[기록 확보: 7½층 도달]`, `[삐빅스 수표 $2.56 보유]`, `[반려 1,901호 판결 1승]` 동적 인쇄
  - 느와르풍 올리브/스틸/앰버/CRT 테마 스타일 적용
- [ ] **Step 3: Run partial tests P1 ~ P5 to verify PASS**
  `python -B test_index.py` 실행하여 P1~P5 통과 확인.

---

### Task 3: Total Singularity Gauge 아날로그 계기판 & 터치 두드림 구현 (GREEN Phase 2)

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `scanTrilogySaves()` 클리어 카운트 (0~3)
- Produces: SVG/CSS 바늘 계기판 HUD, `jiggleGauge()` 인터랙션

- [ ] **Step 1: 게이지 HUD 시각화 컴포넌트 마크업 & CSS**
  - 70% ~ 100% 스케일 아날로그 계기판 (황동 바늘, 눈금, CRT 수치 표시)
  - 100% 도달 시 황금빛 인광 및 특이점 도달 배너 `[SINGULARITY ACHIEVED]` 발광
- [ ] **Step 2: 클릭/터치 두드림 인터랙션 결속**
  - 계기판 영역 mousedown / touchstart 시 바늘 각도 미세 진동 (+1px 떨림 및 순간 +0.5% 반동 애니메이션)
  - 관측 기록: "두드림: 입력으로 인식됨 (+1)" 문구 동적 노출
- [ ] **Step 3: Run partial test P6 to verify PASS**
  `python -B test_index.py` 실행하여 P6 통과 확인.

---

### Task 4: 테이프 데크 주크박스 & 각주 슬라이더 실시간 모핑 합성기 구현 (GREEN Phase 3)

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: Web Audio API (`AudioContext`, `OscillatorNode`, `GainNode`, `BiquadFilterNode`)
- Produces: `JUKEBOX` 싱글톤 객체, `setFootnotes(n)`, 테이프 회전 카세트 애니메이션

- [ ] **Step 1: Web Audio 〈각주를 위하여〉 선율 및 폴리포니 스케줄러 이식**
  - `NOTE` 주파수 맵 및 `LEAD`, `ARP`, `COUNTER` 멜로디 배열
  - 5개 악기 음색 합성기:
    - `musicbox`: 순수 사인파 + 3배음 (맑은 오르골)
    - `bass`: 저역 필터링 삼각파 (5도 베이스)
    - `piano`: 듀얼 디튠 삼각파 (아르페지오)
    - `harpsichord`: 고역 배음 톱니파 (Era 31 패킷실)
    - `organ`: 옥타브 레이어드 사각파 + 로우패스 (Era 47 특이점 갱도)
- [ ] **Step 2: 각주 슬라이더 (0, 4, 12, 31, 47) 모핑 로직**
  - 슬라이더 값에 따라 각 악기 트랙의 Gain 볼륨을 선형 보간(cross-fade)하여 끊김 없이 편성 확장
  - 슬라이더 조절 시 인쇄 레이블:
    - 0: `각주 0개 · 뮤직박스 단선율`
    - 4: `각주 4개 · 베이스 보강`
    - 12: `각주 12개 · 아르페지오 편곡`
    - 31: `각주 31개 · 하프시코드 앙상블`
    - 47: `각주 47개 · 파이프오르간 풀 코랄`
- [ ] **Step 3: 테이프 데크 UI (재생/정지 버튼, 카세트 릴 회전 애니메이션)**
- [ ] **Step 4: Run full test suite `test_index.py` to verify 8/8 PASS**
  `python -B test_index.py` 실행하여 P1 ~ P8 전수 GREEN 확인.

---

### Task 5: 3부작 회귀 제로 전수 검증 & 최종 배포 점검

**Files:**
- Test: `test_episode1.py`, `test_episode2.py`, `test_episode3.py`, `test_index.py`

- [ ] **Step 1: Run complete 4-suite regression pipeline**
  ```bash
  python -B test_episode1.py
  python -B test_episode2.py
  python -B test_episode3.py
  python -B test_index.py
  ```
  Ep1 (23/23), Ep2 (23/23), Ep3 (23/23), Portal (8/8) 전수 `exit 0` 통과 확인.
- [ ] **Step 2: Commit portal upgrade**
  ```bash
  git add index.html test_index.py plans/2026-09-03-portal-dashboard-jukebox.md
  git commit -m "feat: index.html 3부작 통합 관측 대시보드 & 각주 모핑 주크박스 완공"
  ```
