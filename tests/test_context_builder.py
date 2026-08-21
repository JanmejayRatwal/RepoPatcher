from pathlib import Path

from app.retrieval.context_builder import ContextBuilder


def test_build_context(tmp_path: Path):
    repository = tmp_path / "repo"
    repository.mkdir()

    calculator = repository / "calculator.py"
    utils = repository / "utils.py"

    calculator.write_text(
        """
from utils import calculate_tax


def calculate_total(price):
    tax = calculate_tax(price)
    return price + tax
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

    builder = ContextBuilder()

    result = builder.build(
        repository_path=str(repository),
        file_path=str(calculator),
        line_number=6,
        error_message="Example error",
    )

    assert result["success"] is True

    assert result["primary_symbol"]["name"] == (
        "calculate_total"
    )

    assert len(result["imports"]) == 1

    assert (
        result["imports"][0]["name"]
        == "calculate_tax"
    )

    assert len(result["related_symbols"]) == 1

    assert (
        result["related_symbols"][0]["name"]
        == "calculate_tax"
    )