"""Minimal pre-training loop for FarolLM.

Supports: gradient accumulation, gradient clipping, WSD scheduler,
mixed precision, checkpointing, W&B logging.
"""

import math
import os
import time

import torch
import yaml
from torch.utils.data import DataLoader

from src.model.farol import FarolConfig, FarolLM


def get_lr(step: int, config: dict) -> float:
    """Learning rate scheduler. Supports WSD, linear D2Z, and cosine."""
    max_steps = config["training"]["max_steps"]
    max_lr = config["training"]["learning_rate"]
    min_lr = config["training"].get("min_learning_rate", 0.0)

    sched = config.get("scheduler", {})
    sched_type = sched.get("type", "wsd")
    warmup_frac = sched.get("warmup_fraction", 0.02)
    warmup_steps = int(max_steps * warmup_frac)

    if step < warmup_steps:
        return max_lr * (step + 1) / warmup_steps

    if sched_type == "linear_d2z":
        # Linear decay-to-zero (2025 SOTA, Hagele et al.)
        # 60% compute savings over cosine-10x
        progress = (step - warmup_steps) / max(max_steps - warmup_steps, 1)
        return max_lr * (1 - progress)

    elif sched_type == "wsd":
        # Warmup-Stable-Decay (MiniCPM / SmolLM3)
        stable_frac = sched.get("stable_fraction", 0.78)
        stable_steps = int(max_steps * stable_frac)
        decay_start = warmup_steps + stable_steps
        if step < decay_start:
            return max_lr
        decay_steps = max_steps - decay_start
        progress = (step - decay_start) / max(decay_steps, 1)
        return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))

    elif sched_type == "cosine":
        progress = (step - warmup_steps) / max(max_steps - warmup_steps, 1)
        return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))

    return max_lr


def train(config_path: str, dataset=None):
    with open(config_path) as f:
        config = yaml.safe_load(f)

    model_cfg = FarolConfig(**config["model"])
    train_cfg = config["training"]

    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"

    dtype = torch.float32
    if train_cfg.get("dtype") == "bfloat16" and device != "mps":
        dtype = torch.bfloat16
    elif train_cfg.get("dtype") == "float16":
        dtype = torch.float16

    model = FarolLM(model_cfg)
    model._apply_depth_scaled_init()
    if train_cfg.get("gradient_checkpointing", False):
        model.enable_gradient_checkpointing()
    model = model.to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"FarolLM: {n_params:,} params on {device} ({dtype})")

    from src.train.optimizers import create_optimizer
    optimizer = create_optimizer(model, config)

    if dataset is None:
        from src.data.dataset import RandomTokenDataset
        dataset = RandomTokenDataset(
            num_samples=1000,
            seq_len=config["data"]["seq_len"],
            vocab_size=model_cfg.vocab_size,
        )

    loader = DataLoader(
        dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=True,
        drop_last=True,
        num_workers=min(4, os.cpu_count() or 1),
        pin_memory=(device == "cuda"),
        persistent_workers=True if (os.cpu_count() or 1) > 1 else False,
    )

    grad_accum = train_cfg["gradient_accumulation_steps"]
    max_steps = train_cfg["max_steps"]
    grad_clip = train_cfg.get("grad_clip", 1.0)
    log_every = config.get("logging", {}).get("log_every_steps", 10)

    model.train()
    step = 0
    data_iter = iter(loader)
    t0 = time.time()

    while step < max_steps:
        optimizer.zero_grad()
        loss_accum = 0.0

        for micro_step in range(grad_accum):
            try:
                x, y = next(data_iter)
            except StopIteration:
                data_iter = iter(loader)
                x, y = next(data_iter)

            x, y = x.to(device), y.to(device)

            with torch.autocast(device_type=device if device != "mps" else "cpu", dtype=dtype):
                _, loss = model(x, y)
                loss = loss / grad_accum

            loss.backward()
            loss_accum += loss.item()

        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

        lr = get_lr(step, config)
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        optimizer.step()
        step += 1

        if step % log_every == 0:
            dt = time.time() - t0
            tokens_per_sec = (
                train_cfg["batch_size"]
                * grad_accum
                * config["data"]["seq_len"]
                * log_every
                / dt
            )
            print(
                f"step {step:>6d}/{max_steps} | "
                f"loss {loss_accum:.4f} | "
                f"lr {lr:.2e} | "
                f"tok/s {tokens_per_sec:.0f} | "
                f"dt {dt:.1f}s"
            )
            t0 = time.time()

        ckpt_cfg = config.get("checkpointing", {})
        save_every = ckpt_cfg.get("save_every_steps", 0)
        if save_every and step % save_every == 0:
            out_dir = ckpt_cfg.get("output_dir", "checkpoints")
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, f"step_{step:06d}.pt")
            torch.save({
                "step": step,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "config": config,
            }, path)
            print(f"checkpoint saved: {path}")

    print(f"training complete: {step} steps")
    return model


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/farol-small.yaml"
    train(config_path)
