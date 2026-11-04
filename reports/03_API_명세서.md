# 산출물 3. API 명세서

기준 주소 `http://127.0.0.1:8000` (FastAPI, `.venv`). 업로드는 `multipart/form-data`, 필드명 `image`. 한도 5MB(`MAX_UPLOAD_BYTES`), 형식 JPEG·PNG·WEBP, 최대 1,200만 픽셀.

| API ID | Method | URL | 요청 형태 | 성공 HTTP | 주요 응답 | 실패 HTTP |
|---|---|---|---|---:|---|---|
| API-01 | GET | `/health` | 없음 | 200 | `status` | 서버 미실행 시 응답 없음 |
| API-02 | POST | `/api/sync/classify/` | `multipart/form-data` / `image` | 200 | `model_id`, `top1`, `all`, `inference_ms`, `cache_hit` | 400, 413, 422 |
| API-03 | POST | `/api/async/classify/` | `multipart/form-data` / `image` | **202** | `job_id`, `status`, `check_url` | 400, 413, 422, 503 |
| API-04 | GET | `/api/async/jobs/{job_id}/` | 정수 `job_id` | 200 | `status`, `model_id`, `top1`, `all`, `inference_ms`, `cache_hit`, `error_message` | 404 |
| WEB-01 | GET | `/vision/sync/` | 없음 | 200 | HTML | — |
| WEB-02 | GET | `/vision/async/` | 없음 | 200 | HTML (1초 간격, 최대 60회 조회) | — |
| WEB-03 | GET | `/docs` | 없음 | 200 | Swagger UI ([캡처](evidence/ui_swagger.png)) | — |

### API-02 동기 분류 상세

| 항목 | 내용 |
|---|---|
| Content-Type | `multipart/form-data` |
| 요청 필드 | `image`: JPEG/PNG/WEBP, 5MB 이하 |
| 성공 | 200 — 응답 안에 분류 결과 포함 |
| 오류 | 400 이미지가 아님·형식 불가·해상도 초과, 413 5MB 초과, 422 `image` 누락 (FastAPI 검증) |
| 캐시 | `cache_hit=true`면 `inference_ms=null` — 추론을 **건너뛴 것**이지 0ms가 아님 |
| Redis 장애 | 캐시 조회·저장을 건너뛰고 추론해서 200 (T-15 확인) |

### API-03 / API-04 상세

- **202는 작업 접수일 뿐 완료가 아니다.** 완료는 API-04 응답의 `status=done`으로 확인한다.
- `top1`·`all`은 `done`일 때만, `error_message`는 `failed`일 때만 값이 있다.
- 503: Redis(브로커)가 내려가 `classify_job.delay`가 실패하면 DB 행을 `failed`로 바꾸고 503을 돌려준다 (T-15).
- 응답 필드명은 `all`이다. `all_scores`는 DB 컬럼명이다.

## 요청·응답 증빙

전체 원본: [evidence/api_responses.json](evidence/api_responses.json) (2026-11-04T12:51:31+09:00, `scripts/bench_api.py`, Validation 이미지)

API-02 성공 — `val/healthy/healthy_val.0.jpg` → HTTP 200, 23.6 ms

```json
{
  "model_id": "artifacts/beans_resnet18_full",
  "top1": {
    "label": "healthy",
    "score": 0.9102250933647156
  },
  "all": [
    {
      "label": "healthy",
      "score": 0.9102250933647156
    },
    {
      "label": "angular_leaf_spot",
      "score": 0.05476333200931549
    },
    {
      "label": "bean_rust",
      "score": 0.03501157462596893
    }
  ],
  "inference_ms": 18.37,
  "cache_hit": false
}
```

API-02 같은 파일 재요청 (캐시 HIT) → HTTP 200, 2.2 ms

```json
{
  "model_id": "artifacts/beans_resnet18_full",
  "top1": {
    "label": "healthy",
    "score": 0.9102250933647156
  },
  "all": [
    {
      "label": "healthy",
      "score": 0.9102250933647156
    },
    {
      "label": "angular_leaf_spot",
      "score": 0.05476333200931549
    },
    {
      "label": "bean_rust",
      "score": 0.03501157462596893
    }
  ],
  "inference_ms": null,
  "cache_hit": true
}
```

API-03 접수 — `val/bean_rust/bean_rust_val.10.jpg` → HTTP 202, 8.9 ms

```json
{
  "job_id": 2,
  "status": "queued",
  "check_url": "/api/async/jobs/2/"
}
```

API-04 완료 (관찰한 상태: queued → done) → HTTP 200

```json
{
  "job_id": 2,
  "status": "done",
  "model_id": "artifacts/beans_resnet18_full",
  "top1": {
    "label": "bean_rust",
    "score": 0.9991656541824341
  },
  "all": [
    {
      "label": "bean_rust",
      "score": 0.9991656541824341
    },
    {
      "label": "angular_leaf_spot",
      "score": 0.0006010123179294169
    },
    {
      "label": "healthy",
      "score": 0.00023333744320552796
    }
  ],
  "inference_ms": 19.15,
  "cache_hit": false,
  "error_message": null
}
```

API-02 오류 (텍스트 파일) → 400

```json
{
  "detail": "올바른 이미지 파일이 아닙니다."
}
```

API-04 오류 (없는 작업) → 404

```json
{
  "detail": "해당 작업이 없습니다."
}
```

API-03 오류 (Redis 정지) → 503 — [t15_redis_stopped.txt](evidence/t15_redis_stopped.txt)

```json
{"detail": "작업 큐 등록 실패: Redis 연결을 확인하세요."}
```

## 실행 근거표

| 검증 ID | 테스트 입력 | 실제 상태코드 | 증빙 |
|---|---|---:|---|
| API-01-T01 | GET `/health` | 200 | api_responses.json `error_cases.health` |
| API-02-T01 | Validation JPG 5장, 처음 보냄 (MISS) | 200 ×5 | api_responses.json `runs` |
| API-02-T02 | 같은 5장 다시 (HIT) | 200 ×5 | 같은 파일 |
| API-02-T03 | 텍스트 파일 `not_image.txt` | 400 | `error_cases.txt_sync` |
| API-02-T04 | 6MB 파일 | 413 | `error_cases.big_sync` |
| API-02-T05 | 파일 없이 POST | 422 | `error_cases.no_file_sync` |
| API-02-T06 | Redis 정지 중 JPG | 200 (`cache_hit` false, 추론 진행) | [t15_redis_stopped.txt](evidence/t15_redis_stopped.txt) |
| API-03-T01 | Validation JPG 5장 | 202 ×5 | api_responses.json |
| API-03-T02 | 텍스트 파일 | 400 (큐 등록 전 차단, DB 행 없음) | `error_cases.txt_async` |
| API-03-T03 | 6MB 파일 | 413 | `error_cases.big_async` |
| API-03-T04 | Redis 정지 중 JPG | 503 (job 14 `failed`) | t15_redis_stopped.txt |
| API-04-T01 | 접수된 job 2~11 | 200, 전부 `done` | api_responses.json |
| API-04-T02 | `/api/async/jobs/999999/` | 404 | `error_cases.job_404` |
| API-04-T03 | 업로드 파일이 사라진 job 13 | 200, `failed` + `error_message` | [t10_t16_worker_stopped.txt](evidence/t10_t16_worker_stopped.txt) |
| WEB-01·02 | 화면에서 업로드·버튼 클릭 | 200 | [ui_sync_miss.png](evidence/ui_sync_miss.png), [ui_async_done.png](evidence/ui_async_done.png) |
