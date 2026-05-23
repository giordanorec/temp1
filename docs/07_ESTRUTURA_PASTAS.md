# 07 — Estrutura de pastas

```
farol-lm/
├── .claude/agents/           # system prompts dos agentes
├── CLAUDE.md                 # descricao do projeto
├── README.md                 # visao pro usuario final
├── .gitignore
├── docs/                     # documentacao viva
│   ├── 00_OBJETIVO.md a 10_PRIMEIROS_PASSOS.md
│   ├── DECISOES.md           # log cronologico
│   └── PESQUISA_LLM.md      # levantamento do ecossistema
├── specs/                    # tickets do Arquiteto
├── reports/                  # respostas dos especialistas
│   └── <feature>/<agente>.md
├── memory/                   # memoria persistente (NAO versionado)
│   └── <agente>/MEMORY.md
├── status/                   # NAO versionado
│   └── <agente>.json
├── logs/                     # NAO versionado
│   └── <agente>/current.log
├── sessions.json             # NAO versionado
├── scripts/                  # orquestracao multi-agente
├── src/
│   ├── tokenizer/            # treino e uso do tokenizador BPE
│   ├── model/                # definicao da arquitetura FarolLM
│   ├── data/                 # download, curadoria, tokenizacao
│   ├── train/                # loop de pre-treinamento
│   └── eval/                 # avaliacao em benchmarks
├── configs/                  # yamls de hiperparametros
├── tests/                    # testes automatizados
├── notebooks/                # exploracao e analise
├── data/                     # dados brutos e processados (NAO versionado)
│   ├── raw/
│   └── tokenized/
├── checkpoints/              # pesos salvos (NAO versionado)
└── pyproject.toml            # dependencias e config
```

## Regra de ouro

**Um agente, uma pasta principal.** Sem sobreposicao. Contratos entre
pastas sao documentados em `docs/01_ARQUITETURA.md` e reforcados em
`specs/<feature>.md`.
