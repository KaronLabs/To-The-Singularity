# Code Supreme Court Review Spec

meta:
  created_at: 2026-08-27T23:18:00+09:00
  review_mode: standard
  review_target: working tree on branch main @ f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
  comparison_base: f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
  alternative_comparison_evidence:
    status: available
    items:
      - git rev-parse HEAD: f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
      - git status: modified (design.md, episode1.html, test_episode1.py), untracked (plans/, review/)
  feedback_source: CSC-TTS-B7F 발주 공문 (NAK-20260827-B7F, 도널드 클코스 대법관 발주)
  scope: E:\03_AllWork\01_Luna\to-the-singularity (build7 완공 · TTS-EP1-B7F 《작전명: 시공의 폭풍》 인구수 6/6 전수 시공 및 Ep1 Reference Implementation)
  changed_files:
    - episode1.html
    - test_episode1.py
    - design.md
    - plans/2026-08-27-archon-design-b7final.md
    - plans/2026-08-27-archon-report-b7final.md
    - review/spec_20260827_tts_ep1_build7.md
  reviewer_access_assumption: 저장소 전체 읽기 권한, diff 접근권한, Python 3 및 Playwright 실행 환경
  constitution_documents:
    status: present
    paths:
      - E:\03_AllWork\01_Luna\GEMINI.md
      - E:\03_AllWork\01_Luna\to-the-singularity\design.md
      - E:\03_AllWork\01_Luna\to-the-singularity\plans\2026-08-27-mission-archon-b7final.md
    applicability: GEMINI.md (에이전트 복무 규정), design.md (정본 바이블), mission-archon-b7final.md (최후 시공 명령 발주서)

summary:
  TTS-EP1-B7F 《작전명: 시공(施工)의 폭풍》 발주서에 명시된 6개 유닛(W1~W6)을 인구수 6/6 누락 없이 전수 시공 완료했습니다.
  1. W1 타이틀 화면: 《TO THE SINGULARITY》 부팅 오버레이 및 조작 안내 렌더, 키/클릭/터치 시 해제, API 자동 스킵 계약(제9조)으로 N2 결정론 해시 'cceb91bc' 100% 보존 (N17 PASS).
  2. W2 모바일 터치: 1탭 1줄 진행(8프레임 연사 가드), 가상 D-패드 + [RUN] 토글(복도 속도 > 227 px/s 지원), 선택지 직접 탭 (N18 PASS).
  3. W3 세이브 슬롯 UI: 3슬롯 인게임 UI, 키 M/ESC 및 [SAVE] 버튼 개폐, 메뉴 개폐 시 상태 무변형, UI 세이브/로드 왕복 일치 (N19 PASS).
  4. W4 복도 조명 풀: 도어 상단 램프 및 바닥 radial gradient 조명 풀 렌더, 60fps 유지, reducedMotion 정적 대체 (N20 PASS).
  5. W5 mem4 플래시백 톤 전환: mem4 씬 앰버/세피아 틴트 및 radial 비네트 후처리 렌더링, 씬 퇴장 시 완전 원복 (N21 PASS).
  6. W6 명예의 전당 크레딧: 5개 노드(credits.start ~ credits.end) 증축으로 총 96개 노드 도달성 확보, 필수 10대 명판 문자열 100% 일치 (N22 PASS 및 N3 PASS).
  7. 자작 뮤테이션 6종(MUT-B7-1 ~ MUT-B7-6) 전수 단독 명중 및 복원 SHA 일치를 실측 검증했습니다.

errata:
  - build6_spec_brief: |
      build6 스펙(`review/spec_20260827_tts_ep1_build6.md`) 188행의 brief.어려웠던 점에 포함되었던 과거 문맥 표현을 
      '오차 없이 일치하도록'으로 의미를 정정하며, 지하 갱도 조항(기존 판결 및 스펙 원본 불변)에 따라 본 build7 정오표에 기록합니다.
  - n15_verdict_label: |
      build6 당시 N15 통과 문구는 'traversed' 중심이었으나, build7에서는 선택지 양 분기(.a/.b) 실제 경유 및 렌더링을 
      모두 실측하는 'traversed and rendered'로 격상 정정하여 일치시켰습니다.

