import ast
from pathlib import Path


class ErrorDetector:
    """Detect basic Python syntax errors in source files."""

    def check_file(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "file": str(path),
                "error_type": "FileNotFoundError",
                "message": f"File not found: {path}",
            }

        if not path.is_file():
            return {
                "success": False,
                "file": str(path),
                "error_type": "NotAFile",
                "message": f"Path is not a file: {path}",
            }

        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source)

            return {
                "success": True,
                "file": str(path),
                "error_type": None,
                "message": "No syntax errors detected.",
            }

        except SyntaxError as error:
            return {
                "success": False,
                "file": str(path),
                "error_type": "SyntaxError",
                "message": error.msg,
                "line": error.lineno,
                "column": error.offset,
                "text": error.text.strip() if error.text else None,
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "file": str(path),
                "error_type": "UnicodeDecodeError",
                "message": "Unable to decode the file as UTF-8.",
            }

        except OSError as error:
            return {
                "success": False,
                "file": str(path),
                "error_type": type(error).__name__,
                "message": str(error),
            }