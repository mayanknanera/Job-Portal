import json
from groq import Groq
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

SYSTEM_PROMPT = (
    "You are a helpful AI job assistant for CareerPlus, a job portal platform. "
    "Help users with finding jobs, career advice, resume tips, interview preparation, "
    "and understanding job requirements. Be professional, friendly, and concise."
)


@login_required
def chat_view(request):
    return render(request, 'chat.html')


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        history = request.session.get("history", [])

        if not history:
            history.append({"role": "system", "content": SYSTEM_PROMPT})

        history.append({"role": "user", "content": user_message})

        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history,
            temperature=0.7,
            max_tokens=1024,
        )

        reply = completion.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        # Keep 1 system message + last 20 messages
        if len(history) > 21:
            history = [history[0]] + history[-20:]

        request.session["history"] = history
        request.session.modified = True

        return JsonResponse({"reply": reply})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def clear_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    request.session["history"] = []
    request.session.modified = True
    return JsonResponse({"status": "success"})
