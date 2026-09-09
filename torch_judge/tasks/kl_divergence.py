"""KL 散度 task."""

TASK = {'category': 'RLHF',
 'title': 'KL 散度',
 'difficulty': 'Medium',
 'function_name': 'kl_divergence',
 'hint': '对两组 logits 分别做 log-softmax，按 `sum p * (log p - log q)` 计算每个样本的 KL，并支持 none/mean/sum。',
 'tests': [{'name': '匹配参考公式',
            'code': 'import torch, torch.nn.functional as F\n'
                    'torch.manual_seed(2); p=torch.randn(5,9); q=torch.randn(5,9)\n'
                    "ref=F.kl_div(F.log_softmax(q,-1),F.softmax(p,-1),reduction='none').sum(-1)\n"
                    "assert torch.allclose({fn}(p,q,'none'),ref,atol=1e-6)\n"
                    'assert torch.allclose({fn}(p,q),ref.mean(),atol=1e-6)\n'},
           {'name': '相同分布为零',
            'code': 'import torch\n'
                    'x=torch.tensor([[1000.,999.,-1000.]])\n'
                    'v={fn}(x,x)\n'
                    'assert torch.allclose(v,torch.tensor(0.),atol=1e-7) and torch.isfinite(v)\n'},
           {'name': 'sum 与梯度',
            'code': 'import torch\n'
                    'p=torch.randn(3,4,requires_grad=True); q=torch.randn(3,4,requires_grad=True)\n'
                    "v={fn}(p,q,'sum'); v.backward()\n"
                    'assert p.grad is not None and q.grad is not None and v.ndim==0\n'}]}
