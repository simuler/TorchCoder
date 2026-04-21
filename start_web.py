#!/usr/bin/env python
"""Start TorchCoder web server."""

import os
import sys
from pathlib import Path

# Prevent OpenMP duplicate library crash on Windows (numpy + torch both bundle libiomp5md.dll)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Check if required dependencies are installed."""
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
    print("🔥 TorchCoder Web Server")
    print("=" * 50)

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("\nPlease install them with:")
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
        browser_hint_label = "Public URL"
    elif host in {"0.0.0.0", "::"}:
        browser_hint = f"http://<server-ip>:{port}"
        browser_hint_label = "Open"
    else:
        browser_hint = f"http://{host}:{port}"
        browser_hint_label = "Open"

    print(f"\n  Bind: {host}:{port}")
    print(f"  Database: {db_path}")
    print(f"  {browser_hint_label}: {browser_hint}")
    if public_origin:
        print("  Proxy: forward Host, X-Forwarded-Proto, and X-Forwarded-For")
    else:
        print("  Tip: set PUBLIC_ORIGIN=https://your-domain for clearer remote deployment hints")
    print("  Press Ctrl+C to stop\n")
    print("=" * 50 + "\n")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
