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
- 클래스별 Precision·Recall·혼동행렬: 미측정 (제공 코드가 계산하지 않음)
- 증빙: [학습 로그](evidence/train_log_head_only.txt), [training_report.json 사본](data/training_report_head_only.json)

## 4. 생성 파일 확인

| 파일 | 크기 |
|---|---:|
| config.json (`id2label`: 0 angular_leaf_spot, 1 bean_rust, 2 healthy) | 808 B |
| model.safetensors | 44.8 MB |
| preprocessor_config.json | 352 B |
| training_report.json | 468 B |

모델 파일은 Git에 올리지 않음 (`artifacts/` 제외).

## 5. 서비스 연결 확인

## 6. 결과 판정과 한계
