# 08 — Fases

O projeto avança em fases com critério de saída explícito. Cada fase
fecha com commit, update em `DECISOES.md`, e checkpoint com o usuário.

## Fase 0 — Discovery

- [ ] Perguntas de objetivo, público, escopo, stack.
- [ ] Decisões principais tomadas (stack, time, hospedagem).
- [ ] Confirmação do repo GitHub privado (se aplicável).

## Fase 1 — Especificação

- [ ] `docs/00_OBJETIVO.md` a `docs/10_PRIMEIROS_PASSOS.md` preenchidos.
- [ ] `docs/DECISOES.md` com a decisão inicial.

## Fase 2 — Definição do time

- [ ] `.claude/agents/arquiteto.md` + N especialistas (escolhidos
  conforme domínio).

## Fase 3 — Setup

- [ ] Estrutura de pastas.
- [ ] Configuração do stack (manifests, configs).
- [ ] Scripts de orquestração em `scripts/`.
- [ ] **Smoke test** validando stack ponta a ponta.
- [ ] Commit inicial + push pro repo GitHub.

**Critério de saída**: projeto roda 1-comando (`npm install && npm run smoke`
ou equivalente) em máquina limpa.

## Fase 4+ — Implementação iterativa

Cada feature segue o protocolo:
1. Arquiteto escreve `specs/<feature>.md`.
2. Arquiteto dispara especialistas via `scripts/drive.sh` em paralelo.
3. Especialistas escrevem `reports/<feature>/<agente>.md`.
4. Arquiteto integra, decide próximo passo.
5. QA valida.
6. Commit com `docs/DECISOES.md` atualizado.
7. Resumo pro usuário.

Cada fase adicional tem critério de saída próprio — definir aqui.
