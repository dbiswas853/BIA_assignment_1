from .ollama_client import OllamaClient
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .schemas import AnalysisResult, REPLY_MARKER


class MedicalSentimentAnalyzer:
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def analyze(self, user_query: str) -> AnalysisResult:
        cleaned_query = user_query.strip()
        if not cleaned_query:
            return AnalysisResult(
                domain_status="unclear",
                sentiment="neutral",
                assistant_reply="Please enter a medical question or statement.",
            )

        raw_response = self.client.generate_text(
            prompt=build_user_prompt(cleaned_query),
            system_prompt=SYSTEM_PROMPT,
        )
        return AnalysisResult.from_tagged_text(raw_response)

    def analyze_stream(self, user_query: str):
        cleaned_query = user_query.strip()
        if not cleaned_query:
            yield {
                "type": "result",
                "result": AnalysisResult(
                    domain_status="unclear",
                    sentiment="neutral",
                    assistant_reply="Please enter a medical question or statement.",
                ),
            }
            return

        raw_response = ""
        emitted_reply_length = 0

        for chunk in self.client.stream_text(
            prompt=build_user_prompt(cleaned_query),
            system_prompt=SYSTEM_PROMPT,
        ):
            raw_response += chunk
            reply_text = self._extract_reply_text(raw_response)

            if len(reply_text) > emitted_reply_length:
                next_chunk = reply_text[emitted_reply_length:]
                emitted_reply_length = len(reply_text)
                yield {"type": "chunk", "content": next_chunk}

        result = AnalysisResult.from_tagged_text(raw_response)

        if emitted_reply_length == 0 and result.assistant_reply:
            yield {"type": "chunk", "content": result.assistant_reply}

        yield {"type": "result", "result": result}

    def _extract_reply_text(self, raw_response: str) -> str:
        if REPLY_MARKER not in raw_response:
            return ""

        return raw_response.split(REPLY_MARKER, maxsplit=1)[1].lstrip()