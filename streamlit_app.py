import streamlit as st

from medical_chatbot import MedicalSentimentAnalyzer


st.set_page_config(page_title="Medical Sentiment Chatbot", page_icon="+", layout="centered")

analyzer = MedicalSentimentAnalyzer()


def render_metadata(domain_status: str, sentiment: str) -> None:
    st.caption(f"Domain: {domain_status} | Sentiment: {sentiment}")


st.title("Medical Domain Sentiment Analyzer")
st.write(
    "Enter a medical statement or question. The assistant only supports medical-domain input and will ask for clarification when the request is unclear."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello. Share a medical question or statement, and I will classify the sentiment as positive, negative, or neutral.",
            "domain_status": "greeting",
            "sentiment": "neutral",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        render_metadata(message["domain_status"], message["sentiment"])

user_query = st.chat_input("Describe a medical concern, update, or question")

if user_query:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
            "domain_status": "user_input",
            "sentiment": "n/a",
        }
    )

    with st.chat_message("user"):
        st.write(user_query)
        render_metadata("user_input", "n/a")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        result_text = ""
        domain_status = "unclear"
        sentiment = "neutral"

        try:
            for event in analyzer.analyze_stream(user_query):
                if event["type"] == "chunk":
                    result_text += event["content"]
                    response_placeholder.write(result_text)
                elif event["type"] == "result":
                    result = event["result"]
                    result_text = result.assistant_reply
                    domain_status = result.domain_status
                    sentiment = result.sentiment
        except RuntimeError as exc:
            result_text = str(exc)
            response_placeholder.write(result_text)

        if result_text:
            response_placeholder.write(result_text)
        render_metadata(domain_status, sentiment)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result_text,
            "domain_status": domain_status,
            "sentiment": sentiment,
        }
    )