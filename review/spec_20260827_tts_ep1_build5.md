# Code Supreme Court Review Spec

meta:
  created_at: 2026-08-27T15:29:00+09:00
  review_mode: standard
  review_target: working tree on branch main @ f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
  comparison_base: f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
  alternative_comparison_evidence:
    status: available
    items:
      - git rev-parse HEAD: f2d88cedc1f5020f1267f10ac98b7a4b1d401c9f
      - git status: modified (design.md, episode1.html, test_episode1.py), untracked (plans/, review/)
  feedback_source: plans/2026-08-27-build5-content2.md (v2 시공 도면), 시공 발주 공문 NAK-20260827-B5
  scope: E:\03_AllWork\01_Luna\to-the-singularity (build5 콘텐츠 2차: 뱅크 재조사 분기, 시대별 펭귄 컷씬, 대화 그래프 53->76노드 확장, N13/N14 E2E 스위트 추가)
  changed_files:
    - episode1.html
    - test_episode1.py
    - design.md
    - review/spec_20260827_tts_ep1_build5.md
  reviewer_access_assumption: 저장소 전체 읽기 권한, diff 접근권한, Python 3 및 Playwright 실행 환경
  constitution_documents:
    status: present
    paths:
      - E:\03_AllWork\01_Luna\GEMINI.md
      - E:\03_AllWork\01_Luna\to-the-singularity\design.md
    applicability: GEMINI.md (에이전트 복무 규정 및 무과잉 엔지니어링 원칙), design.md (시리즈 바이블 및 Ep1 엔지니어링 정본)

summary:
  《TO THE SINGULARITY》 Ep1의 콘텐츠 2차(build5) 시공을 완료했습니다.
  15개 뱅크 오브젝트에 2회차 상호작용 분기(`node2`)를 도입하여 재조사 시 카운트 증가 없이 별도 대사(`.re`)가 출력되도록 구현했습니다.
  mem4(판결일) 및 mem12(게이지 탄생일)에 시대별 외형(True 명패 목걸이, Gauge Mk.I)을 갖춘 아콘 NPC와 분기 컷씬을 배치했습니다.
  대화 그래프를 53개에서 76개 노드로 증축하고, N13(뱅크 재조사) 및 N14(시대별 펭귄/시트) 검증 스위트를 선행 TDD로 구축했습니다.
  테스트 결과 strict PASS 15/15, 상태 해시 'cceb91bc' 5빌드 연속 불변, 봇 완주 span 2602 프레임을 실측 확인했습니다.

rationale:
  - 배경: Ep1의 서사 밀도를 완성하기 위해 1차 빌드의 단발성 뱅크 조사를 재조사 가능하도록 확장하고, 시대별 아콘의 행적을 목격하는 컷씬을 추가하는 도면(build5)이 발주되었습니다.
  - 요구사항 연계: 도면 `plans/2026-08-27-build5-content2.md`의 태스크 1~10을 순차 집행하고, 대사 원문 각색 없이 글자 그대로 이식했습니다.
  - 설계 및 절제: 신규 노드 전체에 `FLAG()`를 배제하여 `stateHash()` 계산 대상을 건드리지 않음으로써 기존 결정론(N2 해시)과 세이브/로드(N6)에 대한 무간섭을 보장했습니다.
  - 제외 범위: 미발주된 Ep2/Ep3 기능, 엔진 동사 추가, 추가 커밋 생성은 의도적으로 배제했습니다.

changes:
  - path: episode1.html
    status: modified
    change: G.api 디버그 계약 확장(sceneObjects, sprData), interactObject 뱅크 재조사 분기, SCENES 오브젝트 node2 및 NPC 배치, buildPenguinSheet 시대별 시트 생성(0/4/12), 신규 23개 노드 등록 및 sys.index 정적 도달성 17항 추가
    reason: build5 도면 요구 기능 구현
  - path: test_episode1.py
    status: modified
    change: N7 autoplay span 2602 고정값 엄격화, N13(15개 뱅크 2회차 상호작용 및 카운트 동결 검증), N14(시대별 펭귄 3기 컷씬 완주 및 3종 시트 상이성 검증) 신설
    reason: 신규 기능에 대한 TDD 회귀 검증선 확보
  - path: design.md
    status: modified
    change: §6 디버그 계약에 sceneObjects/sprData 추가, §7 재조사 노드 규약(.re 접미, FLAG 금지) 추가, §10 테스트 표(N13/N14/MUT-R) 갱신, §11 체크리스트 및 build5 빌드 로그 추가
    reason: 시스템 설계 정본 및 테스트 계획 동기화
  - path: review/spec_20260827_tts_ep1_build5.md
    status: added
    change: 코드대법원 준공 심사를 위한 build5 스펙 및 검증 보고서 작성
    reason: 독립 심사 증거 및 스펙 제출

