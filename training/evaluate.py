"""학습된 모델을 Val 또는 Test 폴더로 평가한다 (제공 코드 외 추가 파일).

예:
  python -m training.evaluate --model artifacts/beans_resnet18 --split val
  python -m training.evaluate --model artifacts/beans_resnet18 --split test --final

- 전처리·데이터 읽기는 training/finetune.py의 FolderImages를 그대로 쓴다 (학습 때와 같은 조건).
- Test는 최종 모델을 고른 뒤에만 쓴다. --final 없이는 실행되지 않고, 실행할 때마다
  reports/data/test_runs.log에 한 줄씩 남긴다 (Test를 몇 번 봤는지 숨기지 않기 위해).
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import AutoImageProcessor, AutoModelForImageClassification

from training.finetune import FolderImages


def evaluate(model_dir: Path, data_dir: Path, batch_size: int):
    processor = AutoImageProcessor.from_pretrained(str(model_dir))
    model = AutoModelForImageClassification.from_pretrained(str(model_dir))
    classes = [model.config.id2label[i] for i in range(len(model.config.id2label))]
    folders = sorted(p.name for p in data_dir.iterdir() if p.is_dir())
    if folders != sorted(classes):
        raise ValueError(f"폴더 {folders}와 모델 라벨 {classes}가 다릅니다.")

    dataset = FolderImages(data_dir, classes, processor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()

    preds, scores = [], []
    with torch.no_grad():
        for batch in loader:
            probs = model(pixel_values=batch["pixel_values"].to(device)).logits.softmax(dim=-1).cpu()
            top = probs.max(dim=-1)
            preds += top.indices.tolist()
            scores += top.values.tolist()

    labels = [label for _, label in dataset.records]
    n = len(classes)
    cm = [[0] * n for _ in range(n)]  # 행 = 정답, 열 = 예측
    for t, p in zip(labels, preds):
        cm[t][p] += 1

    per_class = {}
    for i, name in enumerate(classes):
        tp = cm[i][i]
        pred_i = sum(cm[r][i] for r in range(n))
        true_i = sum(cm[i])
        precision = tp / pred_i if pred_i else 0.0
        recall = tp / true_i if true_i else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[name] = {"precision": round(precision, 4), "recall": round(recall, 4),
                           "f1": round(f1, 4), "support": true_i}

    correct = sum(t == p for t, p in zip(labels, preds))
    right = [s for t, p, s in zip(labels, preds, scores) if t == p]
    wrong = [s for t, p, s in zip(labels, preds, scores) if t != p]
    errors = [{"file": f"{path.parent.name}/{path.name}", "true": classes[t], "pred": classes[p], "score": round(s, 4)}
              for (path, t), p, s in zip(dataset.records, preds, scores) if t != p]

    return {
        "model": str(model_dir),
        "data": str(data_dir),
        "device": str(device),
        "evaluated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "count": len(labels),
        "correct": correct,
        "accuracy": round(correct / len(labels), 4),
        "macro_f1": round(sum(c["f1"] for c in per_class.values()) / n, 4),
        "per_class": per_class,
        "confusion_matrix": {"labels": classes, "rows_true_cols_pred": cm},
        "mean_top1_score": {"correct": round(sum(right) / len(right), 4) if right else None,
                            "wrong": round(sum(wrong) / len(wrong), 4) if wrong else None},
        "errors": errors,
    }


def to_markdown(r: dict) -> str:
    classes = r["confusion_matrix"]["labels"]
    lines = [f"- 데이터: `{r['data']}` {r['count']}장 / 모델: `{r['model']}` / 장치: {r['device']}",
             f"- Accuracy: **{r['accuracy']}** ({r['correct']}/{r['count']}), Macro F1: {r['macro_f1']}",
             f"- 평균 1순위 점수: 맞힌 것 {r['mean_top1_score']['correct']}, 틀린 것 {r['mean_top1_score']['wrong']}",
             "", "| 클래스 | Precision | Recall | F1 | 장수 |", "|---|---:|---:|---:|---:|"]
    for name, m in r["per_class"].items():
        lines.append(f"| {name} | {m['precision']} | {m['recall']} | {m['f1']} | {m['support']} |")
    lines += ["", "혼동행렬 (행 = 정답, 열 = 예측):", "",
              "| 정답 \\ 예측 | " + " | ".join(classes) + " |", "|---|" + "---:|" * len(classes)]
    for name, row in zip(classes, r["confusion_matrix"]["rows_true_cols_pred"]):
        lines.append(f"| {name} | " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="artifacts/beans_resnet18")
    parser.add_argument("--data", default="dataset")
    parser.add_argument("--split", choices=["val", "test"], default="val")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--out", default=None, help="결과 JSON 경로 (기본: reports/data/eval_<모델폴더>_<split>.json)")
    parser.add_argument("--final", action="store_true", help="Test 평가 허용 (최종 모델을 고른 뒤에만)")
    args = parser.parse_args()

    if args.split == "test" and not args.final:
        parser.error("Test는 최종 모델을 Val로 고른 뒤 한 번만 씁니다. 그때 --final을 붙이세요.")

    model_dir = Path(args.model)
    result = evaluate(model_dir, Path(args.data) / args.split, args.batch_size)
    result["split"] = args.split

    out = Path(args.out or f"reports/data/eval_{model_dir.name}_{args.split}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.split == "test":
        with open(out.parent / "test_runs.log", "a", encoding="utf-8") as log:
            log.write(f"{result['evaluated_at']}\t{model_dir}\taccuracy={result['accuracy']}\n")

    print(to_markdown(result))
    print(f"\n틀린 이미지 {len(result['errors'])}장, 저장: {out}")


if __name__ == "__main__":
    main()
