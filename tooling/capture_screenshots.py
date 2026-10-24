from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "screenshots"
BASE_URL = "http://127.0.0.1:8000"


def wait_for_server() -> None:
    for _ in range(90):
        try:
            with urllib.request.urlopen(BASE_URL + "/api/health", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Backend did not become healthy within 45 seconds.")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        wait_for_server()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            errors = []
            desktop = browser.new_page(viewport={"width": 1440, "height": 1100})
            desktop.on("pageerror", lambda error: errors.append(str(error)))
            desktop.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            desktop.screenshot(path=str(OUTPUT / "game-mod-asset-lab-desktop.png"), full_page=True)
            desktop.locator("#settings").scroll_into_view_if_needed()
            desktop.screenshot(path=str(OUTPUT / "game-mod-asset-lab-settings.png"))
            mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            mobile.on("pageerror", lambda error: errors.append(str(error)))
            mobile.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            mobile.screenshot(path=str(OUTPUT / "game-mod-asset-lab-mobile.png"), full_page=True)
            browser.close()
            if errors:
                (OUTPUT / "browser-errors.txt").write_text("\\n".join(errors), encoding="utf-8")
                raise RuntimeError("Browser JavaScript errors: " + "; ".join(errors))
    finally:
        server.terminate()
        server.wait(timeout=10)
    print(f"Screenshots saved in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
