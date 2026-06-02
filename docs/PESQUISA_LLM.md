# Pesquisa: Construindo uma LLM/SLM do Zero

Levantamento completo do ecossistema open source, literatura academica e
custos praticos. Base para decisoes do Discovery.

Data: 2026-05-23

---

## 1. FRAMEWORKS PARA TREINAR DO ZERO

### Tier 1 — Educacional / Prototipagem

| Framework | Repo | O que faz | Licenca |
|---|---|---|---|
| **nanochat** (Karpathy) | [github.com/karpathy/nanochat](https://github.com/karpathy/nanochat) | Pipeline completo (~8k linhas): tokenizador Rust, pre-treino FineWeb, SFT, GRPO. ~$100 em 4h/8xH100 | MIT |
| **nanoGPT** (Karpathy) | [github.com/karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) | ~600 linhas, reproduz GPT-2 124M. **Depreciado** (substituido por nanochat). 58.6k stars | MIT |
| **modded-nanogpt** | [github.com/KellerJordan/modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt) | Fork gamificado: GPT-2 124M em ~90 segundos | MIT |
| **minbpe** (Karpathy) | [github.com/karpathy/minbpe](https://github.com/karpathy/minbpe) | BPE educacional em Python puro. Reproduz tokenizador GPT-4 | MIT |

### Tier 2 — Producao (1-8 GPUs)

| Framework | Repo | O que faz | Licenca |
|---|---|---|---|
| **LitGPT** (Lightning AI) | [github.com/Lightning-AI/litgpt](https://github.com/Lightning-AI/litgpt) | 20+ LLMs do zero, sem abstracoes. FSDP, 1-1000+ GPUs. Base do TinyLlama | Apache 2.0 |
| **TorchTitan** (Meta) | [github.com/pytorch/torchtitan](https://github.com/pytorch/torchtitan) | Nativo PyTorch, 3D parallelism modular. Aceito no ICLR 2025 | BSD |
| **Oumi** | [github.com/oumi-ai/oumi](https://github.com/oumi-ai/oumi) | Ciclo completo: dados, treino, avaliacao, deploy. 200+ receitas, 10M-405B params | Apache 2.0 |
| **LLM Foundry** (Databricks) | [github.com/mosaicml/llm-foundry](https://github.com/mosaicml/llm-foundry) | Treino + fine-tune + eval + deploy. Base do DBRX e MPT | Apache 2.0 |

### Tier 3 — Larga escala (clusters, 100B+)

| Framework | Repo | O que faz | Licenca |
|---|---|---|---|
| **Megatron-LM** (NVIDIA) | [github.com/NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) | Referencia da industria. TP, PP, DP, EP, CP, FP8/FP4. MoE Zoo (DeepSeek-V3, Mixtral) | BSD |
| **GPT-NeoX** (EleutherAI) | [github.com/EleutherAI/gpt-neox](https://github.com/EleutherAI/gpt-neox) | Megatron + DeepSpeed. Usado por Stability AI, Together.ai, CMU | Apache 2.0 |
| **MaxText** (Google) | [github.com/AI-Hypercomputer/maxtext](https://github.com/AI-Hypercomputer/maxtext) | JAX, otimizado para TPUs. Suporta Gemma, Llama, DeepSeek, Qwen | Apache 2.0 |
| **Levanter/Marin** (Stanford) | [github.com/marin-community/levanter](https://github.com/marin-community/levanter) | JAX, reprodutivel bit-a-bit. Marin 32B superou OLMo 2 em 32/42 tarefas | Permissiva |

---

## 2. TOKENIZADORES

| Tokenizador | Repo | Algoritmos | Diferencial |
|---|---|---|---|
| **HuggingFace Tokenizers** | [github.com/huggingface/tokenizers](https://github.com/huggingface/tokenizers) | BPE, WordPiece, Unigram | Rust core, 1GB em <20s. O mais flexivel para treinar novos |
| **SentencePiece** (Google) | [github.com/google/sentencepiece](https://github.com/google/sentencepiece) | BPE, Unigram | Opera em byte stream bruto. Padrao multilingual (Gemini, T5, LLaMA) |
| **tiktoken** (OpenAI) | [github.com/openai/tiktoken](https://github.com/openai/tiktoken) | BPE (somente encoding) | 3-6x mais rapido. NAO treina novos vocabularios |
| **minbpe** (Karpathy) | [github.com/karpathy/minbpe](https://github.com/karpathy/minbpe) | BPE | Educacional. Reproduz GPT-4 tokenizer |

---

## 3. DATASETS PARA PRE-TREINAMENTO

| Dataset | Tamanho | Fonte | Licenca | Nota |
|---|---|---|---|---|
| **FineWeb** (HuggingFace) | ~15T tokens | 96 CommonCrawl snapshots | ODC-By | Maior dataset publico limpo |
| **FineWeb-Edu** | 1.3T tokens | Subset educacional do FineWeb | ODC-By | 10% dos tokens = performance de 350B brutos |
| **FineWeb-2** | ~3T+ palavras, 1000+ idiomas | CommonCrawl multilingual | ODC-By | Otimo para portugues |
| **RedPajama V2** | 100T+ brutos | 84 snapshots CommonCrawl | Apache 2.0 | 40+ sinais de qualidade |
| **SlimPajama** | 627B tokens | RedPajama V1 deduplicado | Apache 2.0 | 50% menor, mais limpo |
| **The Pile** | ~300B+ tokens | 22 subsets (PubMed, ArXiv, GitHub, etc) | Mista | Base do GPT-J, Pythia |
| **Dolma 3** | ~9.3T tokens | Web, PDFs, codigo, math | ODC-BY | Base do OLMo 2/3 |
| **CulturaX** | 6.3T tokens, 167 idiomas | mC4 + OSCAR | Permissiva | Maior multilingual aberto |
| **The Stack v2** | 4T+ tokens, 619 linguagens | Software Heritage + GitHub | Varia | Base do StarCoder2 |
| **DCLM** | 240T+ tokens brutos | CommonCrawl | Open source | Benchmark de curadoria |

### Datasets de Preferencia (RLHF/DPO)

| Dataset | Licenca | Nota |
|---|---|---|
| **HH-RLHF** (Anthropic) | MIT | Pares de preferencia humana |
| **UltraFeedback** | MIT | Anotado por GPT-4 |
| **HelpSteer** (NVIDIA) | CC-BY-4.0 | Anotacao humana de alta qualidade |
| **OpenAssistant** | Apache 2.0 | Conversas anotadas por voluntarios |

---

## 4. ALINHAMENTO (RLHF / DPO / GRPO)

| Framework | Repo | Algoritmos | Escala |
|---|---|---|---|
| **TRL** (HuggingFace) | [github.com/huggingface/trl](https://github.com/huggingface/trl) | PPO, DPO, GRPO, RLOO, KTO, SFT | Acessivel, funciona em consumer GPUs |
| **OpenRLHF** | [github.com/OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) | PPO, DPO, KTO, DAPO, REINFORCE++ | Projetado para 70B+. Ray + vLLM + DeepSpeed |
| **DeepSpeed-Chat** | [github.com/microsoft/DeepSpeedExamples](https://github.com/microsoft/DeepSpeedExamples) | SFT, Reward Model, PPO | 15x mais rapido que alternativas |
| **NeMo RL** (NVIDIA) | [github.com/NVIDIA-NeMo/RL](https://github.com/NVIDIA-NeMo/RL) | GRPO, GSPO, DAPO, SFT, DPO | Enterprise, DTensor + Megatron Core |
| **VERL** (ByteDance) | [github.com/volcengine/verl](https://github.com/volcengine/verl) | PPO, GRPO, ReMax, REINFORCE++ | DAPO superou GRPO do DeepSeek |

---

## 5. TREINAMENTO DISTRIBUIDO

| Framework | Quando usar | Diferencial |
|---|---|---|
| **DeepSpeed ZeRO** (Microsoft) | Modelo nao cabe em 1 GPU | 3 estagios + Infinity (trilhoes de params). Melhor offloading CPU/NVMe |
| **PyTorch FSDP** (Meta) | 7B-70B em 2-8 GPUs | Nativo PyTorch. Ate 5x mais rapido que ZeRO-3 por iteracao |
| **Colossal-AI** | Paralelismo hibrido | Interface unificada. Ate 2.76x speedup |
| **NeMo** (NVIDIA) | End-to-end enterprise | Megatron Core interno. Otimizado para hardware NVIDIA |

---

## 6. MODELOS 100% ABERTOS (codigo de treino + dados + pesos)

| Modelo | Org | Tamanhos | Dados | Repo de treino |
|---|---|---|---|---|
| **OLMo / OLMo 2 / OLMo 3** | AI2 | 1B-32B | Dolma | [github.com/allenai/OLMo](https://github.com/allenai/OLMo) |
| **Pythia** | EleutherAI | 70M-12B | The Pile | [github.com/EleutherAI/pythia](https://github.com/EleutherAI/pythia) |
| **LLM360 Amber** | LLM360 | 7B | 1.3T tokens | [github.com/LLM360/amber-train](https://github.com/LLM360/amber-train) |
| **MAP-Neo** | M-A-P / Waterloo | 7B | 4.5T tokens | Publico |
| **Marin** | Stanford CRFM | 8B/32B | Publico | Levanter/JAX |
| **Cerebras-GPT** | Cerebras | 111M-13B | Publico | Model Zoo |

**Nota:** LLaMA, Mistral, Qwen, Gemma, DeepSeek publicam pesos mas NAO o codigo/dados de treinamento completos.

---

## 7. PAPERS FUNDAMENTAIS

### Arquitetura

| Paper | Autores | Ano | Contribuicao chave |
|---|---|---|---|
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Vaswani et al. | 2017 | Arquitetura Transformer |
| [GPT-1](https://openai.com/research/language-unsupervised) | Radford et al. | 2018 | Pre-treino generativo + fine-tuning |
| [GPT-2](https://openai.com/research/better-language-models) | Radford et al. | 2019 | Zero-shot multitask |
| [GPT-3](https://arxiv.org/abs/2005.14165) | Brown et al. | 2020 | Few-shot learning a 175B params |
| [LLaMA](https://arxiv.org/abs/2302.13971) | Touvron et al. | 2023 | 13B supera GPT-3 175B com dados publicos |
| [LLaMA 2](https://arxiv.org/abs/2307.09288) | Touvron et al. | 2023 | RLHF em larga escala, open source |
| [LLaMA 3](https://arxiv.org/abs/2407.21783) | Meta AI | 2024 | 405B, 15.6T tokens, multimodal |

### Scaling Laws

| Paper | Contribuicao chave |
|---|---|
| [Scaling Laws for Neural LMs](https://arxiv.org/abs/2001.08361) (Kaplan et al. 2020) | Leis de potencia previsiveis performance vs tamanho/dados/compute |
| [Chinchilla](https://arxiv.org/abs/2203.15556) (Hoffmann et al. 2022) | Modelos menores + mais dados > modelos maiores + menos dados. ~20 tokens/param |
| [Predictable Scale: Step Law](https://arxiv.org/abs/2503.04715) (2025) | 3.700 modelos treinados. Lei de escala para LR e batch size |
| [Scaling Optimal LR](https://arxiv.org/abs/2409.19913) (2024) | LR otima muda com horizonte de tokens |

### SLMs (Small Language Models)

| Paper | Modelo | Tamanho | Inovacao |
|---|---|---|---|
| [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644) | Phi-1 | 1.3B | Dados sinteticos "textbook-quality" |
| [Phi-1.5](https://arxiv.org/abs/2309.05463) | Phi-1.5 | 1.3B | Raciocinio via dados sinteticos |
| [Phi-3](https://arxiv.org/abs/2404.14219) | Phi-3-mini | 3.8B | Rivaliza Mixtral 8x7B, roda em celular |
| [Phi-4](https://arxiv.org/abs/2412.08905) | Phi-4 | 14B | Dados sinteticos de alta qualidade |
| [TinyLlama](https://arxiv.org/abs/2401.02385) | TinyLlama | 1.1B | 3T tokens, FlashAttention, 90 dias em 16xA100 |
| [SmolLM2](https://arxiv.org/abs/2502.02737) | SmolLM2 | 135M-1.7B | 11T tokens multi-estagio |
| [MiniCPM](https://arxiv.org/abs/2404.06395) | MiniCPM | 1.2B-2.4B | WSD scheduler, ~7B performance |
| [MobileLLM](https://arxiv.org/abs/2402.14905) | MobileLLM | 125M-350M | Deep-and-thin, embedding sharing |

### Arquiteturas Alternativas

| Paper | Contribuicao |
|---|---|
| [Mamba](https://arxiv.org/abs/2312.00752) (Gu, Dao 2023) | SSMs seletivos, complexidade linear, 20-40x mais rapido |
| [Mixtral of Experts](https://arxiv.org/abs/2401.04088) (Mistral 2024) | MoE 8x7B, ativa so 13B por token, supera LLaMA-2 70B |
| [DeepSeek-V3](https://arxiv.org/abs/2412.19437) (2024) | 671B MoE, treinado por apenas $5.6M |
| [DeepSeek-R1](https://arxiv.org/abs/2501.12948) (2025) | RL puro sem SFT, raciocinio emergente |
| [Switch Transformers](https://arxiv.org/abs/2101.03961) | MoE simplificado, trilhoes de params |

### Alinhamento

| Paper | Contribuicao |
|---|---|
| [InstructGPT](https://arxiv.org/abs/2203.02155) (OpenAI 2022) | Pipeline SFT -> Reward Model -> PPO |
| [DPO](https://arxiv.org/abs/2305.18290) (Rafailov et al. 2023) | Elimina reward model, loss de classificacao simples |
| [Constitutional AI](https://arxiv.org/abs/2212.08073) (Anthropic 2022) | Auto-melhoria com "constituicao" de principios |
| [RLAIF vs RLHF](https://arxiv.org/abs/2309.00267) (2023) | Viabilidade de feedback por AI em escala |

### Dados e Treinamento

| Paper | Contribuicao |
|---|---|
| [Scaling Data-Constrained LMs](https://arxiv.org/abs/2305.16264) | 400+ modelos, dados repetidos perdem valor com meia-vida de ~16 epocas |
| [Ultra-FineWeb](https://arxiv.org/abs/2505.05427) | Filtragem eficiente de dados |
| [Byte Pair Encoding is Suboptimal](https://arxiv.org/abs/2004.03720) | Alternativas ao BPE |
| [Rethinking Multilingual Tokenizer Design](https://arxiv.org/abs/2508.06533) | Tokenizers para cenarios multilinguais |

### Surveys

| Paper | Escopo |
|---|---|
| [Survey on MoE in LLMs](https://arxiv.org/abs/2407.06204) (2024) | Switch, Mixtral, DeepSeekMoE |
| [Small Language Models Survey](https://arxiv.org/abs/2409.15790) (2024) | Medicao e comparacao de SLMs |
| [SLMs: Architectures, Techniques, Evaluation](https://arxiv.org/abs/2505.19529) (2025) | Survey mais recente de SLMs |
| [S4 to Mamba Evolution](https://arxiv.org/abs/2503.18970) (2025) | Evolucao dos SSMs |

---

## 8. TUTORIAIS E CURSOS

| Recurso | Autor | Formato | Nivel |
|---|---|---|---|
| [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) | Karpathy | Video (YouTube) | Iniciante -> Intermediario |
| "Let's Build GPT" | Karpathy | Video | Intermediario |
| "Let's reproduce GPT-2" | Karpathy | Video | Intermediario |
| [Build a LLM (From Scratch)](https://github.com/rasbt/LLMs-from-scratch) | Sebastian Raschka | Livro (Manning 2024) | Intermediario |
| [Hugging Face NLP Course](https://huggingface.co/learn/nlp-course) | HuggingFace | Online | Iniciante |
| [A Hackers' Guide to LMs](https://www.fast.ai/) | Jeremy Howard | Video | Intermediario |
| [From Zero to Hero with LLMs](https://www.louisbouchard.ai/from-zero-to-hero-with-llms/) | Louis Bouchard | Playlist (50h+) | Todos |

---

## 9. HARDWARE E CUSTOS

### GPUs Principais (2025-2026)

| GPU | VRAM | FP16 TFLOPS | Preco (compra) |
|---|---|---|---|
| RTX 4090 | 24 GB | ~330 | ~$1.600 (usada) |
| RTX 5090 | 32 GB | ~450+ | ~$2.000 |
| A100 40GB | 40 GB | ~312 | Enterprise |
| A100 80GB | 80 GB | ~312 | Enterprise |
| H100 80GB | 80 GB HBM3 | ~990 FP16 / 3000 FP8 | ~$25.000 |
| H200 | 141 GB HBM3e | ~990+ | ~$39.000 |

### Aluguel de GPU na Nuvem (mid-2026)

| Provedor | A100 80GB | H100 80GB | H200 |
|---|---|---|---|
| **RunPod** | $1.99/h | $2.49/h (on-demand) | ~$3.50/h |
| **Lambda Labs** | ~$1.50/h | $2.99/h | - |
| **Vast.ai** | ~$1.00-1.50/h | ~$1.50-2.50/h | Variavel |
| **CoreWeave** | ~$2.06/h | ~$6.16/h | - |
| **AWS** | ~$2.50-3.00/h | ~$3.90/h | - |
| **GCP** | ~$2.50/h | ~$3.00/h | - |
| **Azure** | ~$3.00/h | ~$6.98/h | - |
| **Nebius** | - | - | $3.50/h (on-demand) |

### Custos Estimados de Treinamento (precos mid-2026)

Formula: **FLOPs = 6 x N x D** (N=params, D=tokens)

| Modelo | Tokens | Horas H100 | Custo (spot ~$1.50/h) | Custo (on-demand ~$2.50/h) |
|---|---|---|---|---|
| 100M | 2B | ~8h | ~$12 | ~$20 |
| 500M | 10B | ~21h | ~$32 | ~$53 |
| 1B | 20B (Chinchilla) | ~83h | ~$125 | ~$208 |
| 1B | 100B | ~417h | ~$625 | ~$1.040 |
| 1B | 1T | ~4.170h | ~$6.250 | ~$10.400 |
| 3B | 60B (Chinchilla) | ~750h | ~$1.125 | ~$1.875 |
| 3B | 300B | ~3.750h | ~$5.625 | ~$9.375 |
| 7B | 1T | ~29.170h | ~$43.750 | ~$72.900 |

**Nota:** multiplicar por 2-5x para incluir experimentos falhos e hyperparameter search.

### Programas Academicos (compute gratuito/subsidiado)

| Programa | Recurso | Requisito |
|---|---|---|
| **Google TPU Research Cloud** | 1.000+ TPUs gratis | Publicar pesquisa, aceita internacionais |
| **NVIDIA Academic Grant** | Ate 30.000h de H100 | PI (professor/pesquisador) |
| **AWS Research Credits** | Ate $5.000 (estudantes) | Aplicacao, 90-120 dias |
| **Google Cloud Research** | Ate $5.000 (professores) | Vinculo academico |
| **NAIRR** (EUA) | Creditos Azure + NVIDIA | Instituicoes americanas |

**Para brasileiros:** Google TRC e NVIDIA Academic Grant aceitam candidatos internacionais.
Verificar editais FAPESP, CNPq, CAPES para cloud computing.

### Otimizacoes para Compute Limitado

| Tecnica | Economia de VRAM | Custo |
|---|---|---|
| **Flash Attention 2/3** | O(n^2) -> O(n), 2-4x speedup | Nenhum |
| **Mixed Precision (BF16)** | ~50% memoria, ~2x velocidade | Minimo |
| **Gradient Checkpointing** | ~60-70% ativacoes | +20-30% tempo |
| **Gradient Accumulation** | Simula batch grande sem VRAM | Nenhum |
| **AdamW 8-bit** (bitsandbytes) | ~50% estados otimizador | Minimo |

### Casos de Sucesso com Recursos Limitados

| Projeto | Setup | Resultado |
|---|---|---|
| **nanochat** (Karpathy) | 8xH100, 4h, ~$100 | 500M funcional |
| **TinyLlama** | 16xA100-40G, 90 dias | 1.1B competitivo em 3T tokens |
| **Cramming** | 1x A6000 ou RTX 3090, 1 dia | BERT ~100M razoavel |
| **LLM on RTX 3090** (Giles Thomas) | 1x RTX 3090 | GPT-2 small (124M) do zero |
| **SmolLM2 135M/360M** | Pocas GPUs | SLMs altamente competitivos |
| **FLM-101B** | <$100K total | 101B params com arquitetura eficiente |
| **2x RTX 5090** | ~$4K hardware | Iguala H100 para modelos ate 70B |

### Monitoramento de Treinamento

| Ferramenta | Tipo | Preco |
|---|---|---|
| **W&B** (Weights & Biases) | SaaS | Gratuito (pessoal) |
| **MLflow** | Open source (Apache 2.0) | Gratuito |
| **TensorBoard** | Open source | Gratuito |
| **Aim** | Open source | Gratuito |
| **ClearML** | Open source + SaaS | Gratuito (community) |

---

## 10. ESTRATEGIAS-CHAVE PARA SLMs EFICIENTES

Com base em toda a literatura pesquisada:

1. **Dados de alta qualidade > quantidade bruta** — Phi mostrou que dados sinteticos "textbook-quality" superam web scraping massivo. FineWeb-Edu confirma: 10% dos tokens filtrados = performance de 100% brutos.

2. **Overtraining funciona** — TinyLlama (1.1B em 3T tokens) e SmolLM2 (1.7B em 11T tokens) mostram que treinar com muito mais dados que Chinchilla preve melhora SLMs significativamente.

3. **Arquitetura deep-and-thin** — MobileLLM e MiniCPM mostram que modelos mais profundos e estreitos superam modelos rasos e largos no regime sub-bilhao.

4. **Treinamento multi-estagio** — SmolLM2 e Phi-3 usam mistura progressiva de dados gerais -> codigo -> matematica -> instrucoes.

5. **WSD scheduler** — MiniCPM introduziu Warmup-Stable-Decay que facilita treinamento continuo e adaptacao de dominio.

6. **Tecnicas obrigatorias** — GQA, embedding sharing, SwiGLU, FlashAttention sao essenciais.

7. **Modelo 100% reproduzivel** — OLMo (AI2) e o unico com dados + codigo + checkpoints + logs completos. Melhor ponto de partida para aprendizado.
