# Fontes de Dados: Portugues Informal e Regional

Levantamento de fontes publicas de texto informal, coloquial e regional
em portugues brasileiro. Foco em linguagem falada e variacao nordestina.

---

## Mega-Corpora Prontos (pre-treinamento)

| Dataset | Tokens | Conteudo | Licenca | URL |
|---|---|---|---|---|
| **GigaVerbo** (TucanoBR) | 200B+ | Web, artigos, conversas, legal | Mista | huggingface.co/datasets/TucanoBR/GigaVerbo |
| **Jabuticaba** (SoberanIA) | 139B+ | Noticias, legal, user-generated | Formulario | huggingface.co/datasets/soberania/jabuticaba |
| **CulturaX** (pt subset) | Bilhoes | mC4 + OSCAR | Aberta | huggingface.co/datasets/uonlp/CulturaX |
| **FineWeb-2** (pt subset) | Bilhoes | CommonCrawl filtrado | ODC-By | huggingface.co/datasets/HuggingFaceFW/fineweb-2 |
| **BrWaC** | 2.68B | Web brasileira | Academica | huggingface.co/datasets/UFRGS/brwac |
| **Portuguese-PD** | 672M palavras | Dominio publico (7.840 titulos) | Livre | huggingface.co/datasets/PleIAs/Portuguese-PD |
| **Carolina Corpus** | 823M palavras | Instrucional, juridico, social, jornalismo | Aberta | huggingface.co/datasets/carolina-c4ai/corpus-carolina |

**Nota:** GigaVerbo e Jabuticaba sao os mais completos e ja limpos.
Juntos dao ~340B tokens — mais que suficiente para pre-treinar o FarolLM.

---

## Linguagem Informal / Coloquial

### Reddit pt-BR
- **Fonte:** Pushshift Reddit dumps (files.pushshift.io/reddit/comments/)
- **Como:** Baixar dumps mensais (.zst), filtrar por subreddits brasileiros
  (r/brasil, r/desabafos, r/futebol, r/investimentos, r/brasilivre)
  ou por deteccao de lingua (fastText)
- **Volume:** ~1-5B tokens (estimado)
- **Informalidade:** Alta (girias, abreviacoes, humor)
- **Legal:** Conteudo publico

### Twitter/X em portugues
- **Datasets existentes no HuggingFace:**
  - ToLD-Br: 21K tweets anotados (JAugusto97/told-br)
  - TweetSentBR: 15K+ tweets (eduagarcia/tweetsentbr_fewshot)
  - fpaulino/portuguese-tweets
- **Limitacao:** Datasets pequenos (dezenas de milhares). API do Twitter
  ficou cara desde 2023. Util para fine-tuning, nao pre-treino.

### Telegram publico brasileiro
- **Dataset existente:** 10.7M posts de 968 comunidades brasileiras
  (arXiv:2601.18622)
- **Ferramentas de scraping:** ergoncugler/web-scraping-telegram,
  Telethon, Pyrogram
- **Legal:** Grupos publicos sao acessiveis por qualquer pessoa

### Forums brasileiros (scraping)
- **Hardmob** (hardmob.com) — games, tech, promoforum. Desde ~2005.
- **Adrenaline** (adrenaline.com.br) — hardware, off-topic
- **Skyscrapercity BR** — urbanismo, cidades
- **Estimativa:** Dezenas de GB por forum

---

## Fala Transcrita (a fonte mais valiosa para linguagem falada)

### Tagarela — 8.972 horas de podcasts transcritos
- **Paper:** arXiv:2603.15326
- **Subsets:** Completo (8.972h com disfluencias) e limpo (2.800h)
- **Pipeline:** yt-dlp + diarizacao + denoising + Whisper large-v3
- **Licenca:** Academica

### CORAA — 290 horas de audio transcrito
- **URL:** huggingface.co/datasets/gabrielrstan/CORAA-v1.1
- **Fontes incluidas:** NURC-Recife (!), SP2010, C-ORAL-Brasil, TEDx
- **Licenca:** CC BY-NC-ND 4.0
- **CONTEM DADOS DE RECIFE**

