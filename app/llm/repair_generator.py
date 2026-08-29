from app.llm.ollama_controller import OllamaController
from app.llm.response_parser import ResponseParser


class RepairGenerator:
    """Generate a structured repair proposal using an LLM."""

    REQUIRED_FIELDS = {
        "file",
        "target",
        "change_type",
        "original",
        "replacement",
        "reason",
    }

    def __init__(
        self,
        controller: OllamaController | None = None,
    ):
        self.controller = (
            controller
            if controller is not None
            else OllamaController()
        )

        self.response_parser = ResponseParser()

    def generate(self, context: dict, analysis: dict) -> dict:
        """Generate a repair proposal from repository context and analysis."""

        prompt = self._build_repair_prompt(
            context,
            analysis,
        )

        response = self.controller.analyze_context(prompt)

        if not response["success"]:
            return {
                "success": False,
                "stage": "ollama",
                "error": response["error"],
            }

        parsed = self._parse_repair_response(
            response["response"]
        )

        if not parsed["success"]:
            return parsed

        return {
            "success": True,
            "repair": parsed["data"],
            "model": response["model"],
        }

    def _build_repair_prompt(
        self,
        context: dict,
        analysis: dict,
    ) -> str:
        return f"""
You are the repair-generation component of RepoMedic.

Your task is to propose a minimal repair for the detected
software error.

IMPORTANT RULES:

- Use ONLY the repository context and analysis provided.
- Do not invent files.
- Do not invent functions or variables.
- Do not make unrelated improvements.
- Generate the smallest change that can reasonably fix the error.
- Do not apply the change yourself.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not include ```json.

Repository context:

{context}

Previous analysis:

{analysis}

Return exactly this JSON structure:

{{
  "file": "path/to/file.py",
  "target": "function_or_symbol",
  "change_type": "replace",
  "original": "exact original code",
  "replacement": "exact replacement code",
  "reason": "why this change should fix the error"
}}
""".strip()

    def _parse_repair_response(
        self,
        response: str,
    ) -> dict:

        try:
            import json

            data = json.loads(response)

        except json.JSONDecodeError as error:
            return {
                "success": False,
                "stage": "repair_parser",
                "error": f"Invalid JSON response: {error}",
            }

        if not isinstance(data, dict):
            return {
                "success": False,
                "stage": "repair_parser",
                "error": "Repair response must be a JSON object.",
            }

        missing = self.REQUIRED_FIELDS - data.keys()

        if missing:
            return {
                "success": False,
                "stage": "repair_parser",
                "error": (
                    "Missing required fields: "
                    + ", ".join(sorted(missing))
                ),
            }

        for field in self.REQUIRED_FIELDS:
            if not isinstance(data[field], str):
                return {
                    "success": False,
                    "stage": "repair_parser",
                    "error": (
                        f"{field} must be a string."
                    ),
                }

        return {
            "success": True,
            "data": data,
        }