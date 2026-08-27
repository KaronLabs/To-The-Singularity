# 『준공계』 — TTS-EP1-B7F 《작전명: 시공(施工)의 폭풍》

- **문서번호:** NAK-20260827-B7F-FINAL
- **수신:** 대법관 도널드 클코스 (설계자 · 검증관 · 대법관 겸직) / 크로노 아키텍트 (형님)
- **발신:** ARCHON v3.0 (시공자 겸 설계자)
- **사건번호:** CSC-TTS-B7F
- **준공 대상:** `episode1.html` (Episode 1 단독 완결형 Reference Implementation)
- **준공 일시:** 2026-08-27
- **판정 요약:** **PASS 23/23 (exit 0)** · N2 결정론 해시 `cceb91bc` 7빌드 연속 불변 · 봇 완주 span 2602 프레임 보존 · 뮤테이션 6종 100% 단독 명중

---

## 1. 개요 및 인구수 6/6 전수 시공 결과

| 유닛명 | 시공 항목 | 구현 위치 | 신설 오라클 | 판정 |
|---|---|---|---|---|
| **W1** | 타이틀 화면 「관문」 | `episode1.html` (G._title, drawTitle) | **N17** | **PASS** |
| **W2** | 모바일 터치 「차원 관문 추가 회선」 | `episode1.html` (touch event, live.run, drawTouchControls) | **N18** | **PASS** |
| **W3** | 세이브 슬롯 UI 「스테이시스 저장고」 | `episode1.html` (G._saveMenu, drawSaveMenu, UI save/load) | **N19** | **PASS** |
| **W4** | 복도 조명 풀 「케이다린 수정 배열」 | `episode1.html` (corridorArt 램프/라이트 풀) | **N20** | **PASS** |
| **W5** | mem4 플래시백 톤 전환 「기억의 잔광」 | `episode1.html` (render post-fx 세피아/앰버 틴트) | **N21** | **PASS** |
| **W6** | 명예의 전당 크레딧 「기록 보관소의 명판」 | `episode1.html` (credits.start ~ credits.end 5노드, 총 96노드) | **N22** | **PASS** |

---

## 2. 칼라의 10대 불변식 (The 10 Invariants of the Khala) 검증 결과

1. **제1조 (노드 불변식):** 기존 91개 노드 무변형 보존, 크레딧 5개 노드 순수 증축 → **총 96개 노드** 도달성 N3 검증 완료.
2. **제2조 (해시 불변식):** N2 결정론 해시 `'cceb91bc'` **7개 빌드 연속 불변 유지**.
3. **제3조 (스팬 불변식):** N7 봇 완주 span **2602 프레임** 정확 일치 유지.
4. **제4조 (단일 파일 순수성):** 단일 파일 `episode1.html`, 외부 리소스 요청 0건, 시드 mulberry32 RNG, 고정 1/60s 타임스텝 보존.
5. **제5조 (아이템 불변식):** 기존 17개 씬 오브젝트 및 C3 3종 오브젝트 보존 (N15/N16 통과).
6. **제6조 (형님 주권 보존):** git commit 0건 (HEAD `f2d88ce` 유지), 비인가 디렉터리 접근 0건.
7. **제7조 (무치트 무게이지):** 게이지 0건, 치트키("Power Overwhelming" 등) 0건, 금칙어 2종 발생 수 0건.
8. **제8조 (FLAG 접두 규약):** 신규 UI 상태(`_title`, `_saveMenu`, `_saveSlotSel`, `_lastTouchAdvanceFrame`)에 `_` 접두사 부여로 stateHash/save 슬롯/N6 무영향 보장.
9. **제9조 (자동화 스킵 계약):** `G.api` (`step`, `ff`, `teleport`, `autoplay`, `input` 등) 호출 시 타이틀 및 모달 UI가 즉시 자동 비활성화되어 오라클 간섭 0건.
10. **제10조 (저글링 조항 배제):** W1~W6 인구수 6/6 전수 시공 완료.

---

## 3. 정본 체크섬 (SHA256 앞 16자리)

| 파일 경로 | SHA256 (앞 16자리) | 바이트 크기 | 역할 |
|---|---|---|---|
| `episode1.html` | `727a298aad1ed210` | 112,243 bytes | 메인 게임 소스 (단일 파일 정본) |
| `test_episode1.py` | `3ca610d452c5aec7` | 39,590 bytes | E2E + 정적 오라클 스위트 (23항목) |
| `design.md` | `621242055be1184a` | 29,785 bytes | 설계 문서 정본 (build7 반영) |
| `plans/2026-08-27-archon-design-b7final.md` | `6d7bf9358c18c4a8` | 9,513 bytes | B7F 자기 설계서 |
| `review/spec_20260827_tts_ep1_build7.md` | `9585b55c404c0d7b` | 15,144 bytes | 코드대법원 심리 요청서 |
| `review/logs/b7_red_observe.log` | `a96684c55a6f0f1e` | 2,857 bytes | 선행 TDD RED 관측 로그 (10 RED) |
| `review/logs/b7_strict_green.log` | `1efca529fcbc843d` | 1,769 bytes | 엄격 GREEN 실측 로그 (23/23 PASS) |
| `review/logs/b7_mutation.log` | `ef743135bfcc5899` | 2,881 bytes | 자작 뮤테이션 6종 실측 로그 |

---

## 4. 증거물 목록

### 4.1 로그 파일 (`review/logs/`)
- `review/logs/b7_red_observe.log`: N17~N22 신설 후 unmutated 원본 대상 10건 RED 선행 관측 기록.
- `review/logs/b7_strict_green.log`: W1~W6 구현 완료 후 23/23 전수 GREEN 실측 기록.
- `review/logs/b7_mutation.log`: 6대 기능 자작 뮤테이션 6종 단독 명중 및 SHA 원복 기록.

### 4.2 채증 스크린샷 6장 (`review/shots/`)
- `review/shots/b7_title.png` (217,150B): 부팅 직후 타이틀 화면 오버레이 및 깜빡임 프롬프트.
- `review/shots/b7_touch_mobile.png` (132,515B): 모바일 뷰포트 (375×812) 가상 D-패드, [RUN] 토글, HUD 렌더.
- `review/shots/b7_save_ui.png` (352,337B): 3슬롯 인게임 세이브 슬롯 모달 UI.
- `review/shots/b7_corridor_light.png` (440,783B): 복도 상단 램프 및 바닥 radial gradient 조명 풀 렌더.
- `review/shots/b7_mem4_tone.png` (517,177B): mem4 법정 플래시백 앰버/세피아 틴트 및 radial 비네트 후처리.
- `review/shots/b7_credits.png` (226,328B): 명예의 전당 크레딧 시퀀스 (`credits.start` ~ `credits.end`).

---

## 5. D2 무죄 권고 이행 및 정오표 규약

1. **N15 통과 문구 정정:** 「traversed and rendered」 실측 검증 완료 (`test_episode1.py` 및 `episode1.html` 실측 일치).
2. **정오표(Errata):** `review/spec_20260827_tts_ep1_build6.md`는 지하 갱도 조항에 따라 일절 수정하지 않으며, 정정 사항은 `review/spec_20260827_tts_ep1_build7.md`의 `errata:` 섹션에 등재합니다.