### NURC Digital — Fala culta urbana de Recife
- **URL:** fale.ufal.br/projeto/nurcdigital/
- **Tamanho:** 32 inqueritos com audio + transcricoes
- **Variedade:** Fala de Recife, Pernambuco
- **Licenca:** Academica, download gratuito (CNPq)
- **EXATAMENTE o que precisamos para variacao pernambucana**

### C-ORAL-BRASIL — Fala espontanea informal
- **Tamanho:** 208K palavras, 21h de gravacao
- **Variedade:** Fala informal de BH (MG)
- **Licenca:** Academica (UFMG)

### Transcrever por conta propria (Whisper)
- **Ferramenta:** Whisper large-v3 ou freds0/distil-whisper-large-v3-ptbr
- **Canais sugeridos:** Flow Podcast, PodPah, Mano a Mano, Nerdcast,
  podcasts pernambucanos locais
- **Legal:** Audio publico; pesquisa academica coberta por fair use

---

## Dados Regionais Nordestinos / Pernambucanos

### Literatura em dominio publico
- **Euclides da Cunha** (m. 1909) — "Os Sertoes" (linguagem sertaneja)
- **Castro Alves** (m. 1871) — poesia baiana
- **Tobias Barreto** (m. 1889) — ensaios (Recife, Escola do Recife)
- **Joaquim Nabuco** (m. 1910) — ensaios abolicionistas (Recife)
- **Jose de Alencar** (m. 1877) — "O Sertanejo", regionalismos
- **Portal:** dominiopublico.gov.br + Project Gutenberg
- **HuggingFace:** PleIAs/Portuguese-PD (672M palavras em dominio publico)

**Ariano Suassuna:** Faleceu em 2014, dominio publico so em 2085.
Nao pode ser usado sem autorizacao dos herdeiros.

### Cordel
- Acervos da Academia Brasileira de Literatura de Cordel
- Projeto Cordel UFPE (verificar disponibilidade)
- Muitos folhetos antigos em dominio publico

### Letras de musica
- **4MuLA Dataset:** 96K musicas, 76 generos (zenodo.org/records/4585498)
- **138K letras brasileiras:** 14 generos incluindo forro, axe, samba
  (arXiv:2003.05377)
- **Vagalume API:** centenas de milhares de letras (api.vagalume.com.br)
- **Generos regionais:** frevo, maracatu, manguebeat, forro, brega

### WhatsApp (pesquisa academica)
- **FakeWhatsApp.Br:** mensagens anotadas de grupos publicos
  (github.com/cabrau/FakeWhatsApp.Br)
- **COVID19.BR:** 269K mensagens de grupos publicos, anonimizado

---

## Estrategia de Dados para o FarolLM

### Pre-treinamento (bilhoes de tokens, formal + informal)
1. GigaVerbo (200B tokens) — base formal
2. FineWeb-2 pt + CulturaX pt — reforco
3. Reddit pt-BR filtrado do Pushshift — informal
4. Tagarela (podcasts transcritos) — fala real
5. Carolina Corpus subset "virtual" — midias sociais

### Mid-training (mistura progressiva de informal)
6. Telegram publico brasileiro
7. Forums (Hardmob, Adrenaline)
8. YouTube transcritos (Whisper) de canais informais

### Fine-tuning regional (pernambucano/nordestino)
9. NURC Digital Recife (fala culta urbana recifense)
10. CORAA subset NURC-RE
11. Cordel (dominio publico)
12. Letras: frevo, maracatu, manguebeat, forro
13. Literatura nordestina (dominio publico)
14. Transcrever podcasts/canais pernambucanos com Whisper
15. (Opcional) Mensagens proprias do WhatsApp (anonimizadas)

---

## Referencia Mestra
- github.com/ajdavidl/Portuguese-NLP — lista curada de todos os recursos
- huggingface.co/collections/ai-eldorado/brazilian-portuguese-datasets
