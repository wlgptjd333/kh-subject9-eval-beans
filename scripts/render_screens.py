"""reports/evidence/screens/src/*.txt (실제 명령 출력) → 터미널 모양 PNG. 브라우저 JSON 화면도 함께 캡처."""
import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

S = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports/evidence/screens")
src, out = S / "src", S
out.mkdir(exist_ok=True)
TITLES = {
    "cap01_dataset": "데이터 배치·클래스별 개수 (dataset/train·val·test)",
    "cap02_model_dirs": "학습 모델 폴더 (E0·E2)와 .env MODEL_PATH",
    "cap03_train_e0": "E0 Head-only 학습 로그 (--freeze-backbone, 3 Epoch)",
    "cap04_train_e2": "E2 Full Fine-tuning 학습 로그 (5 Epoch, lr 5e-5)",
    "cap05_test_eval": "Val 기준 모델 선정 기록과 Test 실행 기록",
    "cap06_runtime": "실행 구조: Docker는 Redis·PostgreSQL만, FastAPI·Celery는 .venv",
    "cap07_db_schema": "PostgreSQL image_jobs 테이블 구조",
    "cap08_db_rows": "PostgreSQL image_jobs 작업 이력 (SQL 조회)",
    "cap09_redis_cache": "Redis 캐시 MISS → HIT (같은 Validation 이미지 2회)",
    "cap10_timings": "성능 측정 원본 timings.csv",
    "cap11_pytest": "모의 테스트 pytest",
    "cap12_t10_worker_stopped": "T-10·T-16 Worker 정지 중 접수 → 재시작 후 처리 / 파일 유실 failed",
    "cap13_t15_redis_stopped": "T-15 Redis 정지 → 동기 200, 비동기 503 → 복구",
    "cap14_worker_log": "Celery Worker 로그",
    "cap15_errors": "오류 입력 응답 (400·413·422·404)",
    "cap16_review_rule": "개선 실험: E2 + '확인 필요' 규칙 Test 적용 결과",
}
CSS = """body{margin:0;background:#1e1e1e;font-family:'D2Coding','Consolas','Malgun Gothic',monospace}
.bar{background:#323233;color:#ccc;padding:8px 14px;font:14px 'Malgun Gothic',sans-serif}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px}
pre{margin:0;padding:14px 16px;color:#d4d4d4;font-size:13px;line-height:1.45;white-space:pre-wrap;word-break:break-all}
.p{color:#6a9955}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome", headless=True)
    page = b.new_page(viewport={"width": 1180, "height": 300}, device_scale_factor=1)
    for f in sorted(src.glob("*.txt")):
        lines = f.read_text(encoding="utf-8").splitlines()
        body = "\n".join(f'<span class="p">{html.escape(l)}</span>' if l.startswith("user1@wsl:") else html.escape(l)
                         for l in lines)
        doc = (f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
               f"<div class='bar'><span class='dot' style='background:#ff5f57'></span><span class='dot' style='background:#febc2e'></span>"
               f"<span class='dot' style='background:#28c840'></span>&nbsp; Ubuntu (WSL2) — {html.escape(TITLES.get(f.stem, f.stem))}</div>"
               f"<pre>{body}</pre></body></html>")
        page.set_content(doc)
        page.screenshot(path=str(out / f"{f.stem}.png"), full_page=True)
        print("ok", f.stem)
    # 브라우저에서 실제 API 응답
    for name, url in [("cap17_job_done_json", "http://127.0.0.1:8000/api/async/jobs/16/"),
                      ("cap18_job_failed_json", "http://127.0.0.1:8000/api/async/jobs/13/"),
                      ("ui_swagger", "http://127.0.0.1:8000/docs")]:
        page.set_viewport_size({"width": 1180, "height": 800 if name == "ui_swagger" else 130})
        page.goto(url); page.wait_for_timeout(1500)
        page.screenshot(path=str(out / f"{name}.png"))
        print("ok", name)
    b.close()
