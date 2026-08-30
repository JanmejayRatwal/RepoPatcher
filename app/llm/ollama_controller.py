import json
import urllib.error
import urllib.request


class OllamaController:
    """Interface with a locally running Ollama model."""
    
    def analyze_context(self,
        prompt: str,
       ) -> dict:
        """Analyse repository context using Ollama."""
        
        return self.generate(prompt)

    def __init__(
        self,
        model: str = "qwen2.5-coder:14b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, prompt: str) -> dict:
        """Send a prompt to the local Ollama API."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{self.host}/api/generate",
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=180,
            ) as response:

                response_data = json.loads(
                    response.read().decode("utf-8")
                )

            return {
                "success": True,
                "response": response_data.get(
                    "response",
                    "",
                ),
                "model": self.model,
            }

        except urllib.error.URLError as error:
            return {
                "success": False,
                "error": f"Ollama connection failed: {error}",
            }

        except TimeoutError:
            return {
                "success": False,
                "error": "Ollama request timed out.",
            }

        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Ollama returned invalid JSON.",
            }
            
            
