"""PreNorm 包装器 task."""

TASK = {'category': '完整架构',
 'title': 'PreNorm 包装器',
 'difficulty': 'Medium',
 'function_name': 'PreNorm',
 'hint': 'PreNorm 的顺序是先执行 LayerNorm，再调用被包装的子模块；额外位置参数和关键字参数需要原样透传。',
 'tests': [{'name': '先归一化再调用',
            'code': 'import torch, torch.nn as nn\n'
                    'm={fn}(6,nn.Identity()); x=torch.randn(2,4,6)\n'
                    'assert torch.allclose(m(x),m.norm(x),atol=1e-6)\n'
                    'assert isinstance(m.norm,nn.LayerNorm)\n'},
           {'name': '包装子模块',
            'code': 'import torch, torch.nn as nn\n'
                    'linear=nn.Linear(5,3); m={fn}(5,linear); x=torch.randn(2,4,5)\n'
                    'assert torch.allclose(m(x),linear(m.norm(x)),atol=1e-6) and '
                    'm(x).shape==(2,4,3)\n'},
           {'name': '参数透传与梯度',
            'code': 'import torch, torch.nn as nn\n'
                    'class Scale(nn.Module):\n'
                    '    def forward(self,x,factor=1): return x*factor\n'
                    'm={fn}(4,Scale()); x=torch.randn(2,3,4,requires_grad=True); y=m(x,factor=3); '
                    'y.sum().backward()\n'
                    'assert torch.allclose(y,m.norm(x)*3,atol=1e-6) and x.grad is not None\n'}]}
