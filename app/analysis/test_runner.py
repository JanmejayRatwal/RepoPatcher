import subprocess
import sys
from pathlib import Path


class TestRunner:
    """Run a repository's test suite and collect execution results."""

    def run(self, repository_path: str) -> dict:
        repository = Path(repository_path)

        if not repository.exists():
            return {
                "success": False,
                "status": "repository_not_found",
                "exit_code": None,
                "stdout": "",
                "stderr": f"Repository not found: {repository}",
            }

        if not repository.is_dir():
            return {
                "success": False,
                "status": "invalid_repository",
                "exit_code": None,
                "stdout": "",
                "stderr": f"Not a directory: {repository}",
            }

        try:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                ],
                cwd=repository,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": process.returncode == 0,
                "status": (
                    "passed"
                    if process.returncode == 0
                    else "failed"
                ),
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
            }

        except subprocess.TimeoutExpired as error:
            return {
                "success": False,
                "status": "timeout",
                "exit_code": None,
                "stdout": error.stdout or "",
                "stderr": error.stderr or "",
            }

        except OSError as error:
            return {
                "success": False,
                "status": "execution_error",
                "exit_code": None,
                "stdout": "",
                "stderr": str(error),
            }