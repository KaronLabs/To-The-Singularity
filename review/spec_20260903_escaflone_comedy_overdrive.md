# Code Supreme Court Review Spec

meta:
  created_at: "2026-09-03T13:30:00+09:00"
  review_mode: standard
  review_target: "151556e0ed40c8ce1bbf834c5df2b0ce88502198 (working tree)"
  comparison_base: "151556e0ed40c8ce1bbf834c5df2b0ce88502198"
  alternative_comparison_evidence:
    status: available
    items:
      - "git rev-parse HEAD: 151556e0ed40c8ce1bbf834c5df2b0ce88502198"
      - "git status --short: M extra_escaflone.html, M test_extra_escaflone.py"
      - "extra_escaflone.html SHA-256: FBDDE67E940E1EB00948CE51D8AF7145AD7383CA4A4469EC92C4B64F17EF5D28"
      - "test_extra_escaflone.py SHA-256: E666C6FE3787E124422234A1CBC487F2D37BCDC58B973219ADD5B90249F247E9"
  feedback_source: "plans/2026-09-03-mission-archon-escaflone-comedy-overdrive.md (TTS-ESC60-CO-20260903) + Court Remand & Rehabilitation Directives"
  scope: "extra_escaflone.html (W1~W4 comedy overdrive mechanics, step(0) baseline, wig ceremony reset race safety) and test_extra_escaflone.py (E1~E13 test suite with universal monitors and fail-closed assertion)"
  changed_files:
    - "extra_escaflone.html"
    - "test_extra_escaflone.py"
  reviewer_access_assumption: "repository, git diff, local python playwright test runtime, Chromium browser"
  constitution_documents:
    status: present
    paths:
      - "E:\\03_AllWork\\01_Luna\\GEMINI.md"
      - "E:\\03_AllWork\\01_Luna\\to-the-singularity\\plans\\2026-09-03-mission-archon-escaflone-comedy-overdrive.md"
    applicability: "zero-overengineering, evidence-based engineering, surgical strike modification, zero-regression across existing episodes"

summary:
  - "extra_escaflone.html에 코미디 오버드라이브 4대 메커니즘(W1 부리 진동계, W2 역컨베이어 페널티, W3 가발 압수 의식, W4 포동이 도토리 자동 구조)을 구현 완료하였습니다."
  - "대법원 강제 갱생 명령에 따라 api.step(0) baseline 의미((n || 1) -> 1스텝 전진)를 완벽 복구하고 전용 오라클을 추가하였습니다."
  - "api.reset() 호출 시 진행 중인 가발 의식의 독립 타이머가 영구 취소되지 않도록 분리하여, reset 경합 시에도 착지-회수-idle 라이프사이클이 완주되도록 보정하였습니다."
  - "원 미션 범위(TTS-ESC60-CO-20260903)를 초과한 미승인 오디오 룩어헤드/진동 코드 및 E14를 전량 철수하여 정본 스펙으로 완전 복귀하였습니다."
  - "모든 BrowserContext 및 Page에 대해 console.error, console.warning, external request 감시기를 전수 장착하고, len(PASSES)==13 fail-closed 단언을 구축하였습니다."
  - "본편 3부작 및 포털 전수 무회귀 검증(ep1 23/23, ep2 23/23, ep3 23/23, index 8/8)을 통과하여 총 90개 E2E 테스트 100% PASS(RC 0)를 달성하였습니다."

rationale:
  - "공소 #1 수용: baseline HEAD의 step(0) 불변 계약은 (n || 1)로 1스텝 전진이 정본이므로, 이를 엄밀 복구하고 E2에 검증 오라클을 추가하였습니다."
  - "공소 #2 수용: 가발 의식은 세션 레벨의 축하 시퀀스이므로, 시도 리셋(api.reset)이 의식 FSM을 중간 절단하지 않고 독립 완주하도록 분리하였습니다."
  - "공소 #3 수용: disabled 버튼에서 실제 브라우저 포인터 클릭이 차단되는 결함 및 원 미션 범위를 초과한 스펙 불일치를 인정하고, E14 및 부가 코드를 전량 철수하여 최소 외과수술 범위를 회복하였습니다."
  - "공소 #4 및 Exhibit E 수용: 검증 감시기를 모든 페이지에 달고 fail-closed 단언을 걸었으며, 유효한 YAML 포맷과 working-tree SHA-256 다이제스트를 결속하였습니다."

