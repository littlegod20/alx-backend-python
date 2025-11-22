from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission class that:
    1. Allows only authenticated users to access the API
    2. Allows only participants in a conversation to send, view, update and delete messages
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is authenticated.
        For POST requests (creating messages), also verify the user is a participant in the chat.
        """
        # First check if user is authenticated
        if not (request.user and request.user.is_authenticated):
            return False
        
        # For message creation, check if user is a participant in the chat
        if request.method == 'POST' and hasattr(view, 'get_serializer_class'):
            # Check if this is a MessageViewSet
            if hasattr(view, 'queryset') and view.queryset.model.__name__ == 'Message':
                chat_id = request.data.get('chat')
                if chat_id:
                    from .models import Chat
                    try:
                        chat = Chat.objects.get(pk=chat_id)
                        is_participant = request.user == chat.user1 or request.user == chat.user2
                        return is_participant
                    except Chat.DoesNotExist:
                        return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant in the conversation (chat).
        This applies to object-level operations (retrieve, update, delete).
        """
        # For Message objects, check if user is participant in the message's chat
        if hasattr(obj, 'chat'):
            chat = obj.chat
            is_participant = request.user == chat.user1 or request.user == chat.user2
            return is_participant
        
        # For Chat objects, check if user is a participant
        if hasattr(obj, 'user1') and hasattr(obj, 'user2'):
            return request.user == obj.user1 or request.user == obj.user2
        
        return False
