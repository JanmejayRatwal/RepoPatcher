from pathlib import Path


class PatchValidator:
    """Validate an LLM-generated repair before applying it."""

    def validate(
        self,
        repository_path: str,
        repair: dict,
    ) -> dict:
        """Validate a proposed repair."""

        required_fields = {
            "file",
            "target",
            "change_type",
            "original",
            "replacement",
            "reason",
        }

        missing = required_fields - repair.keys()

        if missing:
            return {
                "valid": False,
                "error": (
                    "Missing repair fields: "
                    + ", ".join(sorted(missing))
                ),
            }

        repository = Path(repository_path).resolve()

        target_file = (
            repository / repair["file"]
        ).resolve()

        # Prevent paths such as ../../some_file
        try:
            target_file.relative_to(repository)

        except ValueError:
            return {
                "valid": False,
                "error": "Target file is outside the repository.",
            }

        if not target_file.exists():
            return {
                "valid": False,
                "error": "Target file does not exist.",
            }

        if not target_file.is_file():
            return {
                "valid": False,
                "error": "Target path is not a file.",
            }

        original = repair["original"]
        replacement = repair["replacement"]

        if not original:
            return {
                "valid": False,
                "error": "Original code cannot be empty.",
            }

        if original == replacement:
            return {
                "valid": False,
                "error": (
                    "Original and replacement code are identical."
                ),
            }

        content = target_file.read_text(
            encoding="utf-8"
        )

        occurrences = content.count(original)

        if occurrences == 0:
            return {
                "valid": False,
                "error": (
                    "Original code was not found "
                    "in the target file."
                ),
            }

        if occurrences > 1:
            return {
                "valid": False,
                "error": (
                    "Original code occurs multiple times "
                    "in the target file."
                ),
            }

        return {
            "valid": True,
            "file": str(target_file),
            "occurrences": occurrences,
        }