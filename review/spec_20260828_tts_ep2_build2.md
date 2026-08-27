# Code Supreme Court Review Spec — Episode 2 build2 (갱생 이행본)

meta:
  created_at: 2026-08-28
  review_mode: standard
  review_target: working_tree_f2d88ce / episode2.html (ep2-build2)
  comparison_base: episode2.html ep2-build1 sha256_16 `c1b55052216e34a0` (증거 보전: review/evidence_ep2_archon/)
  submitter: 도널드 클코스 (삼권통합 대법관 — 본 건에서는 시공자 신분)
  submitter_note: 본 건의 시공자는 CSC-TTS-EP2 담당 판사와 동일인이므로, 이해충돌 원칙에 따라 자가 판결을 금하고 PENDING으로 상정한다.
  reviewer_required: different_session_or_model (삐빅스 또는 독립 세션 권장)
  checksums_sha256_16:
    episode2.html: da965927be0f885d (65,031B + touch-action 패치, LF)
    test_episode2.py: f4778c9a55ef3c6e (Static + M1~M22)
    episode1.html: 727a298aad1ed210 (Ep1 무수정 보존)
    design.md: 8c71cab6b863b6ac (§12 Ep2 빌드 대장 등재)
  changed_files: episode2.html, test_episode2.py, design.md, review/spec_20260828_tts_ep2_build2.md,
    review/logs/ep2_red_observe_build2.log, review/logs/ep2_strict_green_build2.log,
    review/logs/ep2_mutation_build2.log, review/shots/ep2b2_*.png (7),
    review/evidence_ep2_archon/ (build1 원본 보전 2건)

summary:
  CSC-TTS-EP2 판결(GUILTY / REVISE / 🍕56)의 강제 갱생 명령 8건을 전수 이행한 build2.
  절차는 선(先)오라클: 강화 슈트(M1~M22) 작성 → build1 대상 RED 22건 실캡처 → 시공 →
  GREEN 23/23 (exit 0) → 뮤테이션 9종 → 채증 7장 육안 → 본 스펙.

rehab_orders_execution:
  - order: 1 (Ep1 세이브 연동 키 정정)
    action: checkEp1Migration()이 Ep1 실키 tts_ep1_s1..3을 순회 판독. 유령 키 tts_save_slot_1 제거.
    verified: M4 — 실키 양성 + 무세이브 부정 케이스.
  - order: 2 (퍼즐 인게임 배선 + BFS 실구현)
    action: 배전반 대화 종료 시 PUZZLE.active 실개방(엔진 간선). 파이프 개구부 비트마스크 라우팅
      trace()(BFS 플러드) + 4차원 상태공간 (x, y, W31경유, W47경유) BFS solve()(회전 배정 후 trace 재검증).
      DELIVERED → 24프레임 후 cleared 대화 및 puzzle_tube_cleared 게이트. setTimeout 전면 제거.
      키보드 커서(방향키/E/Enter/Esc) + 클릭/탭 조작.
    verified: M6(스크램블→DEADLOCK 정확, rotate→IDLE), M7(인게임 개방→솔브→DELIVERED→cleared 대화+플래그).
  - order: 3 (모바일 터치 실장)
    action: touchstart/move/end 3종 리스너, D-pad/RUN 토글/[E] HUD, 탭 진행, preventDefault +
      canvas `touch-action: none` (MDN 공식 문서 교차확인 후 반영).
    verified: M15 — has_touch 컨텍스트에서 실 TouchEvent 디스패치: D-pad 보행, RUN 배속, 탭 +1줄.
  - order: 4 (세이브 메뉴 기능화)
    action: ↑↓ 슬롯 선택 / Enter 저장 / L 불러오기 / Esc 닫기, 슬롯 메타 표시, skipTitle의
      무조건 메뉴 폐쇄 제거(API 자동 스킵 계약은 유지).
    verified: M21 — 실키보드로 저장·불러오기 왕복. M20 — 제9조 API 자동 해제.
  - order: 5 (fps 실측)
    action: 상수 60 제거, 프레임 타임스탬프 1초 롤링 윈도우 실측.
    verified: M17 — 60Hz 주입 → 60 판독, 30Hz 주입 → 30 판독.
  - order: 6 (공허 오라클 해소)
    action: M11(실대화 텍스트 유지/전진 + 재방문 .re 분기), M13(이동 상태 60/120Hz 비율,
      __gameLoop가 실누산기 경유), M5(파티클 단일 소스 실목록), M3(데드엔드 실계산 + 정확 82노드).
    verified: M13 비율 0.983 (실이동 9.4타일), M18 reduced-motion 파티클 0 실측.
  - order: 7 (RED 로그 실캡처 + 하네스 정직화)
    action: 하네스에 실패 요약 + exit code 제어(RED 실패 시 exit 1), 성공 시에만 계산된 배너.
    verified: ep2_red_observe_build2.log = build1 대상 실제 출력 22건 RED + RED_EXIT=1.
      뮤테이션 9회 전부 exit 1, 허위 배너 출력 0회.
  - order: 8 (콘텐츠 도달성 + 정합성)
    action: 신규 오브젝트 9기(난간/방풍문/에어록/허브랙/CRT/수정 풀/암반층/서가/코어) + 재방문
      node2 메커니즘 + 프롤로그 실플레이 배선(타이틀 해제 1회) + 중복 노드 삭제(83→82) +
      크레딧 자칭 훈장 삭제 + M19 어록 결박 해제(어록 귀속 자체는 형님 재가 대기 사안으로 보존) +
      오브젝트 스프라이트 19종 + 디버그 라벨 제거 + [E] 근접 마커 + 체커 바닥.
    verified: M22 — 전 81 콘텐츠 노드 실플레이 간선 도달. M19 — 자칭 훈장 부재.

