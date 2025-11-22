"""
Custom authentication classes and utilities for the messaging app.
"""

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class ChatAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for chat operations.
    This is a placeholder - JWT authentication is already configured globally.
    You can extend this if you need chat-specific authentication logic.
    """
    
    def authenticate(self, request):
        # This is a placeholder - actual authentication is handled by
        # JWT authentication configured in settings.py
        # You can add custom logic here if needed, such as:
        # - Chat-specific token validation
        # - Rate limiting per user
        # - IP-based restrictions
        return None


def get_user_chats(user):
    """
    Helper function to get all chats for a given user.
    Returns queryset of chats where user is either user1 or user2.
    """
    from django.db import models
    from .models import Chat
    return Chat.objects.filter(
        models.Q(user1=user) | models.Q(user2=user)
    )


def is_chat_participant(user, chat):
    """
    Helper function to check if a user is a participant in a chat.
    """
    return user == chat.user1 or user == chat.user2


def can_send_message(user, chat):
    """
    Helper function to check if a user can send a message in a chat.
    """
    return is_chat_participant(user, chat)
