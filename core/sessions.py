class SessionState:
    def __init__(self,session_id):
        self.session_id = session_id
        self.messages = []
        self.extracted = {"bankAccounts": [],
    "upiIds": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": []
}
        self.turns = 0
        self.agent_active = True
        self.scamDetected = False
        self.callback_sent = False

sessions = {}

def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = SessionState(session_id)
    return sessions[session_id]

