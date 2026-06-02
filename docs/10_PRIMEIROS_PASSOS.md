# 10 — Primeiros passos (Fase 0 — Fundacao)

Roteiro executado pelo Arquiteto ou pelo usuario no Mac Mini M4.

## Passo 1. Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

## Passo 2. Dependencias iniciais

```bash
pip install torch torchvision torchaudio  # PyTorch com MPS
pip install litgpt
pip install tokenizers sentencepiece
pip install transformers datasets
pip install wandb tensorboard
pip install trl peft
pip install lm-eval  # EleutherAI evaluation harness
pip install ruff pytest pytest-cov
```

## Passo 3. Reproduzir nanochat (Fase 0)

```bash
git clone https://github.com/karpathy/nanochat.git /tmp/nanochat
cd /tmp/nanochat
# Seguir README do nanochat para treinar GPT-2 124M
# Documentar licoes em docs/DECISOES.md
```

## Passo 4. Treinar tokenizador (Fase 1)

```bash
# Baixar amostras de dados
python src/data/download.py --dataset fineweb2 --lang pt,en --size 1GB
python src/data/download.py --dataset culturax --lang pt --size 500MB

# Treinar BPE
python src/tokenizer/train_bpe.py --vocab-size 32768 --data data/raw/
```

## Passo 5. Definir e treinar modelo (Fases 2-3)

```bash
# Tokenizar corpus
python src/data/tokenize_corpus.py --tokenizer tokenizer/ --output data/tokenized/

# Treinar
python src/train/pretrain.py --config configs/farol-300m.yaml
```

## Passo 6. Spawn dos agentes (quando em modo multi-agente)

```bash
for agente in pipeline-dev devops-installer qa-tester docs-writer; do
    scripts/spawn.sh "$agente"
done
```

## Passo 7. Abrir dashboard

```bash
scripts/open_dashboard.sh
```
