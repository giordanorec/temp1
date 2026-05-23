# {{NOME_PROJETO}}

{{UMA_FRASE_DESCRITIVA}}

## Objetivo

{{BREVE_DESCRICAO_EXPANDIDA}}

Ver `docs/00_OBJETIVO.md` para detalhes.

## Como reler o contexto

Ordem de leitura:
1. `~/.claude/CLAUDE.md` (regras globais, se existir)
2. Este arquivo
3. `docs/DECISOES.md` (log cronológico)
4. `docs/00_OBJETIVO.md` até `docs/10_PRIMEIROS_PASSOS.md`

## Stack

{{STACK_RESUMIDA}}

## Como rodar

{{COMANDOS_DE_BOOTSTRAP_E_DEV}}

## Multi-agente

- `sessions.json` — map agente → session_id
- `scripts/open_dashboard.sh` — abre grade tmux
- `scripts/spawn.sh <agente>` — cria sessão
- `scripts/drive.sh <agente> "<prompt>"` — manda prompt em background
- `scripts/take_over.sh <agente>` — humano assume
