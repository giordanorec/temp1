#!/usr/bin/env bash
# Usado pela status bar do tmux. Imprime contagem de agentes por estado.
# Saída: " ⦿ idle: N  ◐ working: N  ✋ human: N "
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

idle=0
working=0
human=0

shopt -s nullglob
for f in status/*.json; do
    s=$(jq -r '.status // "unknown"' "$f" 2>/dev/null || echo "unknown")
    case "$s" in
        idle)          idle=$((idle+1)) ;;
        working)       working=$((working+1)) ;;
        human_driving) human=$((human+1)) ;;
    esac
done

# Cores tmux-style inline (#[fg=colour...])
printf '#[fg=colour244]⦿ idle %d#[default]  #[fg=colour118,bold]◐ working %d#[default]  #[fg=colour208,bold]✋ human %d#[default]' \
    "$idle" "$working" "$human"
