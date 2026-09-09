"""HA-LoRA 多头注意力 task."""

TASK = {'category': '参数高效微调',
 'title': 'HA-LoRA 多头注意力',
 'difficulty': 'Hard',
 'function_name': 'PurifiedMultiHeadAttention',
 'hint': '为每个注意力头分别设置低秩 A/B，并用 softmax 门控调节每个头的 LoRA 更新；基础 Q/K/V/O 投影保持标准 MHA。',
 'tests': [{'name': '逐头低秩参数',
            'code': 'import torch\n'
                    'm={fn}(16,4,rank=3)\n'
                    'assert m.lora_A_q.shape==(4,4,3) and m.lora_B_q.shape==(4,3,4)\n'
                    'assert m.lora_A_v.shape==(4,4,3) and m.head_gates.shape==(4,)\n'
                    'assert torch.count_nonzero(m.lora_B_q)==0 and '
                    'torch.count_nonzero(m.lora_B_v)==0\n'},
           {'name': '零初始化等价基础注意力',
            'code': 'import torch, math\n'
                    'torch.manual_seed(4); m={fn}(8,2,rank=2); x=torch.randn(1,3,8); y=m(x)\n'
                    'q=m.W_q(x).view(1,3,2,4).transpose(1,2); '
                    'k=m.W_k(x).view(1,3,2,4).transpose(1,2); '
                    'v=m.W_v(x).view(1,3,2,4).transpose(1,2)\n'
                    'ref=torch.softmax(q@k.transpose(-2,-1)/2.0,-1)@v\n'
                    'ref=m.W_o(ref.transpose(1,2).contiguous().view(1,3,8))\n'
                    'assert torch.allclose(y,ref,atol=1e-6)\n'},
           {'name': 'LoRA 梯度',
            'code': 'import torch\n'
                    'm={fn}(8,2,rank=2); x=torch.randn(2,3,8)\n'
                    'm(x).sum().backward()\n'
                    'assert m.lora_B_q.grad is not None and m.lora_B_v.grad is not None and '
                    'm.head_gates.grad is not None\n'}]}
