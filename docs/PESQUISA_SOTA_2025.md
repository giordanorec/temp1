# Pesquisa SOTA 2025-2026: Avancos Implementados no FarolLM

Levantamento das inovacoes de ponta em arquitetura e treinamento de LLMs.
Base para decisoes de implementacao. Tudo abaixo foi pesquisado e
implementado no FarolLM.

---

## Arquitetura

### QK-Norm (Implementado)
Normaliza Q e K via RMSNorm antes do attention score. Previne
explosao de logits em modelos profundos. Adotado por DeepSeek-V3,
OLMo 2/3, Gemma 3. Substituiu o logit soft-capping da Gemma 2.

### iRoPE / NoPE (Implementado)
Remove RoPE de cada 4a layer (SmolLM3) ou alterna RoPE/NoPE (Llama 4).
Layers sem RoPE fazem attention global sem restricao posicional,
focando em associacoes semanticas. Melhora generalizacao para
contextos longos: treina em 256K, extrapola para 10M (Llama 4).

### Sliding Window + Global Attention (Implementado)
5 layers com sliding window local (512-1024 tokens) + 1 layer com
attention global, repetindo (Gemma 3). Apenas as layers globais
(1/6 do total) guardam KV cache completo. Reduz memoria drasticamente.
Gemma 3 usa dual RoPE: base=10K (local), base=1M (global).

### Multi-Token Prediction (Implementado)
DeepSeek-V3: branch auxiliar prevendo D tokens futuros. Cada MTP
module combina hidden state anterior + embedding do token futuro
via projecao + transformer block. Sinais de treino mais densos +
habilita speculative decoding na inferencia (1.8x mais rapido).

### Multi-Head Latent Attention (MLA) — DeepSeek-V3 (Referencia)
Comprime KV cache ~10x via projecao low-rank (inspirado em LoRA).
Em vez de cachear K e V completos, cacheia um unico vetor latente
comprimido. Na inferencia, as projecoes de recuperacao sao absorvidas
nas projecoes de Q e output, evitando descompressao.
- Complexo demais para 300M; relevante para scale-up futuro.

### Differential Attention (Referencia)
Microsoft ICLR 2025. Calcula attention como diferenca de dois softmax:
DiffAttn = softmax(Q1*K1) - lambda*softmax(Q2*K2). Cancela ruido,
promove sparsity, reduz alucinacao. Lambda e aprendido.
- Implementavel; considerar para v2 do FarolLM.

### Gated Delta Networks (Referencia)
NVIDIA ICLR 2025. Substitui self-attention por delta rule com gating.
Complexidade linear, superior a Mamba2 em reasoning e retrieval.
Qwen 3.5 usa 75% GatedDeltaNet + 25% softmax attention.

### RWKV-7 "Goose" (Referencia)
Evolucao linear de sequencia com delta rule generalizada, gating
vetorial, LR in-context. 2.9B params, SOTA multilingual na classe 3B.
Totalmente parallelizavel para treino.

---

## Otimizadores

### Muon (Implementado)
Keller Jordan 2025, PyTorch core 2.9+. Substitui scaling coordenada
do Adam por ortogonalizacao Newton-Schulz da matriz de gradientes.
~35% mais rapido que AdamW no regime SLM. Aplica-se apenas a pesos
2D (attention/MLP); embeddings/norms usam AdamW separado.
- Sweet spot: modelos 100M-1.2B (speedup decresce com escala).
- MuonClip (Kimi-K2): variante com QK-clip (tau=100) para zero
  loss spikes em escala producao.

### Cautious AdamW / C-AdamW (Implementado)
arXiv 2411.16085. Modificacao de 1 linha: mascara update onde ele
discorda da direcao do gradiente atual. ~1.47x mais sample-efficient.
`mask = (update * grad > 0).float(); update = update * mask`

### Schedule-Free AdamW (Referencia)
Meta/Aaron Defazio, ICLR 2025. Elimina necessidade de schedule.
Interpola + media dos iterados. Usa LR 1-10x maior que AdamW normal.
ScheduleFree+ (mai/2026) estende para treinamento longo.
- pip install schedulefree

### AdEMAMix (Referencia)
Apple/EPFL, ICLR 2025. Mistura dois EMAs: rapido (beta1=0.9) e
lento (beta3=0.9999). 1.3B em 101B tokens = AdamW em 197B tokens.
~2x eficiencia de dados.

---

## Schedulers

