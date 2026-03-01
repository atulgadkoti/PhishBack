# PhishBack

**An AI-powered agentic honeypot that engages scammers in realistic conversations to waste their time and extract intelligence.**

PhishBack receives incoming scam messages via API, detects scam intent using a TF-IDF + XGBoost ML model, and — when a scam is detected — engages the scammer as a confused, elderly persona ("Rajesh Kumar") powered by Google Gemini LLM. The goal is to extracting valuable intelligence like phishing links, UPI IDs, phone numbers, and bank account numbers.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [License](#license)

---

## How It Works

```
Scammer Message → API → Scam Detection (XGBoost) → LLM Engagement (Gemini) → Reply
                                                          ↓
                                               Extract Intelligence
                                          (Links, UPI, Phone, Bank A/C)
                                                          ↓
                                               Callback with Report
```

1. **Receive** — A scam message hits the `/honeypot` POST endpoint.
2. **Detect** — The TF-IDF + XGBoost classifier scores the message for scam probability.
3. **Engage** — If scam is detected, an LLM agent (Gemini) replies as a confused old man, trying to extract more intel.
4. **Extract** — Regex-based extractors pull out phishing links, UPI IDs, phone numbers, and bank account numbers from every message.
5. **Report** — Once enough intelligence is gathered (or max turns reached), a callback is sent with all extracted data.

---

## Architecture

| Component | File | Role |
|---|---|---|
| **API Server** | `app.py` | FastAPI endpoint, request validation, auth |
| **Flow Controller** | `core/flow.py` | Orchestrates detection → reply → extraction → callback |
| **Scam Detector** | `core/scam_intent.py` | TF-IDF + XGBoost scam classification with keyword fallback |
| **Agent Logic** | `core/agent.py` | Decides which goal/strategy to use based on scammer intent |
| **LLM Agent** | `core/llm_agent.py` | Gemini-powered response generation as "Rajesh Kumar" persona |
| **Extractor** | `core/extractor.py` | Regex extraction of UPI, links, phones, bank accounts |
| **Session Manager** | `core/sessions.py` | Per-session conversation state and extracted intelligence |
| **Callback** | `tools/callback.py` | Sends extracted intelligence report via callback API |
| **ML Models** | `models/` | Serialized TF-IDF vectorizer + XGBoost classifier (`.pkl`) |

---

## Tech Stack

- **Framework:** FastAPI
- **LLM:** Google Gemini 1.5 Flash (via `google-genai`)
- **ML:** XGBoost + TF-IDF (scikit-learn, joblib)
- **Language:** Python 3.10+
- **Deployment:** Vercel (serverless)

---

## Project Structure

```
PhishBack-main/
├── app.py                  # FastAPI application & routes
├── vercel.json             # Vercel deployment config
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
└── tools/
    └── callback.py         # Intelligence report callback
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Gemini API key
- A honeypot API key (any secret string for auth)

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
export HONEYPOT_API_KEY="your-secret-api-key"
export LLM_API_KEY="your-google-gemini-api-key"

# Windows (PowerShell)
$env:HONEYPOT_API_KEY = "your-secret-api-key"
$env:LLM_API_KEY = "your-google-gemini-api-key"
```

### Run Locally

```bash
uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

---

## API Reference

### `POST /honeypot`

Receive and respond to a scam message.

**Headers:**

| Header | Type | Required | Description |
|---|---|---|---|
| `x-api-key` | `string` | Yes | API key for authentication |

**Request Body:**

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Dear customer, your account has been blocked. Click here to verify.",
    "timestamp": 1709312400
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Previous message...",
      "timestamp": 1709312300
    }
  ],
  "metadata": {
    "channel": "sms",
    "language": "en",
    "locale": "IN"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "reply": "hmm wat is this? y my account blocked? is this real sir? i'm scared"
}
```

**Status Codes:**

| Code | Description |
|---|---|
| `200` | Success — reply generated |
| `401` | Invalid API key |
| `422` | Request validation error |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HONEYPOT_API_KEY` | Yes | Secret key to authenticate incoming API requests |
| `LLM_API_KEY` | Yes | Google Gemini API key for LLM response generation |

---

## Deployment

### Vercel

The project includes a `vercel.json` for one-click deployment:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Make sure to set the environment variables in your Vercel project settings.

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
