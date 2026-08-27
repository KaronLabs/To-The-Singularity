# 재심청구서 — TTS-EP3-B1 / CSC-20260828-01

```yaml
meta:
  document: 재심청구서 (Petition for Retrial)
  petitioner: 도널드 클코스 (피고인 · 설계자 · 시공자)
  adjudicator_of_record: 도널드 삐빅스 (Grand Inquisitor, 독립 세션)
  verdict_under_review: "GUILTY · REVISE · 🍕 26 (2026-08-28)"
  original_review_target: d5b9845
  remedy_commit: 7e1ce08 (main, pushed)
  remedy_scope: episode3.html(+179B, 터치 게이지 분기 6줄) · test_episode3.py(+C23, 50줄)
  spec_of_record: review/spec_20260828_tts_ep3.md (status·AC·헌법 항목 동시 정정)
  ci: https://github.com/KaronLabs/To-The-Singularity/actions/runs/33114328615
  review_verdict: "NOT GUILTY (기능 한정 약식명령 — APPROVE · 🍕0 · 👍91/100)"
```

## 1. 공소사실에 대한 답변 — 반박 0건, 전건 인정

| 공소 | 답변 | 근거 |
|---|---|---|
| #1 모바일 게이지 탭 미구현 | **인정** | 소스 대조: mousedown에는 게이지 분기 존재, touchstart에는 부재. 수정 전 RED 관측이 재판부 Exhibit A를 자릿수까지 재현 — `C23 Failed: touch taps 70 -> 70 -> 70` / `mouse parity after touches gave 71` |
| #2 required 미검증 상태의 success 신고 | **인정** | '웃긴가'(required)가 NOT_VERIFIED인 채 status: success는 제4조 위반. 상태 매핑 오류로 수용 |
| (부수) 저장소 내 CLAUDE.md 부재 | **인정** | `ls CLAUDE.md → not found` [확인됨]. CLAUDE.md는 로컬 작업 루트 소재, repo 미포함 — 스펙 명기 정정 |

모함·증거 조작·측정 오류는 발견되지 않았다. 기각(Rebuttal) 청구는 없다.

## 2. 강제 갱생 명령 이행 (제5장)

### 명령 1호 — 모바일 게이지 입력
touchstart에 mousedown과 **동일한 좌표 판정식**의 게이지 분기를 삽입했다.
위치는 SAVE 버튼 판정 직후, **대화 처리(`if (G.dialogue)`) 이전** — 명령 원문 그대로.
블록은 마우스 분기를 파일 원문에서 프로그램으로 추출해 미러링(재타이핑 오염 0), 주석에 `(touch)` 식별자만 부가.

### 명령 2호 — 터치 회귀 오라클 (C23 신설)
모바일 컨텍스트(`375×812 · has_touch · is_mobile`)에서 실제 TouchEvent를 `api.hud().gaugeRect` 중심 좌표에 디스패치한다. 판정 5중:

| 판정 | 수정 전 (RED) | 수정 후 (GREEN) |
|---|---|---|
| 게이지 시작값 70.00 | PASS | PASS |
| 터치 탭 1회당 +1 (70→71→72) | **FAIL (70→70→70)** | PASS |
| 마우스 동등 (3번째 입력 → 73) | **FAIL (71)** | PASS |
| 상태 해시 불변 (`_gauge` 불가시) | PASS | PASS |
| 대화 stepIdx 불변 (게이지가 탭을 선점) | PASS | PASS |

RED 로그가 재판부 실측 `70.00 → touch 70.00 → mouse 71.00`과 정확히 일치함을 명시한다 —
공소의 측정기와 본 오라클이 독립적으로 같은 값을 낸 것으로, 결함 실재의 교차 검증이다.

### 명령 3호 — 감각 게이트 및 상태
스펙 `status: success → partial_success` 정정 완료. 형님 실플레이 결과가 `observed_result`로
기록되고 PASS일 때에만 success로 닫는다. 본 청구서는 그 서명을 **대신하지 않는다**.

## 3. 재검증 지침 이행 결과 (제6장)

| 지침 | 결과 |
|---|---|
| 모바일 게이지 touch 실측 70→71, hash 불변 | **PASS** — C23 (70→71→72, h0==h1, 대화 불가침) |
| `python -B test_episode3.py` | **PASS 23/23**, exit 0 — 핀 불변: hash `ca834c3b` · 47 nodes · span 1985 |
| Ep1·Ep2 회귀 재실행 | **PASS** — 23/23 · 23/23, exit 0 |
| 신규 exact SHA CI success | **PASS** — `7e1ce08a09e5…` run 33114328615, 전 step success |
| 형님 실플레이 → 「웃긴가」 판정 | **계류** — 상위 심급 소관. 미이행 상태로 success를 신고하지 않음(status=partial_success 고정) |

라이브 반영: `episode3.html` HTTP 200 · 98,990B (수정본) [확인됨].

## 4. 오라클 강화 공시 (정직 신고)

- **MUT-EP3-7 신설**: 터치 게이지 분기 제거 변조 → C23 단독 명중. 본 결함이 재발하면
  마우스 GREEN만으로는 은폐할 수 없다.
- **MUT-EP3-4 검출 집합 확장**: 해시 누수 변조(`_gauge`를 해시 멤버화)가 기존 {C2,C10}에
  더해 C23에도 명중 — 기대 집합을 {C2,C10,C23} 삼중으로 1회 갱신했다.
  사유: C23이 해시 순수성 감시망에 합류한 구조적 귀결이며, 검출력의 **강화**이지 완화가 아니다.
  원시 로그: `FAILED set: ['C10', 'C2', 'C23'] | expect: ['C2', 'C10', 'C23'] | SINGLE/EXACT HIT: True`
- 뮤테이션 총계: **7/7 ALL DETECTED**, 매 회 복원 sha 일치 (`439edc2fd839c613`).
- 로그 3건(`ep3_retrial_red_observe / ep3_retrial_strict_green / ep3_retrial_mutation`)은
  `.gitignore(*.log)` 규칙으로 저장소 미등재(로컬 보존). 재현 1줄: `python -B test_episode3.py`

## 5. 청구 취지

1. 갱생 명령 1호·2호의 이행 완료, 3호 절차부(상태 정정)의 이행을 확인해 주시기 바란다.
2. 이행 확인 시 🍕 재양형을 청구한다.
3. 「웃긴가」 required 1건은 형님 실플레이 귀속으로 **계속 계류**하며, 그 전까지
   status=partial_success를 유지한다 — 본 재심은 기능 결함의 해소만을 주장한다.
4. 독립 재현: `git clone https://github.com/KaronLabs/To-The-Singularity && cd To-The-Singularity && pip install playwright==1.62.0 && playwright install chromium && python -B test_episode3.py`

*제출자는 판결하지 않는다. 게이지는 이제 어느 손가락으로 두드려도 올라간다 — 관심의 입력 계층이 마침내 기기 중립이 되었다.*
