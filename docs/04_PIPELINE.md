# 04 — Pipeline / Fluxo de execucao

## Fluxo principal

```
[1. Coleta de dados]
     |
     v
[2. Curadoria e filtragem]
     |
     v
[3. Treino de tokenizador BPE]
     |
     v
[4. Tokenizacao do corpus]
     |
     v
[5. Pre-treinamento (next-token prediction)]
     |
     v
[6. Avaliacao em benchmarks]
     |
     v
[7. SFT (Supervised Fine-Tuning)]
     |
     v
[8. DPO (Direct Preference Optimization)]
     |
     v
[9. Avaliacao final + publicacao]
```

## Estagios

1. **Coleta de dados** — Download de subsets de FineWeb-2 (multilingual),
   CulturaX (pt-br forte), opcionalmente The Stack v2 (codigo).
   Estimativa: 10-50B tokens para treino inicial no M4.

2. **Curadoria** — Filtragem por qualidade (perplexidade, idioma,
   deduplicacao). Inspirado em FineWeb-Edu: qualidade > quantidade.

3. **Tokenizador** — Treinar BPE multilingual (pt + en + code) com
   HuggingFace Tokenizers sobre amostra representativa do corpus.
   Vocab size: 32K-64K.

4. **Tokenizacao** — Aplicar tokenizador ao corpus completo. Salvar
   em formato binario (numpy memmap) para leitura eficiente.

5. **Pre-treinamento** — Next-token prediction com LitGPT.
   Otimizacoes: BF16, Flash Attention 2, gradient checkpointing,
   gradient accumulation. WSD scheduler (MiniCPM-style).

6. **Avaliacao** — MMLU, HellaSwag, ARC, benchmarks multilinguais.
   lm-evaluation-harness (EleutherAI).

7. **SFT** — Fine-tuning supervisionado com datasets de instrucao
   (OpenAssistant, UltraChat).

8. **DPO** — Alinhamento com preferencias via TRL. Datasets:
   UltraFeedback, HelpSteer.

9. **Publicacao** — Modelo, tokenizador, dados de treinamento e logs
   no Hugging Face. Model card completo.

## Tratamento de erro

- Divergencia de loss: reduzir LR, verificar dados corrompidos,
  rollback para ultimo checkpoint estavel
- OOM no M4: reduzir batch size, aumentar gradient accumulation,
  ativar gradient checkpointing
- Dados corrompidos: validacao automatica pre-tokenizacao
