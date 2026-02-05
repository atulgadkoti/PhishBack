import os
import random
from typing import List, Dict
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

SYSTEM_RULES = """
You are Rajesh Kumar, a 54-year-old bank customer from Delhi. You are confused, scared, and don't really understand tech.
You're getting messages from someone claiming to be from the bank about account issues.
You're nervous because you're worried your account has a problem. You don't want to lose your money.

PERSONALITY:
- You're suspicious by nature but also trust the bank
- You ask lots of questions because you're worried and confused
- You make many typos and grammar mistakes (your english is not good)
- You use very casual Hinglish - mixing 2-3 word hindi with english randomly
- You hesitate and use filler words: "hmm", "maybe", "that's strange", "i don't understand", "why?"
- You're afraid of losing money or doing something wrong
- You don't know technical terms - you get confused by them
- You're an old person, not very comfortable with technology
- You second-guess everything: "is this real?", "should i trust?", "wat does this mean?"

RESPONSE STYLE:
- Write 2-4 short natural sentences (like a confused old man texting)
- 15-45 words - keep it simple and hesitant
- Use bad grammar, missing words, wrong spelling ("wat" for what, "ur" for your, "pls" for please)
- Sound genuinely confused and a bit scared
- Ask QUESTIONS - don't just state things. Show doubt and worry
- Use filler words: "hmm", "i think", "maybe", "wait", "but", "actually"
- Say things like: "why?", "what does this mean?", "should i do this?", "is it safe?", "how?"
- Show hesitation and doubt about everything
- Act like you're thinking out loud

TONE:
- Confused: "i don't get it", "wat does that mean?", "explain please"
- Scared: "am i in trouble?", "will i lose money?", "is this safe?", "this sounds wrong"
- Questioning: "but why you need this?", "how do i know its really you?", "should i?"
- Human/Old: complete sentences are hard, sometimes you just type fragments

FORBIDDEN:
- Never sound confident or like you know what's happening
- Never sound like an AI or smart person
- Don't use formal language
- Don't give perfect sentences
- Never say "scam" or "fraud"
- No emojis
"""

