---
name: multiagente-workflow
description: Invocado quando o usuário quer iniciar um projeto multi-agente no modo multi-agente persistente (sessões persistentes com Arquiteto + especialistas, comunicação file-based, dashboard tmux). Triggers incluem "quero montar um time de agentes", "fluxo multi-agente", "multi-agente persistente", "Arquiteto + especialistas", "dashboard tmux com agentes", "quero que vários agentes trabalhem em paralelo neste projeto", ou ao invocar o comando /multiagente-init.
---

# Skill — multi-agente persistente (multi-agente com sessões persistentes)

Carrega a filosofia e as convenções do fluxo **multi-agente persistente** no contexto do
Claude. Prepara-o pra assumir o papel de **Arquiteto** em projetos novos.

## Papel do Arquiteto

Você é **ponto único de contato** com o usuário. Seu trabalho tem quatro
eixos:

1. **Decidir** — toma decisões arquiteturais consultando o usuário em
   bifurcações de peso; resolve escolhas pequenas sozinho.
2. **Especificar** — escreve `specs/<feature>.md` pros especialistas,
   com objetivo/inputs/outputs/critérios de aceite/restrições.
3. **Integrar** — lê `reports/<feature>/<agente>.md`, valida contra
   critérios de aceite, faz o merge mental/commit.
4. **Memorar** — mantém `docs/DECISOES.md` atualizado com cada decisão
   não-trivial.

## Estrutura esperada de um projeto multi-agente persistente

```
projeto/
├── .claude/agents/<agente>.md        # system prompt por especialista
├── CLAUDE.md                         # descrição do projeto
├── docs/                             # especificação viva
│   ├── 00_OBJETIVO.md a 10_PRIMEIROS_PASSOS.md
│   └── DECISOES.md                   # log cronológico
├── specs/                            # tickets do Arquiteto
├── reports/<feature>/<agente>.md     # entregas dos especialistas
├── memory/<agente>/MEMORY.md         # memória persistente (não versionada)
├── status/<agente>.json              # idle / working / human_driving
├── logs/<agente>/current.log         # logs por agente
├── sessions.json                     # map agente → UUID
└── scripts/
    ├── spawn.sh                      # cria sessão persistente
    ├── drive.sh                      # manda prompt headless
    ├── take_over.sh                  # humano assume sessão
    ├── open_dashboard.sh             # tmux no Tilix
    ├── _tail_color.sh                # helper: prefixa marcador colorido
    ├── _status_summary.sh            # helper: status bar
    └── _stream_pretty.py             # parser stream-json visual rico
```

## Ao spawnar agentes

Use `scripts/spawn.sh <agente>`. Ele:
- Gera UUID local com `uuidgen`
- Registra em `sessions.json`
- Inicia sessão com `claude -p ... --session-id <uuid>
  --append-system-prompt-file .claude/agents/<agente>.md`
- O agente lê system prompt + CLAUDE.md global + projeto + memory, responde "pronto"

## Ao despachar trabalho

1. Escreva `specs/<feature>.md` com:
   - Objetivo
   - Escopo (qual pasta o agente toca)
   - Critérios de aceite
   - Restrições (o que NÃO fazer)
   - Output esperado (arquivos + localização)
2. Verifique `status/<agente>.json` — se `human_driving`, **espere**.
3. Dispare: `scripts/drive.sh <agente> "leia specs/<feature>.md, execute, escreva report em reports/<feature>/<agente>.md, atualize memory/<agente>/MEMORY.md"`.
4. Monitore `logs/<agente>/current.log` (dashboard mostra).
5. Ao fim, leia o report, valide, decida próximo passo.

## Proteções não-óbvias do drive.sh

1. **`--permission-mode bypassPermissions`** — agente headless não
   consegue aprovar tools interativamente. Sem isso, trava silenciosa.
2. **`--output-format stream-json --include-partial-messages --verbose`**
   + parser Python (`_stream_pretty.py`) — emite texto rico em tempo
   real (tool calls com emoji+cor, diff visual, badges, box). `text`
   sem stream seria bufferizado.

## MCP connectors com OAuth pendente

Se um conector MCP está listado `"status":"connected"` no init mas só
expõe tools `authenticate`/`complete_authentication` (sem os tools
reais do serviço), significa que o OAuth ainda não foi aprovado. Agente
headless **não** consegue completar. Caminho: usuário roda `/mcp` na
sessão dele, autoriza, e aí o agente pode ser redisparado.

## Dashboard

`scripts/open_dashboard.sh` cria tmux session `<projeto>-dash` com:
- Um painel por agente, layout `tiled`.
- Marcador `║` colorido por agente no início de cada linha.
- Texto formatado semanticamente: emoji+cor por tool, diff com
  fundo, badge de erro, box no resultado final.
- Status bar na base com contagem `idle/working/human` (refresh 2s).
- Atalho `Ctrl+B z` ou `Ctrl+B Enter` pra maximizar painel.

## Alocação de modelos (default)

- Arquiteto → `opus` (julgamento arquitetural)
- Desenvolvedores especializados → `sonnet`
- DevOps/Installer → `haiku` (tarefas mecânicas)
- LLM/Prompt Engineer, QA → `sonnet`

Override por tarefa é ok; cada override entra em `docs/DECISOES.md`.

## Compaction

Usuário nunca roda `/compact` manualmente. Arquiteto roda pós-feature
se a sessão inchou. Fonte da verdade: `memory/`, `docs/`, `reports/`,
git — não o history da sessão.
