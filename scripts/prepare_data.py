"""beans 데이터를 받아 원본은 beans_source/에 보존하고, 제공 코드용 dataset/에 배치한다. (제공 코드 아님 — 추가 스크립트)

사용 (프로젝트 루트에서):
  python scripts/prepare_data.py --download     # Hugging Face에서 zip 3개를 받아서 배치
  python scripts/prepare_data.py                # beans_source/zips/에 zip이 이미 있을 때

- 원본 폴더 validation → 코드 폴더 dataset/val (제공 finetune.py가 val을 읽음)
- 이미지가 아닌 파일(.DS_Store 등)은 건너뛰고 목록을 남김
- 클래스별 장수와 SHA-256 중복·split 간 누출을 검사해 reports/data/dataset_check.json에 저장
"""
import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

HF = "https://huggingface.co/datasets/AI-Lab-Makerere/beans/resolve/main/data/{}.zip"
CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SPLITS = {"train": "train", "validation": "val", "test": "test"}  # 원본 → 코드 폴더


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--source", default="beans_source")
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--report", default="reports/data/dataset_check.json")
    args = ap.parse_args()
    src, ds = Path(args.source), Path(args.dataset)
    zips = src / "zips"
    zips.mkdir(parents=True, exist_ok=True)

    if args.download:
        for split in SPLITS:
            dest = zips / f"{split}.zip"
            if not dest.exists():
                print("download", HF.format(split))
                urllib.request.urlretrieve(HF.format(split), dest)
    zip_hash = {f"{s}.zip": sha256(zips / f"{s}.zip") for s in SPLITS}

    skipped = []
    for split in SPLITS:
        out = src / split
        if out.exists():
            shutil.rmtree(out)
        with zipfile.ZipFile(zips / f"{split}.zip") as z:
            for info in z.infolist():
                name = PurePosixPath(info.filename)
                if info.is_dir() or name.is_absolute() or ".." in name.parts:
                    continue
                parts = list(name.parts)
                idx = next((i for i, p in enumerate(parts) if p in CLASSES), None)
                if idx is None or Path(parts[-1]).suffix.lower() not in EXTS:
                    skipped.append(info.filename)
                    continue
                dest = out / parts[idx] / parts[-1]
                dest.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as r, open(dest, "wb") as w:
                    shutil.copyfileobj(r, w)

    if ds.exists():
        shutil.rmtree(ds)
    counts, hashes = {}, defaultdict(list)
    for split, code in SPLITS.items():
        shutil.copytree(src / split, ds / code)
        c = Counter()
        for f in sorted((ds / code).rglob("*")):
            if f.is_file():
                c[f.parent.name] += 1
                hashes[sha256(f)].append(f"{code}/{f.parent.name}/{f.name}")
        counts[code] = {k: c[k] for k in CLASSES}

    dups = [v for v in hashes.values() if len(v) > 1]
    cross = [v for v in dups if len({p.split("/")[0] for p in v}) > 1]
    names = Counter(p.split("/")[-1] for v in hashes.values() for p in v)
    result = {
        "source": "https://huggingface.co/datasets/AI-Lab-Makerere/beans (data/*.zip)",
        "mapping": SPLITS,
        "zip_sha256": zip_hash,
        "counts": counts,
        "totals": {k: sum(v.values()) for k, v in counts.items()},
        "skipped_non_image": skipped,
        "duplicate_groups": dups,
        "cross_split_duplicates": cross,
        "same_filename_count": sum(1 for k in names.values() if k > 1),
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["counts", "totals", "skipped_non_image"]}, ensure_ascii=False, indent=1))
    print(f"중복 묶음 {len(dups)}, split 간 중복 {len(cross)}, 파일명 겹침 {result['same_filename_count']} → {args.report}")


if __name__ == "__main__":
    main()
