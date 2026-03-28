# Medical Domain Sentiment Chatbot

This project is a Streamlit chatbot that uses local Ollama inference with `gpt-oss-safeguard:20b` to:

- accept a user medical query
- classify sentiment as `positive`, `negative`, or `neutral`
- reject non-medical queries
- ask for clarification when the query is too vague
- stream the assistant reply into the UI for lower perceived latency

The project does not use LangChain or any other orchestration framework.

## Features

- Ollama-based local inference through Python `urllib`
- Medical-domain gating through prompt rules
- Streaming assistant output in Streamlit chat UI
- Modular Python structure for client, analyzer, prompts, and schema parsing
- Greeting handling for simple inputs like `hi` or `hello`

## Project Structure

```text
assignment_1/
|-- medical_chatbot/
|   |-- __init__.py
|   |-- analyzer.py
|   |-- config.py
|   |-- ollama_client.py
|   |-- prompts.py
|   |-- schemas.py
|-- hello_ollama.py
|-- requirements.txt
|-- setup.ps1
|-- streamlit_app.py
```

## Prerequisites

Install these before running the app:

1. Python 3.11+ or newer
2. Ollama installed and running locally
3. The Ollama model `gpt-oss-safeguard:20b` available locally

Check the model with:

```powershell
ollama list
```

If the model is missing, pull it with:

```powershell
ollama pull gpt-oss-safeguard:20b
```

## Setup

Run the setup script from the project root:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\setup.ps1
```

What the setup script does:

1. creates `.venv` if it does not exist
2. upgrades `pip`
3. installs dependencies from `requirements.txt`
4. verifies the required Ollama model exists locally

## Run the App

Start the Streamlit chatbot with:

```powershell
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

By default, Streamlit prints a local URL such as:

```text
http://localhost:8501
```

## How It Works

1. The Streamlit UI collects a user query.
2. The analyzer sends the query to Ollama.
3. The prompt instructs the model to return tagged output containing:
   - `DOMAIN_STATUS`
   - `SENTIMENT`
   - `ASSISTANT_REPLY`
4. The assistant reply is streamed into the UI as tokens arrive.
5. The final result is parsed and shown with domain and sentiment metadata.

## Supported Behaviors

### Medical query

The app analyzes the input and returns:

- `positive`
- `negative`
- `neutral`

### Greeting

Example inputs:

- `hi`
- `hello`
- `good morning`

Expected behavior:

- sentiment is `neutral`
- domain status is `greeting`
- assistant asks for a medical query

### Non-medical query

Example input:

- `What is the best laptop for coding?`

Expected behavior:

- sentiment is `neutral`
- domain status is `non_medical`
- assistant refuses and asks for a medical-domain query

### Unclear query

Example input:

- `I am not feeling right.`

Expected behavior:

- sentiment is `neutral`
- domain status is `unclear`
- assistant asks for clarification

## Example Test Inputs

### Positive

1. I am feeling much better after taking the prescribed medicine, and my fever is gone.
2. My blood sugar levels have improved a lot since I started following the diet plan.
3. The surgery went well, and I am recovering comfortably without much pain.

### Negative

1. I have had severe chest pain since last night, and it keeps getting worse.
2. The new medication is making me nauseous and dizzy all day.
3. My wound looks swollen and painful, and I think it may be infected.

### Neutral

1. I have a headache and mild cough for the last two days.
2. My doctor asked me to do a blood test next week for further evaluation.
3. I am taking tablets for blood pressure every morning.

## Key Files

- [streamlit_app.py](streamlit_app.py): Streamlit chat interface
- [medical_chatbot/analyzer.py](medical_chatbot/analyzer.py): Main sentiment analysis workflow
- [medical_chatbot/ollama_client.py](medical_chatbot/ollama_client.py): Ollama HTTP client with streaming support
- [medical_chatbot/prompts.py](medical_chatbot/prompts.py): Prompt rules for domain restriction and sentiment output
- [medical_chatbot/schemas.py](medical_chatbot/schemas.py): Parsing and validation of model output

## Notes

- Streaming improves perceived latency by showing the reply as it is generated.
- First-token latency can still be high if the `gpt-oss-safeguard:20b` model is cold.
- This project is intended for informational sentiment analysis and query routing, not medical diagnosis.

## Troubleshooting

### `No module named streamlit`

Run:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### `Could not reach Ollama`

Make sure Ollama is running locally and the API is available at:

```text
http://localhost:11434
```

### Port already in use

Start Streamlit on another port:

```powershell
.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8502
```