acceptance_criteria:
  - { criterion: 부팅 무결(리소스 0, 콘솔 0) + 결정론 금지 원시(setTimeout/Date.now/Math.random) 부재, required: true, result: PASS, verification: Static, M1 }
  - { criterion: 결정론 해시 '926f420b' 고정, required: true, result: PASS, verification: M2 }
  - { criterion: 그래프 정확 82노드, 고아 0, 데드엔드 실계산 0, required: true, result: PASS, verification: M3 }
  - { criterion: Ep1 실키 세이브 연동 (양성+부정), required: true, result: PASS, verification: M4 }
  - { criterion: 바람 파티클 실목록/씬 격리/이동 실측, required: true, result: PASS, verification: M5 }
  - { criterion: 퍼즐 FSM DEADLOCK 정확 + rotate 리셋, required: true, result: PASS, verification: M6 }
  - { criterion: 인게임 퍼즐 개방 + BFS 솔브 + DELIVERED 스토리 게이트, required: true, result: PASS, verification: M7 }
  - { criterion: Era 31/47 오브젝트 + 보이스 전환, required: true, result: PASS, verification: M8, M9 }
  - { criterion: 삐빅스 논쟁 오답 루프 / 정답 시에만 $2.56, required: true, result: PASS, verification: M10 }
  - { criterion: 1입력 1줄 실검증 + 재방문 .re 분기, required: true, result: PASS, verification: M11 }
  - { criterion: 선택지 대기 + 3라벨 렌더, required: true, result: PASS, verification: M12 }
  - { criterion: 주사율 독립(실이동, 비율 ≤1.06), required: true, result: PASS, verification: M13 (0.983) }
  - { criterion: 세이브/로드 전체 해시 왕복, required: true, result: PASS, verification: M14 }
  - { criterion: 실 TouchEvent 모바일 조작, required: true, result: PASS, verification: M15 }
  - { criterion: 봇 실주행 완주(보행+퍼즐+종착 씬), required: true, result: PASS, verification: M16 (span 89) }
  - { criterion: fps 계기판 실측성(주입 주기 추종), required: true, result: PASS, verification: M17 }
  - { criterion: reduced-motion 플래그 + 파티클 0, required: true, result: PASS, verification: M18 }
  - { criterion: 크레딧 5노드 + 필수 문구 + 자칭 훈장 부재, required: true, result: PASS, verification: M19 }
  - { criterion: 제9조 자동화 스킵(타이틀+모달), required: true, result: PASS, verification: M20 }
  - { criterion: 세이브 메뉴 UI 실키 저장/불러오기, required: true, result: PASS, verification: M21 }
  - { criterion: 전 노드 실플레이 도달, required: true, result: PASS, verification: M22 }
  - { criterion: Ep1 회귀 제로, required: true, result: PASS, verification: sha 727a298aad1ed210 불변 + 동일 세션 새 셸 test_episode1.py 23/23 · cceb91bc · span 2602 }

