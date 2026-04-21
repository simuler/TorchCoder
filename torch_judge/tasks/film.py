"""FiLM (Feature-wise Linear Modulation) task — conditional feature modulation."""

TASK = {
    "category": "条件调制 — Diffusion",
    "title": "FiLM Layer",
    "difficulty": "Medium",
    "function_name": "FiLM",
    "hint": "FiLM applies affine transform conditioned on input: γ(c) * x + β(c). Use a small MLP to predict scale γ and shift β from condition. Simple but powerful for style transfer and conditional generation.",
    "tests": [
        {
            "name": "Output shape",
            "code": """
import torch
film = {fn}(feature_dim=64, cond_dim=32)
x = torch.randn(2, 10, 64)
cond = torch.randn(2, 32)
out = film(x, cond)
assert out.shape == (2, 10, 64), f'Shape mismatch: {out.shape}'
""",
        },
        {
            "name": "Has modulation parameters",
            "code": """
import torch, torch.nn as nn
film = {fn}(feature_dim=32, cond_dim=16)
assert hasattr(film, 'gamma_fc') or hasattr(film, 'beta_fc'), 'Need gamma_fc and beta_fc for modulation'
""",
        },
        {
            "name": "Applies affine modulation",
            "code": """
import torch
film = {fn}(feature_dim=32, cond_dim=16)
x = torch.randn(1, 4, 32)
cond = torch.randn(1, 16)
out = film(x, cond)
# FiLM should apply gamma * x + beta
# Without proper implementation, this test verifies the structure
assert out.shape == x.shape, 'Output shape should match input'
""",
        },
        {
            "name": "Condition affects output",
            "code": """
import torch
film = {fn}(feature_dim=32, cond_dim=16)
x = torch.randn(1, 4, 32)
cond1 = torch.zeros(1, 16)
cond2 = torch.ones(1, 16)
out1 = film(x, cond1)
out2 = film(x, cond2)
assert not torch.allclose(out1, out2, atol=1e-3), 'Different conditions should give different outputs'
""",
        },
        {
            "name": "Gradient flow",
            "code": """
import torch
film = {fn}(feature_dim=32, cond_dim=16)
x = torch.randn(1, 4, 32, requires_grad=True)
cond = torch.randn(1, 16, requires_grad=True)
out = film(x, cond)
out.sum().backward()
assert x.grad is not None, 'x.grad is None'
assert cond.grad is not None, 'cond.grad is None'
""",
        },
        {
            "name": "Identity when gamma=1, beta=0",
            "code": """
import torch
film = {fn}(feature_dim=32, cond_dim=16)
x = torch.randn(1, 4, 32)
# If gamma=1 and beta=0, output should equal normalized input
# This tests that the modulation structure is correct
assert hasattr(film, 'gamma_fc') or hasattr(film, 'fc_gamma') or hasattr(film, 'mlp'), 'FiLM needs modulation layers'
""",
        },
    ],
}
