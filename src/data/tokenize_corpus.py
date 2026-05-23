"""Tokenize a text corpus and save as numpy memmap for training.

Reads text files, tokenizes with a trained BPE tokenizer, and writes
the token IDs to a binary file (numpy memmap, uint16).

Usage:
    python -m src.data.tokenize_corpus \
        --tokenizer tokenizer/tokenizer.json \
        --input data/raw/ \
        --output data/tokenized/train.bin
"""

import argparse
import os
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer


def tokenize_file(tokenizer: Tokenizer, path: str) -> list[int]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    encoded = tokenizer.encode(text)
    return encoded.ids


def tokenize_directory(
    tokenizer_path: str,
    input_dir: str,
    output_path: str,
    file_extensions: tuple[str, ...] = (".txt", ".md"),
) -> int:
    tokenizer = Tokenizer.from_file(tokenizer_path)
    bos_id = tokenizer.token_to_id("<|begin_of_text|>")
    eos_id = tokenizer.token_to_id("<|end_of_text|>")

    all_ids: list[int] = []
    files = sorted(Path(input_dir).rglob("*"))
    files = [f for f in files if f.suffix in file_extensions and f.is_file()]

    print(f"Tokenizing {len(files)} files from {input_dir}...")

    for i, fpath in enumerate(files):
        ids = tokenize_file(tokenizer, str(fpath))
        if bos_id is not None:
            all_ids.append(bos_id)
        all_ids.extend(ids)
        if eos_id is not None:
            all_ids.append(eos_id)

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(files)} files, {len(all_ids):,} tokens so far")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    arr = np.array(all_ids, dtype=np.uint16)
    arr.tofile(output_path)

    print(f"  Total: {len(all_ids):,} tokens -> {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")

    return len(all_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tokenize corpus for FarolLM")
    parser.add_argument("--tokenizer", required=True, help="Path to tokenizer.json")
    parser.add_argument("--input", required=True, help="Input directory with text files")
    parser.add_argument("--output", required=True, help="Output .bin file path")
    args = parser.parse_args()

    tokenize_directory(args.tokenizer, args.input, args.output)
