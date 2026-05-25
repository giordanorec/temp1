# Inovacoes Globais em LLM/SLM (Fora dos EUA) — 2025-2026

Levantamento de inovacoes tecnicas por pais. Foco em contribuicoes
implementaveis num projeto from-scratch como o FarolLM.

---

## China

### DeepSeek (V3, R1)
- **MLA (Multi-Head Latent Attention)**: comprime KV cache ~10x via
  projecao low-rank. Na inferencia, projecoes sao absorvidas — attention
  computada diretamente no espaco latente. Paper: arXiv:2412.19437.
  Codigo: github.com/deepseek-ai/DeepSeek-V3
- **MoE sem loss auxiliar**: bias dinamico por expert (gamma adjustment)
  em vez de loss que degrada qualidade. arXiv:2408.15664
- **MTP (Multi-Token Prediction)**: prediz D tokens futuros, >80%
  acceptance rate para speculative decoding, ~1.8x inference speedup
- **FP8 treinamento**: tile quantization (1x128 per-token, 128x128
  per-block), <0.25% loss delta vs BF16
- Scale: 671B total, 37B ativo, 14.8T tokens, custo $5.6M

### Qwen / Alibaba (3, 3.5, 3.6)
- **Hybrid GatedDeltaNet + Attention**: 75% layers linear (GDN) +
  25% softmax attention. GDN usa delta rule + exponential gating +
  CausalConv1D. Estado recorrente fixo O(1) vs KV cache O(n).
  github.com/QwenLM/Qwen3.6
- **Qwen3-Next-80B-A3B**: ultra-sparse MoE (80B total, 3B ativo)
- **Qwen3.5-397B-A17B**: 512 experts, 10+1 ativos, 201 linguas
- **Qwen3.6-27B**: dense, supera modelos frontier em coding/agency
- Paper: arXiv:2505.09388

### MiniCPM (Tsinghua / ModelBest)
- **WSD Scheduler**: warmup-stable-decay sem precisar definir steps
  totais. Ja implementado no FarolLM. arXiv:2404.06395
- **Model wind tunnel**: busca de HP em modelos <100M, transfere
  via mu-parametrizacao

### Moonshot AI / Kimi K2
- **MuonClip**: Muon + QK-Clip (tau=100). Zero loss spikes em 15.5T
  tokens de treinamento. 1.04T total, 32B ativo, 384 experts.
  github.com/moonshotai/Kimi-K2. arXiv:2507.20534

### GLM-4.5 (Zhipu AI)
- 355B/32B MoE, thinking/non-thinking hybrid, 23T tokens, MIT license

---

## Japao

### LLM-jp-4 (National Institute of Informatics)
- Comunidade de 2.600+ participantes. 8B dense + 32B-A3B MoE.
  12T tokens, 65K context. Supera GPT-4o e Qwen3-8B em varios
  benchmarks. Fully open. huggingface.co/llm-jp

### PLaMo 2 (Preferred Networks)
- **Hybrid SSM + Sliding Window Attention** (Samba-based).
  Alterna Mamba2 e SWA. Pruning eficiente: 8B iguala 100B anterior.
  arXiv:2509.04897. huggingface.co/pfnet/plamo-2-8b

### Sakana AI
- **Evolutionary Model Merging**: algoritmos evolutivos para descobrir
  combinacoes otimas de modelos open-source sem retreino.
  Publicado na Nature Machine Intelligence. arXiv:2403.13187

### Stockmark-2-100B
- 100B scratch-built, MIT, focado em dominio industrial japones

### Rakuten AI 3.0
- ~700B MoE (671B/37B), 128K context, Apache 2.0. Arquitetura
  similar a DeepSeek-V3.

---

## Coreia do Sul

### Upstage SOLAR
- **Depth Up-Scaling (DUS)**: escala modelos adicionando layers +
  continual pretraining. SOLAR-10.7B iguala modelos 3-4x maiores.
  Sem mudancas em frameworks. arXiv:2312.15166

### Naver HyperCLOVA X
- 6.500x mais dados em coreano que GPT-4. Serving disaggregado
  com 3x reducao de latencia.

### Iniciativa soberana sul-coreana
- 3 equipes (LG AI, SK Telecom, Upstage) desenvolvendo modelos
  foundation com meta de 95% performance do ChatGPT.

---

## Alemanha

