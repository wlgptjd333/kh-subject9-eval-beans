"""동기·비동기 화면에서 실제로 파일을 고르고 버튼을 눌러 결과 화면을 캡처한다. (제공 코드 아님 — 추가 스크립트)

필요: pip install playwright  (설치된 Chrome을 channel="chrome"으로 사용, 브라우저 추가 설치 없음)
사용:
  python scripts/capture_ui.py --sync-image <jpg> --async-image <jpg> --out reports/evidence
- 서비스(http://127.0.0.1:8000)가 실행 중이어야 함
- 동기: 같은 파일을 두 번 보내 MISS / HIT 화면을 각각 저장
- 비동기: 접수 직후 / done 확인 후 화면 저장 (화면은 1초 간격으로 상태를 조회)
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--sync-image", required=True)
    ap.add_argument("--async-image", required=True)
    ap.add_argument("--out", default="reports/evidence")
    ap.add_argument("--channel", default="chrome")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=args.channel, headless=True)
        page = browser.new_page(viewport={"width": 1100, "height": 1400})

        page.goto(args.base + "/vision/sync/")
        page.set_input_files("#image", args.sync_image)
        page.click("#send")
        page.wait_for_function("document.querySelector('#output').textContent.includes('cache_hit')", timeout=60000)
        page.screenshot(path=str(out / "ui_sync_miss.png"), full_page=True)
        print("sync 1:", page.inner_text("#state"))
        page.click("#send")
        page.wait_for_function("document.querySelector('#output').textContent.includes('\"cache_hit\": true')", timeout=60000)
        page.screenshot(path=str(out / "ui_sync_hit.png"), full_page=True)
        print("sync 2:", page.inner_text("#state"))

        page.goto(args.base + "/vision/async/")
        page.set_input_files("#image", args.async_image)
        page.click("#send")
        page.wait_for_function("document.querySelector('#state').textContent.includes('접수 완료')", timeout=60000)
        page.screenshot(path=str(out / "ui_async_accepted.png"), full_page=True)
        print("async 접수:", page.inner_text("#state"))
        page.wait_for_function("/상태 (done|failed)/.test(document.querySelector('#state').textContent)", timeout=90000)
        page.screenshot(path=str(out / "ui_async_done.png"), full_page=True)
        print("async 완료:", page.inner_text("#state"))

        page.goto(args.base + "/docs")
        page.wait_for_selector("text=/api/async/classify/", timeout=60000)
        page.screenshot(path=str(out / "ui_swagger.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
