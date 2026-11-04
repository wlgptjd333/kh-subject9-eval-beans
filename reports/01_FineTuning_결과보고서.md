# 산출물 1. Fine-tuning 결과보고서

- 평가 대상: 콩잎 질병 이미지 3클래스 분류
- 기준 모델: microsoft/resnet-18
- 학습 방식: **Head-only** (Backbone freeze, `--freeze-backbone`) — 전체 모델 학습 아님
- 입력 데이터: `dataset/train`, `dataset/val` / 최종 보관: `dataset/test` (학습·모델 선택에 사용하지 않음)
- 모델 저장 위치: `artifacts/beans_resnet18/`
- 학습 환경: 프로젝트 전용 `.venv` (Python 3.11.17, torch 2.15.0+cu132, transformers 4.57.6), GPU RTX 3060
- 실험 상태: Head-only 학습 완료 (2026-11-04)

## 1. 데이터 구성

출처: Hugging Face [AI-Lab-Makerere/beans](https://huggingface.co/datasets/AI-Lab-Makerere/beans) `data/train.zip`, `data/validation.zip`, `data/test.zip`. 배치는 `scripts/prepare_data.py`, 결과 원본 [dataset_check.json](data/dataset_check.json).

| 클래스 | Train | Validation | Test |
|---|---:|---:|---:|
| angular_leaf_spot | 345 | 44 | 43 |
| bean_rust | 348 | 45 | 43 |
| healthy | 341 | 44 | 42 |
| 합계 | 1,034 | 133 | 128 |

- 원본 보존: `beans_source/zips/`(zip), `beans_source/train|validation|test/`(압축 해제본) — Git 제외
- 매핑: 원본 `train` → `dataset/train`, **원본 `validation` → `dataset/val`**, 원본 `test` → `dataset/test`
- 제외: `train/healthy/healthy_train.120tore` 1개 — 이미지가 아닌 macOS `.DS_Store` 파일(시작 바이트 `Bud1`). 제외 후 Train 1,034장 = 데이터 카드 수량
- 정답: 폴더 라벨을 그대로 따름
- 클래스 균형: split마다 세 클래스 수 차이 최대 4장
- 중복·누출 점검: 전체 1,295장 SHA-256 비교 → 같은 내용 0쌍, split 간 중복 0쌍, 파일명 겹침 0건
- 한계: 해시는 **완전히 같은 파일**만 찾음. 같은 잎을 다시 찍은 사진(거의 같은 이미지)은 확인하지 못함

zip 원본 SHA-256:

```text
284fe8456ce20687f4367ae7ad94a64577e7f9fde2c2c6b1c74340ab5dc82715  train.zip
90b7aa1c26d91d9afff07a30bbc67a5ea34f1f1397f068d8675be09d7d0c602d  validation.zip
ca67b15d960d1e2fd9d23fd8498ce86818ead90755c630a43baf19ec4af09312  test.zip
```

## 2. 실행 설정

| 파라미터 | 값 |
|---|---|
| base_model | microsoft/resnet-18 |
| epochs | 3 |
| batch_size | 8 |
| learning_rate | 0.0002 (제공 코드 기본값) |
| freeze_backbone | True — `classifier.`로 시작하는 파라미터만 학습 |
| output | artifacts/beans_resnet18 |
| seed | 42 (제공 코드) |
| 장치 | GPU (CUDA 자동 사용) |

```bash
source .venv/bin/activate
python -m training.finetune --data dataset --output artifacts/beans_resnet18 --epochs 3 --batch-size 8 --freeze-backbone
```

출력층 교체 확인 (학습 로그): `classifier.1.weight` `[1000, 512]` → `[3, 512]`, `classifier.1.bias` `[1000]` → `[3]` 새로 초기화

## 3. 학습 결과 (`training_report.json`과 일치)

| Epoch | Train Loss | Validation Accuracy |
|---|---:|---:|
| 1 | 0.9924 | 0.6617 |
| 2 | 0.8108 | 0.7669 |
| 3 | 0.7078 | 0.7669 |

- Best Validation Accuracy: **0.7669** (133장 중 102장)
- 저장된 모델: **Epoch 2** 가중치 — 제공 코드는 `acc > best_acc`일 때만 저장, 같은 값인 Epoch 3은 저장 안 함
- Train Loss가 3 Epoch 내내 감소 → 아직 수렴 전일 가능성 (개선 실험 E1에서 확인)
- Test Accuracy: **미측정** (제공 코드에 Test 평가 없음, 최종 모델 선정 후 1회 측정 예정)
- 증빙: [학습 로그](evidence/train_log_head_only.txt), [training_report.json 사본](data/training_report_head_only.json), [환경·모델 폴더](evidence/train_env_and_model.txt)

**재현성 확인:** 같은 명령을 다른 Python 환경(수업용 가상환경)에서 먼저 실행했던 모델과, 프로젝트 전용 `.venv`에서 다시 학습한 모델의 `model.safetensors` SHA-256이 같다(`c4ba88e1…`, 가중치 차이 0.0). seed 42 고정과 같은 패키지 버전 덕분이다. 이 보고서의 모든 수치는 `.venv`에서 다시 만든 것이다 ([E-04](07_기능테스트_오류분석.md)).

### 3-1. Validation 세부 평가 (추가 스크립트 `training/evaluate.py`)

제공 코드는 정확도만 출력하므로, `finetune.py`의 데이터 읽기·전처리(`FolderImages`)를 그대로 쓰는 평가 스크립트를 **새 파일로 추가**했다.

```bash
python -m training.evaluate --model artifacts/beans_resnet18 --split val
```

- 데이터: `dataset/val` 133장 / 모델: `artifacts/beans_resnet18` / 장치: cuda
- Accuracy: **0.7669** (102/133), Macro F1: 0.764
- 평균 1순위 점수: 맞힌 것 0.6071, 틀린 것 0.504

| 클래스 | Precision | Recall | F1 | 장수 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 0.7857 | 0.75 | 0.7674 | 44 |
| bean_rust | 0.725 | 0.6444 | 0.6824 | 45 |
| healthy | 0.7843 | 0.9091 | 0.8421 | 44 |

혼동행렬 (행 = 정답, 열 = 예측):

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| angular_leaf_spot | 33 | 8 | 3 |
| bean_rust | 8 | 29 | 8 |
| healthy | 1 | 3 | 40 |

- Accuracy 0.7669가 학습 로그 Best Val과 같음 → 평가 조건이 학습 때와 일치
- 가장 약한 클래스 **bean_rust** (Recall 0.6444): 45장 중 8장 angular_leaf_spot, 8장 healthy로 예측
- 병든 잎을 healthy로 놓친 경우 11장 (angular 3 + rust 8) — 질병 분류에서 가장 위험한 오류
- 틀린 예측의 평균 1순위 점수(0.504)가 맞힌 예측(0.6071)보다 낮음 → 낮은 점수를 "확인 필요"로 돌리는 규칙의 근거 (제안, 미구현)
- 틀린 이미지 31장: [eval_beans_resnet18_val.json](data/eval_beans_resnet18_val.json) `errors`

## 4. 생성 파일 확인

| 파일 | 크기 |
|---|---:|
| config.json (`id2label`: 0 angular_leaf_spot, 1 bean_rust, 2 healthy) | 808 B |
| model.safetensors | 44.8 MB |
| preprocessor_config.json | 352 B |
| training_report.json | 468 B |

모델 파일은 Git에 올리지 않음. 폴더 목록: [train_env_and_model.txt](evidence/train_env_and_model.txt)

## 5. 서비스 연결 확인

`.env` `MODEL_PATH=artifacts/beans_resnet18`, FastAPI·Celery를 `.venv`에서 실행 (2026-11-04).

- 모든 응답의 `model_id` = `artifacts/beans_resnet18`, 라벨은 3클래스만 → 원본 1,000클래스가 아니라 학습한 모델이 쓰임
- 서비스 측정에 쓴 **Validation** 이미지 12장 (캐시 HIT 중복 제외):

| run_id | 경로 | 파일 | 정답 | 예측 | 점수 | 일치 |
|---:|---|---|---|---|---:|:-:|
| 0 | sync | `val/angular_leaf_spot/angular_leaf_spot_val.0.jpg` | angular_leaf_spot | angular_leaf_spot | 0.482 | O |
| 0 | async | `val/bean_rust/bean_rust_val.0.jpg` | bean_rust | healthy | 0.434 | X |
| 1 | sync | `val/healthy/healthy_val.0.jpg` | healthy | bean_rust | 0.477 | X |
| 2 | sync | `val/angular_leaf_spot/angular_leaf_spot_val.1.jpg` | angular_leaf_spot | bean_rust | 0.463 | X |
| 3 | sync | `val/bean_rust/bean_rust_val.1.jpg` | bean_rust | angular_leaf_spot | 0.461 | X |
| 4 | sync | `val/healthy/healthy_val.1.jpg` | healthy | healthy | 0.668 | O |
| 5 | sync | `val/angular_leaf_spot/angular_leaf_spot_val.10.jpg` | angular_leaf_spot | angular_leaf_spot | 0.502 | O |
| 1 | async | `val/bean_rust/bean_rust_val.10.jpg` | bean_rust | bean_rust | 0.430 | O |
| 2 | async | `val/healthy/healthy_val.10.jpg` | healthy | healthy | 0.717 | O |
| 3 | async | `val/angular_leaf_spot/angular_leaf_spot_val.11.jpg` | angular_leaf_spot | bean_rust | 0.448 | X |
| 4 | async | `val/bean_rust/bean_rust_val.11.jpg` | bean_rust | healthy | 0.493 | X |
| 5 | async | `val/healthy/healthy_val.11.jpg` | healthy | healthy | 0.744 | O |

12장 중 6장 일치 — 동작 확인용 표본이며 정확도 지표가 아님. 증빙 [api_responses.json](evidence/api_responses.json)

> **Test 사용 기록:** 처음 02 방식(전부 Docker)으로 측정할 때 Test 이미지 15장을 시연·측정에 썼고 예측 결과를 봤다(모델·설정 선택에는 쓰지 않음). 이후 시연·측정은 모두 Validation 이미지로 바꿨다 ([E-05](07_기능테스트_오류분석.md)). 기록: [docker_mode_02/api_responses.json](evidence/docker_mode_02/api_responses.json)

## 6. 개선 실험 (평가 가이드 6-1, 같은 Validation 133장 기준)

| 실험 | 제공 코드 변경 | 실행 설정 | Validation Accuracy | 상태 |
|---|---|---|---:|---|
| E0: Head-only 기준선 | 없음 | `--freeze-backbone`, 3 Epoch, lr 2e-4 | 0.7669 | 실행 (필수) |
| E1: Head-only 10 Epoch | 없음 | `--freeze-backbone --epochs 10` → `artifacts/beans_resnet18_head10` | 미측정 | 실행 예정 |
| E2: Full Fine-tuning | 없음 | 옵션 제외, `--lr 0.00005` → `artifacts/beans_resnet18_full` | 미측정 | 실행 예정 (선택) |

Epoch·학습률 변경은 실행 옵션 차이이며 제공 코드 수정이 아니다. 각 결과는 별도 폴더에 저장해 E0를 덮어쓰지 않는다. 최종 모델은 Validation으로만 고르고, Test는 그 뒤 E0와 최종 모델을 한 번에 측정한다.

## 7. 결과 판정과 한계

- 완료: 제공 코드로 Head-only Fine-tuning 실행, 3클래스 모델 생성, 서비스에서 이 모델 사용 확인
- 1순위 점수가 낮은 편(틀린 예측 평균 0.504) — 확신이 약한 예측이 많음
- 한계: Test Accuracy·개선 실험 미완료, 거의 같은 사진 중복은 미점검, 단일 학습 seed
