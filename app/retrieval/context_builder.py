from pathlib import Path

from app.retrieval.context_retriever import ContextRetriever
from app.retrieval.import_analyzer import ImportAnalyzer
from app.retrieval.import_resolver import ImportResolver
from app.retrieval.symbol_index import SymbolIndex


class ContextBuilder:
    """Build a structured repair context for an error."""

    def __init__(self):
        self.context_retriever = ContextRetriever()
        self.import_analyzer = ImportAnalyzer()
        self.import_resolver = ImportResolver()
        self.symbol_index = SymbolIndex()

    def build(
        self,
        repository_path: str,
        file_path: str,
        line_number: int,
        error_message: str,
    ) -> dict:

        repository = Path(repository_path).resolve()
        target_file = Path(file_path).resolve()

        result = {
            "success": False,
            "error": {
                "message": error_message,
                "file": str(target_file),
                "line": line_number,
            },
            "primary_context": None,
            "primary_symbol": None,
            "imports": [],
            "related_symbols": [],
        }

        # -------------------------------------------------
        # 1. Get surrounding source code
        # -------------------------------------------------

        context = self.context_retriever.get_file_context(
            str(target_file),
            line_number,
        )

        if not context["success"]:
            result["error"]["context_error"] = context["error"]
            return result

        result["primary_context"] = context

        # -------------------------------------------------
        # 2. Find containing function/class
        # -------------------------------------------------

        symbol_context = (
            self.context_retriever.get_symbol_context(
                str(target_file),
                line_number,
            )
        )

        if (
            symbol_context["success"]
            and symbol_context.get("found")
        ):
            result["primary_symbol"] = (
                symbol_context["symbol"]
            )

        # -------------------------------------------------
        # 3. Analyze imports
        # -------------------------------------------------

        import_result = self.import_analyzer.analyze(
            str(target_file)
        )

        if import_result["success"]:
            result["imports"] = import_result["imports"]

        # -------------------------------------------------
        # 4. Build repository symbol index
        # -------------------------------------------------

        index_result = self.symbol_index.build(
            str(repository)
        )

        if not index_result["success"]:
            result["error"]["index_error"] = (
                index_result["error"]
            )
            return result

        symbols = index_result["symbols"]

        # -------------------------------------------------
        # 5. Resolve imported modules
        # -------------------------------------------------

        for imported in result["imports"]:

            module = imported["module"]
            symbol_name = imported["name"]

            resolved_files = (
                self.import_resolver.resolve(
                    str(repository),
                    str(target_file),
                    module,
                    symbol_name,
                )
            )

            for resolved in resolved_files:

                if symbol_name is None:
                    continue

                matching_symbols = (
                    self.symbol_index.find_symbol(
                        symbols,
                        symbol_name,
                    )
                )

                for symbol in matching_symbols:

                    if symbol["file"] != resolved["file"]:
                        continue

                    result["related_symbols"].append(
                        symbol
                    )

        result["success"] = True

        return result