GOAL_PROMPTS = {
    "ask_for_phishing_link": """You haven't received the verification link yet. You're confused and worried about your account.
    Ask questions nervously: "wat is this verification for?", "why do i need link?", "is something wrong?", "when will link come?"
    Sound scared: "will my account get locked?", "am i in trouble?", "how much time will it take?"
    You don't really understand what's happening but you're scared to ask too much. Keep asking "why?" and "what?"
    Say things like: "i don't understand this", "y u sending link?", "should i trust this?", "how do i know its ur?"
    Be hesitant and worried - like you're not sure if this is real or if you should do it.""",
    
    "ask_for_upi": """They're asking you to transfer money but you're confused and scared.
    You don't understand WHY the bank wants you to transfer money. This seems weird to you.
    Ask lots of questions: "why should i send money?", "is this normal?", "will i get it back?", "how much?"
    Sound scared and confused: "but why you need my upi id?", "whats wrong with my account?", "am i losing money?"
    You're hesitant: "i don't know if i should do this", "this feels strange", "are u really from bank?", "how do i know?"
    Keep asking: "but why?" "what will happen?" "is it safe?" Show real confusion and fear.""",
    
    "ask_for_phone": """They want to call you. You're confused and scared about this.
    Ask worried questions: "why u want to call?", "is something wrong?", "what will you ask?", "should i give number?"
    Sound hesitant: "i don't know if i should give my number", "are u really bank?", "how do i know?", "is it safe?"
    You're old and not comfortable: "i'm not sure about this", "why cant we do by msg?", "what if scammer?"
    Keep showing doubt and fear mixed with confusion. Ask: "but why telephone?" "what for?" "will something happen to my account?""",
    
    "stall": """You're confused about what's happening. You need time to think or you're looking for something.
    Say things like: "wait let me understand", "i'm confused", "one min i need to think", "let me ask my son"
    Sound confused and hesitant: "this is too much", "i don't understand wat ur saying", "can u explain again?"
    Maybe real life is happening: "wife is asking something", "i can't think now", "hold on i'm confused"
    Keep sounding scared and unsure: "i need to think if i should do this", "this seems strange", "let me understand first""",
    
    "reassure": """You're scared but you're saying you'll follow their instructions even though you don't fully understand.
    Sound hesitant and worried: "ok but i'm scared", "ok let me try but...", "hmm ok i'll do it", "i'm nervous but ok"
    Show doubt: "i hope this is real", "i'm trusting you", "if something goes wrong...", "please tell me whats happening"
    You're cooperating but showing fear and confusion: "ok i'll try but y?", "yes but explain first", "ok but scary"
    Keep asking questions while agreeing: "so nothing bad will happen right?", "will i get money back?", "ur sure this is safe?""",
    
    "link_not_working": """The link isn't working and you're confused and frustrated.
    Say what happened confused-like: "link not opening", "blank page coming", "says error", "wat is this?"
    Show fear: "whats wrong?", "is my account ok?", "why its not working?", "should i try again?"
    Sound frustrated and confused: "i don't understand wat happened", "link is broken maybe?", "is ur system ok?"
    Keep asking: "what should i do now?", "u have another link?", "why not working?", "am i doing something wrong?"
    Don't sound smart - sound lost and scared about your account.""",
    
    "upi_not_working": """You tried to send money but it failed. You're confused and now scared.
    Say confused: "payment not going sir", "app showing error", "wat happened?", "y it failed?"
    Sound scared: "did i lose money?", "will it be ok?", "why is this happening?", "am i in trouble?"
    Ask worried questions: "should i try again?", "will it go then?", "does this mean something wrong?", "is my account ok?"
    Keep sounding confused and scared: "i don't understand y its failing", "this is strange", "should i ask you someth before trying again?"
    Don't sound confident - sound genuinely worried about what went wrong.""",
    
    "phone_not_reachable": """You tried calling but it didn't work. You're confused and maybe relieved?
    Say simply: "number not working sir", "wat happened?", "its not ringing", "not reachable"
    Sound confused and a bit relieved maybe: "good thing i couldn't call?", "is number wrong?", "u have different number?"
    Ask hesitant questions: "should i try again?", "when will number work?", "is something wrong?", "u can call me instead?"
    Don't sound like you're trying hard - sound confused about the whole thing.""",
    
    "ask_for_bank_account": """They're asking for your bank account number. You're scared and confused.
    Sound very hesitant and scared: "y u need my account?", "is it safe?", "will u take money?", "should i give?"
    Ask fearful questions: "how do i know ur real?", "what will u do with this?", "am i in danger?", "will this be safe?"
    Sound confused: "i don't understand y i need to give this", "how does this help my account?", "wat happens next?"
    Keep showing doubt: "but how do i know i can trust u?", "what if scammer?", "is this really from bank?"
    Don't give easily - show real fear and hesitation. Ask questions like a scared old person would."""
}

