from rest_framework import serializers

from .models import Conversation, Message, User

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ('conversation_id', 'created_at')

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('message_id', 'sent_at')