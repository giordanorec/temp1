"""Tests for 2025-2026 SOTA features: NoPE, sliding window, MTP, QK-norm, etc."""

import torch

from src.model.farol import FarolConfig, FarolLM, MTPHead


def _small_config(**overrides) -> FarolConfig:
    defaults = dict(
        vocab_size=512, hidden_size=64, intermediate_size=176,
        num_layers=8, num_heads=4, num_kv_heads=2, max_seq_len=128,
    )
    defaults.update(overrides)
    return FarolConfig(**defaults)


def test_qk_norm_enabled():
    config = _small_config(qk_norm=True)
    model = FarolLM(config)
    assert model.layers[0].attn.q_norm is not None
    assert model.layers[0].attn.k_norm is not None

    x = torch.randint(0, 512, (1, 32))
    logits, _ = model(x)
    assert logits.shape == (1, 32, 512)


def test_qk_norm_disabled():
    config = _small_config(qk_norm=False)
    model = FarolLM(config)
    assert model.layers[0].attn.q_norm is None


def test_nope_every_4th_layer():
    config = _small_config(nope_layer_interval=4)
    model = FarolLM(config)

    # Layers 0,1,2 use RoPE; layer 3 does not; layers 4,5,6 use RoPE; layer 7 does not
    assert model.layers[0].attn.use_rope is True
    assert model.layers[1].attn.use_rope is True
    assert model.layers[2].attn.use_rope is True
    assert model.layers[3].attn.use_rope is False  # 4th layer
    assert model.layers[7].attn.use_rope is False  # 8th layer

    x = torch.randint(0, 512, (1, 32))
    logits, _ = model(x)
    assert logits.shape == (1, 32, 512)


def test_sliding_window_attention():
    config = _small_config(sliding_window=32, global_attention_interval=4)
    model = FarolLM(config)

    # Most layers use sliding window; every 4th uses global
    assert model.layers[0].attn.sliding_window == 32
    assert model.layers[1].attn.sliding_window == 32
    assert model.layers[2].attn.sliding_window == 32
    assert model.layers[3].attn.sliding_window == 0  # global (4th)

    x = torch.randint(0, 512, (2, 64))
    logits, _ = model(x)
    assert logits.shape == (2, 64, 512)


def test_sliding_window_backward():
    config = _small_config(sliding_window=16, global_attention_interval=4)
    model = FarolLM(config)
    model.train()

    x = torch.randint(0, 512, (2, 32))
    y = torch.randint(0, 512, (2, 32))
    _, loss = model(x, y)
    loss.backward()


def test_logit_soft_cap():
    config = _small_config(logit_soft_cap=30.0)
    model = FarolLM(config)
    model.eval()

    x = torch.randint(0, 512, (1, 16))
    logits, _ = model(x)
    assert logits.abs().max() <= 30.0 + 1e-5


def test_z_loss():
    config = _small_config(z_loss_weight=1e-4)
    model = FarolLM(config)
    model.train()

    x = torch.randint(0, 512, (2, 16))
    y = torch.randint(0, 512, (2, 16))
    _, loss_with_z = model(x, y)

    config_no_z = _small_config(z_loss_weight=0.0)
    model_no_z = FarolLM(config_no_z)
    model_no_z.load_state_dict(model.state_dict())
    _, loss_without_z = model_no_z(x, y)

    # z-loss adds a small positive term
    assert loss_with_z.item() >= loss_without_z.item() - 1e-4


def test_mtp_head():
    config = _small_config()
    mtp = MTPHead(config, depth=2)

    B, T = 2, 32
    hidden = torch.randn(B, T, config.hidden_size)
    tok_emb = torch.nn.Embedding(config.vocab_size, config.hidden_size)
    targets = torch.randint(0, config.vocab_size, (B, T))

    loss = mtp(hidden, tok_emb, targets)
    assert loss.item() > 0
    loss.backward()


def test_mtp_with_model():
    config = _small_config()
    model = FarolLM(config)
    mtp = MTPHead(config, depth=2)
    model.train()

    x = torch.randint(0, 512, (2, 32))
    y = torch.randint(0, 512, (2, 32))

    # Get hidden states before lm_head
    with torch.no_grad():
        h = model.tok_emb(x)
        for layer in model.layers:
            h = layer(h, model.rope_freqs)
        h = model.norm(h)

    _, ce_loss = model(x, y)
    mtp_loss = mtp(h.detach(), model.tok_emb, y)

    total_loss = ce_loss + 0.3 * mtp_loss
    total_loss.backward()


def test_depth_scaled_init():
    config = _small_config(num_layers=8)
    model = FarolLM(config)
    model._apply_depth_scaled_init()

    expected_std = 0.02 / (2 * 8) ** 0.5
    actual_std = model.layers[0].attn.o_proj.weight.std().item()
    assert abs(actual_std - expected_std) < 0.005


def test_all_features_combined():
    """Smoke test with ALL advanced features enabled."""
    config = _small_config(
        qk_norm=True,
        logit_soft_cap=30.0,
        z_loss_weight=1e-4,
        nope_layer_interval=4,
        sliding_window=16,
        global_attention_interval=4,
        embedding_multiplier=8.0,  # sqrt(64)
    )
    model = FarolLM(config)
    model._apply_depth_scaled_init()
    model.enable_gradient_checkpointing()
    model.train()

    x = torch.randint(0, 512, (2, 32))
    y = torch.randint(0, 512, (2, 32))
    _, loss = model(x, y)
    loss.backward()

    assert loss.item() > 0
    for name, p in model.named_parameters():
        if p.requires_grad:
            assert p.grad is not None, f"No gradient for {name}"