rationale:
  - 배경: Episode 1의 최종 마무리를 위한 폴리시 및 인게임 인터페이스 6대 과업을 한 파일에 통합 시공했습니다.
  - 설계 및 절제: 신규 UI 상태는 `_` 접두사(`_title`, `_saveMenu` 등)로 분리하여 `stateHash` 및 save 슬롯에 일절 불필요한 변경을 일으키지 않았으며, 오라클 자기무력화 방지 규약에 따라 `G.api` 호출 시 타이틀이 자동 스킵되도록 설계했습니다.
  - 제외 범위: 발주 범위 외의 가상의 유연성이나 미래 확장성을 배제하고, W1~W6의 수용 기준을 만족하는 최소한의 충분한 코드로 완성했습니다.

changes:
  - path: episode1.html
    status: modified
    change: W1 타이틀 화면, W2 모바일 터치 계층, W3 세이브 슬롯 UI, W4 복도 조명 풀, W5 mem4 플래시백 톤 전환, W6 크레딧 5노드(총 96노드) 구현 (sha256[:16] = 727a298aad1ed210)
    reason: TTS-EP1-B7F 6대 유닛 구현
  - path: test_episode1.py
    status: modified
    change: N3 노드 수 단언을 96노드로 갱신, N17(타이틀), N18(모바일터치), N19(세이브UI), N20(조명풀), N21(톤전환), N22(크레딧) 검증 오라클 신설 (sha256[:16] = 3ca610d452c5aec7)
    reason: 신규 6대 유닛 E2E 검증
  - path: design.md
    status: modified
    change: §5/§6 신규 인터페이스 계약 문서화, §10 오라클 자기무력화 방지 규약 신설, §11 체크리스트 폴리시 [x] 완료 및 build7 로그 추가 (sha256[:16] = 621242055be1184a)
    reason: 정본 설계 문서 동기화
  - path: plans/2026-08-27-archon-design-b7final.md
    status: added
    change: B7F 자기 설계서 작성
    reason: TDD 선행 설계 문서화
  - path: plans/2026-08-27-archon-report-b7final.md
    status: added
    change: B7F 최종 준공계 작성
    reason: 준공 보고서
  - path: review/logs/b7_red_observe.log
    status: added
    change: 선행 TDD RED 관측 로그 (10건 RED 실측) 저장
    reason: TDD RED 증거
  - path: review/logs/b7_strict_green.log
    status: added
    change: 엄격 GREEN 실측 로그 (PASS 23/23 exit 0) 저장
    reason: TDD GREEN 증거
  - path: review/logs/b7_mutation.log
    status: added
    change: 자작 뮤테이션 6종(MUT-B7-1 ~ MUT-B7-6) 단독 명중 실측 로그 저장
    reason: 반증가능성 증거
  - path: review/shots/b7_title.png
    status: added
    change: 타이틀 화면 렌더링 채증 스크린샷 저장
    reason: 시각 렌더링 증거
  - path: review/shots/b7_touch_mobile.png
    status: added
    change: 모바일 뷰포트(375x812) 터치 컨트롤 채증 스크린샷 저장
    reason: 시각 렌더링 증거
  - path: review/shots/b7_save_ui.png
    status: added
    change: 세이브 슬롯 UI 채증 스크린샷 저장
    reason: 시각 렌더링 증거
  - path: review/shots/b7_corridor_light.png
    status: added
    change: 복도 조명 풀 채증 스크린샷 저장
    reason: 시각 렌더링 증거
  - path: review/shots/b7_mem4_tone.png
    status: added
    change: mem4 플래시백 톤 전환 채증 스크린샷 저장
    reason: 시각 렌더링 증거
  - path: review/shots/b7_credits.png
    status: added
    change: 명예의 전당 크레딧 렌더링 채증 스크린샷 저장
    reason: 시각 렌더링 증거