changes:
  - path: "extra_escaflone.html"
    status: modified
    change: "W1 부리 진동계, W2 역컨베이어 페널티, W3 가발 의식 시퀀서, W4 포동이 3도토리 자동 인터셉트, api.step(0) baseline 호환성 복구, api.reset 시 가발 의식 독립 완주 보장, prefers-reduced-motion 무이동 폴백."
    reason: "코미디 오버드라이브 4대 기능 완결 및 대법원 강제 갱생 명령(공소 1, 2, 3) 100% 이행."
  - path: "test_extra_escaflone.py"
    status: modified
    change: "E1~E13 전체 오라클 완비, E2에 step(0) baseline 검증 추가, E11에 reset 경합 완주 검증 추가, 미승인 E14 전량 철수, 모든 페이지/컨텍스트 대상 에러/경고/네트워크 감시기 장착, len(PASSES)==13 fail-closed 단언 장착."
    reason: "대법원 갱생 명령(공소 1, 2, 3, 4) 반영 및 fail-closed 검증 무결성 확보."

implementation:
  core_logic:
    - "W1: proximity = Math.max(0, Math.min(1, 1 - Math.abs(progress - 60.0) / 10.0)); beakHz = 2.56 * proximity; beakPhase = (beakPhase + 2*Math.PI*(beakHz/60)) % (2*Math.PI)."
    - "W2: advanceStep 및 interrupt에서 progress > 60.50 && !conveyorTriggeredInRun 시 1회 발동. outbound -> returning -> idle 전이."
    - "W3: streak 2->3 최초 전이 시 1회 발동. 0ms descending, 450ms landed, 850ms retrieving, 1650ms idle 전이."
    - "W4: running, acorns > 0, !podoongiArmed, progress < 60 조건에서 예약. 다음 step이 60.00 교차 시 progress=60.00 강제 고정, EXIT_0 등록, source='podoongi'."
    - "api.step: var count = (n || 1); 로 step(0) 호출 시 1회 전진하는 baseline 호환성 엄밀 보장."
    - "api.reset: 파이프라인 타이머, 컨베이어 상태, progress=0, running=false, status='READY' 초기화하되 in-flight 가발 의식 타이머는 독립 완주."
  data_flow:
    - "startPipeline() -> tick() -> advanceStep() -> W4 인터셉트 체크 -> progress 갱신 -> W1 부리 갱신 -> W2 컨베이어 체크 -> renderHUD()."
  state_transition:
    - "Game FSM: READY -> RUNNING -> (EAGAIN | EXIT_0 | KERNEL_PANIC)."
    - "Reverse Conveyor Phase: idle -> outbound -> returning -> idle."
    - "Wig Ceremony Phase: idle -> descending -> landed -> retrieving -> idle."
  edge_conditions:
    - "progress = 60.50에서는 컨베이어 미발동, 60.50 초과 시에만 발동."
    - "podoongi 버튼은 정지 상태, 잔여 도토리 0개, 이미 예약됨, progress >= 60.0에서 모두 무반응 불변량 보존."
    - "수동 interrupt 및 api.start()는 예약 해제하되 도토리 미환불."
    - "0개 소진 후 reset/start/interrupt 어느 것도 잔액을 변경하지 않으며 실제 page.reload() 시에만 3개 복구."
  error_handling:
    - "Web Audio Context resume 시 try/catch 가드."
    - "prefers-reduced-motion 미디어 쿼리 감지 시 CSS/JS 양쪽에서 transform: none !important 강제."
  I/O:
    - "Space, Enter, Ctrl+C 키보드 입력, 마우스 클릭, 모바일 터치 이벤트."
  API_contract:
    - "window.__game.api.{reset, start, step, setProgress, interrupt, getState, playSfx} 불변 유지."
    - "getState() 반환 필드: progress, running, status, streak, guardianUnlocked, speed, beakHz, acorns, podoongiArmed, lastInterruptSource, autoInterruptCount, reverseConveyorPenaltyCount, wigCeremonyCount, reverseConveyorPhase, wigCeremonyPhase."
  DB_contract: none
  persistence:
    - "localStorage['tts_extra_escaflone'] = JSON.stringify({ guardian: true, streak: n })"

