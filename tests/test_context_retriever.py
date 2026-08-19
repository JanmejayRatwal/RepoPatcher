from pathlib import Path

from app.retrieval.context_retriever import ContextRetriever


def test_get_file_context(tmp_path: Path):
    file = tmp_path / "example.py"

    file.write_text(
        "line 1\n"
        "line 2\n"
        "line 3\n"
        "line 4\n"
        "line 5\n",
        encoding="utf-8",
    )

    retriever = ContextRetriever()

    result = retriever.get_file_context(
        str(file),
        line_number=3,
        context_lines=1,
    )

    assert result["success"] is True
    assert result["error_line"] == 3

    assert len(result["context"]) == 3

    assert result["context"][0]["line_number"] == 2
    assert result["context"][1]["line_number"] == 3
    assert result["context"][2]["line_number"] == 4


def test_error_line_is_marked(tmp_path: Path):
    file = tmp_path / "example.py"

    file.write_text(
        "one\n"
        "two\n"
        "three\n",
        encoding="utf-8",
    )

    retriever = ContextRetriever()

    result = retriever.get_file_context(
        str(file),
        line_number=2,
        context_lines=1,
    )

    error_lines = [
        item
        for item in result["context"]
        if item["is_error_line"]
    ]

    assert len(error_lines) == 1
    assert error_lines[0]["line_number"] == 2


def test_invalid_line_number(tmp_path: Path):
    file = tmp_path / "example.py"

    file.write_text(
        "hello\n",
        encoding="utf-8",
    )

    retriever = ContextRetriever()

    result = retriever.get_file_context(
        str(file),
        line_number=10,
    )

    assert result["success"] is False