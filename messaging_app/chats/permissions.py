from rest_framework import permissions


class IsChatParticipant(permissions.BasePermission):
    """
    Permission to only allow users who are participants in a chat
    to view or modify that chat.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.user1 or request.user == obj.user2
        
        # Write permissions are allowed to any participant
        return request.user == obj.user1 or request.user == obj.user2


class IsMessageParticipant(permissions.BasePermission):
    """
    Permission to only allow users who are participants in a message's chat
    to view that message.
    """
    
    def has_object_permission(self, request, view, obj):
        # Users can view messages if they're part of the chat
        chat = obj.chat
        is_participant = request.user == chat.user1 or request.user == chat.user2
        
        if request.method in permissions.SAFE_METHODS:
            return is_participant
        
        # Users can only modify messages they sent
        return is_participant and request.user == obj.sender


class IsMessageSender(permissions.BasePermission):
    """
    Permission to only allow the sender of a message to modify it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the sender can modify their own messages
        return request.user == obj.sender


class CanSendMessage(permissions.BasePermission):
    """
    Permission to check if a user can send a message in a chat.
    Used for message creation.
    """
    
    def has_permission(self, request, view):
        # For creation, check if user is part of the chat
        if request.method == 'POST':
            chat_id = request.data.get('chat')
            if chat_id:
                from .models import Chat
                try:
                    chat = Chat.objects.get(pk=chat_id)
                    return request.user == chat.user1 or request.user == chat.user2
                except Chat.DoesNotExist:
                    return False
        return True

