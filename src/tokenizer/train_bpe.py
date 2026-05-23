"""Train a BPE tokenizer for FarolLM.

Trains a multilingual BPE tokenizer using HuggingFace Tokenizers library.
Designed for pt + en + code coverage.

Usage:
    python -m src.tokenizer.train_bpe \
        --input data/raw/sample.txt \
        --output tokenizer/ \
        --vocab-size 32768
"""

import argparse
import os
from pathlib import Path

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers, decoders


def create_tokenizer(vocab_size: int = 32768) -> tuple[Tokenizer, trainers.BpeTrainer]:
    tokenizer = Tokenizer(models.BPE())

    tokenizer.normalizer = normalizers.Sequence([
        normalizers.NFC(),
        normalizers.Replace(r"\s+", " "),
    ])

    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()

    special_tokens = [
        "<|begin_of_text|>",
        "<|end_of_text|>",
        "<|pad|>",
        "<|unk|>",
    ]

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=special_tokens,
        show_progress=True,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )

    return tokenizer, trainer


def train_from_files(
    input_paths: list[str],
    output_dir: str,
    vocab_size: int = 32768,
) -> Tokenizer:
    tokenizer, trainer = create_tokenizer(vocab_size)

    print(f"Training BPE tokenizer (vocab_size={vocab_size})...")
    print(f"  Input files: {input_paths}")

    tokenizer.train(input_paths, trainer)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "tokenizer.json")
    tokenizer.save(out_path)
    print(f"  Saved to: {out_path}")
    print(f"  Vocab size: {tokenizer.get_vocab_size()}")

    test_sentences = [
        "O FarolLM e um modelo de linguagem treinado do zero.",
        "The quick brown fox jumps over the lazy dog.",
        "def hello_world():\n    print('Hello, world!')",
        "A UFPE fica em Recife, Pernambuco, Brasil.",
    ]
    print("\n  Sample encodings:")
    for sent in test_sentences:
        encoded = tokenizer.encode(sent)
        tokens = encoded.tokens[:20]
        print(f"    [{len(encoded.ids):>3d} tokens] {sent[:60]}")
        print(f"              {' '.join(tokens[:15])}...")

    return tokenizer


def train_from_iterator(
    iterator,
    output_dir: str,
    vocab_size: int = 32768,
) -> Tokenizer:
    tokenizer, trainer = create_tokenizer(vocab_size)
    tokenizer.train_from_iterator(iterator, trainer)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "tokenizer.json")
    tokenizer.save(out_path)
    return tokenizer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train BPE tokenizer for FarolLM")
    parser.add_argument("--input", nargs="+", required=True, help="Input text files")
    parser.add_argument("--output", default="tokenizer/", help="Output directory")
    parser.add_argument("--vocab-size", type=int, default=32768)
    args = parser.parse_args()

    train_from_files(args.input, args.output, args.vocab_size)
