from django.db import models
import uuid

class Document(models.Model):
    """
    Represents a processed document with embeddings stored in a vector database.
    """
    asset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.file_name} ({self.asset_id})"


class Chat(models.Model):
    """
    Represents a single chat session linked to a processed document.
    """
    chat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chats')
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_interacted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat {self.chat_id} for Asset {self.asset.asset_id}"


class Conversation(models.Model):
    """
    Represents a single exchange in a chat thread.
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='conversations')
    user_query = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation in Chat {self.chat.chat_id} at {self.created_at}"
