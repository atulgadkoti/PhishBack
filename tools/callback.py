import requests
import time


GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def generate_agent_notes(session) -> str:
    """Generate intelligent notes about the scammer's tactics"""
    notes = []
    extracted = session.extracted
    
    # Analyze what was extracted
    if len(extracted.get("phishingLinks", [])) > 0:
        notes.append(f"Shared {len(extracted['phishingLinks'])} phishing link(s)")
    
    if len(extracted.get("upiIds", [])) > 0:
        notes.append(f"Provided {len(extracted['upiIds'])} UPI ID(s) for fraudulent payments")
    
    if len(extracted.get("phoneNumbers", [])) > 0:
        notes.append(f"Shared {len(extracted['phoneNumbers'])} phone number(s)")
    
    if len(extracted.get("bankAccounts", [])) > 0:
        notes.append(f"Mentioned {len(extracted['bankAccounts'])} bank account(s)")
    
    # Analyze conversation pattern
    if session.turns < 5:
        notes.append("Short conversation - scammer gave up quickly")
    elif session.turns > 15:
        notes.append("Extended engagement - scammer was persistent")
    
    # Check for suspicious keywords
    if len(extracted.get("suspiciousKeywords", [])) > 0:
        keywords = ", ".join(extracted["suspiciousKeywords"][:5])
        notes.append(f"Used urgency tactics: {keywords}")
    
    # Analyze message patterns
    if len(session.messages) > 0:
        scammer_msgs = [msg["content"] for msg in session.messages if msg["role"] == "assistant"]
        if scammer_msgs:
            avg_length = sum(len(msg.split()) for msg in scammer_msgs) / len(scammer_msgs)
            if avg_length > 20:
                notes.append("Verbose messaging style - detailed social engineering")
            elif avg_length < 5:
                notes.append("Brief messages - aggressive/impatient approach")
    
    return "; ".join(notes) if notes else "Scammer interaction detected and logged"


def send_guvi_callback(session):

    payload = {
        "sessionId": session.session_id,
        "scamDetected": True,
        "totalMessagesExchanged": session.turns,
        "extractedIntelligence": session.extracted,
        "agentNotes": generate_agent_notes(session)
    }

    for attempt in range(3):  
        try:
            response = requests.post(
                GUVI_CALLBACK_URL,
                json=payload,
                timeout=5
            )

            print("GUVI CALLBACK STATUS:", response.status_code)
            print("GUVI RESPONSE:", response.text)

            if response.status_code == 200:
                session.callback_sent = True
                return 

        except Exception as e:
            print("GUVI CALLBACK ERROR:", str(e))

        time.sleep(2)  

    print("GUVI CALLBACK FAILED AFTER RETRIES")
