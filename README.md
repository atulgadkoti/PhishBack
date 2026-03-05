# PhishBack

**An AI-powered scam engagement tool that detects scam messages and responds with a realistic persona to waste scammers' time and extract intelligence.**

PhishBack provides a web-based interface where users can send scammer messages. The system detects scam intent using a TF-IDF + XGBoost ML model and — when a scam is detected — engages with a confused, elderly persona ("Rajesh Kumar") powered by Google Gemini LLM. It extracts valuable intelligence like phishing links, UPI IDs, phone numbers, and bank account numbers from the conversation.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [How the Agent Works](#how-the-agent-works)
- [License](#license)

---

## How It Works

```
Scammer Message → Frontend → /api/chat → Scam Detection (XGBoost) → LLM Engagement (Gemini) → Reply
                                                                            ↓
                                                                 Extract Intelligence
                                                            (Links, UPI, Phone, Bank A/C)
```

1. **Input** — A scam message is entered on the frontend web interface.
2. **Detect** — The TF-IDF + XGBoost classifier scores the message for scam probability.
3. **Engage** — If scam is detected, an LLM agent (Gemini) replies as a confused old man, trying to extract more intel.
4. **Extract** — Regex-based extractors pull out phishing links, UPI IDs, phone numbers, and bank account numbers from every message.
5. **Display** — The agent's reply, threat assessment, and extracted intelligence are shown on the frontend in real time.

---

## Architecture

| Component | File | Role |
|---|---|---|
| **API Server** | `app.py` | FastAPI server, serves frontend & chat API |
| **Flow Controller** | `core/flow.py` | Orchestrates detection → reply → extraction |
| **Scam Detector** | `core/scam_intent.py` | TF-IDF + XGBoost scam classification with keyword fallback |
| **Agent Logic** | `core/agent.py` | Decides which goal/strategy to use based on scammer intent |
| **LLM Agent** | `core/llm_agent.py` | Gemini-powered response generation as "Rajesh Kumar" persona |
| **Extractor** | `core/extractor.py` | Regex extraction of UPI, links, phones, bank accounts |
| **Session Manager** | `core/sessions.py` | Per-session conversation state and extracted intelligence |
| **ML Models** | `models/` | Serialized TF-IDF vectorizer + XGBoost classifier (`.pkl`) |
| **Frontend** | `templates/index.html` | Web UI for interacting with the agent |

---

## Tech Stack

- **Framework:** FastAPI
- **LLM:** Google Gemini 2.5 Flash (via `google-genai`)
- **ML:** XGBoost + TF-IDF (scikit-learn, joblib)
- **Language:** Python 3.11+
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render

---

## Project Structure

```
PhishBack-main/
├── app.py                  # FastAPI application & routes
├── render.yaml             # Render deployment config
├── requirement.txt         # Python dependencies
├── core/
│   ├── flow.py             # Main message handling flow
│   ├── scam_intent.py      # ML-based scam detection
│   ├── agent.py            # Strategic reply decision engine
│   ├── llm_agent.py        # Gemini LLM integration & persona
│   ├── extractor.py        # Regex-based intelligence extraction
│   ├── sessions.py         # Session state management
│   └── testing.py          # Testing utilities
├── models/
│   ├── tfidf_vectorizer.pkl
│   └── xgb_scam_classifier.pkl
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── style.css           # Frontend styles
├── templates/
│   └── index.html          # Frontend UI
└── tools/
    └── callback.py         # Intelligence report callback
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/PhishBack.git
cd PhishBack

# Install dependencies
pip install -r requirement.txt
```

### Set Environment Variables

```bash
# Linux/Mac
export LLM_API_KEY="your-google-gemini-api-key"

# Windows (PowerShell)
$env:LLM_API_KEY = "your-google-gemini-api-key"
```

### Run Locally

```bash
uvicorn app:app --reload --port 8000
```

Open `http://localhost:8000` in your browser to access the frontend. Type scam messages to test the detection and AI engagement.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `LLM_API_KEY` | Yes | Google Gemini API key for LLM response generation |

---

## Deployment

### Render

The project includes a `render.yaml` for deployment on Render:

1. Push your code to a GitHub repository.
2. Connect the repo to [Render](https://render.com).
3. Render will auto-detect the `render.yaml` config and set up the service.
4. Set the `LLM_API_KEY` environment variable in your Render dashboard.

The service runs with:

```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## How the Agent Works

The agent persona **Rajesh Kumar** is a 54-year-old confused, scared, tech-illiterate man from Delhi. The agent strategically:

- **Stalls** — buys time with confusion and hesitation
- **Asks for links** — tries to get phishing URLs from the scammer
- **Asks for UPI** — extracts payment identifiers
- **Asks for phone numbers** — gets scammer contact info
- **Fakes failures** — "link not opening sir", "payment not going" to keep the scammer hooked
- **Uses Hinglish** — mixes Hindi and English naturally with typos and bad grammar

The session ends when **2+ intelligence types** are extracted or **20 turns** are reached.

---

## License

MIT License

Copyright (c) 2026 PhishBack Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