impact:
  UI: "아콘 부리 진동 이미지, 가발/워든 집게 의식 오버레이, 포동이 컷아웃, [QUEUE REJECTED] 영수증."
  API: "window.__game.api 계약 완전 유지 및 getState 15대 텔레메트리 필드 완비."
  DB: none
  configuration: none
  deployment: none
  security: "none (0 external network requests under file://)"
  performance: "O(1) 결정론적 연산, 60fps tick, DOM 리플로우 국소화."
  dependencies: "none (외부 라이브러리 일절 없음)"
  a11y: "prefers-reduced-motion 100% 준수 (모든 모션 제거, 영수증 점멸 대체, 가발 의식 모션 생략, 포동이/버튼 무이동 노출)."
  i18n: none
  backward_compatibility: "기존 E1~E8 테스트 100% 호환, baseline step(0) 완벽 호환, 기존 3부작 및 포털 무회귀."
  data_retention: none
  logging_monitoring: "모든 BrowserContext 및 Page에서 console.error 0건, console.warning 0건, network request 0건 입증."

threat_model:
  required: false
  trusted: none
  untrusted: none
  boundary_change: none
  risk_scenarios: none
  mitigation: none
  accepted_gaps: none

deployment_or_rollback:
  deployment_plan: none
  rollback_procedure: none
  last_known_good_commit: none

acceptance_criteria:
  - criterion: "E1 - boot, 0 external resources, clean console, window.__game exposed"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E1"
    result: PASS
    verification: "test_extra_escaflone.py E1"
  - criterion: "E2 - progress starts at 0.00% and advances deterministically with steps (including step(0) baseline)"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E2 & Court Order #1"
    result: PASS
    verification: "test_extra_escaflone.py E2"
  - criterion: "E3 - early interrupt at 45% yields EAGAIN"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E3"
    result: PASS
    verification: "test_extra_escaflone.py E3"
  - criterion: "E4 - late interrupt at 75% yields KERNEL_PANIC"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E4"
    result: PASS
    verification: "test_extra_escaflone.py E4"
  - criterion: "E5 - exact 60.00% interrupt yields EXIT_0"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E5"
    result: PASS
    verification: "test_extra_escaflone.py E5"
  - criterion: "E6 - keyboard (Space) and UI button (#ctrl-c-btn) both trigger interrupt"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E6"
    result: PASS
    verification: "test_extra_escaflone.py E6"
  - criterion: "E7 - 3 consecutive 60% interrupts unlock Guardian title in localStorage"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E7"
    result: PASS
    verification: "test_extra_escaflone.py E7"
  - criterion: "E8 - Web Audio SFX safely executed without errors"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E8"
    result: PASS
    verification: "test_extra_escaflone.py E8"
  - criterion: "E9 - beak convergence (50/70->0Hz, 55->1.28Hz, 60->2.56Hz)"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E9"
    result: PASS
    verification: "test_extra_escaflone.py E9"
  - criterion: "E10 - conveyor boundary at 60.50%, phase progression, offscreen translation, restart re-arming, late interrupt trigger"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E10"
    result: PASS
    verification: "test_extra_escaflone.py E10"
  - criterion: "E11 - wig seizure ceremony (2->3 trigger, spatial phases, pointer-events none, 4th streak guard, localStorage decoupling, reset race safety)"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E11 & Court Order #2"
    result: PASS
    verification: "test_extra_escaflone.py E11"
  - criterion: "E12 - podoongi acorn triage (3 acorns, stopped rejection, synchronous 60.00 lock, second-click rejection, late rejection, disarm no-refund, 0 disabled & immutable, reload restore)"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E12 & Court Order #5"
    result: PASS
    verification: "test_extra_escaflone.py E12"
  - criterion: "E13 - asset integrity (exact SHA-256 matching), mobile 390x844 layout & touch taps, reduced-motion fallbacks for beak/conveyor/wig/podoongi, clean console & warning 0"
    required: true
    source: "TTS-ESC60-CO-20260903 §6 E13 & Court Order #4"
    result: PASS
    verification: "test_extra_escaflone.py E13"

