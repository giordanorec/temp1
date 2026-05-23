---
description: "Abre (ou reabre) o dashboard tmux do projeto multi-agente persistente"
argument-hint: "[--rebuild] força destruir e recriar a sessão tmux"
---

Abre o dashboard tmux com um painel por agente, mostrando o log ao vivo
de cada especialista.

## Processo

1. **Pré-check**: se `sessions.json` não existe no cwd, avise que o
   projeto não foi inicializado — sugira `/multiagente-init`.

2. **Executar**:
   - Se `$ARGUMENTS` contém `--rebuild`: `scripts/open_dashboard.sh --rebuild`
   - Senão: `scripts/open_dashboard.sh`

3. **Confirmar**: uma janela Tilix deve ter aberto. Se não abriu,
   dê as instruções de attach manual:
   `tmux attach -t $(basename $(pwd))-dash`

## Atalhos dentro do dashboard

- `Ctrl+B z` ou `Ctrl+B Enter` — maximizar/minimizar painel atual
- `Ctrl+B <seta>` — navegar entre painéis
- `Ctrl+B d` — detach (sessão continua viva em background)
- `Ctrl+B [` — modo scroll (`q` pra sair)
- Clique do mouse — selecionar painel

## Status bar

Na base da sessão tmux, contador atualizado a cada 2s:
`⦿ idle N  ◐ working N  ✋ human N`.
