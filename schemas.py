from dataclasses import dataclass


VALID_DOMAIN_STATUSES = {"medical", "non_medical", "unclear", "greeting"}
VALID_SENTIMENTS = {"positive", "negative", "neutral"}
REPLY_MARKER = "ASSISTANT_REPLY:"


@dataclass(slots=True)
class AnalysisResult:
    domain_status: str
    sentiment: str
    assistant_reply: str

    @classmethod
    def from_payload(cls, payload: dict) -> "AnalysisResult":
        domain_status = str(payload.get("domain_status", "unclear")).strip().lower()
        sentiment = str(payload.get("sentiment", "neutral")).strip().lower()
        assistant_reply = str(payload.get("assistant_reply", "")).strip()

        if domain_status not in VALID_DOMAIN_STATUSES:
            domain_status = "unclear"
        if sentiment not in VALID_SENTIMENTS:
            sentiment = "neutral"
        if not assistant_reply:
            assistant_reply = "Please share a medical question or statement so I can help."

        return cls(
            domain_status=domain_status,
            sentiment=sentiment,
            assistant_reply=assistant_reply,
        )

    @classmethod
    def from_tagged_text(cls, raw_text: str) -> "AnalysisResult":
        domain_status = "unclear"
        sentiment = "neutral"
        assistant_reply = ""

        for line in raw_text.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith("DOMAIN_STATUS:"):
                domain_status = stripped_line.partition(":")[2].strip().lower()
            elif stripped_line.startswith("SENTIMENT:"):
                sentiment = stripped_line.partition(":")[2].strip().lower()

        if REPLY_MARKER in raw_text:
            assistant_reply = raw_text.split(REPLY_MARKER, maxsplit=1)[1].strip()

        return cls.from_payload(
            {
                "domain_status": domain_status,
                "sentiment": sentiment,
                "assistant_reply": assistant_reply,
            }
        )