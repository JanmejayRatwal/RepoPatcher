from app.llm.repair_generator import RepairGenerator


class FakeController:

    def analyze_context(self, prompt: str) -> dict:
        return {
            "success": True,
            "model": "fake-model",
            "response": """
{
    "file": "calculator.py",
    "target": "add",
    "change_type": "replace",
    "original": "return a - b",
    "replacement": "return a + b",
    "reason": "The add function must add the two arguments."
}
""",
        }


def test_generate_repair():

    context = {
        "error": {
            "file": "calculator.py",
            "line": 2,
            "message": "Expected 5 but got -1",
        },
        "primary_context": {
            "lines": [
                "def add(a, b):",
                "    return a - b",
            ]
        },
        "primary_symbol": {
            "name": "add",
            "type": "function",
        },
    }

    analysis = {
        "analysis": "The add function is incorrect.",
        "suspected_cause": (
            "The function subtracts instead of adding."
        ),
        "confidence": 0.95,
        "relevant_symbols": ["add"],
        "repair_requirements": [
            "Change subtraction to addition."
        ],
    }

    generator = RepairGenerator(
        controller=FakeController()
    )

    result = generator.generate(
        context,
        analysis,
    )

    assert result["success"] is True

    repair = result["repair"]

    assert repair["file"] == "calculator.py"
    assert repair["target"] == "add"
    assert repair["change_type"] == "replace"
    assert repair["original"] == "return a - b"
    assert repair["replacement"] == "return a + b"