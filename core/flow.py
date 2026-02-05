from core.extractor import extract_all
from core.sessions import get_session
from core.agent import agent_decide_reply, should_stop
from core.scam_intent import detect_scam_intent
from tools.callback import send_guvi_callback


def update_intelligence(session, extracted):
    for key in session.extracted:
        for item in extracted[key]:
            if item not in session.extracted[key]:
                session.extracted[key].append(item)


def handle_message(session_id, message_text):

    session = get_session(session_id)

    session.turns += 1
    session.messages.append({
    "sender": "scammer",
    "text": message_text
})
    if not session.scamDetected and detect_scam_intent(message_text): #atul bhai aur kshitiz bhai ke liye <3
        session.scamDetected = True

    if not session.scamDetected:
        if not session.callback_sent:
            send_guvi_callback(session, scam_detected=False)
        return None, True  # True = session terminated

    extracted = extract_all(message_text)
    update_intelligence(session, extracted)


    reply = agent_decide_reply(session)
    session.messages.append({
    "sender": "agent",
    "text": reply
})
    print("SESSION STATE:", session.extracted)
    
    stop_flag = should_stop(session)

    if (
        stop_flag
        and session.scamDetected
        and not session.callback_sent
    ):
        send_guvi_callback(session)


    return reply, stop_flag
