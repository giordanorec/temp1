"""End-to-end test: train tokenizer -> tokenize data -> train model -> generate."""

import os
import tempfile

import numpy as np
import torch

from src.model.farol import FarolConfig, FarolLM
from src.tokenizer.train_bpe import train_from_iterator
from src.data.dataset import MemmapDataset


CORPUS = [
    "O FarolLM e um modelo de linguagem multilingual treinado do zero.",
    "The Transformer architecture uses self-attention mechanisms.",
    "def train(model, data):\n    for batch in data:\n        loss = model(batch)\n        loss.backward()",
    "Recife e a capital de Pernambuco, no nordeste do Brasil.",
    "Language models predict the next token in a sequence.",
    "import torch\nimport torch.nn as nn\nimport torch.nn.functional as F",
    "A pesquisa em inteligencia artificial avanca rapidamente.",
    "Gradient descent minimizes the loss function iteratively.",
    "O tokenizador BPE divide texto em subpalavras frequentes.",
    "Neural networks learn hierarchical representations of data.",
] * 100


def test_full_pipeline():
    """Train tokenizer, tokenize corpus, train model, generate text."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Train tokenizer
        tokenizer = train_from_iterator(
            iterator=CORPUS,
            output_dir=os.path.join(tmpdir, "tokenizer"),
            vocab_size=512,
        )
        vocab_size = tokenizer.get_vocab_size()
        assert vocab_size > 0

        # 2. Tokenize corpus into memmap
        all_ids = []
        bos = tokenizer.token_to_id("<|begin_of_text|>")
        eos = tokenizer.token_to_id("<|end_of_text|>")
        for text in CORPUS:
            ids = tokenizer.encode(text).ids
            if bos is not None:
                all_ids.append(bos)
            all_ids.extend(ids)
            if eos is not None:
                all_ids.append(eos)

        bin_path = os.path.join(tmpdir, "train.bin")
        arr = np.array(all_ids, dtype=np.uint16)
        arr.tofile(bin_path)
        assert os.path.exists(bin_path)

        # 3. Create dataset
        seq_len = 64
        dataset = MemmapDataset(bin_path, seq_len=seq_len)
        assert len(dataset) > 0
        x, y = dataset[0]
        assert x.shape == (seq_len,)

        # 4. Create and train tiny model
        config = FarolConfig(
            vocab_size=vocab_size,
            hidden_size=64,
            intermediate_size=176,
            num_layers=2,
            num_heads=4,
            num_kv_heads=2,
            max_seq_len=seq_len,
        )
        model = FarolLM(config)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

        model.train()
        losses = []
        loader = torch.utils.data.DataLoader(dataset, batch_size=4, shuffle=True)
        for i, (bx, by) in enumerate(loader):
            if i >= 10:
                break
            _, loss = model(bx, by)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            losses.append(loss.item())

        assert len(losses) == 10
        assert all(l > 0 for l in losses)

        # 5. Generate
        model.eval()
        prompt_ids = tokenizer.encode("O FarolLM").ids[:8]
        prompt = torch.tensor([prompt_ids], dtype=torch.long)
        output = model.generate(prompt, max_new_tokens=20, temperature=1.0, top_k=50)
        assert output.shape[1] == len(prompt_ids) + 20

        generated_ids = output[0].tolist()
        text = tokenizer.decode(generated_ids)
        assert len(text) > 0
        print(f"\n  Generated: {text[:100]}")
