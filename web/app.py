"""FastAPI backend for the TorchCoder web interface."""

from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

# Prevent OpenMP duplicate library crash on Windows (numpy + torch both bundle libiomp5md.dll)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import torch
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from torch_judge.tasks import get_task, list_tasks
from web.persistence import (
    SESSION_TTL_DAYS,
    authenticate_user,
    create_session,
    create_user,
    delete_session,
    get_progress_map,
    get_task_state,
    get_user_by_session,
    init_db,
    record_submission,
    reset_user_progress,
    save_task_draft,
    set_current_task,
    touch_task,
)

app = FastAPI(title="TorchCoder", description="PyTorch interview practice platform")

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

SESSION_COOKIE_NAME = "torchcoder_session"
SESSION_COOKIE_MAX_AGE = SESSION_TTL_DAYS * 24 * 60 * 60
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

init_db()


class AuthRequest(BaseModel):
    username: str
    password: str


class SubmitRequest(BaseModel):
    task_id: str
    code: str


class WorkspaceRequest(BaseModel):
    code: str


class SubmitResponse(BaseModel):
    success: bool
    passed: int
    total: int
    total_time: float
    results: list[dict[str, Any]]
    output: str
    persisted: bool


_TASK_ASSET_ALIASES = {
    "mha": "multihead_attention",
}

def _build_asset_map(directory: str, suffix: str = "") -> dict[str, Path]:
    """Build a map from repository asset name without prefix/suffix to file path."""
    base_dir = Path(__file__).parent.parent / directory
    if not base_dir.exists():
        return {}

    result: dict[str, Path] = {}
    for asset in sorted(base_dir.glob(f"*{suffix}.ipynb")):
        name = asset.stem
        base = name.removesuffix(suffix) if suffix else name
        parts = base.split("_", 1)
        key = parts[1] if len(parts) == 2 and parts[0].isdigit() else base
        result[key] = asset
    return result


_TEMPLATE_MAP = _build_asset_map("templates")
_SOLUTION_MAP = _build_asset_map("solutions", "_solution")


def _find_asset_path(task_id: str, asset_map: dict[str, Path]) -> Path | None:
    if task_id in asset_map:
        return asset_map[task_id]
    alias = _TASK_ASSET_ALIASES.get(task_id)
    if alias and alias in asset_map:
        return asset_map[alias]
    return None


def _find_template_path(task_id: str) -> Path | None:
    return _find_asset_path(task_id, _TEMPLATE_MAP)


def _find_solution_path(task_id: str) -> Path | None:
    return _find_asset_path(task_id, _SOLUTION_MAP)


def _clean_description(markdown: str) -> str:
    import re

    markdown = re.sub(
        r"###\s*Signature\s*```python\s*.*?```",
        "",
        markdown,
        flags=re.DOTALL | re.IGNORECASE,
    )
    markdown = re.sub(
        r"###\s*Example\s*```\s*.*?```",
        "",
        markdown,
        flags=re.DOTALL | re.IGNORECASE,
    )
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


def _extract_signature_from_markdown(markdown: str) -> str:
    import re

    pattern = r"###\s*Signature\s*```python\s*(.*?)```"
    match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extract_example_from_markdown(markdown: str) -> str:
    import re

    pattern = r"###\s*Example\s*```\s*(.*?)```"
    match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _get_task_description(task_id: str) -> str:
    template_path = _find_template_path(task_id)

    if template_path and template_path.exists():
        try:
            with open(template_path, encoding="utf-8") as handle:
                asset_doc = json.load(handle)
            for cell in asset_doc.get("cells", []):
                if cell.get("cell_type") != "markdown":
                    continue
                source = "".join(cell.get("source", []))
                if task_id in source.lower() or "implement" in source.lower():
                    return _clean_description(source.strip())
        except Exception:
            pass

    task = get_task(task_id)
    if task:
        return f"Implement `{task['function_name']}` - {task['title']}"
    return ""


def _get_template_code(task_id: str) -> tuple[str, str, str]:
    template_path = _find_template_path(task_id)

    signature = ""
    example = ""
    template_code = ""
    markdown_content = ""

    if template_path and template_path.exists():
        try:
            with open(template_path, encoding="utf-8") as handle:
                asset_doc = json.load(handle)

            for cell in asset_doc.get("cells", []):
                if cell.get("cell_type") == "markdown":
                    markdown_content += "".join(cell.get("source", [])) + "\n\n"

            signature = _extract_signature_from_markdown(markdown_content)
            example = _extract_example_from_markdown(markdown_content)

            import_lines: list[str] = []
            for cell in asset_doc.get("cells", []):
                if cell.get("cell_type") != "code":
                    continue
                source = "".join(cell.get("source", []))
                stripped = source.strip()
                if stripped.startswith("import") or stripped.startswith("from"):
                    if "torch_judge" not in stripped:
                        import_lines.append(stripped)
                        continue
                if "TODO" in source or "def " in source or "class " in source:
                    template_code = stripped
                    if import_lines:
                        template_code = "\n".join(import_lines) + "\n\n" + template_code
                    break
        except Exception:
            pass

    if not template_code:
        task = get_task(task_id)
        if task:
            function_name = task["function_name"]
            if function_name[0].isupper():
                template_code = (
                    f"class {function_name}:\n"
                    "    def __init__(self, ...):\n"
                    "        # TODO: implement\n"
                    "        pass\n"
                )
                if not signature:
                    signature = f"class {function_name}:\n    def __init__(self, ...)"
            else:
                template_code = (
                    f"def {function_name}(...):\n"
                    "    # TODO: implement\n"
                    "    pass\n"
                )
                if not signature:
                    signature = f"def {function_name}(...)"

    return template_code, signature, example


