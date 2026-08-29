from app.patching.patch_applier import PatchApplier


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


def test_apply_patch(tmp_path):

    create_calculator(tmp_path)

    applier = PatchApplier()

    result = applier.apply(
        str(tmp_path),
        valid_repair(),
    )

    assert result["success"] is True

    calculator = (
        tmp_path / "calculator.py"
    )

    content = calculator.read_text(
        encoding="utf-8"
    )

    assert "return a + b" in content
    assert "return a - b" not in content


def test_missing_file(tmp_path):

    applier = PatchApplier()

    repair = valid_repair()

    result = applier.apply(
        str(tmp_path),
        repair,
    )

    assert result["success"] is False
    assert "does not exist" in result["error"]


def test_original_not_found(tmp_path):

    create_calculator(tmp_path)

    applier = PatchApplier()

    repair = valid_repair()

    repair["original"] = "return a * b"

    result = applier.apply(
        str(tmp_path),
        repair,
    )

    assert result["success"] is False
    assert "found 0" in result["error"]


def test_multiple_occurrences(tmp_path):

    calculator = tmp_path / "calculator.py"

    calculator.write_text(
        """def add(a, b):
    return a - b

def subtract(a, b):
    return a - b
""",
        encoding="utf-8",
    )

    applier = PatchApplier()

    result = applier.apply(
        str(tmp_path),
        valid_repair(),
    )

    assert result["success"] is False
    assert "found 2" in result["error"]


def test_path_escape(tmp_path):

    create_calculator(tmp_path)

    applier = PatchApplier()

    repair = valid_repair()

    repair["file"] = "../calculator.py"

    result = applier.apply(
        str(tmp_path),
        repair,
    )

    assert result["success"] is False
    assert "outside the repository" in result["error"]