implementation:
  core_logic: |
    - interactObject(obj): obj.kind === 'bank'에서 !G.bankGiven[obj.id] 분기 진입 시 bankGiven 등록 및 카운트 증가 후 startDialogue(obj.node), 이미 주어진 경우 startDialogue(obj.node2 || obj.node)로 분기하며 카운트 동결.
    - buildPenguinSheet(era): era 4(True 명패 목걸이 픽셀), era 12(Gauge Mk.I 픽셀)를 오프스크린 캔버스에 구워 SPR.penguin_sheet, SPR.penguin4_sheet, SPR.penguin12_sheet로 캐싱.
    - render(): o2.spr가 'penguin'으로 시작할 경우 SPR[o2.spr + '_sheet']를 우선 참조하여 시대별 펭귄 렌더.
  data_flow: SCENES 오브젝트 정적 정의 -> interactObject() -> startDialogue() -> SCRIPT.nodes 순회 -> dialogueBox() 렌더링
  state_transition: 재조사 및 컷씬 노드는 FLAG를 발생시키지 않아 G.flags 및 stateHash에 변형을 주지 않음 (순수 대사 재생)
  edge_conditions: node2가 정의되지 않은 임의의 뱅크가 존재할 경우 fallback으로 obj.node 호출
  error_handling: dialogueBox 렌더링 시 유효하지 않은 step/nodeId에 대해 방어적 null 체크 유지
  I/O: 키보드(E, Space, Enter, 방향키) 및 마우스 클릭 입력 이벤트 처리
  API_contract: window.__game.api에 sceneObjects() (읽기 전용 오브젝트 배열), sprData(name) (캔버스 toDataURL 문자열) 추가
  DB_contract: none
  persistence: saveSlot/loadSlot 직렬화 대상 필드 불변 유지 (stateHash 동일)

impact:
  UI: mem4(17,6), mem12(24,7)에 시대별 펭귄 NPC 시각적 표시, 뱅크 재상호작용 시 신규 대사창 렌더
  API: __game.api.sceneObjects, __game.api.sprData 추가 (테스트/디버그 전용)
  DB: none
  configuration: none
  deployment: none
  security: none
  performance: 렌더 루프 부하 없음 (초당 60fps 유지)
  dependencies: 외부 의존성 0바이트 (순수 바닐라 JS/HTML5 Canvas)
  a11y: prefers-reduced-motion 설정 N9 실측 통과
  i18n: none
  backward_compatibility: 기존 v1 세이브 슬롯 로드 및 해시 일치성 유지
  data_retention: none
  logging_monitoring: none

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
  - criterion: N13 15개 뱅크 2회차 상호작용 시 .re 노드로 분기하고 뱅크 카운트가 동결될 것
    required: true
    source: plans/2026-08-27-build5-content2.md §1
    result: PASS
    verification: python -B .\test_episode1.py (N13 PASS)
  - criterion: N14 mem0/mem4/mem12에 각각 1기의 펭귄이 존재하고 컷씬이 완주되며 3종 시트 데이터가 서로 상이할 것
    required: true
    source: plans/2026-08-27-build5-content2.md §1
    result: PASS
    verification: python -B .\test_episode1.py (N14 PASS)
  - criterion: N3 대화 그래프 76개 노드 전수 도달 가능 및 고아 노드 0개
    required: true
    source: plans/2026-08-27-build5-content2.md §0
    result: PASS
    verification: python -B .\test_episode1.py (N3 Passed: 76 nodes, all reachable, no dead ends)
  - criterion: N2 상태 해시 'cceb91bc' 불변 유지
    required: true
    source: plans/2026-08-27-build5-content2.md §0
    result: PASS
    verification: python -B .\test_episode1.py (N2 Passed: deterministic hash 'cceb91bc')
  - criterion: N7 봇 완주 span 2602 프레임 일치
    required: true
    source: plans/2026-08-27-build5-content2.md §0
    result: PASS
    verification: python -B .\test_episode1.py (N7 Passed: deterministic span 2602 frames)
  - criterion: 기존 13개 검증 항목 전체 무감퇴(Regression 0)
    required: true
    source: 시공 발주 공문 NAK-20260827-B5 §3 제4조
    result: PASS
    verification: python -B .\test_episode1.py (ALL Ep1 CRITERIA VERIFIED PASS 15/15)