validation:
  automated:
    - { command: "RED_OBSERVE=1 python -B test_episode2.py (vs build1)", result: "22 RED + exit 1", artifact: review/logs/ep2_red_observe_build2.log }
    - { command: "python -B test_episode2.py (새 셸)", result: "PASS 23/23, exit 0", artifact: review/logs/ep2_strict_green_build2.log }
    - { command: "strict_mut_ep2.py (스크래치 사본, RED_OBSERVE 전체 실패 집합)", result: "9/9 검출: 8건 단독 명중, MUT-B2-3은 {M7, M16} 이중 명중(봇이 솔버로 퍼즐을 실제 풀도록 강화된 설계 결합 — 설명 불가 명중 0건), 전 회 복원 sha 일치", artifact: review/logs/ep2_mutation_build2.log }
  manual:
    - { procedure: "채증 7장 전량 육안", result: PASS, observed: "모바일 HUD(D-pad/RUN/[E]) · 씬별 고유 스프라이트/디버그 라벨 부재 · 퍼즐 DELIVERED 상태 · SLOT 2 실키 저장 완료 메시지", artifact: "review/shots/ep2b2_*.png (7)" }
    - { procedure: "MDN touch-action / Touch events 공식 문서 교차검증", result: PASS, observed: "preventDefault 단독 불충분 — touch-action 병행 권고 확인 후 반영" }
  ci: { result: NOT_RUN, summary: 로컬 단독 환경 }

risks:
  - { description: "AudioContext 자동재생 정책 — 첫 입력 전 suspend", severity: low, handling: safeguard, reason: "keydown/click/touchstart에서 init+resume 결속" }
  - { description: "MUT-B2-3 이중 명중이 보여주듯 M16은 퍼즐 서브시스템과 결합되어 있음(의도된 강화)", severity: low, handling: documented }
  - { description: "실기기(비에뮬레이션) 터치 실측은 미실행 — 형님 수동 완주 시 확인 권장", severity: low, handling: disclosed }

status: success
review_verdict: PENDING

addendum_build3:
  date: 2026-08-28
  trigger: 감각 게이트(형님 수동 플레이) 판정 — "기능 무죄, 게임필 유죄"
  target_update: episode2.html sha256_16 `6b786661b8b2dd14` (71,469B), test_episode2.py M15 타자기 계약 반영
  scope: 렌더/오디오 계층 한정 (걷기 애니메이션·추적 동료·타자기 대사·선율 BGM·세트 드레싱·페이드/토스트)
  verification: 새 GREEN 23/23 exit 0 (봇 span 89 동일 = 시뮬레이션 무풍 증명), 뮤테이션 앵커 9종 원문 보존 확인 + 재실행 로그 갱신
  review_verdict: PENDING (유지)

addendum_ci:
  date: 2026-08-28
  trigger: CI(GitHub Actions) 도입 후 최초 실행에서 test_episode2.py 이식성 결함 검출
  defect: |
    test_episode2.py 17~18행이 `BASE = Path(r"E:\03_AllWork\01_Luna\to-the-singularity")` 절대경로에
    의존. 윈도우 로컬에서는 GREEN이었으나 ubuntu-latest 러너에서 경로 부재로 상대경로가 되어
    `HTML_PATH.as_uri()`가 ValueError로 즉사 (run 33106515192, step 7). Ep1은 동일 위치에서
    `Path(__file__).with_name(...).resolve()`를 사용하고 있어 CI에서 정상 통과.
  instrument_failure: |
    도입 전 자가 스캔에서 `grep -nE "E:\\|Path\(r"`가 거짓 음성(exit 1)을 반환하여 결함을
    놓쳤음. `grep -nF 'Path(r'`로는 즉시 검출됨. 검증 도구 자체의 오탐/미탐 가능성을
    기록으로 남긴다 — 계기판 위조 판례와 동일 계열(측정하되, 측정기를 믿지 말 것).
  fix: 17~18행을 Ep1과 동일한 `Path(__file__).with_name("episode2.html").resolve()` 관용구로 통일.
  verification: |
    로컬 GREEN 23/23 exit 0, 타 디렉터리(cwd=/tmp) 실행에서도 GREEN 23/23 (이식성 실증),
    CI(ubuntu-latest, Python 3.12, playwright 1.62.0) GREEN.
  checksums_sha256_16:
    test_episode2.py: abaa8898fd75956b (구 f4778c9a55ef3c6e)
    .github/workflows/ci.yml: 2a134e41d82f341a
  note: 게임 본편(episode2.html) 무수정 — 결함은 오라클 측에만 존재했다.
  review_verdict: PENDING (유지)
