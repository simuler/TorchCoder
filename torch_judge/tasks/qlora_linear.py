"""QLoRA 量化低秩线性层 task."""

TASK = {'category': '参数高效微调',
 'title': 'QLoRA 量化低秩线性层',
 'difficulty': 'Hard',
 'function_name': 'QLoRALinear',
 'hint': '把冻结的基础权重对称量化到 4-bit 范围 `[-8, 7]`，前向时反量化，再叠加可训练的 LoRA 低秩更新。',
 'tests': [{'name': '4-bit 权重与形状',
            'code': 'import torch\n'
                    'm={fn}(12,7,rank=3)\n'
                    'assert m.qweight.dtype==torch.int8 and m.qweight.shape==(7,12)\n'
                    'assert int(m.qweight.min())>=-8 and int(m.qweight.max())<=7\n'
                    'assert m.A.shape==(3,12) and m.B.shape==(7,3)\n'
                    'assert m(torch.randn(2,4,12)).shape==(2,4,7)\n'},
           {'name': '零初始化适配器',
            'code': 'import torch, torch.nn.functional as F\n'
                    'm={fn}(6,5,rank=2,alpha=4); x=torch.randn(3,6)\n'
                    'ref=F.linear(x,m.qweight.float()*m.weight_scale)\n'
                    'assert torch.allclose(m(x),ref,atol=1e-6) and torch.count_nonzero(m.B)==0\n'},
           {'name': '低秩更新与梯度',
            'code': 'import torch, torch.nn.functional as F\n'
                    'm={fn}(6,5,rank=2,alpha=4); x=torch.randn(3,6)\n'
                    'with torch.no_grad(): m.B.fill_(0.2)\n'
                    'ref=F.linear(x,m.qweight.float()*m.weight_scale)+F.linear(F.linear(x,m.A),m.B)*2\n'
                    'assert torch.allclose(m(x),ref,atol=1e-6)\n'
                    'm(x).sum().backward(); assert m.A.grad is not None and m.B.grad is not '
                    'None\n'}]}
