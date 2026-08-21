import ast
from pathlib import Path


class SymbolIndex:
    """Build an index of Python functions and classes in a repository."""
    
    def find_symbol( self,
        symbols: list[dict],
        name: str,
     ) -> list[dict]:
        """Find symbols by name."""

        return [
            symbol
            for symbol in symbols
            if symbol["name"] == name
        ]
        
        
    

    def build(self, repository_path: str) -> dict:
        repository = Path(repository_path)

        if not repository.exists():
            return {
                "success": False,
                "error": f"Repository not found: {repository}",
            }

        symbols = []

        for file_path in repository.rglob("*.py"):

            if any(
                part in {
                    ".git",
                    ".venv",
                    "venv",
                    "env",
                    "__pycache__",
                    "node_modules",
                    ".idea",
                    ".vscode",
                }
                for part in file_path.parts
            ):
                continue

            try:
                source = file_path.read_text(
                    encoding="utf-8"
                )

                tree = ast.parse(source)

            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):

                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef,
                    ),
                ):
                    symbols.append(
                        {
                            "name": node.name,
                            "type": (
                                "class"
                                if isinstance(
                                    node,
                                    ast.ClassDef,
                                )
                                else "function"
                            ),
                            "file": str(file_path),
                            "line": node.lineno,
                            "end_line": node.end_lineno,
                        }
                    )

        return {
            "success": True,
            "symbols": symbols,
         }
        
        
        
        
def find_symbol(
    self,
    symbols: list[dict],
    name: str,
) -> list[dict]:
    """Find symbols by name."""

    return [
        symbol
        for symbol in symbols
        if symbol["name"] == name
    ]
    
def find_symbol(
    self,
    symbols: list[dict],
    name: str,
) -> list[dict]:
    """Find symbols by name."""

    return [
        symbol
        for symbol in symbols
        if symbol["name"] == name
    ]