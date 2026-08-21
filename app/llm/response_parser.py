import json


class ResponseParser:
    """Parse structured responses returned by the local LLM."""

    REQUIRED_FIELDS = {
        "analysis",
        "suspected_cause",
        "confidence",
        "relevant_symbols",
        "repair_requirements",
    }

    def parse(self, response: str) -> dict:
        """Parse and validate an LLM JSON response."""

        try:
            data = json.loads(response)

        except json.JSONDecodeError as error:
            return {
                "success": False,
                "error": f"Invalid JSON response: {error}",
            }

        if not isinstance(data, dict):
            return {
                "success": False,
                "error": "LLM response must be a JSON object.",
            }

        missing = self.REQUIRED_FIELDS - data.keys()

        if missing:
            return {
                "success": False,
                "error": (
                    "Missing required fields: "
                    + ", ".join(sorted(missing))
                ),
            }

        if not isinstance(data["analysis"], str):
            return {
                "success": False,
                "error": "analysis must be a string.",
            }

        if not isinstance(data["suspected_cause"], str):
            return {
                "success": False,
                "error": "suspected_cause must be a string.",
            }

        if not isinstance(data["confidence"], (int, float)):
            return {
                "success": False,
                "error": "confidence must be numeric.",
            }

        if not 0 <= data["confidence"] <= 1:
            return {
                "success": False,
                "error": "confidence must be between 0 and 1.",
            }

        if not isinstance(data["relevant_symbols"], list):
            return {
                "success": False,
                "error": "relevant_symbols must be a list.",
            }

        if not isinstance(data["repair_requirements"], list):
            return {
                "success": False,
                "error": "repair_requirements must be a list.",
            }

        return {
            "success": True,
            "data": data,
        }