def _get_solution(task_id: str) -> dict[str, str] | None:
    solution_path = _find_solution_path(task_id)
    if not solution_path or not solution_path.exists():
        return None

    try:
        with open(solution_path, encoding="utf-8") as handle:
            asset_doc = json.load(handle)
    except Exception:
        return None

    markdown_parts: list[str] = []
    code_parts: list[str] = []

    for cell in asset_doc.get("cells", []):
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        if cell.get("cell_type") == "markdown":
            markdown_parts.append(source.strip())
        elif cell.get("cell_type") == "code":
            stripped = source.strip()
            if "from torch_judge" in stripped or "torch_judge.check" in stripped:
                continue
            code_parts.append(stripped)

    return {
        "markdown": "\n\n".join(markdown_parts),
        "code": "\n\n".join(code_parts),
    }


def _run_tests(task_id: str, code: str) -> tuple[int, int, float, list[dict[str, Any]], str]:
    task = get_task(task_id)
    if not task:
        return 0, 0, 0.0, [], "Task not found"

    function_name = task["function_name"]
    tests = task["tests"]

    stdout_capture = StringIO()
    stderr_capture = StringIO()
    namespace: dict[str, Any] = {
        "torch": torch,
        "nn": torch.nn,
        "F": torch.nn.functional,
        "np": np,
        "numpy": np,
        "math": math,
        "__builtins__": __builtins__,
    }

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(compile(code, "<user_code>", "exec"), namespace)
    except SyntaxError as exc:
        return 0, len(tests), 0.0, [], f"Syntax Error: {exc}"
    except Exception as exc:
        return 0, len(tests), 0.0, [], f"Code execution error: {type(exc).__name__}: {exc}"

    if function_name not in namespace:
        return 0, len(tests), 0.0, [], f"Function/class '{function_name}' not found in your code."

    user_fn = namespace[function_name]
    test_namespace = {**namespace, function_name: user_fn}

    results: list[dict[str, Any]] = []
    passed = 0
    total_time = 0.0

    for test in tests:
        test_code = test["code"].replace("{fn}", function_name)
        t0 = time.perf_counter()
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(compile(test_code, f"<test:{test['name']}>", "exec"), test_namespace)
            elapsed = time.perf_counter() - t0
            total_time += elapsed
            passed += 1
            results.append(
                {
                    "name": test["name"],
                    "passed": True,
                    "time": elapsed,
                    "error": None,
                }
            )
        except AssertionError as exc:
            elapsed = time.perf_counter() - t0
            results.append(
                {
                    "name": test["name"],
                    "passed": False,
                    "time": elapsed,
                    "error": str(exc) or "Assertion failed",
                }
            )
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            results.append(
                {
                    "name": test["name"],
                    "passed": False,
                    "time": elapsed,
                    "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
                }
            )

    output = stdout_capture.getvalue()
    if stderr_capture.getvalue():
        output += "\n" + stderr_capture.getvalue()

    return passed, len(tests), total_time, results, output.strip()


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=SESSION_COOKIE_MAX_AGE,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def _build_auth_payload(user: dict[str, Any] | None) -> dict[str, Any]:
    if not user:
        return {
            "authenticated": False,
            "user": None,
            "current_task_id": None,
        }
    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "created_at": user["created_at"],
            "last_login_at": user["last_login_at"],
        },
        "current_task_id": user.get("current_task_id"),
    }


async def get_optional_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, Any] | None:
    return get_user_by_session(session_token)


async def get_required_user(
    user: dict[str, Any] | None = Depends(get_optional_user),
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, Any]:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Session expired. Please sign in again."
                if session_token
                else "Please sign in to use this feature."
            ),
        )
    return user


