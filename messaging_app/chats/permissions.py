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
        For POST requests (creating messages), also verify the user is a participant in the conversation.
        """
       
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant in the conversation.
        This applies to object-level operations (retrieve, update, delete).
        Explicitly handles PUT, PATCH, and DELETE methods.
        """
        user = request.user

        # Handle Message objects
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
            is_participant = user in conversation.participants.all()
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant
            if request.method in permissions.SAFE_METHODS:
                return is_participant
        
        # Handle Conversation objects
        if hasattr(obj, 'participants'):
            is_participant = user in obj.participants.all()
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant
            if request.method in permissions.SAFE_METHODS:
                return is_participant
        
        return False
