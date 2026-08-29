from pathlib import Path


class PatchApplier:
    """Apply a validated repair to a repository file."""

    def apply(
        self,
        repository_path: str,
        repair: dict,
    ) -> dict:
        """Apply a repair to the target file."""

        repository = Path(repository_path).resolve()

        target_file = (
            repository / repair["file"]
        ).resolve()

        try:
            target_file.relative_to(repository)

        except ValueError:
            return {
                "success": False,
                "error": "Target file is outside the repository.",
            }

        if not target_file.exists():
            return {
                "success": False,
                "error": "Target file does not exist.",
            }

        content = target_file.read_text(
            encoding="utf-8"
        )

        original = repair["original"]
        replacement = repair["replacement"]

        occurrences = content.count(original)

        if occurrences != 1:
            return {
                "success": False,
                "error": (
                    "Expected exactly one occurrence "
                    f"but found {occurrences}."
                ),
            }

        updated_content = content.replace(
            original,
            replacement,
            1,
        )

        target_file.write_text(
            updated_content,
            encoding="utf-8",
        )

        return {
            "success": True,
            "file": str(target_file),
            "occurrences": 1,
        }