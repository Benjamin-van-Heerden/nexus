import subprocess
from datetime import datetime

from src.utils.paths import get_project_root


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=get_project_root(),
        capture_output=True,
        text=True,
    )


def pre_sync() -> None:
    _run_git("pull")


def post_sync() -> None:
    status = _run_git("status", "--porcelain")
    if not status.stdout.strip():
        return

    _run_git("add", "-A")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _run_git("commit", "-m", timestamp)
    _run_git("push")
