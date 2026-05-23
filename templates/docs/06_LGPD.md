# 06 — LGPD

**Só aplicável** se o projeto coleta/processa dados pessoais. Se não,
delete este arquivo.

## Base legal

{{LEGITIMO_INTERESSE | CONSENTIMENTO | EXECUCAO_DE_CONTRATO | ...}}

## Finalidade específica

{{PARA_QUE_OS_DADOS_SAO_USADOS}}

## Balanceamento (se legítimo interesse)

{{POR_QUE_O_BENEFICIO_SUPERA_O_IMPACTO}}

## Campos obrigatórios de auditoria

Toda linha de registro deve ter:
- `data_primeira_coleta`
- `fonte_origem`
- `opt_out` (boolean)

## Tabela de opt-outs

`opt_outs` — guarda hashes SHA-256 (nunca email/telefone em claro).

## Retenção

- **Ativos**: {{PRAZO}}
- **Opt-outs**: indefinido (pra não re-coletar).

## Canal de opt-out

Link/endereço incluído em toda comunicação enviada.

## Plano em caso de incidente

{{PASSO_A_PASSO}}
