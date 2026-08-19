from pathlib import Path

from app.analysis.test_runner import TestRunner


def create_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    tests = repository / "tests"
    tests.mkdir()

    test_file = tests / "test_example.py"

    test_file.write_text(
        """
def test_addition():
    assert 2 + 2 == 4
""",
        encoding="utf-8",
    )

    return repository


def test_tests_pass(tmp_path: Path):
    repository = create_repository(tmp_path)

    runner = TestRunner()

    result = runner.run(str(repository))

    assert result["success"] is True
    assert result["status"] == "passed"
    assert result["exit_code"] == 0


def test_tests_fail(tmp_path: Path):
    repository = tmp_path / "failing_repo"
    repository.mkdir()

    tests = repository / "tests"
    tests.mkdir()

    test_file = tests / "test_failure.py"

    test_file.write_text(
        """
def test_failure():
    assert 2 + 2 == 5
""",
        encoding="utf-8",
    )

    runner = TestRunner()

    result = runner.run(str(repository))

    assert result["success"] is False
    assert result["status"] == "failed"
    assert result["exit_code"] != 0