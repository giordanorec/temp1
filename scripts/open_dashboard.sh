#!/usr/bin/env bash
# Dashboard tmux do old-lady-game.
# - um painel por agente, tile layout
# - cor distinta por agente, aplicada no conteúdo (via awk) e no título
# - bordas heavy, título colorido na borda superior
# - status bar dinâmica com contagem idle/working/human a cada 2s
#
# Uso:
#   scripts/open_dashboard.sh              # Tilix (default)
#   scripts/open_dashboard.sh --attach     # attach no terminal atual
#   scripts/open_dashboard.sh --gnome      # gnome-terminal
#   scripts/open_dashboard.sh --detach     # só cria, não abre UI
#   scripts/open_dashboard.sh --rebuild    # mata e recria a sessão
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"
PROJECT_NAME="$(basename "${PROJECT_DIR}")"
SESSION="${PROJECT_NAME}-dash"

MODE="tilix"
REBUILD=0
for arg in "$@"; do
    case "${arg}" in
        --attach)  MODE="attach" ;;
        --gnome)   MODE="gnome"  ;;
        --detach)  MODE="detach" ;;
        --rebuild) REBUILD=1     ;;
        --help)
            grep '^#' "$0" | head -16
            exit 0
            ;;
    esac
done

if ! command -v tmux >/dev/null; then
    echo "ERRO: tmux não instalado." >&2
    exit 1
fi
if [[ ! -f sessions.json ]]; then
    echo "ERRO: sessions.json não existe. Rode scripts/spawn.sh <agente> primeiro." >&2
    exit 1
fi

