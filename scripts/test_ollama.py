from app.llm.ollama_controller import OllamaController
from app.llm.prompt_builder import PromptBuilder
from app.llm.response_parser import ResponseParser


def main():
    context = {
        "error": {
            "file": "calculator.py",
            "line": 2,
            "message": "Test failure: expected 5 but received -1",
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

    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build_error_analysis_prompt(
        context
    )

    controller = OllamaController(
        model="qwen2.5-coder:14b"
    )

    print("\nSending request to Ollama...\n")

    response = controller.analyze_context(prompt)

    if not response["success"]:
        print("Ollama request failed:")
        print(response["error"])
        return

    print("Raw Ollama response:")
    print(response["response"])

    parser = ResponseParser()

    parsed = parser.parse(
        response["response"]
    )

    if not parsed["success"]:
        print("\nResponse validation failed:")
        print(parsed["error"])
        return

    print("\nParsed response:")
    print(parsed["data"])


if __name__ == "__main__":
    main()