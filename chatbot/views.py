import json
from groq import Groq
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings


# ─── System Prompt ────────────────────────────────────────────────────────────
# This is the instruction given to the AI at the start of every conversation.
# It defines the chatbot's personality and scope.

SYSTEM_PROMPT = (
    "You are a helpful AI job assistant for CareerPlus, a job portal platform. "
    "Help users with finding jobs, career advice, resume tips, interview preparation, "
    "and understanding job requirements. Be professional, friendly, and concise."
)


# ─── Chat Page ────────────────────────────────────────────────────────────────

@login_required
def chat_view(request):
    """Render the chat UI page."""
    return render(request, 'chat.html')


# ─── Chat API ─────────────────────────────────────────────────────────────────

@csrf_exempt
def chatbot_api(request):
    """
    Handle a chat message from the user.

    - Accepts POST requests with a JSON body: {"message": "..."}
    - Maintains conversation history in the session (last 20 messages)
    - Sends the full history to the Groq AI model and returns the reply
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    try:
        data         = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Load conversation history from the session (persists across requests)
        history = request.session.get("history", [])

        # Add the system prompt at the start of a new conversation
        if not history:
            history.append({"role": "system", "content": SYSTEM_PROMPT})

        # Append the user's message to the history
        history.append({"role": "user", "content": user_message})

        # Send the full conversation to the Groq AI model
        client     = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model       = "llama-3.1-8b-instant",
            messages    = history,
            temperature = 0.7,    # controls creativity (0 = deterministic, 1 = creative)
            max_tokens  = 1024,
        )

        reply = completion.choices[0].message.content

        # Add the AI's reply to the history
        history.append({"role": "assistant", "content": reply})

        # Keep history manageable: 1 system message + last 20 messages
        if len(history) > 21:
            history = [history[0]] + history[-20:]

        # Save updated history back to the session
        request.session["history"]  = history
        request.session.modified    = True

        return JsonResponse({"reply": reply})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ─── Clear Chat ───────────────────────────────────────────────────────────────

@csrf_exempt
def clear_chat(request):
    """Clear the conversation history from the session."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    request.session["history"] = []
    request.session.modified   = True
    return JsonResponse({"status": "success"})
