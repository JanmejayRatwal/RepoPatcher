from app.llm.ollama_controller import OllamaController
from app.llm.prompt_builder import PromptBuilder


def test_llm_pipeline():
    context = {
        "error": {
            "file": "calculator.py",
            "line": 5,
            "message": "Incorrect calculation",
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
        "imports": [],
        "related_symbols": [],
    }

    builder = PromptBuilder()

    prompt = builder.build_error_analysis_prompt(
        context
    )

    controller = OllamaController()

    controller.generate = lambda prompt: {
        "success": True,
        "response": "The add function appears incorrect.",
        "model": controller.model,
    }

    result = controller.analyze_context(prompt)

    assert result["success"] is True
    assert "incorrect" in result["response"].lower()
    assert result["model"] == "qwen2.5-coder:14b"