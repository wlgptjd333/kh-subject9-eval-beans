"""CNN 점수 + OpenCV HSV 병반 후보 면적비로 '확인 필요(review_required)'를 표시하는 규칙 실험 (제공 코드 외 추가 파일).

평가 가이드 6-2·6-3의 'CNN + Rule' 실험. 모델 라벨은 바꾸지 않고 보류 플래그만 붙인다.

  python scripts/review_rule.py features --model artifacts/beans_resnet18_full --split train
  python scripts/review_rule.py features --model artifacts/beans_resnet18_full --split val
  python scripts/review_rule.py select   --model artifacts/beans_resnet18_full
  python scripts/review_rule.py features --model artifacts/beans_resnet18_full --split test --final
  python scripts/review_rule.py apply    --model artifacts/beans_resnet18_full --split test

- 면적비 기준은 Train의 healthy 이미지 분포에서 정한다 (Val·Test를 보지 않음).
- 점수 기준은 Validation에서 고른다. Test는 규칙을 확정한 뒤 한 번만 적용한다 (test_runs.log 기록).
"""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
DATA = Path("reports/data")
FIG = Path("reports/figures/hsv_examples")

# HSV(OpenCV: H 0~179) — 녹색 잎 구간. 샘플 이미지를 보고 정한 고정값
GREEN_LO, GREEN_HI = (33, 40, 40), (90, 255, 255)
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))


