# 09 — Riscos

Armadilhas conhecidas. Cada risco tem mitigacao documentada. Arquiteto
monitora; cada agente le este arquivo antes de comecar.

## R1. Compute insuficiente no M4

**Risco**: Mac Mini M4 64GB nao tem tensor cores NVIDIA. Throughput
~5-10x menor que A100. Treinar 500M em 50B tokens pode levar semanas.

**Mitigacao**: Comecar com modelo menor (124M via nanochat), iterar
rapido. Treino completo na cloud (Fase 4). M4 serve para prototipagem
e iteracoes rapidas.

## R2. Qualidade dos dados multilinguais

**Risco**: Dados em portugues podem ter qualidade inferior aos em
ingles. Filtragem pode remover conteudo valido.

**Mitigacao**: Usar FineWeb-2 (curado pela HuggingFace com filtros
por idioma) + CulturaX. Validar manualmente amostras antes de treinar.

## R3. Divergencia de treinamento

**Risco**: Loss explode ou plateau prematuro por hiperparametros
errados.

**Mitigacao**: Seguir scaling laws documentadas (MiniCPM, Chinchilla).
Comecar com LR conservador. Checkpoints frequentes. W&B para detectar
problemas cedo.

## R4. Tokenizador ruim para portugues

**Risco**: BPE treinado com peso excessivo em ingles fragmenta
portugues demais (fertility rate alta).

**Mitigacao**: Balancear corpus de treino do tokenizador (50% pt,
40% en, 10% code). Avaliar fertility rate por idioma antes de treinar
o modelo.

## R5. Scope creep

**Risco**: Projeto cresce alem do possivel (multimodal, 7B, etc)
antes de completar o basico.

**Mitigacao**: Fases com criterio de saida rigido. Cada expansao
passa pelo Discovery e entra em DECISOES.md. Nao pular fases.

## R6. Reprodutibilidade

**Risco**: Detalhes de treinamento perdidos, tornando o projeto
nao-reproduzivel.

**Mitigacao**: Logar tudo em W&B. Versionar configs. Checkpoints
intermediarios. DECISOES.md vivo.

---

## Riscos comuns em projetos multi-agente persistente

- **Dois agentes tocam a mesma coisa** — mitigacao: `01_ARQUITETURA.md`
  define divisao explicita; Arquiteto revisa specs antes de despachar.
- **Concorrencia humano vs Arquiteto** — `drive.sh` respeita `status/`
  `human_driving`; `take_over.sh` seta e resseta.
- **Sessoes crescendo demais** — Arquiteto roda `/compact` pos-feature;
  memoria principal mora em `memory/`, nao no history.
