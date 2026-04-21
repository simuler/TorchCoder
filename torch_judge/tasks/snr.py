"""SNR (Sigmoid Noise Schedule) task — noise scheduling for diffusion models."""

TASK = {
    "category": "扩散模型训练",
    "title": "Sigmoid Noise Schedule",
    "difficulty": "Medium",
    "function_name": "sigmoid_schedule",
    "hint": "Sigmoid schedule creates smooth transition between signal and noise. σ(t) = exp(σ_min + (σ_max - σ_min) * sigmoid(γ * (t - 0.5))). Or for β schedule: β(t) = sigmoid(...) mapped to [β_start, β_end].",
    "tests": [
        {
            "name": "Output shape",
            "code": """
import torch
t = torch.linspace(0, 1, 100)
betas = {fn}(t, beta_start=0.0001, beta_end=0.02)
assert betas.shape == t.shape, f'Shape mismatch: {betas.shape}'
""",
        },
        {
            "name": "Bounds at endpoints",
            "code": """
import torch
t = torch.tensor([0.0, 1.0])
betas = {fn}(t, beta_start=0.0001, beta_end=0.02)
assert betas[0] < 0.001, f'beta at t=0 should be near beta_start, got {betas[0]}'
assert betas[1] > 0.015, f'beta at t=1 should be near beta_end, got {betas[1]}'
""",
        },
        {
            "name": "Monotonic increase",
            "code": """
import torch
t = torch.linspace(0, 1, 100)
betas = {fn}(t, beta_start=0.0001, beta_end=0.02)
diffs = betas[1:] - betas[:-1]
assert (diffs >= -1e-6).all(), 'Betas should be monotonically non-decreasing'
""",
        },
        {
            "name": "Smooth transition",
            "code": """
import torch
t = torch.linspace(0, 1, 100)
betas = {fn}(t, beta_start=0.0001, beta_end=0.02)
# Sigmoid should give smooth S-curve, not linear
mid = betas[49]  # t=0.5
linear_mid = 0.5 * (0.0001 + 0.02)
# Sigmoid mid should be close to linear mid for standard sigmoid
assert abs(mid - linear_mid) < 0.005, f'Mid point should be smooth transition'
""",
        },
        {
            "name": "Different parameters give different schedules",
            "code": """
import torch
t = torch.linspace(0, 1, 50)
betas1 = {fn}(t, beta_start=0.0001, beta_end=0.02)
betas2 = {fn}(t, beta_start=0.0001, beta_end=0.05)
assert not torch.allclose(betas1, betas2, atol=1e-3), 'Different beta_end should give different schedule'
""",
        },
    ],
}
