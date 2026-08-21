from pathlib import Path

from app.retrieval.context_builder import ContextBuilder


def test_complete_context_pipeline(tmp_path: Path):
    repository = tmp_path / "repo"
    repository.mkdir()

    utils = repository / "utils.py"
    calculator = repository / "calculator.py"

    utils.write_text(
        """
def calculate_tax(price):
    return price * 0.18


def calculate_discount(price):
    return price * 0.10
""",
        encoding="utf-8",
    )

    calculator.write_text(
        """
from utils import calculate_tax


def calculate_total(price):
    tax = calculate_tax(price)
    return price + tax
""",
        encoding="utf-8",
    )

    builder = ContextBuilder()

    result = builder.build(
        repository_path=str(repository),
        file_path=str(calculator),
        line_number=6,
        error_message="Example calculation error",
    )

    assert result["success"] is True

    # Error information
    assert result["error"]["file"] == str(calculator)
    assert result["error"]["line"] == 6

    # Primary symbol
    assert result["primary_symbol"]["name"] == (
        "calculate_total"
    )

    # Import
    assert len(result["imports"]) == 1

    imported = result["imports"][0]

    assert imported["module"] == "utils"
    assert imported["name"] == "calculate_tax"

    # Related symbol
    assert len(result["related_symbols"]) == 1

    related = result["related_symbols"][0]

    assert related["name"] == "calculate_tax"
    assert related["file"] == str(utils)