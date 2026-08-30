import json


class PromptBuilder:
    """Build prompts for the local coding LLM."""

    def build_error_analysis_prompt(
        self,
        context: dict,
    ) -> str:
        """Build a focused prompt for analysing a repository error."""

        context_json = json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        )

        return f"""You are RepoPatcher's local code analysis controller.

                Analyze the software error using ONLY the repository context below.

                Your job:
                1. Identify the error.
                2. Identify the most likely responsible code.
                3. Consider related imported code.
                4. State what is required before a repair can be generated.
                
                Do NOT:
                - modify code
                - invent files, symbols, or code
                - include Markdown
                - include explanations outside JSON
                
                Do not generate a final patch yet.
                
                Return ONLY valid JSON using exactly this structure:
                
                {{
                  "analysis": "concise explanation of the error",
                  "suspected_cause": "most likely cause",
                  "confidence": 0.0,
                  "relevant_symbols": [],
                  "repair_requirements": []
                }}
                
                Rules:
                - confidence must be between 0 and 1.
                - relevant_symbols must be an array.
                - repair_requirements must be an array.
                - Use only information present in the repository context.
                
                Repository context:
                {context_json}
                """.strip()