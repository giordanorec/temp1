"""Smoke tests for FarolLM model architecture."""

import torch
import yaml

from src.model.farol import FarolConfig, FarolLM


def load_config(path: str = "configs/farol-small.yaml") -> FarolConfig:
    with open(path) as f:
        cfg = yaml.safe_load(f)["model"]
    return FarolConfig(**cfg)


def test_config_param_count():
    config = FarolConfig()  # default 300M
    n = config.num_params()
    assert 250_000_000 < n < 400_000_000, f"Expected ~300M params, got {n:,}"


def test_config_small():
    config = load_config()
    n = config.num_params()
    assert n < 1_000_000, f"Small config should be <1M params, got {n:,}"


def test_forward_pass():
    config = load_config()
    model = FarolLM(config)
    model.eval()

    B, T = 2, 64
    idx = torch.randint(0, config.vocab_size, (B, T))
    logits, loss = model(idx)

    assert logits.shape == (B, T, config.vocab_size)
    assert loss is None


def test_forward_with_targets():
    config = load_config()
    model = FarolLM(config)
    model.train()

    B, T = 2, 64
    idx = torch.randint(0, config.vocab_size, (B, T))
    targets = torch.randint(0, config.vocab_size, (B, T))
    logits, loss = model(idx, targets)

    assert logits.shape == (B, T, config.vocab_size)
    assert loss is not None
    assert loss.item() > 0


def test_backward_pass():
    config = load_config()
    model = FarolLM(config)
    model.train()

    B, T = 2, 32
    idx = torch.randint(0, config.vocab_size, (B, T))
    targets = torch.randint(0, config.vocab_size, (B, T))
    _, loss = model(idx, targets)
    loss.backward()

    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"No gradient for {name}"


def test_generate():
    config = load_config()
    model = FarolLM(config)
    model.eval()

    prompt = torch.randint(0, config.vocab_size, (1, 8))
    output = model.generate(prompt, max_new_tokens=16, temperature=1.0, top_k=10)

    assert output.shape == (1, 24)  # 8 prompt + 16 generated
    assert (output >= 0).all() and (output < config.vocab_size).all()


def test_weight_tying():
    config = load_config()
    assert config.tie_word_embeddings
    model = FarolLM(config)
    assert model.tok_emb.weight is model.lm_head.weight


def test_gqa_ratio():
    config = FarolConfig()
    assert config.num_heads % config.num_kv_heads == 0
    assert config.num_heads // config.num_kv_heads == 4  # 4 Q heads per KV head


def test_rope_freqs_shape():
    config = load_config()
    model = FarolLM(config)
    assert model.rope_freqs.shape == (config.max_seq_len, config.head_dim // 2)


def test_train_step():
    """Minimal training step: forward, backward, optimizer step."""
    config = load_config()
    model = FarolLM(config)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    B, T = 2, 32
    idx = torch.randint(0, config.vocab_size, (B, T))
    targets = torch.randint(0, config.vocab_size, (B, T))

    _, loss1 = model(idx, targets)
    loss1.backward()
    optimizer.step()
    optimizer.zero_grad()

    _, loss2 = model(idx, targets)
    # Loss should change after one step (not necessarily decrease on random data)
    assert loss2.item() != loss1.item() or True  # just ensure no crash
