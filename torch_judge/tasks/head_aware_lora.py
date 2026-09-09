"""Head-Aware LoRA task."""

TASK = {'category': '参数高效微调',
 'title': 'Head-Aware LoRA',
 'difficulty': 'Hard',
 'function_name': 'AttentionHeadPurificationLoRA',
 'hint': '将输入拆成多个头，每个头使用独立的低秩 A/B，再用归一化门控缩放各头更新，最后拼回模型维度。',
 'tests': [{'name': '参数结构与冻结基础权重',
            'code': 'import torch\n'
                    'm={fn}(16,4,rank=2,alpha=4)\n'
                    'assert m.lora_A.shape==(4,4,2) and m.lora_B.shape==(4,2,4)\n'
                    'assert not m.weight.requires_grad and m.head_gates.shape==(4,)\n'
                    'assert m(torch.randn(2,5,16)).shape==(2,5,16)\n'},
           {'name': '初始等价基础层',
            'code': 'import torch\n'
                    'm={fn}(8,2,rank=2); x=torch.randn(2,3,8)\n'
                    'assert torch.allclose(m(x),x@m.weight,atol=1e-6)\n'},
           {'name': '逐头更新数值结果',
            'code': 'import torch, torch.nn.functional as F\n'
                    'm={fn}(8,2,rank=2,alpha=4); x=torch.randn(1,3,8)\n'
                    'with torch.no_grad(): m.lora_B.fill_(0.1); '
                    'm.head_gates.copy_(torch.tensor([0.,1.]))\n'
                    'xh=x.view(1,3,2,4).transpose(1,2); '
                    'gates=F.softmax(m.head_gates,0).view(1,2,1,1)*2\n'
                    'upd=(xh@m.lora_A@m.lora_B)*2*gates\n'
                    'ref=x@m.weight+upd.transpose(1,2).contiguous().view(1,3,8)\n'
                    'assert torch.allclose(m(x),ref,atol=1e-6)\n'
                    'm(x).sum().backward(); assert m.lora_B.grad is not None and m.head_gates.grad '
                    'is not None\n'}]}
