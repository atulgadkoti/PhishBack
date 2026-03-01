import re

def extract_upi(text):
    pattern = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
    return re.findall(pattern, text)

def extract_phone(text):
    pattern = r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    return re.findall(pattern, text)

def extract_links(text):
    pattern = r"(https?://[^\s]+|www\.[^\s]+|\b[a-zA-Z0-9-]+\.(?:com|in|net|org|co\.in)\b)"
    return re.findall(pattern, text)

def extract_bank(text):
    pattern = r"\b\d{9,18}\b"
    return re.findall(pattern, text)

SCAM_KEYWORDS = ["urgent", "verify", "blocked", "suspended", "click", "otp"]
def extract_keywords(text):
    found = []
    for k in SCAM_KEYWORDS:
        if k in text.lower():
            found.append(k)
    return list(set(found)) 

def extract_all(text):
    
    phones = extract_phone(text)
    raw_banks = extract_bank(text)
    
    phone_digits_set = set(re.sub(r"\D", "", p)[-10:] for p in phones)


    clean_banks = []
    for bank in raw_banks:
        if bank not in phone_digits_set and len(bank) != 10:
            clean_banks.append(bank)

    return {
        "upiIds": extract_upi(text),
        "phoneNumbers": phones,
        "phishingLinks": extract_links(text),
        "bankAccounts": clean_banks, 
        "suspiciousKeywords": extract_keywords(text)
}