AGENTES=($(jq -r 'keys[]' sessions.json))
if [[ ${#AGENTES[@]} -eq 0 ]]; then
    echo "ERRO: sessions.json vazio." >&2
    exit 1
fi

# Paleta 256 colors — cores saturadas, legíveis sobre fundo escuro,
# escolhidas pra terem bom contraste entre si.
COLORS=(208 45 118 213 226 75 141 198 51 156 220 171 33 214 81 183)

# Marcador do início de cada linha. Default: apenas ▊ em todos.
# Pra testar símbolos lado a lado, defina BULLETS_TEST como lista no
# ambiente (ciclada pelos panes). Exemplo:
#   BULLETS_TEST="▊ ◇ ⟫ ◎" scripts/open_dashboard.sh --rebuild
if [[ -n "${BULLETS_TEST:-}" ]]; then
    # shellcheck disable=SC2206
    BULLETS=( ${BULLETS_TEST} )
else
    BULLETS=("║")
fi

for agente in "${AGENTES[@]}"; do
    mkdir -p "logs/${agente}"
    touch "logs/${agente}/current.log"
done

# Comando rodado dentro de cada painel: delega pro helper _tail_color.sh
# que faz tail + sed-colorize. Aceita bullet char como 3º arg.
make_pane_cmd() {
    local color="$1" log="$2" bullet="$3"
    printf "%q %q %q %q" "${PROJECT_DIR}/scripts/_tail_color.sh" \
        "${color}" "${log}" "${bullet}"
}

# Título colorido com bullet decorativo. Vai na pane-border.
make_pane_title() {
    local color="$1" name="$2"
    printf "#[fg=colour%s,bold]●#[default] #[fg=colour%s]%s#[default]" \
        "$color" "$color" "$name"
}

if [[ ${REBUILD} -eq 1 ]] && tmux has-session -t "${SESSION}" 2>/dev/null; then
    tmux kill-session -t "${SESSION}"
    echo "→ sessão antiga destruída."
fi

if tmux has-session -t "${SESSION}" 2>/dev/null; then
    echo "→ sessão tmux '${SESSION}' já existe, reanexando."
else
    FIRST="${AGENTES[0]}"
    FIRST_COLOR="${COLORS[0]}"
    FIRST_BULLET="${BULLETS[0]}"

    tmux new-session -d -s "${SESSION}" -n "agents" \
        "$(make_pane_cmd "${FIRST_COLOR}" "logs/${FIRST}/current.log" "${FIRST_BULLET}")"
    tmux select-pane -t "${SESSION}" -T "$(make_pane_title "${FIRST_COLOR}" "${FIRST}")"

    for i in "${!AGENTES[@]}"; do
        [[ $i -eq 0 ]] && continue
        agente="${AGENTES[$i]}"
        color="${COLORS[$((i % ${#COLORS[@]}))]}"
        bullet="${BULLETS[$((i % ${#BULLETS[@]}))]}"
        tmux split-window -t "${SESSION}" \
            "$(make_pane_cmd "${color}" "logs/${agente}/current.log" "${bullet}")"
        tmux select-pane -t "${SESSION}" -T "$(make_pane_title "${color}" "${agente}")"
        tmux select-layout -t "${SESSION}" tiled >/dev/null
    done
    tmux select-layout -t "${SESSION}" tiled >/dev/null

    # Bordas: linhas heavy, título no topo, ativo destacado
    tmux set -t "${SESSION}" pane-border-status top >/dev/null
    tmux set -t "${SESSION}" pane-border-format ' #{pane_title} ' >/dev/null
    tmux set -t "${SESSION}" pane-border-lines 'heavy' >/dev/null 2>&1 || true
    tmux set -t "${SESSION}" pane-border-style 'fg=colour238' >/dev/null
    tmux set -t "${SESSION}" pane-active-border-style 'fg=colour231,bold' >/dev/null
    tmux set -t "${SESSION}" pane-border-indicators 'colour' >/dev/null 2>&1 || true

    # Status bar dinâmica (refresh a cada 2s, chama _status_summary.sh)
    tmux set -t "${SESSION}" status on >/dev/null
    tmux set -t "${SESSION}" status-interval 2 >/dev/null
    tmux set -t "${SESSION}" status-bg 'colour234' >/dev/null
    tmux set -t "${SESSION}" status-fg 'colour252' >/dev/null
    tmux set -t "${SESSION}" status-justify 'centre' >/dev/null
    tmux set -t "${SESSION}" status-left-length 40 >/dev/null
    tmux set -t "${SESSION}" status-right-length 120 >/dev/null
    tmux set -t "${SESSION}" status-left " #[fg=colour208,bold]◆ ${PROJECT_NAME} #[fg=colour238]│#[default] " >/dev/null
    tmux set -t "${SESSION}" status-right "#(${PROJECT_DIR}/scripts/_status_summary.sh)  #[fg=colour238]│#[fg=colour45,bold] %H:%M #[default]" >/dev/null

    tmux set -t "${SESSION}" mouse on >/dev/null 2>&1 || true
    tmux set -t "${SESSION}" history-limit 50000 >/dev/null 2>&1 || true

    # Atalho ergonômico pra maximizar/minimizar painel: prefix + Enter.
    # (Ctrl+B z continua funcionando — este é adicional.)
    tmux bind-key -T prefix Enter resize-pane -Z >/dev/null 2>&1 || true

    echo "→ sessão tmux '${SESSION}' criada com ${#AGENTES[@]} painéis."
fi

case "${MODE}" in
    tilix)
        if command -v tilix >/dev/null; then
            tilix -e "tmux attach -t ${SESSION}" >/dev/null 2>&1 &
            disown
            echo "→ abriu no Tilix."
        else
            echo "⚠ Tilix não encontrado, usando gnome-terminal."
            gnome-terminal -- tmux attach -t "${SESSION}" 2>/dev/null &
            disown
        fi
        ;;
    gnome)
        gnome-terminal -- tmux attach -t "${SESSION}" &
        disown
        ;;
    attach)
        exec tmux attach -t "${SESSION}"
        ;;
    detach)
        echo "→ sessão existe em background. attach:  tmux attach -t ${SESSION}"
        ;;
esac

cat <<EOF

atalhos tmux:
   Ctrl+B z         MAXIMIZAR/minimizar o painel atual (alt: Ctrl+B Enter)
   Ctrl+B +seta     navegar entre painéis
   Ctrl+B d         detach (sessão continua viva)
   Ctrl+B [         modo scroll (q sai)
   mouse click      selecionar painel

reconstruir:  scripts/open_dashboard.sh --rebuild
EOF
