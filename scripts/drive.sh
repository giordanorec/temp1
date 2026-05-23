#!/usr/bin/env bash
# Manda prompt headless a um agente já spawned e imprime o trabalho do
# agente ao vivo (texto, tool calls, results) no log.
#
# Uso: scripts/drive.sh <agente> "<prompt>"
#
# Proteções importantes:
# 1. --permission-mode bypassPermissions: agentes headless não conseguem
#    aprovar tools interativamente.
# 2. --output-format stream-json --include-partial-messages: emite eventos
#    linha a linha (JSON) à medida que acontecem. Parseado por
#    _stream_pretty.py pra formato humano em tempo real.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

AGENTE="${1:?Uso: scripts/drive.sh <agente> \"<prompt>\"}"
PROMPT="${2:?prompt obrigatório}"

if [[ ! -f sessions.json ]]; then
    echo "ERRO: sessions.json não existe. Rode scripts/spawn.sh ${AGENTE} primeiro." >&2
    exit 1
fi

SESSION_ID=$(jq -r --arg a "${AGENTE}" '.[$a] // empty' sessions.json)
if [[ -z "${SESSION_ID}" ]]; then
    echo "ERRO: ${AGENTE} não está em sessions.json." >&2
    exit 1
fi

STATUS_FILE="status/${AGENTE}.json"
if [[ -f "${STATUS_FILE}" ]]; then
    HUMAN=$(jq -r '.status // ""' "${STATUS_FILE}")
    if [[ "${HUMAN}" == "human_driving" ]]; then
        echo "ERRO: ${AGENTE} está sob controle humano. Aguarde." >&2
        exit 2
    fi
fi

echo "{\"status\":\"working\",\"started_at\":\"$(date -Iseconds)\",\"task\":\"$(echo "${PROMPT}" | head -c80 | tr '\n' ' ')\"}" > "${STATUS_FILE}"

mkdir -p "logs/${AGENTE}"
LOG="logs/${AGENTE}/current.log"

{
    echo "═════════════════════════════════════════════"
    echo "$(date -Iseconds)  DRIVE  ${AGENTE}"
    echo "prompt: ${PROMPT}"
    echo "─────────────────────────────────────────────"
} >> "${LOG}"

# stream-json emite eventos linha a linha (já é line-delimited). Pipe
# pelo parser Python que transforma em formato humano live.
# --verbose é obrigatório com stream-json pra imprimir todos os eventos.
RC=0
set +e
claude --resume "${SESSION_ID}" \
       -p "${PROMPT}" \
       --permission-mode bypassPermissions \
       --output-format stream-json \
       --include-partial-messages \
       --verbose 2>&1 \
  | python3 "${PROJECT_DIR}/scripts/_stream_pretty.py" \
  >> "${LOG}"
RC=${PIPESTATUS[0]}
set -e

{
    echo ""
    echo "═════════════════════════════════════════════"
    echo "$(date -Iseconds)  DRIVE exit=${RC}"
    echo ""
    # 25 linhas em branco pra empurrar o conteúdo anterior pra fora da
    # viewport. Assim o pane do agente ocioso fica quase vazio —
    # atrai o olho pros painéis que ainda estão ativos.
    for _ in $(seq 1 25); do echo ""; done
    echo "────────── ◇ ocioso · aguardando próximo drive ──────────"
    echo ""
} >> "${LOG}"

echo "{\"status\":\"idle\",\"finished_at\":\"$(date -Iseconds)\"}" > "${STATUS_FILE}"
