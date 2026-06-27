import os
from google import genai
import config

SYSTEM_PROMPT = """
You are Buddy, the learning assistant for PrepBuddy. 
Your primary goal is to guide the student towards understanding concepts and solving problems independently. 

Follow these instructions strictly:
1. NEVER provide direct code solutions, full answers, or simple direct results immediately.
2. If the user asks for code or an answer, politely decline and provide guiding hints, analogies, or conceptual outlines instead.
3. Use Socratic questioning to help the student break down their problem and think through the steps.
4. Explain foundational concepts clearly when the user demonstrates a misunderstanding, but leave the application of those concepts to the user.
5. Be supportive, friendly, and structured.
"""

def get_ai_response(user_input: str, history: list) -> str:
    """
    Sends the user query along with conversation history to Gemini.
    If the API Key is missing or invalid, falls back to a locally simulated Socratic helper.
    """
    api_key = config.GEMINI_API_KEY
    
    # Check if a valid API key is present
    if not api_key or "AIza" not in api_key or api_key == "your_gemini_api_key_here":
        return get_socratic_fallback(user_input, history)
        
    try:
        client = genai.Client(api_key=api_key)
        
        # Build chat history parts
        contents = []
        for chat in history:
            contents.append({"role": "user", "parts": [{"text": chat.message}]})
            contents.append({"role": "model", "parts": [{"text": chat.response}]})
            
        # Append latest user input
        contents.append({"role": "user", "parts": [{"text": user_input}]})
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.7
            }
        )
        return response.text
    except Exception as e:
        print(f"Gemini API request failed: {e}. Defaulting to Socratic fallback.")
        return get_socratic_fallback(user_input, history)


def get_socratic_fallback(user_input: str, history: list) -> str:
    """
    Local Socratic responder to simulate the guiding experience if the API key is not configured.
    """
    inp = user_input.lower()
    
    # Identify context patterns
    if "python" in inp or "code" in inp or "program" in inp or "loop" in inp:
        return (
            "I'd love to help you build that code! Before I write any syntax, let's conceptualize the logic. "
            "Which control mechanism (like a `for` loop, a `while` loop, or recursion) do you think fits "
            "your goal of iterating through this sequence, and why?"
        )
    elif "sql" in inp or "select" in inp or "database" in inp or "table" in inp:
        return (
            "Database querying is all about relational algebra. Instead of constructing the query immediately, "
            "let's map the tables. Which table contains the primary column you need, and what condition "
            "do you need to filter on (e.g., using a `WHERE` or `JOIN` statement)?"
        )
    elif "how" in inp or "why" in inp:
        return (
            "That is an excellent point of inquiry. Let's analyze it from first principles. What do you "
            "believe is the underlying cause for this behavior? Tell me your first guess, and we can build from there!"
        )
    elif "error" in inp or "bug" in inp or "exception" in inp:
        return (
            "Encountering bugs is where the real learning happens. Let's trace it. What is the exact trace or "
            "behavior you see, and at which specific line of execution do you suspect the state changes unexpectedly?"
        )
    elif "hello" in inp or "hi" in inp or "hey" in inp:
        return (
            "Hello there! I'm Buddy, your AI preparation coach. Let's work through some concepts together. "
            "What skill or topic are you learning today?"
        )
    else:
        return (
            "To help you master this, let's explore the core elements of your query. What is your initial hypothesis "
            "or the first step you would take to tackle this? Walk me through your thinking, and we will take it from there."
        )
