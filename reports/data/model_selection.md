# 최종 모델 선정 기록 (Test 평가 전)

- 작성: 2026-11-04, **Test split을 평가하기 전에** 커밋한다 (Git 이력으로 순서 확인 가능)
- 기준: 같은 Validation 133장에서 Accuracy가 가장 높은 모델, 같으면 Macro F1
- 원본: `eval_beans_resnet18_val.json`, `eval_beans_resnet18_head10_val.json`, `eval_beans_resnet18_full_val.json`

| 실험 | 설정 | Best Epoch | Val Accuracy | Macro F1 | bean_rust Recall |
|---|---|---:|---:|---:|---:|
| E0 Head-only | `--freeze-backbone`, 3 Epoch, lr 2e-4 | 2 | 0.7669 | 0.764 | 0.6444 |
| E1 Head-only 10 Epoch | `--freeze-backbone`, 10 Epoch, lr 2e-4 | 8 | 0.8947 | 0.8953 | 0.8667 |
| E2 Full Fine-tuning | 옵션 없음(전체 학습), 5 Epoch, lr 5e-5 | 4 | **0.9850** | **0.985** | **0.9556** |

**선정: E2 `artifacts/beans_resnet18_full`.**

Test 평가 계획 (각 1회, `python -m training.evaluate --split test --final`):
- E0 `artifacts/beans_resnet18` — 필수 기준선, 서비스 모델
- E2 `artifacts/beans_resnet18_full` — 최종 선정 모델

E1은 선정되지 않았으므로 Test에 쓰지 않는다. Test 결과를 보고 모델·설정을 바꾸지 않는다.
