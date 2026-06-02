"""Evaluation wrapper for FarolLM using lm-evaluation-harness.

Converts FarolLM to a format compatible with EleutherAI's
lm-evaluation-harness for standard benchmark evaluation.

Usage:
    python -m src.eval.benchmark --model-dir farol-lm-300m --tasks hellaswag,mmlu
"""

import argparse
import json
import os


def evaluate_perplexity(model, dataset, device="cpu"):
    """Compute perplexity on a dataset (quick internal eval)."""
    import math
    import torch

    model.eval()
    total_loss = 0.0
    total_tokens = 0
    loader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=False)

    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            _, loss = model(x, y)
            total_loss += loss.item() * y.numel()
            total_tokens += y.numel()

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)
    return {"loss": avg_loss, "perplexity": perplexity, "tokens": total_tokens}


def run_lm_eval(model_dir: str, tasks: str, device: str = "cpu", batch_size: int = 4):
    """Run lm-evaluation-harness benchmarks.

    Requires: pip install lm-eval
    """
    try:
        import lm_eval
    except ImportError:
        print("lm-eval not installed. Run: pip install lm-eval")
        return None

    print(f"Running evaluation on: {tasks}")
    print(f"Model: {model_dir}")
    print(f"Device: {device}")

    results = lm_eval.simple_evaluate(
        model="hf",
        model_args=f"pretrained={model_dir},dtype=float32,device={device}",
        tasks=tasks.split(","),
        batch_size=batch_size,
    )

    output_path = os.path.join(model_dir, "eval_results.json")
    with open(output_path, "w") as f:
        json.dump(results.get("results", {}), f, indent=2)
    print(f"\nResults saved to {output_path}")

    for task, metrics in results.get("results", {}).items():
        acc = metrics.get("acc,none", metrics.get("acc_norm,none", "N/A"))
        print(f"  {task}: {acc}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate FarolLM")
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--tasks", default="hellaswag,arc_easy")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    run_lm_eval(args.model_dir, args.tasks, args.device, args.batch_size)
