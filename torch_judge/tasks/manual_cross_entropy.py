"""手写交叉熵损失 task."""

TASK = {'category': '基础层',
 'title': '手写交叉熵损失',
 'difficulty': 'Medium',
 'function_name': 'manual_cross_entropy',
 'hint': '先减去每行最大值，用 LogSumExp 得到稳定的 log-softmax，再 gather 目标类别并取负均值。',
 'tests': [{'name': '匹配 PyTorch',
            'code': 'import torch, torch.nn.functional as F\n'
                    'torch.manual_seed(0); logits=torch.randn(7,11); '
                    'targets=torch.randint(0,11,(7,))\n'
                    'assert '
                    'torch.allclose({fn}(logits,targets),F.cross_entropy(logits,targets),atol=1e-6)\n'},
           {'name': '极端 logits 数值稳定',
            'code': 'import torch\n'
                    'logits=torch.tensor([[10000.,9999.,-10000.],[-10000.,10000.,9999.]])\n'
                    'loss={fn}(logits,torch.tensor([0,1]))\n'
                    'assert torch.isfinite(loss) and loss.item()>0\n'},
           {'name': '梯度',
            'code': 'import torch\n'
                    'x=torch.randn(4,5,requires_grad=True); loss={fn}(x,torch.tensor([0,1,2,3])); '
                    'loss.backward()\n'
                    'assert x.grad is not None and torch.isfinite(x.grad).all()\n'}]}
