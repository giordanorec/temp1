---
description: "Spawna um novo especialista num projeto já iniciado"
argument-hint: "<nome-do-agente> (ex frontend-dev, dba, llm-prompt)"
---

Spawna um agente especialista adicional no projeto corrente.

## Pré-requisitos

- Projeto já inicializado com `/multiagente-init` (tem `scripts/spawn.sh`,
  `.claude/agents/`, `sessions.json`).
- Argumento obrigatório: `$ARGUMENTS` = nome do agente.

## Passo 0 — Descobrir plugin root

```bash
PLUGIN_ROOT=$(find ~/.claude/plugins/cache -maxdepth 5 -type d \
    -path "*/multiagentes-giordano/*" -name "scripts" 2>/dev/null \
  | head -1 | xargs -r dirname)
```

## Processo

1. **Validar argumento**: se `$ARGUMENTS` vazio, peça o nome do agente.

2. **Verificar se o agente-file existe**:
   - Se `./.claude/agents/$ARGUMENTS.md` existir, ok, prossiga.
   - Se não existir, procure em `$PLUGIN_ROOT/agents/$ARGUMENTS.md`:
     - Se encontrar, copie para `.claude/agents/`:
       ```bash
       cp "$PLUGIN_ROOT/agents/$ARGUMENTS.md" ".claude/agents/"
       ```
     - Se não encontrar nem no plugin: liste os templates disponíveis
       (`ls "$PLUGIN_ROOT/agents/"`) e peça pro usuário escolher, ou
       ofereça criar do zero com frontmatter mínimo.

3. **Verificar se não está duplicado**: se o agente já está em
   `sessions.json`, avise que já existe e sugira `/multiagente-dashboard`
   pra ver os painéis.

4. **Spawnar**: `scripts/spawn.sh "$ARGUMENTS"`.

5. **Atualizar dashboard**: `scripts/open_dashboard.sh --rebuild`.

6. **Reportar**: session_id, cor atribuída no dashboard, próxima
   sugestão de spec pra ele.
