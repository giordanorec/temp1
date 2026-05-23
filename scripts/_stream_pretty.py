#!/usr/bin/env python3
"""Parseia stream-json do claude e imprime em formato visual rico,
à la Claude Code rodando no terminal.

Design:
- Cada tipo de tool tem emoji + cor próprios.
- Edit mostra diff visual: linha antiga com fundo vermelho escuro,
  linha nova com fundo verde escuro.
- Results OK em dim verde; erros com badge [ERR] fundo vermelho.
- Resultado final numa "box" com bordas e métricas em magenta.
- Texto narrativo do assistant em branco, live typing.

Não usa cor do agente — essa vem do `_tail_color.sh` via `║` colorido
no início de cada linha. O parser emite cores SEMÂNTICAS no resto da
linha, que convivem com o marcador.
"""
import json
import sys

# Atributos ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Foreground
FG_BLACK = "\033[30m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[97m"
FG_GRAY = "\033[90m"

# Foreground bright
FG_B_RED = "\033[91m"
FG_B_GREEN = "\033[92m"
FG_B_YELLOW = "\033[93m"
FG_B_BLUE = "\033[94m"
FG_B_MAGENTA = "\033[95m"
FG_B_CYAN = "\033[96m"

# Background (apenas pra destaque forte)
BG_RED = "\033[48;5;52m"   # vermelho escuro
BG_GREEN = "\033[48;5;22m" # verde escuro
BG_YELLOW = "\033[48;5;58m" # amarelo escuro
BG_RED_BRIGHT = "\033[48;5;160m"


# Mapa de tool → (emoji, cor, label-curto).
# Emojis Unicode monospace-friendly. Cor semântica por tipo:
# - Read/info = azul
# - Write/create = verde
# - Edit/modify = amarelo
# - Bash/exec = magenta
# - Grep/search = cyan
# - Task/meta = rosa
# - Web/remote = cyan
TOOLS = {
    "Read":         ("📖", FG_B_BLUE,    "Read"),
    "Write":        ("📝", FG_B_GREEN,   "Write"),
    "Edit":         ("✏️ ", FG_B_YELLOW,  "Edit"),
    "NotebookRead": ("📓", FG_B_BLUE,    "NotebookRead"),
    "NotebookEdit": ("📓", FG_B_YELLOW,  "NotebookEdit"),
    "Bash":         ("⚡", FG_B_MAGENTA, "Bash"),
    "Grep":         ("🔍", FG_B_CYAN,    "Grep"),
    "Glob":         ("🗂️ ", FG_B_CYAN,    "Glob"),
    "TaskCreate":   ("📋", FG_B_MAGENTA, "TaskCreate"),
    "TaskUpdate":   ("✅", FG_B_MAGENTA, "TaskUpdate"),
    "TaskList":     ("📋", FG_B_MAGENTA, "TaskList"),
    "WebFetch":     ("🌐", FG_B_CYAN,    "WebFetch"),
    "WebSearch":    ("🔎", FG_B_CYAN,    "WebSearch"),
    "Skill":        ("🧩", FG_B_MAGENTA, "Skill"),
    "Agent":        ("🤖", FG_B_MAGENTA, "Agent"),
}
TOOL_DEFAULT = ("🔧", FG_CYAN, None)


def trunc(s, n=140):
    s = str(s).replace("\n", " ⏎ ")
    return s if len(s) <= n else s[: n - 1] + "…"


def fmt_tool_input(name, inp):
    """Retorna (args_string, diff_lines_or_None).

    diff_lines é usado apenas por Edit — é uma tupla (old, new) pra mostrar
    diff visual. Para outros tools, retorna None.
    """
    if not isinstance(inp, dict):
        return trunc(inp), None
    if name in ("Write", "Read", "NotebookRead"):
        return inp.get("file_path", ""), None
    if name == "Edit":
        p = inp.get("file_path", "")
        old = inp.get("old_string", "")
        new = inp.get("new_string", "")
        return p, (old, new)
    if name == "NotebookEdit":
        return inp.get("notebook_path", ""), None
    if name == "Bash":
        return trunc(inp.get("command", ""), 160), None
    if name == "Grep":
        pat = inp.get("pattern", "")
        path = inp.get("path", "")
        return (f"{pat}" + (f"  @ {path}" if path else "")), None
    if name == "Glob":
        return inp.get("pattern", ""), None
    if name == "TaskCreate":
        return trunc(inp.get("subject", ""), 80), None
    if name == "TaskUpdate":
        tid = inp.get("taskId", "")
        st = inp.get("status", "")
        return (f"#{tid} → {st}" if st else f"#{tid}"), None
    return trunc(json.dumps(inp, ensure_ascii=False), 120), None


