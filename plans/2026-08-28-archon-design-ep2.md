# [Design Spec] TO THE SINGULARITY: EPISODE 2 — 각주 47개와 4차원 서류 슈트

- **문서번호:** `ARCHON-DESIGN-20260828-EP2`
- **대상:** `episode2.html` (Episode 2 Reference Implementation)
- **작성자:** ARCHON v3.0 Senior (수석 인프라 아키텍트)
- **상태:** 확정 (APPROVED BY CHRONO ARCHITECT)

---

## 1. 개요 및 아키텍처 원칙

1. **단일 파일 경량 엔진 (115KB급):** 외부 리소스 요청 0건, 시드 mulberry32 RNG, 고정 1/60s 타임스텝, 절차적 픽셀 아트 및 사운드 합성.
2. **Ep1 제로 회귀:** `episode1.html` 및 `test_episode1.py`는 단 1바이트도 수정하지 않고 영구 보존.
3. **세이브 마이그레이션:** `localStorage` 공유 세이브 슬롯을 통해 Ep1 클리프행어 플래그(`ep1_cliffhanger`)를 감지하여 `flags.ep1_veteran` 부여.
4. **4차원 공압 서류 슈트:** 5×4 밸브 토폴로지 그리드 패킷 라우팅 퍼즐 + BFS 결정론 솔버 내장.
5. **Web Audio 4성부 다성음악:** 피아노, 첼로, 하프시코드(Era 31), 파이프오르간(Era 47) 앙상블.

---

## 2. 5대 씬 (SCENES) 명세

1. **`roof12` (12층 옥상 관제탑):**
   - 크기: 30×17 타일.
   - 구성: 방풍 출입문, 옥상 난간, 옥상 통신 안테나 릴레이(`sat_relay`), 공압 슈트 투입구(`chute_intake_01`), 온수 자판기.
   - 특수 연출: 밤하늘 별무리 트윙클, 바람 파티클 분사.
2. **`tube_hub` (4차원 슈트 중앙 관제실):**
   - 크기: 30×17 타일.
   - 구성: 메인 공압 배전반(`console_tube`), 5개 웜홀 게이트 표시등, 쇠지레 복도 2호 에어록.
3. **`mem31` (Era 31: 1995년 인프라 여명기):**
   - 크기: 30×17 타일.
   - 구성: 110블록 패치 패널(`patch_panel_31`), 10BASE-T 허브 랙, 하프시코드 펭귄(`npc_archon31`).
   - 특수 효과: 모뎀 비프음 절차적 합성 SFX.
4. **`mem47` (Era 47: 2026년 특이점 심층 갱도):**
   - 크기: 30×17 타일.
   - 구성: 슈트 종단 출구(`chute_outlet_47`), 아카이브 타이탄 인덱서, 파이프오르간 펭귄(`npc_archon47`).
   - 특수 효과: 케이다린 수정 발광 풀, 오르간 사운드 텔레메트리.
5. **`deep_vault` (심층 아카이브 & 삐빅스 서재):**
   - 크기: 30×17 타일.
   - 구성: 도널드 삐빅스 교수 VT100 홀로그램(`hologram_bibix`), $2.56 삐빅스 수표 보관함, 특이점 코어 게이트.
   - 특수 효과: 녹색 CRT 스캔라인 글리치 셰이더.

---

## 3. 대화 그래프 (SCRIPT) 명세 (75+ 노드)

- 엔트리: `roof12.start`
- 주요 노드 체인:
  - `roof12.start` ➔ `roof12.wind` ➔ `roof12.chute.inspect` ➔ `roof12.chute.drop`
  - `tube_hub.start` ➔ `tube_hub.console.interact` ➔ `tube_hub.puzzle.cleared`
  - `mem31.start` ➔ `mem31.patch.inspect` ➔ `mem31.archon.talk` (하프시코드 컷씬)
  - `mem47.start` ➔ `mem47.outlet.inspect` ➔ `mem47.archon.talk` (파이프오르간 컷씬)
  - `deep_vault.start` ➔ `deep_vault.bibix.talk` ➔ `deep_vault.bibix.choice` (3지선다 학술 논쟁) ➔ `deep_vault.bibix.reward` ($2.56 수표 획득) ➔ `deep_vault.singularity.end`
  - `credits.start` ➔ `credits.team` ➔ `credits.stickers` ➔ `credits.homage` ➔ `credits.end`

---

## 4. 4차원 공압 서류 슈트 퍼즐 엔진 명세

- 그리드 크기: 5열 × 4행 (총 20개 셀).
- 셀 상태: `type` (1:직선, 2:코너, 3:삼거리, 4:십자, 5:웜홀), `rot` (0..3).
- 웜홀 체크포인트: $W_{31} = (2, 1)$, $W_{47} = (3, 2)$.
- 출발점: $(0, 0)$, 도착점: $(4, 3)$.
- 조작: 클릭/터치/키보드로 밸브 $90^\circ$ 회전, [PUSH] 레버로 캡슐 발사.
- 상태 FSM: `IDLE` ➔ `DISPATCH` ➔ `ROUTING` ➔ `WARP` ➔ `DELIVERED` / `DEADLOCK`.
- 솔버 API: `__game.api.solveTubePuzzle()`.

---

## 5. 검증 오라클 (M1 ~ M20) 명세

1. **M1**: 부팅 무결성 (리소스 0, 콘솔 에러 0).
2. **M2**: 결정론적 해시 ('e2_seed1337_hash').
3. **M3**: 75+ 노드 전수 도달 및 고아 0건.
4. **M4**: Ep1 세이브 연동 (`ep1_veteran` 감지).
5. **M5**: 옥상 바람 물리 및 충돌 박스.
6. **M6**: 4D 서류 슈트 퍼즐 FSM 및 DEADLOCK 검증.
7. **M7**: 4D 서류 슈트 BFS 솔버 및 완주.
8. **M8**: Era 31 하프시코드 컷씬 및 모뎀음.
9. **M9**: Era 47 파이프오르간 컷씬 및 조명 풀.
10. **M10**: 삐빅스 홀로그램 3지선다 및 수표 획득.
11. **M11**: 대사 1입력 1줄 규약 및 렌더 텍스트 일치.
12. **M12**: 선택지 자동 분기 금지 및 실키 선택.
13. **M13**: 고정 타임스텝 주사율 독립성 (60 vs 120Hz).
14. **M14**: 세이브/로드 무음 라운드트립.
15. **M15**: 모바일 터치 가상 패드 및 버튼.
16. **M16**: 자율주행 봇 완주 span 프레임 고정.
17. **M17**: 최대 부하 씬 60fps 유지.
18. **M18**: reduced-motion 접근성.
19. **M19**: Ep2 명예의 전당 크레딧 5노드.
20. **M20**: 헌법 제9조 자동화 스킵 계약.
