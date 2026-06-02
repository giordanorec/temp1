#!/usr/bin/env bash
# Cria a sessão persistente de um agente pela primeira vez.
# Gera um UUID, inicia sessão com --session-id fixo, registra em sessions.json.
# Uso: scripts/spawn.sh <agente>
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

AGENTE="${1:?Uso: scripts/spawn.sh <agente>}"
AGENT_FILE=".claude/agents/${AGENTE}.md"

if [[ ! -f "${AGENT_FILE}" ]]; then
    echo "ERRO: ${AGENT_FILE} não existe." >&2
    exit 1
fi

mkdir -p "logs/${AGENTE}" "memory/${AGENTE}/notas" "status" "reports"
[[ -f "memory/${AGENTE}/MEMORY.md" ]] || cat > "memory/${AGENTE}/MEMORY.md" <<EOF
# Memória persistente — ${AGENTE}

Este arquivo é sua continuidade entre invocações. Adicione no fim, não
reescreva o topo. Lições breves (1-3 bullets por ciclo).

## Primeiro spawn

- Agente spawned em $(date -Iseconds).
EOF

# UUID fixo, controlado por nós
SESSION_ID=$(uuidgen)

# sessions.json bootstrap
[[ -f sessions.json ]] || echo "{}" > sessions.json

# Registra ANTES do claude rodar — assim se ele travar, a gente sabe o ID.
jq --arg a "${AGENTE}" --arg id "${SESSION_ID}" \
   '. + {($a): $id}' sessions.json > sessions.json.tmp
mv sessions.json.tmp sessions.json

# Prompt inicial: o agente se orienta lendo tudo.
INIT_PROMPT="Você é o agente '${AGENTE}' do projeto old-lady-game. Primeira sessão.

1. Leia ~/.claude/CLAUDE.md (regras globais do Giordano).
2. Leia ./CLAUDE.md (descrição do projeto).
3. Leia ./.claude/agents/${AGENTE}.md (seu system prompt).
4. Leia ./memory/${AGENTE}/MEMORY.md (sua memória persistente; provavelmente vazia ainda).
5. Leia ./docs/DECISOES.md e ./docs/00_OBJETIVO.md.

Depois responda APENAS: 'pronto — ${AGENTE} online.' Não execute mais nada.
Aguarde próximo prompt do Arquiteto via scripts/drive.sh."

mkdir -p "logs/${AGENTE}"
{
    echo "═════════════════════════════════════════════"
    echo "$(date -Iseconds)  SPAWN  ${AGENTE}  session=${SESSION_ID}"
    echo "═════════════════════════════════════════════"
    claude -p "${INIT_PROMPT}" \
        --session-id "${SESSION_ID}" \
        --append-system-prompt-file "${AGENT_FILE}" \
        --output-format text 2>&1
    RC=$?
    echo ""
    echo "═════════════════════════════════════════════"
    echo "$(date -Iseconds)  SPAWN exit=${RC}"
    echo ""
} | tee -a "logs/${AGENTE}/current.log" >&2

# status idle
echo "{\"status\":\"idle\",\"spawned_at\":\"$(date -Iseconds)\"}" > "status/${AGENTE}.json"

echo "→ ${AGENTE} spawned com session_id=${SESSION_ID}"
echo "→ logs/${AGENTE}/current.log"
