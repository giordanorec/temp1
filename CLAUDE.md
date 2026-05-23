# FarolLM

LLM/SLM multilingual treinada do zero como projeto de pesquisa academica,
para entendimento profundo de todo o pipeline de criacao de modelos de linguagem.

## Objetivo

Criar um modelo de linguagem proprio, do zero (tokenizador, arquitetura,
pre-treinamento, alinhamento), documentando cada decisao e publicando
codigo, dados e pesos abertos. Foco em aprendizado e pesquisa.

Ver `docs/00_OBJETIVO.md` para detalhes.

## Como reler o contexto

Ordem de leitura:
1. `~/.claude/CLAUDE.md` (regras globais, se existir)
2. Este arquivo
3. `docs/DECISOES.md` (log cronologico)
4. `docs/00_OBJETIVO.md` ate `docs/10_PRIMEIROS_PASSOS.md`

## Stack

- Python 3.11+ / PyTorch 2.x
- LitGPT (framework de treinamento)
- HuggingFace Tokenizers + SentencePiece (tokenizador BPE multilingual)
- FineWeb-2 + CulturaX (dados multilinguais)
- TRL (alinhamento DPO)
- W&B + TensorBoard (monitoramento)
- Hardware primario: Mac Mini M4 64GB

## Como rodar

```bash
# TODO: preencher apos setup da Fase 3
```

## Multi-agente

- `sessions.json` — map agente -> session_id
- `scripts/open_dashboard.sh` — abre grade tmux
- `scripts/spawn.sh <agente>` — cria sessao
- `scripts/drive.sh <agente> "<prompt>"` — manda prompt em background
- `scripts/take_over.sh <agente>` — humano assume
