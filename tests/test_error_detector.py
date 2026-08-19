from pathlib import Path

from app.analysis.error_detector import ErrorDetector


def test_valid_python_file(tmp_path: Path):
    file = tmp_path / "valid.py"
    file.write_text(
        "def hello():\n"
        "    print('Hello')\n",
        encoding="utf-8",
    )

    detector = ErrorDetector()
    result = detector.check_file(str(file))

    assert result["success"] is True
    assert result["error_type"] is None


def test_invalid_python_file(tmp_path: Path):
    file = tmp_path / "invalid.py"
    file.write_text(
        "def hello()\n"
        "    print('Hello')\n",
        encoding="utf-8",
    )

    detector = ErrorDetector()
    result = detector.check_file(str(file))

    assert result["success"] is False
    assert result["error_type"] == "SyntaxError"
    assert result["line"] == 1


def test_missing_file():
    detector = ErrorDetector()

    result = detector.check_file("does_not_exist.py")

    assert result["success"] is False
    assert result["error_type"] == "FileNotFoundError"