from pathlib import Path

from app.analysis.error_detector import ErrorDetector


class RepositoryScanner:
    """Scan a repository for Python files and detect syntax errors."""

    def __init__(self):
        self.detector = ErrorDetector()

    def discover_python_files(self, repository_path: str) -> list[Path]:
        """
        Find Python files inside the repository.

        Hidden directories and common generated/virtual-environment
        directories are ignored.
        """

        repository = Path(repository_path)

        if not repository.exists():
            raise FileNotFoundError(
                f"Repository not found: {repository}"
            )

        if not repository.is_dir():
            raise NotADirectoryError(
                f"Repository path is not a directory: {repository}"
            )

        ignored_directories = {
            ".git",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            ".idea",
            ".vscode",
        }

        python_files = []

        for path in repository.rglob("*.py"):
            if any(
                directory in ignored_directories
                for directory in path.parts
            ):
                continue

            python_files.append(path)

        return sorted(python_files)

    def scan(self, repository_path: str) -> dict:
        """Scan all discovered Python files."""

        python_files = self.discover_python_files(repository_path)

        results = []

        for file_path in python_files:
            result = self.detector.check_file(str(file_path))
            results.append(result)

        errors = [
            result
            for result in results
            if not result["success"]
        ]

        return {
            "repository": str(Path(repository_path).resolve()),
            "files_scanned": len(python_files),
            "errors_found": len(errors),
            "results": results,
            "errors": errors,
        }