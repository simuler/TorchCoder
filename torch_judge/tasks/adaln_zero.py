"""AdaLN-Zero task — zero-initialized AdaLN for stable Diffusion Transformer training."""

TASK = {
    "category": "条件调制 — Diffusion",
    "title": "AdaLN-Zero",
    "difficulty": "Hard",
    "function_name": "AdaLNZero",
    "hint": "AdaLN-Zero initializes the last linear layer to zero so γ=β=0 initially. Also includes a gate for residual. Output: gate * (γ * ln(x) + β). Gate initialized to 0, allowing the model to gradually increase modulation strength.",
    "tests": [
        {
            "name": "Output shape",
            "code": """
import torch
adaln = {fn}(hidden_dim=64, cond_dim=128)
x = torch.randn(2, 10, 64)
cond = torch.randn(2, 128)
out = adaln(x, cond)
assert out.shape == (2, 10, 64), f'Shape mismatch: {out.shape}'
""",
        },
        {
            "name": "Zero initialization",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
# The final projection should be zero-initialized
# This ensures γ=0, β=0, gate=0 at initialization
x = torch.randn(1, 4, 32)
cond = torch.randn(1, 64)
out = adaln(x, cond)
# With zero init, output should be close to zero
assert torch.allclose(out, torch.zeros_like(out), atol=1e-5), f'Zero init should give zero output, got max {out.abs().max()}'
""",
        },
        {
            "name": "Has gate parameter",
            "code": """
import torch, torch.nn as nn
adaln = {fn}(hidden_dim=32, cond_dim=64)
assert hasattr(adaln, 'gate_proj'), 'Need self.gate_proj for residual gate'
""",
        },
        {
            "name": "Gate allows gradual learning",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
x = torch.randn(1, 4, 32)
cond = torch.randn(1, 64)
# Set non-zero modulation but zero gate
with torch.no_grad():
    # Manually set gamma, beta but keep gate at zero
    adaln.gate_proj.weight.zero_()
    adaln.gate_proj.bias.zero_()
out = adaln(x, cond)
assert torch.allclose(out, torch.zeros_like(out), atol=1e-5), 'Zero gate should give zero output'
""",
        },
        {
            "name": "Gradient flow",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
x = torch.randn(1, 4, 32, requires_grad=True)
cond = torch.randn(1, 64, requires_grad=True)
out = adaln(x, cond)
out.sum().backward()
assert x.grad is not None, 'x.grad is None'
assert cond.grad is not None, 'cond.grad is None'
""",
        },
        {
            "name": "Non-zero after training simulation",
            "code": """
import torch, torch.optim as optim
adaln = {fn}(hidden_dim=32, cond_dim=64)
optimizer = optim.SGD(adaln.parameters(), lr=0.1)
x = torch.randn(1, 4, 32)
cond = torch.randn(1, 64)
target = torch.randn(1, 4, 32)
# Simulate a few training steps
for _ in range(5):
    out = adaln(x, cond)
    loss = (out - target).pow(2).sum()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
out_after = adaln(x, cond)
assert not torch.allclose(out_after, torch.zeros_like(out_after), atol=1e-3), 'After training, output should be non-zero'
""",
        },
    ],
}
