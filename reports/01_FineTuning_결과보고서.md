# 산출물 1. Fine-tuning 결과보고서

- 기준 모델: microsoft/resnet-18
- 학습 방식: Head-only (Backbone freeze)
- 모델 저장 위치: artifacts/beans_resnet18/
- 실험 상태: 미실행

## 1. 데이터 구성

| 클래스 | Train | Validation | Test |
|---|---:|---:|---:|
| angular_leaf_spot | | | |
| bean_rust | | | |
| healthy | | | |
| 합계 | | | |

- 원본 폴더 → 코드 폴더: train → train / validation → val / test → test
- 중복·누출 점검: (확인 방식과 결과 기입)

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