### Aleph Alpha — T-Free Architecture
- **Tokenizer-Free LLM**: processa texto diretamente em bytes/chars
  com modelo hierarquico. ~7 chars/vetor vs ~4 tradicional. Reduz
  parametros de embedding em 85%. Transfer cross-lingual natural.
  arXiv:2406.19223. (Cohere adquiriu Aleph Alpha em abr/2026)

### OpenEuroLLM
- Consorcio de 20 instituicoes europeias. LLMs cobrindo 24 linguas
  da UE. Financiado pelo EC Digital Europe Programme. openeurollm.eu

---

## Franca

### Mistral AI
- **Mistral Small 4** (mar/2026): 119B total, 6B ativo, 128 experts,
  4 ativos. Unifica reasoning + vision + code.
- **Mistral Large 3** (dez/2025): 675B/41B, 256K context, 40+ linguas
- **Ministral 3** (dez/2025): Dense 3B/7B/14B, 14B reasoning = 85% AIME

### CroissantLLM
- **Blueprint para SLM bilingual**: 1.3B, 3T tokens, ratio 1:1
  frances:ingles. Tokenizador otimizado para bilinguismo.
  Supera Bloom 3B em tarefas francesas. arXiv:2402.00786.
  **Muito relevante pro FarolLM (pt:en 1:1).**

---

## Reino Unido

### Google DeepMind (Londres)
- **Gemma 4**: sliding window + global, Per-Layer Embeddings (PLE)
  para rodar em mobile. 256K context. Apache 2.0.
- **Gemma 3n**: PLE reduz RAM significativamente, 4B roda como 2B.
- **Gemma Scope 2**: interpretabilidade open-source.

### Cohere
- **Tiny Aya** (fev/2026): 3.35B, 70+ linguas, roda em laptop.
  Relevante para multilingual SLM.

---

## Singapura

### AI Singapore — SEA-LION
- Familia open-source para 11 linguas do sudeste asiatico.
  v4: multimodal, 256K context, OCR regional.
  SEA-LION-Embedding: SOTA para 10 linguas regionais.
  arXiv:2504.05747. github.com/aisingapore/sealion

---

## Israel

### AI21 Labs — Jamba
- **Hybrid Mamba-Transformer + MoE**: ratio 1:7 attention:Mamba,
  MoE a cada 2 layers. 256K context, 3x throughput vs Transformer
  puro em sequencias longas. Jamba 1.5: 398B/94B.
  arXiv:2403.19887. ICLR 2025.

---

## India

### Sarvam AI — Indus (105B)
- Sparse MoE 105B/10.3B, MLA-style, 12T tokens, 22 linguas indianas
  incluindo romanizado e code-mixed (Hinglish). Apache 2.0.
  Construido inteiramente na India.

### Krutrim AI
- Tokenizacao otimizada para linguas indicas (Devanagari, Tamil, etc).
  arXiv:2502.09642

---

## Emirados Arabes (UAE)

### TII Falcon H1
- **Parallel Hybrid Mamba-Transformer**: attention e SSM rodam
  simultaneamente (nao sequencialmente como Jamba). Outputs
  concatenados. 0.5B a 34B, 18 linguas, 256K context.
  falconllm.tii.ae/falcon-h1.html

### Falcon H1R 7B
- Variante de reasoning que supera modelos 7x maiores.

---

## Inovacoes mais relevantes para o FarolLM

| Inovacao | Origem | Aplicabilidade |
|---|---|---|
| **CroissantLLM (bilingual 1:1)** | Franca | Blueprint direto para pt:en 1:1 |
| **GatedDeltaNet hybrid** | Qwen (China) | Linear attention + softmax, O(1) state |
| **T-Free (tokenizer-free)** | Alemanha | Elimina tokenizador, multilingual natural |
| **WSD scheduler** | MiniCPM (China) | Ja implementado |
| **MuonClip** | Kimi (China) | Estabilidade do Muon em escala |
| **DUS (Depth Up-Scaling)** | Coreia | Escalar modelo adicionando layers |
| **Jamba ratio 1:7** | Israel | Hibrido Mamba-Transformer provado |
| **PLaMo SSM+SWA** | Japao | Mamba2 + sliding window, pruning |
| **SEA-LION multilingual** | Singapura | Referencia para modelo multilingual |
| **Falcon H1 parallel hybrid** | UAE | Attention e SSM em paralelo |
