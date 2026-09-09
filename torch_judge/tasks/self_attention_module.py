"""自注意力模块 task."""

TASK = {'category': '注意力机制',
 'title': '自注意力模块',
 'difficulty': 'Medium',
 'function_name': 'SelfAttention',
 'hint': '从同一个输入生成 Q、K、V，按 `QK^T / sqrt(d)` 计算权重，再与 V 相乘。',
 'tests': [{'name': '输出形状',
            'code': 'import torch, torch.nn as nn\n'
                    'm = {fn}(10)\n'
                    'x = torch.randn(3, 6, 10)\n'
                    'assert m(x).shape == x.shape\n'
                    'assert all(isinstance(getattr(m, n), nn.Linear) for n in '
                    "['W_q','W_k','W_v'])\n"},
           {'name': '恒等投影数值结果',
            'code': 'import torch, math\n'
                    'm = {fn}(4)\n'
                    'with torch.no_grad():\n'
                    '    for layer in [m.W_q,m.W_k,m.W_v]:\n'
                    '        layer.weight.copy_(torch.eye(4)); layer.bias.zero_()\n'
                    'x = torch.tensor([[[1.,0,0,0],[0,1.,0,0]]])\n'
                    'ref = torch.softmax(x @ x.transpose(-2,-1) / 2.0, -1) @ x\n'
                    'assert torch.allclose(m(x), ref, atol=1e-6)\n'},
           {'name': '梯度',
            'code': 'import torch\n'
                    'm = {fn}(6)\n'
                    'x = torch.randn(2,3,6,requires_grad=True)\n'
                    'm(x).sum().backward()\n'
                    'assert x.grad is not None and m.W_q.weight.grad is not None\n'}]}
