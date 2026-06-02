# 09 — Riscos

Armadilhas conhecidas. Cada risco tem mitigação documentada. Arquiteto
monitora; cada agente lê este arquivo antes de começar.

## R1. {{NOME_DO_RISCO}}

**Risco**: {{DESCRICAO_DO_RISCO}}

**Mitigação**: {{COMO_EVITAR_OU_DETECTAR}}

## R2. ...

---

## Riscos comuns em projetos multi-agente persistente

- **Dois agentes tocam a mesma coisa** — mitigação: `01_ARQUITETURA.md`
  define divisão explícita; Arquiteto revisa specs antes de despachar
  e rejeita sobreposição.
- **Concorrência humano vs Arquiteto** — `drive.sh` respeita `status/`
  `human_driving`; `take_over.sh` seta e resseta.
- **Sessões crescendo demais** — Arquiteto roda `/compact` pós-feature;
  memória principal mora em `memory/`, não no history.
- **Gargalo no Arquiteto** — specs bem escritas deixam especialistas
  rodarem autônomos mais tempo; reports em lote.
