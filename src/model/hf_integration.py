"""HuggingFace Hub integration for FarolLM.

Save/load model and tokenizer in HF-compatible format.
Push to Hugging Face Hub.

Usage:
    # Save locally
    python -m src.model.hf_integration save --checkpoint checkpoints/step_100000.pt --output farol-lm-300m

    # Push to Hub
    python -m src.model.hf_integration push --checkpoint checkpoints/step_100000.pt --repo giordanorec/farol-lm-300m
"""

import argparse
import json
import os

import torch

from src.model.farol import FarolConfig, FarolLM


def save_pretrained(
    model: FarolLM,
    config: FarolConfig,
    output_dir: str,
    tokenizer_path: str | None = None,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    torch.save(model.state_dict(), os.path.join(output_dir, "model.pt"))

    try:
        from safetensors.torch import save_file
        save_file(model.state_dict(), os.path.join(output_dir, "model.safetensors"))
    except ImportError:
        pass

    config_dict = {
        "model_type": "farol",
        "architectures": ["FarolLM"],
        "vocab_size": config.vocab_size,
        "hidden_size": config.hidden_size,
        "intermediate_size": config.intermediate_size,
        "num_hidden_layers": config.num_layers,
        "num_attention_heads": config.num_heads,
        "num_key_value_heads": config.num_kv_heads,
        "max_position_embeddings": config.max_seq_len,
        "rms_norm_eps": config.rms_norm_eps,
        "rope_theta": config.rope_theta,
        "tie_word_embeddings": config.tie_word_embeddings,
        "torch_dtype": "bfloat16",
        "total_params": config.num_params(),
    }
    with open(os.path.join(output_dir, "config.json"), "w") as f:
        json.dump(config_dict, f, indent=2)

    if tokenizer_path and os.path.exists(tokenizer_path):
        import shutil
        for fname in os.listdir(tokenizer_path):
            src = os.path.join(tokenizer_path, fname)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(output_dir, fname))

    model_card = f"""---
language:
  - pt
  - en
license: mit
tags:
  - farol-lm
  - from-scratch
  - multilingual
  - research
---

# FarolLM

LLM/SLM multilingual treinada do zero como projeto de pesquisa academica.

## Model Details

- **Parameters:** {config.num_params():,}
- **Architecture:** Decoder-only Transformer (Llama-style)
- **Components:** RoPE, SwiGLU, GQA ({config.num_heads}Q/{config.num_kv_heads}KV), RMSNorm
- **Layers:** {config.num_layers}
- **Hidden size:** {config.hidden_size}
- **Vocab size:** {config.vocab_size}
- **Max context:** {config.max_seq_len}
- **License:** MIT

## Training

Treinado do zero em dados multilinguais (FineWeb-2 + CulturaX).
Pipeline completo documentado no repositorio.

## Usage

```python
from src.model.farol import FarolConfig, FarolLM
from src.model.hf_integration import load_pretrained

model, config = load_pretrained("path/to/model")
```

## Citation

```bibtex
@misc{{farollm2026,
  title={{FarolLM: A Multilingual Small Language Model Trained From Scratch}},
  author={{Giordano Ribeiro Eulalio Cabral}},
  year={{2026}},
  url={{https://github.com/giordanorec/farol-lm}}
}}
```
"""
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write(model_card)

    print(f"Model saved to {output_dir}/")
    print(f"  config.json, model.pt, README.md")


def load_pretrained(
    model_dir: str, device: str = "cpu"
) -> tuple[FarolLM, FarolConfig]:
    with open(os.path.join(model_dir, "config.json")) as f:
        cfg = json.load(f)

    config = FarolConfig(
        vocab_size=cfg["vocab_size"],
        hidden_size=cfg["hidden_size"],
        intermediate_size=cfg["intermediate_size"],
        num_layers=cfg["num_hidden_layers"],
        num_heads=cfg["num_attention_heads"],
        num_kv_heads=cfg["num_key_value_heads"],
        max_seq_len=cfg["max_position_embeddings"],
        rms_norm_eps=cfg["rms_norm_eps"],
        rope_theta=cfg["rope_theta"],
        tie_word_embeddings=cfg["tie_word_embeddings"],
    )

    model = FarolLM(config)

    safetensors_path = os.path.join(model_dir, "model.safetensors")
    pt_path = os.path.join(model_dir, "model.pt")

    if os.path.exists(safetensors_path):
        from safetensors.torch import load_file
        state_dict = load_file(safetensors_path, device=device)
        model.load_state_dict(state_dict)
    elif os.path.exists(pt_path):
        state_dict = torch.load(pt_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
    else:
        raise FileNotFoundError(f"No model weights found in {model_dir}")

    model.to(device)
    model.eval()
    return model, config


def push_to_hub(model_dir: str, repo_id: str) -> None:
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(repo_id, exist_ok=True, repo_type="model")
    api.upload_folder(folder_path=model_dir, repo_id=repo_id, repo_type="model")
    print(f"Pushed to https://huggingface.co/{repo_id}")


def from_checkpoint(checkpoint_path: str, output_dir: str) -> None:
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    cfg = ckpt["config"]["model"]
    config = FarolConfig(**cfg)
    model = FarolLM(config)
    model.load_state_dict(ckpt["model"])
    save_pretrained(model, config, output_dir)
    print(f"Step {ckpt.get('step', '?')} exported to {output_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HuggingFace integration for FarolLM")
    sub = parser.add_subparsers(dest="command")

    save_cmd = sub.add_parser("save", help="Export checkpoint to HF format")
    save_cmd.add_argument("--checkpoint", required=True)
    save_cmd.add_argument("--output", required=True)

    push_cmd = sub.add_parser("push", help="Push to HuggingFace Hub")
    push_cmd.add_argument("--model-dir", required=True)
    push_cmd.add_argument("--repo", required=True, help="e.g. giordanorec/farol-lm-300m")

    args = parser.parse_args()

    if args.command == "save":
        from_checkpoint(args.checkpoint, args.output)
    elif args.command == "push":
        push_to_hub(args.model_dir, args.repo)
    else:
        parser.print_help()
