"""BatchNorm implementation task."""

TASK = {
    "category": "基础层",
    "title": "Implement BatchNorm",
    "difficulty": "Medium",
    "function_name": "my_batch_norm",
    "hint": "Normalize each feature across the batch (dim=0): (x - mean) / sqrt(var + eps) * gamma + beta. Use unbiased=False for variance.",
    "tests": [
        {
            "name": "Basic behavior — zero mean per feature",
            "code": """
import torch
x = torch.randn(8, 4)
gamma = torch.ones(4)
beta = torch.zeros(4)
out = {fn}(x, gamma, beta)
assert out.shape == x.shape, f'Shape mismatch: {out.shape}'
col_means = out.mean(dim=0)
assert torch.allclose(col_means, torch.zeros(4), atol=1e-5), f'Column means not zero: {col_means}'
""",
        },
        {
            "name": "Numerical correctness",
            "code": """
import torch
x = torch.randn(16, 8)
gamma = torch.randn(8)
beta = torch.randn(8)
out = {fn}(x, gamma, beta)
mean = x.mean(dim=0)
var = x.var(dim=0, unbiased=False)
ref = gamma * (x - mean) / torch.sqrt(var + 1e-5) + beta
assert torch.allclose(out, ref, atol=1e-4), 'Value mismatch'
""",
        },
        {
            "name": "Gradient flow",
            "code": """
import torch
x = torch.randn(4, 8, requires_grad=True)
gamma = torch.ones(8, requires_grad=True)
beta = torch.zeros(8, requires_grad=True)
out = {fn}(x, gamma, beta)
out.sum().backward()
assert x.grad is not None, 'x.grad is None'
assert gamma.grad is not None, 'gamma.grad is None'
""",
        },
    ],
}
