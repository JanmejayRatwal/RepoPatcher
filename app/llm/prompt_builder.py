import json


class PromptBuilder:
    """Build prompts for the local coding LLM."""

    def build_error_analysis_prompt(
        self,
        context: dict,
    ) -> str:
        """Build a prompt for analysing a repository error."""

        context_json = json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        )

        return f"""
            You are the local analysis controller for RepoPatcher.

            Your task is to analyse a software error using ONLY
            the repository context provided below.

            Do not modify code.
            Do not invent files or code that are not present
            in the provided context.

            Determine:

            1. What the error is.
            2. Which part of the code is most likely responsible.
            3. Whether related imported code may be involved.
            4. What additional information would be useful before
               attempting a repair.
            qwen2.5-coder:14b 
            Do not generate a final patch yet.
            
            Repository context:
            
            ```json
            {context_json}
            Return ONLY valid JSON.
           
           Use exactly this structure:
           
           {{
             "analysis": "concise explanation of the error",
             "suspected_cause": "most likely cause",
             "confidence": 0.0,
             "relevant_symbols": [],
             "repair_requirements": []
           }}
           
           Rules:
           
           - confidence must be a number between 0 and 1.
           - relevant_symbols must be a JSON array.
           - repair_requirements must be a JSON array.
           - Do not include Markdown.
           - Do not include ```json.
           - Do not generate a patch.
           - Do not invent repository information.
            """.strip()