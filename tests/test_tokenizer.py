"""Tests for BPE tokenizer training and usage."""

import os
import tempfile

from src.tokenizer.train_bpe import create_tokenizer, train_from_iterator


SAMPLE_TEXTS = [
    "O FarolLM e um modelo de linguagem multilingual.",
    "The Transformer architecture revolutionized NLP.",
    "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "A universidade federal de Pernambuco fica em Recife.",
    "Machine learning models require large datasets for training.",
    "import torch\nimport torch.nn as nn",
] * 50  # repeat for minimum frequency


def test_create_tokenizer():
    tokenizer, trainer = create_tokenizer(vocab_size=256)
    assert tokenizer is not None
    assert trainer is not None


def test_train_from_iterator():
    with tempfile.TemporaryDirectory() as tmpdir:
        tokenizer = train_from_iterator(
            iterator=SAMPLE_TEXTS,
            output_dir=tmpdir,
            vocab_size=256,
        )
        assert tokenizer.get_vocab_size() <= 300  # 256 byte alphabet + special tokens + merges
        assert os.path.exists(os.path.join(tmpdir, "tokenizer.json"))


def test_encode_decode_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        tokenizer = train_from_iterator(
            iterator=SAMPLE_TEXTS,
            output_dir=tmpdir,
            vocab_size=256,
        )
        text = "O FarolLM e um modelo de linguagem."
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded.ids)
        assert decoded == text


def test_special_tokens():
    with tempfile.TemporaryDirectory() as tmpdir:
        tokenizer = train_from_iterator(
            iterator=SAMPLE_TEXTS,
            output_dir=tmpdir,
            vocab_size=256,
        )
        bos = tokenizer.token_to_id("<|begin_of_text|>")
        eos = tokenizer.token_to_id("<|end_of_text|>")
        assert bos is not None
        assert eos is not None
        assert bos != eos


def test_multilingual_encoding():
    with tempfile.TemporaryDirectory() as tmpdir:
        tokenizer = train_from_iterator(
            iterator=SAMPLE_TEXTS,
            output_dir=tmpdir,
            vocab_size=256,
        )
        pt = tokenizer.encode("modelo de linguagem")
        en = tokenizer.encode("language model")
        assert len(pt.ids) > 0
        assert len(en.ids) > 0
