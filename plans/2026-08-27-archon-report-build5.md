준공계: TTS-EP1-B5
시공자: ARCHON
도면: plans/2026-08-27-build5-content2.md (v2)
태스크_이행:
  1_테스트_선행: 완료 (N7 span 2602 고정 검증, N13 뱅크 재조사, N14 시대별 펭귄 검증 스위트 신설, ast.parse 무결성 확인)
  2_RED_관측: 완료 (RED_OBSERVE=1 환경에서 10건 RED 실측 로그 확보, 기존 13항 GREEN 유지)
  3_디버그_계약_확장: 완료 (G.api에 sceneObjects, sprData 읽기 전용 메서드 2종 추가)
  4_뱅크_재조사_메커니즘: 완료 (interactObject bank 분기 2회차 시 node2 분기 및 카운트 동결)
  5_SCENES_배선: 완료 (15개 뱅크 오브젝트 node2 추가, mem4/mem12 시대별 아콘 NPC 2기 배치)
  6_스프라이트_시대변형: 완료 (buildPenguinSheet(era) 0/4/12 시트 3종 독립 빌드 및 draw 렌더러 분기)
  7_대화노드_23개_증축: 완료 (재조사 15노드, 컷씬 8노드 원문 오타/각색 없이 배치, FLAG 0개 보장)
  8_정적_도달성_등록: 완료 (sys.index에 17개 엔트리 등록, 76노드 전수 도달)
  9_GREEN_뮤테이션_채증: 완료 (strict 15/15 PASS, MUT-R1/R2/R3 단독 명중 및 복원 sha 일치, 채증 3장 완료)
  10_문서화: 완료 (design.md build5 갱신, review/spec_20260827_tts_ep1_build5.md 신규 작성)
최종_실측:
  strict: PASS 15/15
  N2: 'cceb91bc'
  N3: 76 nodes
  N7_span: 2602
  N12_ratio: 1.017
sha256_16:
  episode1.html: 3962a191a7239fa7
  test_episode1.py: 7ef1d510410d0ab0
  design.md: 2684e24e0c84968d
  spec: dcfd512b2f0bcaaa
로그_경로:
  - review/spec_20260827_tts_ep1_build5.md
채증_경로:
  - review/shots/mem4_penguin.png
  - review/shots/mem12_penguin.png
  - review/shots/bank_revisit.png
일탈_및_미이행: 없음
재량_행사_내역:
  - NPC 배치: mem4 (17,6), mem12 (24,7) 도면 지정 기준 좌표 그대로 배치하여 간섭 0 유지
  - 시대 액세서리 픽셀: mem4 목걸이 True 명패(3x2 백색+테두리 1px), mem12 가슴 Gauge Mk.I(amber 점+바늘 1px) 픽셀 렌더링
잔여_질의: []
게이지: 표기하지 않음 (제8조 준수)
