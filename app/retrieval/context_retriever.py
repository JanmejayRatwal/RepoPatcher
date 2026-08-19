import ast
from pathlib import Path


class ContextRetriever:
    """Retrieve relevant source code surrounding an error."""

    def get_file_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 10,
    ) -> dict:
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
            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "Unable to decode file as UTF-8.",
            }

        if line_number < 1 or line_number > len(lines):
            return {
                "success": False,
                "error": f"Invalid line number: {line_number}",
            }

        start = max(
            0,
            line_number - 1 - context_lines,
        )

        end = min(
            len(lines),
            line_number + context_lines,
        )

        context = []

        for index in range(start, end):
            context.append(
                {
                    "line_number": index + 1,
                    "code": lines[index],
                    "is_error_line": (
                        index + 1 == line_number
                    ),
                }
            )

        return {
            "success": True,
            "file": str(path),
            "error_line": line_number,
            "start_line": start + 1,
            "end_line": end,
            "context": context,
        }

    def get_symbol_context(
        self,
        file_path: str,
        line_number: int,
    ) -> dict:
        """Find the function or class containing a line."""

        path = Path(file_path)

        if not path.exists() or not path.is_file():
            return {
                "success": False,
                "error": f"File not found: {path}",
            }

        try:
            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(source)

        except SyntaxError as error:
            return {
                "success": False,
                "error": (
                    "Cannot analyze symbols because "
                    f"the file contains a syntax error: {error}"
                ),
            }

        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "Unable to decode file as UTF-8.",
            }

        containing_symbols = []

        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                continue

            if not hasattr(node, "end_lineno"):
                continue

            if (
                node.lineno
                <= line_number
                <= node.end_lineno
            ):
                containing_symbols.append(node)

        if not containing_symbols:
            return {
                "success": True,
                "found": False,
                "symbol": None,
            }

        # The smallest containing symbol is usually
        # the most relevant one.
        symbol = min(
            containing_symbols,
            key=lambda node: (
                node.end_lineno - node.lineno
            ),
        )

        lines = source.splitlines()

        symbol_context = "\n".join(
            lines[
                symbol.lineno - 1 : symbol.end_lineno
            ]
        )

        if isinstance(symbol, ast.ClassDef):
            symbol_type = "class"

        elif isinstance(
            symbol,
            (
                ast.AsyncFunctionDef,
                ast.FunctionDef,
            ),
        ):
            symbol_type = "function"

        else:
            symbol_type = "unknown"

        return {
            "success": True,
            "found": True,
            "symbol": {
                "name": symbol.name,
                "type": symbol_type,
                "start_line": symbol.lineno,
                "end_line": symbol.end_lineno,
                "code": symbol_context,
            },
        }