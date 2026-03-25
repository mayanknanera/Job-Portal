from django.urls import path
from .views import chatbot_api, chat_view, clear_chat

app_name = 'chatbot'

urlpatterns = [
    path("chat/", chat_view, name="chat"),
    path("chatbot/api/", chatbot_api, name="chatbot_api"),
    path("chatbot/clear/", clear_chat, name="clear_chat"),
]