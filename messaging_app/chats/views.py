from django.shortcuts import render
from django.db import models
from rest_framework import viewsets
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from .permissions import IsChatParticipant, IsMessageParticipant, CanSendMessage


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsChatParticipant]
    
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
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsMessageParticipant, CanSendMessage]
    
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
        """
        serializer.save(sender=self.request.user)