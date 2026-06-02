# FarolLM

**LLM/SLM multilingual treinada do zero** como projeto de pesquisa academica.

304M parametros | Decoder-only Transformer | Portugues + Ingles | MIT License

---

## Por que

Todo mundo diz que fazer uma LLM e impossivel. Mas pesquisadores em
Oxford, Stanford e Sorbonne recriam coisas prontas com facilidade.
O FarolLM existe para provar que e possivel — e documentar cada passo.

## Arquitetura

```
Llama-style Decoder-only Transformer (SOTA 2025-2026)
├── RoPE + iRoPE/NoPE every 4th layer (SmolLM3/Llama 4)
├── GQA: 16 Q heads / 4 KV heads
├── QK-Norm on Q and K (DeepSeek-V3, OLMo 2/3)
├── SwiGLU FFN
├── RMSNorm (pre-norm)
├── Sliding window 512 + global every 6th layer (Gemma 3)
├── Logit soft-capping (Gemma 2)
├── Z-loss regularization (PaLM/Gemma)
├── Output embedding centering (2026)
├── Depth-scaled init (GPT-2/DeepSeek)
├── Multi-Token Prediction head (DeepSeek-V3)
└── Gradient checkpointing
```

| Parametro | Valor |
|---|---|
| Parameters | 304M |
| Layers | 24 |
| Hidden | 1024 |
| Heads | 16Q / 4KV (GQA) |
| FFN | 2816 (SwiGLU) |
| Vocab | 32K (BPE multilingual) |
| Context | 2048 |
| Memory (bf16) | ~0.6 GB |

## Quick Start

```bash
# Clone and install
git clone https://github.com/giordanorec/temp1.git farol-lm
cd farol-lm
pip install -e ".[dev]"

# Verify
pytest tests/ -v                    # 39 tests should pass
python -m src info                  # show architecture

# Download data (~1GB for tokenizer)
python -m src.data.prepare tokenizer-corpus

# Train tokenizer
python -m src tokenizer train --vocab-size 32768

# Train (smoke test — seconds)
python -m src train --config configs/farol-small.yaml

# Train (real — days/weeks on M4 64GB)
python -m src train --config configs/farol-300m.yaml

# Export to HuggingFace format
python -m src export --checkpoint checkpoints/farol-300m/step_100000.pt --output farol-lm-300m

# Push to Hub
python -m src push --model-dir farol-lm-300m --repo giordanorec/farol-lm-300m
```

## Training Innovations

| Feature | Source | Status |
|---|---|---|
| Muon optimizer (~35% faster) | Keller Jordan 2025 | Implemented |
| Cautious AdamW (C-AdamW) | arXiv 2411.16085 | Implemented |
| Linear D2Z schedule | Hagele et al. 2025 | Implemented |
| WSD schedule | MiniCPM 2024 | Implemented |
| QK-Norm | DeepSeek-V3, OLMo 2/3 | Implemented |
| iRoPE (NoPE layers) | SmolLM3, Llama 4 | Implemented |
| Sliding window attention | Gemma 3 | Implemented |
| Multi-Token Prediction | DeepSeek-V3 | Implemented |
| Gradient checkpointing | Standard | Implemented |
| BF16 mixed precision | Standard | Implemented |

## Data

Training data comes from open datasets via HuggingFace streaming:

- **FineWeb-2**: 15T+ tokens, 1000+ languages (Portuguese + English subsets)
- **CulturaX**: 6.3T tokens, 167 languages (strong Portuguese coverage)

Data pipeline includes quality filtering, NFC normalization, and exact
deduplication. See `src/data/prepare.py`.

## Project Structure

```
farol-lm/
├── src/
│   ├── model/farol.py          # FarolLM architecture (304M params)
│   ├── model/hf_integration.py # Save/load/push to HuggingFace Hub
│   ├── tokenizer/train_bpe.py  # BPE tokenizer training
│   ├── data/prepare.py         # Download + filter + dedup pipeline
│   ├── data/dataset.py         # Memory-mapped dataset
│   ├── data/tokenize_corpus.py # Tokenize text -> numpy memmap
│   ├── train/trainer.py        # Training loop (grad accum, WSD, autocast)
│   ├── train/optimizers.py     # Muon, C-AdamW, optimizer factory
│   ├── eval/benchmark.py       # lm-evaluation-harness wrapper
│   └── __main__.py             # Unified CLI
├── configs/
│   ├── farol-300m.yaml         # Production config (SOTA features)
│   └── farol-small.yaml        # Smoke test config
├── tests/                      # 39 tests (model, training, tokenizer, e2e)
├── docs/                       # Full documentation + research + proposals
└── scripts/                    # Multi-agent orchestration (optional)
```

## Documentation

- `docs/00_OBJETIVO.md` — Project goals and scope
- `docs/01_ARQUITETURA.md` — Architecture decisions
- `docs/04_PIPELINE.md` — Training pipeline (9 stages)
- `docs/05_STACK.md` — Tech stack rationale
- `docs/08_FASES.md` — Project phases with exit criteria
- `docs/09_RISCOS.md` — Known risks and mitigations
- `docs/DECISOES.md` — Decision log (living document)
- `docs/PESQUISA_LLM.md` — Comprehensive ecosystem research
- `docs/PROPOSTAS_COMPUTE.md` — Compute grant proposals (7 programs)

## Hardware

- **Prototyping**: Mac Mini M4 64GB (Apple Silicon, MPS backend)
- **Production**: Cloud GPUs via compute grants (Google TRC, NVIDIA Academic)
- Estimated cost for 300M on 20B tokens: ~$50-100

## License

MIT

## Author

Giordano Ribeiro Eulalio Cabral (grec@cin.ufpe.br)
CIn-UFPE, Recife, Brazil

## Citation

```bibtex
@misc{farollm2026,
  title={FarolLM: A Multilingual Small Language Model Trained From Scratch},
  author={Giordano Ribeiro Eulalio Cabral},
  year={2026},
  url={https://github.com/giordanorec/farol-lm}
}
```
