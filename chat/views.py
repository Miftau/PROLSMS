from django.shortcuts import render, get_object_or_404
from .models import ChatRoom
from django.contrib.auth.decorators import login_required

@login_required
def chat_room_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    return render(request, 'chat/chat_room.html', {'room': room})
