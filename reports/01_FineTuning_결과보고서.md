# 산출물 1. Fine-tuning 결과보고서

- 기준 모델: microsoft/resnet-18
- 학습 방식: Head-only (Backbone freeze)
- 모델 저장 위치: artifacts/beans_resnet18/
- 실험 상태: Head-only 학습 완료 (2026-11-04)

## 1. 데이터 구성

출처: Hugging Face [AI-Lab-Makerere/beans](https://huggingface.co/datasets/AI-Lab-Makerere/beans) `data/train.zip`, `data/validation.zip`, `data/test.zip` (2026-11-04 다운로드)

| 클래스 | Train | Validation | Test |
|---|---:|---:|---:|
| angular_leaf_spot | 345 | 44 | 43 |
| bean_rust | 348 | 45 | 43 |
| healthy | 341 | 44 | 42 |
| 합계 | 1,034 | 133 | 128 |

- 원본 보존: `beans_source/zips/`(zip 원본), `beans_source/train|validation|test/`(압축 해제본). Git 제외
- 원본 폴더 → 코드 폴더: `train` → `dataset/train` / `validation` → `dataset/val` / `test` → `dataset/test`
- 압축 해제 시 제외: `train/healthy/healthy_train.120tore` 1개 — 이미지가 아닌 macOS `.DS_Store` 파일(파일 시작 `Bud1`). 데이터 카드 수량(Train 1,034)과 일치
- 클래스 균형: split마다 세 클래스 수가 거의 같음 (차이 최대 4장)
- 중복·누출 점검: 전체 1,295장의 SHA-256 해시 비교 → 같은 내용의 파일 0쌍, split 간 중복 0쌍, 파일명 중복 0건
- 한계: 해시 비교는 **완전히 같은 파일**만 찾는다. 같은 잎을 다시 찍은 사진(거의 같은 이미지)은 이 방법으로 확인되지 않음 — 눈으로 일부 확인 필요

zip 원본 SHA-256:

```text
ca67b15d960d1e2fd9d23fd8498ce86818ead90755c630a43baf19ec4af09312  test.zip
284fe8456ce20687f4367ae7ad94a64577e7f9fde2c2c6b1c74340ab5dc82715  train.zip
90b7aa1c26d91d9afff07a30bbc67a5ea34f1f1397f068d8675be09d7d0c602d  validation.zip
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
| 학습 장치 | GPU (NVIDIA GeForce RTX 3060, WSL2) — 제공 코드가 CUDA를 자동 사용 |
| 환경 | Python 3.11.17, torch 2.15.0+cu132, transformers 4.57.6 |

실행 명령 (제공 문서 그대로):

```bash
python -m training.finetune --data dataset --output artifacts/beans_resnet18 --epochs 3 --batch-size 8 --freeze-backbone
```

출력층 교체 확인 (학습 로그): `classifier.1.weight` `[1000, 512]` → `[3, 512]`, `classifier.1.bias` `[1000]` → `[3]` 가 새로 초기화됨

## 3. 학습 결과 (`training_report.json`에서 옮김)

| Epoch | Train Loss | Validation Accuracy |
|---|---:|---:|
| 1 | 0.9924 | 0.6617 |
| 2 | 0.8108 | 0.7669 |
| 3 | 0.7078 | 0.7669 |

- Best Validation Accuracy: **0.7669** (133장 중 102장)
- 저장된 모델: **Epoch 2** 가중치 — 제공 코드는 `acc > best_acc`일 때만 저장하므로, 같은 값인 Epoch 3은 저장하지 않음
- Train Loss는 3 Epoch 동안 계속 감소 → 3 Epoch에서 아직 수렴하지 않았을 가능성
- Test Accuracy: 미측정 (제공 코드에 Test 평가 절차 없음)
- 클래스별 Precision·Recall·혼동행렬: 아래 3-1 (Val 기준, 추가 스크립트)
- 증빙: [학습 로그](evidence/train_log_head_only.txt), [training_report.json 사본](data/training_report_head_only.json)

### 3-1. Validation 세부 평가 (추가 스크립트 `training/evaluate.py`)

제공 코드는 정확도만 출력하므로, 같은 데이터 읽기·전처리(`finetune.py`의 `FolderImages`)를 그대로 쓰는 평가 스크립트를 **새 파일로 추가**했다. 제공 코드는 고치지 않았다.

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

- 확인: Accuracy 0.7669(102/133)가 학습 로그의 Best Val Accuracy와 같음 → 평가 조건이 학습 때와 일치
- 가장 약한 클래스: **bean_rust** (Recall 0.6444). 녹병 잎 45장 중 8장은 angular_leaf_spot, 8장은 healthy로 예측
- 많이 헷갈린 쌍: angular_leaf_spot→bean_rust 8장, bean_rust→healthy 8장, bean_rust→angular_leaf_spot 8장, angular_leaf_spot→healthy 3장
- healthy는 Recall 0.9091로 가장 잘 맞힘. 병든 잎을 healthy로 놓친 경우는 11장(angular 3 + rust 8)
- 틀린 예측의 평균 1순위 점수(0.504)가 맞힌 예측(0.6071)보다 낮음 → 점수가 낮으면 사람이 확인하는 규칙의 근거가 될 수 있음 (제안, 미구현)
- 틀린 이미지 31장 목록: [eval_beans_resnet18_val.json](data/eval_beans_resnet18_val.json) `errors`
- Test: **아직 쓰지 않음.** 개선 실험을 Val로 마친 뒤 최종 모델을 정하고 `--split test --final`로 한 번만 평가한다. Test 실행 기록은 `reports/data/test_runs.log`에 자동으로 남는다

## 4. 생성 파일 확인

| 파일 | 크기 |
|---|---:|
| config.json (`id2label`: 0 angular_leaf_spot, 1 bean_rust, 2 healthy) | 808 B |
| model.safetensors | 44.8 MB |
| preprocessor_config.json | 352 B |
| training_report.json | 468 B |

모델 파일은 Git에 올리지 않음 (`artifacts/` 제외).

## 5. 서비스 연결 확인

`.env`의 `MODEL_PATH=artifacts/beans_resnet18`로 web·worker를 띄우고 API로 확인 (2026-11-04).

- 응답 `model_id`가 `artifacts/beans_resnet18`, 라벨은 `angular_leaf_spot`·`bean_rust`·`healthy` 3개만 나옴 → 원본 1,000클래스가 아니라 학습한 모델이 쓰임
- 서비스 측정에 쓴 Test 이미지 12장의 예측 (캐시 HIT 중복 제외):

| run_id | 경로 | 파일 | 정답 | 예측 | 점수 | 일치 |
|---:|---|---|---|---|---:|:-:|
| 0 | sync | `test/angular_leaf_spot/angular_leaf_spot_test.0.jpg` | angular_leaf_spot | angular_leaf_spot | 0.462 | O |
| 0 | async | `test/bean_rust/bean_rust_test.0.jpg` | bean_rust | bean_rust | 0.605 | O |
| 1 | sync | `test/healthy/healthy_test.0.jpg` | healthy | healthy | 0.637 | O |
| 2 | sync | `test/angular_leaf_spot/angular_leaf_spot_test.1.jpg` | angular_leaf_spot | angular_leaf_spot | 0.518 | O |
| 3 | sync | `test/bean_rust/bean_rust_test.1.jpg` | bean_rust | bean_rust | 0.515 | O |
| 4 | sync | `test/healthy/healthy_test.1.jpg` | healthy | healthy | 0.817 | O |
| 5 | sync | `test/angular_leaf_spot/angular_leaf_spot_test.10.jpg` | angular_leaf_spot | angular_leaf_spot | 0.515 | O |
| 1 | async | `test/bean_rust/bean_rust_test.10.jpg` | bean_rust | angular_leaf_spot | 0.383 | X |
| 2 | async | `test/healthy/healthy_test.10.jpg` | healthy | bean_rust | 0.500 | X |
| 3 | async | `test/angular_leaf_spot/angular_leaf_spot_test.11.jpg` | angular_leaf_spot | angular_leaf_spot | 0.580 | O |
| 4 | async | `test/bean_rust/bean_rust_test.11.jpg` | bean_rust | bean_rust | 0.591 | O |
| 5 | async | `test/healthy/healthy_test.11.jpg` | healthy | healthy | 0.848 | O |

12장 중 10장 일치. **이것은 동작 확인용 표본이지 Test Accuracy가 아니다** (128장 전체 평가는 하지 않음). 증빙: [api_responses.json](evidence/api_responses.json)

## 6. 결과 판정과 한계

- 판정: 제공 코드로 Head-only Fine-tuning을 실행해 3클래스 모델을 만들었고, 서비스에서 이 모델이 쓰이는 것을 확인함
- Best Validation Accuracy 0.7669는 3 Epoch, Backbone 고정 조건의 값. Train Loss가 계속 내려가는 중이라 Epoch를 늘리면 바뀔 수 있음 (미실험)
- 1순위 점수가 0.38~0.85로 낮은 편 — 확신이 약한 예측이 많음. 서비스 표본에서 틀린 2장은 점수 0.383, 0.500
- 한계: Test Accuracy와 Full Fine-tuning 비교는 미측정. 클래스별 지표·혼동행렬은 Val 기준으로만 측정
