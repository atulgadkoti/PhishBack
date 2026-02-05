import random
import re
from core.llm_agent import llm_generate
from core.extractor import extract_all


def analyze_scammer_intent(last_message: str) -> dict:
    msg_lower = last_message.lower()
    
    intent = {
        "asking_to_click_link": False,
        "asking_for_info": False,
        "providing_link": False,
        "providing_upi": False,
        "providing_phone": False,
        "asking_confirmation": False,
        "threatening": False,
        "requesting_action": False
    }
    
    extracted = extract_all(last_message)
    intent["providing_link"] = len(extracted["phishingLinks"]) > 0
    intent["providing_upi"] = len(extracted["upiIds"]) > 0
    intent["providing_phone"] = len(extracted["phoneNumbers"]) > 0
    
    link_keywords = ["click", "open", "visit", "go to", "check link", "follow link", "tap"]
    intent["asking_to_click_link"] = any(kw in msg_lower for kw in link_keywords)
    
    info_keywords = ["your account", "your number", "your otp", "send otp", "enter", "provide", "share"]
    intent["asking_for_info"] = any(kw in msg_lower for kw in info_keywords)
    
    confirm_keywords = ["did you", "have you", "confirm", "verify", "done", "completed", "received"]
    intent["asking_confirmation"] = any(kw in msg_lower for kw in confirm_keywords)
    
    threat_keywords = ["urgent", "immediately", "blocked", "suspended", "close", "deactivate", "within", "hours"]
    intent["threatening"] = any(kw in msg_lower for kw in threat_keywords)
    
    action_keywords = ["please", "kindly", "request", "need to", "must", "required", "should"]
    intent["requesting_action"] = any(kw in msg_lower for kw in action_keywords)
    
    return intent


def agent_decide_reply(session):
    last_scammer_msg = ""
    if len(session.messages) > 0:
        for msg in reversed(session.messages):
            if msg["role"] == "assistant":
                last_scammer_msg = msg["content"]
                break
    
    scammer_intent = analyze_scammer_intent(last_scammer_msg)
    extracted = session.extracted
    
    has_upi = len(extracted.get("upiIds", [])) > 0
    has_link = len(extracted.get("phishingLinks", [])) > 0
    has_phone = len(extracted.get("phoneNumbers", [])) > 0
    has_bank = len(extracted.get("bankAccounts", [])) > 0
    
    missing = []
    if not has_link:
        missing.append("link")
    if not has_upi:
        missing.append("upi")
    if not has_phone:
        missing.append("phone")
    if not has_bank:
        missing.append("bank")
    
    if scammer_intent["providing_upi"] and has_upi:
        if random.random() < 0.4:
            if "phone" in missing:
                return llm_generate("ask_for_phone", session.messages)
            elif "link" in missing:
                return llm_generate("ask_for_phishing_link", session.messages)
            elif "bank" in missing:
                return llm_generate("ask_for_bank_account", session.messages)
        return llm_generate("upi_not_working", session.messages)
    
    if scammer_intent["providing_link"] and has_link:
        if random.random() < 0.5:
            if "upi" in missing:
                return llm_generate("ask_for_upi", session.messages)
            elif "phone" in missing:
                return llm_generate("ask_for_phone", session.messages)
            elif "bank" in missing:
                return llm_generate("ask_for_bank_account", session.messages)
        return llm_generate("link_not_working", session.messages)
    
    if scammer_intent["providing_phone"] and has_phone:
        if random.random() < 0.5:
            if "link" in missing:
                return llm_generate("ask_for_phishing_link", session.messages)
            elif "upi" in missing:
                return llm_generate("ask_for_upi", session.messages)
            elif "bank" in missing:
                return llm_generate("ask_for_bank_account", session.messages)
        return llm_generate("phone_not_reachable", session.messages)
    
    if scammer_intent["asking_to_click_link"] and has_link:
        return llm_generate("link_not_working", session.messages)
    
    if scammer_intent["asking_confirmation"]:
        if len(missing) > 0 and random.random() < 0.6:
            target = random.choice(missing)
            if target == "link":
                return llm_generate("ask_for_phishing_link", session.messages)
            elif target == "upi":
                return llm_generate("ask_for_upi", session.messages)
            elif target == "phone":
                return llm_generate("ask_for_phone", session.messages)
            elif target == "bank":
                return llm_generate("ask_for_bank_account", session.messages)
        if random.random() < 0.7:
            return llm_generate("stall", session.messages)
        return llm_generate("reassure", session.messages)
    
    if scammer_intent["threatening"]:
        if len(missing) > 0 and random.random() < 0.5:
            target = random.choice(missing)
            if target == "upi":
                return llm_generate("ask_for_upi", session.messages)
            elif target == "phone":
                return llm_generate("ask_for_phone", session.messages)
        return llm_generate("reassure", session.messages)
    
    if scammer_intent["asking_for_info"]:
        if len(missing) > 0 and random.random() < 0.6:
            target = random.choice(missing)
            if target == "phone":
                return llm_generate("ask_for_phone", session.messages)
            elif target == "link":
                return llm_generate("ask_for_phishing_link", session.messages)
            elif target == "upi":
                return llm_generate("ask_for_upi", session.messages)
        return llm_generate("stall", session.messages)
    
    if scammer_intent["requesting_action"]:
        if len(missing) > 0 and random.random() < 0.6:
            target = random.choice(missing)
            if target == "link":
                return llm_generate("ask_for_phishing_link", session.messages)
            elif target == "upi":
                return llm_generate("ask_for_upi", session.messages)
    
    if session.turns < 3:
        return llm_generate("stall", session.messages)
    
    if len(missing) > 0:
        weights = {
            "link": 0.35,
            "upi": 0.30,
            "phone": 0.20,
            "bank": 0.15
        }
        
        available_options = [(item, weights.get(item, 0.25)) for item in missing]
        total_weight = sum(w for _, w in available_options)
        
        rand_val = random.random() * total_weight
        cumulative = 0
        for item, weight in available_options:
            cumulative += weight
            if rand_val <= cumulative:
                if item == "link":
                    return llm_generate("ask_for_phishing_link", session.messages)
                elif item == "upi":
                    return llm_generate("ask_for_upi", session.messages)
                elif item == "phone":
                    return llm_generate("ask_for_phone", session.messages)
                elif item == "bank":
                    return llm_generate("ask_for_bank_account", session.messages)
                break
    
    if random.random() < 0.5:
        return llm_generate("stall", session.messages)
    
    return llm_generate("ask_for_phishing_link", session.messages)


def should_stop(session):
    fields = session.extracted

    score = sum([
        len(fields["upiIds"]) > 0,
        len(fields["phishingLinks"]) > 0,
        len(fields["phoneNumbers"]) > 0,
        len(fields["bankAccounts"]) > 0
    ])

    has_enough_info = score >= 2
    too_many_turns = session.turns >= 20
    
    if len(session.messages) >= 6:
        recent_scammer_msgs = [
            msg["content"] for msg in session.messages[-6:] 
            if msg["role"] == "assistant"
        ]
        if len(recent_scammer_msgs) >= 3:
            avg_length = sum(len(msg.split()) for msg in recent_scammer_msgs) / len(recent_scammer_msgs)
            scammer_giving_up = avg_length < 3
            if scammer_giving_up and score > 0:
                return True
    
    return has_enough_info or too_many_turns

