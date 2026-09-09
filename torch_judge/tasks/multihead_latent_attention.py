"""多头潜在注意力（MLA） task."""

TASK = {'category': '注意力机制',
 'title': '多头潜在注意力（MLA）',
 'difficulty': 'Hard',
 'function_name': 'MultiHeadLatentAttention',
 'hint': '先把输入压缩到低维潜变量，再分别解压得到 K 和 V；Q 保持标准多头投影。',
 'tests': [{'name': '低秩结构与形状',
            'code': 'import torch\n'
                    'm={fn}(d_model=16,num_heads=4,latent_dim=6)\n'
                    'assert m.kv_down.weight.shape==(6,16)\n'
                    'assert m.k_up.weight.shape==(16,6) and m.v_up.weight.shape==(16,6)\n'
                    'assert m(torch.randn(2,5,16)).shape==(2,5,16)\n'},
           {'name': '数值结果',
            'code': 'import torch, math\n'
                    'torch.manual_seed(5)\n'
                    'm={fn}(8,2,3); x=torch.randn(1,4,8); y=m(x)\n'
                    'q=m.W_q(x).view(1,4,2,4).transpose(1,2); z=m.kv_down(x)\n'
                    'k=m.k_up(z).view(1,4,2,4).transpose(1,2); '
                    'v=m.v_up(z).view(1,4,2,4).transpose(1,2)\n'
                    'ref=torch.softmax(q@k.transpose(-2,-1)/2.0,-1)@v\n'
                    'ref=m.W_o(ref.transpose(1,2).contiguous().view(1,4,8))\n'
                    'assert torch.allclose(y,ref,atol=1e-6)\n'},
           {'name': '潜变量梯度',
            'code': 'import torch\n'
                    'm={fn}(12,3,4); x=torch.randn(1,3,12,requires_grad=True)\n'
                    'm(x).sum().backward()\n'
                    'assert x.grad is not None and m.kv_down.weight.grad is not None\n'}]}
