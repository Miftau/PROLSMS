from django.urls import path
from .views import chat_room_view

urlpatterns = [
    path('room/<int:room_id>/', chat_room_view, name='chat-room'),
]
