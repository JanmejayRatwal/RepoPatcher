from pathlib import Path

from app.retrieval.import_analyzer import ImportAnalyzer


def test_analyze_imports(tmp_path: Path):
    file = tmp_path / "calculator.py"

    file.write_text(
        """
import math
from utils import calculate_tax
from database import UserRepository
""",
        encoding="utf-8",
    )

    analyzer = ImportAnalyzer()

    result = analyzer.analyze(str(file))

    assert result["success"] is True

    imports = result["imports"]

    assert {
        "type": "import",
        "module": "math",
        "name": None,
        "alias": None,
    } in imports

    assert {
        "type": "from_import",
        "module": "utils",
        "name": "calculate_tax",
        "alias": None,
    } in imports

    assert {
        "type": "from_import",
        "module": "database",
        "name": "UserRepository",
        "alias": None,
    } in imports


def test_import_alias(tmp_path: Path):
    file = tmp_path / "calculator.py"

    file.write_text(
        """
from utils import calculate_tax as tax
""",
        encoding="utf-8",
    )

    analyzer = ImportAnalyzer()

    result = analyzer.analyze(str(file))

    assert result["success"] is True

    assert result["imports"][0]["name"] == "calculate_tax"
    assert result["imports"][0]["alias"] == "tax"