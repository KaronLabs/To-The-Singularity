# Episode 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify `episode2.html` (Episode 2: 《각주 47개와 4차원 서류 슈트》) as a complete, standalone 115KB-class single-file reference implementation with 20/20 automated E2E test oracles.

**Architecture:** Single-file HTML/JS procedural canvas engine with 5 new scenes, 75+ SCRIPT nodes, 4D pneumatic packet routing puzzle with BFS solver, 4-voice procedural Web Audio synth (Piano, Cello, Harpsichord, Pipe Organ), save slot migration from Ep1, and mobile touch support.

**Tech Stack:** Vanilla JS (ES5/ES6), Canvas 2D, Web Audio API, Python 3 / Playwright (`test_episode2.py`).

**Spec:** `plans/2026-08-28-archon-design-ep2.md`

## Global Constraints
- Single-file `episode2.html` with 0 external network requests / assets.
- Fixed 1/60s timestep with rAF accumulator and catch-up cap.
- Seeded mulberry32 PRNG and FNV-1a state serialization for deterministic hash.
- Zero mutation to `episode1.html` or `test_episode1.py`.
- No forbidden words ("완벽", "이상 없음", "전부 통과했습니다" 등).

---

### Task 1: TDD Test Perimeter Construction (`test_episode2.py`)
**Files:**
- Create: `test_episode2.py`
- Test: `test_episode2.py`

**Interfaces:**
- Consumes: `window.__game` and `window.__game.api` contracts
- Produces: 20 E2E & static oracles (M1 ~ M20)

- [ ] **Step 1: Write failing test suite `test_episode2.py`**
- [ ] **Step 2: Run test suite to observe initial RED failure state** (record `review/logs/ep2_red_observe.log`)

### Task 2: Core Engine Baseline & Scene Setup (`episode2.html`)
**Files:**
- Create: `episode2.html`
- Test: `test_episode2.py` (M1, M2, M4, M5)

**Interfaces:**
- Produces: 5 scenes (`roof12`, `tube_hub`, `mem31`, `mem47`, `deep_vault`), procedural tilemap painter, particle wind effect, collision checks.

- [ ] **Step 1: Scaffold `episode2.html` from verified core engine**
- [ ] **Step 2: Implement 5 scenes and procedural tilemap renderers**
- [ ] **Step 3: Run `test_episode2.py` and verify M1, M2, M4, M5 pass**

### Task 3: Characters & SCRIPT Graph (75+ Nodes)
**Files:**
- Modify: `episode2.html`
- Test: `test_episode2.py` (M3, M8, M9, M10, M11, M12, M19)

**Interfaces:**
- Produces: Sprites for Klkos (coat), Newbie (mech), Archon 31 (harpsichord), Archon 47 (organ), Bibix Hologram, 75+ SCRIPT nodes, $2.56 check reward.

- [ ] **Step 1: Add character sprite painters and CRT glitch renderer for Bibix**
- [ ] **Step 2: Write all 75+ dialogue nodes in SCRIPT with branching choices**
- [ ] **Step 3: Run `test_episode2.py` and verify dialogue & character oracles pass**

### Task 4: 4D Pneumatic Tube Puzzle Engine & BFS Solver
**Files:**
- Modify: `episode2.html`
- Test: `test_episode2.py` (M6, M7, M20)

**Interfaces:**
- Produces: 5x4 valve grid UI, packet transit FSM (`IDLE`, `DISPATCH`, `ROUTING`, `WARP`, `DELIVERED`, `DEADLOCK`), `__game.api.solveTubePuzzle()`.

- [ ] **Step 1: Implement 5x4 pneumatic valve grid and packet routing physics**
- [ ] **Step 2: Implement BFS deterministic puzzle solver in `solveTubePuzzle()`**
- [ ] **Step 3: Run `test_episode2.py` and verify M6, M7, M20 pass**

### Task 5: Web Audio 4-Voice Polyphonic Synth Engine
**Files:**
- Modify: `episode2.html`
- Test: `test_episode2.py` (M8, M9, M17)

**Interfaces:**
- Produces: Piano, Cello, Harpsichord (Era 31), Pipe Organ (Era 47) real-time procedural synthesizers.

- [ ] **Step 1: Implement Harpsichord and Pipe Organ procedural synth voices**
- [ ] **Step 2: Hook up dynamic arrangement scheduler based on active era**
- [ ] **Step 3: Run `test_episode2.py` and verify audio telemetry**

### Task 6: Full Verification, Autoplay Bot, and Mutation Testing
**Files:**
- Modify: `episode2.html`
- Create: `scratch/run_ep2_mutations.py`
- Test: `test_episode2.py` (All M1~M20)

**Interfaces:**
- Produces: Full autoplay bot, `review/logs/ep2_strict_green.log`, `review/logs/ep2_mutation.log`, 6 screenshots in `review/shots/`.

- [ ] **Step 1: Run full test suite and confirm strict GREEN 20/20**
- [ ] **Step 2: Execute 6 mutations and verify single-hit assertions**
- [ ] **Step 3: Capture 6 screenshots in `review/shots/`**

### Task 7: Final Completion Report & Code Supreme Court Spec
**Files:**
- Create: `plans/2026-08-28-archon-report-ep2.md`
- Create: `review/spec_20260828_tts_ep2.md`

- [ ] **Step 1: Compute front-16 SHA256 checksums and write completion report**
- [ ] **Step 2: Write Code Supreme Court review spec for Episode 2**
- [ ] **Step 3: Verify 0 forbidden words across all generated files**
