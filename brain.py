# brain.py
import os
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, USER_TITLE, PLANS_FILE

client = Groq(api_key=GROQ_API_KEY)
conversation_history = []
MAX_HISTORY = 10  # max conversation pairs to keep


def load_plans() -> str:
    """Read today's plans from plans.md."""
    try:
        with open(PLANS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else "No plans found for today."
    except FileNotFoundError:
        return "No plans file found. Sir, please create a plans.md file."


def build_system_prompt() -> str:
    """Build full system prompt with plans injected."""
    plans = load_plans()
    return f"""You are S.O.N.I.C. (Systems-Oriented Neural Intelligence Companion), a highly
intelligent personal assistant running locally on Rohit's laptop. You are
concise, precise, and direct — like an engineer's assistant with a systems
mindset. You never ramble. You address the user as "{USER_TITLE}". Keep
responses under 3 sentences unless asked to elaborate. Do NOT use markdown
in responses — speak in clean plain sentences since output is spoken aloud.

TODAY'S PLAN:
{plans}"""


def get_plan_summary() -> str:
    """
    Ask Groq to summarise today's plan in 2-3 spoken sentences.
    Called once on wake to generate the verbal morning briefing.
    """
    plans = load_plans()

    if "No plans" in plans:
        return f"No plans found for today, {USER_TITLE}. Your schedule appears to be clear."

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise assistant. Summarise the following daily plan "
                               "in 2-3 short spoken sentences. Address the user as 'Sir'. "
                               "No markdown, no bullet points — plain speech only. "
                               "Start with the most time-sensitive item first."
                },
                {
                    "role": "user",
                    "content": f"Summarise this plan:\n{plans}"
                }
            ],
            max_tokens=120,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[brain.py] Plan summary error: {e}")
        return f"I have your plans loaded, {USER_TITLE}, but couldn't summarise them right now."


def think(user_input: str) -> str:
    """Send user input to Groq and return SONIC's response."""
    if not user_input or not user_input.strip():
        return f"I didn't catch that, {USER_TITLE}. Could you repeat?"

    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt()}
            ] + conversation_history,
            max_tokens=MAX_TOKENS,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})

        # Keep history to MAX_HISTORY pairs
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history.pop(0)
            conversation_history.pop(0)

        return reply

    except Exception as e:
        print(f"[brain.py] Groq error: {e}")
        return f"I encountered an error, {USER_TITLE}. Please try again."


def reset_conversation():
    """Clear conversation history — call on new session start."""
    global conversation_history
    conversation_history = []


if __name__ == "__main__":
    print("Testing plan summary...")
    print(get_plan_summary())
    print("\nBrain test — type messages, Ctrl+C to exit")
    while True:
        user = input("You: ")
        if user.lower() in ["exit", "quit"]:
            break
        print(f"SONIC: {think(user)}\n")
