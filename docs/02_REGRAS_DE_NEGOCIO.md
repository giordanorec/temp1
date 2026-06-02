# 02 — Regras do Projeto

## Principios

- Todo codigo e reproduzivel: qualquer pessoa com o repo re-treina o modelo
- Cada decisao e documentada em DECISOES.md antes de ser implementada
- Dados de treinamento sao publicos e licenciados de forma aberta
- Nenhuma dependencia proprietaria ou closed-source

## Invariantes (obrigatorias)

- **I1.** Tokenizador e treinado do zero (nao reutilizar tokenizador existente)
- **I2.** Arquitetura e implementada do zero (nao carregar pesos pre-treinados)
- **I3.** Todos os hiperparametros sao versionados em YAML sob `configs/`
- **I4.** Checkpoints intermediarios sao salvos a cada N steps (configuravel)
- **I5.** Loss e metricas sao logados em W&B a cada step

## Casos de borda para QA

1. Tokenizador recebe texto so em portugues — deve funcionar
2. Tokenizador recebe texto so em ingles — deve funcionar
3. Tokenizador recebe codigo Python — deve funcionar
4. Tokenizador recebe emoji/unicode exotico — nao deve crashar
5. Modelo recebe contexto maior que max_seq_len — deve truncar com aviso
6. Treino interrompido e retomado de checkpoint — loss deve continuar de onde parou
