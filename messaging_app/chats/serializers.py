from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# ValidationError is available as serializers.ValidationError for validation methods
serializers.ValidationError = ValidationError

from .models import Conversation, Message, User


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with nested sender information"""
    sender = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    sender_email = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()
    message_body = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=10000,
        help_text="The content of the message"
    )
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('message_id', 'sent_at', 'sender')
    
    def get_sender_email(self, obj):
        """Return sender's email address"""
        return obj.sender.email if obj.sender else None
    
    def get_sender_name(self, obj):
        """Return sender's full name"""
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}"
        return None
    
    def validate_message_body(self, value):
        """Validate message body is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        if len(value.strip()) > 10000:
            raise serializers.ValidationError("Message body is too long. Maximum 10000 characters allowed.")
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages"""
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    participant_emails = serializers.SerializerMethodField()
    participant_names = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ('conversation_id', 'created_at')
    
    def get_participant_emails(self, obj):
        """Return list of participant email addresses"""
        return [user.email for user in obj.participants.all()]
    
    def get_participant_names(self, obj):
        """Return list of participant full names"""
        return [f"{user.first_name} {user.last_name}" for user in obj.participants.all()]
    
    def get_messages(self, obj):
        """Return nested messages for this conversation"""
        messages = obj.messages.all()[:50]  # Limit to last 50 messages
        return MessageSerializer(messages, many=True).data
    
    def get_message_count(self, obj):
        """Return total number of messages in conversation"""
        return obj.messages.count()
    
    def validate_participants(self, value):
        """Validate participants list"""
        if not value:
            raise serializers.ValidationError("A conversation must have at least one participant.")
        if len(value) < 1:
            raise serializers.ValidationError("A conversation must have at least one participant.")
        return value