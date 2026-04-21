"""Hand-written backward pass for a two-layer MLP."""

TASK = {
    "category": "ML 基础与解码策略",
    "title": "Hand-Written Backward for a 2-Layer MLP",
    "difficulty": "Hard",
    "function_name": "mlp_backward",
    "hint": (
        "Forward: z1 = x @ w1.T + b1, h = ReLU(z1), y = h @ w2.T + b2, "
        "loss = mean((y - target)^2). Backprop from the MSE loss manually, "
        "then multiply by the ReLU mask (z1 > 0)."
    ),
    "tests": [
        {
            "name": "Returns all gradient tensors",
            "code": """
import torch
x = torch.randn(4, 3)
w1 = torch.randn(5, 3)
b1 = torch.randn(5)
w2 = torch.randn(2, 5)
b2 = torch.randn(2)
target = torch.randn(4, 2)
grads = {fn}(x, w1, b1, w2, b2, target)
assert set(grads.keys()) == {'w1', 'b1', 'w2', 'b2'}, f'Wrong gradient keys: {grads.keys()}'
assert grads['w1'].shape == w1.shape
assert grads['b1'].shape == b1.shape
assert grads['w2'].shape == w2.shape
assert grads['b2'].shape == b2.shape
""",
        },
        {
            "name": "Matches autograd",
            "code": """
import torch
torch.manual_seed(0)
x = torch.randn(6, 4)
w1 = torch.randn(7, 4)
b1 = torch.randn(7)
w2 = torch.randn(3, 7)
b2 = torch.randn(3)
target = torch.randn(6, 3)
grads = {fn}(x, w1, b1, w2, b2, target)

w1_ref = w1.clone().requires_grad_(True)
b1_ref = b1.clone().requires_grad_(True)
w2_ref = w2.clone().requires_grad_(True)
b2_ref = b2.clone().requires_grad_(True)

z1 = x @ w1_ref.T + b1_ref
h = torch.relu(z1)
out = h @ w2_ref.T + b2_ref
loss = ((out - target) ** 2).mean()
loss.backward()

assert torch.allclose(grads['w1'], w1_ref.grad, atol=1e-5), 'w1 gradient mismatch'
assert torch.allclose(grads['b1'], b1_ref.grad, atol=1e-5), 'b1 gradient mismatch'
assert torch.allclose(grads['w2'], w2_ref.grad, atol=1e-5), 'w2 gradient mismatch'
assert torch.allclose(grads['b2'], b2_ref.grad, atol=1e-5), 'b2 gradient mismatch'
""",
        },
        {
            "name": "ReLU blocks negative hidden units",
            "code": """
import torch
x = torch.tensor([[1.0, 1.0]])
w1 = torch.tensor([[-2.0, -2.0], [1.0, 1.0]])
b1 = torch.tensor([-1.0, 0.0])
w2 = torch.tensor([[3.0, 4.0]])
b2 = torch.tensor([0.0])
target = torch.tensor([[1.0]])
grads = {fn}(x, w1, b1, w2, b2, target)
assert torch.allclose(grads['w1'][0], torch.zeros_like(grads['w1'][0])), 'Negative ReLU unit should have zero weight gradient'
assert torch.allclose(grads['b1'][0], torch.tensor(0.0)), 'Negative ReLU unit should have zero bias gradient'
assert grads['w1'][1].abs().sum() > 0, 'Active ReLU unit should receive gradient'
""",
        },
    ],
}
