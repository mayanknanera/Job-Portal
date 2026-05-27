from django.urls import path
from .views import chatbot_api, chat_view, clear_chat

app_name = 'chatbot'

# ─── Chatbot URL Patterns ─────────────────────────────────────────────────────

urlpatterns = [
    path("chat/",          chat_view,    name="chat"),         # chat UI page
    path("chatbot/api/",   chatbot_api,  name="chatbot_api"),  # send a message
    path("chatbot/clear/", clear_chat,   name="clear_chat"),   # clear history
]
