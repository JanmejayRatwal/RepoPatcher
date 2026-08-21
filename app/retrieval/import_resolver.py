from pathlib import Path


class ImportResolver:
    """Resolve imported symbols to files in a repository."""

    def resolve(
        self,
        repository_path: str,
        importing_file: str,
        module: str,
        symbol: str | None = None,
    ) -> list[dict]:
        repository = Path(repository_path).resolve()
        importing_path = Path(importing_file).resolve()

        module_parts = module.split(".")

        candidates = []

        # Example:
        # utils -> utils.py
        candidates.append(
            repository.joinpath(
                *module_parts
            ).with_suffix(".py")
        )

        # Example:
        # utils -> utils/__init__.py
        candidates.append(
            repository.joinpath(
                *module_parts,
                "__init__.py",
            )
        )

        matches = []

        for candidate in candidates:

            if not candidate.exists():
                continue

            if not candidate.is_file():
                continue

            result = {
                "module": module,
                "file": str(candidate),
            }

            if symbol is not None:
                result["symbol"] = symbol

            matches.append(result)

        return matches