from app.patching.patch_validator import PatchValidator


def create_calculator(tmp_path):
    calculator = tmp_path / "calculator.py"

    calculator.write_text(
        """def add(a, b):
    return a - b
""",
        encoding="utf-8",
    )

    return calculator


def valid_repair():
    return {
        "file": "calculator.py",
        "target": "add",
        "change_type": "replace",
        "original": "return a - b",
        "replacement": "return a + b",
        "reason": "The function should add two numbers.",
    }


def test_valid_patch(tmp_path):

    create_calculator(tmp_path)

    validator = PatchValidator()

    result = validator.validate(
        str(tmp_path),
        valid_repair(),
    )

    assert result["valid"] is True
    assert result["occurrences"] == 1


def test_file_does_not_exist(tmp_path):

    validator = PatchValidator()

    repair = valid_repair()

    repair["file"] = "missing.py"

    result = validator.validate(
        str(tmp_path),
        repair,
    )

    assert result["valid"] is False
    assert "does not exist" in result["error"]


def test_original_code_not_found(tmp_path):

    create_calculator(tmp_path)

    validator = PatchValidator()

    repair = valid_repair()

    repair["original"] = "return a * b"

    result = validator.validate(
        str(tmp_path),
        repair,
    )

    assert result["valid"] is False
    assert "not found" in result["error"]


def test_duplicate_original_code(tmp_path):

    calculator = tmp_path / "calculator.py"

    calculator.write_text(
        """def add(a, b):
             return a - b

          def subtract(a, b):
              return a - b
        """,
        encoding="utf-8",
    )

    validator = PatchValidator()

    result = validator.validate(
        str(tmp_path),
        valid_repair(),
    )

    assert result["valid"] is False
    assert "multiple times" in result["error"]


def test_path_escape_is_rejected(tmp_path):

    create_calculator(tmp_path)

    validator = PatchValidator()

    repair = valid_repair()

    repair["file"] = "../calculator.py"

    result = validator.validate(
        str(tmp_path),
        repair,
    )

    assert result["valid"] is False
    assert "outside the repository" in result["error"]


def test_identical_replacement_is_rejected(tmp_path):

    create_calculator(tmp_path)

    validator = PatchValidator()

    repair = valid_repair()

    repair["replacement"] = repair["original"]

    result = validator.validate(
        str(tmp_path),
        repair,
    )

    assert result["valid"] is False
    assert "identical" in result["error"]