# Propostas de Compute Grants — FarolLM

Rascunhos de aplicacao para programas de compute gratuito/subsidiado.

---

## 1. Google TPU Research Cloud (TRC)

**URL:** https://sites.research.google/trc/about/
**Aprovacao:** ~3-4 dias uteis (rolling basis)
**Recurso:** TPU v2/v3/v4, 30 dias renovaveis

### Proposta

**Project title:** FarolLM — Training a multilingual small language model from scratch

**Description:**

FarolLM is a research project to build and openly publish a 300-500M
parameter multilingual (Portuguese + English) language model, trained
entirely from scratch — tokenizer, architecture, pre-training, and
alignment — documenting every decision for full reproducibility.

The project addresses the gap in openly documented LLM training
pipelines. While many open-weight models exist (LLaMA, Mistral, Qwen),
very few publish their complete training code, data pipeline, and
decision log. FarolLM aims to be fully transparent: every architectural
choice, hyperparameter decision, and training curve will be documented
and published.

**Architecture:** Decoder-only Transformer (Llama-style) with RoPE,
SwiGLU, Grouped-Query Attention (16Q/4KV), and RMSNorm. 304M parameters.
The architecture is already implemented and tested (19 automated tests
passing, including end-to-end pipeline validation).

**Data:** FineWeb-2 (multilingual, 15T+ tokens across 1000+ languages)
and CulturaX (6.3T tokens, 167 languages with strong Portuguese coverage).
Target: 20-100B tokens for pre-training.

**Why TPU:** Pre-training a 300M+ model on 20-100B tokens of multilingual
data requires significant compute beyond consumer hardware (Mac Mini M4
64GB). TPU access would enable training at scale and experimentation
with larger model variants (up to 1B parameters).

**Outputs (all will be published openly):**
- Full training code on GitHub (MIT license)
- Model weights and tokenizer on Hugging Face
- Training logs and W&B dashboards
- Complete decision log documenting every non-trivial choice
- Academic paper describing the pipeline and findings
- Blog posts for the broader community

**Framework:** PyTorch (architecture already implemented). Open to
migrating pre-training to JAX/MaxText for TPU-optimized performance.

**Affiliation:** Centro de Informatica (CIn), Universidade Federal
de Pernambuco (UFPE), Recife, Brazil.

**Contact:** grec@cin.ufpe.br

**Typical dataset size:** 20-100B tokens (40-200GB tokenized)

**Typical training time:** Days to weeks depending on model size and
token budget.

**Hardware currently used:** Mac Mini M4 64GB (Apple Silicon). Limited
to prototyping and small-scale experiments.

---

## 2. Google Cloud Research Credits

**URL:** https://edu.google.com/intl/ALL_us/programs/credits/research/
**Valor:** Ate $1.000 (PhD) ou $5.000 (faculty/pos-doc)
**Aprovacao:** 4-6 semanas

### Proposta

Use a mesma descricao do TRC acima, adaptando para o formato do
formulario. Destacar que os creditos serao usados para:
- Cloud TPU/GPU compute para pre-treinamento
- Google Cloud Storage para datasets (FineWeb-2, CulturaX)
- Vertex AI para avaliacao e inferencia

---

## 3. NVIDIA Academic Grant Program

**URL:** https://www.nvidia.com/en-us/industries/higher-education-research/academic-grant-program/
**Recurso:** Ate 30.000 horas de H100 80GB
**Requisito:** Precisa de PI (Professor/Pesquisador principal)

### Proposta

**Project title:** FarolLM: Open-Source Multilingual Small Language
Model Training Pipeline

**Principal Investigator:** [Professor orientador na UFPE/CIn]

**Co-PI / PhD Student:** Giordano Ribeiro Eulalio Cabral

**Research objectives:**
1. Train a 300M-1B parameter multilingual language model from scratch
2. Document and publish the complete training pipeline for reproducibility
3. Investigate optimal data mixing strategies for Portuguese-English
   multilingual pre-training
4. Evaluate the impact of tokenizer design on multilingual performance

**Compute requirements:**
- 500-4.000 GPU hours of H100 for pre-training experiments
- Multiple runs for hyperparameter search and ablation studies
- Estimated total: 5.000-10.000 GPU hours across all experiments

**Expected outputs:**
- Open-source codebase (MIT)
- Trained model weights on Hugging Face
- Academic paper (target: ACL, EMNLP, or NAACL workshop)
- Technical blog posts

**Note:** Precisa vincular a um professor orientador na UFPE como PI.

---

## 4. AWS Cloud Credit for Research

**URL:** https://aws.amazon.com/government-education/research-and-technical-computing/cloud-credit-for-research/
**Valor:** Ate $5.000 (estudantes)
**Aprovacao:** 90-120 dias

### Proposta

Mesma descricao, adaptando para AWS:
- Usar instancias P4d (A100) ou P5 (H100) para pre-treinamento
- S3 para armazenamento de datasets
- SageMaker para monitoramento

---

## 5. Kaggle (acesso imediato)

**URL:** https://www.kaggle.com/
**Recurso:** 30h/semana de GPU (T4/P100) + TPU v3-8 gratis
**Requisito:** Nenhum — criar conta e usar

Util para:
- Prototipar tokenizador em escala
- Treinar modelo small (< 100M) para validar pipeline
- Avaliar modelos com lm-evaluation-harness

---

## 6. Lambda Labs Research Credits

**URL:** https://lambda.ai/research-credits
**Valor:** Ate $5.000 em creditos GPU
**Requisito:** Pesquisador academico

### Proposta

Adaptar a mesma proposta do TRC para o formato Lambda.
GPUs disponiveis: A100, H100.

---

## 7. CoreWeave Academic Program

**URL:** https://www.coreweave.com/ (verificar programa academico)
**Recurso:** Creditos GPU para pesquisa
**Nota:** Verificar disponibilidade atual do programa academico.

---

## Estrategia recomendada

1. **Imediato:** Aplicar ao Google TRC (3-4 dias) + criar conta Kaggle
2. **Semana 1:** Aplicar ao Google Cloud Research Credits
3. **Semana 2:** Aplicar ao AWS Research Credits + Lambda Labs
4. **Com PI:** Aplicar ao NVIDIA Academic Grant (30.000h H100)
5. **Paralelo:** Usar Kaggle TPU para prototipar pipeline em JAX

Nao sao mutuamente exclusivos — pode ter acesso a todos simultaneamente.
