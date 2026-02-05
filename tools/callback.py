import requests
import time

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def generate_agent_notes(session):
    """Generate dynamic agent notes based on extracted intelligence."""
    notes = []
    extracted = session.extracted
    keywords = extracted.get("suspiciousKeywords", [])
    
    # Use the actually extracted suspicious keywords
    if keywords:
        notes.append(f"Suspicious keywords detected: {', '.join(keywords)}")
    
    # Check for payment redirection - include actual UPI IDs
    if extracted.get("upiIds"):
        notes.append(f"Payment redirection via UPI: {', '.join(extracted['upiIds'])}")
    
    # Check for phishing attempts - include actual links
    if extracted.get("phishingLinks"):
        notes.append(f"Phishing links shared: {', '.join(extracted['phishingLinks'])}")
    
    # Check for contact info harvesting - include actual numbers
    if extracted.get("phoneNumbers"):
        notes.append(f"Phone numbers collected: {', '.join(extracted['phoneNumbers'])}")
    
    # Check for banking info - include actual account numbers
    if extracted.get("bankAccounts"):
        notes.append(f"Bank account numbers shared: {', '.join(extracted['bankAccounts'])}")
    
    if not notes:
        notes.append("Scammer engaged in suspicious conversation patterns")
    
    return ". ".join(notes)


def send_guvi_callback(session, scam_detected=True):

    if scam_detected:
        agent_notes = generate_agent_notes(session)
    else:
        agent_notes = "The message appears to be a legitimate personal inquiry. No scam intent found."
    
    extracted_intelligence = {
        "bankAccounts": session.extracted.get("bankAccounts", []),
        "upiIds": session.extracted.get("upiIds", []),
        "phishingLinks": session.extracted.get("phishingLinks", []),
        "phoneNumbers": session.extracted.get("phoneNumbers", []),
        "suspiciousKeywords": session.extracted.get("suspiciousKeywords", [])
    }

    payload = {
        "sessionId": session.session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": session.turns,
        "extractedIntelligence": extracted_intelligence,
        "agentNotes": agent_notes
    }

    print("GUVI CALLBACK PAYLOAD:", payload)

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
