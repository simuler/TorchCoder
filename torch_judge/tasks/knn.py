"""K-Nearest Neighbors classification task."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "K-Nearest Neighbors Classification",
    "difficulty": "Easy",
    "function_name": "knn_predict",
    "hint": (
        "Compute pairwise distances from each query to each training point, take the "
        "k smallest distances, gather their labels, and use majority vote. For ties, "
        "torch.bincount(...).argmax() gives the smallest label."
    ),
    "tests": [
        {
            "name": "Output shape and dtype",
            "code": """
import torch
x_train = torch.tensor([[0.0, 0.0], [1.0, 1.0], [3.0, 3.0]])
y_train = torch.tensor([0, 0, 1])
x_query = torch.tensor([[0.1, 0.2], [2.5, 2.8]])
pred = {fn}(x_train, y_train, x_query, k=1)
assert pred.shape == (2,), f'Prediction shape mismatch: {pred.shape}'
assert pred.dtype in (torch.int32, torch.int64), f'Predictions should be integer labels, got {pred.dtype}'
""",
        },
        {
            "name": "1-NN matches nearest label",
            "code": """
import torch
x_train = torch.tensor([[0.0, 0.0], [10.0, 10.0], [20.0, 20.0]])
y_train = torch.tensor([1, 3, 5])
x_query = torch.tensor([[0.2, -0.1], [11.0, 9.5], [18.0, 19.0]])
pred = {fn}(x_train, y_train, x_query, k=1)
expected = torch.tensor([1, 3, 5])
assert torch.equal(pred, expected), f'Wrong nearest-neighbor predictions: {pred} vs {expected}'
""",
        },
        {
            "name": "Majority vote with k=3",
            "code": """
import torch
x_train = torch.tensor([
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [4.0, 4.0],
    [4.0, 5.0],
], dtype=torch.float32)
y_train = torch.tensor([0, 0, 1, 1, 1])
x_query = torch.tensor([[0.2, 0.2], [4.2, 4.1]])
pred = {fn}(x_train, y_train, x_query, k=3)
expected = torch.tensor([0, 1])
assert torch.equal(pred, expected), f'Majority vote failed: {pred} vs {expected}'
""",
        },
        {
            "name": "Tie breaks to smaller label",
            "code": """
import torch
x_train = torch.tensor([
    [0.0, 0.0],
    [0.0, 2.0],
    [2.0, 0.0],
    [2.0, 2.0],
], dtype=torch.float32)
y_train = torch.tensor([2, 1, 1, 2])
x_query = torch.tensor([[1.0, 1.0]])
pred = {fn}(x_train, y_train, x_query, k=4)
expected = torch.tensor([1])
assert torch.equal(pred, expected), f'Tie-breaking should pick the smaller label: {pred} vs {expected}'
""",
        },
    ],
}
