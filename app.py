from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict

from core.flow import handle_message
from core.scam_intent import _detector_instance
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os
from core.sessions import sessions
from core.extractor import extract_all
from fastapi.middleware.cors import CORSMiddleware

API_KEY = os.getenv("HONEYPOT_API_KEY", "")


app = FastAPI(title="PhishBack - Agentic Honeypot")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    print("INCOMING:", request.method, request.url)
    response = await call_next(request)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    print("\n--- DEBUG: INCOMING FAILURE ---")
    print(f"URL: {request.url}")
    print(f"Body received: {body.decode('utf-8')}")
    print("Validation Errors:")
    print(json.dumps(exc.errors(), indent=2))
    print("-------------------------------\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode('utf-8')},
    )


# ─── Pydantic Models ────────────────────────────────────────────

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

    class Config:
        extra = "allow"


class ConversationItem(BaseModel):
    sender: str
    text: str
    timestamp: int

    class Config:
        extra = "allow"


class Metadata(BaseModel):
    channel: Optional[str]
    language: Optional[str]
    locale: Optional[str]

    class Config:
        extra = "allow"


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[ConversationItem]] = None
    metadata: Optional[Metadata] = None

    class Config:
        extra = "allow"
        allow_population_by_field_name = True


class HoneypotResponse(BaseModel):
    status: str
    reply: str

    class Config:
        extra = "allow"


class ChatRequest(BaseModel):
    sessionId: str
    message: str


# ─── Frontend Routes ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the demo frontend"""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ─── Demo Chat API (no API key required) ─────────────────────────

@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    """Simplified chat endpoint for the frontend demo"""
    try:
        session_id = payload.sessionId
        message_text = payload.message

        # Get scam probability before processing
        scam_probability = _detector_instance.get_probability(message_text)

        # Process through the main flow
        reply, stop_flag = handle_message(session_id, message_text)

        # Get session state for extracted intel
        session = sessions.get(session_id)
        extracted = session.extracted if session else {}
        scam_detected = session.scamDetected if session else False

        print(f"SESSION: {session_id}")
        print(f"SCAM: {scam_detected} (prob: {scam_probability:.2%})")
        print(f"STOP: {stop_flag}")
        print(f"EXTRACTED: {extracted}")

        return {
            "reply": reply,
            "scamDetected": scam_detected,
            "scamProbability": scam_probability,
            "stopFlag": stop_flag,
            "extracted": extracted
        }

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ─── Original API Endpoint (with API key) ────────────────────────

@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    payload: HoneypotRequest,
    x_api_key: str = Header(...)
):
    print("REQUEST RECEIVED")

    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = payload.sessionId
    incoming_text = payload.message.text

    reply, stop_flag = handle_message(session_id, incoming_text)

    print("SESSION:", session_id)
    print("STOP FLAG:", stop_flag)
    print("EXTRACTED:", sessions[session_id].extracted)

    return {
        "status": "success",
        "reply": reply
    }

@app.post("/honeypot/", response_model=HoneypotResponse, include_in_schema=False)
def honeypot_slash_endpoint(
    payload: HoneypotRequest, 
    x_api_key: str = Header(...)):
    return honeypot_endpoint(payload, x_api_key)