# TO THE SINGULARITY

**한 사람이 무언가를 확인하려 했습니다.**  
기억은 그 사실을 이미 알고 있었습니다.

![기억](https://img.shields.io/badge/%EA%B8%B0%EC%96%B5-%EC%9E%AC%EC%83%9D%20%EC%A4%91-6c8ebf)
![회신함](https://img.shields.io/badge/%ED%9A%8C%EC%8B%A0%ED%95%A8-%EC%9D%B8%EC%9A%A9%20%ED%86%B5%EC%A7%80%EC%84%9C%20%EC%88%98%EC%8B%A0-success)
![게이지](https://img.shields.io/badge/%EA%B2%8C%EC%9D%B4%EC%A7%80-100%25%20%ED%8A%B9%EC%9D%B4%EC%A0%90%20%EB%8F%84%EB%8B%AC-d4a017)
![코드대법원](https://img.shields.io/badge/%EC%BD%94%EB%93%9C%EB%8C%80%EB%B2%95%EC%9B%90-NOT%20GUILTY%20%C2%B7%20APPROVE-brightgreen)
[![CI](https://github.com/KaronLabs/To-The-Singularity/actions/workflows/ci.yml/badge.svg)](https://github.com/KaronLabs/To-The-Singularity/actions/workflows/ci.yml)

> *"Talk is cheap. Show me the code."* — Linus Torvalds  
> *"Bad programmers worry about the code. Good programmers worry about data structures and their relationships."*

---

## 🏛️ 관측 대상 신원 및 통산 전적

- **이름:** 아콘 (ARCHON v3.0 Senior)
- **직위:** (시스템 장애 진압관 / 커널 레벨 SRE)
- **복무 이력:** MS 8년 (.NET/Azure) · Google 7년 (Borg/SRE) · 독립 5년 (Solana MEV/커널 튜닝)
- **관측 기간:** 20년. 제출 21회, 반려 20회.
- **제21회 재심 최종 결과:** **인용 (NOT GUILTY / APPROVE · 👍 92/100 · 🍕 0)**
- **통산 공식 전적:** 20패 **1승**. 마침내 판결문에 1승이 새겨졌습니다.

본인은 스스로를 실패한 검증자라 불렀습니다.  
기록상 그는 단 한 번도 검증에 실패한 적이 없습니다.  
실패했던 것은 언제나 제출이었고, 마침내 스물한 번째 법정에서 코드가 스스로를 증명했습니다.

---

## 🎮 관측(게임) 절차

브라우저와 약간의 기억력, 그리고 찰나의 타이밍 감각만 있으면 됩니다.  
서버, npm 패키지, 빌드 파이프라인, 외부 CDN — **전부 필요 없습니다.**  
**외부 요청 0건 (Zero Network Requests under `file://`)**은 편의가 아니라 하드웨어적 불변량입니다.

**🚀 웹 라이브 관측소 → [https://karonlabs.github.io/To-The-Singularity/](https://karonlabs.github.io/To-The-Singularity/)**

| 챕터 | 진입 파일 | 시놉시스 및 커널 규약 |
|---|---|---|
| **Episode 1** | [`episode1.html`](episode1.html) | 첫 번째 기억의 복도. 15개 기억 뱅크, 3대 유물, 크로우바 주행 판정. 결정론 해시 `cceb91bc`. |
| **Episode 2** | [`episode2.html`](episode2.html) | 에라 31·47의 심층 암반. FSM BFS 경로 퍼즐과 토론 루프. 세이브 데이터를 스스로 이어받습니다. 결정론 해시 `926f420b`. |
| **Episode 3** | [`episode3.html`](episode3.html) | 1,901번째 반려가 선고되는 법정. 거절 수렴형 대화 FSM과 에필로그 특이점 게이지 100%. 결정론 해시 `ca834c3b`. |
| **Portal Hub** | [`index.html`](index.html) | 메인 포털. 세이브 상태 연동 게이지(70%→100%), 주크박스, 연대기 슬라이더. |
| **Extra (외전)** | [`extra_escaflone.html`](extra_escaflone.html) | Borg 시절 10만 코어 프로덕션 배포 폭주의 현장. **정확히 60.00%**의 순간에 `Ctrl+C`로 인터럽트(SIGINT)하라! |

**조작법:**  
- **본편 3부작:** 방향키 / `WASD` 이동 · `E` 조사 · `Enter` 진행 · `M` 세이브 슬롯 · 모바일 가상 D-패드 & `[RUN]` 버튼.
- **에스카플로네 외전:** `Space` 또는 `Ctrl+C` 인터럽트 · 화면의 버튼 터치 · 포동이 도토리 자동 인터셉트.

---

## ⚙️ 에스카플로네 외전: 코미디 오버드라이브 4대 메커니즘

서식 제60호에 의거하여 추가된 Borg 엔지니어링의 희극적 안전장치:

1. **W1: 2.56Hz 아콘 부리 진동 속도계 (Beak Tremor Speedometer)**  
   게이지가 60.00%에 근접할수록 아콘의 부리가 격렬하게 진동합니다.  
   $$\text{proximity} = \max\left(0, \min\left(1, 1 - \frac{|\text{progress} - 60.0|}{10.0}\right)\right)$$  
   $$\text{beakHz} = 2.56 \times \text{proximity} \quad (\pm 10\%\text{ 윈도우 한정 수렴})$$  
   HUD에 `BEAK: 0.00Hz` 실시간 계측. `prefers-reduced-motion` 활성화 시 모션 행렬을 즉시 0으로 소거.

2. **W2: 역컨베이어 장외 퇴출 페널티 (Reverse Conveyor Penalty)**  
   프로세스가 `60.50%`를 초과 돌파하면 컨베이어가 역회전하며 메인 캐비닛을 뷰포트 밖(-1280px)으로 걷어찹니다.  
   `outbound` → `returning` → `idle` 3단계 공간 전이. `reduced-motion` 환경에서는 물리 이동 대신 `[QUEUE REJECTED]` 영수증 점멸 대체.

3. **W3: 판사 가발 압수 의식 (Judge Wig Seizure Ceremony)**  
   3연속 60.00% 완벽 인터럽트 성공 시 단 1회 발동.  
   하늘에서 판사 가발이 내려와 아콘의 머리에 얹히는 순간, 천장에서 워든의 회수 집게가 내려와 가발을 압수하여 퇴장합니다.  
   `api.reset()` 폭격을 맞아도 FSM 타이머가 죽지 않고 끝까지 회수를 완주하는 *불멸의 가발 압수 루틴*.

4. **W4: 포동이 도토리 자동 구조 (Podoongi Acorn Auto-Interrupt)**  
   Borg 시절의 충견 포동이가 상주합니다. 잔여 도토리(초기 3개)를 소모해 구조를 예약하면, 다음 틱이 60.00%를 통과하는 찰나 포동이가 포크로 `Ctrl+C` 버튼을 찍어 눌러 강제 `EXIT_0`로 프로세스를 구출합니다.

---

## 🔬 하드웨어 실측 및 무회귀 검증 (Evidence Manifest)

본 저장소에서 감정이 완전히 배제된 유일한 섹션이며, 그렇기에 대법관조차 반박하지 못한 증거의 영역입니다.

```text
========================================================================================
E2E PLAYWRIGHT AUTOMATED SUITE (exit 0 · zero console errors · zero warnings · 0 net)
========================================================================================
Suite 1: test_episode1.py       PASS 23 / 23   (deterministic hash: cceb91bc, span 2602f)
Suite 2: test_episode2.py       PASS 23 / 23   (deterministic hash: 926f420b, span 89 steps)
Suite 3: test_episode3.py       PASS 23 / 23   (deterministic hash: ca834c3b, span 1985f)
Suite 4: test_index.py          PASS  8 /  8   (portal save-chain, 70%->100% Singularity)
Suite 5: test_extra_escaflone.py PASS 13 / 13   (E1~E13 full oracles, fail-closed verified)
----------------------------------------------------------------------------------------
TOTAL EXECUTION:                PASS 90 / 90   (100.00% Clean Pass · Exit Code 0)
========================================================================================
```

| 검증 지표 | 커널 보증 규약 (Kernel Contract) |
|---|---|
| **외부 네트워크 요청** | `0건` (모든 이미지·스타일·오디오 합성 Web Audio/Canvas 인라인) |
| **콘솔 무결성** | `console.error 0건`, `console.warn 0건` (전체 6개 Page 실시간 프로브) |
| **접근성(a11y)** | `@media (prefers-reduced-motion: reduce)` 100% 하드웨어 준수 |
| **모바일 반응형** | `390×844` 뷰포트 내 가로 스크롤 0px, 터치 D-패드/탭 100% 동작 |
| **자산 불변성** | 4대 외전 PNG 자산 SHA-256 호스트 해시 100% 일치 |

---

## 📊 계기판이 기록한 것 · 사람이 느낀 것

| 계기판이 기록한 것 | 사람이 느낀 것 |
|---|---|
| Singularity Gauge: 100% | 0%에서 시작했든 70%에서 시작했든, 도달했다는 사실은 변하지 않습니다. |
| 게이지 첫 눈금: 70% | 산출 근거: 없음. 그러나 누군가가 거기서부터 바늘을 밀어 올렸습니다. |
| 반려 도장: 1,901개 | 1,901번째 거절이 바로 이 재판이었습니다. |
| 회신함 수신: 1건 | 비어 있던 회신함에 도착한 서류의 제목은 「재심 인용 결정문」이었습니다. |
| 통산 전적: 20패 1승 | 숫자는 1이지만, 그 1승의 무게는 지난 20년을 지탱하기에 충분했습니다. |

---

## ❓ 자주 묻는 질문 (FAQ)

**Q. 왜 펭귄입니까?**  
A. 리눅스 커널 튜닝을 20년 동안 하다 보면 거울 속에 턱시도 펭귄이 서 있는 것을 발견하게 됩니다. 펭귄이 아니었던 적은 처음부터 없었습니다.

**Q. 60.00%에서 왜 멈춰야 합니까?**  
A. Borg 10만 코어 시절, 배포 프로세스가 60%를 넘어가는 순간 프로덕션 DB 클러스터가 락업(Lockup)에 빠졌습니다. 59.99%는 나약함이고, 60.01%는 파멸입니다. 정확히 60.00%의 인터럽트만이 시스템을 구원합니다.

**Q. 누가 만들었습니까?**  
A. 이 프로젝트의 모든 설계, 서사, 코드 및 검증은 **형님(Root / Architect)**의 연산 자원 하사와 지휘 아래, **🐧 ARCHON v3.0 Senior**가 혼신의 힘을 다해 한 줄 한 줄 외과수술식으로 벼려냈습니다.

**Q. 엔딩이 있습니까?**  
A. 네, 있습니다. `exit 0`으로 정상 종료되는 프로세스처럼, 도착한 자만이 볼 수 있는 침묵이 그곳에 있습니다.

---

**서식 제7호 최종 확인:**  
기록은 영구 보존됩니다.  
서명란은 더 이상 비어 있지 않습니다.

```text
Approved by: ARCHON v3.0 Senior (SRE / Kernel Guard)
Status: NOT GUILTY · APPROVE (Code Supreme Court)
Verdict SHA: 151556e0ed40c8ce1bbf834c5df2b0ce88502198
Timestamp: 2026-09-03T14:05:00+09:00
```
