"""Download datasets for FarolLM pre-training.

Supports downloading subsets of FineWeb-2 and CulturaX via
HuggingFace Datasets. Saves as plain text files for tokenizer
training and corpus tokenization.

Usage:
    python -m src.data.download --dataset fineweb2 --lang pt --size 100MB
    python -m src.data.download --dataset culturax --lang pt --size 500MB
    python -m src.data.download --dataset fineweb2 --lang en --size 1GB
"""

import argparse
import os

SIZE_MAP = {
    "10MB": 1_000,
    "100MB": 10_000,
    "500MB": 50_000,
    "1GB": 100_000,
    "5GB": 500_000,
    "10GB": 1_000_000,
}

DATASET_CONFIGS = {
    "fineweb2": {
        "path": "HuggingFaceFW/fineweb-2",
        "text_field": "text",
        "split": "train",
        "streaming": True,
    },
    "culturax": {
        "path": "uonlp/CulturaX",
        "text_field": "text",
        "split": "train",
        "streaming": True,
    },
}


def download(
    dataset_name: str,
    lang: str,
    output_dir: str = "data/raw",
    max_docs: int = 10_000,
    min_length: int = 100,
) -> str:
    from datasets import load_dataset

    config = DATASET_CONFIGS[dataset_name]
    print(f"Downloading {dataset_name} ({lang}), max {max_docs:,} docs...")

    kwargs = {"path": config["path"], "split": config["split"], "streaming": True}

    if dataset_name == "fineweb2":
        kwargs["name"] = lang
    elif dataset_name == "culturax":
        kwargs["name"] = lang

    ds = load_dataset(**kwargs)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{dataset_name}_{lang}.txt")

    count = 0
    total_chars = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for doc in ds:
            text = doc.get(config["text_field"], "")
            if len(text) < min_length:
                continue
            f.write(text.strip())
            f.write("\n\n")
            total_chars += len(text)
            count += 1
            if count % 1000 == 0:
                mb = total_chars / 1_000_000
                print(f"  {count:>8,} docs | {mb:.1f} MB")
            if count >= max_docs:
                break

    mb = total_chars / 1_000_000
    print(f"  Done: {count:,} docs, {mb:.1f} MB -> {out_path}")
    return out_path


def download_all_for_tokenizer(
    output_dir: str = "data/raw",
    pt_docs: int = 50_000,
    en_docs: int = 40_000,
    code_docs: int = 10_000,
) -> list[str]:
    """Download balanced corpus for tokenizer training."""
    paths = []

    print("=== Downloading data for tokenizer training ===\n")

    print("[1/3] Portuguese (FineWeb-2)...")
    paths.append(download("fineweb2", "pt", output_dir, pt_docs))

    print("\n[2/3] English (FineWeb-2)...")
    paths.append(download("fineweb2", "en", output_dir, en_docs))

    print("\n[3/3] Portuguese (CulturaX)...")
    paths.append(download("culturax", "pt", output_dir, code_docs))

    print(f"\n=== Done: {len(paths)} files in {output_dir}/ ===")
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download datasets for FarolLM")
    sub = parser.add_subparsers(dest="command")

    dl = sub.add_parser("single", help="Download a single dataset")
    dl.add_argument("--dataset", choices=list(DATASET_CONFIGS.keys()), required=True)
    dl.add_argument("--lang", required=True, help="Language code (pt, en, etc)")
    dl.add_argument("--output", default="data/raw")
    dl.add_argument("--max-docs", type=int, default=10_000)

    tok = sub.add_parser("tokenizer", help="Download balanced corpus for tokenizer")
    tok.add_argument("--output", default="data/raw")
    tok.add_argument("--pt-docs", type=int, default=50_000)
    tok.add_argument("--en-docs", type=int, default=40_000)

    args = parser.parse_args()

    if args.command == "single":
        download(args.dataset, args.lang, args.output, args.max_docs)
    elif args.command == "tokenizer":
        download_all_for_tokenizer(args.output, args.pt_docs, args.en_docs)
    else:
        parser.print_help()