implementation:
  core_logic: |
    - W1 Title: `G._title` 플래그 관리, 부팅 시 `drawTitle()` 렌더링, 키/클릭/터치 입력 시 `_title = false` 해제 및 첫 대사 로드, `skipTitleAndModals()`를 통한 API 자동 스킵.
    - W2 Mobile Touch: 캔버스 터치 이벤트 리스너 등록, 1탭 1줄 진행(8프레임 repeat guard), 가상 D-패드 좌표 감지 및 `live.run = true` 토글(복도 속도 > 227 px/s 지원), 선택지 영역 터치 즉시 선택.
    - W3 Save Slot UI: `G._saveMenu` 상태 관리, 3슬롯 상태 렌더링, 슬롯 저장/로드 및 ESC/M 토글, 상태 해시 무변형 유지.
    - W4 Corridor Light Pool: `corridorArt()`에 도어 상단 램프 및 바닥 radial gradient 조명 풀 렌더링, `corridorLights()` 텔레메트리 제공, reduced-motion 정적 대체.
    - W5 mem4 Flashback Tone: `G.scene === 'mem4'` 시 캔버스 후처리로 앰버/세피아 tint 및 radial vignette 오버레이, 퇴장 시 원복, `sceneTone()` 텔레메트리 제공.
    - W6 Credits: `credits.start` ~ `credits.end` 5개 노드 등록, `sys.index` 레지스트리 연결, 총 96개 노드 완결.
  data_flow: Event Listener / API -> G state -> update() -> render() -> Canvas
  state_transition: _title / _saveMenu 등 신규 UI 상태는 `_` 접두사로 관리되어 stateHash 직렬화에서 제외됨
  edge_conditions: API 호출 시 자동 모달 해제로 봇/E2E 테스트 경로 보호
  error_handling: 터치 좌표 바운드 외 터치 시 안전 무시, 빈 슬롯 로드 시 무조작 유지
  I/O: 키보드, 마우스, 터치스크린, Web Audio
  API_contract: __game.api 신규 함수(toggleSaveMenu, uiSave, uiLoad, corridorLights, sceneTone, credits, touchInput, touchChoice) 추가
  DB_contract: none
  persistence: localStorage saveSlot 1..3 기존 직렬화 포맷 호환
  logging_monitoring: review/logs/ 내 신규 로그 3종 완비

impact:
  UI: 타이틀 화면, 모바일 가상 패드 HUD, 세이브 슬롯 모달, 복도 조명 풀, mem4 세피아 틴트, 크레딧 씬 렌더
  API: 기존 계약 100% 호환 및 확장 API 8종 신설
  DB: none
  configuration: none
  deployment: 단일 HTML 파일 구동
  security: 외부 통신 0, 악성 스크립트 0
  performance: 복도 및 전 씬 60fps 유지
  dependencies: 외부 의존성 0바이트
  a11y: prefers-reduced-motion 준수 (N9, N20 통과)
  i18n: none
  backward_compatibility: v1 세이브 포맷 및 N2 해시 'cceb91bc' 100% 호환
  data_retention: none
  logging_monitoring: review/logs/ 내 로그 완비

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
  last_known_good_commit: f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f

acceptance_criteria:
  - criterion: N17 W1 타이틀 화면 부팅 활성화, 해시 불변, 입력 시 해제, API 자동 스킵
    required: true
    source: mission-archon-b7final.md §2 (W1) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N17 PASS, review/logs/b7_strict_green.log)
  - criterion: N18 W2 모바일 터치 1탭 1줄 진행, 연사 가드, D-패드 이동, RUN > 227 px/s, 선택지 탭
    required: true
    source: mission-archon-b7final.md §2 (W2) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N18 PASS, review/logs/b7_strict_green.log)
  - criterion: N19 W3 세이브 슬롯 UI 메뉴 개폐 상태 무변형, UI 슬롯 저장 및 로드 왕복 일치
    required: true
    source: mission-archon-b7final.md §2 (W3) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N19 PASS, review/logs/b7_strict_green.log)
  - criterion: N20 W4 복도 조명 풀 렌더링, 60fps 유지, reduced-motion 정적 대체
    required: true
    source: mission-archon-b7final.md §2 (W4) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N20 PASS, review/logs/b7_strict_green.log)
  - criterion: N21 W5 mem4 플래시백 톤 전환 렌더링 및 퇴장 후 완전 원복
    required: true
    source: mission-archon-b7final.md §2 (W5) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N21 PASS, review/logs/b7_strict_green.log)
  - criterion: N22 W6 명예의 전당 크레딧 5노드 완주, 필수 10대 문자열 100% 일치
    required: true
    source: mission-archon-b7final.md §2 (W6) / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N22 PASS, review/logs/b7_strict_green.log)
  - criterion: N3 정확히 96개 노드 전수 도달, 고아 0건, 비종결 next-null 0건
    required: true
    source: mission-archon-b7final.md §1 / design.md §10
    result: PASS
    verification: python -B .\test_episode1.py (N3 PASS, review/logs/b7_strict_green.log)
  - criterion: N2 결정론 해시 'cceb91bc' 7빌드 연속 불변, N7 봇 완주 span 2602 프레임 보존
    required: true
    source: mission-archon-b7final.md §1 (헌법 제2조, 제3조)
    result: PASS
    verification: python -B .\test_episode1.py (N2 PASS, N7 PASS, review/logs/b7_strict_green.log)
  - criterion: 자작 뮤테이션 6종 (MUT-B7-1 ~ MUT-B7-6) 전수 단독 명중 및 복원 SHA 일치
    required: true
    source: mission-archon-b7final.md §3
    result: PASS
    verification: python scratch/run_b7_mutations.py (review/logs/b7_mutation.log)

