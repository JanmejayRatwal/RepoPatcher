from app.llm.analysis_service import LLMAnalysisService


class FakeController:

    def analyze_context(self, prompt: str) -> dict:
        return {
            "success": True,
            "response": """
{
    "analysis": "The add function is incorrect.",
    "suspected_cause": "It subtracts instead of adding.",
    "confidence": 0.95,
    "relevant_symbols": ["add"],
    "repair_requirements": [
        "Change subtraction to addition."
    ]
}
""",
            "model": "fake-model",
        }


def test_analysis_service():
    context = {
        "error": {
            "file": "calculator.py",
            "line": 2,
            "message": "Expected 5 but got -1",
        },
        "primary_context": {},
        "primary_symbol": {
            "name": "add",
            "type": "function",
        },
        "imports": [],
        "related_symbols": [],
    }

    service = LLMAnalysisService(
        controller=FakeController()
    )

    result = service.analyze(context)

    assert result["success"] is True
    assert result["model"] == "fake-model"

    analysis = result["analysis"]

    assert analysis["relevant_symbols"] == ["add"]
    assert analysis["confidence"] == 0.95