#!/usr/bin/env python
"""启动 TorchCoder 网页服务。"""

import os
import sys
from pathlib import Path

# Prevent OpenMP duplicate library crash on Windows (numpy + torch both bundle libiomp5md.dll)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """检查运行所需依赖是否已安装。"""
    missing = []
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")

    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")

    try:
        import torch
    except ImportError:
        missing.append("torch")

    return missing


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🔥 TorchCoder 网页服务")
    print("=" * 50)

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n❌ 缺少依赖：{', '.join(missing)}")
        print("\n请先安装以下依赖：")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    # Import after dependency check
    import uvicorn
    from web.app import app

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    db_path = os.environ.get("TORCHCODER_DB_PATH", "data/torchcoder.db")
    public_origin = os.environ.get("PUBLIC_ORIGIN", "").strip().rstrip("/")

    if public_origin:
        browser_hint = public_origin
        browser_hint_label = "公网地址"
    elif host in {"0.0.0.0", "::"}:
        browser_hint = f"http://<server-ip>:{port}"
        browser_hint_label = "访问地址"
    else:
        browser_hint = f"http://{host}:{port}"
        browser_hint_label = "访问地址"

    print(f"\n  监听地址：{host}:{port}")
    print(f"  数据库：{db_path}")
    print(f"  {browser_hint_label}: {browser_hint}")
    if public_origin:
        print("  反向代理：请透传 Host、X-Forwarded-Proto 和 X-Forwarded-For")
    else:
        print("  提示：可设置 PUBLIC_ORIGIN=https://你的域名，以获得更清晰的公网部署提示")
    print("  按 Ctrl+C 可停止服务\n")
    print("=" * 50 + "\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
