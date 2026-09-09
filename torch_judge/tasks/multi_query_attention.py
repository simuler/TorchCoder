"""多查询注意力（MQA） task."""

TASK = {'category': '注意力机制',
 'title': '多查询注意力（MQA）',
 'difficulty': 'Hard',
 'function_name': 'MultiQueryAttention',
 'hint': '查询使用多个头，而键和值只投影成一个共享头；计算注意力时依靠广播让所有查询头共享同一组 K/V。',
 'tests': [{'name': '输出形状与共享投影',
            'code': 'import torch, torch.nn as nn\n'
                    'm = {fn}(d_model=16, num_heads=4)\n'
                    'x = torch.randn(2, 5, 16)\n'
                    'assert m(x).shape == (2, 5, 16)\n'
                    'assert m.W_q.out_features == 16\n'
                    'assert m.W_k.out_features == 4 and m.W_v.out_features == 4\n'},
           {'name': '数值结果',
            'code': 'import torch, math\n'
                    'torch.manual_seed(7)\n'
                    'm = {fn}(12, 3)\n'
                    'x = torch.randn(2, 4, 12)\n'
                    'out = m(x)\n'
                    'q = m.W_q(x).view(2, 4, 3, 4).transpose(1, 2)\n'
                    'k = m.W_k(x).unsqueeze(1)\n'
                    'v = m.W_v(x).unsqueeze(1)\n'
                    'ref = torch.softmax(q @ k.transpose(-2, -1) / 2.0, dim=-1) @ v\n'
                    'ref = m.W_o(ref.transpose(1, 2).contiguous().view(2, 4, 12))\n'
                    'assert torch.allclose(out, ref, atol=1e-6)\n'},
           {'name': '掩码与梯度',
            'code': 'import torch\n'
                    'm = {fn}(8, 2)\n'
                    'x = torch.randn(1, 3, 8, requires_grad=True)\n'
                    'mask = torch.tensor([[[[1, 1, 0], [1, 1, 0], [1, 1, 0]]]])\n'
                    'y = m(x, mask)\n'
                    'y.sum().backward()\n'
                    'assert torch.isfinite(y).all() and x.grad is not None\n'}]}
