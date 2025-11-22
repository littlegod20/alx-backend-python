from django.shortcuts import render
from django.db import models
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Chat objects.
    Uses IsParticipantOfConversation permission to ensure only authenticated
    users who are participants in a conversation can access chats.
    """
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsParticipantOfConversation]
    
    def get_queryset(self):
        """
        Filter chats to only show those where the current user is a participant.
        """
        user = self.request.user
        if user.is_authenticated:
            return Chat.objects.filter(
                models.Q(user1=user) | models.Q(user2=user)
            )
        return Chat.objects.none()


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Message objects.
    Uses IsParticipantOfConversation permission to ensure only authenticated
    users who are participants in a conversation can send, view, update, and delete messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    
    def get_queryset(self):
        """
        Filter messages to only show those from chats where the current user is a participant.
        """
        user = self.request.user
        if user.is_authenticated:
            return Message.objects.filter(
                models.Q(chat__user1=user) | models.Q(chat__user2=user)
            )
        return Message.objects.none()
    
    def perform_create(self, serializer):
        """
        Automatically set the sender to the current user when creating a message.
        Also verify that the user is a participant in the chat they're sending to.
        """
        chat_id = serializer.validated_data.get('chat')
        if chat_id:
            chat = chat_id if isinstance(chat_id, Chat) else Chat.objects.get(pk=chat_id)
            # Check if user is a participant in the chat
            if self.request.user != chat.user1 and self.request.user != chat.user2:
                raise PermissionDenied("You can only send messages to conversations you are part of.")
        
        serializer.save(sender=self.request.user)