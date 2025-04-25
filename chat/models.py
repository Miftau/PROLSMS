from django.db import models

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    is_group = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"