def lesion_features(path: Path, save_to: Path | None = None) -> dict:
    """잎 마스크(녹색 + 내부 구멍 채움) 안에서 녹색이 아닌 픽셀 = 병반 후보."""
    bgr = cv2.imread(str(path))
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    green = cv2.inRange(hsv, GREEN_LO, GREEN_HI)
    green = cv2.morphologyEx(green, cv2.MORPH_OPEN, KERNEL)
    # 잎 영역: 녹색 덩어리 외곽선을 채워서 잎 안의 반점(녹색 아님)도 잎에 포함
    contours, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in contours if cv2.contourArea(c) >= 0.01 * green.size]
    leaf = np.zeros_like(green)
    cv2.drawContours(leaf, big, -1, 255, thickness=cv2.FILLED)
    leaf = cv2.morphologyEx(leaf, cv2.MORPH_CLOSE, KERNEL, iterations=2)
    lesion = cv2.bitwise_and(leaf, cv2.bitwise_not(green))
    lesion = cv2.morphologyEx(lesion, cv2.MORPH_OPEN, KERNEL)
    n_spots = len(cv2.findContours(lesion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
    leaf_px, lesion_px = int((leaf > 0).sum()), int((lesion > 0).sum())
    if save_to is not None:
        over = bgr.copy()
        over[lesion > 0] = (0, 0, 255)
        edge = cv2.Canny(leaf, 50, 150)
        over[edge > 0] = (255, 255, 0)
        cv2.imwrite(str(save_to), np.hstack([bgr, over]))
    return {"leaf_ratio": round(leaf_px / green.size, 4),
            "lesion_ratio": round(lesion_px / leaf_px, 4) if leaf_px else None,
            "spots": n_spots}


def cnn_scores(model_dir: Path, data_dir: Path):
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoImageProcessor, AutoModelForImageClassification
    from training.finetune import FolderImages

    processor = AutoImageProcessor.from_pretrained(str(model_dir))
    model = AutoModelForImageClassification.from_pretrained(str(model_dir))
    classes = [model.config.id2label[i] for i in range(len(model.config.id2label))]
    ds = FolderImages(data_dir, classes, processor)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(dev).eval()
    probs = []
    with torch.no_grad():
        for b in DataLoader(ds, batch_size=32, shuffle=False):
            probs += model(pixel_values=b["pixel_values"].to(dev)).logits.softmax(-1).cpu().tolist()
    return classes, ds.records, probs


def csv_path(model, split):
    return DATA / f"review_features_{Path(model).name}_{split}.csv"


def cmd_features(a):
    if a.split == "test" and not a.final:
        sys.exit("Test는 규칙을 Val로 확정한 뒤 --final로 한 번만 씁니다.")
    classes, records, probs = cnn_scores(Path(a.model), Path("dataset") / a.split)
    rows = []
    for (path, t), p in zip(records, probs):
        k = int(np.argmax(p))
        rows.append({"file": f"{path.parent.name}/{path.name}", "true": classes[t], "pred": classes[k],
                     "score": round(p[k], 4), **{f"p_{c}": round(v, 4) for c, v in zip(classes, p)},
                     **lesion_features(path)})
    out = csv_path(a.model, a.split)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    if a.split == "test":
        with open(DATA / "test_runs.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now().astimezone().isoformat(timespec='seconds')}\t{a.model}\treview_rule features (CNN 점수+HSV, 규칙 확정 후)\n")
    acc = sum(r["true"] == r["pred"] for r in rows) / len(rows)
    print(f"{out}: {len(rows)}장, CNN accuracy {acc:.4f}")


def load(model, split):
    with open(csv_path(model, split), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["score"] = float(r["score"]); r["lesion_ratio"] = float(r["lesion_ratio"] or 0)
    return rows


def flag(r, t_score, t_ratio):
    """확인 필요: CNN 확신이 낮거나, healthy로 예측했는데 병반 후보가 많을 때."""
    return r["score"] < t_score or (r["pred"] == "healthy" and r["lesion_ratio"] > t_ratio)


def summarize(rows, t_score, t_ratio):
    n = len(rows)
    wrong = [r for r in rows if r["true"] != r["pred"]]
    held = [r for r in rows if flag(r, t_score, t_ratio)]
    auto = [r for r in rows if not flag(r, t_score, t_ratio)]
    caught = [r for r in wrong if flag(r, t_score, t_ratio)]
    return {"count": n, "model_accuracy": round(1 - len(wrong) / n, 4), "errors": len(wrong),
            "held": len(held), "hold_rate": round(len(held) / n, 4),
            "errors_caught": len(caught),
            "auto_count": len(auto),
            "auto_accuracy": round(sum(r["true"] == r["pred"] for r in auto) / len(auto), 4) if auto else None,
            "errors_passed": len(wrong) - len(caught)}


def ratio_threshold(model):
    train = load(model, "train")
    healthy = np.array([r["lesion_ratio"] for r in train if r["true"] == "healthy"])
    diseased = np.array([r["lesion_ratio"] for r in train if r["true"] != "healthy"])
    return float(np.percentile(healthy, 95)), {
        "train_healthy_median": round(float(np.median(healthy)), 4),
        "train_healthy_p95": round(float(np.percentile(healthy, 95)), 4),
        "train_diseased_median": round(float(np.median(diseased)), 4),
        "train_diseased_over_p95": round(float((diseased > np.percentile(healthy, 95)).mean()), 4)}


def cmd_select(a):
    t_ratio, stats = ratio_threshold(a.model)
    val = load(a.model, "val")
    grid = []
    for t in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        for use_ratio in (False, True):
            s = summarize(val, t, t_ratio if use_ratio else 9.9)
            grid.append({"score_threshold": t, "use_lesion_rule": use_ratio, **s})
    # 선정: 보류율 10% 이하에서 잡은 오류가 가장 많은 것, 같으면 보류율이 낮은 것
    ok = [g for g in grid if g["hold_rate"] <= a.max_hold]
    best = max(ok, key=lambda g: (g["errors_caught"], -g["hold_rate"]))
    res = {"model": a.model, "selected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
           "ratio_threshold_from_train": round(t_ratio, 4), "train_ratio_stats": stats,
           "criterion": f"Val 보류율 <= {a.max_hold}에서 잡은 오류 최대, 같으면 보류율 최소",
           "selected": {"score_threshold": best["score_threshold"], "use_lesion_rule": best["use_lesion_rule"]},
           "val_grid": grid}
    out = DATA / f"review_rule_{Path(a.model).name}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "val_grid"}, ensure_ascii=False, indent=1))
    for g in grid:
        print(g)
    # Val 오류 이미지 마스크 예시 저장
    FIG.mkdir(parents=True, exist_ok=True)
    for r in [r for r in val if r["true"] != r["pred"]][:6]:
        lesion_features(Path("dataset/val") / r["file"], FIG / f"{Path(a.model).name}_{Path(r['file']).stem}.jpg")


def cmd_apply(a):
    rule = json.loads((DATA / f"review_rule_{Path(a.model).name}.json").read_text(encoding="utf-8"))
    sel = rule["selected"]
    t_ratio = rule["ratio_threshold_from_train"] if sel["use_lesion_rule"] else 9.9
    rows = load(a.model, a.split)
    s = summarize(rows, sel["score_threshold"], t_ratio)
    rule.setdefault("applied", {})[a.split] = s
    (DATA / f"review_rule_{Path(a.model).name}.json").write_text(json.dumps(rule, ensure_ascii=False, indent=2), encoding="utf-8")
    print(a.split, s)
    for r in rows:
        if r["true"] != r["pred"]:
            print("  error", r["file"], r["pred"], r["score"], r["lesion_ratio"], "held" if flag(r, sel["score_threshold"], t_ratio) else "passed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["features", "select", "apply"])
    p.add_argument("--model", default="artifacts/beans_resnet18_full")
    p.add_argument("--split", choices=["train", "val", "test"], default="val")
    p.add_argument("--final", action="store_true")
    p.add_argument("--max-hold", type=float, default=0.10)
    a = p.parse_args()
    {"features": cmd_features, "select": cmd_select, "apply": cmd_apply}[a.cmd](a)
