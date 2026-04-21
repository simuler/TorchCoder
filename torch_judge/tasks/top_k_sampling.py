"""Top-k sampling task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Top-k Sampling",
    "difficulty": "Medium",
    "function_name": "top_k_sample",
    "hint": (
        "Find the top-k logits, mask all other logits to -inf, apply softmax over the "
        "remaining tokens, then sample from that truncated distribution."
    ),
    "tests": [
        {
            "name": "Samples only from top-k tokens",
            "code": """
import torch
torch.manual_seed(0)
logits = torch.tensor([[5.0, 4.0, 1.0, -2.0]])
out = {fn}(logits, k=2)
assert out.item() in (0, 1), f'Sampled token must be in the top-2 set, got {out.item()}'
""",
        },
        {
            "name": "Matches reference sampling with fixed seed",
            "code": """
import torch
logits = torch.tensor([[2.0, 1.5, 0.1, -1.0], [0.2, 3.0, 2.5, 0.0]], dtype=torch.float32)
torch.manual_seed(123)
out = {fn}(logits, k=2)

torch.manual_seed(123)
top_values, top_indices = torch.topk(logits, k=2, dim=-1)
masked = torch.full_like(logits, float('-inf'))
masked.scatter_(-1, top_indices, top_values)
probs = torch.softmax(masked, dim=-1)
expected = torch.multinomial(probs, num_samples=1).squeeze(-1)
assert torch.equal(out, expected), f'Sampled tokens mismatch: {out} vs {expected}'
""",
        },
        {
            "name": "k=1 equals greedy",
            "code": """
import torch
logits = torch.tensor([[0.2, 1.7, 0.8], [3.0, 2.0, 1.0]])
out = {fn}(logits, k=1)
expected = logits.argmax(dim=-1)
assert torch.equal(out, expected), f'k=1 should be greedy: {out} vs {expected}'
""",
        },
    ],
}
