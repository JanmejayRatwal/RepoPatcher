from pathlib import Path

from app.repository.scanner import RepositoryScanner


def create_sample_repository(tmp_path: Path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    (repository / "valid.py").write_text(
        "def hello():\n"
        "    print('Hello')\n",
        encoding="utf-8",
    )

    (repository / "broken.py").write_text(
        "def hello()\n"
        "    print('Hello')\n",
        encoding="utf-8",
    )

    return repository


def test_python_file_discovery(tmp_path: Path):
    repository = create_sample_repository(tmp_path)

    scanner = RepositoryScanner()

    files = scanner.discover_python_files(str(repository))

    filenames = {file.name for file in files}

    assert filenames == {
        "valid.py",
        "broken.py",
    }


def test_repository_scan(tmp_path: Path):
    repository = create_sample_repository(tmp_path)

    scanner = RepositoryScanner()

    result = scanner.scan(str(repository))

    assert result["files_scanned"] == 2
    assert result["errors_found"] == 1


def test_ignored_directories(tmp_path: Path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    (repository / "valid.py").write_text(
        "print('valid')",
        encoding="utf-8",
    )

    venv = repository / ".venv"
    venv.mkdir()

    (venv / "ignored.py").write_text(
        "def broken()\n",
        encoding="utf-8",
    )

    scanner = RepositoryScanner()

    files = scanner.discover_python_files(str(repository))

    filenames = {file.name for file in files}

    assert "valid.py" in filenames
    assert "ignored.py" not in filenames