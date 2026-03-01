from core.flow import handle_message
from core.sessions import sessions


session_id = "test123"

scammer_messages = [
    "Your account is blocked urgently verify",
    "Send money to UPI: fraudster@upi",
    "Payment link is http://fakebank.xyz/pay",
    "Call me at +919876543210"
]

for msg in scammer_messages:
    reply, stop_flag = handle_message(session_id, msg)

    print("\nScammer:", msg)
    print("Agent  :", reply)
    print("Stop?  :", stop_flag)

    if stop_flag:
        break


print("\nFINAL EXTRACTED INTELLIGENCE")
print(sessions[session_id].extracted)
print("kjfhkffbkfhqhefbwhfbwhfbwhfbwf")

print("\nFULL CHAT HISTORY:")
for msg in sessions[session_id].messages:
    print(msg)
