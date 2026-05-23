# DECISOES.md — log cronologico vivo

Cada entrada e uma decisao nao-trivial com contexto. Preencher no
mesmo commit que materializa a decisao.

---

## 2026-05-23 — Inicio do projeto FarolLM

### Contexto

Giordano quer entender a fundo como se cria uma LLM, treinando uma do
zero. Tem contatos em Oxford, Stanford, Sorbonne que confirmam que
recriar coisas prontas e viavel. Quer um projeto puramente seu,
documentado, e aberto.

### Decisao

- **Nome**: FarolLM
- **Tipo**: SLM (Small Language Model), 300-500M parametros
- **Lingua**: Multilingual (portugues + ingles + code)
- **Dominio**: General purpose inicialmente; especializacao futura
  (codigo, juridico, educacao ou musica — a definir)
- **Stack**: Python/PyTorch + LitGPT + HF Tokenizers + TRL
- **Hardware**: Mac Mini M4 64GB (prototipagem) + cloud GPUs (futuro)
- **Operador**: Uso academico (UFPE)
- **Compliance**: LGPD nao se aplica (dados publicos)
- **Time de agentes**: arquiteto + pipeline-dev + devops-installer +
  qa-tester + docs-writer (4 especialistas)

### Por que / alternativas

- **LitGPT sobre nanochat**: nanochat e educacional (Fase 0), LitGPT
  e producao. Usamos os dois em fases diferentes.
- **PyTorch sobre JAX**: ecossistema mais maduro, Apple MPS suportado,
  mais material educacional. JAX seria melhor com TPUs (Google TRC),
  pode ser explorado na Fase 4.
- **300-500M sobre 1B+**: sweet spot para M4 64GB. Grande o suficiente
  para capacidades emergentes, pequeno o suficiente para iterar rapido.
- **Decoder-only sobre encoder-decoder**: padrao para geracao de texto,
  mais simples, melhor documentado.
- **FineWeb-2 + CulturaX**: melhor cobertura multilingual aberta
  disponivel. FineWeb-2 tem 1000+ idiomas, CulturaX tem forte presenca
  de portugues.

### Consequencias

- Fase 0 (nanochat) bloqueia tudo — e a fundacao de entendimento.
- M4 limita a ~500M params confortavel; scaling precisa de cloud.
- Precisa aplicar para compute grants (Google TRC, NVIDIA) em paralelo
  com Fase 0-1.

---

## 2026-05-23 — Pesquisa do ecossistema

### Contexto

Antes de comecar, fizemos varredura completa do que existe disponivel.

### Decisao

Documento completo em `docs/PESQUISA_LLM.md`. Cobre frameworks,
datasets, papers, custos, hardware e casos de sucesso.

### Destaques

- OLMo (AI2) e o unico modelo 100% reproduzivel (codigo + dados + logs)
- nanochat (Karpathy) e o melhor ponto de partida educacional (~$100)
- TinyLlama provou que 1.1B em 3T tokens funciona em 16xA100 em 90 dias
- FineWeb-2 tem 15T tokens em 1000+ idiomas (maior dataset aberto)
- Google TRC oferece TPUs gratis para pesquisadores (aceita internacionais)
- Custo estimado para 500M em 20B tokens: ~$50-100 em cloud

---
