# 10 — Primeiros passos (Fase 3 — Setup)

Roteiro executado pelo Arquiteto (ou pelo `devops-installer` quando já
spawnado).

## Passo 1. Git + estrutura de pastas

```bash
git init -b main
mkdir -p .claude/agents docs specs reports memory status logs scripts
```

## Passo 2. Stack

{{COMANDOS_DE_INSTALACAO_DO_STACK}}

## Passo 3. Configurações

{{ARQUIVOS_DE_CONFIG_PRINCIPAIS}}

## Passo 4. Smoke test

{{COMANDO_QUE_VALIDA_O_SETUP}}

## Passo 5. Primeiro commit + repo remoto

```bash
git add -A
git commit -m "feat: scaffold inicial"
gh repo create {{USUARIO}}/{{NOME}} --private --source=. --push
```

## Passo 6. Spawn dos agentes

```bash
for agente in {{LISTA_DOS_AGENTES}}; do
    scripts/spawn.sh "$agente"
done
```

## Passo 7. Abrir dashboard

```bash
scripts/open_dashboard.sh
```

## Passo 8. Entrar na Fase 4

Arquiteto escreve `specs/F4-<primeira-feature>.md` e despacha 2-3
especialistas em paralelo.
