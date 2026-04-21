"""PPO clipped policy loss task."""

TASK = {
    "category": "RLHF",
    "title": "PPO Clipped Policy Loss",
    "difficulty": "Hard",
    "function_name": "ppo_clipped_loss",
    "hint": (
        "Compute ratio = exp(new_log_probs - old_log_probs). Then form the unclipped "
        "objective ratio * advantages and the clipped one clamp(ratio, 1-eps, 1+eps) "
        "* advantages. PPO uses the minimum of the two, and the loss is the negative mean."
    ),
    "tests": [
        {
            "name": "Matches reference formula",
            "code": """
import torch
old_log_probs = torch.log(torch.tensor([0.2, 0.5, 0.3], dtype=torch.float32))
new_log_probs = torch.log(torch.tensor([0.25, 0.45, 0.30], dtype=torch.float32))
advantages = torch.tensor([1.0, -0.5, 2.0], dtype=torch.float32)
loss = {fn}(old_log_probs, new_log_probs, advantages, clip_eps=0.2)
ratio = torch.exp(new_log_probs - old_log_probs)
unclipped = ratio * advantages
clipped = torch.clamp(ratio, 0.8, 1.2) * advantages
expected = -torch.minimum(unclipped, clipped).mean()
assert torch.allclose(loss, expected, atol=1e-6), f'Loss mismatch: {loss} vs {expected}'
""",
        },
        {
            "name": "Positive advantages are clipped when ratio is too large",
            "code": """
import torch
old_log_probs = torch.zeros(3)
new_log_probs = torch.log(torch.tensor([2.0, 2.5, 3.0]))
advantages = torch.ones(3)
loss = {fn}(old_log_probs, new_log_probs, advantages, clip_eps=0.1)
expected = -torch.tensor(1.1)
assert torch.allclose(loss, expected, atol=1e-6), f'Expected clipped objective mean -1.1, got {loss}'
""",
        },
        {
            "name": "Negative advantages use clipped lower ratio",
            "code": """
import torch
old_log_probs = torch.zeros(2)
new_log_probs = torch.log(torch.tensor([0.2, 0.5]))
advantages = torch.tensor([-1.0, -2.0])
loss = {fn}(old_log_probs, new_log_probs, advantages, clip_eps=0.1)
ratio = torch.exp(new_log_probs - old_log_probs)
unclipped = ratio * advantages
clipped = torch.clamp(ratio, 0.9, 1.1) * advantages
expected = -torch.minimum(unclipped, clipped).mean()
assert torch.allclose(loss, expected, atol=1e-6), 'Negative-advantage clipping mismatch'
""",
        },
    ],
}
