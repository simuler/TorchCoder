"""Beam search decoding task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Beam Search Decoding",
    "difficulty": "Hard",
    "function_name": "beam_search_decode",
    "hint": (
        "Keep a list of the top beam_width partial sequences. At each timestep, expand "
        "every beam with every token, add the current log-probability to the running "
        "score, then keep only the best beam_width candidates."
    ),
    "tests": [
        {
            "name": "Output types",
            "code": """
import torch
log_probs = torch.log(torch.tensor([
    [0.6, 0.3, 0.1],
    [0.2, 0.5, 0.3],
], dtype=torch.float32))
sequence, score = {fn}(log_probs, beam_width=2)
assert isinstance(sequence, torch.Tensor), f'Sequence should be a tensor, got {type(sequence)}'
assert sequence.shape == (2,), f'Sequence shape mismatch: {sequence.shape}'
assert sequence.dtype in (torch.int32, torch.int64), f'Sequence should be integer typed, got {sequence.dtype}'
assert isinstance(score, float), f'Score should be a Python float, got {type(score)}'
""",
        },
        {
            "name": "Matches exhaustive search on tiny example",
            "code": """
import itertools
import torch
log_probs = torch.log(torch.tensor([
    [0.50, 0.30, 0.20],
    [0.10, 0.70, 0.20],
    [0.60, 0.25, 0.15],
], dtype=torch.float32))
sequence, score = {fn}(log_probs, beam_width=2)
best_seq = None
best_score = None
for seq in itertools.product(range(3), repeat=3):
    seq_score = sum(log_probs[t, token].item() for t, token in enumerate(seq))
    if best_score is None or seq_score > best_score:
        best_seq = seq
        best_score = seq_score
expected_sequence = torch.tensor(best_seq)
assert torch.equal(sequence, expected_sequence), f'Wrong sequence: {sequence} vs {expected_sequence}'
assert abs(score - best_score) < 1e-6, f'Wrong score: {score} vs {best_score}'
""",
        },
        {
            "name": "Beam width 1 equals greedy",
            "code": """
import torch
log_probs = torch.log(torch.tensor([
    [0.1, 0.8, 0.1],
    [0.7, 0.1, 0.2],
    [0.2, 0.3, 0.5],
], dtype=torch.float32))
sequence, score = {fn}(log_probs, beam_width=1)
expected = torch.tensor([1, 0, 2])
expected_score = log_probs[0, 1].item() + log_probs[1, 0].item() + log_probs[2, 2].item()
assert torch.equal(sequence, expected), f'Beam width 1 should be greedy: {sequence} vs {expected}'
assert abs(score - expected_score) < 1e-6, 'Score mismatch for beam width 1'
""",
        },
    ],
}
