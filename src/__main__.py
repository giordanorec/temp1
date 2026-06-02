"""FarolLM CLI.

Usage:
    python -m src download tokenizer          # download data for tokenizer
    python -m src download single --dataset fineweb2 --lang pt
    python -m src tokenizer train --input data/raw/ --vocab-size 32768
    python -m src train --config configs/farol-300m.yaml
    python -m src export --checkpoint checkpoints/step_100000.pt --output farol-lm-300m
    python -m src push --model-dir farol-lm-300m --repo giordanorec/farol-lm-300m
    python -m src generate --model-dir farol-lm-300m --prompt "O FarolLM"
    python -m src info                        # show model architecture info
"""

import argparse
import sys


def cmd_info(args):
    from src.model.farol import FarolConfig
    config = FarolConfig()
    n = config.num_params()
    print("FarolLM default config (300M):")
    print(f"  Parameters:     {n:>12,}")
    print(f"  Layers:         {config.num_layers:>12}")
    print(f"  Hidden size:    {config.hidden_size:>12}")
    print(f"  Heads:          {config.num_heads:>8} Q / {config.num_kv_heads} KV")
    print(f"  Intermediate:   {config.intermediate_size:>12}")
    print(f"  Vocab size:     {config.vocab_size:>12}")
    print(f"  Max seq len:    {config.max_seq_len:>12}")
    print(f"  Head dim:       {config.head_dim:>12}")
    est_gb = n * 2 / 1e9  # bf16
    print(f"  Est. memory:    {est_gb:>10.1f} GB (bf16, weights only)")


def cmd_train(args):
    from src.train.trainer import train
    train(args.config)


def cmd_tokenizer_train(args):
    from src.tokenizer.train_bpe import train_from_files
    import glob
    if args.input:
        files = []
        for path in args.input:
            if "*" in path:
                files.extend(glob.glob(path))
            else:
                files.append(path)
    else:
        files = glob.glob("data/raw/*.txt")
    if not files:
        print("No input files found. Run 'python -m src download tokenizer' first.")
        sys.exit(1)
    train_from_files(files, args.output, args.vocab_size)


def cmd_download(args):
    from src.data.download import download, download_all_for_tokenizer
    if args.subcmd == "tokenizer":
        download_all_for_tokenizer()
    elif args.subcmd == "single":
        download(args.dataset, args.lang, args.output, args.max_docs)


def cmd_export(args):
    from src.model.hf_integration import from_checkpoint
    from_checkpoint(args.checkpoint, args.output)


def cmd_push(args):
    from src.model.hf_integration import push_to_hub
    push_to_hub(args.model_dir, args.repo)


def cmd_generate(args):
    import torch
    from tokenizers import Tokenizer
    from src.model.hf_integration import load_pretrained

    model, config = load_pretrained(args.model_dir, device=args.device)

    tok_path = f"{args.model_dir}/tokenizer.json"
    tokenizer = Tokenizer.from_file(tok_path)

    ids = tokenizer.encode(args.prompt).ids
    idx = torch.tensor([ids], dtype=torch.long, device=args.device)

    output = model.generate(
        idx,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
    )

    text = tokenizer.decode(output[0].tolist())
    print(text)


def main():
    parser = argparse.ArgumentParser(prog="farol", description="FarolLM CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("info", help="Show model architecture info")

    train_p = sub.add_parser("train", help="Pre-train model")
    train_p.add_argument("--config", default="configs/farol-300m.yaml")

    tok_p = sub.add_parser("tokenizer", help="Train BPE tokenizer")
    tok_sub = tok_p.add_subparsers(dest="tok_cmd")
    tok_train = tok_sub.add_parser("train", help="Train tokenizer")
    tok_train.add_argument("--input", nargs="+")
    tok_train.add_argument("--output", default="tokenizer/")
    tok_train.add_argument("--vocab-size", type=int, default=32768)

    dl_p = sub.add_parser("download", help="Download datasets")
    dl_sub = dl_p.add_subparsers(dest="subcmd")
    dl_sub.add_parser("tokenizer", help="Download balanced corpus for tokenizer")
    dl_single = dl_sub.add_parser("single", help="Download single dataset")
    dl_single.add_argument("--dataset", choices=["fineweb2", "culturax"], required=True)
    dl_single.add_argument("--lang", required=True)
    dl_single.add_argument("--output", default="data/raw")
    dl_single.add_argument("--max-docs", type=int, default=10_000)

    exp_p = sub.add_parser("export", help="Export checkpoint to HF format")
    exp_p.add_argument("--checkpoint", required=True)
    exp_p.add_argument("--output", required=True)

    push_p = sub.add_parser("push", help="Push model to HuggingFace Hub")
    push_p.add_argument("--model-dir", required=True)
    push_p.add_argument("--repo", required=True)

    gen_p = sub.add_parser("generate", help="Generate text")
    gen_p.add_argument("--model-dir", required=True)
    gen_p.add_argument("--prompt", default="O FarolLM")
    gen_p.add_argument("--max-tokens", type=int, default=100)
    gen_p.add_argument("--temperature", type=float, default=0.8)
    gen_p.add_argument("--top-k", type=int, default=50)
    gen_p.add_argument("--device", default="cpu")

    args = parser.parse_args()

    if args.command == "info":
        cmd_info(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "tokenizer":
        cmd_tokenizer_train(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
