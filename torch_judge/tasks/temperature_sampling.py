"""Temperature sampling task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Temperature Sampling",
    "difficulty": "Medium",
    "function_name": "temperature_sample",
    "hint": (
        "Scale logits by dividing by temperature before softmax. Lower temperature makes "
        "the distribution sharper; higher temperature makes it flatter. Then sample with "
        "torch.multinomial."
    ),
    "tests": [
        {
            "name": "Returns one token per row",
            "code": """
import torch
torch.manual_seed(0)
logits = torch.tensor([[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]])
out = {fn}(logits, temperature=0.7)
assert out.shape == (2,), f'Expected one sample per row, got {out.shape}'
assert out.dtype in (torch.int32, torch.int64), f'Output should be integer typed, got {out.dtype}'
""",
        },
        {
            "name": "Matches reference sampling with fixed seed",
            "code": """
import torch
logits = torch.tensor([[2.0, 0.5, -1.0], [0.1, 0.2, 0.3]], dtype=torch.float32)
torch.manual_seed(42)
out = {fn}(logits, temperature=0.8)
torch.manual_seed(42)
probs = torch.softmax(logits / 0.8, dim=-1)
expected = torch.multinomial(probs, num_samples=1).squeeze(-1)
assert torch.equal(out, expected), f'Wrong sampled tokens: {out} vs {expected}'
""",
        },
        {
            "name": "Very low temperature behaves greedily",
            "code": """
import torch
logits = torch.tensor([0.0, 5.0, 1.0], dtype=torch.float32)
torch.manual_seed(0)
out = {fn}(logits, temperature=1e-4)
assert out.item() == 1, f'Low temperature should almost always pick argmax, got {out.item()}'
""",
        },
    ],
}
