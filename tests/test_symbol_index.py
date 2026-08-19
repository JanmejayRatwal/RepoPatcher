from pathlib import Path

from app.retrieval.symbol_index import SymbolIndex


def test_build_symbol_index(tmp_path: Path):
    repository = tmp_path / "repo"

    repository.mkdir()

    utils = repository / "utils.py"

    utils.write_text(
        """
def calculate_tax(price):
    return price * 0.18


def calculate_discount(price):
    return price * 0.10


class Calculator:
    pass
""",
        encoding="utf-8",
    )

    index = SymbolIndex()

    result = index.build(str(repository))

    assert result["success"] is True

    names = {
        symbol["name"]
        for symbol in result["symbols"]
    }

    assert "calculate_tax" in names
    assert "calculate_discount" in names
    assert "Calculator" in names