async def get_session_token(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> str | None:
    return session_token


@app.get("/")
async def root() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>TorchCoder</h1><p>Static files not found.</p>")


@app.get("/api/auth/me")
async def auth_me(user: dict[str, Any] | None = Depends(get_optional_user)) -> dict[str, Any]:
    return _build_auth_payload(user)


@app.post("/api/auth/register")
async def register(
    payload: AuthRequest,
    response: Response,
    session_token: str | None = Depends(get_session_token),
) -> dict[str, Any]:
    try:
        user = create_user(payload.username, payload.password)
    except ValueError as exc:
        message = str(exc)
        status_code = (
            status.HTTP_409_CONFLICT if "taken" in message.lower() else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=message) from exc

    delete_session(session_token)
    token = create_session(user["id"])
    _set_session_cookie(response, token)
    return _build_auth_payload(user)


@app.post("/api/auth/login")
async def login(
    payload: AuthRequest,
    response: Response,
    session_token: str | None = Depends(get_session_token),
) -> dict[str, Any]:
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    delete_session(session_token)
    token = create_session(user["id"])
    _set_session_cookie(response, token)
    return _build_auth_payload(user)


@app.post("/api/auth/logout")
async def logout(
    response: Response,
    session_token: str | None = Depends(get_session_token),
) -> dict[str, bool]:
    delete_session(session_token)
    _clear_session_cookie(response)
    return {"success": True}


@app.get("/api/tasks")
async def get_tasks(_: dict[str, Any] = Depends(get_required_user)) -> dict[str, list[dict[str, Any]]]:
    tasks: list[dict[str, Any]] = []
    for task_id, task in list_tasks():
        tasks.append(
            {
                "id": task_id,
                "title": task["title"],
                "difficulty": task["difficulty"],
                "function_name": task["function_name"],
                "category": task.get("category", ""),
            }
        )
    return {"tasks": tasks}


@app.get("/api/tasks/{task_id}")
async def get_task_detail(
    task_id: str,
    user: dict[str, Any] = Depends(get_required_user),
) -> dict[str, Any]:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    touch_task(user["id"], task_id)
    task_state = get_task_state(user["id"], task_id)

    template, signature, example = _get_template_code(task_id)
    return {
        "id": task_id,
        "title": task["title"],
        "difficulty": task["difficulty"],
        "hint": task["hint"],
        "function_name": task["function_name"],
        "description": _get_task_description(task_id),
        "template": template,
        "signature": signature,
        "example": example,
        "tests_count": len(task["tests"]),
        "has_solution": _find_solution_path(task_id) is not None,
        "saved_code": task_state["draft_code"],
        "saved_at": task_state["draft_updated_at"],
        "status": task_state["status"],
        "attempts": task_state["attempts"],
        "best_time": task_state["best_time"],
    }


@app.put("/api/tasks/{task_id}/workspace")
async def save_workspace(
    task_id: str,
    payload: WorkspaceRequest,
    user: dict[str, Any] = Depends(get_required_user),
) -> dict[str, Any]:
    if not get_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    saved_at = save_task_draft(user["id"], task_id, payload.code)
    return {"success": True, "saved_at": saved_at}


@app.get("/api/tasks/{task_id}/solution")
async def get_task_solution(
    task_id: str,
    _: dict[str, Any] = Depends(get_required_user),
) -> dict[str, str]:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    solution = _get_solution(task_id)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not available.",
        )

    return {
        "id": task_id,
        "markdown": solution["markdown"],
        "code": solution["code"],
    }


@app.get("/api/random")
async def get_random_task(
    user: dict[str, Any] = Depends(get_required_user),
) -> dict[str, Any]:
    import random

    tasks = list_tasks()
    progress_map = get_progress_map(user["id"])
    unsolved = [
        (task_id, task)
        for task_id, task in tasks
        if progress_map.get(task_id, {}).get("status") != "solved"
    ]
    pool = unsolved or tasks
    task_id, task = random.choice(pool)

    set_current_task(user["id"], task_id)

    return {
        "id": task_id,
        "title": task["title"],
        "difficulty": task["difficulty"],
        "function_name": task["function_name"],
    }


@app.get("/api/progress")
async def get_progress(
    user: dict[str, Any] = Depends(get_required_user),
) -> dict[str, Any]:
    progress_map = get_progress_map(user["id"])
    tasks = list_tasks()

    task_progress: list[dict[str, Any]] = []
    for task_id, task in tasks:
        entry = progress_map.get(task_id, {})
        draft_code = entry.get("draft_code")
        task_progress.append(
            {
                "id": task_id,
                "title": task["title"],
                "difficulty": task["difficulty"],
                "status": entry.get("status", "todo"),
                "attempts": entry.get("attempts", 0),
                "best_time": entry.get("best_time"),
                "has_draft": bool(draft_code and draft_code.strip()),
                "draft_updated_at": entry.get("draft_updated_at"),
            }
        )

    solved = sum(1 for item in task_progress if item["status"] == "solved")
    return {
        "authenticated": True,
        "current_task_id": user.get("current_task_id"),
        "solved": solved,
        "total": len(tasks),
        "tasks": task_progress,
    }


@app.post("/api/submit", response_model=SubmitResponse)
async def submit_code(
    request: SubmitRequest,
    user: dict[str, Any] = Depends(get_required_user),
) -> SubmitResponse:
    task = get_task(request.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    passed, total, total_time, results, output = _run_tests(request.task_id, request.code)

    record_submission(
        user["id"],
        request.task_id,
        request.code,
        solved=(passed == total),
        total_time=total_time,
    )

    return SubmitResponse(
        success=(passed == total),
        passed=passed,
        total=total,
        total_time=total_time,
        results=results,
        output=output,
        persisted=True,
    )


@app.post("/api/reset")
async def reset_progress(
    user: dict[str, Any] = Depends(get_required_user),
) -> dict[str, bool]:
    reset_user_progress(user["id"])
    return {"success": True}


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