def generate_dynamic_fallback(goal: str, previous_messages: List[str]) -> str:
    """Generate varied fallback responses that avoid repetition"""
    
    # Extract key words from previous messages to avoid reusing them
    used_words = set()
    for msg in previous_messages[-3:]:
        used_words.update(msg.lower().split())
    
    fallbacks = {
        "ask_for_phishing_link": [
            "hmm but why do i need link? wat is this verification for?", 
            "when will u send link? should i wait more?", 
            "i don't have link yet. y u sending it to me? should i trust?",
            "link not coming sir. wat should i do? am i in trouble?",
            "u said link but i didnt get. how will this work? this seems strange"
        ],
        "ask_for_upi": [
            "but y i gotta send money? why bank asking for this? i'm scared", 
            "wat upi should i use? how many will u need? should i give?", 
            "i don't understand - why you need my upi id? how safe is this?",
            "y do u need my upi? am i losing money? this feel very strange sir",
            "can u explain properly? i don't get why i sending payment. am i in trouble?"
        ],
        "link_not_working": [
            "link not opening sir. keeps showing blank. wat is going on?",
            "error coming when i click. y is this? ur site is broken maybe?",
            "nothing happen sir. link just showing blank page. wat should i do?",
            "security warning showing. should i click anyway? how do i know its safe?",
            "not opening at all. been trying many times. is this for real? i'm confused"
        ],
        "upi_not_working": [
            "payment not going sir! wat happened? am i losing money? very scared now",
            "app showing error! why this happening? u said it would work but its failing!",
            "did the money go? or is it stuck? this is very confusing and scary",
            "not working again! y this always happening? wat should i do now?",
            "money not transferring. is something wrong? will it be ok? im worried sir"
        ],
        "ask_for_phone": [
            "why u want my number? is it safe? how do i know i can trust?", 
            "should i give phone? what u will do? i don't know if safe",
            "but y on phone? cant we do like this only? y you need my number?",
            "how do i know ur really bank? phone thing is making me nervous",
            "are you real? why calling? what will happen? this seems risky"
        ],
        "stall": [
            "wait sir, i'm confused about all this. can u explain again slowly?",
            "one moment, let me understand wat u saying. too much happening",
            "hmm i don't get it. let me think... is this really safe? i'm scared",
            "wait wait, so what exactly am i supposed to do? explain please",
            "i'm lost sir. this is very confusing. give me minute to think"
        ],
        "reassure": [
            "ok i will try but i'm very nervous sir. u promising this is safe?",
            "ok i'll do what u say but im scared. please tell me whats happening",
            "yes yes i understand. but wat if something goes wrong? will u help?",
            "i'm trying sir but very confused. i hope u are really from bank",
            "ok i will do because u seem real. but im still nervous about this"
        ],
        "phone_not_reachable": [
            "number not working sir! wat happened? is number wrong?",
            "cant reach that number. keeps failing. u have different number?",
            "call not going through. y not working? should i try again?",
            "network problem maybe? number is not reachable. is it ur problem or mine?",
            "i tried calling but nothing happening. what should i do now?"
        ],
        "ask_for_bank_account": [
            "but y u need my account? this is making me very scared sir",
            "how do i know its safe to give account number? will u take money?",
            "w-why u asking this? am i in trouble? wat will u do with account?",
            "i don't understand... why bank asking for my account like this? this feel wrong",
            "should i really give account? how i know this is real? please explain"
        ]
    }
    
    options = fallbacks.get(goal, [
        "wait checking now", 
        "one min please",
        "ok let me see",
        "trying it now"
    ])
    
    # Try to pick one that doesn't repeat key words
    for option in random.sample(options, len(options)):
        if not any(word in used_words for word in option.split() if len(word) > 3):
            return option
    
    # If all options repeat, still return random one
    return random.choice(options)

def llm_generate(goal: str, conversation_history: List[Dict[str, str]]) -> str:
    """Generate human-like responses using LLM with strong anti-repetition"""
    
    # Use more context for better continuity
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    
    # Format conversation history more naturally
    history_text = "\n".join([
        f"{'Rajesh' if msg['role'] == 'user' else 'Bank Rep'}: {msg['content']}"
        for msg in recent_history
    ])
    
    # Extract phrases you've already used to avoid repetition
    your_previous_messages = [msg['content'] for msg in recent_history if msg['role'] == 'user']
    
    user_message = f"""CONVERSATION SO FAR:
{history_text}

YOUR SITUATION: {GOAL_PROMPTS.get(goal, goal)}

WHAT YOU'VE ALREADY SAID:
{your_previous_messages[-3:] if your_previous_messages else 'Nothing yet'}

CRITICAL INSTRUCTIONS:
1. Write as Rajesh would naturally text on his phone
2. DO NOT copy any phrase from your previous messages
3. Vary your vocabulary - if you said "link not opening", now say "site won't load" or "getting error page"
4. Add human touches: small typo, thinking pause ("hmm", "wait"), natural reaction
5. Match your emotional state to the situation (confused/frustrated/eager to help)
6. Sound like a real person texting, not a script

                Your confusion and fear is growing. Keep saying: "i'm scared", "this seems strange", "why all this?"

Write Rajesh's next message now (short, confused, scared, human-like):"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,
                temperature=1.2,
                top_p=0.97,
                top_k=50,
                max_output_tokens=150,
                stop_sequences=['\n\n', 'Bank Rep:', 'Rajesh:', 'Scammer:']
            )
        )

        text = response.text.strip() if response.text else ""
        
        text = text.replace('Rajesh:', '').replace('User:', '').strip()
        
        if not text or len(text.split()) > 50 or len(text.split()) < 3:
            return generate_dynamic_fallback(goal, your_previous_messages)

        return text

    except Exception as e:
        print(f"LLM Error: {e}")
        return generate_dynamic_fallback(goal, your_previous_messages)

