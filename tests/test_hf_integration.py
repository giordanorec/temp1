"""Tests for HuggingFace integration (save/load)."""

import os
import tempfile

import torch

from src.model.farol import FarolConfig, FarolLM
from src.model.hf_integration import save_pretrained, load_pretrained


def test_save_and_load():
    config = FarolConfig(
        vocab_size=512, hidden_size=64, intermediate_size=176,
        num_layers=2, num_heads=4, num_kv_heads=2, max_seq_len=128,
    )
    model = FarolLM(config)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_pretrained(model, config, tmpdir)

        assert os.path.exists(os.path.join(tmpdir, "config.json"))
        assert os.path.exists(os.path.join(tmpdir, "model.pt"))
        assert os.path.exists(os.path.join(tmpdir, "README.md"))

        loaded_model, loaded_config = load_pretrained(tmpdir)
        assert loaded_config.vocab_size == config.vocab_size
        assert loaded_config.num_layers == config.num_layers

        x = torch.randint(0, 512, (1, 32))
        with torch.no_grad():
            logits_orig, _ = model(x)
            logits_loaded, _ = loaded_model(x)
        assert torch.allclose(logits_orig, logits_loaded, atol=1e-5)


def test_gradient_checkpointing():
    config = FarolConfig(
        vocab_size=512, hidden_size=64, intermediate_size=176,
        num_layers=4, num_heads=4, num_kv_heads=2, max_seq_len=128,
    )
    model = FarolLM(config)
    model.enable_gradient_checkpointing()
    model.train()

    x = torch.randint(0, 512, (2, 32))
    y = torch.randint(0, 512, (2, 32))
    _, loss = model(x, y)
    loss.backward()

    for name, p in model.named_parameters():
        if p.requires_grad:
            assert p.grad is not None, f"No gradient for {name}"

    model.disable_gradient_checkpointing()
    assert not model.gradient_checkpointing
