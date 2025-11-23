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
       
        if not (request.user and request.user.is_authenticated):
            return False

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant in the conversation (chat).
        This applies to object-level operations (retrieve, update, delete).
        Explicitly handles PUT, PATCH, and DELETE methods.
        """

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if hasattr(obj, 'chat'):
                chat = obj.chat
                is_participant = request.user == chat.user1 or request.user == chat.user2
                if request.method == 'DELETE':
                    return is_participant
                return is_participant
            
            if hasattr(obj, 'user1') and hasattr(obj, 'user2'):
                return request.user == obj.user1 or request.user == obj.user2
        
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'chat'):
                chat = obj.chat
                is_participant = request.user == chat.user1 or request.user == chat.user2
                return is_participant
            
            if hasattr(obj, 'user1') and hasattr(obj, 'user2'):
                return request.user == obj.user1 or request.user == obj.user2
        
        return False
