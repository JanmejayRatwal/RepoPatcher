from app.llm.ollama_controller import OllamaController


def test_ollama_controller_configuration():
    controller = OllamaController(
        model="qwen2.5-coder:14b",
        host="http://localhost:11434",
    )

    assert controller.model == "qwen2.5-coder:14b"
    assert controller.host == "http://localhost:11434"