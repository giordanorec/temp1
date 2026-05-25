"""Complete data pipeline for FarolLM.

Downloads, filters, deduplicates, and prepares training data.
Supports streaming to avoid downloading full datasets to disk.

Datasets used:
    - FineWeb-2 (HuggingFace): 15T+ tokens, 1000+ languages
      Portuguese subset: ~200B+ tokens
      English subset: massive
    - CulturaX (UoNLP): 6.3T tokens, 167 languages
      Strong Portuguese coverage from mC4 + OSCAR
    - The Stack v2 (BigCode): 4T+ tokens of code, 619 languages

All datasets are on HuggingFace Hub, downloaded via streaming
(no need to download the full dataset first).

Usage:
    # Download balanced corpus for tokenizer training (~1GB)
    python -m src.data.prepare tokenizer-corpus --output data/raw/

    # Download pre-training corpus (~10-50GB, configurable)
    python -m src.data.prepare pretrain-corpus --output data/raw/ --target-gb 10

    # Filter and deduplicate
    python -m src.data.prepare filter --input data/raw/ --output data/filtered/

    # Tokenize filtered corpus
    python -m src.data.prepare tokenize --input data/filtered/ --tokenizer tokenizer/tokenizer.json --output data/tokenized/

    # Full pipeline (download + filter + tokenize)
    python -m src.data.prepare full --target-gb 10
"""

import argparse
import hashlib
import os
import re
import unicodedata

from tqdm import tqdm


# --- Quality filters ---

def is_quality_text(text: str, min_length: int = 200, max_length: int = 100_000) -> bool:
    if len(text) < min_length or len(text) > max_length:
        return False

    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.5:
        return False

    lines = text.split("\n")
    if len(lines) > 0:
        short_lines = sum(1 for l in lines if len(l.strip()) < 10)
        if short_lines / len(lines) > 0.7:
            return False

    words = text.split()
    if len(words) < 20:
        return False
    unique_words = set(w.lower() for w in words)
    if len(unique_words) / len(words) < 0.1:
        return False

    upper_ratio = sum(c.isupper() for c in text) / max(sum(c.isalpha() for c in text), 1)
    if upper_ratio > 0.5:
        return False

    return True


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\t", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()
    return text


# --- Deduplication ---

def compute_hash(text: str) -> str:
    normalized = " ".join(text.lower().split()[:100])
    return hashlib.md5(normalized.encode()).hexdigest()


class ExactDeduplicator:
    def __init__(self):
        self.seen: set[str] = set()

    def is_duplicate(self, text: str) -> bool:
        h = compute_hash(text)
        if h in self.seen:
            return True
        self.seen.add(h)
        return False


# --- Download and prepare ---

def download_and_filter(
    dataset_name: str,
    lang: str,
    output_path: str,
    max_docs: int = 100_000,
    target_bytes: int | None = None,
):
    from datasets import load_dataset

    config_map = {
        "fineweb2": ("HuggingFaceFW/fineweb-2", "text"),
        "culturax": ("uonlp/CulturaX", "text"),
    }

    hf_name, text_field = config_map[dataset_name]
    print(f"Downloading {dataset_name}/{lang} (streaming)...")

    ds = load_dataset(hf_name, name=lang, split="train", streaming=True)
    dedup = ExactDeduplicator()

    written = 0
    skipped_quality = 0
    skipped_dedup = 0
    total_bytes = 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for doc in tqdm(ds, desc=f"{dataset_name}/{lang}", total=max_docs):
            text = doc.get(text_field, "")
            text = clean_text(text)

            if not is_quality_text(text):
                skipped_quality += 1
                continue

            if dedup.is_duplicate(text):
                skipped_dedup += 1
                continue

            f.write(text)
            f.write("\n\n<|end_of_text|>\n\n")
            written += 1
            total_bytes += len(text.encode())

            if written >= max_docs:
                break
            if target_bytes and total_bytes >= target_bytes:
                break

    mb = total_bytes / 1_000_000
    print(f"  {dataset_name}/{lang}: {written:,} docs, {mb:.1f} MB")
    print(f"  Filtered: {skipped_quality:,} quality, {skipped_dedup:,} dedup")
    return output_path


def prepare_tokenizer_corpus(output_dir: str = "data/raw") -> list[str]:
    """Download ~1GB balanced corpus for tokenizer training."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    targets = [
        ("fineweb2", "pt", 30_000),  # ~500MB Portuguese
        ("fineweb2", "en", 25_000),  # ~400MB English
        ("culturax", "pt", 10_000),  # ~100MB more Portuguese
    ]

    for dataset, lang, n_docs in targets:
        path = os.path.join(output_dir, f"{dataset}_{lang}.txt")
        download_and_filter(dataset, lang, path, max_docs=n_docs)
        paths.append(path)

    print(f"\nTokenizer corpus ready in {output_dir}/ ({len(paths)} files)")
    return paths


def prepare_pretrain_corpus(
    output_dir: str = "data/raw",
    target_gb: float = 10.0,
) -> list[str]:
    """Download pre-training corpus with target size."""
    os.makedirs(output_dir, exist_ok=True)
    target_bytes = int(target_gb * 1e9)
    paths = []

    pt_target = int(target_bytes * 0.50)  # 50% Portuguese
    en_target = int(target_bytes * 0.40)  # 40% English
    cx_target = int(target_bytes * 0.10)  # 10% CulturaX Portuguese

    configs = [
        ("fineweb2", "pt", 10_000_000, pt_target),
        ("fineweb2", "en", 10_000_000, en_target),
        ("culturax", "pt", 10_000_000, cx_target),
    ]

    for dataset, lang, max_docs, tbytes in configs:
        path = os.path.join(output_dir, f"pretrain_{dataset}_{lang}.txt")
        download_and_filter(dataset, lang, path, max_docs=max_docs, target_bytes=tbytes)
        paths.append(path)

    total_size = sum(os.path.getsize(p) for p in paths)
    print(f"\nPre-training corpus: {total_size / 1e9:.1f} GB in {output_dir}/")
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare FarolLM training data")
    sub = parser.add_subparsers(dest="command")

    tok = sub.add_parser("tokenizer-corpus", help="Download corpus for tokenizer")
    tok.add_argument("--output", default="data/raw")

    pre = sub.add_parser("pretrain-corpus", help="Download pre-training corpus")
    pre.add_argument("--output", default="data/raw")
    pre.add_argument("--target-gb", type=float, default=10.0)

    args = parser.parse_args()

    if args.command == "tokenizer-corpus":
        prepare_tokenizer_corpus(args.output)
    elif args.command == "pretrain-corpus":
        prepare_pretrain_corpus(args.output, args.target_gb)
    else:
        parser.print_help()
