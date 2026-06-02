# 01 — Arquitetura

## Principio central

Transformer decoder-only (GPT-style) com melhorias modernas do LLaMA:
RoPE, SwiGLU, GQA, RMSNorm. Arquitetura "deep-and-thin" seguindo
descobertas de MobileLLM e MiniCPM para maximizar performance no regime
sub-bilhao de parametros.

## Diagrama

```
Dados brutos (FineWeb-2 + CulturaX)
        |
        v
  [Tokenizador BPE Multilingual]  <-- HF Tokenizers / SentencePiece
        |
        v
  [Embedding Layer + RoPE]
        |
        v
  [N x Transformer Block]
  |  RMSNorm
  |  -> GQA Multi-Head Attention (Flash Attention 2)
  |  RMSNorm
  |  -> SwiGLU FFN
        |
        v
  [RMSNorm + LM Head]
        |
        v
  [Pre-treino: next-token prediction]
        |
        v
  [SFT + DPO (alinhamento)]
        |
        v
  FarolLM (modelo final)
```

## Por que essa arquitetura e nao outras

**Alternativa A**: Transformer encoder-decoder (T5-style) — descartada
porque modelos decoder-only dominam geracao de texto e sao mais simples
de treinar com next-token prediction.

**Alternativa B**: SSM (Mamba) — interessante mas ecossistema menos
maduro, menos reproduzivel, menos material educacional. Pode ser
explorado em fase futura.

**Alternativa C** (escolhida): Decoder-only Llama-style — arquitetura
mais estudada, mais reproduzivel, com codigo aberto abundante (OLMo,
LitGPT, nanochat). Melhorias (RoPE, SwiGLU, GQA) sao incrementais
e bem documentadas.

## Divisao de trabalho por agente

| Agente | Pasta/arquivos de responsabilidade |
|---|---|
| `pipeline-dev` | `src/model/`, `src/data/`, `src/train/` |
| `devops-installer` | `pyproject.toml`, configs, CI/CD |
| `qa-tester` | `tests/` |
| `docs-writer` | `README.md`, `docs/` |

## Hiperparametros alvo (300-500M)

| Parametro | Valor estimado |
|---|---|
| Layers | 24-32 |
| Hidden dim | 1024-1280 |
| Attention heads | 16 |
| GQA groups | 4 |
| Vocab size | 32K-64K |
| Context length | 2048-4096 |
| Total params | 300M-500M |

Valores finais serao definidos apos Fase 0 (reproducao do nanochat).
