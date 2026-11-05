"""사진 10장을 한꺼번에 보낼 때 동기·비동기 비교 (제공 코드 아님 — 추가 스크립트)

  python scripts/burst_api.py --repeat 3

두 가지 보내는 방식 × 두 가지 경로:
- 연속(sequential): 한 장 응답을 받은 뒤 다음 장 (버튼을 빠르게 10번 누르는 것과 같음)
- 동시(concurrent): 10장을 스레드 10개로 한꺼번에 보냄 (사용자 10명이 같은 순간에 누르는 것과 같음)
- 동기: 10번째 결과까지 받은 시간 / 비동기: 10장 모두 202 받은 시간 + 10장 모두 done 확인 시간

공정 비교: 매 실행 전에 Redis 캐시 DB 1을 비워 10장 모두 MISS, 네 조건 모두 같은 Validation 10장.
Worker 설정은 제공 명령 그대로 (--pool=solo --concurrency=1, 한 번에 1개 처리).
결과: reports/data/burst_10.csv (요청별), reports/data/burst_10_summary.json
"""
import argparse
import csv
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import httpx
from redis import Redis

CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]


def now_ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--data", default="dataset/val")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--poll", type=float, default=0.1)
    ap.add_argument("--skip", type=int, default=27, help="클래스별 앞쪽 N장은 다른 측정·캡처에 썼으므로 건너뜀")
    args = ap.parse_args()

    per = {c: sorted((Path(args.data) / c).iterdir(), key=lambda p: int(p.stem.split(".")[-1])) for c in CLASSES}
    imgs = [per[CLASSES[i % 3]][args.skip + i // 3] for i in range(args.n)]
    blobs = [(p, p.read_bytes()) for p in imgs]
    cache = Redis.from_url("redis://127.0.0.1:6379/1")
    broker = Redis.from_url("redis://127.0.0.1:6379/2")
    client = httpx.Client(base_url=args.base, timeout=120)

    def post(path, item):
        p, b = item
        t = time.perf_counter()
        r = client.post(path, files={"image": (p.name, b, "image/jpeg")})
        return r, round((time.perf_counter() - t) * 1000, 1)

    # 워밍업: 두 프로세스 모두 모델을 올려 둠 (측정 제외)
    warm = per["healthy"][args.skip + args.n]
    wb = (warm, warm.read_bytes())
    post("/api/sync/classify/", wb)
    j = post("/api/async/classify/", wb)[0].json()["job_id"]
    while client.get(f"/api/async/jobs/{j}/").json()["status"] not in ("done", "failed"):
        time.sleep(0.2)

    rows, summary = [], []
    for rep in range(1, args.repeat + 1):
        for mode in ["sequential", "concurrent"]:
            for path in ["sync", "async"]:
                cache.flushdb()
                url = f"/api/{path}/classify/"
                t0 = time.perf_counter()
                if mode == "sequential":
                    res = []
                    for it in blobs:
                        r, ms = post(url, it)
                        res.append((r, ms, now_ms(t0)))
                else:
                    with ThreadPoolExecutor(max_workers=args.n) as ex:
                        futs = [ex.submit(lambda it: (*post(url, it), now_ms(t0)), it) for it in blobs]
                        res = [f.result() for f in futs]
                all_resp = now_ms(t0)
                rec = {"repeat": rep, "mode": mode, "path": path, "all_responses_ms": all_resp}
                if path == "async":
                    rec["queue_len_after_submit"] = broker.llen("celery")
                    ids = [r.json()["job_id"] for r, _, _ in res]
                    done_at, last = {}, {}
                    while len(done_at) < len(ids):
                        for i in ids:
                            if i in done_at:
                                continue
                            js = client.get(f"/api/async/jobs/{i}/").json()
                            if js["status"] in ("done", "failed"):
                                done_at[i] = now_ms(t0); last[i] = js
                        time.sleep(args.poll)
                    rec["all_done_ms"] = max(done_at.values())
                    rec["job_ids"] = f"{min(ids)}-{max(ids)}"
                    rec["worker_inference_ms_sum"] = round(sum(last[i]["inference_ms"] or 0 for i in ids), 1)
                    for (r, ms, at), i in zip(res, ids):
                        rows.append({**{k: rec[k] for k in ("repeat", "mode", "path")}, "file": "", "status": r.status_code,
                                     "http_ms": ms, "responded_at_ms": at, "job_id": i, "done_at_ms": done_at[i],
                                     "label": last[i]["top1"]["label"] if last[i]["top1"] else "", "inference_ms": last[i]["inference_ms"],
                                     "cache_hit": last[i]["cache_hit"]})
                else:
                    for r, ms, at in res:
                        js = r.json()
                        rows.append({**{k: rec[k] for k in ("repeat", "mode", "path")}, "file": "", "status": r.status_code,
                                     "http_ms": ms, "responded_at_ms": at, "job_id": "", "done_at_ms": at,
                                     "label": js["top1"]["label"], "inference_ms": js["inference_ms"], "cache_hit": js["cache_hit"]})
                for row, (p, _) in zip(rows[-args.n:], blobs):
                    row["file"] = f"{p.parent.name}/{p.name}"
                bad = [r for r in rows[-args.n:] if r["status"] not in (200, 202) or r["cache_hit"]]
                if bad:
                    raise SystemExit(f"조건 위반: {bad[:2]}")
                rec["http_ms_median"] = statistics.median(r["http_ms"] for r in rows[-args.n:])
                rec["http_ms_max"] = max(r["http_ms"] for r in rows[-args.n:])
                summary.append(rec)
                print(rec)
                time.sleep(1)

    out = Path("reports/data")
    with open(out / "burst_10.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    agg = {}
    for mode in ["sequential", "concurrent"]:
        for path in ["sync", "async"]:
            s = [x for x in summary if x["mode"] == mode and x["path"] == path]
            agg[f"{mode}.{path}"] = {k: statistics.median(x[k] for x in s) for k in
                                     ["all_responses_ms", "http_ms_median", "http_ms_max", "all_done_ms", "queue_len_after_submit",
                                      "worker_inference_ms_sum"] if k in s[0]}
    (out / "burst_10_summary.json").write_text(json.dumps({
        "measured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "images": [f"{p.parent.name}/{p.name}" for p, _ in blobs], "repeat": args.repeat, "poll_s": args.poll,
        "worker": "--pool=solo --concurrency=1", "median_of_repeats": agg, "runs": summary}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(agg, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
