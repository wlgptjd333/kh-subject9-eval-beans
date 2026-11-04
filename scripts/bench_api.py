"""실행 중인 서비스에 실제 요청을 보내 응답시간·캐시·오류 응답을 측정한다. (제공 코드 아님 — 추가 스크립트)

사용 (서비스 실행 후, 프로젝트 루트에서):
  python scripts/bench_api.py --runs 5

- 이미지: dataset/val 에서 클래스를 번갈아 고른 서로 다른 파일 (Test split은 쓰지 않음)
- 측정 전 Redis 캐시 DB(기본 redis://127.0.0.1:6379/1)를 비워 첫 요청이 MISS가 되게 함
- run_id 0 = 워밍업(프로세스별 모델 첫 로딩), 비교에서 제외
- 결과: reports/data/timings.csv, reports/evidence/api_responses.json
"""
import argparse
import csv
import hashlib
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path

import httpx
from redis import Redis

CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--data", default="dataset/val")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--poll", type=float, default=0.1, help="비동기 상태 조회 간격(초)")
    ap.add_argument("--cache-redis", default="redis://127.0.0.1:6379/1")
    ap.add_argument("--csv", default="reports/data/timings.csv")
    ap.add_argument("--json", default="reports/evidence/api_responses.json")
    args = ap.parse_args()

    need = 2 + 2 * args.runs
    per = {c: sorted((Path(args.data) / c).iterdir()) for c in CLASSES}
    imgs = [per[CLASSES[i % 3]][i // 3] for i in range(need)]
    warm_sync, warm_async = imgs[0], imgs[1]
    sync_set, async_set = imgs[2:2 + args.runs], imgs[2 + args.runs:]

    cache = Redis.from_url(args.cache_redis)
    keys_before = cache.dbsize()
    cache.flushdb()
    client = httpx.Client(base_url=args.base, timeout=120)
    rows, runs = [], []

    def info(p: Path):
        b = p.read_bytes()
        return {"file": f"{Path(args.data).name}/{p.parent.name}/{p.name}", "true_label": p.parent.name,
                "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}

    def post(url, p):
        t0 = time.perf_counter()
        with open(p, "rb") as f:
            r = client.post(url, files={"image": (p.name, f, "image/jpeg")})
        return r, (time.perf_counter() - t0) * 1000, t0

    def sync_run(run_id, p, expect):
        r, ms, _ = post("/api/sync/classify/", p)
        body = r.json()
        got = "HIT" if body.get("cache_hit") else "MISS"
        if r.status_code != 200 or got != expect:
            raise SystemExit(f"sync 예상과 다름: {r.status_code} {got} {body}")
        rows.append([run_id, "sync", got, round(ms, 1), round(ms, 1), body.get("inference_ms"), ""])
        runs.append({"run_id": run_id, "path": "sync", **info(p), "http_status": r.status_code,
                     "http_ms": round(ms, 1), "response": body})

    def async_run(run_id, p, expect):
        r, ms, t0 = post("/api/async/classify/", p)
        acc = r.json()
        if r.status_code != 202:
            raise SystemExit(f"async 접수 실패: {r.status_code} {acc}")
        seen = ["queued"]
        while True:
            j = client.get(acc["check_url"])
            body = j.json()
            if body["status"] != seen[-1]:
                seen.append(body["status"])
            if body["status"] in ("done", "failed"):
                break
            time.sleep(args.poll)
        final = (time.perf_counter() - t0) * 1000
        got = "HIT" if body.get("cache_hit") else "MISS"
        if body["status"] != "done" or got != expect:
            raise SystemExit(f"async 예상과 다름: {body}")
        rows.append([run_id, "async", got, round(ms, 1), round(final, 1), body.get("inference_ms"), acc["job_id"]])
        runs.append({"run_id": run_id, "path": "async", **info(p), "accept_status": r.status_code,
                     "accept_ms": round(ms, 1), "accept_response": acc, "observed_states": seen,
                     "final_ms": round(final, 1), "job_status_code": j.status_code, "job_response": body})

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    sync_run(0, warm_sync, "MISS")
    async_run(0, warm_async, "MISS")
    for i, p in enumerate(sync_set, 1):
        sync_run(i, p, "MISS")
    for i, p in enumerate(sync_set, 1):
        sync_run(i, p, "HIT")
    for i, p in enumerate(async_set, 1):
        async_run(i, p, "MISS")
    for i, p in enumerate(async_set, 1):
        async_run(i, p, "HIT")

    tmp = Path(tempfile.mkdtemp())
    txt = tmp / "not_image.txt"
    txt.write_text("this is not an image\n")
    big = tmp / "big.jpg"
    big.write_bytes(b"\xff\xd8" + os.urandom(6 * 1024 * 1024))
    errors = []
    for tid, method, url, f in [
        ("txt_sync", "POST", "/api/sync/classify/", txt),
        ("txt_async", "POST", "/api/async/classify/", txt),
        ("big_sync", "POST", "/api/sync/classify/", big),
        ("big_async", "POST", "/api/async/classify/", big),
        ("no_file_sync", "POST", "/api/sync/classify/", None),
        ("job_404", "GET", "/api/async/jobs/999999/", None),
        ("health", "GET", "/health", None),
    ]:
        if method == "GET":
            r = client.get(url)
        elif f is None:
            r = client.post(url)
        else:
            with open(f, "rb") as fh:
                r = client.post(url, files={"image": (f.name, fh)})
        errors.append({"id": tid, "method": method, "url": url, "input": f.name if f else None,
                       "status": r.status_code, "body": r.json()})

    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "path", "cache_status", "http_ms", "final_ms", "inference_ms", "job_id"])
        w.writerows([["" if c is None else c for c in r] for r in rows])
    out = {"measured_at": started, "base_url": args.base, "images_from": args.data, "poll_interval_s": args.poll,
           "cache_keys_before_flush": keys_before, "cache_keys_after": cache.dbsize(),
           "runs": runs, "error_cases": errors}
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    for r in rows:
        print(r)
    for e in errors:
        print(e["id"], e["status"], json.dumps(e["body"], ensure_ascii=False)[:100])
    print(f"저장: {args.csv}, {args.json}")


if __name__ == "__main__":
    main()
