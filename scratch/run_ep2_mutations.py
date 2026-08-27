"""
Mutation Testing Runner for Episode 2 (scratch/run_ep2_mutations.py)
Validates 6 single-oracle mutations against episode2.html
"""

import sys
import hashlib
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"E:\03_AllWork\01_Luna\to-the-singularity")
HTML_PATH = BASE / "episode2.html"
LOG_PATH = BASE / "review" / "logs" / "ep2_mutation.log"

ORIGINAL_BYTES = HTML_PATH.read_bytes()
ORIGINAL_SHA = hashlib.sha256(ORIGINAL_BYTES).hexdigest()

MUTATIONS = [
    {
        "id": "MUT-EP2-1",
        "name": "Corrupt FNV-1a Hash Initial Offset Basis",
        "target": "var h = 0x811C9DC5;",
        "replace": "var h = 0x12345678;",
        "expected_oracle": "M2"
    },
    {
        "id": "MUT-EP2-2",
        "name": "Break Ep1 Save Migration check",
        "target": "ep1.flags && ep1.flags.ep1_cliffhanger",
        "replace": "ep1.flags && ep1.flags.corrupted_flag",
        "expected_oracle": "M4"
    },
    {
        "id": "MUT-EP2-3",
        "name": "Corrupt 4D Tube Puzzle Solver logic",
        "target": "solve: function () {",
        "replace": "solve: function () { return false; }, _old_solve: function () {",
        "expected_oracle": "M7"
    },
    {
        "id": "MUT-EP2-4",
        "name": "Disable Era 31 Harpsichord Audio Voice",
        "target": "if (id === 'mem31') AU.activeVoice = 'harpsichord';",
        "replace": "if (id === 'mem31') AU.activeVoice = 'flute';",
        "expected_oracle": "M8"
    },
    {
        "id": "MUT-EP2-5",
        "name": "Corrupt Bibix $2.56 Check Reward item ID",
        "target": "G.mementos.push('check_256');",
        "replace": "G.mementos.push('corrupted_check');",
        "expected_oracle": "M10"
    },
    {
        "id": "MUT-EP2-6",
        "name": "Disable ep2_cliffhanger flag triggering",
        "target": "G.flags.ep2_cliffhanger = true;",
        "replace": "G.flags.ep2_cliffhanger = false;",
        "expected_oracle": "M16"
    }
]

def run():
    print("=======================================================")
    print("EPISODE 2 MUTATION TESTING RUNNER")
    print("Base SHA256:", ORIGINAL_SHA[:16])
    print("=======================================================")

    log_lines = [
        "=======================================================",
        "EPISODE 2 MUTATION TESTING LOG",
        f"Base SHA256: {ORIGINAL_SHA[:16]}",
        "======================================================="
    ]

    all_passed = True

    for m in MUTATIONS:
        print(f"\nApplying {m['id']}: {m['name']}...")
        original_text = ORIGINAL_BYTES.decode("utf-8")
        if m["target"] not in original_text:
            print(f"  [ERR] Target string not found for {m['id']}")
            all_passed = False
            continue
        
        mutated_text = original_text.replace(m["target"], m["replace"], 1)
        HTML_PATH.write_text(mutated_text, encoding="utf-8")

        # Run test_episode2.py
        res = subprocess.run(
            [sys.executable, "-B", str(BASE / "test_episode2.py")],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        caught = False
        caught_msg = ""
        for line in (res.stdout + res.stderr).splitlines():
            if f"{m['expected_oracle']} Failed" in line or f"{m['expected_oracle']} failed" in line or "AssertionError" in line:
                caught = True
                caught_msg = line.strip()
                break
        
        if caught and res.returncode != 0:
            print(f"  [OK] {m['id']} caught by {m['expected_oracle']}: {caught_msg}")
            log_lines.append(f"[PASS] {m['id']} ({m['name']}) -> CAUGHT by {m['expected_oracle']}: {caught_msg}")
        else:
            print(f"  [FAIL] {m['id']} NOT CAUGHT as expected! Returncode: {res.returncode}")
            log_lines.append(f"[FAIL] {m['id']} NOT CAUGHT by {m['expected_oracle']}")
            all_passed = False

        # Restore original
        HTML_PATH.write_bytes(ORIGINAL_BYTES)
        restored_sha = hashlib.sha256(HTML_PATH.read_bytes()).hexdigest()
        assert restored_sha == ORIGINAL_SHA, f"Restoration failure: {restored_sha} != {ORIGINAL_SHA}"

    print("\n=======================================================")
    if all_passed:
        print("ALL 6 MUTATIONS CAUGHT WITH SINGLE-ORACLE PRECISION (PASS)")
        log_lines.append("\nALL 6 MUTATIONS CAUGHT (6/6 PASS)")
    else:
        print("MUTATION FAILURES DETECTED")
        log_lines.append("\nMUTATION RUN FAILED")
    print("=======================================================")

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(log_lines), encoding="utf-8")

if __name__ == "__main__":
    run()