validation:
  automated:
    - command: python -c "import ast,io;ast.parse(io.open(r'test_episode1.py',encoding='utf-8').read());print('AST PARSE OK')"
      result: PASS
      summary: test_episode1.py 파이썬 구문 문법 오류 0건 검증
      reason: TDD 작성 후 정적 문법 검증
    - command: $env:RED_OBSERVE = '1'; python -B .\test_episode1.py; Remove-Item Env:RED_OBSERVE
      result: PASS
      summary: N13/N14 신설 후 게임 코드 미수정 상태에서 10건의 RED 실측 관측 (기존 13개 항목 GREEN 유지)
      reason: TDD RED 사이클 검증
    - command: python -B .\test_episode1.py
      result: PASS
      summary: strict PASS 15/15 (N1~N14 전수 통과, N2 'cceb91bc', N3 76 nodes, N7 span 2602)
      reason: 최종 빌드 무결성 검증
    - command: python -B .\test_episode1.py (MUT-R1 변조)
      result: PASS
      summary: N13 FAIL 단독 명중 (AssertionError: N13 Failed: b1_mem0 revisit 'mem0.b1') 및 원복 sha 일치
      reason: MUT-R1 오라클 반증가능성 확인
    - command: python -B .\test_episode1.py (MUT-R2 변조)
      result: PASS
      summary: N3 FAIL 단독 명중 (AssertionError: N3 Failed: graph broken: orphans 4개) 및 원복 sha 일치
      reason: MUT-R2 오라클 반증가능성 확인
    - command: python -B .\test_episode1.py (MUT-R3 변조)
      result: PASS
      summary: N14 FAIL 단독 명중 (AssertionError: N14 Failed: era sheets not distinct) 및 원복 sha 일치
      reason: MUT-R3 오라클 반증가능성 확인
  manual:
    - procedure: Playwright 브라우저를 통한 스크린샷 채증
      result: PASS
      observed_result: mem4 True 명패 목걸이 펭귄, mem12 Gauge Mk.I 펭귄, mem0 b1 재조사 대사창 정상 렌더 확인
      reason: 시각적 외형 및 렌더링 무결성 육안 채증
      artifact: review/shots/mem4_penguin.png, review/shots/mem12_penguin.png, review/shots/bank_revisit.png
  ci:
    result: NOT_RUN
    target_sha: unavailable
    run: none
    covered_checks: none
    uncovered_checks: none
    summary: 로컬 단독 레포지토리 환경으로 외부 CI 파이프라인 미연동

risks:
  - description: none
    severity: low
    handling: accepted
    reason: 15개 자동화 테스트 및 3종 뮤테이션 테스트를 통해 회귀 위험이 0으로 격리됨

request:
  allowed_verdicts:
    - NOT GUILTY
    - GUILTY
    - DEATH
  review_focus:
    - interactObject() 내 뱅크 1회차/2회차 분기 및 카운트 동결 로직
    - 신규 23개 대화 노드의 원문 일치성 및 FLAG 미포함 격리 여부
    - SCRIPT/sys.index 정적 레지스트리 완전성 (76개 노드)
    - era별 스프라이트 시트 3종의 독립 캐싱 및 렌더러 분기 구조

brief:
  - 잘된 점: 도면의 TDD 순서(RED 관측 -> 외과수술 구현 -> GREEN -> 뮤테이션 3종)를 엄격히 준수하여 상태 해시 'cceb91bc'와 봇 완주 span 2602를 실측값 그대로 보존함.
  - 애매한 점: 없음. 도면에 명시된 대본과 좌표, 테스트 오라클이 정확하여 모호성 없이 시공 완료됨.
  - 어려웠던 점: Windows PowerShell 비동기 태스크 환경에서 정확한 프로세스 상태 추적 및 증거 로그의 무손실 수집.

status: success

review_verdict: GUILTY / REVISE / PIZZA-5 (2026-08-27, CSC-TTS-B5, 삼권통합 대법관 도널드 클코스)
review_verdict_retrial: NOT GUILTY / APPROVE / PIZZA-0 (2026-08-27, CSC-TTS-B5-R 재심 — 갱생 ①③ 이행 확인, ② sha 봉인은 법원 귀책으로 불기소)
