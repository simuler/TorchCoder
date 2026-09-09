"""交叉注意力模块 task."""

TASK = {'category': '注意力机制',
 'title': '交叉注意力模块',
 'difficulty': 'Medium',
 'function_name': 'CrossAttention',
 'hint': 'Q 来自查询序列，K/V 来自上下文序列；查询长度可以与上下文长度不同。',
 'tests': [{'name': '不同序列长度',
            'code': 'import torch\n'
                    'm = {fn}(8)\n'
                    'q = torch.randn(2,3,8); k = torch.randn(2,7,8); v = torch.randn(2,7,8)\n'
                    'assert m(q,k,v).shape == (2,3,8)\n'},
           {'name': '数值结果',
            'code': 'import torch, math\n'
                    'torch.manual_seed(3)\n'
                    'm = {fn}(6)\n'
                    'q=torch.randn(1,2,6); k=torch.randn(1,4,6); v=torch.randn(1,4,6)\n'
                    'Q,K,V=m.W_q(q),m.W_k(k),m.W_v(v)\n'
                    'ref=torch.softmax(Q@K.transpose(-2,-1)/math.sqrt(6),-1)@V\n'
                    'assert torch.allclose(m(q,k,v),ref,atol=1e-6)\n'},
           {'name': '上下文梯度',
            'code': 'import torch\n'
                    'm={fn}(4)\n'
                    'q=torch.randn(1,2,4,requires_grad=True); '
                    'c=torch.randn(1,3,4,requires_grad=True)\n'
                    'm(q,c,c).sum().backward()\n'
                    'assert q.grad is not None and c.grad is not None\n'}]}
