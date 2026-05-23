# 07 — Estrutura de pastas

```
projeto/
├── .claude/agents/           # system prompts dos agentes
├── CLAUDE.md                 # descrição do projeto
├── README.md                 # visão pro usuário final
├── .gitignore
├── docs/                     # documentação viva
│   ├── 00_OBJETIVO.md a 10_PRIMEIROS_PASSOS.md
│   └── DECISOES.md           # log cronológico
├── specs/                    # tickets do Arquiteto
├── reports/                  # respostas dos especialistas
│   └── <feature>/<agente>.md
├── memory/                   # memória persistente (NÃO versionado)
│   └── <agente>/MEMORY.md
├── status/                   # NÃO versionado
│   └── <agente>.json         # idle / working / human_driving
├── logs/                     # NÃO versionado
│   └── <agente>/current.log
├── sessions.json             # NÃO versionado (agente → session_id)
├── scripts/                  # orquestração
└── {{PASTAS_DO_STACK}}       # src/, lib/, tests/, etc
```

## Regra de ouro

**Um agente, uma pasta principal.** Sem sobreposição. Contratos entre
pastas são documentados em `docs/01_ARQUITETURA.md` e reforçados em
`specs/<feature>.md`.