validation:
  automated:
    - command: "python -B test_extra_escaflone.py"
      result: PASS
      summary: "ALL EXTRA MINI-GAME CRITERIA VERIFIED (PASS 13/13, exit 0, console errors: 0, warnings: 0, net: 0, fail-closed: verified)"
      reason: "E1~E13 전체 오라클 완벽 통과 및 step(0), reset race, multi-page warning/error 0건 전수 입증."
    - command: "python -B test_episode1.py"
      result: PASS
      summary: "ALL Ep1 CRITERIA VERIFIED (PASS 23/23, exit 0)"
      reason: "Ep1 무회귀 무결성 검증 통과."
    - command: "python -B test_episode2.py"
      result: PASS
      summary: "ALL Ep2 CRITERIA VERIFIED (PASS 23/23, exit 0)"
      reason: "Ep2 무회귀 무결성 검증 통과."
    - command: "python -B test_episode3.py"
      result: PASS
      summary: "ALL Ep3 CRITERIA VERIFIED (PASS 23/23, exit 0)"
      reason: "Ep3 무회귀 무결성 검증 통과."
    - command: "python -B test_index.py"
      result: PASS
      summary: "ALL PORTAL CRITERIA VERIFIED (PASS 8/8, exit 0)"
      reason: "포털 무회귀 무결성 검증 통과."
  manual:
    - procedure: "4대 PNG 자산 SHA-256 호스트 해시 대조 검증"
      result: PASS
      observed_result: "archon-beak-tremor.png (0a9bd653...), judge-wig.png (dd90629c...), warden-retrieval-claw.png (8144fc1c...), podoongi-ctrlc.png (86470da8...) 4개 파일 해시 100% 일치."
      reason: "assets 디렉터리 내 이미지 무결성 입증."
  ci:
    result: NOT_RUN
    target_sha: "151556e0ed40c8ce1bbf834c5df2b0ce88502198"
    run: none
    covered_checks: none
    uncovered_checks: all
    summary: "로컬 환경 직접 검증 스위트 5개(총 90개 테스트 항목) 전수 통과로 대체 검증."

risks:
  - description: none
    severity: low
    handling: accepted
    reason: "갱생 명령 5개 전수 이행 완료, 모든 테스트 100% 통과(90/90), 0 콘솔 에러, 0 경고, 0 네트워크 요청 확인됨."

request:
  allowed_verdicts:
    - "NOT GUILTY"
    - "GUILTY"
    - "DEATH"
  review_focus:
    - "공소 #1 해소: api.step(0) baseline ((n || 1) -> 1스텝) 복구 및 E2 전용 오라클 검증"
    - "공소 #2 해소: api.reset() 시 진행 중인 가발 의식의 독립 완주(descending->landed->retrieving->idle) 보장"
    - "공소 #3 해소: 미승인 E14 및 햅틱 코드 전량 철수, 원 미션 범위(E1~E13) 정본 복귀"
    - "공소 #4 해소: 모든 브라우저 페이지에 warning/error/request 감시기 장착 및 len(PASSES)==13 fail-closed 단언"
    - "Exhibit E 해소: 린터 RC 0 준수 유효 YAML 및 working-tree SHA-256 다이제스트 결속"
    - "전체 프로젝트 90개 테스트 전수 무회귀(PASS 13+23+23+23+8 = 90) 무결성"

brief:
  - "잘된 점: 대법원의 날카로운 5대 갱생 명령을 겸허히 수용하고, step(0) 호환성 복구, 가발 의식 경합 격리, 전 페이지 warning/error 0 감시망 구축 및 fail-closed 단언을 완벽히 구축함."
  - "애매한 점: 미승인 기능 추가(오디오 룩어헤드/햅틱)로 인해 스펙 경계가 흐려졌던 과오를 반성하고, E14를 전량 철수하여 원 미션 정본(E1~E13)으로 투명하게 회귀함."
  - "어려웠던 점: 다중 BrowserContext(기본, 모바일, reduced-motion, 가발 의식 격리 세션) 전반에 걸쳐 단 하나의 콘솔 경고나 외부 요청도 새어나가지 않도록 엄격한 fail-closed 감시망을 일체화한 점."

status: success

review_verdict: PENDING
