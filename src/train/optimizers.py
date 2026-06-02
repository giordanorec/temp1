"""Advanced optimizers for FarolLM.

Implements:
- Muon: Newton-Schulz orthogonalized momentum (2025, Keller Jordan)
  ~35% faster training than AdamW at SLM scale.
- Cautious AdamW (C-AdamW): one-line improvement over AdamW (2024)
  Only applies updates aligned with current gradient direction.

References:
- Muon: https://github.com/KellerJordan/Muon
- C-AdamW: https://arxiv.org/abs/2411.16085
"""

import torch
from torch.optim import AdamW


def newton_schulz_orthogonalize(G: torch.Tensor, steps: int = 5) -> torch.Tensor:
    """Project gradient matrix onto nearest orthogonal matrix via Newton-Schulz iteration."""
    a, b, c = (3.4445, -4.7750, 2.0315)

    # Normalize spectral norm to ~1
    G = G / (G.norm() + 1e-7)
    X = G

    for _ in range(steps):
        A = X @ X.T
        X = a * X + b * (A @ X) + c * (A @ (A @ X))

    return X


class Muon(torch.optim.Optimizer):
    """Muon optimizer — orthogonalized momentum for 2D weight matrices.

    Only applies to 2D parameters (weight matrices in attention/MLP).
    Embeddings, norms, biases should use a separate AdamW optimizer.
    """

    def __init__(self, params, lr: float = 0.02, momentum: float = 0.95, ns_steps: int = 5):
        defaults = dict(lr=lr, momentum=momentum, ns_steps=ns_steps)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]
            momentum = group["momentum"]
            ns_steps = group["ns_steps"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                g = p.grad
                state = self.state[p]

                if len(state) == 0:
                    state["momentum_buffer"] = torch.zeros_like(g)

                buf = state["momentum_buffer"]
                buf.mul_(momentum).add_(g)

                if g.ndim == 2:
                    update = newton_schulz_orthogonalize(buf.float(), ns_steps).type_as(p)
                else:
                    update = buf

                p.add_(update, alpha=-lr)

        return loss


def create_optimizer(model, config: dict) -> torch.optim.Optimizer:
    """Create optimizer with Muon for 2D weights and AdamW for the rest.

    This is the recommended setup: Muon handles the bulk of parameters
    (attention projections, MLP layers) while AdamW handles embeddings,
    norms, and biases where orthogonalization doesn't apply.
    """
    train_cfg = config["training"]
    optimizer_type = train_cfg.get("optimizer", "adamw")

    if optimizer_type == "muon":
        muon_params = []
        adamw_params = []

        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
            if param.ndim == 2 and "tok_emb" not in name and "lm_head" not in name:
                muon_params.append(param)
            else:
                adamw_params.append(param)

        muon_lr = train_cfg.get("muon_lr", 0.02)
        adamw_lr = train_cfg["learning_rate"]

        optimizer = torch.optim.Optimizer.__new__(torch.optim.Optimizer)
        optimizer.__init__(
            [{"params": []}],
            defaults={},
        )

        muon_opt = Muon(muon_params, lr=muon_lr, momentum=0.95)
        adamw_opt = AdamW(
            adamw_params,
            lr=adamw_lr,
            weight_decay=train_cfg.get("weight_decay", 0.1),
            betas=(0.9, 0.95),
        )

        return _DualOptimizer(muon_opt, adamw_opt)

    elif optimizer_type == "cautious_adamw":
        return CautiousAdamW(
            model.parameters(),
            lr=train_cfg["learning_rate"],
            weight_decay=train_cfg.get("weight_decay", 0.1),
            betas=(0.9, 0.95),
        )

    else:
        return AdamW(
            model.parameters(),
            lr=train_cfg["learning_rate"],
            weight_decay=train_cfg.get("weight_decay", 0.1),
            betas=(0.9, 0.95),
        )


class CautiousAdamW(AdamW):
    """AdamW with cautious update masking (C-AdamW).

    Only applies the update step when it aligns with the current
    gradient direction (positive dot product). Masks out components
    where the momentum-based update disagrees with the raw gradient.

    ~1.47x more sample-efficient than standard AdamW.
    """

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue

                grad = p.grad
                state = self.state[p]

                if len(state) == 0:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(p)
                    state["exp_avg_sq"] = torch.zeros_like(p)

                exp_avg, exp_avg_sq = state["exp_avg"], state["exp_avg_sq"]
                beta1, beta2 = group["betas"]
                state["step"] += 1

                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                bias_correction1 = 1 - beta1 ** state["step"]
                bias_correction2 = 1 - beta2 ** state["step"]

                corrected_avg = exp_avg / bias_correction1
                corrected_sq = exp_avg_sq / bias_correction2

                denom = corrected_sq.sqrt().add_(group.get("eps", 1e-8))
                update = corrected_avg / denom

                # Cautious masking: only update where aligned with gradient
                mask = (update * grad > 0).float()
                update = update * mask

                if group["weight_decay"] != 0:
                    p.add_(p, alpha=-group["lr"] * group["weight_decay"])

                p.add_(update, alpha=-group["lr"])

        return loss


class _DualOptimizer:
    """Wraps two optimizers (Muon + AdamW) as one interface."""

    def __init__(self, opt1, opt2):
        self.opt1 = opt1
        self.opt2 = opt2

    def step(self, closure=None):
        self.opt1.step(closure)
        self.opt2.step(closure)

    def zero_grad(self, set_to_none=True):
        self.opt1.zero_grad(set_to_none)
        self.opt2.zero_grad(set_to_none)

    @property
    def param_groups(self):
        return self.opt1.param_groups + self.opt2.param_groups

    def state_dict(self):
        return {"opt1": self.opt1.state_dict(), "opt2": self.opt2.state_dict()}

    def load_state_dict(self, state_dict):
        self.opt1.load_state_dict(state_dict["opt1"])
        self.opt2.load_state_dict(state_dict["opt2"])
