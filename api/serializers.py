from rest_framework import serializers
from .models import (Document,Chat,Conversation,)

class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['user_query', 'bot_response', 'created_at']


class ChatDetailSerializer(serializers.ModelSerializer):
    conversations = ConversationSerializer(many=True, read_only=True)
    asset = AssetsSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['chat_id', 'asset', 'started_at', 'last_interacted_at', 'conversations']