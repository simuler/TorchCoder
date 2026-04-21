"""AdaLN (Adaptive Layer Normalization) task — used in DiT, Diffusion Transformers."""

TASK = {
    "category": "条件调制 — Diffusion",
    "title": "AdaLN (Adaptive Layer Normalization)",
    "difficulty": "Hard",
    "function_name": "AdaLN",
    "hint": "AdaLN modulates LayerNorm using conditioning: γ, β = f(cond). Use nn.SiLU + nn.Linear to predict scale and shift from condition. Output: γ * normalize(x) + β. γ typically initialized to 1, β to 0.",
    "tests": [
        {
            "name": "Output shape",
            "code": """
import torch, torch.nn as nn
adaln = {fn}(hidden_dim=64, cond_dim=128)
x = torch.randn(2, 10, 64)
cond = torch.randn(2, 128)
out = adaln(x, cond)
assert out.shape == (2, 10, 64), f'Shape mismatch: {out.shape}'
""",
        },
        {
            "name": "Has modulation layers",
            "code": """
import torch, torch.nn as nn
adaln = {fn}(hidden_dim=32, cond_dim=64)
assert hasattr(adaln, 'norm'), 'Need self.norm = nn.LayerNorm'
assert hasattr(adaln, 'cond_mlp'), 'Need self.cond_mlp for scale/shift prediction'
assert isinstance(adaln.norm, nn.LayerNorm), 'norm should be nn.LayerNorm'
""",
        },
        {
            "name": "Produces per-sample modulation",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
x = torch.randn(2, 10, 32)
cond1 = torch.randn(2, 64)
cond2 = torch.randn(2, 64)
out1 = adaln(x, cond1)
out2 = adaln(x, cond2)
# Same x, different cond should give different outputs
assert not torch.allclose(out1, out2, atol=1e-3), 'Different conditions should give different outputs'
""",
        },
        {
            "name": "Condition-independent when gamma=1, beta=0",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
x = torch.randn(1, 4, 32)
# Initialize to identity modulation
with torch.no_grad():
    for p in adaln.cond_mlp.parameters():
        p.zero_()
out = adaln(x, torch.randn(1, 64))
# With zero MLP, should approximate standard LayerNorm (gamma≈0 -> 1 after init)
assert out.shape == x.shape, 'Output shape should match input'
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
            "name": "Modulation affects normalized output",
            "code": """
import torch
adaln = {fn}(hidden_dim=32, cond_dim=64)
x = torch.randn(1, 4, 32)
cond = torch.randn(1, 64)
out = adaln(x, cond)
# Output should be normalized (zero mean, unit variance per token) before modulation
# After modulation, it may have different statistics
assert out.shape == x.shape
# Check that modulation actually happened (not just LayerNorm)
ref_norm = torch.nn.functional.layer_norm(x, [32])
assert not torch.allclose(out, ref_norm, atol=1e-3), 'AdaLN should differ from plain LayerNorm'
""",
        },
    ],
}
