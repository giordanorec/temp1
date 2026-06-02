# FarolLM-Cifra — Handoff Completo

> Documento de transferencia para iniciar o projeto **FarolLM-Cifra** em um repositorio novo, em outra sessao do Claude Code.
> Escrito para ser autocontido: outra sessao deve conseguir abrir esse MD, ler ate o fim e tocar o projeto do zero sem perguntar nada.
>
> Data do handoff: 2026-06-02
> Autor original: Giordano R. E. Cabral (grec@cin.ufpe.br) — UFPE/CIn
> Status: especificacao inicial, nada implementado ainda no repo destino

---

## Sumario

1. [TL;DR](#1-tldr)
2. [Visao e Objetivo](#2-visao-e-objetivo)
3. [Contexto e Motivacao](#3-contexto-e-motivacao)
4. [Related Work (estado da arte)](#4-related-work-estado-da-arte)
5. [Novidade e Gap de Pesquisa](#5-novidade-e-gap-de-pesquisa)
6. [Especificacao do Dataset](#6-especificacao-do-dataset)
7. [Especificacao do Tokenizador](#7-especificacao-do-tokenizador)
8. [Arquitetura do Modelo](#8-arquitetura-do-modelo)
9. [Pipeline de Treinamento](#9-pipeline-de-treinamento)
10. [Hardware e Compute](#10-hardware-e-compute)
11. [Stack Tecnologica](#11-stack-tecnologica)
12. [Estrutura do Repositorio](#12-estrutura-do-repositorio)
13. [Sistema Multi-agente](#13-sistema-multi-agente)
14. [Roadmap por Fases](#14-roadmap-por-fases)
15. [Criterios de Aceitacao](#15-criterios-de-aceitacao)
16. [Avaliacao e Benchmarks](#16-avaliacao-e-benchmarks)
17. [Etica, Licenca, Compliance](#17-etica-licenca-compliance)
18. [Plano de Publicacao](#18-plano-de-publicacao)
19. [Riscos e Contingencias](#19-riscos-e-contingencias)
20. [Decisoes Pendentes](#20-decisoes-pendentes)
21. [Referencias Completas](#21-referencias-completas)
22. [Apendices](#22-apendices)

---

## 1. TL;DR

**FarolLM-Cifra** e um Small Language Model (SLM) de 100-300M parametros, treinado do zero, especializado no formato **"cifra"** (letra de musica com acordes posicionados acima das silabas correspondentes). Foco em musica popular brasileira e latina, com tokenizador musical proprio que trata acordes como tokens atomicos.

- **Dado-chave:** ~2M cifras com metadata (artista, genero, tom, capotraste) ja coletadas.
- **Hardware-alvo:** Mac Mini M4 64GB (treinamento local) + opcao de TPU/GPU em nuvem para scaling.
- **Diferencial:** **Primeiro modelo dedicado ao formato cifra**. Modelos existentes (ChatMusician, MIDI-LLM, DadaGP) usam ABC notation, MIDI ou tablatura — nenhum gera letra com acordes inline em pt-BR.
- **Deliverables:** modelo no HuggingFace + dataset (se licenciamento permitir) + paper + demo Gradio.

---

## 2. Visao e Objetivo

### 2.1 Visao

Criar o primeiro Language Model que compreende e gera **musica como musicos amadores brasileiros realmente a consomem**: letra com acordes inline (formato cifra), em portugues, com vocabulario nativo de generos brasileiros (samba, forro, sertanejo, bossa, MPB, frevo, axe, pagode, etc.).

### 2.2 Objetivos especificos

| ID | Objetivo | Metrica de sucesso |
|---|---|---|
| O1 | Gerar cifra completa a partir de prompt (genero+tom+tema) | Avaliacao humana: >70% das cifras geradas sao tocaveis e plausiveis |
| O2 | Transposicao automatica de cifras | Acuracia >95% em transposicoes simples; >85% em complexas (com inversoes, dim, aug) |
| O3 | Sugerir acordes para letra dada | Avaliacao humana: >60% das sugestoes sao musicalmente coerentes |
| O4 | Analise harmonica (graus, modulacoes, substituicoes) | Acuracia >80% em comparacao com analise manual de musicologo |
| O5 | Identificar genero pela progressao | F1 >0.7 em 8+ generos |
| O6 | Continuar/completar cifra parcial | Perplexidade < baseline (LLaMA 3.2 1B em mesmo dado) |

### 2.3 Nao-objetivos (escopo fora)

- Nao gerar audio (e modelo de texto symbolic only).
- Nao fazer transcricao audio->cifra (problema de MIR, fora do escopo).
- Nao gerar partitura/MIDI (formato cifra apenas).
- Nao competir com modelos de uso geral (GPT-4, Claude) em tarefas nao-musicais.

---

## 3. Contexto e Motivacao

### 3.1 Por que cifra (e nao ABC/MIDI/tab)?

| Formato | Quem usa | Pontos fortes | Pontos fracos |
|---|---|---|---|
| **ABC notation** | Musicos eruditos, folk anglosaxao | Compacto, encoda ritmo + melodia | Quase ninguem no Brasil le |
| **MIDI** | Producao musical | Padrao da industria | Nao tem letra; nao tocavel direto |
| **Tablatura** | Guitarristas | Mostra dedilhado exato | Verboso, instrumento-especifico |
| **Cifra** | **Musico amador brasileiro** | Universal, simples, com letra | Sem ritmo explicito, ambigua |

A cifra e o formato **dominante no Brasil**: CifraClub tem ~30M visitas/mes, e o **8o site mais acessado do pais** (categoria entretenimento). Outros sites (Cifras.com.br, Cifra Club, Letras) somam outro tanto.

### 3.2 Por que treinar do zero (e nao fine-tunar)?

- O **tokenizador** e o diferencial. Acordes como tokens atomicos so e possivel com vocabulario novo.
- ChatMusician usa tokenizer do LLaMA2: `Am7` vira 2-3 tokens. No nosso, vira 1 token.
- Treinar do zero forca entendimento profundo do pipeline (objetivo academico do FarolLM).

### 3.3 Por que portugues + Brasil?

- **Gap real:** nenhum music LLM publicado e treinado em pt-BR.
- **Dados unicos:** 2M cifras em pt-BR e um asset que ninguem mais tem.
- **Patrimonio cultural:** generos brasileiros tem harmonias caracteristicas (samba, bossa, choro) nao representadas em modelos anglosaxoes.

---

## 4. Related Work (estado da arte)

### 4.1 Music LLMs (mais proximos)

#### ChatMusician (2024) — competidor mais direto
- **Paper:** https://arxiv.org/abs/2402.16153
- **Modelo:** https://huggingface.co/m-a-p/ChatMusician
- **Base:** LLaMA2 7B + continual pretraining em ABC notation
- **Faz:** geracao de melodia, analise harmonica, composicao condicionada
- **Nao faz:** formato cifra, pt-BR, generos brasileiros
- **Citar como baseline e related work obrigatorio.**

#### MuPT — A Generative Symbolic Music Pretrained Transformer (2024)
- **Paper:** https://arxiv.org/abs/2404.06393
- ABC notation multi-track, scaling laws para musica symbolic
- Util pra justificar escolhas de tamanho de modelo

#### MIDI-LLM (2025)
- **Paper:** https://arxiv.org/abs/2511.03942
- LLM adaptado para gerar MIDI a partir de texto
- Two-stage training: vocab expansion + finetuning

#### SongComposer (2024)
- **Paper:** https://arxiv.org/abs/2402.17645
- LLM para letra+melodia juntos (tuple-based representation)
- Letra com timing, mas sem acordes inline

#### Amuse (2024)
- **Paper:** https://arxiv.org/abs/2412.18940
- Songwriting assistant com chord progressions a partir de inputs multimodais
- LLM gera apenas a progressao de acordes, nao a cifra completa

### 4.2 Datasets de musica symbolic

#### Chordonomicon (2024) — referencia obrigatoria
- **Paper:** https://arxiv.org/abs/2410.22046
- **Dataset:** 666K musicas, progressoes de acordes + metadata
- **Importante:** so progressoes de acordes (sem letra), em ingles
- **Nosso dataset (2M cifras com letra+metadata)** e 3x maior em volume e tem letra+acordes alinhados.

#### DadaGP (2021)
- **Paper:** https://arxiv.org/abs/2107.14653
- 26K musicas GuitarPro tokenizadas, 739 generos
- Formato: tablatura completa (fret/string por nota), nao cifra

#### POP909-CL (2025, usado por BACHI)
- **Paper:** https://arxiv.org/abs/2510.06528
- Anotacoes simbolicas de chord recognition em pop chines

#### Weimar Jazz Database
- Jazz transcriptions com chord progressions, usado por Jazz Transformer

### 4.3 Geracao de tablatura

#### Fretting-Transformer (2025)
- **Paper:** https://arxiv.org/abs/2506.14223
- T5 encoder-decoder para MIDI -> tab
- Resolve ambiguidade string/fret

#### Rock Guitar Tablature Generation via NLP (2023)
- **Paper:** https://arxiv.org/abs/2301.05295
- Modelo autoregressivo NLP para gerar tabs de rock

#### MIDI-to-Tab Masked LM (2024)
- **Paper:** https://arxiv.org/abs/2408.05024
- Masked language modeling para tablatura

### 4.4 Chord recognition (audio/symbolic -> acordes)

#### BACHI (2025)
- **Paper:** https://arxiv.org/abs/2510.06528
- SOTA em chord recognition simbolico (boundary-aware + masked iterative decoding)

#### MMT-BERT (2024)
- **Paper:** https://arxiv.org/abs/2409.00919
- Chord-aware symbolic music generation via GAN + MusicBERT

### 4.5 Tecnica relacionada (importante para implementacao)

- **TunesFormer** — control codes para forma musical: https://arxiv.org/abs/2301.02884
- **Pop Music Transformer** — beat-based modeling: https://arxiv.org/abs/2002.00212
- **Jazz Transformer** — Transformer-XL para jazz: https://arxiv.org/abs/2008.01307
- **MusicGen-Chord** — audio condicionado em acordes: https://arxiv.org/abs/2412.00325 (so pra contexto, e audio)

### 4.6 Outras refs de tokenizacao musical

- **REMI** (Pop Music Transformer): tokenizacao com beat/bar markers
- **Compound Word Transformer**: tokens compostos para musica
- **MMM** (Multi-Track Music Machine): https://arxiv.org/abs/2008.06048

### 4.7 LLM pretraining basics (para revisitar)

- **Chinchilla** (Hoffmann et al. 2022): 20 tokens/param optimal
- **LLaMA 3** paper: arquitetura de referencia
- **Qwen 2.5** paper: tokenizer tricks para multilingual
- **NanoGPT** (Karpathy): codebase mais simples para entender ponta-a-ponta

---

## 5. Novidade e Gap de Pesquisa

### 5.1 O gap

Apos revisao da literatura (HF papers, arxiv 2020-2026), **nao existe modelo dedicado ao formato cifra** (chord-over-lyrics). Existe:
- Modelos de chord progression (Chordonomicon, Amuse) — **sem letra**.
- Modelos de letra+melodia (SongComposer) — **sem acordes inline**.
- Modelos de ABC notation (ChatMusician) — **formato diferente, anglosaxao**.
- Modelos de tablatura (DadaGP) — **formato diferente, mais tecnico**.

### 5.2 Contribuicoes esperadas

1. **Formato cifra como representacao para LLM** (contribuicao de representacao).
2. **Tokenizador musical com acordes atomicos** (contribuicao tecnica).
3. **Modelo SOTA em geracao de cifras em pt-BR** (contribuicao empirica).
4. **Dataset publico curado** (se licenciamento permitir) de cifras com metadata.
5. **Benchmark de avaliacao** de cifra generation (BLEU musical, acuracia de transposicao, plausibilidade harmonica).

### 5.3 Como posicionar o paper

**Titulo provavel:** *"FarolLM-Cifra: A Chord-Over-Lyrics Language Model for Brazilian Popular Music"*

**Venue alvo:**
- ISMIR 2027 (top em music information retrieval)
- ACL Findings (NLP venues aceitam musica como dominio)
- LREC-COLING (boa pra datasets/recursos)
- BRACIS 2027 (visibilidade no Brasil)

---

## 6. Especificacao do Dataset

### 6.1 Origem

- **~2M cifras** coletadas via scraping do CifraClub e similares (mesmo modelo de coleta web usado por CulturaX, FineWeb).
- **Formato bruto:** HTML com tags `<pre>` contendo cifras + metadata em headers/meta.
- **Cobertura:** internacional, mas majoritariamente pt-BR. Generos: todos.

### 6.2 Schema do dado processado

Cada cifra processada e um JSONL record:

```json
{
  "id": "cifra_000001",
  "artist": "Luiz Gonzaga",
  "title": "Asa Branca",
  "genre": "forró",
  "subgenre": "forró pé de serra",
  "key": "G",
  "capo": 0,
  "tuning": "EADGBE",
  "language": "pt-BR",
  "year": 1947,
  "raw_text": "...",
  "structured": [
    {"section": "intro", "chords": ["G", "D7", "G"]},
    {"section": "verse_1",
     "lines": [
       {"chords_line": "G          C",
        "lyrics_line": "Quando olhei a terra ardendo"},
       {"chords_line": "D7         G",
        "lyrics_line": "Qual fogueira de São João"}
     ]}
  ],
  "chord_vocabulary": ["G", "C", "D7"],
  "source_url": "...",
  "license_status": "unknown|cc|fair_use|...",
  "quality_score": 0.87
}
```

### 6.3 Pipeline de preparacao (etapas)

1. **Crawl/Load** — carregar HTML bruto.
2. **Parse** — extrair metadata + corpo da cifra usando regex/BeautifulSoup. Identificar linhas de acordes vs linhas de letra (heuristicas: linhas com so acordes/whitespace; linhas com vocabulario portugues).
3. **Validar acordes** — cada token de acorde tem que casar com regex de acorde valido: `^[A-G][#b]?(m|maj|min|dim|aug|sus|add|maj7|m7|7|9|11|13|...)*(/[A-G][#b]?)?$`.
4. **Estruturar** — detectar secoes (Intro, Verso, Refrao, Ponte, Solo) por marcadores comuns.
5. **Deduplicar** — MinHash/LSH em hash de letras (mesma letra = mesma musica, mesmo que cifra varie). Manter a versao mais "rica" (mais metadata, melhor parsing).
6. **Filtrar qualidade**:
   - Remover cifras com <4 acordes distintos (provavelmente corrompidas).
   - Remover cifras sem letra.
   - Remover cifras com >20% de tokens nao-reconheciveis.
7. **Detectar lingua** — fastText/cld3 para confirmar pt-BR vs outros.
8. **Classificar genero** — usar metadata quando existir; classificar com modelo auxiliar (BERT pt-BR fine-tuned em pares letra+genero) quando nao.
9. **Inferir tom (se faltar)** — algoritmo Krumhansl-Schmuckler ou heuristica baseada em primeiro/ultimo acorde + tonal centers.
10. **Splits** — train/val/test 95/2.5/2.5, **stratificado por artista** (evitar leakage: musicas do mesmo artista nao podem aparecer em splits diferentes).

### 6.4 Formato de treino (texto plano)

Para o LM ver, cada cifra vira:

```
<|cifra|>
<|meta|>
artist: Luiz Gonzaga
title: Asa Branca
genre: forró
key: G
capo: 0
year: 1947
<|/meta|>
<|body|>
<|intro|>
G | D7 | G

<|verse|>
G          C
Quando olhei a terra ardendo
D7         G
Qual fogueira de São João

<|chorus|>
...
<|/body|>
<|end|>
```

Tokens especiais essenciais: `<|cifra|>`, `<|meta|>`, `<|/meta|>`, `<|body|>`, `<|/body|>`, `<|intro|>`, `<|verse|>`, `<|chorus|>`, `<|bridge|>`, `<|solo|>`, `<|outro|>`, `<|end|>`.

### 6.5 Estatisticas esperadas (apos limpeza)

| Metric | Valor estimado |
|---|---|
| Cifras totais brutas | ~2M |
| Apos dedup | ~1.2-1.5M |
| Apos filtro qualidade | ~1.0M |
| Tokens totais (com tokenizer musical) | ~400-800M |
| Vocab unico de acordes | ~2-5k |
| Generos distintos | 30+ |
| Artistas distintos | 50k+ |
| Tamanho medio cifra (tokens) | 400-600 |
| Tamanho maximo recomendado (context) | 2048-4096 |

### 6.6 Limpeza adicional

- Normalizar acordes ambíguos: `B♭` -> `Bb`, `D7+` -> `D7`, etc. Manter dicionario de equivalencias.
- Reposicionar acordes que ficaram mal-alinhados no parsing (heuristica: cada acorde deve estar acima de uma silaba; usar separacao silabica).
- Remover marcacoes do site (`Cifra Club`, `(bis)`, links).

---

## 7. Especificacao do Tokenizador

### 7.1 Decisao central

**Tokenizador BPE customizado** treinado com SentencePiece + HuggingFace Tokenizers, com:
- Vocab size: **32k tokens**.
- Vocabulario inicial pre-populado com **acordes como tokens atomicos** (~3k acordes).
- BPE aprende o resto em cima da letra + estrutura.

### 7.2 Vocabulario pre-populado (manual)

#### Acordes (~3k tokens)
- Triades maiores: C, C#, Db, D, ... B (12)
- Triades menores: Cm, ... Bm (12)
- 7as: C7, Cmaj7, Cm7, Cm7b5, Cdim7, ... (12 * 6 = 72)
- 9/11/13: C9, C11, C13, Cm9, Cmaj9, ... (12 * 8 = 96)
- Sus/add: Csus2, Csus4, Cadd9, ... (12 * 4 = 48)
- Dim/aug: Cdim, Caug, C°, C+ (12 * 4 = 48)
- Slash chords (inversoes): C/E, C/G, G/B, ... (combinacoes mais comuns, ~500)
- Enarmonicos: tratar Db == C#, Eb == D# como tokens **separados** (preservar como esta na cifra original).

**Heuristica:** rodar parser em 100k cifras primeiro, extrair top-3000 acordes mais frequentes, adicionar como tokens atomicos.

#### Markers estruturais
`<|intro|>`, `<|verse|>`, `<|verse_1|>`, ..., `<|chorus|>`, `<|pre_chorus|>`, `<|bridge|>`, `<|solo|>`, `<|outro|>`, `<|interlude|>`.

#### Markers de metadata
`<|cifra|>`, `<|meta|>`, `<|/meta|>`, `<|body|>`, `<|/body|>`, `<|end|>`, `<|pad|>`, `<|unk|>`, `<|bos|>`, `<|eos|>`.

#### Generos (tokens)
`<|forro|>`, `<|samba|>`, `<|bossa|>`, `<|sertanejo|>`, `<|mpb|>`, `<|frevo|>`, `<|axe|>`, `<|pagode|>`, `<|choro|>`, `<|rock_br|>`, `<|pop|>`, `<|gospel|>`, `<|reggae|>`, etc.

#### Tonalidades
`<|tom_C|>`, `<|tom_Cm|>`, ..., `<|tom_B|>`, `<|tom_Bm|>`.

### 7.3 BPE para o resto

Treinar SentencePiece BPE com vocab restante (~28k tokens) em corpus de letras em pt-BR + en (proporcional ao mix do dataset).

### 7.4 Como validar o tokenizador

Apos treino:
1. Pegar 1000 cifras random, tokenizar.
2. Conferir que acorde medio = 1 token (nao 2-3 como em tokenizer generico).
3. Comparar bytes/token com LLaMA tokenizer no mesmo corpus — deve ser ~30-40% mais eficiente.
4. Round-trip test: decode(encode(x)) == x para 100% dos casos.

### 7.5 Codigo de referencia

- HF Tokenizers tutorial: https://huggingface.co/docs/tokenizers
- SentencePiece: https://github.com/google/sentencepiece
- Exemplo de custom vocab pre-populado: ver Karpathy minbpe (https://github.com/karpathy/minbpe)

---

## 8. Arquitetura do Modelo

### 8.1 Decisao

**Transformer decoder-only**, ao estilo LLaMA 3 (RMSNorm, SwiGLU, RoPE, GQA).

### 8.2 Configuracoes propostas

| Variante | Params | Layers | d_model | n_heads | n_kv_heads | ctx | Compute treino M4 |
|---|---|---|---|---|---|---|---|
| **FarolLM-Cifra-tiny** | ~50M | 12 | 512 | 8 | 4 | 2048 | ~3 dias |
| **FarolLM-Cifra-small** | ~150M | 16 | 768 | 12 | 4 | 2048 | ~1-2 semanas |
| **FarolLM-Cifra-base** | ~300M | 24 | 1024 | 16 | 4 | 4096 | ~3-4 semanas |

**Recomendacao inicial:** comecar pelo `tiny` para validar pipeline end-to-end. So escalar para `small`/`base` apos pipeline limpo.

### 8.3 Detalhes arquiteturais

- **Norm:** RMSNorm pre-norm.
- **Activation:** SwiGLU em FFN.
- **Positional:** RoPE (Rotary Position Embedding), base=10000.
- **Attention:** Grouped Query Attention (GQA) com `n_kv_heads = n_heads / 4`.
- **Tie embeddings:** sim (input embed = output projection).
- **Dropout:** 0.0 (LLaMA-style); reativar so se observar overfit.
- **Init:** LLaMA-style (std=0.02, escalado por layer).

### 8.4 Opcao alternativa: continual pretraining

Como caminho mais barato, considerar:
1. Pegar **LLaMA 3.2 1B** ou **Qwen 2.5 0.5B**.
2. Expandir vocab com tokens musicais novos (extender embedding).
3. Continual pretraining em 100-200M tokens de cifra.

**Trade-off:**
- Pro: muito mais barato, ja sabe portugues e world knowledge.
- Con: tokenizer original nao trata acordes como atomicos (gambiarra com vocab extension).
- **Decisao:** primeiro fazer FarolLM-Cifra-tiny do zero. Se resultados forem ruins, fallback para continual pretraining.

---

## 9. Pipeline de Treinamento

### 9.1 Estagios

```
[Dataset bruto 2M cifras]
        │
        ▼
[Fase 1: Pre-processamento]  →  ~1M cifras limpas em JSONL + format treino
        │
        ▼
[Fase 2: Treinar tokenizer]  →  tokenizer.json (32k vocab)
        │
        ▼
[Fase 3: Tokenizar dataset]  →  arquivos .bin (numpy memmap) + indices
        │
        ▼
[Fase 4: Pretraining]        →  checkpoints/farolllm-cifra-tiny/
        │
        ▼
[Fase 5: SFT (instruction tuning)] → seguindo prompts (transposicao, geracao guiada)
        │
        ▼
[Fase 6: Avaliacao]          →  benchmarks + avaliacao humana
        │
        ▼
[Fase 7: Publicacao]         →  HF Hub + paper + demo
```

### 9.2 Hyperparameters (referencia para tiny)

| Param | Valor |
|---|---|
| Optimizer | AdamW |
| beta1, beta2 | 0.9, 0.95 |
| Weight decay | 0.1 |
| LR (peak) | 3e-4 |
| LR schedule | Cosine, warmup 2000 steps |
| LR min | 3e-5 |
| Grad clip | 1.0 |
| Batch size (tokens) | 256k tokens/step (gradient accumulation se preciso) |
| Sequence length | 2048 |
| Steps | ~3000-10000 (depende do dataset) |
| Precision | bf16 mixed (M4 suporta) |
| Eval interval | 500 steps |
| Save interval | 1000 steps |

### 9.3 SFT (Fase 5) — formato

Apos pretraining, fine-tune em **pares instrucao -> resposta** para varios casos de uso:

```json
{
  "instruction": "Gere uma cifra de forró em Sol maior sobre saudade do sertão",
  "input": "",
  "output": "<|cifra|>\n<|meta|>\ngenre: forró\nkey: G\n<|/meta|>\n..."
}
{
  "instruction": "Transponha a seguinte cifra de C para G",
  "input": "<cifra em C>",
  "output": "<cifra em G>"
}
{
  "instruction": "Quais acordes combinam com essa letra?",
  "input": "<letra sem acordes>",
  "output": "<cifra com acordes>"
}
```

**Origem dos pares SFT:**
- Sinteticos (gerados por templating + dataset original).
- Curados manualmente (~1000 exemplos de alta qualidade).
- Opcional: usar GPT-4/Claude para gerar candidatos, revisar humanamente.

### 9.4 Alinhamento (opcional, Fase 5.5)

DPO (Direct Preference Optimization) com pares de cifras boas vs ruins. Usar TRL library. Mais relevante se for liberar para uso publico.

### 9.5 Resumindo dependencias temporais

| Fase | Duracao estimada (M4) | Bloqueador |
|---|---|---|
| 1. Pre-proc | 3-7 dias | CPU (paralelizar) |
| 2. Tokenizer | 1-2 dias | CPU |
| 3. Tokenizar | 1 dia | CPU |
| 4. Pretrain tiny | 3-7 dias | GPU (MPS) |
| 5. SFT | 1-2 dias | GPU |
| 6. Eval | 3-5 dias | Humano + GPU |
| 7. Publicar | 3-5 dias | Docs + paper |

**Total estimado:** 4-8 semanas para v0.1 com modelo tiny.

---

## 10. Hardware e Compute

### 10.1 Primario: Mac Mini M4 64GB

- **GPU backend:** PyTorch MPS (Metal Performance Shaders).
- **Memoria unificada:** 64GB compartilhados CPU/GPU = grande vantagem para batch.
- **Throughput estimado (tiny, 50M):** ~10-30k tokens/s em bf16.

### 10.2 Secundario / scaling

Se for necessario escalar para small/base:

| Provider | Opcao | Custo aproximado |
|---|---|---|
| Lambda Labs | 1x A100 80GB | $1.10/h |
| RunPod | 1x A6000 48GB | $0.60/h |
| Google Cloud | TPU v3-8 | ~$8/h |
| Vast.ai | 1x 3090 24GB | $0.30/h |
| Modal | A100 serverless | pay-per-use |

**Estimativa total:** treino completo base (300M, 800M tokens) em A100 ~24-48h, custo $30-100.

### 10.3 Storage

- Dataset bruto + processado: ~50-100GB.
- Checkpoints: cada save ~1-3GB (tiny), ~5-10GB (small).
- Logs/W&B/TB: ~5GB.
- **Recomendacao:** SSD externo dedicado (>500GB).

---

## 11. Stack Tecnologica

### 11.1 Linguagens e runtime
- **Python 3.11+**
- **PyTorch 2.5+** (com suporte MPS)
- **CUDA opcional** para scaling cloud

### 11.2 Bibliotecas principais

| Lib | Versao | Para que |
|---|---|---|
| `torch` | 2.5+ | Backbone do treino |
| `transformers` | 4.45+ | Carregar/salvar modelos, infra HF |
| `tokenizers` | 0.20+ | Tokenizer custom |
| `sentencepiece` | 0.2+ | BPE training |
| `datasets` | 3.0+ | Carregar dataset, splits |
| `accelerate` | 1.0+ | Mixed precision, multi-GPU |
| `trl` | 0.11+ | SFT + DPO |
| `wandb` | latest | Tracking |
| `tensorboard` | latest | Tracking local |
| `litgpt` | 0.4+ | (opcional) framework de treino simplificado |
| `numpy`, `pandas`, `polars` | latest | Processamento de dados |
| `beautifulsoup4`, `lxml` | latest | Parsing HTML |
| `datasketch` | latest | MinHash para dedup |
| `langdetect`/`fasttext` | latest | Detecao de lingua |
| `mir_eval` | latest | Metricas musicais |
| `music21` | latest | (opcional) analise harmonica auxiliar |
| `gradio` | 5.0+ | Demo |

### 11.3 Tooling de dev

- **uv** ou **poetry** para gerenciar deps (uv recomendado, mais rapido).
- **ruff** linter + formatter.
- **pytest** para testes.
- **pre-commit** para hooks.
- **dvc** ou **git-lfs** para dataset versioning.
- **make**/`just` para tasks frequentes.

### 11.4 Estrutura pyproject.toml (esqueleto)

```toml
[project]
name = "farolllm-cifra"
version = "0.0.1"
requires-python = ">=3.11"
dependencies = [
    "torch>=2.5",
    "transformers>=4.45",
    "tokenizers>=0.20",
    "sentencepiece>=0.2",
    "datasets>=3.0",
    "accelerate>=1.0",
    "trl>=0.11",
    "wandb",
    "tensorboard",
    "numpy",
    "pandas",
    "polars",
    "beautifulsoup4",
    "lxml",
    "datasketch",
    "langdetect",
    "mir_eval",
    "gradio>=5.0",
]

[project.optional-dependencies]
dev = ["ruff", "pytest", "pre-commit", "ipython", "jupyter"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

---

## 12. Estrutura do Repositorio

```
farolllm-cifra/
├── CLAUDE.md                       # instrucoes para Claude Code (resumo do projeto)
├── README.md                       # README publico
├── HANDOFF.md                      # este documento
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
│
├── docs/
│   ├── 00_OBJETIVO.md
│   ├── 01_ARQUITETURA.md
│   ├── 02_DATASET.md
│   ├── 03_TOKENIZER.md
│   ├── 04_TRAINING.md
│   ├── 05_EVAL.md
│   ├── 06_PUBLICACAO.md
│   ├── DECISOES.md                 # log de decisoes cronologico
│   ├── RELATED_WORK.md             # papers, modelos, datasets relacionados
│   └── RISCOS.md
│
├── configs/
│   ├── tokenizer/
│   │   ├── vocab_atomic_chords.json
│   │   ├── vocab_structural_tokens.json
│   │   └── tokenizer_config.json
│   ├── model/
│   │   ├── tiny.yaml
│   │   ├── small.yaml
│   │   └── base.yaml
│   ├── train/
│   │   ├── pretrain_tiny.yaml
│   │   ├── pretrain_small.yaml
│   │   └── sft.yaml
│   └── data/
│       ├── splits.yaml
│       └── filters.yaml
│
├── data/                           # NAO commitar grandes (gitignored), usar DVC
│   ├── raw/                        # HTML/JSON brutos
│   ├── parsed/                     # JSONL pos parse
│   ├── filtered/                   # JSONL pos filtros
│   ├── tokenized/                  # .bin memmaps
│   └── sft/                        # pares instrucao-resposta
│
├── src/
│   └── farolllm_cifra/
│       ├── __init__.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── crawl.py            # se aplicavel, ou loaders
│       │   ├── parse.py            # parse HTML -> JSONL estruturado
│       │   ├── chord_regex.py      # regex e normalizacao de acordes
│       │   ├── structure.py        # detectar secoes
│       │   ├── dedup.py            # MinHash
│       │   ├── filters.py          # filtros de qualidade
│       │   ├── language.py         # detect lang
│       │   ├── genre.py            # inferir/classificar genero
│       │   ├── key.py              # inferir tom
│       │   ├── format.py           # JSONL -> texto plano para treino
│       │   └── splits.py           # train/val/test
│       │
│       ├── tokenizer/
│       │   ├── __init__.py
│       │   ├── chord_vocab.py      # gerar vocab inicial de acordes
│       │   ├── train.py            # treinar BPE
│       │   ├── tokenize.py         # tokenizar dataset
│       │   └── validate.py         # round-trip tests
│       │
│       ├── model/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── transformer.py      # implementacao decoder-only (LLaMA-style)
│       │   ├── attention.py
│       │   ├── rope.py
│       │   └── checkpointing.py
│       │
│       ├── train/
│       │   ├── __init__.py
│       │   ├── pretrain.py
│       │   ├── sft.py
│       │   ├── dpo.py              # opcional
│       │   ├── data_loader.py
│       │   ├── scheduler.py
│       │   └── utils.py
│       │
│       ├── eval/
│       │   ├── __init__.py
│       │   ├── perplexity.py
│       │   ├── transpose_acc.py    # acuracia em transposicao
│       │   ├── harmonic_eval.py    # plausibilidade harmonica
│       │   ├── genre_classify.py   # F1 em classificacao por progressao
│       │   └── human_eval_harness.py  # interface para avaliacao humana
│       │
│       ├── inference/
│       │   ├── __init__.py
│       │   ├── generate.py
│       │   └── sampling.py         # nucleus, temperature, etc.
│       │
│       └── demo/
│           ├── __init__.py
│           ├── gradio_app.py
│           └── examples.py
│
├── scripts/
│   ├── 01_parse_raw.py
│   ├── 02_clean_dataset.py
│   ├── 03_dedup.py
│   ├── 04_train_tokenizer.py
│   ├── 05_tokenize_dataset.py
│   ├── 06_pretrain.py
│   ├── 07_sft.py
│   ├── 08_eval.py
│   ├── 09_export_hf.py
│   ├── 10_run_demo.py
│   │
│   ├── multi_agent/
│   │   ├── sessions.json
│   │   ├── spawn.sh
│   │   ├── drive.sh
│   │   ├── take_over.sh
│   │   ├── open_dashboard.sh
│   │   └── _status_summary.sh
│   │
│   └── utils/
│       ├── inspect_cifra.py
│       ├── plot_loss.py
│       └── compare_tokenizers.py
│
├── notebooks/
│   ├── 01_explore_raw_data.ipynb
│   ├── 02_chord_distribution.ipynb
│   ├── 03_tokenizer_analysis.ipynb
│   ├── 04_eval_qualitative.ipynb
│   └── 05_demo_outputs.ipynb
│
├── tests/
│   ├── test_chord_regex.py
│   ├── test_parse.py
│   ├── test_dedup.py
│   ├── test_tokenizer.py
│   ├── test_model_forward.py
│   ├── test_train_step.py
│   ├── test_transpose.py
│   └── test_end_to_end_smoke.py
│
├── checkpoints/                    # gitignored, modelos salvos
│   └── .gitkeep
│
├── logs/                           # gitignored, logs de treino
│   └── .gitkeep
│
├── reports/                        # outputs de eval, plots, samples
│   └── .gitkeep
│
└── .claude/                        # configs para Claude Code
    ├── settings.json
    ├── settings.local.json
    └── agents/
        ├── arquiteto.md
        ├── pipeline-dev.md
        ├── docs-writer.md
        ├── qa-tester.md
        └── devops-installer.md
```

### 12.1 Arquivos obrigatorios na raiz

- `CLAUDE.md` — versao curta com regras do projeto + links pra docs/.
- `README.md` — user-facing, com badges, exemplo de uso, link pra HF.
- `HANDOFF.md` — este documento.
- `pyproject.toml` — deps.

---

## 13. Sistema Multi-agente

Heranca direta do FarolLM principal (mesma estrutura). Cada agente tem responsabilidade clara, separados por arquivos em `.claude/agents/`.

### 13.1 Agentes e responsabilidades

#### `arquiteto` (coordenador)
- **Quem invoca:** o humano (Giordano), via prompt no terminal principal.
- **O que faz:**
  - Mantem visao geral do projeto.
  - Decide arquitetura, particiona trabalho, escolhe agente certo.
  - **Unico ponto de contato com o usuario humano.**
  - Atualiza `docs/DECISOES.md` apos cada decisao significativa.
  - Le e atualiza `docs/00_OBJETIVO.md`, `docs/01_ARQUITETURA.md`.
- **O que NAO faz:** codigo extenso, ops, redacao final de docs.
- **Inputs:** prompts do usuario, status dos outros agentes.
- **Outputs:** decisoes, tarefas delegadas, atualizacao de docs centrais.

#### `pipeline-dev` (engenheiro principal)
- **Quem invoca:** `arquiteto`.
- **O que faz:**
  - Escreve **todo** o codigo do pipeline em `src/farolllm_cifra/`.
  - Implementa data loaders, tokenizer, modelo, loops de treino, eval.
  - Roda experimentos pequenos para validar.
  - Escreve testes basicos junto com o codigo.
- **O que NAO faz:** infra, CI/CD, deploy, redacao de docs publicos.
- **Inputs:** especificacao do arquiteto.
- **Outputs:** PRs com codigo funcional + testes basicos.

#### `qa-tester` (testes e validacao)
- **Quem invoca:** `arquiteto` ou apos PR do `pipeline-dev`.
- **O que faz:**
  - Escreve testes (unit, integration, end-to-end smoke).
  - Roda benchmarks de eval.
  - Valida criterios de aceitacao.
  - **Avaliacao qualitativa:** olha samples gerados, marca o que ta bom/ruim.
  - Compara contra baselines (ChatMusician, GPT-4 com prompting).
- **Outputs:** relatorios em `reports/`, issues abertas se algo falha.

#### `docs-writer` (documentacao)
- **Quem invoca:** `arquiteto`, antes de release ou ao consolidar fase.
- **O que faz:**
  - Escreve `README.md` user-facing.
  - Escreve docs em `docs/` (00..06).
  - Escreve model card pra HF Hub.
  - Comeca o draft do paper.
  - **Tom:** direto, sem floreios. Sem emojis (regra global).
- **Outputs:** docs em markdown polidos.

#### `devops-installer` (infra e setup)
- **Quem invoca:** `arquiteto` no inicio ou quando precisar de algo de infra.
- **O que faz:**
  - Setup inicial do repo (pyproject, pre-commit, ruff, pytest).
  - Configura W&B, TensorBoard.
  - Configura git-lfs/DVC se for usar.
  - Scripts de deploy (HF Hub upload, Gradio Spaces).
  - Em caso de scaling, configura ambiente em provider cloud.
- **Outputs:** ambiente reproduzivel.

### 13.2 Convencoes do multi-agente (do CLAUDE.md original)

- `sessions.json` mapeia agente -> session_id do Claude Code.
- `scripts/multi_agent/spawn.sh <agente>` cria sessao tmux.
- `scripts/multi_agent/drive.sh <agente> "<prompt>"` manda prompt em background.
- `scripts/multi_agent/take_over.sh <agente>` humano assume.
- `scripts/multi_agent/open_dashboard.sh` abre grade tmux com todos.

### 13.3 Workflow tipico

1. **Humano** abre dashboard: `./scripts/multi_agent/open_dashboard.sh`
2. **Humano** fala com `arquiteto`: "vamos comecar a fase de pre-processamento"
3. **Arquiteto** decompoe e delega para `pipeline-dev`: "implementa `src/farolllm_cifra/data/parse.py` seguindo spec X"
4. **Pipeline-dev** implementa, escreve testes, commita.
5. **Qa-tester** rodam testes, valida.
6. **Arquiteto** consolida, atualiza `DECISOES.md`.
7. **Docs-writer** atualiza docs apos cada fase.

### 13.4 Modelo recomendado por agente

- `arquiteto`: opus (decide bem, raramente).
- `pipeline-dev`: sonnet/opus (codigo extenso, qualidade alta).
- `qa-tester`: sonnet/haiku (varredura ampla, paralelizavel).
- `docs-writer`: sonnet (textos cuidadosos).
- `devops-installer`: haiku/sonnet (tasks pontuais).

---

## 14. Roadmap por Fases

### Fase 0 — Setup (3-5 dias)
**Owner:** devops-installer + arquiteto

- [ ] Criar repo `farolllm-cifra` no GitHub.
- [ ] Setup pyproject.toml, uv lock, pre-commit, ruff, pytest.
- [ ] Criar estrutura de pastas.
- [ ] Configurar `.claude/` com agentes.
- [ ] Definir `sessions.json` e scripts multi-agente.
- [ ] Configurar W&B + TensorBoard.
- [ ] Configurar DVC ou git-lfs para dataset.
- [ ] Copiar/escrever `CLAUDE.md`, `README.md`, `HANDOFF.md` (este).
- [ ] Setup CI basico (GitHub Actions: ruff + pytest).

**DoD:** repo limpo, `pytest` roda 0 testes ok, `ruff` passa.

### Fase 1 — Dataset (1-2 semanas)
**Owner:** pipeline-dev + qa-tester

- [ ] Importar dados brutos (~2M cifras) para `data/raw/`.
- [ ] Implementar `parse.py` (HTML -> JSONL estruturado).
- [ ] Implementar `chord_regex.py` (validacao e normalizacao).
- [ ] Implementar `structure.py` (detectar secoes).
- [ ] Implementar `dedup.py` (MinHash).
- [ ] Implementar `filters.py` (filtros de qualidade).
- [ ] Implementar `language.py` (detec pt-BR).
- [ ] Implementar `genre.py` (classificacao).
- [ ] Implementar `key.py` (inferencia de tom).
- [ ] Implementar `format.py` (JSONL -> texto plano).
- [ ] Implementar `splits.py` (stratified by artist).
- [ ] Rodar pipeline completo.
- [ ] Notebook `01_explore_raw_data.ipynb` com estatisticas.
- [ ] Notebook `02_chord_distribution.ipynb`.
- [ ] Testes: 80%+ coverage em `src/farolllm_cifra/data/`.

**DoD:** ~1M cifras limpas em `data/filtered/*.jsonl`, splits prontos, notebook com estatisticas.

### Fase 2 — Tokenizador (3-5 dias)
**Owner:** pipeline-dev

- [ ] `chord_vocab.py`: gerar lista de top-3000 acordes.
- [ ] `train.py`: treinar BPE com vocab inicial.
- [ ] `tokenize.py`: tokenizar dataset -> .bin.
- [ ] `validate.py`: round-trip tests, comparacao com LLaMA tokenizer.
- [ ] Notebook `03_tokenizer_analysis.ipynb`.

**DoD:** `tokenizer.json` salvo, eficiencia ~30%+ melhor que LLaMA em corpus de cifras, round-trip 100%.

### Fase 3 — Modelo + Pretraining (1-2 semanas)
**Owner:** pipeline-dev + qa-tester

- [ ] Implementar `model/transformer.py` (LLaMA-style).
- [ ] Implementar `train/pretrain.py`.
- [ ] Configurar W&B logging.
- [ ] Treinar `tiny` (50M) em subset (100k cifras) — smoke test.
- [ ] Validar loss decrescendo, samples plausiveis.
- [ ] Treinar `tiny` em dataset completo.
- [ ] Salvar checkpoints regularmente.

**DoD:** modelo tiny treinado, perplexidade < baseline LLaMA 3.2 1B no mesmo split, samples qualitativos plausiveis.

### Fase 4 — SFT (3-7 dias)
**Owner:** pipeline-dev

- [ ] Construir dataset SFT (~10k pares).
  - 50% sinteticos (transposicao, geracao por genero/tom).
  - 30% reformulacoes do dataset original.
  - 20% manualmente curados.
- [ ] Implementar `train/sft.py` com TRL.
- [ ] Treinar.
- [ ] Avaliacao qualitativa de samples.

**DoD:** modelo segue instrucoes em pt-BR para todos os 6 casos de uso de O1-O6.

### Fase 5 — Avaliacao (1 semana)
**Owner:** qa-tester

- [ ] Implementar metricas em `eval/`.
- [ ] Rodar benchmarks automatizados.
- [ ] Setup harness de avaliacao humana (Gradio simples + planilha).
- [ ] Convidar 5-10 musicos para avaliar 100 samples.
- [ ] Comparar contra baselines:
  - LLaMA 3.2 1B (zero-shot prompt).
  - ChatMusician (com adapter pra cifra).
  - GPT-4 (zero-shot, via API se possivel).
- [ ] Relatorio em `reports/eval_v1.md`.

**DoD:** relatorio completo com tabelas, modelo bate todos os baselines em geracao de cifra pt-BR.

### Fase 6 — Demo e Publicacao (1-2 semanas)
**Owner:** docs-writer + devops-installer

- [ ] Implementar `demo/gradio_app.py`.
- [ ] Subir para HF Spaces.
- [ ] Subir modelo no HF Hub com model card completa.
- [ ] Subir dataset (se licenciamento permitir) — senao, subir so o pipeline + samples.
- [ ] Escrever paper (draft em LaTeX ou markdown).
- [ ] Submeter para arxiv.

**DoD:** modelo publico no HF, demo funcional, paper em arxiv.

### Fase 7 — Iteracao (continuo)
- Scaling: small e base se houver compute.
- DPO se feedback do publico sugerir.
- Generalizar para espanhol/ingles.
- Multimodal: integrar com audio (futuro).

---

## 15. Criterios de Aceitacao

### 15.1 Tecnicos

- [ ] Tokenizer trata >95% dos acordes como token unico.
- [ ] Modelo treina sem OOM no M4 64GB.
- [ ] Perplexidade no val set < baseline (LLaMA 3.2 1B com mesmo prompt).
- [ ] Transposicao automatica: acuracia >95% em casos simples.
- [ ] Geracao: <5% de samples com acordes invalidos (acorde que nao parseia).

### 15.2 Qualitativos

- [ ] Em 100 samples gerados, >70% sao avaliados como "tocavel" por musicos.
- [ ] Generos brasileiros tem caracteristicas distintas nas geracoes (samba diferente de forro etc.).
- [ ] Metadata respeitada: se prompt diz "key: G", saida fica em G.

### 15.3 Reprodutibilidade

- [ ] Pipeline roda end-to-end com `make all` (ou equivalente).
- [ ] Seeds fixadas para reproducibilidade.
- [ ] Versoes pinned no `uv.lock`.
- [ ] Model card no HF tem todas as infos (data, hyperparams, eval).

### 15.4 Documentacao

- [ ] README com quickstart em <5min.
- [ ] Docs `docs/00..06` completos.
- [ ] `DECISOES.md` cronologico atualizado.
- [ ] Paper draft.

---

## 16. Avaliacao e Benchmarks

### 16.1 Metricas automaticas

| Metrica | Definicao | Range esperado |
|---|---|---|
| **Perplexity** | Padrao LM | tiny: 4-6 |
| **Chord validity rate** | % acordes gerados que sao parseáveis | >95% |
| **Key consistency** | % de cifras geradas que ficam no tom prometido | >85% |
| **Genre consistency** | F1 de classificador genero-by-progression | >0.7 |
| **Transpose accuracy** | Acuracia em transposicao exata | >95% simples, >85% complexa |
| **Unique chord ratio** | Diversidade de acordes (vs colapso para C-G-Am-F) | >0.5 |
| **Repetition penalty score** | Quanto o modelo repete (n-gram repetition) | < baseline |

### 16.2 Avaliacao humana

**Protocolo:**
- 100 cifras geradas (10 por genero, 10 generos).
- 5 musicos amadores + 2 musicos profissionais avaliam.
- Cada avaliador olha cifra, opcionalmente toca, da nota:
  - **Plausibilidade harmonica (1-5):** as progressoes fazem sentido?
  - **Aderencia ao genero (1-5):** soa como o genero pedido?
  - **Qualidade da letra (1-5):** letra coerente, em portugues correto?
  - **Tocabilidade (1-5):** consigo tocar isso?
  - **Geral (1-5):** nota global.

**Baselines pra comparar:**
- LLaMA 3.2 1B (zero-shot).
- GPT-4 (zero-shot, prompt elaborado).
- ChatMusician (com adapter pra formato cifra).

### 16.3 Benchmark publico (proposto)

Criar benchmark `CifraBench`:
- 500 prompts (genre, key, theme).
- Held-out, nao usado em treino.
- Metricas automaticas + plataforma de submissao.

---

## 17. Etica, Licenca, Compliance

### 17.1 Origem dos dados

Cifras sao **conteudo gerado por usuarios** em sites tipo CifraClub. Tem dois niveis de copyright:
1. **Letra:** copyright do autor/editora.
2. **Cifra:** transcricao do usuario (cifra em si geralmente nao tem copyright forte, mas e zona cinza).

### 17.2 Postura

- **Dataset NAO sera publicado bruto.** So estatisticas, samples e scripts de reproducao a partir do site origem.
- **Modelo pode ser publicado** sob argumento de uso transformativo (research, educacao).
- **Justificar como pesquisa academica** (mesma logica de CulturaX/FineWeb).
- **Citar fontes** sempre que possivel (artista, link CifraClub).
- **Mecanismo de opt-out:** artistas/editoras podem solicitar remocao.

### 17.3 Lincenca do codigo
- **MIT** ou **Apache 2.0** para codigo.
- **CC-BY-NC** para modelo (uso comercial requer autorizacao).

### 17.4 LGPD
- Dados nao contem PII (so nome de artista, ja publico).
- Nao precisa de DPIA, mas registrar em `docs/COMPLIANCE.md`.

### 17.5 Caveats do modelo (model card)
- "Pode gerar letras com vies, nao usar em producao sem revisao humana."
- "Nao substitui licenca de cover/perform de musicas reais."
- "Treinado em dados majoritariamente em portugues; performance em outras linguas pode ser ruim."

---

## 18. Plano de Publicacao

### 18.1 Artefatos

1. **Codigo:** GitHub repo publico, MIT.
2. **Modelo:** HuggingFace Hub (`UFPE-CIn/farolllm-cifra-tiny`), CC-BY-NC.
3. **Dataset:** **nao publicado bruto.** Publicar scripts de reproducao + samples + estatisticas.
4. **Demo:** HF Spaces (Gradio).
5. **Paper:** arxiv + venue (ISMIR/ACL/LREC).
6. **Blogpost:** Medium ou similar, em portugues, para audiencia musical.

### 18.2 Cronograma

| Marco | Quando | Status |
|---|---|---|
| MVP tiny | Mes 1-2 | a iniciar |
| Eval completa | Mes 2-3 | - |
| Modelo no HF + demo | Mes 3 | - |
| Paper arxiv | Mes 3-4 | - |
| Submissao venue | Mes 4-6 (depende do call) | - |

### 18.3 Outreach

- Twitter/X anuncio em PT e EN.
- Linkedin (audiencia academica BR).
- Mailing list HF papers (https://huggingface.co/papers).
- Submeter pra **MusicMeta** e **r/MachineLearning**.
- Apresentar em encontros locais (Pernambuco Tech, RecData).

---

## 19. Riscos e Contingencias

| Risco | Probabilidade | Impacto | Mitigacao |
|---|---|---|---|
| Dataset com baixa qualidade pos-parsing | Media | Alto | Investir em filtros, fazer validacao manual de amostra |
| Modelo nao converge no M4 | Baixa | Alto | Fallback para cloud GPU |
| Tokenizer com acordes raros nao cobertos | Media | Medio | Iterar vocab; usar fallback BPE |
| Copyright takedown post-publicacao | Media | Alto | Postura defensiva; opt-out; nao publicar dataset bruto |
| ChatMusician/outro modelo sai antes com mesma proposta | Baixa | Alto | Manter velocidade; focar diferencial pt-BR |
| Avaliacao humana inviavel (sem musicos disponiveis) | Media | Medio | Recrutar via UFPE, comunidade musical Recife |
| M4 insuficiente para scaling | Alta (pra base) | Medio | Cloud GPU; manter tiny como deliverable principal |
| Tempo subestimado | Alta | Medio | Marcos curtos; descopar agressivamente |

---

## 20. Decisoes Pendentes

Estas precisam de input antes/durante a execucao:

1. **Tamanho do modelo:** comecar tiny (50M) ou pular pra small (150M)?
   - Recomendacao: tiny primeiro.
2. **Treinar do zero vs continual pretraining em LLaMA 3.2 1B?**
   - Recomendacao: do zero pra alinhar com objetivo academico do FarolLM. Mas validar com SLM tiny primeiro.
3. **Publicar dataset bruto ou nao?**
   - Recomendacao: NAO. So scripts + samples.
4. **Multimodal/audio no futuro?**
   - Decisao: fora de escopo v0.
5. **Espanhol/ingles incluir desde ja?**
   - Recomendacao: pt-BR puro v0; expandir na v1.
6. **Hospedar demo onde?**
   - Recomendacao: HF Spaces (gratuito, integrado).
7. **Licenca do modelo:** CC-BY-NC ou Apache?
   - Recomendacao: CC-BY-NC pra v0 (conservador).

---

## 21. Referencias Completas

### 21.1 Papers (todos com link)

#### Music LLMs
- ChatMusician: https://arxiv.org/abs/2402.16153
- MuPT: https://arxiv.org/abs/2404.06393
- MIDI-LLM: https://arxiv.org/abs/2511.03942
- SongComposer: https://arxiv.org/abs/2402.17645
- SongMASS: https://arxiv.org/abs/2012.05168
- Amuse: https://arxiv.org/abs/2412.18940
- MMM (Multi-Track Music Machine): https://arxiv.org/abs/2008.06048
- Jazz Transformer: https://arxiv.org/abs/2008.01307
- Pop Music Transformer: https://arxiv.org/abs/2002.00212
- TunesFormer: https://arxiv.org/abs/2301.02884
- MusiConGen: https://arxiv.org/abs/2407.15060
- MusicGen-Chord: https://arxiv.org/abs/2412.00325
- SegTune: https://arxiv.org/abs/2510.18416
- Unlocking Pre-Trained Music LMs: https://arxiv.org/abs/2408.15176
- Text2midi-InferAlign: https://arxiv.org/abs/2505.12669

#### Chord/Harmony
- BACHI (chord recognition): https://arxiv.org/abs/2510.06528
- MMT-BERT (chord-aware): https://arxiv.org/abs/2409.00919
- Chord-Conditioned Melody Harmonization (DeepChoir): https://arxiv.org/abs/2202.08423
- Domain-Knowledge Music Embedding: https://arxiv.org/abs/2212.00973
- Generating Lead Sheets with Affect: https://arxiv.org/abs/2104.13056

#### Tablature
- DadaGP: https://arxiv.org/abs/2107.14653
- Fretting-Transformer: https://arxiv.org/abs/2506.14223
- Rock Guitar Tablature Gen via NLP: https://arxiv.org/abs/2301.05295
- MIDI-to-Tab Masked LM: https://arxiv.org/abs/2408.05024
- ML for MIDI-Guitar Tab Conversion: https://arxiv.org/abs/2510.10619

#### Datasets
- Chordonomicon: https://arxiv.org/abs/2410.22046

#### LLM basics
- Chinchilla (Hoffmann et al.): https://arxiv.org/abs/2203.15556
- LLaMA: https://arxiv.org/abs/2302.13971
- LLaMA 2: https://arxiv.org/abs/2307.09288
- LLaMA 3: https://arxiv.org/abs/2407.21783
- RoPE: https://arxiv.org/abs/2104.09864
- SwiGLU: https://arxiv.org/abs/2002.05202
- GQA: https://arxiv.org/abs/2305.13245
- RMSNorm: https://arxiv.org/abs/1910.07467

#### Alignment
- DPO: https://arxiv.org/abs/2305.18290
- RLHF (InstructGPT): https://arxiv.org/abs/2203.02155

#### Tokenization
- SentencePiece: https://arxiv.org/abs/1808.06226
- BPE original (Sennrich): https://arxiv.org/abs/1508.07909

### 21.2 Modelos no HuggingFace

- m-a-p/ChatMusician: https://huggingface.co/m-a-p/ChatMusician
- m-a-p/ChatMusician-Base: https://huggingface.co/m-a-p/ChatMusician-Base
- Meta-Llama-3.2-1B: https://huggingface.co/meta-llama/Llama-3.2-1B
- Qwen2.5-0.5B: https://huggingface.co/Qwen/Qwen2.5-0.5B

### 21.3 Datasets relacionados

- Chordonomicon: https://huggingface.co/datasets (procurar)
- DadaGP: https://github.com/dada-bots/dadaGP
- POP909: https://github.com/music-x-lab/POP909-Dataset
- Lakh MIDI: https://colinraffel.com/projects/lmd/
- CulturaX: https://huggingface.co/datasets/uonlp/CulturaX
- FineWeb-2: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2

### 21.4 Frameworks / codebases referencia

- **NanoGPT** (Karpathy) — minimal LM trainer: https://github.com/karpathy/nanoGPT
- **minbpe** (Karpathy) — minimal BPE tokenizer: https://github.com/karpathy/minbpe
- **LitGPT** — framework de treinamento: https://github.com/Lightning-AI/litgpt
- **TRL** — Transformer RL: https://github.com/huggingface/trl
- **HuggingFace Transformers:** https://github.com/huggingface/transformers
- **HuggingFace Tokenizers:** https://github.com/huggingface/tokenizers
- **Accelerate:** https://github.com/huggingface/accelerate

### 21.5 Ferramentas musicais

- music21 (analise musical Python): https://web.mit.edu/music21/
- mir_eval (metricas MIR): https://github.com/mir-evaluation/mir_eval
- pretty_midi: https://github.com/craffel/pretty-midi

### 21.6 Lista negra (NAO recomendado)

- Megatron-LM (overkill para esse tamanho).
- DeepSpeed Stage 3 (idem).
- Tokenizers em rust from-scratch (use HF Tokenizers).

---

## 22. Apendices

### A. Exemplo completo de cifra processada

**Raw (CifraClub):**
```
Asa Branca - Luiz Gonzaga
Tom: G

[Intro] G  D7  G

G                       C
Quando olhei a terra ardendo
D7                      G
Qual fogueira de São João
G                       C
Eu perguntei a Deus do céu, ai
D7                      G
Por que tamanha judiação
```

**Parseado (JSONL):**
```json
{
  "id": "asa_branca_lg_001",
  "artist": "Luiz Gonzaga",
  "title": "Asa Branca",
  "genre": "forró",
  "subgenre": "forró pé de serra",
  "key": "G",
  "capo": 0,
  "language": "pt-BR",
  "structured": [
    {
      "section": "intro",
      "chords_inline": "G  D7  G"
    },
    {
      "section": "verse_1",
      "lines": [
        {"chords": "G                       C",
         "lyrics": "Quando olhei a terra ardendo"},
        {"chords": "D7                      G",
         "lyrics": "Qual fogueira de São João"},
        {"chords": "G                       C",
         "lyrics": "Eu perguntei a Deus do céu, ai"},
        {"chords": "D7                      G",
         "lyrics": "Por que tamanha judiação"}
      ]
    }
  ],
  "chord_vocabulary": ["G", "C", "D7"]
}
```

**Formato de treino (texto plano):**
```
<|cifra|>
<|meta|>
artist: Luiz Gonzaga
title: Asa Branca
genre: forró
key: G
capo: 0
language: pt-BR
<|/meta|>
<|body|>
<|intro|>
G D7 G

<|verse_1|>
G                       C
Quando olhei a terra ardendo
D7                      G
Qual fogueira de São João
G                       C
Eu perguntei a Deus do céu, ai
D7                      G
Por que tamanha judiação
<|/body|>
<|end|>
```

**Apos tokenizer (ilustrativo):**
```
[<|cifra|>, <|meta|>, artist:, _Luiz, _Gonzaga, \n, title:, _Asa, _Branca, ...,
 <|/meta|>, <|body|>, <|intro|>, \n, G, _, D7, _, G, \n\n,
 <|verse_1|>, \n, G, _spaces_, C, \n, Quando, _olhei, _a, _terra, _ardendo, ...,
 <|/body|>, <|end|>]
```

### B. Exemplo de prompt SFT

```json
{
  "messages": [
    {"role": "system", "content": "Voce e um assistente musical especializado em musica brasileira."},
    {"role": "user", "content": "Gere uma cifra de samba em Re menor sobre saudade."},
    {"role": "assistant", "content": "<|cifra|>\n<|meta|>\ngenre: samba\nkey: Dm\n<|/meta|>\n<|body|>\n..."}
  ]
}
```

### C. Comandos rapidos esperados (Makefile)

```makefile
.PHONY: setup data tokenizer pretrain sft eval demo all

setup:
	uv sync

data:
	python scripts/01_parse_raw.py
	python scripts/02_clean_dataset.py
	python scripts/03_dedup.py

tokenizer:
	python scripts/04_train_tokenizer.py
	python scripts/05_tokenize_dataset.py

pretrain:
	python scripts/06_pretrain.py --config configs/train/pretrain_tiny.yaml

sft:
	python scripts/07_sft.py --config configs/train/sft.yaml

eval:
	python scripts/08_eval.py

demo:
	python scripts/10_run_demo.py

all: setup data tokenizer pretrain sft eval
```

### D. Checklist primeira semana

```
Dia 1-2 (setup):
[ ] criar repo, pyproject, estrutura
[ ] copiar HANDOFF.md, escrever CLAUDE.md curto
[ ] setup pre-commit, ruff, pytest
[ ] configurar agentes em .claude/agents/

Dia 3-4 (data exploration):
[ ] importar 1000 cifras de amostra
[ ] notebook explorando estrutura, parseando
[ ] decidir estrategia de regex de acordes
[ ] documentar formato em docs/02_DATASET.md

Dia 5-7 (parsing real):
[ ] implementar parse.py completo
[ ] rodar em 10k amostras
[ ] medir qualidade do parsing
[ ] iterar
```

### E. Regex de acorde (ponto de partida)

```python
CHORD_REGEX = re.compile(
    r'^'
    r'([A-G][#b]?)'              # nota fundamental
    r'(m|maj|min|dim|aug|sus|°|\+)?'  # qualidade
    r'(\d+)?'                    # extensao numerica (7, 9, 11, 13)
    r'((?:add|sus|maj|m|b|#)\d+)*'  # adicoes
    r'(/[A-G][#b]?)?'            # baixo (slash chord)
    r'$'
)
```

Validar essa contra 10k acordes reais antes de confiar.

### F. Lista nao-exaustiva de tokens estruturais comuns em cifras BR

- [Intro], [Introdução], (Intro)
- [Verso 1], [Verso 2], [V1], [V2]
- [Refrão], [Refrao], [Estribilho], (Refrão)
- [Pré-refrão], [Pre-refrao]
- [Ponte], [Bridge]
- [Solo], [Improviso]
- [Outro], [Final], [Fim]
- [Interlúdio]
- [Coda]
- [Tag]
- [Modulação]

Normalizar tudo para conjunto canonico: `intro, verse_N, pre_chorus, chorus, bridge, solo, outro, interlude, coda`.

### G. Glossario rapido

- **Cifra:** formato texto com acordes alinhados acima das silabas.
- **Acorde:** combinacao de 3+ notas tocadas simultaneamente (C, Am7, etc.).
- **Tom (key):** tonalidade central da musica (G major, A minor).
- **Transposicao:** mover toda a musica para outra tonalidade (subir/descer todos os acordes).
- **Progressao:** sequencia de acordes (ex: I-V-vi-IV em C = C-G-Am-F).
- **Slash chord:** acorde com baixo diferente da fundamental (C/E = C com baixo em E).
- **SLM/LLM:** Small/Large Language Model.
- **BPE:** Byte Pair Encoding, algoritmo de tokenizacao.
- **SFT:** Supervised Fine-Tuning.
- **DPO:** Direct Preference Optimization.
- **MIR:** Music Information Retrieval.

### H. Contato / autor original

- **Giordano R. E. Cabral** — grec@cin.ufpe.br
- **UFPE - Centro de Informatica (CIn)**
- Recife, Pernambuco, Brasil

### I. Prompt inicial para a outra sessao do Claude Code

Cole isso no primeiro turno da nova sessao:

```
Vou comecar o projeto FarolLM-Cifra do zero em um repositorio novo.
Leia o arquivo HANDOFF_FAROLLM_CIFRA.md inteiro antes de qualquer coisa.
Apos ler, faca:
1. Resumo em 200 palavras do que entendeu.
2. Liste as 3 primeiras tarefas concretas que vamos fazer hoje.
3. Pergunte o que ainda esta ambiguo (max 5 perguntas).
NAO comece a implementar antes da aprovacao do plano.
```

---

## Fim do documento

Versao 1.0 — 2026-06-02
Proxima revisao prevista apos Fase 0 (setup) concluida.

Se algo aqui esta ambiguo ou faltando, abrir issue ou ajustar diretamente — esse documento e vivo.