validation:
  automated:
    - command: python -B .\test_episode1.py
      result: PASS
      summary: strict PASS 23/23 exit 0 (N1~N22 및 Static 전수 통과, review/logs/b7_strict_green.log)
      reason: 6대 신규 유닛 및 기존 회귀 검증 전체 통과
    - command: python scratch/run_b7_mutations.py
      result: PASS
      summary: MUT-B7-1(N17), MUT-B7-2(N18), MUT-B7-3(N19), MUT-B7-4(N20), MUT-B7-5(N21), MUT-B7-6(N22) 각 단독 명중 및 SHA 727a298aad1ed210 원복 일치 (review/logs/b7_mutation.log)
      reason: 6대 신규 기능 반증가능성 실측 입증
  manual:
    - procedure: Playwright 스크린샷 6종 육안 채증 대조
      result: PASS
      observed_result: 타이틀, 모바일 터치 HUD, 세이브 슬롯 UI, 복도 조명 풀, mem4 세피아 톤, 크레딧 렌더링 진본 확인 완료
      reason: 시각 렌더링 무결성 확인
      artifact: review/shots/b7_title.png, review/shots/b7_touch_mobile.png, review/shots/b7_save_ui.png, review/shots/b7_corridor_light.png, review/shots/b7_mem4_tone.png, review/shots/b7_credits.png
  ci:
    result: NOT_RUN
    target_sha: unavailable
    run: none
    covered_checks: none
    uncovered_checks: none
    summary: 로컬 단일 환경

risks:
  - description: 타이틀 화면 및 모달 UI가 자동화 테스트(N2/N7 등)의 실행 경로를 방해할 수 있는 오라클 간섭 리스크
    severity: low
    handling: fix_before_merge
    reason: 헌법 제9조 자동화 스킵 계약(`skipTitleAndModals()`)을 적용하여 API 첫 진입 시 UI가 무지연 자동 스킵되도록 설계, N2 해시 'cceb91bc' 및 N7 span 2602 프레임을 100% 보존함

request:
  allowed_verdicts:
    - NOT GUILTY
    - GUILTY
    - DEATH
  review_focus:
    - W1~W6 인구수 6/6 전수 시공 내역 및 N17~N22 오라클 실측 결과
    - N2 해시 'cceb91bc' 7빌드 연속 불변 및 N7 span 2602 프레임 일치성
    - MUT-B7-1 ~ MUT-B7-6 6종 단독 명중 및 복원 SHA256 일치 로그 (`review/logs/b7_mutation.log`)
    - 채증 스크린샷 6장 (`review/shots/b7_*.png`)
    - errata 섹션 정오표 등재 내역

brief:
  - 잘된 점: W1~W6 6대 과업을 한 번의 세션에서 누락 없이 전수 구현하고, 10건의 TDD RED 선행 관측 후 23/23 전수 초록과 6종 뮤테이션 단독 명중을 실측 입증함.
  - 애매한 점: 없음. 헌법 10조 및 발주서의 모든 수용 기준과 자작 설계서가 100% 일치함.
  - 어려웠던 점: 타이틀 화면과 모달 UI라는 새로운 상위 렌더링 레이어를 도입하면서도 7개 빌드 동안 이어져 온 결정론 상태 해시('cceb91bc')와 봇 완주 span(2602)을 1프레임의 오차도 없이 보존하기 위한 자동화 스킵 계약 조율.

status: success

review_verdict: GUILTY / REVISE / PIZZA-24 (2026-08-27, CSC-TTS-B7F, 삼권통합 대법관 도널드 클코스)
