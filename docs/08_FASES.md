# 08 — Fases

O projeto avanca em fases com criterio de saida explicito. Cada fase
fecha com commit, update em `DECISOES.md`, e checkpoint com o usuario.

## Fase 0 — Fundacao (nanochat)

- [ ] Clonar e rodar nanochat (Karpathy) localmente
- [ ] Reproduzir GPT-2 124M (subset pequeno)
- [ ] Entender cada componente: tokenizador, modelo, treino, SFT
- [ ] Documentar licoes em `docs/DECISOES.md`

**Criterio de saida**: modelo 124M gerando texto coerente, autor
entende cada linha do pipeline.

## Fase 1 — Tokenizador proprio

- [ ] Baixar amostras de FineWeb-2 (pt + en) e CulturaX
- [ ] Treinar BPE multilingual com HF Tokenizers
- [ ] Avaliar: fertility rate, coverage, edge cases multilinguais
- [ ] Publicar tokenizador no Hugging Face

**Criterio de saida**: tokenizador BPE com vocab 32-64K que tokeniza
portugues e ingles com fertility rate competitiva.

## Fase 2 — Arquitetura FarolLM

- [ ] Definir arquitetura (Llama-style, 300-500M params)
- [ ] Implementar em PyTorch puro (ou via LitGPT)
- [ ] Smoke test: forward pass + backward pass sem erros
- [ ] Contar parametros, estimar FLOPs, validar que cabe no M4

**Criterio de saida**: modelo compila, forward/backward funcionam,
cabe na memoria do M4 64GB.

## Fase 3 — Pre-treinamento

- [ ] Preparar corpus tokenizado (numpy memmap)
- [ ] Configurar treino: BF16, Flash Attention, grad checkpointing
- [ ] Treinar no M4 (subset 10-50B tokens)
- [ ] Monitorar loss, learning rate, throughput via W&B
- [ ] Checkpoints intermediarios

**Criterio de saida**: loss decrescente consistente, modelo gera texto
minimamente coerente.

## Fase 4 — Escalar (cloud)

- [ ] Aplicar para Google TRC ou NVIDIA Academic Grant
- [ ] Ou alugar GPUs (RunPod/Vast.ai)
- [ ] Re-treinar com corpus completo (100B-1T tokens)
- [ ] Avaliar em benchmarks padrao

**Criterio de saida**: modelo avaliado em MMLU, HellaSwag, ARC com
scores documentados.

## Fase 5 — Alinhamento

- [ ] SFT com datasets de instrucao
- [ ] DPO com datasets de preferencia
- [ ] Avaliacao qualitativa (conversas, tarefas)

**Criterio de saida**: modelo segue instrucoes em portugues e ingles.

## Fase 6 — Dominio e publicacao

- [ ] Fine-tune para dominio escolhido (codigo, juridico, educacao ou musica)
- [ ] Model card completo
- [ ] Publicar no Hugging Face: modelo, tokenizador, dados, logs
- [ ] Paper ou blog post documentando o processo

**Criterio de saida**: modelo publicado, reproduzivel, documentado.
