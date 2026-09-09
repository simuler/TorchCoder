"""自回归 SFT 损失 task."""

TASK = {'category': 'RLHF',
 'title': '自回归 SFT 损失',
 'difficulty': 'Medium',
 'function_name': 'compute_sft_loss',
 'hint': '自回归模型用第 t 位 logits 预测第 t+1 位标签，因此 logits 去掉末位、labels 去掉首位，再展平计算交叉熵。',
 'tests': [{'name': '移位后匹配参考',
            'code': 'import torch, torch.nn.functional as F\n'
                    'torch.manual_seed(0); logits=torch.randn(2,5,9); '
                    'labels=torch.randint(0,9,(2,5))\n'
                    'ref=F.cross_entropy(logits[:,:-1].reshape(-1,9),labels[:,1:].reshape(-1))\n'
                    'assert torch.allclose({fn}(logits,labels),ref,atol=1e-6)\n'},
           {'name': '忽略 Prompt',
            'code': 'import torch, torch.nn.functional as F\n'
                    'logits=torch.randn(1,5,7); labels=torch.tensor([[-100,-100,2,3,4]])\n'
                    'loss={fn}(logits,labels)\n'
                    'ref=F.cross_entropy(logits[:,:-1].reshape(-1,7),labels[:,1:].reshape(-1),ignore_index=-100)\n'
                    'assert torch.allclose(loss,ref)\n'},
           {'name': '梯度',
            'code': 'import torch\n'
                    'x=torch.randn(2,4,6,requires_grad=True); y=torch.randint(0,6,(2,4)); '
                    '{fn}(x,y).backward()\n'
                    'assert x.grad is not None\n'}]}
