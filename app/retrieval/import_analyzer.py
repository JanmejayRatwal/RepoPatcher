import ast
from pathlib import Path


class ImportAnalyzer:
    """Analyze Python imports in a source file."""

    def analyze(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}",
            }

        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {path}",
            }

        try:
            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(source)

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "Unable to decode file as UTF-8.",
            }

        except SyntaxError as error:
            return {
                "success": False,
                "error": f"Syntax error: {error}",
            }

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "name": None,
                            "alias": alias.asname,
                        }
                    )

            elif isinstance(node, ast.ImportFrom):

                for alias in node.names:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                        }
                    )

        return {
            "success": True,
            "file": str(path),
            "imports": imports,
        }