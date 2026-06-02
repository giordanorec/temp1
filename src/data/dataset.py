"""Memory-mapped dataset for pre-training.

Reads tokenized data from a numpy memmap file. Each sample is a
contiguous chunk of `seq_len + 1` tokens (input + target shifted by 1).
"""

import os

import numpy as np
import torch
from torch.utils.data import Dataset


class MemmapDataset(Dataset):
    def __init__(self, path: str, seq_len: int, dtype=np.uint16):
        self.seq_len = seq_len
        file_size = os.path.getsize(path)
        self.data = np.memmap(path, dtype=dtype, mode="r")
        self.num_tokens = len(self.data)
        self.num_samples = (self.num_tokens - 1) // seq_len

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        start = idx * self.seq_len
        end = start + self.seq_len + 1
        chunk = torch.from_numpy(self.data[start:end].astype(np.int64))
        x = chunk[:-1]
        y = chunk[1:]
        return x, y


class RandomTokenDataset(Dataset):
    """Synthetic dataset for smoke tests — generates random token sequences."""

    def __init__(self, num_samples: int, seq_len: int, vocab_size: int):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.vocab_size = vocab_size

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        tokens = torch.randint(0, self.vocab_size, (self.seq_len + 1,))
        return tokens[:-1], tokens[1:]
