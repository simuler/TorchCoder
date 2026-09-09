"""带 KV Cache 的多头注意力 task."""

TASK = {'category': 'LLM 推理组件',
 'title': '带 KV Cache 的多头注意力',
 'difficulty': 'Hard',
 'function_name': 'CachedMultiHeadAttention',
 'hint': '启用缓存时把本轮 K/V 追加到历史缓存，Q 只保留本轮查询；每次追加后必须更新 cache_k 和 cache_v。',
 'tests': [{'name': '缓存连续增长',
            'code': 'import torch\n'
                    'm = {fn}(12, 3)\n'
                    'y1 = m(torch.randn(2, 4, 12), use_cache=True)\n'
                    'assert y1.shape == (2, 4, 12) and m.cache_k.shape == (2, 3, 4, 4)\n'
                    'y2 = m(torch.randn(2, 1, 12), use_cache=True)\n'
                    'assert y2.shape == (2, 1, 12) and m.cache_k.shape[2] == 5 and '
                    'm.cache_v.shape[2] == 5\n'},
           {'name': '重置缓存',
            'code': 'import torch\n'
                    'm = {fn}(8, 2)\n'
                    'm(torch.randn(1, 3, 8), use_cache=True)\n'
                    'm.reset_cache()\n'
                    'assert m.cache_k is None and m.cache_v is None\n'},
           {'name': '非缓存数值结果',
            'code': 'import torch, math\n'
                    'torch.manual_seed(1)\n'
                    'm = {fn}(8, 2)\n'
                    'x = torch.randn(1, 3, 8)\n'
                    'y = m(x)\n'
                    'q = m.W_q(x).view(1,3,2,4).transpose(1,2)\n'
                    'k = m.W_k(x).view(1,3,2,4).transpose(1,2)\n'
                    'v = m.W_v(x).view(1,3,2,4).transpose(1,2)\n'
                    'ref = torch.softmax(q @ k.transpose(-2,-1) / 2.0, -1) @ v\n'
                    'ref = m.W_o(ref.transpose(1,2).contiguous().view(1,3,8))\n'
                    'assert torch.allclose(y, ref, atol=1e-6)\n'}]}
