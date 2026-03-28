import json
from urllib import error, request

from .config import MODEL_NAME, OLLAMA_URL, REQUEST_TIMEOUT_SECONDS


class OllamaClient:
    def __init__(self, model_name: str = MODEL_NAME, ollama_url: str = OLLAMA_URL):
        self.model_name = model_name
        self.ollama_url = ollama_url

    def generate_json(self, prompt: str, system_prompt: str) -> dict:
        raw_response = self.generate_text(prompt=prompt, system_prompt=system_prompt)

        try:
            return json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned invalid JSON for the analysis request.") from exc

    def generate_text(self, prompt: str, system_prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.8},
        }
        http_request = self._build_request(payload)

        try:
            with request.urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                result = json.load(response)
        except error.URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama. Make sure the Ollama app or service is running."
            ) from exc

        raw_response = str(result.get("response", "")).strip()
        if not raw_response:
            raise RuntimeError("Ollama returned an empty response.")

        return raw_response

    def stream_text(self, prompt: str, system_prompt: str):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {"temperature": 0.2},
        }
        http_request = self._build_request(payload)

        try:
            with request.urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                for raw_line in response:
                    if not raw_line:
                        continue

                    chunk = json.loads(raw_line.decode("utf-8"))
                    piece = str(chunk.get("response", ""))
                    if piece:
                        yield piece
                    if chunk.get("done"):
                        break
        except error.URLError as exc:
            raise RuntimeError(
                "Could not reach Ollama. Make sure the Ollama app or service is running."
            ) from exc

    def _build_request(self, payload: dict) -> request.Request:
        data = json.dumps(payload).encode("utf-8")
        return request.Request(
            self.ollama_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )