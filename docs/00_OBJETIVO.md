# 00 — Objetivo

## O que se quer alcancar

Criar uma LLM/SLM multilingual do zero — tokenizador, arquitetura,
pre-treinamento, alinhamento — documentando cada etapa para entendimento
profundo de todo o pipeline. O modelo final sera publicado com codigo,
dados de treinamento e pesos abertos.

## Publico-alvo

- O proprio autor (aprendizado profundo)
- Comunidade academica (pesquisa reproduzivel)
- UFPE e colaboradores em Oxford, Stanford, Sorbonne

## Escopo dentro

- Treinar tokenizador BPE multilingual proprio
- Definir arquitetura Transformer (Llama-style) de 300M-500M params
- Pre-treinar em dados multilinguais abertos (FineWeb-2, CulturaX)
- Alinhar via SFT + DPO
- Documentar cada decisao e publicar tudo open source
- Rodar localmente no Mac Mini M4 64GB (fase inicial)
- Escalar para cloud GPUs (fase futura)

## Escopo fora

- Competir com modelos comerciais (GPT-4, Claude, etc)
- Treinamento multimodal (imagem, audio) — pode ser Fase futura
- Deploy em producao para usuarios finais
- Fine-tuning de modelos existentes (o ponto e treinar do zero)

## Criterio de sucesso

1. Modelo pre-treinado gera texto coerente em portugues e ingles
2. Pipeline completo reproduzivel: qualquer pessoa com o repo consegue
   re-treinar o modelo seguindo os docs
3. Cada etapa documentada com decisoes, alternativas e raciocinio
4. Modelo publicado no Hugging Face com model card completo
5. Pelo menos um benchmark padrao avaliado (ex: MMLU, HellaSwag)
