"""Top-p (nucleus) sampling task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Top-p Sampling",
    "difficulty": "Hard",
    "function_name": "top_p_sample",
    "hint": (
        "Sort tokens by probability descending, take the smallest prefix whose cumulative "
        "probability reaches p, mask the rest, renormalize, and sample from that nucleus."
    ),
    "tests": [
        {
            "name": "Samples only from nucleus set",
            "code": """
import torch
torch.manual_seed(0)
logits = torch.tensor([[4.0, 3.5, 1.0, -2.0]], dtype=torch.float32)
out = {fn}(logits, p=0.8)
assert out.item() in (0, 1), f'Sampled token must come from the nucleus set, got {out.item()}'
""",
        },
        {
            "name": "Matches reference sampling with fixed seed",
            "code": """
import torch

def reference_top_p(logits: torch.Tensor, p: float) -> torch.Tensor:
    if logits.dim() == 1:
        logits = logits.unsqueeze(0)
    probs = torch.softmax(logits, dim=-1)
    outputs = []
    for row in probs:
        sorted_probs, sorted_indices = torch.sort(row, descending=True)
        cumulative = sorted_probs.cumsum(dim=0)
        keep = cumulative <= p
        keep[0] = True
        first_exceed = torch.nonzero(cumulative > p, as_tuple=False)
        if first_exceed.numel() > 0:
            keep[first_exceed[0, 0]] = True
        filtered = torch.zeros_like(row)
        filtered[sorted_indices[keep]] = row[sorted_indices[keep]]
        filtered = filtered / filtered.sum()
        token = torch.multinomial(filtered, num_samples=1)
        outputs.append(token)
    return torch.stack(outputs).squeeze(-1)

logits = torch.tensor([[2.5, 2.0, 1.0, -0.5], [0.1, 0.2, 3.0, 2.9]], dtype=torch.float32)
torch.manual_seed(9)
out = {fn}(logits, p=0.75)
torch.manual_seed(9)
expected = reference_top_p(logits, p=0.75)
assert torch.equal(out, expected), f'Sampled tokens mismatch: {out} vs {expected}'
""",
        },
        {
            "name": "Small p still keeps at least one token",
            "code": """
import torch
logits = torch.tensor([1.0, 5.0, 0.5], dtype=torch.float32)
torch.manual_seed(0)
out = {fn}(logits, p=0.01)
assert out.item() == 1, f'At least the top token must remain available, got {out.item()}'
""",
        },
    ],
}
