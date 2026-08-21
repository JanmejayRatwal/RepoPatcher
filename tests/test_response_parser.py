from app.llm.response_parser import ResponseParser


def test_parse_valid_response():
    response = """
{
    "analysis": "The function uses the wrong operator.",
    "suspected_cause": "Subtraction is used instead of addition.",
    "confidence": 0.98,
    "relevant_symbols": ["add"],
    "repair_requirements": [
        "Use addition instead of subtraction."
    ]
}
"""

    parser = ResponseParser()

    result = parser.parse(response)

    assert result["success"] is True

    data = result["data"]

    assert data["analysis"]
    assert data["suspected_cause"]
    assert data["confidence"] == 0.98
    assert data["relevant_symbols"] == ["add"]


def test_parse_invalid_json():
    parser = ResponseParser()

    result = parser.parse(
        "This is not JSON."
    )

    assert result["success"] is False


def test_parse_missing_field():
    parser = ResponseParser()

    response = """
{
    "analysis": "Something is wrong.",
    "suspected_cause": "Unknown",
    "confidence": 0.5,
    "relevant_symbols": []
}
"""

    result = parser.parse(response)

    assert result["success"] is False
    assert "repair_requirements" in result["error"]


def test_confidence_out_of_range():
    parser = ResponseParser()

    response = """
  {
    "analysis": "Something is wrong.",
    "suspected_cause": "Unknown",
    "confidence": 2.0,
    "relevant_symbols": [],
    "repair_requirements": []
  }
    """

    result = parser.parse(response)

    assert result["success"] is False