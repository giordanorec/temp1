#!/usr/bin/env bash
# Humano assume interativamente a sessão de um agente.
# Uso: scripts/take_over.sh <agente>
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

AGENTE="${1:?Uso: scripts/take_over.sh <agente>}"

SESSION_ID=$(jq -r --arg a "${AGENTE}" '.[$a] // empty' sessions.json)
if [[ -z "${SESSION_ID}" ]]; then
    echo "ERRO: ${AGENTE} não está em sessions.json." >&2
    exit 1
fi

mkdir -p status
STATUS_FILE="status/${AGENTE}.json"
echo "{\"status\":\"human_driving\",\"started_at\":\"$(date -Iseconds)\"}" > "${STATUS_FILE}"

trap 'echo "{\"status\":\"idle\",\"finished_at\":\"$(date -Iseconds)\"}" > "'"${STATUS_FILE}"'"' EXIT

echo "→ você está dirigindo '${AGENTE}'. Ctrl+D para sair."
echo "→ o Arquiteto não vai interromper enquanto você está aqui."
echo ""

exec claude --resume "${SESSION_ID}"