### Linear Decay-to-Zero (D2Z) (Implementado)
Hagele et al. fev/2025. Decai LR linearmente ate zero apos warmup.
60% compute savings vs cosine com decay a 10%. Novo SOTA para
treinamento de comprimento fixo.

### WSD — Warmup-Stable-Decay (Implementado)
MiniCPM/SmolLM3. Linear warmup -> plateau -> cosine cooldown curto.
Vantagem: nao precisa comprometer com budget total de antemao.
Pode branchar do plateau a qualquer momento.

---

## Estabilidade Numerica

### Logit Soft-Capping (Implementado)
Gemma 2: `cap * tanh(logits / cap)`. Attention cap=50, output cap=30.
Previne predicoes overconfident. Substituido por QK-Norm na Gemma 3,
mas ambos podem coexistir.

### Z-Loss (Implementado)
PaLM/Gemma: `z_loss = logsumexp(logits)^2 * weight`. Estabiliza
o normalizador do softmax. weight=1e-4 tipico.

### Output Embedding Centering (Implementado)
arXiv 2601.02031 (jan/2026). mu-centering: subtrai media dos
embeddings de saida antes de computar logits. Supera z-loss,
custo zero. Aplicado durante treinamento apenas.

### Depth-Scaled Init (Implementado)
GPT-2/DeepSeek: init das projecoes residuais com
std = 0.02 / sqrt(2 * num_layers). Previne explosao de sinal
em modelos profundos.

---

## Dados

### Qualidade > Quantidade (Consenso 2025-2026)
SmolLM3, Phi-4, FineWeb-Edu provam que curadoria agressiva supera
volume bruto. 10% dos tokens filtrados = performance de 100% brutos.

### Pipeline FineWeb-Edu (Implementado)
1. LLM anota amostra com "educational value" score
2. Treina classificador leve (FastText)
3. Aplica threshold no corpus completo

### Deduplicacao (Implementado)
Exact dedup via MD5 (implementado). MinHash LSH (estado da arte)
com 128-256 permutacoes, Jaccard threshold 0.7-0.8 para near-dedup.

### Overtraining funciona
TinyLlama (1.1B / 3T tokens), SmolLM2 (1.7B / 11T tokens):
treinar com muito mais dados que Chinchilla preve melhora SLMs.

---

## O que os ultimos modelos usam

| Modelo | Params | Inovacoes chave |
|---|---|---|
| **DeepSeek-V3** | 671B (37B ativo) | MLA, MoE aux-loss-free, FP8, MTP, DualPipe |
| **Llama 4** | 17B ativo | iRoPE, sparse MoE, early fusion multimodal |
| **Qwen 3.5** | 397B (17B ativo) | 75% GatedDeltaNet + 25% softmax, sparse MoE |
| **Gemma 3** | 1B-27B | Sliding window + global, dual RoPE, QK-Norm |
| **SmolLM3** | 3B | NoPE/4, tied emb, GQA, 11.2T tokens 3-stage |
| **OLMo 3** | 1B-32B | Post-RMSNorm, QK-Norm, 3-stage, fully open |
| **Phi-4** | 14B | Synthetic data dominant, RL for reasoning |
| **Kimi K2** | 1T (32B ativo) | MuonClip, zero loss spikes |

---

## Fontes

- DeepSeek-V3: arXiv 2412.19437
- Differential Attention: arXiv 2410.05258 (ICLR 2025)
- Native Sparse Attention: arXiv 2502.11089 (ACL 2025)
- Llama 4: ai.meta.com/blog/llama-4
- Gemma 3: arXiv 2503.19786
- GatedDeltaNet: arXiv 2412.06464 (ICLR 2025)
- RWKV-7: arXiv 2503.14456
- xLSTM: arXiv 2405.04517 (NeurIPS 2024)
- Jamba: arXiv 2403.19887 (ICLR 2025)
- Qwen 3.5: qwen.ai/blog?id=qwen3.5
- SmolLM3: huggingface.co/blog/smollm3
- OLMo 3: allenai.org/blog/olmo3
- Muon: PyTorch 2.9+, arXiv 2502.16982
- C-AdamW: arXiv 2411.16085
- Linear D2Z: arXiv 2502.15938
- Schedule-Free: arXiv 2405.15682 (ICLR 2025)
- AdEMAMix: arXiv 2409.03137 (ICLR 2025)
- HybridNorm: arXiv 2503.04598 (NeurIPS 2025)
- BLT (byte-level): arXiv 2412.09871 (ACL 2025)
- FlashAttention-3: arXiv 2407.08608
- Output Embedding Centering: arXiv 2601.02031
