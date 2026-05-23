# 01 — Arquitetura

## Princípio central

{{DESCRICAO_DO_DESIGN_PRINCIPAL}}

## Diagrama

```
{{BLOCO_ASCII_DOS_COMPONENTES}}
```

## Por que essa arquitetura e não outras

**Alternativa A**: {{DESCRICAO}} — descartada porque {{MOTIVO}}.

**Alternativa B** (escolhida): {{DESCRICAO}} — {{VANTAGENS}}.

## Divisão de trabalho por agente

| Agente | Pasta/arquivos de responsabilidade |
|---|---|
| `<agente-1>` | `<pasta>/` |
| `<agente-2>` | `<pasta>/` |

Sem sobreposição: cada pasta pertence a **um** agente. Contratos entre
pastas são documentados em `specs/`.

## Contratos de interface

### {{NOME_DA_INTERFACE}}

```{{LANG}}
{{ASSINATURA_PUBLICA}}
```

Mudanças na interface exigem update em `specs/` e em `docs/DECISOES.md`.
