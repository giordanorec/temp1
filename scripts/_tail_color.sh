#!/usr/bin/env bash
# Segue um log e prefixa cada linha não-vazia com um bullet colorido
# (símbolo na cor do agente). Deixa o RESTO da linha como está —
# preserva as formatações semânticas (bold/dim/vermelho/verde) emitidas
# pelo _stream_pretty.py.
#
# Uso: _tail_color.sh <color_code> <path_to_log> [bullet_char]
#   bullet_char default: ║ (double vertical)
#
# Armadilha: awk com fflush() não funciona via tmux split-window (stdout
# trava). sed -u (unbuffered by design) é a escolha certa.
set -eu

COLOR="${1:?color required}"
LOG="${2:?log path required}"
BULLET_CHAR="${3:-║}"

ESC=$(printf '\033')
BULLET="${ESC}[38;5;${COLOR}m${BULLET_CHAR}${ESC}[0m "

tail -n +1 -F "${LOG}" | sed -u "/^\$/!s/^/${BULLET}/"
