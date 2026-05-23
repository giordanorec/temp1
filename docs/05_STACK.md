# 05 — Stack

## Linguagem principal

Python 3.11+ — escolhida por ser o padrao de facto em ML/AI, com
ecossistema incomparavel (PyTorch, HuggingFace, etc).

## Runtime

- Python 3.11+ (Apple Silicon nativo)
- PyTorch 2.x com suporte MPS (Metal Performance Shaders)

## Framework / libs principais

- **LitGPT**: Framework de treinamento. 20+ LLMs implementados sem
  abstracoes opacas. Base do TinyLlama. Suporta Apple MPS.
- **HuggingFace Tokenizers**: Treinar tokenizador BPE multilingual.
  Core em Rust, bindings Python.
- **SentencePiece**: Alternativa/complemento para tokenizacao
  multilingual byte-level.
- **TRL**: Alinhamento (SFT, DPO). Acessivel, funciona em hardware
  consumer.
- **lm-evaluation-harness**: Avaliacao em benchmarks padrao (EleutherAI).
- **Weights & Biases**: Monitoramento de treinamento (tier gratuito).
- **TensorBoard**: Debug em tempo real.

## Testes

pytest + pytest-cov

## Qualidade

- Lint: ruff
- Format: ruff format
- Pre-commit: ruff + pytest

## Ordem de preferencia ao adicionar deps novas

1. Ja instalado? Use.
2. Stdlib resolve? Use.
3. Biblioteca madura (>1k stars, updates recentes)? OK, passa pelo
   DevOps.
4. Biblioteca obscura? Discuta com Arquiteto antes.

## O que NAO entra (veto)

- **TensorFlow**: projeto e PyTorch-only por consistencia
- **JAX**: interessante mas curva de aprendizado desnecessaria para
  o escopo atual (pode ser explorado em fase futura com TPUs)
- **Frameworks proprietarios**: tudo deve ser open source e reproduzivel
