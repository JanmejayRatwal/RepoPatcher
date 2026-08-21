from app.llm.prompt_builder import PromptBuilder


def test_build_error_analysis_prompt():
    context = {
        "error": {
            "file": "calculator.py",
            "line": 5,
            "message": "Incorrect calculation",
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

    assert "RepoPatcher" in prompt
    assert "calculator.py" in prompt
    assert "Incorrect calculation" in prompt
    assert "Do not generate a final patch yet." in prompt