# 산출물 1. Fine-tuning 결과보고서

- 기준 모델: microsoft/resnet-18
- 학습 방식: Head-only (Backbone freeze)
- 모델 저장 위치: artifacts/beans_resnet18/
- 실험 상태: 미실행

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
| epochs | |
| batch_size | |
| learning_rate | |
| freeze_backbone | |
| seed | 42 (제공 코드) |

## 3. 학습 결과 (`training_report.json`에서 옮김)

| Epoch | Train Loss | Validation Accuracy |
|---|---:|---:|

- Best Validation Accuracy:
- Test Accuracy: 미측정

## 4. 생성 파일 확인

- [ ] config.json
- [ ] model.safetensors
- [ ] preprocessor_config.json
- [ ] training_report.json

## 5. 서비스 연결 확인

## 6. 결과 판정과 한계
