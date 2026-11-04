# 산출물 3. API 명세서

기준 주소 `http://127.0.0.1:8000`. 모든 업로드는 `multipart/form-data`, 필드명 `image`. 업로드 한도 5MB(`MAX_UPLOAD_BYTES`), 허용 형식 JPEG·PNG·WEBP, 최대 1,200만 픽셀.

| API ID | Method | URL | 요청 | 성공 HTTP | 주요 응답 | 실패 HTTP |
|---|---|---|---|---:|---|---|
| A-01 | GET | `/health` | 없음 | 200 | `{"status":"ok"}` | — |
| A-02 | POST | `/api/sync/classify/` | `image` 파일 | 200 | `model_id`, `top1{label,score}`, `all[]`, `inference_ms`, `cache_hit` | 400 이미지 아님·형식 불가, 413 5MB 초과, 422 `image` 누락 |
| A-03 | POST | `/api/async/classify/` | `image` 파일 | **202** | `job_id`, `status:"queued"`, `check_url` | 400, 413, 422, 503 큐 등록 실패(Redis) |
| A-04 | GET | `/api/async/jobs/{job_id}/` | 경로 변수 `job_id` | 200 | `status`(queued·running·done·failed), `top1`·`all`(done일 때만), `inference_ms`, `cache_hit`, `error_message`(failed일 때만) | 404 없는 작업 |
| W-01 | GET | `/vision/sync/` | 없음 | 200 | 동기 분류 화면 (HTML) | — |
| W-02 | GET | `/vision/async/` | 없음 | 200 | 비동기 분류 화면 (HTML, 1초 간격 최대 60회 조회) | — |
| W-03 | GET | `/docs` | 없음 | 200 | Swagger 문서 | — |

- **202는 "접수"이지 "완료"가 아니다.** 결과는 A-04로 따로 조회해야 한다.
- `cache_hit=true`일 때 `inference_ms=null` → 모델 추론을 **건너뛰었다**는 뜻이지 0ms가 아니다.
- 동기 API는 DB에 기록하지 않는다. `image_jobs`에는 비동기 작업만 쌓인다.

## 요청·응답 증빙

전체 원본: [evidence/api_responses.json](evidence/api_responses.json) (2026-11-04 11:09:24 +0900, `requests` 라이브러리로 호출)

A-02 동기, 처음 보내는 이미지 `test/healthy/healthy_test.0.jpg` → HTTP 200, 24.6 ms

```json
{
  "model_id": "artifacts/beans_resnet18",
  "top1": {
    "label": "healthy",
    "score": 0.636943519115448
  },
  "all": [
    {
      "label": "healthy",
      "score": 0.636943519115448
    },
    {
      "label": "bean_rust",
      "score": 0.24815838038921356
    },
    {
      "label": "angular_leaf_spot",
      "score": 0.11489810794591904
    }
  ],
  "inference_ms": 18.88,
  "cache_hit": false
}
```

같은 파일을 다시 보냄 → HTTP 200, 3.6 ms, 캐시 HIT

```json
{
  "model_id": "artifacts/beans_resnet18",
  "top1": {
    "label": "healthy",
    "score": 0.636943519115448
  },
  "all": [
    {
      "label": "healthy",
      "score": 0.636943519115448
    },
    {
      "label": "bean_rust",
      "score": 0.24815838038921356
    },
    {
      "label": "angular_leaf_spot",
      "score": 0.11489810794591904
    }
  ],
  "inference_ms": null,
  "cache_hit": true
}
```

A-03 비동기 접수 `test/bean_rust/bean_rust_test.10.jpg` → HTTP 202, 10.3 ms

```json
{
  "job_id": 2,
  "status": "queued",
  "check_url": "/api/async/jobs/2/"
}
```

A-04 조회 (관찰한 상태 변화: queued → done) → HTTP 200

```json
{
  "job_id": 2,
  "status": "done",
  "model_id": "artifacts/beans_resnet18",
  "top1": {
    "label": "angular_leaf_spot",
    "score": 0.3825364112854004
  },
  "all": [
    {
      "label": "angular_leaf_spot",
      "score": 0.3825364112854004
    },
    {
      "label": "healthy",
      "score": 0.3227664828300476
    },
    {
      "label": "bean_rust",
      "score": 0.2946971356868744
    }
  ],
  "inference_ms": 16.9,
  "cache_hit": false,
  "error_message": null
}
```

## 실행 근거표

| 검증 ID | 입력 | 실제 상태코드 | 증빙 |
|---|---|---:|---|
| V-01 | GET `/health` | 200 | api_responses.json `error_cases.health` |
| V-02 | POST sync, 콩잎 JPG 5장 (MISS) | 200 ×5 | api_responses.json `runs` |
| V-03 | POST sync, 같은 5장 다시 (HIT) | 200 ×5 | 같은 파일 |
| V-04 | POST async, 콩잎 JPG 5장 | 202 ×5 | 같은 파일 |
| V-05 | GET `/api/async/jobs/{2~11}/` | 200, 전부 `done` | 같은 파일 |
| V-06 | POST sync, 텍스트 파일 `not_image.txt` | 400 `올바른 이미지 파일이 아닙니다.` | `error_cases.txt_sync` |
| V-07 | POST async, 텍스트 파일 | 400 (큐 등록 전 차단, DB 기록 없음) | `error_cases.txt_async` |
| V-08 | POST sync, 6MB 파일 | 413 `5MB 이하 파일만 허용합니다.` | `error_cases.big_sync` |
| V-09 | POST async, 6MB 파일 | 413 | `error_cases.big_async` |
| V-10 | POST sync, 파일 없이 | 422 (FastAPI 검증 `Field required`) | `error_cases.no_file_sync` |
| V-11 | GET `/api/async/jobs/999999/` | 404 `해당 작업이 없습니다.` | `error_cases.job_404` |
| V-12 | POST async, Worker 정지 상태 | 202 → 5초 뒤에도 `queued` | [t10_worker_stopped.txt](evidence/t10_worker_stopped.txt) |
| — | 503 큐 등록 실패 | 미실시 (Redis를 끈 상태 접수는 시험하지 않음) | — |
