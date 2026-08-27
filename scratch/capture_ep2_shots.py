"""
Screenshot Capture Script for Episode 2 (scratch/capture_ep2_shots.py)
Captures 6 high-res shots into review/shots/
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"E:\03_AllWork\01_Luna\to-the-singularity")
HTML_PATH = BASE / "episode2.html"
URL = HTML_PATH.as_uri()
SHOTS_DIR = BASE / "review" / "shots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)

def capture():
    print("=======================================================")
    print("EPISODE 2 SCREENSHOT CAPTURE")
    print("=======================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 960, "height": 540})

        def fresh():
            page.goto(URL)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(200)

        # 1. roof12
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('roof12', 10, 10);
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_roof12.png"))
        print("  [OK] Captured ep2_roof12.png")

        # 2. tube_hub
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('tube_hub', 15, 10);
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_tube_hub.png"))
        print("  [OK] Captured ep2_tube_hub.png")

        # 3. mem31
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('mem31', 10, 10);
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_mem31.png"))
        print("  [OK] Captured ep2_mem31.png")

        # 4. mem47
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('mem47', 10, 10);
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_mem47.png"))
        print("  [OK] Captured ep2_mem47.png")

        # 5. deep_vault
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('deep_vault', 15, 10);
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_deep_vault.png"))
        print("  [OK] Captured ep2_deep_vault.png")

        # 6. puzzle_tube
        fresh()
        page.evaluate("""
        (() => {
          const g = window.__game;
          g.api.teleport('tube_hub', 15, 10);
          g.api.openTubePuzzle();
          g.api.step(30);
        })()
        """)
        page.screenshot(path=str(SHOTS_DIR / "ep2_puzzle_tube.png"))
        print("  [OK] Captured ep2_puzzle_tube.png")

        browser.close()

    print("=======================================================")
    print("ALL 6 SCREENSHOTS SUCCESSFULLY CAPTURED")
    print("=======================================================")

if __name__ == "__main__":
    capture()
