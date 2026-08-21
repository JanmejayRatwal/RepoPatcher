from app.llm.ollama_controller import OllamaController
from app.llm.prompt_builder import PromptBuilder
from app.llm.response_parser import ResponseParser


class LLMAnalysisService:
    """Coordinate context preparation and local LLM analysis."""

    def __init__(
        self,
        controller: OllamaController | None = None,
    ):
        self.controller = (
            controller
            if controller is not None
            else OllamaController()
        )

        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()

    def analyze(self, context: dict) -> dict:
        """Analyse structured repository context."""

        prompt = (
            self.prompt_builder
            .build_error_analysis_prompt(context)
        )

        response = self.controller.analyze_context(
            prompt
        )

        if not response["success"]:
            return {
                "success": False,
                "stage": "ollama",
                "error": response["error"],
            }

        parsed = self.response_parser.parse(
            response["response"]
        )

        if not parsed["success"]:
            return {
                "success": False,
                "stage": "response_parser",
                "error": parsed["error"],
                "raw_response": response["response"],
            }

        return {
            "success": True,
            "analysis": parsed["data"],
            "model": response["model"],
        }