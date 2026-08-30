import json
import re


class ResponseParser:
    """Parse and validate structured responses returned by the local LLM."""

    REQUIRED_FIELDS = {
        "analysis",
        "suspected_cause",
        "confidence",
        "relevant_symbols",
        "repair_requirements",
    }

    def parse(self, response: str) -> dict:
        """Parse and validate an LLM JSON response."""

        # --------------------------------------------------
        # 1. Basic response validation
        # --------------------------------------------------

        if not isinstance(response, str):
            return {
                "success": False,
                "error": "LLM response must be a string.",
            }

        cleaned = response.strip()

        if not cleaned:
            return {
                "success": False,
                "error": "LLM response is empty.",
            }

        # --------------------------------------------------
        # 2. Remove Markdown code fences
        # --------------------------------------------------

        # Handles:
        #
        # ```json
        # {...}
        # ```
        #
        # and:
        #
        # ```
        # {...}
        # ```

        cleaned = re.sub(
            r"^\s*```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```\s*$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        # --------------------------------------------------
        # 3. Parse JSON
        # --------------------------------------------------

        try:
            data = json.loads(cleaned)

        except json.JSONDecodeError as error:

            # --------------------------------------------------
            # 4. Attempt to recover JSON embedded in text
            # --------------------------------------------------

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start == -1 or end == -1 or end <= start:
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {error}",
                    "raw_response": response,
                }

            json_candidate = cleaned[start:end + 1]

            try:
                data = json.loads(json_candidate)

            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Invalid JSON response: {error}",
                    "raw_response": response,
                }

        # --------------------------------------------------
        # 5. Validate root object
        # --------------------------------------------------

        if not isinstance(data, dict):
            return {
                "success": False,
                "error": "LLM response must be a JSON object.",
            }

        # --------------------------------------------------
        # 6. Validate required fields
        # --------------------------------------------------

        missing = self.REQUIRED_FIELDS - data.keys()

        if missing:
            return {
                "success": False,
                "error": (
                    "Missing required fields: "
                    + ", ".join(sorted(missing))
                ),
            }

        # --------------------------------------------------
        # 7. Validate analysis
        # --------------------------------------------------

        if not isinstance(data["analysis"], str):
            return {
                "success": False,
                "error": "analysis must be a string.",
            }

        # --------------------------------------------------
        # 8. Validate suspected cause
        # --------------------------------------------------

        if not isinstance(data["suspected_cause"], str):
            return {
                "success": False,
                "error": "suspected_cause must be a string.",
            }

        # --------------------------------------------------
        # 9. Validate confidence
        # --------------------------------------------------

        if (
            isinstance(data["confidence"], bool)
            or not isinstance(
                data["confidence"],
                (int, float),
            )
        ):
            return {
                "success": False,
                "error": "confidence must be numeric.",
            }

        if not 0 <= data["confidence"] <= 1:
            return {
                "success": False,
                "error": "confidence must be between 0 and 1.",
            }

        # --------------------------------------------------
        # 10. Validate relevant symbols
        # --------------------------------------------------

        if not isinstance(data["relevant_symbols"], list):
            return {
                "success": False,
                "error": "relevant_symbols must be a list.",
            }

        # --------------------------------------------------
        # 11. Validate repair requirements
        # --------------------------------------------------

        if not isinstance(
            data["repair_requirements"],
            list,
        ):
            return {
                "success": False,
                "error": "repair_requirements must be a list.",
            }

        # --------------------------------------------------
        # 12. Return validated result
        # --------------------------------------------------

        return {
            "success": True,
            "data": data,
        }