def fmt_tool_result(content):
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
            else:
                parts.append(str(c))
        content = " ".join(parts)
    return trunc(content, 120)


def render_diff(old, new, max_lines_per_side=3):
    """Renderiza diff visual do Edit — linhas removidas com fundo vermelho
    escuro, adicionadas com fundo verde escuro. Trunca pra max_lines.
    Imprime indented sob a linha do tool."""
    old_lines = (old or "").splitlines() or [""]
    new_lines = (new or "").splitlines() or [""]

    def emit(lines, bg, prefix, color):
        shown = lines[:max_lines_per_side]
        for ln in shown:
            # bg + espaço + prefixo + linha truncada + padding-ish + reset
            sys.stdout.write(f"    {bg}{color} {prefix} {trunc(ln, 100)}{RESET}\n")
        if len(lines) > max_lines_per_side:
            sys.stdout.write(
                f"    {DIM}{FG_GRAY}    (+{len(lines) - max_lines_per_side} linhas){RESET}\n"
            )

    emit(old_lines, BG_RED, "-", FG_B_RED)
    emit(new_lines, BG_GREEN, "+", FG_B_GREEN)
    sys.stdout.flush()


current_block_type = None
current_tool_name = None
current_tool_input_json = ""


def handle_stream_event(ev):
    global current_block_type, current_tool_name, current_tool_input_json
    inner = ev.get("event", {}) or {}
    et = inner.get("type")

    if et == "content_block_start":
        block = inner.get("content_block", {}) or {}
        current_block_type = block.get("type")
        if current_block_type == "tool_use":
            current_tool_name = block.get("name", "?")
            current_tool_input_json = ""

    elif et == "content_block_delta":
        delta = inner.get("delta", {}) or {}
        dt = delta.get("type")
        if dt == "text_delta":
            sys.stdout.write(delta.get("text", ""))
            sys.stdout.flush()
        elif dt == "input_json_delta":
            current_tool_input_json += delta.get("partial_json", "")

    elif et == "content_block_stop":
        if current_block_type == "text":
            sys.stdout.write(RESET + "\n")
            sys.stdout.flush()
        elif current_block_type == "tool_use":
            try:
                inp = json.loads(current_tool_input_json) if current_tool_input_json else {}
            except json.JSONDecodeError:
                inp = {}
            args, diff = fmt_tool_input(current_tool_name, inp)
            emoji, color, label = TOOLS.get(current_tool_name, TOOL_DEFAULT)
            name_label = label or current_tool_name
            sys.stdout.write(
                f"{emoji} {BOLD}{color}{name_label}{RESET} "
                f"{FG_GRAY}·{RESET} {DIM}{args}{RESET}\n"
            )
            sys.stdout.flush()
            if diff is not None:
                render_diff(*diff)
        current_block_type = None
        current_tool_name = None
        current_tool_input_json = ""


def handle_user(ev):
    msg = ev.get("message", {}) or {}
    for c in msg.get("content", []) or []:
        if isinstance(c, dict) and c.get("type") == "tool_result":
            preview = fmt_tool_result(c.get("content", ""))
            if c.get("is_error"):
                print(
                    f"  {BG_RED_BRIGHT}{FG_WHITE}{BOLD} ERRO {RESET} "
                    f"{FG_B_RED}{preview}{RESET}",
                    flush=True,
                )
            else:
                print(
                    f"  {FG_GREEN}└─{RESET} {DIM}{preview}{RESET}",
                    flush=True,
                )


def handle_result(ev):
    sub = ev.get("subtype", "")
    dur = ev.get("duration_ms")
    cost = ev.get("total_cost_usd")
    ok = sub == "success"
    badge_bg = BG_GREEN if ok else BG_RED_BRIGHT
    badge_fg = FG_B_GREEN if ok else FG_WHITE
    badge = f"{badge_bg}{FG_WHITE}{BOLD} {sub.upper()} {RESET}"
    metrics = []
    if dur:
        metrics.append(f"{dur/1000:.1f}s")
    if cost:
        metrics.append(f"${cost:.4f}")
    metrics_str = f"{FG_GRAY} · {FG_B_MAGENTA}{'  ·  '.join(metrics)}{RESET}" if metrics else ""
    print(
        f"\n{badge_fg}╭─ resultado ─────────────────{RESET}\n"
        f"  {badge}{metrics_str}\n"
        f"{badge_fg}╰──────────────────────────────{RESET}",
        flush=True,
    )


for raw in sys.stdin:
    raw = raw.strip()
    if not raw or raw[0] not in "{[":
        continue
    try:
        ev = json.loads(raw)
    except Exception:
        continue

    t = ev.get("type")
    if t == "stream_event":
        handle_stream_event(ev)
    elif t == "user":
        handle_user(ev)
    elif t == "result":
        handle_result(ev)
