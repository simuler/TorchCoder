"""Internal task registry used by the TorchCoder web application."""

from torch_judge.tasks import TASKS, get_task, list_tasks

__all__ = ["TASKS", "get_task", "list_tasks"]
