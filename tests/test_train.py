"""Smoke tests for training loop and data pipeline."""

import torch

from src.data.dataset import RandomTokenDataset
from src.train.trainer import get_lr, train


def test_random_dataset():
    ds = RandomTokenDataset(num_samples=10, seq_len=32, vocab_size=100)
    assert len(ds) == 10
    x, y = ds[0]
    assert x.shape == (32,)
    assert y.shape == (32,)
    assert x.dtype == torch.int64


def test_wsd_scheduler():
    config = {
        "training": {
            "max_steps": 1000,
            "learning_rate": 3e-4,
            "min_learning_rate": 3e-5,
        },
        "scheduler": {
            "warmup_fraction": 0.1,
            "stable_fraction": 0.7,
            "decay_fraction": 0.2,
        },
    }
    lr_0 = get_lr(0, config)
    lr_warmup_end = get_lr(99, config)
    lr_stable = get_lr(500, config)
    lr_end = get_lr(999, config)

    assert lr_0 < lr_warmup_end  # warmup increasing
    assert abs(lr_stable - 3e-4) < 1e-6  # stable at max_lr
    assert lr_end < lr_stable  # decaying at end
    assert lr_end >= 3e-5  # above min_lr


def test_train_smoke():
    """Run 10 steps of training on random data — validates full pipeline."""
    model = train("configs/farol-small.yaml")
    assert model is not None
    n = sum(p.numel() for p in model.parameters())
    assert n > 0
