from pathlib import Path

from app.retrieval.import_resolver import ImportResolver


def test_resolve_module(tmp_path: Path):
    repository = tmp_path / "repo"
    repository.mkdir()

    calculator = repository / "calculator.py"
    utils = repository / "utils.py"

    calculator.write_text(
        """
from utils import calculate_tax

def calculate_total(price):
    return price + calculate_tax(price)
""",
        encoding="utf-8",
    )

    utils.write_text(
        """
def calculate_tax(price):
    return price * 0.18
""",
        encoding="utf-8",
    )

    resolver = ImportResolver()

    result = resolver.resolve(
        str(repository),
        str(calculator),
        "utils",
        "calculate_tax",
    )

    assert len(result) == 1

    assert result[0]["module"] == "utils"
    assert result[0]["symbol"] == "calculate_tax"
    assert result[0]["file"].endswith("utils.py")


def test_unresolved_module(tmp_path: Path):
    repository = tmp_path / "repo"
    repository.mkdir()

    resolver = ImportResolver()

    result = resolver.resolve(
        str(repository),
        str(repository / "main.py"),
        "does_not_exist",
        "something",
    )

    assert result == []