"""Greedy decoding task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Greedy Search Decoding",
    "difficulty": "Easy",
    "function_name": "greedy_decode",
    "hint": "Greedy decoding picks the token with the largest logit at each position. This is just argmax over the vocabulary dimension.",
    "tests": [
        {
            "name": "1-D logits",
            "code": """
import torch
logits = torch.tensor([0.1, 2.5, -1.0, 2.4])
out = {fn}(logits)
assert out.shape == (), f'Expected scalar output for 1-D logits, got {out.shape}'
assert out.item() == 1, f'Expected token 1, got {out.item()}'
""",
        },
        {
            "name": "Batch decoding",
            "code": """
import torch
logits = torch.tensor([
    [0.0, 3.0, 1.0],
    [2.0, 1.0, 2.5],
    [-5.0, -1.0, -2.0],
])
out = {fn}(logits)
expected = torch.tensor([1, 2, 1])
assert torch.equal(out, expected), f'Wrong greedy predictions: {out} vs {expected}'
""",
        },
        {
            "name": "Matches torch.argmax",
            "code": """
import torch
torch.manual_seed(0)
logits = torch.randn(4, 7, 13)
out = {fn}(logits)
expected = logits.argmax(dim=-1)
assert torch.equal(out, expected), 'greedy_decode should match argmax(dim=-1)'
""",
        },
    ],
}
